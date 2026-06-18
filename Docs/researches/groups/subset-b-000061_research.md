# subset-b-000061 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/bridge.go -->
# sources/cloud-native/containerd/core/runtime/v2/bridge.go

## Purpose
Provides the compatibility client facade used by containerd to talk to runtime v2/v3 shim task services over either ttrpc or gRPC. The file hides transport and API-version differences behind `TaskServiceClient`, whose methods match the current v3 task API.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TaskServiceClient` lists the task RPC surface: state, create, start, delete, pids, pause/resume, checkpoint, kill, exec, pty resize, close IO, update, wait, stats, connect, and shutdown. `NewTaskClient` dispatches on concrete client type: `*ttrpc.Client` supports v2 via `ttrpcV2Bridge` and v3 directly, while `grpc.ClientConnInterface` supports only v3 via `grpcV3Bridge`.

The control flow is adapter-only. For v2 ttrpc shims, each bridge method builds the v2 request from the v3 request, calls the v2 generated client, and maps the v2 response into the v3 response type. gRPC v3 methods pass through to the generated gRPC client because the request/response types already match. The file keeps no persistent state beyond client pointers in bridge structs.

Dependencies include generated task APIs for v2 and v3, ttrpc, gRPC, and protobuf empty responses. Integration points are `newShimTask`, shim reload/downgrade handling, and any code that wants a version-neutral task client.

Primary risks are lossy compatibility if v3 fields are added but not represented in v2, unsupported version errors, nil response dereferences if an RPC returns both nil response and error handling changes, and accidental use of gRPC for non-v3 shims. Test signals are table tests for `NewTaskClient`, bridge request/response mapping for every RPC, and integration tests against v2 ttrpc, v3 ttrpc, and v3 gRPC shims.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/bridge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/bundle.go -->
# sources/cloud-native/containerd/core/runtime/v2/bundle.go

## Purpose
Creates, loads, and deletes runtime v2 OCI bundle directories. A bundle records the task ID, namespace, state path, rootfs directory, optional OCI config, and a symlink to a persistent work directory.

## APIs, Flow, State, Dependencies, Risks, And Tests
`LoadBundle` reconstructs a `Bundle` from state root, namespace, and task ID. `NewBundle` validates the task ID, requires a namespace in context, creates state and work directories, creates `rootfs`, symlinks `work`, applies platform-specific permissions for OCI specs, and writes `config.json` when a non-nil spec is supplied. `Bundle.Delete` recursively unmounts `rootfs`, removes it, atomically renames/removes the bundle path, and does the same for the linked work directory. `atomicDelete` performs rename-to-hidden then recursive deletion.

The main state is filesystem state under `state/<namespace>/<id>` and `root/<namespace>/<id>`. Error handling tracks created paths and removes them on failed creation. Deletion is best-effort across bundle and workdir, but returns joined contextual errors when both paths fail.

Dependencies include namespace extraction, identifier validation, OCI config filename conventions, mount recursive unmount, and typeurl detection for OCI specs. It is used by `TaskManager.Create`, shim reload, and shim cleanup.

Risks include partial cleanup on filesystem races, failure to remove still-mounted rootfs, stale work directories after state loss, nil spec handling for sandboxers, and permission mismatches with user namespaces. Test signals come from bundle creation tests, deletion tests around mounted rootfs/work symlink behavior, and crash/restart recovery tests that reload bundle state.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/bundle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/bundle_default.go -->
# sources/cloud-native/containerd/core/runtime/v2/bundle_default.go

## Purpose
Provides the non-Linux implementation of `prepareBundleDirectoryPermissions`, making bundle permission adjustment a no-op on platforms without Linux user namespace GID remapping behavior.

## APIs, Flow, State, Dependencies, Risks, And Tests
The only API is `prepareBundleDirectoryPermissions(path string, spec []byte) error`, compiled with `//go:build !linux`. It returns nil without inspecting the path or spec. There is no control flow beyond the return, no state mutation, and no persistence.

The file exists so `bundle.go` can call the same function on every platform while Linux-specific ownership/chmod logic lives in `bundle_linux.go`. It has no imports and integrates through Go build tags.

The main risk is assuming Linux-style access fixes happen on other platforms; this file deliberately does nothing, so platform-specific user namespace support would need its own implementation. Test signals are cross-platform compilation and bundle tests that import shared test utilities on all platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/bundle_default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/bundle_linux.go -->
# sources/cloud-native/containerd/core/runtime/v2/bundle_linux.go

## Purpose
Implements Linux bundle directory permission adjustment for user-namespace-remapped containers. If container root GID 0 maps to a nonzero host GID, the bundle directory is chowned to that GID and chmodded to `0710`.

## APIs, Flow, State, Dependencies, Risks, And Tests
`prepareBundleDirectoryPermissions` calls `remappedGID`; a zero result leaves the bundle at default permissions, while a nonzero result performs `os.Chown(path, -1, gid)` and `os.Chmod(path, 0710)`. `remappedGID` unmarshals a minimal subset of the OCI spec, checks `Linux.GIDMappings`, and returns the host ID for the mapping whose `ContainerID` is zero.

State changes are filesystem ownership and mode changes on the bundle directory before config is written. No metadata is persisted beyond these mode bits. Dependencies are JSON parsing, `os.Chown`, `os.Chmod`, and runtime-spec Linux ID mapping structures.

This integrates with `NewBundle` only when the marshaled typeurl contains an OCI `specs.Spec`. Risks include malformed JSON rejecting bundle creation, root privileges required for chown, userns mappings without container ID 0 being ignored, and access failures if runtime expectations differ from `0710`.

Test signals are `TestNewBundle` under root, verifying default `0700` vs userns `0710` and GID ownership, plus `TestRemappedGID` for empty, nil, present, and missing GID mapping cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/bundle_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/bundle_linux_test.go -->
# sources/cloud-native/containerd/core/runtime/v2/bundle_linux_test.go

## Purpose
Validates Linux-specific bundle permission and GID remapping behavior.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TestNewBundle` runs as root, creates temporary root/state directories, marshals OCI specs with and without Linux GID mappings, calls `NewBundle`, and asserts directory mode plus `syscall.Stat_t.Gid`. `TestRemappedGID` marshals several minimal OCI specs and verifies `remappedGID` returns zero for no mapping and the expected host GID for container ID 0.

The tests create temporary bundle/work filesystem state and remove it through test temp cleanup. They depend on `testutil.RequiresRoot`, typeurl, OCI/specs structs, and `testify` assertions.

The important signal is that bundle directory permissions are stable for both ordinary and userns-remapped containers. Risks covered include missing Linux sections, empty mappings, mappings for non-root container IDs, and invalid ownership expectations. Gaps include negative tests for malformed spec JSON and chown/chmod failure injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/bundle_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/bundle_test.go -->
# sources/cloud-native/containerd/core/runtime/v2/bundle_test.go

## Purpose
Keeps the shared bundle test package importing `testutil` on all platforms so test flags and platform-specific test wiring remain available even when Linux-only tests are excluded.

## APIs, Flow, State, Dependencies, Risks, And Tests
The file has no executable tests and no exported API. It contains a blank import of `github.com/containerd/containerd/v2/pkg/testutil`.

There is no runtime state or control flow. Integration is with Go's test binary construction: when `bundle_linux_test.go` is not compiled, this file still ensures the package-level test utility side effects and flags are present.

Risks are minimal; removing it could create cross-platform test flag drift. The test signal is successful package test compilation on non-Linux platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/bundle_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/example/cmd/main.go -->
# sources/cloud-native/containerd/core/runtime/v2/example/cmd/main.go

## Purpose
Entrypoint for the example runtime v2 shim binary. It wires the example shim manager into the generic shim runner.

## APIs, Flow, State, Dependencies, Risks, And Tests
`main` calls `shim.RunShim(context.Background(), example.NewManager("io.containerd.example.v1"))`. There are no flags, persistent state, or local error handling in this file.

It depends on the local `example` package and containerd's `pkg/shim` runner. Integration is instructional: a real shim binary can follow this shape to register services and run under containerd's shim bootstrap protocol.

Risks are that this is intentionally skeletal; operational behavior lives in the runner and example manager. Test signals are compile checks and running the example shim enough to confirm it registers and exits through the shim framework.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/example/cmd/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/example/example.go -->
# sources/cloud-native/containerd/core/runtime/v2/example/example.go

## Purpose
Demonstrates the shape of a runtime v2 shim implementation: plugin registration, shim manager identity, runtime info, task service registration, and the task RPC method set.

## APIs, Flow, State, Dependencies, Risks, And Tests
The package registers a ttrpc task plugin requiring event publisher and shutdown services. `NewManager` returns a `shim.Shim` manager with `Name`, `Start`, `Stop`, and `Info`; only `Info` is implemented, returning runtime name/version. `newTaskService` returns `exampleTaskService`, which implements `shim.TTRPCService` and the generated v2 task service. `RegisterTTRPC` installs the task service. Most task methods return `errdefs.ErrNotImplemented`; `Shutdown` calls `os.Exit(0)`.

There is no durable task state, process tracking, or filesystem persistence. Control flow demonstrates plugin initialization and ttrpc registration rather than real container lifecycle.

Dependencies include bootstrap v1, task v2 API, type protobufs, shim package, shutdown service, plugin registry, ttrpc, and errdefs. It integrates with `example/cmd/main.go`.

Risks are mostly educational: using this as production code would fail all lifecycle operations, and `Shutdown` exits the process immediately. Test signals are compile-time interface conformance and smoke tests that plugin registration and `-info` behavior work.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/example/example.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/logging/logging.go -->
# sources/cloud-native/containerd/core/runtime/v2/logging/logging.go

## Purpose
Defines the common runtime v2 external logging driver contract used by platform-specific launcher helpers.

## APIs, Flow, State, Dependencies, Risks, And Tests
`Config` carries container ID, namespace, stdout reader, and stderr reader. `LoggerFunc` is the callback signature implemented by a logging binary; it receives a context, config, and `ready` callback that must be invoked once setup is complete so the container can start.

There is no control flow or persistence in this common file. State is caller-provided stream handles and identity fields. Platform files implement `Run`.

Dependencies are only `context` and `io`. Integration points are external logging binaries and shim code that launches them with container IO and wait synchronization.

Risks include logger implementations forgetting to call `ready`, mishandling stream lifetime, or blocking startup. Test signals come from platform-specific `Run` tests and integration tests launching a logger binary through the shim.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/logging/logging.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/logging/logging_unix.go -->
# sources/cloud-native/containerd/core/runtime/v2/logging/logging_unix.go

## Purpose
Implements `logging.Run` for Unix platforms. It exposes inherited file descriptors and environment variables to a custom logging function and coordinates readiness through a wait pipe.

## APIs, Flow, State, Dependencies, Risks, And Tests
`Run(fn LoggerFunc)` builds a context, reads `CONTAINER_ID` and `CONTAINER_NAMESPACE`, wraps file descriptors 3 and 4 as stdout/stderr readers, and fd 5 as the wait pipe. It installs `SIGTERM` handling, runs the logger function in a goroutine, and exits with status 1 if the function returns an error or 0 on success. The `ready` closure writes one byte to the wait pipe then closes it.

State consists of inherited file descriptors and signal/context lifetime. No disk persistence occurs. Dependencies include `os`, `os/signal`, Unix signals, and the common logging contract.

Integration is with shim-launched logging binaries that receive container IO as fds. Risks include missing or invalid fds, logger goroutine blocking, repeated `ready` calls, and startup deadlock if `ready` is never called. Test signals should simulate fds/pipes, verify wait-byte behavior, and confirm signal cancellation and exit code paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/logging/logging_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/logging/logging_windows.go -->
# sources/cloud-native/containerd/core/runtime/v2/logging/logging_windows.go

## Purpose
Implements `logging.Run` for Windows logging binaries using named pipe paths supplied in environment variables.

## APIs, Flow, State, Dependencies, Risks, And Tests
`Run` delegates to `runInternal`, prints any returned error to stderr, and exits nonzero. `runInternal` requires `CONTAINER_STDOUT` and `CONTAINER_STDERR`, dials them with go-winio, dials `CONTAINER_WAIT`, builds `Config`, watches interrupt/SIGTERM, and invokes the logger function. `ready` writes a byte to the wait pipe then closes it.

State is the named pipe connections and signal-driven context. There is no disk persistence. Dependencies include `github.com/Microsoft/go-winio`, `net`, `os/signal`, and Windows syscall signals.

Integration mirrors Unix logging but the shim passes pipe names instead of inherited fds. Risks include missing env vars, pipe dial timeouts/failures, leaked connections if logger exits before readiness, and named-pipe behavior differences in multi-container shims. Test signals are unit tests for missing env var errors, fake pipe readiness, signal cancellation, and error propagation from `LoggerFunc`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/logging/logging_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/manager_unix.go -->
# sources/cloud-native/containerd/core/runtime/v2/manager_unix.go

## Purpose
Sets the default runtime v2 task-manager platform list for non-Windows builds.

## APIs, Flow, State, Dependencies, Risks, And Tests
`defaultPlatforms` returns a single entry: `platforms.DefaultString()`. It is used by `TaskConfig` during runtime plugin registration.

There is no persistence or complex control flow. The dependency is `github.com/containerd/platforms`. Integration is with plugin metadata, which advertises supported platforms.

Risk is incorrect platform advertising if cross-platform support changes. Test signal is plugin initialization metadata on Unix builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/manager_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/manager_windows.go -->
# sources/cloud-native/containerd/core/runtime/v2/manager_windows.go

## Purpose
Sets the default runtime v2 task-manager platform list for Windows builds.

## APIs, Flow, State, Dependencies, Risks, And Tests
`defaultPlatforms` returns `platforms.DefaultString()` plus `"linux/amd64"`, allowing Windows containerd configurations to advertise the native platform and Linux/amd64 support for compatible runtime scenarios.

The file has no persistent state. It integrates through `TaskConfig` plugin registration. Dependencies are limited to `github.com/containerd/platforms`.

Risks include over-advertising Linux support where no Linux runtime is configured. Test signals are Windows plugin metadata checks and platform selection integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/manager_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/process.go -->
# sources/cloud-native/containerd/core/runtime/v2/process.go

## Purpose
Implements `runtime.ExecProcess` for additional processes inside a shim-managed task and shared status conversion from task protobuf status to runtime status.

## APIs, Flow, State, Dependencies, Risks, And Tests
`process` holds an exec ID and parent `shimTask`. Methods translate runtime operations to shim task RPCs with `ExecID`: `Kill`, `State`, `ResizePty`, `CloseIO`, `Start`, `Wait`, and `Delete`. `statusFromProto` maps created/running/stopped/paused/pausing statuses to runtime statuses.

There is no local persistence; process state is retrieved from or mutated by the shim. RPC errors are converted with `errgrpc.ToNative`, and closed ttrpc connections map state lookup to `ErrNotFound`.

Dependencies include task v3 API, task status types, errdefs/errgrpc, ttrpc, runtime interfaces, and protobuf timestamp conversion. Integration is through `shimTask.Exec` and `shimTask.Process`.

Risks include an empty or wrong exec ID targeting the wrong process, unmapped status values becoming zero-value status, and differences between ttrpc closed errors and gRPC failures. Test signals include fake task-client tests for every method, error conversion checks, and lifecycle integration for exec start/wait/delete.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/process.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim.go -->
# sources/cloud-native/containerd/core/runtime/v2/shim.go

## Purpose
Defines shim connection, bootstrap parsing, cleanup on shim death, shim instance lifecycle, and the `runtime.Task` adapter backed by the shim task service.

## APIs, Flow, State, Dependencies, Risks, And Tests
Important APIs include timeout constants, `loadShim`, `cleanupAfterDeadShim`, `ShimInstance`, `clientVersionDowngrader`, `parseStartResponse`, `writeBootstrapParams`, `readBootstrapParams`, `makeConnection`, `grpcDialContext`, `shim`, `grpcConn`, `newShimTask`, and all `shimTask` runtime task methods. `parseStartResponse` accepts current protobuf bootstrap output and legacy JSON/raw-address output, normalizing to version/protocol/address while rejecting future versions. `makeConnection` creates ttrpc or gRPC clients and wires close callbacks.

`shimTask` methods convert runtime operations to task v3 API calls: create, start, pause, resume, kill, exec, pids, resize, close IO, wait, checkpoint, update, stats, process lookup, state, delete, and shutdown. Delete carefully handles duplicate event risks, sandboxed shim shutdown rules, connection close waiting, and bundle deletion. Create can unpack a checkpoint rootfs diff archive before restoring.

State persists through bundle directories and `bootstrap.json`; live state is client connection, version, address, and shim-owned task state. Dependencies span bootstrap/task APIs, events, errdefs, ttrpc/gRPC, OpenTelemetry interceptors, archive/compression, atomicfile, shim dialer, timeout, and runtime interfaces.

Risks include duplicate exit/delete events, leaked shim processes after shutdown failures, incorrect v2/v3 downgrade behavior, unsupported future bootstrap versions, rootfs diff unpack errors, and different close semantics between transports. Test signals include bootstrap parsing/migration tests, connection integration tests, task method mapping, shim death cleanup event tests, and restore/checkpoint paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_load.go -->
# sources/cloud-native/containerd/core/runtime/v2/shim_load.go

## Purpose
Reloads existing shim processes from the runtime state directory after containerd restarts and cleans stale work directories.

## APIs, Flow, State, Dependencies, Risks, And Tests
`LoadExistingShims` scans namespace directories in `stateDir`, calls `loadShims` per namespace, and then `cleanupWorkDirs` in the persistent root. `loadShims` scans bundle directories concurrently, skips hidden entries, drops empty or unreadable bundles, and calls `m.loadShim`. `m.loadShim` resolves the runtime from `shim-binary-path` or container metadata, reconnects to the shim via `loadShimTask`, and cleans leaked shims that have no sandbox record and no process list. `loadShimTask` verifies task service connectivity via `PID`, downgrading client version on `ErrNotImplemented`. `cleanupWorkDirs` removes root work dirs that have no live shim.

State inputs are filesystem bundle directories, optional `shim-binary-path`, bootstrap files, metadata container records, sandbox records, and the in-memory namespace shim map. Cleanup mutates bundle/work directories and may publish cleanup events through dead-shim cleanup.

Dependencies include namespaces, mount unmounting, errgroup concurrency, runtime `GOMAXPROCS`, metadata stores, shim binary deletion, and timeouts.

Risks include deleting bundles that are temporarily unreadable, failing to load one namespace while continuing others, races with live shim exit, wrong runtime resolution after metadata loss, and stale workdir removal after state loss. Tests should cover restart reload, empty bundle cleanup, legacy bootstrap migration, leaked shim cleanup, and namespace isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_load.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_manager.go -->
# sources/cloud-native/containerd/core/runtime/v2/shim_manager.go

## Purpose
Registers and implements the v2 shim manager plugin, which resolves shim binaries, starts or reuses shim instances, tracks them by namespace, and exposes cleanup/delete operations.

## APIs, Flow, State, Dependencies, Risks, And Tests
`ShimConfig` configures environment and socket directory. Plugin init validates or chooses a short socket dir, opens metadata/event stores, and returns `NewShimManager`. `ManagerConfig` and `ShimManager` hold containerd addresses, env, runtime path cache, shim map, event exchange, container store, sandbox store, and shim info cache.

`Start` decides whether to reuse a sandbox shim or invoke a shim binary. It uses sandbox metadata/address/version when possible, writes `sandbox` and `bootstrap.json` into the task bundle for sandbox reuse, otherwise calls `startShim`. `startShim` resolves the runtime path, builds a shim binary command wrapper, starts it with runtime options, and installs dead-shim cleanup callbacks. `restoreBootstrapParams` migrates legacy `address` files into `bootstrap.json`. `resolveRuntimePath` accepts absolute executable paths, rejects relative paths, resolves runtime names to shim binary names, and caches results. `loadShimInfo` calls runtime `-info` and extracts mount types handled by custom shims.

Persistent state includes bundle files `sandbox`, `bootstrap.json`, optional legacy `address`, and runtime path cache in memory. Dependencies include plugin registry, metadata stores, events, sandbox store, shim binary helpers, typeurl, timeout, and versioned config migration.

Risks include socket path limits, stale runtime path cache after upgrades, misdetecting sandbox API support, duplicate cleanup callbacks, and legacy config migration surprises. Tests include runtime path resolution, sandbox reuse/invocation integration, bootstrap migration, mount annotation handling, and plugin config migration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_test.go -->
# sources/cloud-native/containerd/core/runtime/v2/shim_test.go

## Purpose
Tests bootstrap response parsing and legacy bootstrap file migration behavior.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TestParseStartResponse` checks raw address output, JSON bootstrap responses for ttrpc/gRPC, malformed legacy JSON falling back to raw-address ttrpc, and unsupported future versions returning `ErrNotImplemented`. `TestRestoreBootstrapParams` writes a legacy `address` file, calls `restoreBootstrapParams`, and confirms `bootstrap.json` is written and readable with version 2/ttrpc values.

The tests mutate temporary directories only. Dependencies include bootstrap API, errdefs, and testify require.

These tests guard the compatibility surface for old shim binaries and the migration path used during reload. Remaining gaps include protobuf bootstrap parsing, invalid `bootstrap.json` content, and filesystem write failure cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_unix.go -->
# sources/cloud-native/containerd/core/runtime/v2/shim_unix.go

## Purpose
Provides non-Windows shim logging pipe behavior and default socket-directory selection.

## APIs, Flow, State, Dependencies, Risks, And Tests
`openShimLog` opens `bundle.Path/log` as a FIFO with read/write, create, and nonblocking flags. `checkCopyShimLogError` suppresses expected read-closed/closed errors only when the context has been canceled. `defaultSocketDir` chooses a short socket directory: root uses `/run/containerd/s`; non-root tries that, `$XDG_RUNTIME_DIR/containerd/s`, `/run/<uid>/containerd/s`, then `/tmp/containerd-s-<uid>`. `ensureSocketDir` creates a directory, verifies ownership, and normalizes mode to `0700`.

State changes are filesystem directory creation/chmod and FIFO creation. Dependencies include containerd defaults, fifo package, Unix syscalls, and user ownership checks.

Integration points are shim log copying and shim manager socket dir selection. Risks include failure to find a short owned directory, FIFO open semantics causing synchronization issues, and ignoring only the correct expected log-copy errors. Test signals include `TestCheckCopyShimLogError`, socket dir ownership/mode tests, and rootless startup integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_unix_test.go -->
# sources/cloud-native/containerd/core/runtime/v2/shim_unix_test.go

## Purpose
Validates Unix shim log copy error filtering.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TestCheckCopyShimLogError` checks that before context cancellation, `fifo.ErrReadClosed` and nil are returned unchanged. After cancellation, `fifo.ErrReadClosed` and `os.ErrClosed` are suppressed to nil, while nil and unrelated FIFO errors remain unchanged.

The test has no persistence. It depends on context cancellation, `os`, and `github.com/containerd/fifo`.

This guards against noisy logs during expected shutdown while preserving real copy errors. A notable edge is that the test expects nil to remain nil after cancellation, which is both suppression-compatible and normal behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_windows.go -->
# sources/cloud-native/containerd/core/runtime/v2/shim_windows.go

## Purpose
Provides Windows shim log pipe reconnection and default shim socket directory behavior.

## APIs, Flow, State, Dependencies, Risks, And Tests
`deferredPipeConnection` implements an `io.ReadCloser` whose read/close wait for a background named-pipe dial to finish. `openShimLog` derives namespace from context and dials `\\.\pipe\containerd-shim-<namespace>-<id>-log` asynchronously. `checkCopyShimLogError` suppresses `os.ErrNotExist`, which is expected for secondary containers in multi-container shims that do not have separate log pipes. `defaultSocketDir` returns the default state `s` directory.

State is the deferred network connection and any dial error. No disk state is mutated here. Dependencies include named pipe dialer behavior supplied by shim client code, namespaces, sync wait groups/once, and defaults.

Risks include delayed dial errors surfacing only on read/close, namespace absence preventing log open, and silently ignoring pipe-not-found cases that might hide unexpected missing logs. Test signals include Windows `checkCopyShimLogError` tests and integration tests for reconnecting shim logs across containerd restarts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_windows_test.go -->
# sources/cloud-native/containerd/core/runtime/v2/shim_windows_test.go

## Purpose
Tests Windows shim log copy error filtering.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TestCheckCopyShimLogError` verifies nil and arbitrary errors pass through unchanged, while `os.ErrNotExist` is converted to nil. It uses `t.Context()` and a synthetic error.

There is no persistent state. The test guards the multi-container shim behavior where some containers do not expose separate log pipes. Remaining gaps include exercising `deferredPipeConnection` and named-pipe dial failure behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/shim_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/socket_linux.go -->
# sources/cloud-native/containerd/core/runtime/v2/socket_linux.go

## Purpose
Defines the maximum shim socket directory length for Linux.

## APIs, Flow, State, Dependencies, Risks, And Tests
`maxSocketDirLen` is `42`, derived from Linux Unix-socket path limits after accounting for a slash and 64-character hash filename. There is no control flow or persistence.

The constant is consumed by shim manager config validation and Unix default socket directory selection. Risk is off-by-one behavior if socket naming changes. Test signals are socket path construction tests and plugin config validation for too-long `socket_dir`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/socket_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/socket_unix.go -->
# sources/cloud-native/containerd/core/runtime/v2/socket_unix.go

## Purpose
Defines the maximum shim socket directory length for non-Linux, non-Windows Unix builds.

## APIs, Flow, State, Dependencies, Risks, And Tests
`maxSocketDirLen` is `38`, derived from macOS-style Unix-socket path limits. It has no imports, state, or control flow.

The constant integrates with socket directory validation. Risks are platform assumptions for less common Unix targets. Test signals are build-tag compilation and socket path length validation tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/socket_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/socket_windows.go -->
# sources/cloud-native/containerd/core/runtime/v2/socket_windows.go

## Purpose
Defines the maximum shim socket directory length for Windows builds.

## APIs, Flow, State, Dependencies, Risks, And Tests
`maxSocketDirLen` is `42`, matching the Linux-derived calculation used by shim socket path construction. The file has no control flow or persistence.

It integrates with shim manager config validation. Risks are documentation/constant drift if Windows transport naming changes. Test signals are Windows build compilation and `socket_dir` length validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/socket_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/task_manager.go -->
# sources/cloud-native/containerd/core/runtime/v2/task_manager.go

## Purpose
Registers and implements the runtime v2 task manager plugin. It creates bundles, activates mounts, starts shims, creates shim tasks, lists/gets/deletes tasks, exposes runtime plugin info, and validates runtime feature support.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TaskConfig` carries platform strings. Plugin init parses platforms, exports supported log URI schemes, gets shim/mount/warning services, creates root/state dirs, reloads shims, emits platform warnings, and returns `TaskManager`. `NewTaskManager` is a direct constructor. `Create` builds a bundle, activates rootfs mounts with GC labels and shim-handled mount allowances, starts a shim, creates a `shimTask`, validates runtime features, calls task `Create`, and downgrades client version on `ErrNotImplemented`. Failure paths delete bundles, deactivate mounts, delete shim records, and try shim task cleanup. `Get`, `Tasks`, and `Delete` adapt shim map entries to runtime tasks. `PluginInfo` runs shim `-info`. `validateRuntimeFeatures` checks OCI idmap mounts against runtime feature output.

State includes root/state directories, active mount-manager entries, shim-manager namespace map, and bundle files. Dependencies include plugins, metadata services, mount manager, warning service, typeurl, OCI specs/features, runtime API, errdefs, and external shim binaries.

Risks include cleanup leaks on partial failures, mount activation races with duplicate task IDs, runc feature detection gaps, nil mount manager assumptions, and v2/v3 downgrade complexity. Test signals cover runtime path resolution, idmap feature validation, create/delete integration, mount activation/deactivation behavior, and plugin initialization metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/task_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/task_manager_linux.go -->
# sources/cloud-native/containerd/core/runtime/v2/task_manager_linux.go

## Purpose
Emits Linux-specific runtime task manager deprecation warnings.

## APIs, Flow, State, Dependencies, Risks, And Tests
`emitPlatformWarnings` checks cgroups mode and emits `deprecation.CgroupV1` through the warning service when not running unified cgroup v2. It does not persist state.

Dependencies are `github.com/containerd/cgroups/v3`, deprecation definitions, and the warning service. Integration is plugin initialization in `task_manager.go`.

Risks are warning spam or missed deprecation notice if cgroup mode detection changes. Test signals are mocked warning service checks under cgroup v1/v2 modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/task_manager_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/task_manager_others.go -->
# sources/cloud-native/containerd/core/runtime/v2/task_manager_others.go

## Purpose
Provides a no-op `emitPlatformWarnings` implementation for non-Linux builds.

## APIs, Flow, State, Dependencies, Risks, And Tests
The function accepts context and warning service but emits nothing. There is no state, persistence, or control flow beyond return.

It integrates with task manager plugin initialization through build tags. Risk is low; future non-Linux deprecations would need platform-specific logic. Test signal is cross-platform compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/task_manager_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/task_manager_test.go -->
# sources/cloud-native/containerd/core/runtime/v2/task_manager_test.go

## Purpose
Tests shim runtime path resolution for the task/shim manager.

## APIs, Flow, State, Dependencies, Risks, And Tests
`setupAbsoluteShimPath` creates an executable fake `containerd-shim-runc-v2` in a temp directory and prepends it to `PATH`. `TestResolveRuntimePath` checks absolute path resolution, runtime-name resolution through `exec.LookPath`, invalid absolute paths, empty names, relative paths, embedded slashes, and malformed runtime names.

State is limited to temp files and `PATH` environment mutation. The test depends on non-Windows/non-Darwin build tags and filesystem executable mode.

It guards against accepting unsafe relative shim paths and verifies expected runtime-name lookup. Gaps include cache invalidation behavior and side-by-side binary fallback via `os.Executable`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/task_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/bridge.go -->
# sources/cloud-native/containerd/core/sandbox/bridge.go

## Purpose
Provides a transport-neutral sandbox API client facade, allowing callers to use the ttrpc sandbox service interface against either ttrpc or gRPC clients.

## APIs, Flow, State, Dependencies, Risks, And Tests
`NewClient` returns a generated ttrpc sandbox client for `*ttrpc.Client` or a `grpcBridge` wrapping a generated gRPC client for `grpc.ClientConnInterface`. The bridge implements all sandbox service methods by forwarding to gRPC: create, start, platform, stop, wait, status, ping, shutdown, and metrics.

There is no persistence and only a stored gRPC client pointer. Dependencies include generated runtime sandbox v1 API, ttrpc, and gRPC.

Integration points are shim/sandbox controllers that need one client interface regardless of transport. Risks are unsupported client types and future sandbox API methods requiring bridge updates. Test signals are interface conformance, unsupported type tests, and method forwarding tests with fake gRPC/ttrpc clients.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/bridge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/controller.go -->
# sources/cloud-native/containerd/core/sandbox/controller.go

## Purpose
Defines the runtime sandbox controller interface, option types, and status/instance structs used to manage sandbox lifecycles.

## APIs, Flow, State, Dependencies, Risks, And Tests
`CreateOptions` carries rootfs mounts, marshaled sandbox options, network namespace path, and annotations. `WithRootFS`, `WithOptions`, `WithNetNSPath`, and `WithAnnotations` populate it. `StopOptions` and `WithTimeout` carry optional stop timeout. `Controller` defines create/start/platform/stop/wait/status/shutdown/metrics/update operations. `ControllerInstance`, `ExitStatus`, and `ControllerStatus` model returned runtime state.

The file defines contracts only; it does not persist state. Options marshal arbitrary values through typeurl, so type registration matters. Dependencies include mount types, metrics protobuf, typeurl, image-spec platform, and time.

Integration points are remote sandbox proxy controllers, shim sandbox implementations, CRI, and task manager sandbox reuse. Risks include ambiguous field update semantics, option marshal failures, timeout truncation in proxies, and controllers returning inconsistent address/version values. Test signals are option unit tests, controller conformance tests, and lifecycle integration with a real sandbox shim.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/helpers.go -->
# sources/cloud-native/containerd/core/sandbox/helpers.go

## Purpose
Converts between internal `sandbox.Sandbox` metadata and API protobuf `types.Sandbox`.

## APIs, Flow, State, Dependencies, Risks, And Tests
`ToProto` maps ID, runtime name/options, sandboxer, labels, timestamps, extensions, and spec to protobuf. Extensions and options/spec are converted through typeurl/protobuf `Any`. `FromProto` reverses the mapping into internal structs.

There is no persistence here; it transforms metadata objects passed to stores/controllers. Dependencies include containerd API types, protobuf timestamp helpers, gogo `Any`, and typeurl.

Integration points are sandbox store proxy, sandbox controller proxy, metadata store implementations, and API services. Risks include nil `Runtime` in protobuf causing panic, unregistered or opaque typeurl extensions, and shallow map reuse. Test signals should round-trip sandbox metadata with labels, timestamps, spec, runtime options, and extensions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/proxy/controller.go -->
# sources/cloud-native/containerd/core/sandbox/proxy/controller.go

## Purpose
Implements `sandbox.Controller` by proxying calls to the containerd sandbox controller gRPC API.

## APIs, Flow, State, Dependencies, Risks, And Tests
`NewSandboxController` stores a controller client and sandboxer name. `Create` applies create options, converts sandbox metadata to proto, and sends rootfs, options, netns path, annotations, sandbox metadata, and sandboxer. `Start`, `Platform`, `Stop`, `Shutdown`, `Status`, `Metrics`, and `Update` perform request/response mapping and native error conversion. `Wait` retries `Unavailable` gRPC errors with exponential backoff from 128 ms up to 4096 ms until success or context cancellation.

No local persistence exists. State is remote controller state and the sandboxer name. Dependencies include sandbox service API, mount proto conversion, typeurl, errgrpc/errdefs, metrics API, and image-spec platform.

Integration is the remote client path for sandbox lifecycle management. Risks include timeout seconds truncation, `Wait` returning the last unavailable error on context cancellation, missing sandboxer in `Update`, and backoff delaying cancellation responsiveness. Test signals include fake gRPC controller method mapping, unavailable retry behavior, field update propagation, and error conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/proxy/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/proxy/store.go -->
# sources/cloud-native/containerd/core/sandbox/proxy/store.go

## Purpose
Implements `sandbox.Store` by proxying sandbox metadata operations to the containerd sandbox store gRPC API.

## APIs, Flow, State, Dependencies, Risks, And Tests
`NewSandboxStore` wraps an API `StoreClient`. `Create`, `Update`, `Get`, `List`, and `Delete` build corresponding gRPC requests, convert sandbox metadata to/from protobuf with `sandbox.ToProto` and `sandbox.FromProto`, and convert gRPC errors to native errdefs.

The proxy holds no persistent local state; all metadata persistence is remote. Dependencies are sandbox service API, errgrpc, and internal sandbox helper conversion.

Integration points are clients managing sandbox records over the API service. Risks include conversion panics on malformed protobufs, field mask mismatch in `Update`, and remote filtering semantics in `List`. Test signals are fake store client tests for request shapes, error conversion, list conversion, and field path forwarding.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/proxy/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/store.go -->
# sources/cloud-native/containerd/core/sandbox/store.go

## Purpose
Defines the sandbox metadata model, runtime options, store interface, and helper methods for labels/extensions.

## APIs, Flow, State, Dependencies, Risks, And Tests
`Sandbox` stores ID, labels, runtime options, spec, sandboxer name, timestamps, and typed extensions. `RuntimeOpts` stores runtime name/options. `Store` defines create/update/get/list/delete. `AddExtension` initializes the extensions map and marshals arbitrary objects with typeurl. `GetExtension` unmarshals by name and returns `ErrNotFound` when absent. `AddLabel` and `GetLabel` manage labels.

This file defines persistent metadata shape but does not implement storage. Dependencies are context, time, errdefs, and typeurl.

Integration points are metadata DB stores, sandbox proxy store, task manager sandbox checks, and CRI sandbox metadata. Risks include typeurl registration requirements, callers mutating maps after store calls, missing label/extension semantics, and partial update field-name drift. Test signals are extension round-trip tests, label helper tests, and store implementation conformance.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/store_test.go -->
# sources/cloud-native/containerd/core/sandbox/store_test.go

## Purpose
Tests typed sandbox extension helper round-tripping.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TestAddExtension` registers a local `test` struct type with typeurl, adds it to a sandbox under key `"test"`, retrieves it into another struct value, and asserts the field value survived.

The test mutates only in-memory sandbox metadata. Dependencies include typeurl and testify assertions.

It verifies extension map initialization, marshal, unmarshal, and key lookup. Gaps include absent extension error tests, invalid type unmarshalling, and label helper tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/sandbox/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/benchsuite/benchmark.go -->
# sources/cloud-native/containerd/core/snapshots/benchsuite/benchmark.go

## Purpose
Declares the Linux-only `benchsuite` package companion file for snapshotter benchmarks.

## APIs, Flow, State, Dependencies, Risks, And Tests
The file contains only package declaration and license under `//go:build linux`. There are no functions, types, imports, state changes, or persistence.

It integrates with `benchmark_test.go` by establishing the package on Linux. The only risk is accidental build-tag/package drift. Test signal is successful Linux test package compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/benchsuite/benchmark.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/benchsuite/benchmark_test.go -->
# sources/cloud-native/containerd/core/snapshots/benchsuite/benchmark_test.go

## Purpose
Provides Linux benchmarks comparing native, overlay, and devmapper snapshotters across repeated layered writes, updates, deletes, prepares, mounts, and commits.

## APIs, Flow, State, Dependencies, Risks, And Tests
Package flags configure root paths and devmapper thin-pool device. `BenchmarkNative`, `BenchmarkOverlay`, and `BenchmarkDeviceMapper` create the selected snapshotter, defer cleanup, and call `benchmarkSnapshotter`. The benchmark builds 16 layers of 1 MiB file operations. For each benchmark iteration and layer, it prepares a snapshot, applies the layer through `mount.WithTempMount`, commits it, and accumulates durations for prepare, write, and commit. Extra timing lines are printed to stdout. `makeApplier`, `applierFn`, and `updateFile` generate random file operations and partial overwrites.

State includes benchmark root directories, snapshotter metadata/data, devmapper pools, and committed layer chains. Dependencies include native/overlay/devmapper snapshotters, mount helpers, fstest, crypto random, flags, atomic counters, logging, and testing.

Risks include destructive cleanup of configured roots, requiring real devmapper setup, accumulating snapshots across `b.N`, non-deterministic random data and time-based seeds, and stdout formatting coupling. Test signals are benchmark completion, per-phase timings, bytes/sec, and cleanup without leaked mounts/devices.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/benchsuite/benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/proxy/convert.go -->
# sources/cloud-native/containerd/core/snapshots/proxy/convert.go

## Purpose
Converts snapshot metadata and usage values between internal `snapshots` types and the snapshot service protobuf API.

## APIs, Flow, State, Dependencies, Risks, And Tests
`KindToProto` maps active/view to explicit proto values and defaults all other kinds to committed. `KindFromProto` maps active/view and defaults all other proto values to committed. `InfoToProto` maps name, parent, kind, created/updated timestamps, and labels. `InfoFromProto` reverses the mapping. `UsageFromProto` and `UsageToProto` convert inodes and size.

There is no persistence or side effect. Dependencies are snapshot service API, internal snapshot types, and protobuf timestamp helpers.

Integration points are proxy snapshotter RPC methods and any API service converting snapshot metadata. Risks include treating unknown kinds as committed, nil `Info` pointers panicking, and map aliasing. Test signals are round-trip conversion tests for all known kinds, timestamps, labels, and usage values, plus unknown-kind behavior tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/proxy/convert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/proxy/proxy.go -->
# sources/cloud-native/containerd/core/snapshots/proxy/proxy.go

## Purpose
Implements the `snapshots.Snapshotter` interface over the containerd snapshot gRPC API.

## APIs, Flow, State, Dependencies, Risks, And Tests
`NewSnapshotter` stores a `SnapshotsClient` and snapshotter name. Methods translate the snapshotter interface to RPCs: `Stat`, `Update`, `Usage`, `Mounts`, `Prepare`, `View`, `Commit`, `Remove`, `Walk`, `Close`, and `Cleanup`. Prepare/View/Commit apply local `snapshots.Opt` values into temporary `Info` to pass labels and parent. `Walk` consumes the streaming `List` RPC until EOF and calls the caller's walk function for each returned info.

The proxy has no local persistent state; remote snapshotter state is authoritative. Dependencies include snapshot service API, errgrpc, mount proto conversion, internal snapshots types, and protobuf field masks.

Integration points are remote containerd clients and services that expose snapshotters through gRPC. Risks include local option support limited to labels/parent, streaming errors mid-walk, callback errors aborting list processing, `Close` being a no-op, and remote cleanup semantics. Test signals are fake RPC mapping tests, walk streaming/EOF/error behavior, option propagation, and native error conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/proxy/proxy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/snapshotter.go -->
# sources/cloud-native/containerd/core/snapshots/snapshotter.go

## Purpose
Defines containerd's snapshotter contract, snapshot metadata structures, label constants, kind handling, cleanup interface, and creation options.

## APIs, Flow, State, Dependencies, Risks, And Tests
Constants define unpack key formats and snapshot labels, including UID/GID mappings and max-size hints. `Kind` models unknown/view/active/committed with parsing, string, and JSON marshal/unmarshal helpers. `Info` stores snapshot kind, name, parent, labels, and timestamps. `Usage` stores inode/size counts and `Add` combines usage values. `Snapshotter` defines stat, update, usage, mounts, prepare, view, commit, remove, walk, and close. `Cleaner` adds async cleanup. `WithLabels`, `FilterInheritedLabels`, and `WithParent` are option/helper functions.

The file is an interface/contract layer, not an implementation. Persistence semantics are documented: active/view/committed snapshots share one keyspace, active snapshots commit into immutable committed snapshots, and parent-child relationships constrain removal.

Dependencies are context, JSON, maps, strings, time, and containerd mount types. Integrations include all snapshotter plugins, metadata stores, proxy clients, unpack code, image layer import, and runtime rootfs preparation.

Risks include implementers violating lifecycle rules, callers relying on ignored max-size labels, unknown kinds mapping to unknown in JSON parsing, and inherited label filtering mistakes. Test signals are snapshotter conformance suites, kind JSON tests, label filtering tests, usage aggregation tests, and plugin integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/storage/bolt.go -->
# sources/cloud-native/containerd/core/snapshots/storage/bolt.go

## Purpose
Implements BoltDB-backed snapshot metadata operations used by snapshotter implementations: info lookup/update/walk, active/view creation, active commit, removal, parent-chain lookup, usage storage, and ID mapping.

## APIs, Flow, State, Dependencies, Risks, And Tests
The storage schema uses version bucket `v1`, child bucket `snapshots`, parent backlink bucket `parents`, and per-snapshot keys for id, parent, kind, usage inodes/size, timestamps, and labels. `GetInfo`, `UpdateInfo`, `WalkInfo`, `GetSnapshot`, `CreateSnapshot`, `Remove`, `CommitActive`, and `IDMap` are the public operations. Helpers encode parent composite keys, require a transaction in context, create buckets, follow parent chains, read/write snapshot info, read/write usage, and adapt info to filter fields.

Control flow is transaction-bound. Creation only accepts active/view and requires committed parents. Commit creates the committed bucket, reads active metadata, ensures active kind, replaces labels, optionally rebases only parentless actives, writes usage, deletes the active bucket, and updates parent backlinks. Removal refuses snapshots with children and removes parent backlinks. Walk parses filters and scans all snapshot buckets.

Persistence is strongly tied to Bolt bucket layout and transaction context. Dependencies include bbolt, boltutil timestamps/labels, filters, snapshots types, errdefs, binary varints, and time.

Risks include no operation without transaction, parent backlink corruption blocking removals or parent-chain reads, unknown filters, defaulting missing kind to unknown, inability to remove parents with active/view children, and commit creating destination before validating source. Test signals are the metastore suite for create/get/walk/commit/remove/parents/rebase plus benchmarks and crash-consistency tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/storage/bolt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/storage/bolt_test.go -->
# sources/cloud-native/containerd/core/snapshots/storage/bolt_test.go

## Purpose
Connects the generic metastore test and benchmark suites to the BoltDB `MetaStore` implementation.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TestMetastore` passes a temp `metadata.db` path to `NewMetaStore` and runs `MetaStoreSuite`. `BenchmarkSuite` does the same for `Benchmarks`. The blank `testutil` import ensures snapshot test flags are defined.

State is temporary Bolt database files created during tests/benchmarks. Dependencies include `filepath`, `testing`, and the local suite helpers.

The file verifies that the Bolt implementation satisfies the generic storage behavior. Risks are mostly in coverage: it delegates all assertions to the suite. Test signal is the full suite passing against real bbolt persistence.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/storage/bolt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/storage/metastore.go -->
# sources/cloud-native/containerd/core/snapshots/storage/metastore.go

## Purpose
Defines the transaction wrapper and lifecycle for a BoltDB-backed snapshot metadata store.

## APIs, Flow, State, Dependencies, Risks, And Tests
`Transactor` abstracts commit/rollback. `Snapshot` returns active/view metadata: kind, numeric ID, and ordered parent IDs. `Opt` customizes bbolt options. `MetaStore` stores db path, mutex, lazy-open database pointer, and options. `NewMetaStore` records dbfile and options. `TransactionContext` lazily opens the DB, begins a read or write transaction, and injects it into context with `transactionKey`. `WithTransaction` runs a callback and commits only if writable and callback succeeds; otherwise it rolls back, joining callback and transaction errors. `Close` closes the DB if open.

Persistent state is the Bolt database file; transactions are stored only in context. The mutex protects lazy opening and closing. Dependencies include bbolt, snapshots, log, context, errors, and sync.

Integration points are storage operations in `bolt.go` and snapshotter plugins that wrap metadata and filesystem operations atomically. Risks include callers forgetting rollback/commit when using `TransactionContext` directly, context key coupling, close while transactions are active, and callback side effects that must be cleaned after commit failure. Test signals are metastore suite and transaction open/close benchmarks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/storage/metastore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/storage/metastore_bench_test.go -->
# sources/cloud-native/containerd/core/snapshots/storage/metastore_bench_test.go

## Purpose
Defines generic benchmarks for snapshot metadata stores.

## APIs, Flow, State, Dependencies, Risks, And Tests
`Benchmarks` registers sub-benchmarks for stat active, stat committed, create active, remove, commit, get active parent chain, writable transaction open/close, and read transaction open/close. `makeBench` creates a metastore, opens one writable transaction for repeated operation benchmarks, and runs the benchmark function. Helper benchmarks create and remove snapshots around timed sections as needed. `getActiveBenchmark` builds a 10-deep committed parent chain and repeatedly resolves an active snapshot's parent IDs.

State is temporary database files and snapshot metadata inside benchmark transactions. Dependencies include testing, context, fmt, and snapshots types.

Risks include long-lived write transactions not representing real concurrent workloads, setup leakage into timing if `StopTimer` is missed, and benchmark keys reused intentionally with cleanup. Signals are ns/op for metadata operations and transaction overhead across implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/storage/metastore_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/storage/metastore_test.go -->
# sources/cloud-native/containerd/core/snapshots/storage/metastore_test.go

## Purpose
Provides a reusable behavioral test suite for snapshot metadata stores.

## APIs, Flow, State, Dependencies, Risks, And Tests
`MetaStoreSuite` registers tests for info lookup, empty/missing DB behavior, walk, active/view retrieval, create errors, commit errors, remove errors, parent ID ordering, and rebase behavior. Test wrappers create a temp metastore and run functions in read or write transactions. `basePopulate` creates committed, active, and view snapshots with parent relationships. Assertion helpers check errdefs categories. Individual tests validate kind/name/parent/timestamp/label equality, duplicate detection, parent must be committed, active commit preserves ID, views cannot commit, children block removal, parent IDs are ordered from immediate parent upward, and limited rebase is allowed only for parentless actives or unchanged parents.

State is temporary metastore data in real transactions. Dependencies include cmp, testify, errdefs, snapshots, context, and time.

Risks covered include inconsistent parent backlinks, wrong error categories, invalid commit/remove semantics, and broken timestamp handling. Gaps include process-crash tests and concurrent transaction tests. Passing this suite is the main correctness signal for a storage backend.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/storage/metastore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/testsuite/helpers.go -->
# sources/cloud-native/containerd/core/snapshots/testsuite/helpers.go

## Purpose
Provides shared helpers for snapshotter conformance tests that create, mount, mutate, commit, view, and compare snapshot chains.

## APIs, Flow, State, Dependencies, Risks, And Tests
`applyToMounts` creates a temp target, mounts provided mounts, applies a `fstest.Applier`, and unmounts. `createSnapshot` prepares a random active key, applies changes, commits it to a generated name, and returns that committed name. `checkSnapshot` creates a view of a committed snapshot, mounts it, and compares it to an expected directory. `checkSnapshots` applies a sequence of layers to both a real snapshotter and a flat temp directory, checking every committed layer. `checkInfo` compares snapshot metadata fields exactly.

State includes temp directories, active/view/committed snapshots in the supplied snapshotter, and mount lifecycle. Dependencies include mount helpers, fstest, randutil, os, and internal snapshot types.

Integration is with the broader snapshotter testsuite. Risks include leaked mounts on error, generated name collisions being unlikely but possible, and strict timestamp equality in `checkInfo`. Test signals are successful layered filesystem equality checks and cleanup of views/mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/testsuite/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/testsuite/issues.go -->
# sources/cloud-native/containerd/core/snapshots/testsuite/issues.go

## Purpose
Captures regression tests for historical filesystem layering bugs in snapshotter implementations.

## APIs, Flow, State, Dependencies, Risks, And Tests
`checkLayerFileUpdate` repeatedly verifies overwriting files and modes across layers, sleeping to cross timestamp boundaries. `checkRemoveDirectoryInLowerLayer` verifies removal/recreation of lower-layer directories. `checkChown` validates ownership changes except on Windows. `checkRename` returns a test function that accounts for overlay-style directory rename limitations while still testing file rename/overwrite cases. `checkDirectoryPermissionOnCommit` validates directory ownership/mode preservation across remove/recreate and commit. `checkStatInWalk` creates named snapshots and calls `Stat` from inside `Walk`. `createNamedSnapshots` builds a small committed/active/view graph.

State is all in the supplied snapshotter and temp work dirs through helper functions. Dependencies include fstest, runtime GOOS, strings, testing, time, and snapshots.

Integration is the snapshotter conformance suite. Risks covered include copy-up bugs, whiteout/remove behavior, chown/permission preservation, rename semantics, timestamp-sensitive failures, and deadlocks when statting during walk. Some listed TODO issue checks remain comments, not implemented tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/testsuite/issues.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/testsuite/mount.go -->
# sources/cloud-native/containerd/core/snapshots/testsuite/mount.go

## Purpose
Provides mount and unmount helpers for snapshotter tests, with optional integration through the containerd mount manager.

## APIs, Flow, State, Dependencies, Risks, And Tests
`withMountManager` creates a temp target root, opens a Bolt DB, constructs a mount manager, registers cleanup, and stores it in context. `mountAll` checks for a mount manager in context, tries `Activate` to transform mounts, falls back only on `ErrNotImplemented`, then calls `mount.All`. `unmountCtx` unmounts all mounts at the target and deactivates the mount manager entry, ignoring `ErrNotFound`. `unmountAll` is a test helper that fails the test on unmount errors. `umountflags` is zero.

State includes temp mount targets, a temporary mount-manager Bolt DB, active mount-manager records, and real OS mounts. Dependencies include bbolt, mount manager, errdefs, mount package, testing, and context values.

Risks include leaked mounts if cleanup order fails, context key misuse, requiring platform mount privileges/capabilities, and activation errors hiding mount transformations. Test signals are conformance tests passing with and without mount manager activation and cleanup leaving no mounts active.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/testsuite/mount.go -->
