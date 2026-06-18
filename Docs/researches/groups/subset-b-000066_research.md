# subset-b-000066 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/instrument/instrumented_service.go -->
# sources/cloud-native/containerd/internal/cri/instrument/instrumented_service.go

## Purpose

This file wraps the CRI runtime and image gRPC services with containerd-specific request instrumentation. It is the outer service layer that enforces initialization, attaches the containerd namespace to request contexts, logs CRI request/response outcomes, records trace errors for important lifecycle calls, sanitizes selected image errors, and converts internal errors to gRPC status errors.

## Important APIs, Types, and Functions

`criService` is the wrapped dependency and embeds `GRPCServices` plus `IsInitialized`. `GRPCServices` embeds `runtime.RuntimeServiceServer` and `runtime.ImageServiceServer`. `instrumentedService` embeds the unimplemented CRI service servers and delegates to `c criService`. `NewService` returns the wrapper. `checkInitialized` returns gRPC `Unavailable` until the underlying service is ready.

The file implements all CRI runtime/image endpoints visible in this source set: pod sandbox lifecycle, port-forward, container lifecycle, exec/attach, resource updates, image operations, stats, status, version, runtime config, log reopen, checkpoint, event streaming, pod sandbox metrics, and pod resource updates.

## Control Flow

Every unary method starts with `checkInitialized`, logs request metadata, defers outcome logging, calls the underlying service, and returns `errgrpc.ToGRPC(err)`. Most calls wrap the context with `ctrdutil.WithNamespace(ctx)` before delegation; `ListMetricDescriptors`, `ListPodSandboxMetrics`, and `RuntimeConfig` call through with the original context. Lifecycle-heavy calls also record the final error on the tracing span. Image calls sanitize errors before gRPC conversion to avoid leaking sensitive registry data.

`GetContainerEvents` is the server-streaming exception: it checks initialization, uses the stream context for logging, delegates directly to `in.c.GetContainerEvents`, then converts the returned error.

## State and Persistence Behavior

The wrapper is stateless apart from the service pointer. It does not persist CRI state, mutate stores, or own lifecycle resources. Its durable effect is indirect: every delegated call runs in the intended containerd namespace, so store and content operations hit the CRI namespace consistently.

## Dependencies and Integration Points

It depends on CRI protobuf servers, `errdefs`/`errgrpc`, containerd logging, CRI util namespace helpers, and tracing. It is registered wherever the CRI plugin exposes runtime and image gRPC services. It integrates with all server implementation files by delegating to the same CRI service interface.

## Risks and Edge Cases

Adding a new CRI method without the initialization guard or namespace injection would create inconsistent behavior. Logging full request objects can expose useful operational context but must avoid secrets; image errors are explicitly sanitized, while other method logs depend on request content. The few methods that do not namespace-wrap their context should remain intentional because changing that may alter metadata or metrics behavior.

## Test Signals

Useful tests assert initialization failure returns gRPC unavailable, delegated calls receive a namespaced context, errors are gRPC converted, image errors are sanitized, and tracing/logging hooks run on success and failure. Integration tests should verify every CRI endpoint remains reachable through this wrapper.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/instrument/instrumented_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/container_io.go -->
# sources/cloud-native/containerd/internal/cri/io/container_io.go

## Purpose

This file owns long-lived container stdio plumbing. It adapts containerd `cio.IO` to either filesystem FIFOs or reconnectable streaming endpoints, fans container stdout/stderr to multiple attach/log consumers, and manages cancellation/wait/close behavior for container IO.

## Important APIs, Types, and Functions

`ContainerIO` stores the container ID, `cio.FIFOSet`, opened `stdioStream`, stdout/stderr `WriterGroup`s, and a `wgCloser`. `ContainerIOOpts` configures construction through `WithFIFOs`, `WithNewFIFOs`, and `WithStreams`. `NewContainerIO` validates FIFOs/streams and opens actual stdio endpoints. `Config` returns the `cio.Config`. `Pipe` starts background copying from container output into writer groups. `Attach` wires a client’s stdin/stdout/stderr to the existing streams. `AddOutput` registers named output writers and returns displaced writers. `Cancel`, `Wait`, and `Close` delegate to the closer and FIFO set.

## Control Flow

Construction applies all options, requires a non-nil FIFO set, then calls `newStdioStream`. `Pipe` starts one goroutine for stdout and, when non-TTY, one for stderr; each drains into the writer group, closes its reader/group, and marks the shared waitgroup done. `Attach` generates per-attach keys, optionally copies client stdin into container stdin, registers output writers with close informers, waits for output close or context cancellation, removes writer-group entries on cancellation, and ensures the wrapped stdin reader is closed.

## State and Persistence Behavior

Runtime state is in open FIFOs/streams, writer-group membership, goroutines, and waitgroups. FIFO paths live below the volatile container root when `WithNewFIFOs` is used. Streaming mode encodes stable stream IDs derived from container ID and stream name so shim streams can reconnect after containerd restarts.

## Dependencies and Integration Points

It depends on the CRI `io` helpers, `pkg/cio`, `pkg/ioutil.WriterGroup`, containerd logging, and `util.GenerateID`. The CRI server attaches user streams through `ContainerIO.Attach`; container creation stores the `ContainerIO` in the container store.

## Risks and Edge Cases

TTY mode intentionally suppresses stderr. Incorrect writer-group removal can leak attach writers or block copies. `StdinOnce` behavior differs for TTY and non-TTY to match kubectl/docker expectations. Output goroutines must be closed on create failure and container teardown, otherwise FIFO reads or stream connections can leak.

## Test Signals

Tests should cover FIFO and stream construction, TTY versus non-TTY stderr behavior, attach cancellation cleanup, `StdinOnce` close behavior, multiple concurrent `AddOutput` consumers, and `Wait` returning after output goroutines drain.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/container_io.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/exec_io.go -->
# sources/cloud-native/containerd/internal/cri/io/exec_io.go

## Purpose

This file provides stdio handling for CRI exec sessions. Unlike `ContainerIO`, exec IO is short-lived and connects one client-facing set of streams directly to an exec process’s stdin/stdout/stderr over FIFOs or sandbox streaming endpoints.

## Important APIs, Types, and Functions

`ExecIO` implements `cio.IO` and holds an ID, `cio.FIFOSet`, opened `stdioStream`, and `wgCloser`. `NewFifoExecIO` creates named FIFOs under an IO root. `NewStreamExecIO` creates stable streaming URLs using the exec ID. `Config` exposes the `cio.Config`. `Attach` copies stdin and output and returns a done channel. `Cancel`, `Wait`, and `Close` control cancellation, waitgroups, and FIFO closure.

## Control Flow

Both constructors build a FIFO set, open it with `newStdioStream`, and return the configured object. `Attach` wraps stdin so it can interrupt `io.Copy`; on stdin completion it closes process stdin when `StdinOnce` is set and non-TTY, otherwise closes output readers to end the session. Each selected output starts a goroutine that copies from exec stdout/stderr into the client writer, closes both ends, closes stdin wrapper if present, and marks both the exec closer waitgroup and local attach waitgroup done. A background goroutine closes the returned `done` channel when all requested streams finish.

## State and Persistence Behavior

State is limited to open FIFOs/streams and goroutine synchronization. Exec stream IDs are deterministic from exec ID and stream type for reconnectable streaming. No CRI store state is persisted here.

## Dependencies and Integration Points

It shares helpers with container IO, uses `pkg/cio`, `pkg/ioutil`, and containerd logging. CRI exec server code constructs `ExecIO` for each exec request and passes `AttachOptions` from streaming server callbacks.

## Risks and Edge Cases

TTY mode omits stderr. If stdin ends first and `StdinOnce` is false, output streams are closed to prevent hanging sessions. Copy errors are logged but not returned through the done channel, so callers need other signals for failures. Close ordering matters to avoid blocked FIFO writers/readers.

## Test Signals

Tests should exercise stdin-only, stdout/stderr, TTY, cancellation, `StdinOnce`, stream close ordering, and `Close` on partially opened IO.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/exec_io.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/helpers.go -->
# sources/cloud-native/containerd/internal/cri/io/helpers.go

## Purpose

This file contains shared CRI IO primitives: attach option shape, stream type constants, FIFO/stream URL construction, stdio opening, and a waitgroup-aware closer used by both container and exec IO.

## Important APIs, Types, and Functions

`AttachOptions` carries client stdin/stdout/stderr, TTY mode, `StdinOnce`, and a `CloseStdin` callback to close the runtime side. `StreamType` defines `Stdin`, `Stdout`, and `Stderr`. `wgCloser` owns a cancelable context, waitgroup, and closers. `newFifos` creates `root/io` and a `cio.FIFOSet`, blanking stdin when disabled. `newStreams` builds a `cio.FIFOSet` containing streaming URLs with `streaming_id` query parameters. `newStdioStream` opens the configured stdin/stdout/stderr endpoints. `openStdin` and `openOutput` choose local pipe versus streaming endpoint by checking for `://`.

## Control Flow

`newStdioStream` creates a background context and opens each configured endpoint in order. If any open fails, already-opened closers are closed and the context is canceled. The returned `wgCloser` lets callers wait for copy goroutines, close all endpoints, or cancel pending opens/copies. URL-less endpoints go through platform `openPipe`; URL endpoints go through streaming helpers.

## State and Persistence Behavior

The only persistent filesystem state created here is the FIFO directory and FIFO files under the supplied root. Streaming mode stores no local files; it encodes stream identity into URL fields that are later opened on demand.

## Dependencies and Integration Points

It depends on CRI runtime stream constants, `pkg/cio`, standard `syscall` open flags, and platform-specific `openPipe` implementations. It is the central abstraction used by `container_io.go` and `exec_io.go`.

## Risks and Edge Cases

The local-versus-stream decision is string-based on `://`, so malformed paths containing that token would be treated as URLs. Partial open failures must close already-opened resources. Stdin can be disabled by blanking its path, which must be respected by attach logic. Stream URL query key must match the streaming server contract.

## Test Signals

Tests should validate FIFO path layout, stdin disabled behavior, stream URL generation for TTY and non-TTY, partial open cleanup, and local/stream dispatch.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/helpers_unix.go -->
# sources/cloud-native/containerd/internal/cri/io/helpers_unix.go

## Purpose

This non-Windows helper implements CRI local pipe opening with Unix FIFOs.

## Important APIs, Types, and Functions

`openPipe(ctx, fn, flag, perm)` delegates directly to `fifo.OpenFifo`, returning an `io.ReadWriteCloser`.

## Control Flow

The caller supplies the context, path, open flags, and permissions. `fifo.OpenFifo` handles FIFO creation/open and context cancellation. There is no additional state or retry logic.

## State and Persistence Behavior

The FIFO path may be created on disk with the requested permissions. The open handle is returned to callers and later closed by `wgCloser` or FIFO set cleanup.

## Dependencies and Integration Points

It is selected by `//go:build !windows` and integrates with `helpers.go` for local FIFO mode on Linux, Darwin, and other Unix-like targets.

## Risks and Edge Cases

Open flags must be chosen correctly by callers for stdin versus output. Cancellation behavior depends on `containerd/fifo`. File permissions are set to `0700` by current callers.

## Test Signals

Unit or integration tests can open read/write FIFO pairs, cancel the context during open, and verify close releases blocked readers/writers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/helpers_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/helpers_windows.go -->
# sources/cloud-native/containerd/internal/cri/io/helpers_windows.go

## Purpose

This Windows helper implements CRI local pipe opening with Windows named pipes.

## Important APIs, Types, and Functions

`pipe` wraps a `net.Listener`, accepted `net.Conn`, accept error, and waitgroup. `openPipe` creates a `winio.ListenPipe`, starts an accept goroutine, closes the pipe on context cancellation, and returns the wrapper. `Read`, `Write`, and `Close` wait for the accept goroutine and then operate on the accepted connection or return the accept error.

## Control Flow

Opening returns before a client connects. First read/write blocks until `Accept` completes. Cancellation closes the listener, which unblocks accept. `Close` closes the listener, waits for accept completion, and closes the connection if one exists.

## State and Persistence Behavior

The state is an OS named-pipe listener and possibly one accepted connection. There is no filesystem directory state beyond the named-pipe namespace.

## Dependencies and Integration Points

It uses `github.com/Microsoft/go-winio` and satisfies the `openPipe` contract consumed by `helpers.go`.

## Risks and Edge Cases

Only one accepted connection is represented. `conErr` is written by the accept goroutine and read after `Wait`, which is safe by synchronization. Close before connect returns the accept error. The `flag` and `perm` parameters are ignored because Windows named pipe APIs do not map directly to Unix flags.

## Test Signals

Windows tests should cover delayed client connect, cancellation before connect, read/write after connect, and close behavior when accept fails.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/helpers_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/logger.go -->
# sources/cloud-native/containerd/internal/cri/io/logger.go

## Purpose

This file converts raw container stdout/stderr bytes into CRI log format. It emits timestamped lines with stream name and full/partial tags, splits overly long lines, preserves partial final lines, drains output on write errors, and updates CRI logging metrics.

## Important APIs, Types, and Functions

`NewDiscardLogger` returns a write closer backed by `io.Discard`. `NewCRILogger(path, w, stream, maxLen)` creates an `io.Pipe`, starts `redirectLogs`, and returns the writer plus a stop channel. `readLine` is a custom buffered line reader that distinguishes newline-terminated lines from EOF without newline. `redirectLogs` performs CRI formatting, line splitting, metric increments, and final cleanup.

## Control Flow

`redirectLogs` reads with a bounded `bufio.Reader`, accumulates chunks in `buf`, and tracks total length. When `maxLen` is exceeded, it emits a partial line containing the first `maxLen` bytes and retains the overflow for the next output entry. When a complete line is seen, it emits a full tag; when EOF/error arrives with buffered bytes and no newline, it emits a partial tag. Each output line is formatted as timestamp, stream, tag, payload, newline.

## State and Persistence Behavior

The file writes to the provided writer, normally a container log file. It does not open the path itself; `path` is used for diagnostics. Metrics counters track input entries/bytes, output entries/bytes, and split-created entries.

## Dependencies and Integration Points

It uses CRI log tag constants, containerd `pkg/ioutil`, logging, and counters from `metrics.go`. Container creation/start paths pass log writers into container IO writer groups.

## Risks and Edge Cases

Line splitting has careful boundary logic around buffer size, CRLF, EOF without newline, and `maxLen <= 0`. Write errors are logged but do not stop draining, avoiding container blockage at the cost of dropped log output. The custom `readLine` panics on theoretically impossible `UnreadByte` or unexpected error states.

## Test Signals

`logger_test.go` covers stdout/stderr, newline and no-newline endings, exact buffer boundaries, long lines, disabled max length, non-divisible max length, and CRLF behavior. Additional tests could assert metric increments and write-error draining.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/logger_test.go -->
# sources/cloud-native/containerd/internal/cri/io/logger_test.go

## Purpose

This test file validates CRI log line formatting and line-splitting behavior implemented by `redirectLogs`.

## Important APIs, Types, and Functions

`TestRedirectLogs` is table-driven. Each case defines raw input, stream, max length, expected CRI tags, and expected content chunks. It invokes `redirectLogs` with an in-memory reader/writer and parses the resulting lines.

## Control Flow

For each test case, the test creates an `io.NopCloser` over the input, writes formatted logs into a buffer, splits output by newline, then validates line count and fields. It parses the timestamp with `timestampFormat`, compares stream names, compares full/partial tags, and compares payload content.

## State and Persistence Behavior

The test uses only in-memory buffers. It does increment global metrics indirectly through `redirectLogs`, but does not assert metric state.

## Dependencies and Integration Points

It depends on `testify/assert`, `testify/require`, CRI runtime log tags, and `pkg/ioutil` for a no-op write closer. It directly exercises unexported package functions because it is in package `io`.

## Risks and Edge Cases

The tests focus on log framing and splitting but not write errors, metrics, concurrent `NewCRILogger` behavior, pipe close semantics, or malformed UTF-8. The table includes important boundary cases: exact buffer size, longer than buffer, exact max, max plus one, multiple max chunks, max shorter than buffer, no limit, negative limit, and CRLF at buffer boundary.

## Test Signals

Passing tests strongly signal that CRI log format remains compatible for common and boundary line lengths. Failures identify regressions in tags, timestamp format, stream names, or payload splitting.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/logger_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/metrics.go -->
# sources/cloud-native/containerd/internal/cri/io/metrics.go

## Purpose

This file registers counters for CRI log processing volume and splitting behavior.

## Important APIs, Types, and Functions

Package variables `inputEntries`, `outputEntries`, `inputBytes`, `outputBytes`, and `splitEntries` are `go-metrics` counters. `init` creates namespace `containerd_cri`, initializes the counters, and registers the namespace.

## Control Flow

Initialization runs at package load. `logger.go` increments these counters while redirecting logs. There is no runtime branching in this file after `init`.

## State and Persistence Behavior

Counter values are process-local metrics state exposed through the containerd metrics registry. They are not persisted across restarts.

## Dependencies and Integration Points

It depends on `github.com/docker/go-metrics` and integrates with CRI logging metrics emitted by `redirectLogs`.

## Risks and Edge Cases

Metric names are part of the observable surface; renaming them can break dashboards. Registration happens unconditionally at package init, so duplicate namespace registration would be a risk if package initialization semantics changed.

## Test Signals

Useful tests or integration checks should confirm the counters are registered and increment during log redirect, especially split entries for long log lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/streaming.go -->
# sources/cloud-native/containerd/internal/cri/io/streaming.go

## Purpose

This file opens CRI IO streams over sandbox-provided streaming endpoints, supporting ttrpc or gRPC transports over Unix/vsock-style addresses.

## Important APIs, Types, and Functions

`ioStream` wraps `streamingapi.Stream` plus the underlying connection/client closer. `openStdinStream` returns a byte-stream writer. `openOutputStream` returns a byte-stream reader. `openStream` parses a URL of the form `<protocol>+<scheme>://<address>?streaming_id=<id>`, dials the real address, creates a proxy stream, and returns a close-aware stream wrapper.

## Control Flow

`openStream` parses and validates the scheme, extracts `streaming_id`, reconstructs the transport address, and dials via `shim.AnonReconnectDialer`. For `ttrpc`, it creates a `ttrpc.Client` and proxy stream creator. For `grpc`, it creates an insecure gRPC client and proxy stream creator. Unsupported protocols and malformed URLs return errors.

## State and Persistence Behavior

State is one stream plus one underlying client connection per open call. `ioStream.Close` closes both the stream and connection. No local files are persisted.

## Dependencies and Integration Points

It depends on containerd streaming/proxy APIs, transfer byte-stream helpers, shim reconnect dialer, ttrpc, and gRPC. `helpers.go` uses these functions whenever FIFO config fields contain a URL.

## Risks and Edge Cases

The gRPC path shadows the earlier dialed connection with a new gRPC client from `grpc.NewClient`, so transport behavior depends on gRPC target parsing. URLs must contain `streaming_id`; older comments sometimes say `stream_id`, but code requires `streaming_id`. Insecure gRPC credentials are expected for local shim transports but would be unsafe for remote networks.

## Test Signals

Tests should cover malformed URL, missing protocol, missing stream ID, unsupported protocol, ttrpc stream creation, gRPC stream creation, and connection closure on stream close.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/io/streaming.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/labels/labels.go -->
# sources/cloud-native/containerd/internal/cri/labels/labels.go

## Purpose

This file defines label and extension keys used by the CRI plugin to mark images, containers, sandboxes, Kubernetes metadata, and stored CRI metadata extensions.

## Important APIs, Types, and Functions

Constants include the `io.cri-containerd` prefix, image management and pinned labels, container kind label and values, container/sandbox metadata extension names, Kubernetes pod name/namespace/UID/container name labels, and the infra container name `POD`.

## Control Flow

There is no executable control flow.

## State and Persistence Behavior

These constants become persisted labels and container extension keys in containerd metadata stores and image/container records. They are part of the compatibility surface for CRI metadata discovery.

## Dependencies and Integration Points

The labels are used by image management, container creation, checkpoint import metadata fixups, NRI wrappers, and store/index code. `ContainerMetadataExtension` is registered in container creation and read by NRI integration.

## Risks and Edge Cases

Changing string values would break lookup of existing images/containers or metadata extensions. Kubernetes label keys must remain aligned with kubelet expectations. The `PinnedImageLabelKey` comment says "label value" but the constant is a key; consumers should rely on the identifier, not the comment.

## Test Signals

Tests should verify labels are applied during image/container creation, extensions round-trip through containerd metadata, and checkpoint restore updates Kubernetes labels correctly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/labels/labels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/nri/nri_api.go -->
# sources/cloud-native/containerd/internal/cri/nri/nri_api.go

## Purpose

This file declares the CRI-side interface required by the NRI adapter. It decouples NRI integration from the full CRI service implementation while exposing the stores and lifecycle operations NRI plugins need.

## Important APIs, Types, and Functions

`CRIImplementation` exposes configuration, sandbox/container stores, sandbox metadata store, container metadata extension key, container resource update, and stop-container operations. Its return types bind the adapter to CRI config, CRI stores, containerd sandbox metadata, CRI runtime protobuf requests, and container store status.

## Control Flow

There is no implementation control flow. The interface defines callbacks used by platform-specific `API` implementations.

## State and Persistence Behavior

The interface itself stores nothing. Implementations provide access to persistent/in-memory CRI stores and containerd metadata.

## Dependencies and Integration Points

It integrates `internal/nri` with CRI server/store packages. Linux NRI code calls these methods for discovery, updates, evictions, spec metadata, and resource update synchronization.

## Risks and Edge Cases

Adding methods increases coupling between NRI and CRI service internals. Implementations must preserve store concurrency semantics and status update invariants. Returning nil or stale stores would make plugin discovery/update behavior unreliable.

## Test Signals

Mocks of this interface should be used for NRI API unit tests, especially resource update, eviction, metadata extension lookup, and disabled-NRI behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/nri/nri_api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/nri/nri_api_linux.go -->
# sources/cloud-native/containerd/internal/cri/nri/nri_api_linux.go

## Purpose

This Linux file implements CRI integration with the Node Resource Interface. It forwards CRI pod/container lifecycle events to NRI, exposes CRI pods and containers as NRI domain objects, allows NRI plugins to adjust OCI specs during container creation, and handles plugin-initiated resource updates or evictions.

## Important APIs, Types, and Functions

`API` holds the CRI implementation and internal NRI API. `NewAPI`, `Register`, `IsDisabled`, and `IsEnabled` manage setup. Lifecycle hooks include `RunPodSandbox`, pod resource update hooks, `StopPodSandbox`, `RemovePodSandbox`, `CreateContainer`, `PostCreateContainer`, start/update/stop/remove container hooks, `NotifyContainerExit`, `UndoCreateContainer`, `WithContainerAdjustment`, `WithContainerExit`, and `BlockPluginSync`.

The NRI domain interface is implemented by `GetName`, list/get pod and container methods, `UpdateContainer`, and `EvictContainer`. Wrappers `criPodSandbox` and `criContainer` expose CRI metadata, labels, annotations, Linux namespaces/resources/devices, CDI devices, seccomp data, PIDs, rlimits, users, and status. `fromCRILinuxResources` and `toCRIResources` convert resource structs.

## Control Flow

Registration registers the CRI domain and starts NRI if enabled. Lifecycle methods short-circuit when disabled, wrap CRI objects, and call matching NRI methods. `RunPodSandbox` compensates failed run by stopping/removing the pod in NRI. `WithContainerAdjustment` unmarshals the OCI spec from a containerd container, asks NRI for adjustments, applies them through an NRI spec generator with resource, RDT, blockio, and CDI resolvers, then re-marshals the adjusted spec. `UpdateContainer` updates CRI status synchronously while calling CRI resource-update logic. `EvictContainer` stops the container through CRI.

## State and Persistence Behavior

The adapter keeps no independent durable state. It reads CRI stores, containerd container metadata, sandbox metadata, OCI specs, and live task PIDs. Spec adjustments mutate the containerd container object before creation persists it. Resource updates mutate CRI container status through `Status.UpdateSync`.

## Dependencies and Integration Points

It depends on containerd client/container metadata, CRI annotations/constants/stores/util, blockio/CDI helpers, NRI APIs and generator, OCI runtime spec, typeurl, errdefs, and CRI protobufs. Container creation appends `WithContainerAdjustment`, defers `UndoCreateContainer`, and blocks plugin sync around new-container operations.

## Risks and Edge Cases

Disabled NRI must be a true no-op. Wrappers tolerate missing store metadata, missing tasks, and deleted network namespaces. Spec adjustment errors abort container creation. Resource conversion omits unsupported fields such as swap and sets OOM score only through the provided argument. `GetPodSandboxID` and `GetName` rely on spec annotations, so missing annotations produce empty identity fields for containerd-only objects.

## Test Signals

Tests should cover disabled behavior, lifecycle forwarding, create adjustment spec mutation, adjustment error rollback, stale netns filtering, resource conversion, plugin update/evict behavior, and wrappers for both CRI-store and raw containerd container inputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/nri/nri_api_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/nri/nri_api_other.go -->
# sources/cloud-native/containerd/internal/cri/nri/nri_api_other.go

## Purpose

This non-Linux file provides a no-op NRI API implementation for unsupported platforms while preserving the same CRI integration surface.

## Important APIs, Types, and Functions

`API` is an empty struct. `NewAPI` returns nil, while methods on nil/empty API values provide disabled behavior where callers keep a typed field. `Register` returns nil and `IsEnabled` returns false. All lifecycle hooks return nil or no adjustment. `WithContainerAdjustment` and `WithContainerExit` return no-op containerd options. `PluginSyncBlock` has a no-op `Unblock`, and `BlockPluginSync` returns nil. Domain methods return the Kubernetes containerd domain name plus empty lists/lookups or nil update/evict errors.

## Control Flow

All methods immediately return without side effects. `UpdateContainerResources` returns the request resources unchanged.

## State and Persistence Behavior

No state is stored or persisted. No CRI stores are read or mutated.

## Dependencies and Integration Points

It is selected by `//go:build !linux` and lets platform-independent CRI code call `c.nri.*` without build-tag conditionals.

## Risks and Edge Cases

Feature parity differs by platform: NRI plugins are effectively unavailable outside Linux. Callers must not assume `BlockPluginSync` returns a non-nil block or that NRI lifecycle failures can occur.

## Test Signals

Non-Linux builds should compile and tests should verify NRI calls are no-ops, especially container creation options and resource update pass-through.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/nri/nri_api_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/container.go -->
# sources/cloud-native/containerd/internal/cri/opts/container.go

## Purpose

This file defines containerd `NewContainerOpts` used by CRI container creation for robust snapshot preparation and image-defined volume initialization.

## Important APIs, Types, and Functions

`WithNewSnapshot` wraps `containerd.WithNewSnapshot`; if snapshot creation fails with not-found, it unpacks the image for the snapshotter and retries. `unpackImage` creates a lease, builds an unpacker for the default platform/snapshotter, optionally appends snapshot labels, dispatches image content, and waits for unpack completion. `WithVolumes` mounts the container rootfs snapshot read-only and copies image volume contents to host volume directories. `copyExistingContents` requires the destination volume directory to be empty and copies source contents excluding SELinux xattrs.

## Control Flow

During container creation, snapshotter is configured first, then `WithNewSnapshot` prepares the rootfs. On missing unpacked content, the wrapper performs an unpack under a lease and retries snapshot creation. `WithVolumes` retrieves snapshot mounts, removes volatile/idmap options, optionally activates mount manager transforms, mounts into a temporary directory, copies each volume source from rootfs into the matching empty host path, and unmounts/deactivates on return.

## State and Persistence Behavior

It creates snapshots in the configured snapshotter, may unpack image content into snapshotter state, creates temporary mount directories, and copies files into CRI-managed host volume directories. Leases protect content during unpack. Temporary mount directories are removed with `os.Remove`.

## Dependencies and Integration Points

It depends on containerd client, images/unpack/snapshots/mount APIs, continuity filesystem copy, snapshotter label helpers, errdefs, platform matching, and semaphores. `server/container_create.go` uses these opts during `client.NewContainer`.

## Risks and Edge Cases

The retry only handles not-found errors. `WithVolumes` refuses non-empty destinations, which prevents overwriting but can fail restore/create if cleanup is incomplete. Windows only copies volumes under C:. Mount/unmount or mount-manager deactivation failures are propagated carefully. Removing only the temp root directory avoids accidentally removing snapshot contents.

## Test Signals

Tests should cover not-found unpack retry, non-not-found propagation, snapshot label behavior, volume copy from rootfs, non-empty destination errors, Windows drive filtering, and cleanup on mount/deactivation failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_darwin_opts.go -->
# sources/cloud-native/containerd/internal/cri/opts/spec_darwin_opts.go

## Purpose

This file adds Darwin-specific mount handling for CRI-generated OCI specs.

## Important APIs, Types, and Functions

`WithDarwinMounts` merges CRI mounts with extra mounts, lets CRI mounts override extras by destination, filters default mounts that are overridden, creates missing host paths, resolves symlinks, and appends bind mounts with `ro` or `rw` options.

## Control Flow

The option copies CRI mounts first, appends non-overridden extras, sorts by destination path depth, builds a destination set, removes default mounts with those destinations, then appends parsed bind mounts to the spec.

## State and Persistence Behavior

It may create host directories for missing mount sources. It mutates only the in-memory OCI spec mounts.

## Dependencies and Integration Points

It depends on CRI runtime mounts, OCI spec options, containerd OS abstraction, and shared `orderedMounts`/`cleanMount`. Darwin spec construction in `container_create.go` uses this option.

## Risks and Edge Cases

Creating missing host paths mirrors Linux behavior but may surprise callers expecting validation-only behavior. Destination comparisons use cleaned paths; named-pipe special handling comes from `cleanMount` in Windows opts, so cross-platform build composition matters.

## Test Signals

Tests should cover CRI overriding extra/default mounts, path sorting, missing source directory creation, symlink resolution errors, and readonly option generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_darwin_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_linux.go -->
# sources/cloud-native/containerd/internal/cri/opts/spec_linux.go

## Purpose

This Linux file provides environment-detection helpers and CDI injection for OCI spec generation.

## Important APIs, Types, and Functions

`SwapControllerAvailable` detects memory swap controller support for cgroup v1 or v2. `isHugetlbControllerPresent`, `cgroupv1HasHugetlb`, and `cgroupv2HasHugetlb` detect hugetlb controller support. `IsCgroup2UnifiedMode` detects cgroup v2 by statfs. `WithCDI` injects CDI devices from CRI `CDIDevices` and legacy CDI annotations, deduplicating names.

## Control Flow

Detection helpers cache results with `sync.Once`. Swap detection checks `/sys/fs/cgroup/memory/memory.memsw.limit_in_bytes` on v1 or `memory.swap.max` under the current cgroup on v2. Hugetlb checks either `/sys/fs/cgroup/hugetlb` or `cgroup.controllers`. `WithCDI` gathers field-based devices first, parses annotations, appends unseen annotation devices, logs duplicates/deprecation, and delegates to CDI spec injection.

## State and Persistence Behavior

Only process-local cached booleans are stored. `WithCDI` mutates the in-memory OCI spec by adding device/mount/env/hook content from CDI specs.

## Dependencies and Integration Points

It depends on cgroups v3, Unix statfs, CDI libraries, CRI runtime types, containerd logging, and CRI CDI spec opts. Linux container spec construction invokes `WithCDI` through platform spec opts.

## Risks and Edge Cases

Cached controller detection may become stale if cgroup mounts change during process lifetime. `IsCgroup2UnifiedMode` panics if `/sys/fs/cgroup` cannot be statfs’d. Annotation parsing errors abort spec generation. Duplicate CDI devices are skipped silently at debug level.

## Test Signals

Tests should mock cgroup files where possible, validate CDI deduplication and annotation parsing errors, and assert spec mutation for field-based and annotation-based devices.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_linux_opts.go -->
# sources/cloud-native/containerd/internal/cri/opts/spec_linux_opts.go

## Purpose

This file contains Linux-specific OCI spec options for mounts, devices, resources, and OOM score handling.

## Important APIs, Types, and Functions

`WithMounts` and `WithMountsCgroupWritable` call `withMounts`, which merges CRI/default/extra mounts and mounts cgroups. `ensureShared` and `ensureSharedOrSlave` validate propagation sources. `WithDevices` injects CRI devices and optionally applies security-context ownership. `WithResources` maps CRI CPU, memory, swap, hugepage, and unified cgroup settings. `WithOOMScoreAdj`, `WithPodOOMScoreAdj`, `getCurrentOOMScoreAdj`, and `restrictOOMScoreAdj` set or restrict process OOM scores.

## Control Flow

Mount handling merges and sorts mounts, creates/normalizes host paths, filters overridden defaults, adds `/sys/fs/cgroup`, preserves host cgroup v2 superblock options when sharing host cgroup namespace, validates propagation, applies read-only or recursive read-only options, relabels SELinux sources, maps idmapped mount IDs, and appends OCI bind mounts. Device handling resolves host symlinks and delegates to OCI device helpers, then updates new device UID/GID if configured. Resource handling initializes spec resource structs and conditionally sets CPU/memory/swap/hugetlb/unified fields.

## State and Persistence Behavior

It may create host mount source directories and relabel mount sources. It reads host cgroup and OOM state. It mutates only the in-memory OCI spec.

## Dependencies and Integration Points

It depends on containerd mount and OS abstractions, OpenContainers SELinux labels, CRI errors, OCI spec opts, cgroup capability helpers in `spec_linux.go`, and container creation’s Linux spec builder.

## Risks and Edge Cases

Recursive read-only requires runtime-handler support and private propagation. Missing hugetlb controller can either warn or error based on config. Swap limits are only set if the swap controller is available. SELinux relabel ignores Linux `ENOTSUP`. OOM restriction prevents containers from getting a lower OOM score than the daemon when configured.

## Test Signals

Existing tests cover OOM restriction and cgroup namespace mount behavior. Additional tests should cover propagation validation, recursive read-only failure modes, device ownership, hugetlb tolerance, unified resources, idmapped mounts, and SELinux relabel errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_linux_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_linux_test.go -->
# sources/cloud-native/containerd/internal/cri/opts/spec_linux_test.go

## Purpose

This test file validates selected Linux spec option behavior: supplemental group merging, OOM score restriction, and cgroup namespace-related mount options.

## Important APIs, Types, and Functions

`TestMergeGids` checks sorted de-duplicated GID merging. `TestRestrictOOMScoreAdj` checks preferred OOM score clamping against the daemon score. `TestWithMountsCgroupNamespaceOptions` checks mount generation when cgroup namespace options vary.

## Control Flow

The tests construct inputs, call the helper/spec option, and assert expected values in returned slices or generated OCI specs. They use Linux-only package access to unexported helpers.

## State and Persistence Behavior

OOM tests read `/proc/self/oom_score_adj` indirectly. Mount tests rely on mocked or controlled OS interfaces rather than changing real host mounts.

## Dependencies and Integration Points

The tests target `spec_opts.go` and `spec_linux_opts.go`, using CRI runtime config and OCI spec structures.

## Risks and Edge Cases

Coverage is focused and does not cover all mount propagation, devices, resources, CDI, or SELinux paths. OOM expectations depend on the current process OOM score.

## Test Signals

Passing tests signal stable group merging, safe OOM clamping, and correct cgroup mount options under tested namespace conditions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_nonlinux.go -->
# sources/cloud-native/containerd/internal/cri/opts/spec_nonlinux.go

## Purpose

This non-Linux file supplies no-op or false-returning Linux capability helpers so shared spec code can compile outside Linux.

## Important APIs, Types, and Functions

`isHugetlbControllerPresent`, `SwapControllerAvailable`, and `IsCgroup2UnifiedMode` return false. `WithCDI` returns a no-op spec option.

## Control Flow

All functions return immediately without reading host state or mutating specs.

## State and Persistence Behavior

No state is stored, read, or persisted.

## Dependencies and Integration Points

It is selected by `//go:build !linux` and satisfies references from cross-platform spec code.

## Risks and Edge Cases

CDI and Linux cgroup capabilities are unavailable on non-Linux targets through this path. Callers should avoid assuming these features work outside Linux.

## Test Signals

Non-Linux builds and tests should assert these helpers are harmless no-ops and do not mutate specs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_nonlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_nonwindows.go -->
# sources/cloud-native/containerd/internal/cri/opts/spec_nonwindows.go

## Purpose

This file provides a non-Windows implementation of the Windows process argument spec option.

## Important APIs, Types, and Functions

`WithProcessCommandLineOrArgsForWindows` returns a spec option that fails with `errdefs.ErrNotImplemented`.

## Control Flow

The returned spec option immediately returns not implemented when applied. Normal non-Windows process argument composition is handled by callers using `WithProcessArgs` directly; this function only satisfies shared references to the Windows-specific API.

## State and Persistence Behavior

It does not mutate the spec because it returns before applying any process arguments.

## Dependencies and Integration Points

It is selected by `//go:build !windows` and lets shared code reference the Windows-named option while compiling on non-Windows platforms.

## Risks and Edge Cases

Windows `ArgsEscaped` semantics are intentionally ignored outside Windows. Cross-platform callers should only rely on Windows command-line behavior on Windows builds.

## Test Signals

Tests should confirm non-Windows callers do not accidentally use this Windows-specific option and that applying it returns `errdefs.ErrNotImplemented`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_nonwindows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_opts.go -->
# sources/cloud-native/containerd/internal/cri/opts/spec_opts.go

## Purpose

This file contains common OCI spec options used across CRI container spec generation: root handling, process args, annotations, security settings, capabilities, labels, sysctls, groups, sandbox shares, and namespace wiring.

## Important APIs, Types, and Functions

Key options include `WithRelativeRoot`, `WithoutRoot`, `WithProcessArgs`, `WithAnnotation`, `WithWindowsAffinityCPUs`, `WithAdditionalGIDs`, `WithoutDefaultSecuritySettings`, `WithCapabilities`, `WithoutAmbientCaps`, `WithSelinuxLabels`, `WithSysctls`, `WithSupplementalGroups`, `WithDefaultSandboxShares`, `WithoutNamespace`, `WithNamespacePath`, and `WithPodNamespaces`. `orderedMounts` sorts mounts by destination depth. Namespace path helpers return `/proc/<pid>/ns/*` paths. `mergeGids` deduplicates/sorts GIDs.

## Control Flow

Most functions return `oci.SpecOpts` closures that initialize missing spec substructures and mutate fields. `WithProcessArgs` merges CRI command/args with image entrypoint/cmd using Docker-like override rules and errors if no command remains. `WithCapabilities` expands CRI capability add/drop entries, handling `ALL` specially. `WithPodNamespaces` joins sandbox network/IPC/UTS namespaces, optionally PID target namespace and pod user namespace mappings.

## State and Persistence Behavior

These options mutate in-memory OCI specs. Namespace helpers encode host `/proc` paths but do not open them. `WithAdditionalGIDs` may read image rootfs group data through containerd OCI helpers when applied.

## Dependencies and Integration Points

It depends on CRI runtime types, image specs, OCI runtime specs, containerd OCI helpers, CRI util, and container metadata. Linux/Windows/Darwin spec builders compose these options with platform-specific options.

## Risks and Edge Cases

Command override behavior is subtle around nil versus empty slices. Capability strings are normalized by prefixing `CAP_`; invalid names may be rejected later. Namespace path joins assume sandbox/target PIDs are valid and alive. `WithoutDefaultSecuritySettings` intentionally clears defaults only when no custom base spec is used by the caller.

## Test Signals

Existing tests cover mount ordering. Good coverage also includes process arg merge cases, GID merging, capability `ALL` add/drop order, namespace path mutation, user namespace modes, and annotation/sysctl merging.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_opts_test.go -->
# sources/cloud-native/containerd/internal/cri/opts/spec_opts_test.go

## Purpose

This test file validates the shared mount ordering helper used by platform mount options.

## Important APIs, Types, and Functions

`TestOrderedMounts` constructs CRI mounts with different destination depths, sorts them with `orderedMounts`, and verifies the expected order.

## Control Flow

The test builds a slice, calls Go sort using the `orderedMounts` methods, and asserts the destination order.

## State and Persistence Behavior

The test is purely in-memory and does not touch host mounts.

## Dependencies and Integration Points

It targets the `orderedMounts` implementation in `spec_opts.go`, which is consumed by Linux, Windows, and Darwin mount option builders.

## Risks and Edge Cases

It tests path-depth sorting, but not equal-depth stability, path cleaning, platform-specific path separators, or named-pipe paths.

## Test Signals

Passing tests signal that broad parent mounts are processed before deeper child mounts, reducing mount shadowing regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_opts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_windows.go -->
# sources/cloud-native/containerd/internal/cri/opts/spec_windows.go

## Purpose

This Windows-only file implements Windows process command-line/args composition, including Docker `ArgsEscaped` compatibility.

## Important APIs, Types, and Functions

`escapeAndCombineArgsWindows` escapes args with `windows.EscapeArg`. `WithProcessCommandLineOrArgsForWindows` chooses between setting a single command line and setting OCI process args depending on image `ArgsEscaped`. `getArgs` merges image entrypoint/cmd with CRI command/args and reports whether the first arg came from the image.

## Control Flow

When `ArgsEscaped` is true, the option gets merged args. If the first arg came from the image, it keeps that first element as already escaped and escapes/joins the rest; otherwise it escapes all args. It then sets `Process.CommandLine`. When `ArgsEscaped` is false, it sets `Process.Args`. `getArgs` follows Docker-like override behavior and errors when no command remains.

## State and Persistence Behavior

The returned options mutate only the in-memory OCI process fields.

## Dependencies and Integration Points

It depends on Windows arg escaping, image specs, CRI configs, and containerd OCI helpers. Windows spec construction uses this instead of `WithProcessArgs`.

## Risks and Edge Cases

Nil versus empty command slices affect override semantics. `ArgsEscaped` is deprecated but needed for Windows image compatibility. Incorrect escaping can change container entrypoint execution.

## Test Signals

Windows tests should cover image-only, CRI override, image `ArgsEscaped`, no-command errors, and command-line versus args field selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_windows_opts.go -->
# sources/cloud-native/containerd/internal/cri/opts/spec_windows_opts.go

## Purpose

This file contains Windows-specific OCI spec options for mounts, resources, credential specs, affinity, and device assignment.

## Important APIs, Types, and Functions

`namedPipePath` and `cleanMount` preserve Windows named pipe paths. `parseMount` validates/creates/resolves host paths and normalizes destinations. `WithWindowsMounts` merges CRI/default/extra mounts. `WithWindowsResources` maps CRI CPU, memory, and affinity fields. `WithWindowsDefaultSandboxShares` sets default sandbox CPU shares. `WithWindowsCredentialSpec` sets gMSA credential spec. `WithWindowsDevices` parses CRI device host paths into OCI Windows device IDs.

## Control Flow

Mount handling appends non-overridden extras, sorts by destination depth, removes overridden defaults, parses each mount, and appends it. `parseMount` avoids stat/clean operations for named pipes, creates missing non-pipe host paths, resolves symlinks, cleans paths for hcsshim, prefixes absolute `\...` destinations with `C:`, rejects destination `C:` drive, and sets `ro`/`rw`. Device handling requires empty `ContainerPath` and `Permissions`, supports legacy `class/<id>` by rewriting to `class://<id>`, splits `IDType://ID`, and delegates to OCI Windows device opts.

## State and Persistence Behavior

It may create missing host directories and mutates only in-memory OCI Windows/mount fields. It does not persist credential specs beyond the OCI spec field.

## Dependencies and Integration Points

It depends on containerd OS abstraction, CRI runtime types, OCI runtime specs, and containerd OCI helpers. Windows container spec construction composes these options.

## Risks and Edge Cases

Named pipe paths must not be cleaned or opened because that can break pipe semantics. Destination path normalization must avoid invalid `C:` root mounts. Device format validation is strict and returns errors for Linux-style CRI device fields. CPU shares/maximum are uint16 conversions from CRI values.

## Test Signals

Existing Windows tests cover devices, resources, and drive mounts. Additional checks should cover named pipe mounts, C: destination rejection, absolute destination prefixing, credential specs, and affinity filtering of nil entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_windows_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_windows_test.go -->
# sources/cloud-native/containerd/internal/cri/opts/spec_windows_test.go

## Purpose

This Windows-focused test file validates Windows device parsing, Windows resource mapping, and drive mount behavior.

## Important APIs, Types, and Functions

`TestWithDevices` exercises `WithWindowsDevices`. `TestWithWindowsResources` checks CPU/memory/affinity resource conversion. `TestDriveMounts` checks mount parsing and path normalization for drive-style Windows paths.

## Control Flow

The tests construct CRI configs/resources/mounts, apply the Windows spec options to OCI specs, and assert expected fields or errors.

## State and Persistence Behavior

The tests use in-memory specs and mocked filesystem/OS interactions where needed. They should not require real HCS containers.

## Dependencies and Integration Points

They cover `spec_windows_opts.go` and indirectly guard behavior used by `server/container_create.go` Windows spec construction.

## Risks and Edge Cases

Coverage is strongest for explicit table cases but may not include named pipe mounts, credential specs, or every invalid path form.

## Test Signals

Passing tests signal that CRI Windows devices and resources are translated into valid OCI Windows fields and that mount path handling remains compatible with hcsshim expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/opts/spec_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/blockio_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/blockio_linux.go

## Purpose

This Linux server helper resolves the effective block I/O class for a container from CRI annotations and validates that blockio support is enabled before applying the class.

## Important APIs, Types, and Functions

`blockIOClassFromAnnotations(containerName, containerAnnotations, podAnnotations)` calls `blockio.ContainerClassFromAnnotations`, checks `blockio.IsEnabled`, optionally ignores disabled errors based on config, and returns the class name or error.

## Control Flow

If annotation parsing returns an error, it is propagated. If a class is requested while blockio is disabled, the method either clears the class and logs debug when configured to ignore, or returns an error refusing container creation. Empty class returns empty success.

## State and Persistence Behavior

It reads CRI service config and blockio global state. It does not mutate persisted state; the returned class is later converted to OCI Linux block IO settings.

## Dependencies and Integration Points

It depends on `pkg/blockio` and containerd logging. Linux container spec creation calls it before appending `oci.WithBlockIO`.

## Risks and Edge Cases

Ignoring disabled blockio can silently drop requested QoS. Refusing disabled blockio fails container creation based on annotations. Annotation precedence is delegated to the blockio package.

## Test Signals

Tests should cover no class, valid class with blockio enabled, parse errors, disabled blockio with ignore true, and disabled blockio with ignore false.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/blockio_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/blockio_stub.go -->
# sources/cloud-native/containerd/internal/cri/server/blockio_stub.go

## Purpose

This non-Linux server helper disables block I/O annotation handling on unsupported platforms.

## Important APIs, Types, and Functions

`blockIOClassFromAnnotations` always returns an empty class and nil error.

## Control Flow

The method immediately returns with no annotation parsing.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It is selected by `//go:build !linux` and allows shared server code to call the helper without platform conditionals.

## Risks and Edge Cases

Blockio annotations are ignored outside Linux. Users may expect annotations to fail or warn, but this stub silently drops them.

## Test Signals

Non-Linux tests should confirm annotated containers still create and no blockio spec fields are applied.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/blockio_stub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/cni_conf_syncer.go -->
# sources/cloud-native/containerd/internal/cri/server/cni_conf_syncer.go

## Purpose

This file watches the CNI configuration directory and reloads the CNI plugin configuration when relevant filesystem changes occur.

## Important APIs, Types, and Functions

`cniNetConfSyncer` stores a watcher, CNI plugin, load options, config directory, and last sync status protected by an RW mutex. `newCNINetConfSyncer` creates directories, starts watching, loads initial config, and stores initial errors. `syncLoop` processes fsnotify events and reloads CNI config. `lastStatus`, `updateLastStatus`, and `stop` expose status and shutdown.

## Control Flow

Construction creates the parent directory with `0755` for rootless CNI tuning compatibility, creates the config dir with `0700`, adds a watcher, and attempts initial load. `syncLoop` ignores chmod/create events, reloads on other changes, returns an error if the watched directory is removed/renamed, records reload errors, and exits on watcher errors or closed channels.

## State and Persistence Behavior

It creates CNI config directories if missing and stores last reload error in memory. It does not persist status. The watcher is an OS resource closed by `stop`.

## Dependencies and Integration Points

It depends on `github.com/containerd/go-cni`, `fsnotify`, containerd logging, and CRI server networking setup.

## Risks and Edge Cases

Reloading on broad event categories may do redundant work. Ignoring create events means a newly created file may not trigger immediate reload until a write/rename occurs, depending on editor behavior. Removal of the config directory stops the loop. Last status must be read under lock.

## Test Signals

Tests should cover initial load failure recording, reload on write/rename/remove, ignored chmod/create, directory removal exit, watcher error exit, and `stop` closing the watcher.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/cni_conf_syncer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_attach.go -->
# sources/cloud-native/containerd/internal/cri/server/container_attach.go

## Purpose

This file implements CRI attach endpoint preparation and the internal callback that binds a streaming attach session to a running container task and its `ContainerIO`.

## Important APIs, Types, and Functions

`Attach` validates the container exists and is running, then asks the stream server for an attach URL. `attachContainer` is the streaming callback that receives client stdin/stdout/stderr, TTY mode, and resize events, loads the task, wires terminal resize, builds `cio.AttachOptions`, and calls `cntr.IO.Attach`.

## Control Flow

`Attach` gets the CRI container from `containerStore`, records tracing attributes, checks status, and returns `streamServer.GetAttach(r)`. `attachContainer` creates a cancellable context, validates container state again, loads the containerd task, starts resize handling that calls `task.Resize`, defines `CloseStdin` as `task.CloseIO(...WithStdinCloser)`, and blocks in `ContainerIO.Attach` until attach completes.

## State and Persistence Behavior

The method does not persist new state. It interacts with live task IO and terminal size state. Attach URLs are managed by the stream server.

## Dependencies and Integration Points

It depends on CRI runtime protobufs, containerd client task APIs, remotecommand terminal sizes, CRI IO package, stream server callbacks, and tracing.

## Risks and Edge Cases

State is checked both before URL creation and at attach time because the container can exit between calls. Resize errors are logged but do not terminate attach. `CloseStdin` must close runtime stdin only when attach semantics require it.

## Test Signals

Tests should cover missing container, non-running state, URL creation, attach callback state revalidation, resize propagation, stdin close behavior, and TTY stderr handling through `ContainerIO`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_attach.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_checkpoint.go -->
# sources/cloud-native/containerd/internal/cri/server/container_checkpoint.go

## Purpose

This non-Linux file stubs checkpoint/restore support for platforms where CRIU checkpointing is unavailable.

## Important APIs, Types, and Functions

`checkIfCheckpointOCIImage` returns empty result. `CRImportCheckpoint` returns `errdefs.ErrNotImplemented`. `CheckpointContainer` updates the checkpoint timer with a dummy runtime label for lint/metric consistency and returns an unimplemented gRPC status error.

## Control Flow

All functions immediately return. Checkpoint requests fail explicitly with `codes.Unimplemented`, and direct checkpoint import attempts fail with `errdefs.ErrNotImplemented`.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It is selected by `//go:build !linux` and allows shared create-container code to compile while checkpoint images are ignored outside Linux.

## Risks and Edge Cases

Direct checkpoint requests and direct checkpoint imports are rejected. `checkIfCheckpointOCIImage` returning no image means normal `CreateContainer` image references do not enter checkpoint restore on non-Linux. Platform behavior differs from Linux restore support.

## Test Signals

Non-Linux tests should assert `CheckpointContainer` returns unimplemented and normal image create paths do not enter checkpoint restore.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_checkpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_checkpoint_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/container_checkpoint_linux.go

## Purpose

This Linux file implements CRI checkpoint export and checkpoint restore/import. It recognizes checkpoint OCI images or local checkpoint archives, reconstructs CRI/container metadata, reuses normal container creation with restore state, unpacks checkpoint payloads, and writes CRIU checkpoint archives.

## Important APIs, Types, and Functions

`checkIfCheckpointOCIImage` resolves an image and checks OCI index annotations for checkpoint metadata. `CRImportCheckpoint` imports a checkpoint archive/image into a CRI container. `CheckpointContainer` checkpoints a running container into an archive. `withCheckpointOpts` configures runtime checkpoint options. `writeCriuCheckpointData`, `writeRootFsDiffTar`, and `writeSpecDumpFile` extract blobs from containerd checkpoint content into checkpoint archive layout.

## Control Flow

Restore validates an image/archive input, detects OCI checkpoint image versus local file, mounts or partially unpacks checkpoint metadata into a temp directory, reads `spec.dump`, `config.dump`, and `status.dump`, fixes metadata/labels/annotations for the target sandbox, ensures the base image exists and is tagged, resolves the image, adjusts image config/env, annotates restore metadata, then calls `createContainer` with `restore=true`. After creation, it copies mounted checkpoint image content or fully unpacks the archive into the container root and restores `container.log` if present.

Checkpoint export verifies CRIU version, validates the container is running, records container config/status metadata, calls task checkpoint with runc options leaving the container running, reads the checkpoint image index, creates a temporary checkpoint directory, copies status/stats/log files, writes config/status dumps, extracts CRIU data/rootfs diff/spec blobs by media type, archives the directory to the requested location, deletes the temporary checkpoint image, and records metrics.

## State and Persistence Behavior

Restore creates temporary directories, snapshot views/mounts, CRI container root/volatile directories through `createContainer`, containerd containers/snapshots, CRI store entries, annotations, and restored log files. Checkpoint creates temporary checkpoint content under the container root, writes the requested archive, and deletes the internal checkpoint image. Both paths use defer cleanup for temp mounts/directories.

## Dependencies and Integration Points

It depends on checkpointctl metadata constants, CRIU utilities/stats, containerd client/content/images/mount/archive APIs, CRI stores/labels/annotations, image store resolution, snapshotter runtime config, OCI descriptors, and Linux runtime options. `CreateContainer` calls this path when the requested image is a checkpoint archive or checkpoint OCI image.

## Risks and Edge Cases

Restore has complex metadata rewriting for pod UID, container/pod labels, hash, and restart count. Base image tag conflicts are tolerated even if tag points to a different digest. Image-store resolve uses a bounded retry loop. Archive extraction defends against `..` only in CRIU checkpoint data extraction. Mount cleanup must run for OCI checkpoint images. Checkpoint requires a running container and sufficient CRIU support.

## Test Signals

Tests should cover checkpoint image detection, local archive metadata unpack filters, restore metadata fixups, base image pull/tag behavior, `createContainer` restore status, log restore, CRIU version failure, non-running checkpoint rejection, media-type extraction, path traversal rejection, and archive creation cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_checkpoint_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create.go -->
# sources/cloud-native/containerd/internal/cri/server/container_create.go

## Purpose

This is the main CRI `CreateContainer` implementation. It validates sandbox/container inputs, reserves unique names, handles checkpoint restore detection, resolves images, builds platform-specific OCI specs, prepares snapshots/volumes/I/O, creates containerd containers, creates CRI store objects, sends events, and invokes NRI hooks.

## Important APIs, Types, and Functions

`CreateContainer` is the public CRI method. `createContainerRequest` carries all inputs for normal and restore create paths. `createContainer` performs the transactional create. `volumeMounts` builds image-defined volume mounts. `runtimeSpec` generates or loads an OCI spec. `platformSpecOpts`, `buildContainerSpec`, `buildLinuxSpec`, `buildWindowsSpec`, and `buildDarwinSpec` compose spec options. `linuxContainerMounts` adds sandbox system file mounts. `runtimeInfo` retrieves runtime metadata from sandbox store or legacy container info.

## Control Flow

`CreateContainer` fetches sandbox and sandbox status, validates metadata and stop signal, reserves the generated CRI name, initializes metadata, detects checkpoint archive/image inputs, and either delegates to `CRImportCheckpoint` or resolves the image and calls `createContainer`.

`createContainer` creates persistent and volatile root directories with rollback cleanup, queries platform/runtime, mutates mounts, builds image volume mounts, gets runtime handler, builds spec, manages SELinux labels, gathers snapshotter opts, creates `ContainerIO` using streaming or FIFO mode, builds platform-specific post-rootfs spec opts, labels and runtime info, appends containerd options including snapshot, volumes, spec, runtime, labels, metadata extension, sandbox association, and NRI adjustment, blocks NRI plugin sync, creates the containerd container, wraps it in the CRI container store with status/resources, adds it to the store, emits a created event, and sends NRI post-create notification.

Spec builders compose OS-specific options for Linux security, namespaces, cgroups, blockio/RDT, annotations, userns, mounts, devices, and resources; Windows process/network/HostProcess/resources/devices/credential spec; and Darwin args/env/mounts.

## State and Persistence Behavior

The create transaction persists container root directories, volatile IO directories, snapshots/rootfs, image volume host directories, containerd container metadata/extensions, CRI container store checkpoints/status, name reservations, SELinux labels, and created events. Deferred cleanup releases names, removes directories, closes IO, deletes containerd containers/snapshots, deletes CRI checkpoint data, and undoes NRI create on errors.

## Dependencies and Integration Points

It integrates CRI sandbox/container stores, sandbox service, image service/resolution, runtime handler config, snapshotters, CRI IO, labels, annotations, OCI opts, blockio/RDT, NRI, tracing, containerd client, and typeurl metadata. It is the central caller of the `opts` package files in this work item.

## Risks and Edge Cases

Rollback ordering is critical to avoid leaked names, snapshots, IO, labels, and store entries. Checkpoint images take a separate path before normal image resolution. User namespace configuration must match sandbox settings. Privileged containers are rejected unless sandbox is privileged. Runtime-handler features gate recursive read-only mounts. Missing log paths disable logging. NRI adjustment can mutate specs or abort creation.

## Test Signals

Tests should cover name reservation conflicts/cleanup, missing metadata, checkpoint path selection, snapshot retry, volume mount generation, platform spec composition, Linux security/userns/namespace errors, Windows HostProcess mismatch, IO type selection, NRI rollback, store add failures, and event emission.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/container_create_linux.go

## Purpose

This Linux companion file supplies Linux-only spec options and snapshotter options used by container creation.

## Important APIs, Types, and Functions

`containerSpecOpts(config, imageConfig)` returns Linux-specific OCI spec options for platform spec application after rootfs mount. It handles supplemental group policy, image/user-derived additional groups, AppArmor, seccomp, and CDI enablement. `snapshotterOpts(config)` returns Linux snapshotter options derived from user namespace ID mappings.

## Control Flow

`containerSpecOpts` reads the Linux security context, derives the user string from run-as username, run-as UID, or image user, then applies supplemental-group policy. `Merge` adds image `/etc/group` groups plus requested supplemental groups; `Strict` adds only requested supplemental groups; unknown policies return an error. It generates AppArmor and seccomp profiles from current and deprecated fields, appends their spec opts when present, and either appends CDI injection or errors if CDI devices were requested while CDI is explicitly disabled. `snapshotterOpts` inspects user namespace mappings and builds snapshotter options so rootfs snapshots can be prepared with matching ID mappings.

## State and Persistence Behavior

Spec options mutate in-memory OCI specs. Snapshotter options influence snapshot creation state during container creation, especially user namespace/idmap behavior.

## Dependencies and Integration Points

It depends on CRI runtime types, image config, Linux security helpers, custom opts, containerd OCI/snapshot APIs, and CRI server configuration. `platformSpecOpts` in `container_create.go` calls this for Linux platforms.

## Risks and Edge Cases

Security option ordering matters because base spec defaults, CRI security context, and runtime config interact. User namespace ID mapping mistakes can make mounted rootfs or devices inaccessible. CDI annotation parsing can fail spec generation. Seccomp/AppArmor behavior depends on host support and configured defaults.

## Test Signals

Linux create tests should cover supplemental group policy, seccomp/AppArmor combinations, run-as user/group derivation for additional groups, CDI fields and annotations, CDI-disabled errors, and snapshotter idmap options.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_create_linux.go -->
