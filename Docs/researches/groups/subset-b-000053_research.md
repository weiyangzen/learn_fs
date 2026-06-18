# Research Group: subset-b-000053

This grouped report covers the containerd client image/task helpers, the Linux `containerd-shim-runc-v2` implementation, `containerd-stress`, and selected daemon builtin/config registration files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/import.go -->
# Research: sources/cloud-native/containerd/client/import.go

## Purpose
Implements `Client.Import`, which ingests an image tar stream into the content store and creates/updates image records from the imported OCI index or manifest set. It is the client-side archive import path and complements remote pull/export operations.

## Important APIs, Control Flow, And State
`ImportOpt` configures reference translation, digest references, index naming, platform filtering, compression, layer discard labels, missing blob tolerance, image labels, and referrer handling. `Client.Import` applies options, creates a temporary lease with `WithLease`, imports content with `archive.ImportIndex`, walks descriptors from the top-level index, derives image names through `imageName`, optionally creates digest-named images, filters by platform, sets children/referrer/GC labels, then updates or creates image service records. Persistent state is in the content store, image store, descriptor labels, and optional referrer metadata; the lease protects temporary imported content while records are established.

## Dependencies And Integration
Depends on `core/content`, `core/images`, `core/images/archive`, `errdefs`, OCI descriptors, and `platforms`. It integrates with GC label propagation, image reference annotations, digest references, platform-specific imports, and content referrer providers.

## Risks And Test Signals
Risks include incomplete archives with `WithSkipMissing`, incorrect reference translation, skipped referrer images, platform filters dropping desired manifests, and shared image label maps being assigned to all output images. Tests should cover multi-platform indexes, referrer descriptors, digest reference callbacks, missing blobs, layer-discard labels, update-vs-create behavior, and lease cleanup on error.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/install.go -->
# Research: sources/cloud-native/containerd/client/install.go

## Purpose
Installs binaries and optionally libraries from an image into containerd's managed opt directory. It is a client helper for images that package executable components intended for local installation.

## Important APIs, Control Flow, And State
`Client.Install` resolves `InstallConfig`, finds the install path via explicit config or the introspection `opt` plugin export, selects platform-specific `bin`/`lib` layer paths, reads the image manifest for the client platform, streams each layer from the content store, decompresses it, filters tar entries, and applies selected entries into the target directory. On Windows it maps `Files\bin`/`Files\lib`, strips the `Files` prefix, and avoids preserving owner. Persistent state is direct filesystem writes under the opt path; content store reads are closed after each layer.

## Dependencies And Integration
Uses image manifest resolution, content readers, containerd archive apply/filter code, compression detection, OS path handling, and introspection plugin exports. It integrates with the daemon opt service contract documented by managed opt.

## Risks And Test Signals
Risks include path traversal or tar metadata assumptions delegated to archive apply, partial installs when a later layer fails, replace protection races around `os.Lstat`, and platform path differences. Tests should cover explicit path versus opt plugin discovery, replace refusal, lib inclusion, decompression errors, Windows path rewrites, and cleanup/close behavior on errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/install.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/install_opts.go -->
# Research: sources/cloud-native/containerd/client/install_opts.go

## Purpose
Defines the small option surface for `Client.Install`, separating install policy from the layer extraction implementation.

## Important APIs, Control Flow, And State
`InstallOpts` mutates an `InstallConfig` containing `Libs`, `Replace`, and `Path`. `WithInstallLibs` enables library extraction, `WithInstallReplace` permits overwriting existing files, and `WithInstallPath` overrides opt-service path discovery. There is no external state or control flow beyond deterministic in-memory mutation of the config struct.

## Dependencies And Integration
This file has no imports. It is consumed by `install.go` and public callers of the client package. The option values directly drive archive filtering and overwrite checks.

## Risks And Test Signals
The main risk is semantic drift with `Install` if new install behavior is added without extending the config. Tests should validate default zero values, option composition order, and that options affect extraction behavior as expected.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/install_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/lease.go -->
# Research: sources/cloud-native/containerd/client/lease.go

## Purpose
Provides a convenience helper for attaching a containerd lease to a context so content and snapshot mutations are protected from garbage collection during multi-step client operations.

## Important APIs, Control Flow, And State
`Client.WithLease` checks whether the context already carries a lease and returns a no-op cleanup if so. Otherwise it creates a lease through `LeasesService`, using a random ID and 24-hour expiration by default when no options are supplied, stores the lease ID in the returned context, and returns a cleanup function that deletes the lease. Persistent state is the lease record in the lease manager; callers own invoking cleanup.

## Dependencies And Integration
Depends on `core/leases`, `context`, and `time`. It is used by import, pull, checkpoint, and other content-producing flows to bridge several service calls safely.

## Risks And Test Signals
Risks include leaked leases if callers ignore the cleanup function, premature GC if a caller uses the original context, and custom options that omit useful expiration. Tests should cover existing lease passthrough, default lease creation, custom options, deletion errors, and behavior when lease creation fails.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/lease.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/namespaces.go -->
# Research: sources/cloud-native/containerd/client/namespaces.go

## Purpose
Adapts the gRPC namespace service client into the `namespaces.Store` interface used by containerd client and in-memory service code.

## Important APIs, Control Flow, And State
`NewNamespaceStoreFromClient` returns `remoteNamespaces`. `Create` sends labels after converting them to protobuf field values. `Labels` fetches namespace metadata and converts labels back to strings. `SetLabel` builds an update request with field paths for one label key and deletes a label when value is empty. `List` returns names from the service response. `Delete` applies namespace delete options into the request. Persistent state lives in the daemon namespace service, not this adapter.

## Dependencies And Integration
Uses `api/services/namespaces/v1`, `errgrpc`, package `namespaces`, and protobuf value helpers. It is wired by `services.go` for remote clients and by callers needing a namespace store abstraction.

## Risks And Test Signals
Risks include incorrect field paths for label updates, empty value semantics surprising callers, and gRPC error conversion gaps. Tests should cover create/list/delete, label conversion, single-label set/unset, delete options, and native error mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/namespaces.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/process.go -->
# Research: sources/cloud-native/containerd/client/process.go

## Purpose
Defines the public `Process` abstraction for exec processes and implements the client-side wrapper that talks to the task service for lifecycle, IO, terminal, wait, and status operations.

## Important APIs, Control Flow, And State
`Process`, `ExitStatus`, and `process` cover ID, PID, start, kill, wait, delete, IO close, resize, IO access, and status. `Start` sends `StartRequest` with `ExecID`, records the PID, and closes/cancels IO on failure. `Kill`, `CloseIO`, `Resize`, and `Status` delegate to task service requests with gRPC error conversion. `Wait` starts a goroutine and returns a one-shot channel carrying either exit code/time or an error with `UnknownExitStatus`. `Delete` runs deletion options, rejects running/paused states, deletes the exec process, and then cancels/waits/closes IO. State is local PID/IO fields plus remote shim task state.

## Dependencies And Integration
Uses task service protobufs, `cio`, tracing, protobuf timestamp conversion, `errdefs`, and `errgrpc`. It is returned by `Task.Exec` and `Task.LoadProcess`.

## Risks And Test Signals
Risks include leaked IO on start/delete errors, waits blocked by caller context, state races between status and delete, and signal/exec ID confusion. Tests should cover start failure cleanup, wait error paths, delete preconditions, IO close stdin behavior, resize requests, and status mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/process.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/pull.go -->
# Research: sources/cloud-native/containerd/client/pull.go

## Purpose
Implements high-level image pulling: resolve a remote reference, fetch content, optionally unpack it into snapshots, then create/update an image record and return a platform-bound `Image`.

## Important APIs, Control Flow, And State
`Client.Pull` builds a `RemoteContext`, configures resolver transfer options, validates single-platform local pull semantics, starts tracing, creates a lease, optionally initializes an `unpack.Unpacker`, wraps handlers so content can be unpacked as it is fetched, calls `fetch`, waits for deferred unpack, creates or updates the image with `createNewImage`, and falls back to `Image.Unpack` when the unpacker saw no unpackable manifests. `fetch` resolves/fetches through a resolver, rejects Docker schema 1, builds a handler chain for fetching, legacy config detection, children/platform filtering, labels, referrers, distribution source labels, and optional wrapper, dispatches descriptors, converts legacy Docker manifests when needed, and returns an image target. Persistent state includes content blobs, labels, snapshots, and image records.

## Dependencies And Integration
Uses remotes, Docker resolver helpers, transfer options, unpack, platform matching, tracing, image handlers, semaphores, and errdefs. It is the main client entry point for remote image ingestion.

## Risks And Test Signals
Risks include platform selection errors, unsupported schema 1 references, handler wrapper ordering, unpack wait errors surfaced after fetch, concurrent image create/update races, and all-metadata behavior. Tests should cover resolver option propagation, multi-platform rejection, unpack success/fallback, referrers, legacy conversion, distribution labels, and image update races.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/sandbox.go -->
# Research: sources/cloud-native/containerd/client/sandbox.go

## Purpose
Adds a high-level client API for sandbox metadata and sandbox controller lifecycle, including creating containers associated with a sandbox.

## Important APIs, Control Flow, And State
`Sandbox` exposes ID, metadata, labels, container creation, start, stop, wait, and shutdown. `sandboxClient` stores the owning `Client` and `api.Sandbox` metadata. `Client.NewSandbox` validates ID, resolves the default sandboxer, initializes timestamps, applies `NewSandboxOpts`, writes metadata to `SandboxStore`, then calls the sandbox controller `Create`. `Shutdown` first asks the controller to shut down and then deletes metadata, ignoring not-found errors. Options set runtime/typeurl options, apply and marshal OCI specs, attach extensions, and set labels. State spans the sandbox store and sandbox controller implementation.

## Dependencies And Integration
Depends on `core/sandbox`, containers metadata, OCI spec helpers, typeurl, protobuf empty types, and errdefs. It integrates with `Client.NewContainer` through `WithSandbox`.

## Risks And Test Signals
Risks include metadata created before controller create failure, stale metadata on partial failures, option marshaling failures, and shutdown idempotency. Tests should cover empty IDs, default sandboxer resolution, spec option application, runtime/extension encoding, container creation with sandbox label, wait errors, and not-found shutdown handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/sandbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/services.go -->
# Research: sources/cloud-native/containerd/client/services.go

## Purpose
Centralizes client service dependencies and provides option helpers for injecting remote or in-memory service implementations.

## Important APIs, Control Flow, And State
The internal `services` struct holds content, images, containers, namespace, snapshotter map, task, diff, events, leases, introspection, sandbox, transfer, and mount services. `ServicesOpt` setters populate those fields; remote gRPC clients are wrapped into store abstractions where needed. `WithSnapshotters` defensively copies the supplied map. `WithInMemoryServices` retrieves required plugin instances from a plugin `InitContext`, maps service plugin names to typed client/store wrappers, and installs the populated `services` struct into client options. State is dependency wiring only; no external persistence occurs here.

## Dependencies And Integration
Uses generated service clients, core service interfaces, plugin registry types, service name constants, and package `maps`. It is the bridge for CRI or other plugins embedding a client without dialing the daemon over gRPC.

## Risks And Test Signals
Risks include panics from wrong plugin instance types, missing service plugin keys, stale service-name mappings, and accidental sharing if future map fields are not copied. Tests should cover each setter, snapshotter map isolation, in-memory service resolution, missing plugin errors, and type assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/services.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/signals.go -->
# Research: sources/cloud-native/containerd/client/signals.go

## Purpose
Resolves container stop signals from container labels or OCI image config, providing a normalized helper for shutdown behavior.

## Important APIs, Control Flow, And State
`StopSignalLabel` names the containerd label `io.containerd.image.config.stop-signal`. `GetStopSignal` reads container labels and parses the label value with `moby/sys/signal`, falling back to a supplied default signal. `GetOCIStopSignal` validates the default string, reads the image config descriptor, verifies it is a known config media type, reads the config blob, unmarshals `v1.Image`, and returns `Config.StopSignal` or the default. There is no persistent mutation; the functions read labels and content blobs.

## Dependencies And Integration
Uses client `Container` and `Image` interfaces, content reads, image media type helpers, OCI image spec JSON, and signal parsing. It integrates with stop/kill workflows that need image-authored stop signal semantics.

## Risks And Test Signals
Risks include invalid signal strings, unknown config media types, malformed config blobs, and label values overriding defaults unexpectedly. Tests should cover missing labels/config signals, invalid defaults, named and numeric signals, config media validation, and content read/unmarshal errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/signals.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/snapshotter_opts_unix.go -->
# Research: sources/cloud-native/containerd/client/snapshotter_opts_unix.go

## Purpose
Implements Unix snapshotter options for user namespace ID remapping and fallback snapshot creation when a snapshotter cannot perform ID-mapped mounts directly.

## Important APIs, Control Flow, And State
`WithRemapperLabels` and `WithUserNSRemapperLabels` encode UID/GID maps into snapshot labels. `resolveSnapshotOptions` fetches snapshotter capabilities, returns the parent unchanged if `remap-ids` is supported or no remap labels are requested, rejects `only-remap-ids` hosts without idmap mount support, unmarshals labels into a `userns.IDMap`, validates a root mapping, computes a stable `remappedSnapshot` digest ID, reuses an existing remapped snapshot when present, otherwise prepares a temporary `-remap` snapshot, calls `remapRootFS`, commits it, and returns the new parent ID. Persistent state is a committed snapshot keyed by the digest of parent and sorted ID maps.

## Dependencies And Integration
Uses snapshots, internal user namespace helpers, OCI runtime ID mappings, digest generation, JSON, and `slices`. It is invoked during snapshot option resolution for task/container rootfs preparation.

## Risks And Test Signals
Risks include expensive fallback chown/remap, partial prepared snapshots after commit failure, mutable sorting of IDMap slices in `ID`, capability interpretation errors, and missing root mapping. Tests should cover capability branches, label parsing failures, stable ID generation, existing snapshot reuse, prepare/remap/commit cleanup, and root-map validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/snapshotter_opts_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/snapshotter_opts_windows.go -->
# Research: sources/cloud-native/containerd/client/snapshotter_opts_windows.go

## Purpose
Provides the Windows build of snapshot option resolution, where Unix user namespace remapping logic is not applicable.

## Important APIs, Control Flow, And State
`resolveSnapshotOptions` accepts the same signature as the Unix implementation but simply returns the parent snapshot key unchanged. It performs no option inspection, no capability probing, and no persistent mutation.

## Dependencies And Integration
Depends only on `context` and `core/snapshots` for signature compatibility. It is selected by Go build tags on Windows and lets shared client code compile without Unix remap behavior.

## Risks And Test Signals
The primary risk is callers expecting remap labels to have an effect on Windows. Build tests should ensure the Windows implementation remains signature-compatible; behavioral tests should assert it is a no-op.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/snapshotter_opts_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/task.go -->
# Research: sources/cloud-native/containerd/client/task.go

## Purpose
Defines the client-side `Task` API for init process lifecycle, exec processes, metrics, resource updates, checkpointing, and OCI spec access.

## Important APIs, Control Flow, And State
The file defines process statuses, IO close info, checkpoint/task/update structs, `TaskInfo`, and the `Task` interface. `task` methods delegate to the task service for start, kill, pause/resume, status, wait, delete, exec, pids, close IO, resize, metrics, checkpoint, update, and process loading. Deletion checks stopped-like state, handles Windows-created PID 0 exceptions, cancels/waits/closes IO carefully, and converts errors. `Exec` creates IO before sending the exec request and cleans it on failure. `Checkpoint` creates a lease, optionally pauses/resumes the task, asks runtime for checkpoint descriptors, optionally includes image and RW snapshot descriptors, writes an OCI index, and creates a checkpoint image unless options dump to a direct path. Persistent state includes runtime task state, content descriptors, checkpoint image records, RW snapshot diffs, and local IO handles.

## Dependencies And Integration
Uses task service protobufs, runc options, typeurl, content/diff/images/mount/rootfs, OCI specs, `cio`, tracing, errdefs, and plugin runtime constants. It is the main client abstraction over shim task services.

## Risks And Test Signals
Risks include task deletion while still running, IO leaks, checkpoint pause/resume failures, wrong runtime option unmarshaling, metrics nil handling, and races during image create. Tests should cover lifecycle calls, exec cleanup, delete preconditions, checkpoint variants, update resource type encoding, metrics not-found handling, and process loading.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/task.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/task_opts.go -->
# Research: sources/cloud-native/containerd/client/task_opts.go

## Purpose
Defines option functions for creating, restoring, checkpointing, deleting, killing, and updating tasks.

## Important APIs, Control Flow, And State
`NewTaskOpts` mutates `TaskInfo` for rootfs mounts, runtime binary path, task API endpoint, checkpoint restore image, CRIU image path, and work path. `WithTaskAPIEndpoint` also fills deprecated runc option fields for compatibility when possible. `WithTaskCheckpoint` decodes an OCI index from an image and selects the `MediaTypeContainerd1Checkpoint` descriptor. `WithProcessKill` waits, sends SIGKILL with `WithKillAll`, tolerates not-found/failed-precondition cases, and waits for exit before deletion continues. `WithResources` validates Linux or Windows resource structs for updates. State changes are in-memory option structs plus process kill side effects for deletion.

## Dependencies And Integration
Uses task/checkpoint structs from `task.go`, runc options, content image decoding, mounts, runtime specs, syscall signals, and errdefs. These options plug into `Container.NewTask`, `Task.Checkpoint`, `Task.Delete`, `Task.Kill`, and `Task.Update`.

## Risks And Test Signals
Risks include incompatible runtime option types, checkpoint images missing expected descriptors, force-kill waits that can block until context cancellation, and unsupported resource types. Tests should cover option mutation, backward-compatible endpoint fields, checkpoint selection, process kill edge cases, and resource validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/task_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/task_opts_unix.go -->
# Research: sources/cloud-native/containerd/client/task_opts_unix.go

## Purpose
Provides Unix-specific task creation options for runc behavior, shim cgroups, and IO ownership.

## Important APIs, Control Flow, And State
`WithNoNewKeyring` and `WithNoPivotRoot` fetch or initialize runc options through `TaskInfo.getRuncOptions` and set `NoNewKeyring` or `NoPivotRoot`. `WithShimCgroup` records the shim cgroup path. `WithUIDOwner` and `WithGIDOwner` set `IoUid` and `IoGid` used by the shim when creating IO FIFOs/pipes. The file mutates task creation option state only; runtime effects occur later in shim/runc create.

## Dependencies And Integration
Depends on `context` and shared task/runc option structures. It integrates with Linux shim create options and manager cgroup placement.

## Risks And Test Signals
Risks include errors if task runtime options are not runc options, invalid cgroup paths, and IO ownership mismatches. Tests should cover option mutation, existing runtime options preservation, and invalid runtime option formats.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/task_opts_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/transfer.go -->
# Research: sources/cloud-native/containerd/client/transfer.go

## Purpose
Exposes generic transfer service operations from the client and supplies a stream creator for transfer proxying.

## Important APIs, Control Flow, And State
`Client.Transfer` passes arbitrary source and destination objects plus transfer options into `c.TransferService().Transfer`. `streamCreator` constructs a streaming proxy creator from `c.streamingClient`, letting transfer implementations create streams through the client connection. There is no local persistence; state mutation depends on the selected transfer source/destination and service implementation.

## Dependencies And Integration
Uses `core/transfer`, `core/streaming`, and transfer/stream proxy packages. It integrates with image/content transfer implementations that may use gRPC streaming through the client.

## Risks And Test Signals
Risks are mostly type-contract errors from arbitrary `any` sources/destinations and stream setup failures. Tests should cover service delegation, option forwarding, stream creator behavior, and failure propagation from transfer implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/transfer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/main.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/main.go

## Purpose
Entrypoint for the Linux runc v2 shim binary.

## Important APIs, Control Flow, And State
`main` calls `shim.RunShim(context.Background(), manager.NewShimManager("io.containerd.runc.v2"))`. The blank import of the task plugin registers the shim task service. Runtime state is managed by the shim framework and manager/service implementations, not this file.

## Dependencies And Integration
Depends on the shim package, runc shim manager, and task plugin registration. It is invoked both as a bootstrap manager binary and as the long-lived shim process spawned by `manager.Start`.

## Risks And Test Signals
Risks are registration/name mismatches and build-tag/platform assumptions. Smoke tests should start the shim through containerd, confirm the runtime name is recognized, and verify the task service is registered.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/main_tracing.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/main_tracing.go

## Purpose
Adds optional tracing and pprof side-effect registrations to the shim binary when built with the `shim_tracing` tag.

## Important APIs, Control Flow, And State
The file contains only blank imports for `internal/pprof` and `pkg/tracing/plugin`. Those package initializers register profiling/tracing behavior. There is no direct code path, local state, or persistence in this file.

## Dependencies And Integration
Controlled by the `shim_tracing` build tag. It integrates with containerd's plugin initialization model and observability tooling for shim processes.

## Risks And Test Signals
Risks include unexpected profiling surface or dependency changes in tracing builds. Build tests with and without `shim_tracing` should verify the binary compiles and observability plugins initialize only under the tag.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/main_tracing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/manager/manager_linux.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/manager/manager_linux.go

## Purpose
Implements the Linux runc v2 shim manager used by containerd to bootstrap shim processes, report runtime info, and force-stop orphaned containers.

## Important APIs, Control Flow, And State
`NewShimManager` returns a `shim.Shim`. `Start` builds an exec command for the current binary with namespace/id/address flags, reads bundle `config.json` annotations to choose a grouping socket, creates one or two inherited Unix sockets, locks the OS thread for optional sched-core setup, starts the shim, optionally joins a configured shim cgroup, adjusts OOM score, and returns bootstrap protocol/address. `Stop` reconstructs bundle path and runc options, force-deletes the runc container, unmounts rootfs, and returns synthetic SIGKILL status. `Info` reads runtime options, resolves runtime binary, reports containerd version, options, and optional `runc features` output. Persistent state includes sockets, bundle files (`config.json`, `options.json`, `runtime`), cgroup membership, and rootfs mounts.

## Dependencies And Integration
Uses bootstrap APIs, shim helpers, runc wrapper files, cgroups v1/v2, OCI runtime features, namespaces, defaults, schedcore, mounts, and typeurl. It is called by containerd runtime v2 infrastructure.

## Risks And Test Signals
Risks include stale socket cleanup, grouping collisions, leaked sockets on partial start, cgroup join failures, thread lock/unlock around sched-core, and runtime feature command incompatibility. Tests should cover socket reuse, debug sockets, group labels, stop cleanup, options parsing, runtime lookup, and cgroup modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/manager/manager_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/deleted_state.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/deleted_state.go

## Purpose
Defines the terminal deleted process state for the shim process state machine.

## Important APIs, Control Flow, And State
`deletedState` implements state methods by returning errors for operations that are invalid after deletion, such as start, delete, pause, resume, checkpoint, exec, kill, update, and status. It preserves the invariant that once an init process transitions to deleted it cannot be manipulated as a live runtime process. It carries no fields and persists no state.

## Dependencies And Integration
Part of the `initState` interface used by `Init`. It integrates with created/running/stopped state transitions and guards ttrpc task service operations indirectly through process methods.

## Risks And Test Signals
Risks include missing methods if `initState` evolves or unclear error semantics for callers. Tests should cover delete transition behavior and that every lifecycle operation rejects deleted processes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/deleted_state.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/exec.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/exec.go

## Purpose
Implements shim-side exec process handling for additional processes inside an existing runc container.

## Important APIs, Control Flow, And State
`Exec` stores ID, PID, status, timestamps, stdio, IO pipes, console, and wait channel. Creation decodes the process spec, sets up terminal or pipe IO, writes the exec process JSON into the bundle, invokes runc `exec`, wires console or pipe copying, opens stdin when provided, and records PID. Lifecycle methods start/wait/delete/kill/resize/status mirror `Process`. On exit it records status/time, shuts down console, closes wait channel, and later deletion drains IO and removes resources. Persistent state includes the generated exec spec file and runc process state; local state is protected by mutexes.

## Dependencies And Integration
Uses go-runc, typeurl/protobuf specs, stdio/console/fifo IO utilities, process state helpers, and the parent `Init.exec` path. It is exposed through `runc.Container.Exec` and task service `Exec`/`Start`.

## Risks And Test Signals
Risks include IO leaks on partial exec creation, invalid process spec unmarshaling, console handoff timeouts, PID file read failures, and deleting before stopped. Tests should cover terminal and nonterminal execs, start errors, wait behavior, kill behavior, IO cleanup, and duplicate exec IDs through container reservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/exec_state.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/exec_state.go

## Purpose
Defines the state machine for shim exec processes.

## Important APIs, Control Flow, And State
The exec state interface and concrete states model created, running, stopped, and deleted exec lifecycles. Created can start, kill, delete, and transition; running can kill and becomes stopped on exit; stopped permits delete; deleted rejects operations. State methods delegate to underlying `Exec` helpers for runc actions and enforce legal transitions. Persistence is not direct, but state transitions determine when wait channels close, exit status is recorded, and runc delete/IO cleanup can run.

## Dependencies And Integration
Uses context, errors, and state-name utilities. It is embedded in `Exec` and driven by shim service calls and reaper exit events.

## Risks And Test Signals
Risks include invalid transitions panicking or returning inconsistent errors, deletion allowed too early, and exit races with start. Tests should cover every transition, set-exited behavior from each live state, and operation rejection by stopped/deleted states.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/exec_state.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/init.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/init.go

## Purpose
Implements shim-side init process management for a runc container, including create, restore, start, wait, delete, pause/resume, kill, update, checkpoint, exec, and IO cleanup.

## Important APIs, Control Flow, And State
`Init` stores process state, wait channel, bundle/work dirs, console/platform, runc handle, IO handles, rootfs path, option flags, PID, status, and timestamps. `Create` sets up terminal socket or pipe IO, handles checkpoint restore state, calls runc create, opens stdin, wires console/pipe copying, and records PID from `init.pid`. `Start`, `Delete`, `Pause`, `Resume`, `Kill`, `Update`, `Checkpoint`, and `Exec` delegate through `initState` to enforce lifecycle. `setExited` records exit time/status, shuts down console, and releases waiters. `delete` drains IO, deletes runc state, closes pipes, and recursively unmounts rootfs. Persistent state includes runc state under root, bundle files, mounted rootfs, pid files, checkpoint data, and generated exec specs.

## Dependencies And Integration
Uses go-runc, containerd mount and stdio helpers, console/fifo IO, OCI specs, protobuf Any, Unix syscalls, and state implementations. It is owned by `runc.Container` and task service.

## Risks And Test Signals
Risks include create/restore cleanup gaps, IO goroutine leaks, rootfs unmount failures, start/exit ordering races, checkpoint side effects, and PID file errors. Tests should cover create terminal/nonterminal, checkpoint restore, lifecycle transitions, IO drain timeout, unmount error propagation, and concurrent start/exit behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/init_state.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/init_state.go

## Purpose
Defines the init process lifecycle state machine, including normal created/running/stopped states and checkpoint-created restore state.

## Important APIs, Control Flow, And State
`initState` declares lifecycle methods. `createdState` permits start, delete, update, kill, and exec, while rejecting pause/resume/checkpoint. `createdCheckpointState` starts from runc restore options and transitions similarly after restore. Running state supports pause, checkpoint, update, exec, kill, and stop transition; stopped state permits delete and rejects active operations. Each state calls underlying `Init` methods and switches `p.initState` on legal transitions. State persistence is in the `Init` object; runc state changes occur through delegated operations.

## Dependencies And Integration
Uses go-runc restore options, protobuf Any for updates, log/error helpers, and state-name utilities. It coordinates with `Init.Create`, checkpoint/restore paths, and reaper-driven `SetExited`.

## Risks And Test Signals
Risks include illegal transition bugs, restore-specific console/IO setup failures, and operation availability differing from containerd API expectations. Tests should cover transition matrix, created checkpoint start, pause/resume/checkpoint legality, update in created/running, and set-exited behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/init_state.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/io.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/io.go

## Purpose
Implements non-terminal shim IO setup and pluggable logging-binary IO for runc processes.

## Important APIs, Control Flow, And State
`processIO` wraps runc IO plus parsed stdio URI and copy mode. `createIO` chooses null IO, FIFO pipe IO, binary/binary-v2 logger IO, or file-backed stdout/stderr. `Copy` starts pipe copy goroutines through `copyPipes`. `copyPipes` opens FIFOs or files, handles stdout/stderr sharing with `countingWriteCloser`, copies stdout/stderr with pooled buffers, opens stdin nonblocking, and closes runc stdin on EOF. `NewBinaryIO` starts a logger process with extra file descriptors, waits for readiness (strict for `binary-v2`), and returns `binaryIO` which closes pipes and terminates the logger. State includes OS pipes/FIFOs/files, child logger processes, goroutines, and wait groups.

## Dependencies And Integration
Uses go-runc IO, containerd fifo, stdio URI conventions, namespace lookup, logging, OS pipes, exec, and helper utilities in `io_util.go`. It is used by init and exec creation.

## Risks And Test Signals
Risks include FIFO open deadlocks, logger readiness hangs/errors, shared stdout/stderr close ordering, file permission issues, and IO goroutine leaks. Tests should cover null/fifo/file/binary schemes, binary-v2 readiness, stdout-stderr same file behavior, stdin closure, and cleanup on partial errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/io.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/io_test.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/io_test.go

## Purpose
Provides unit coverage for shim IO helper behavior, especially command construction and file closing utilities.

## Important APIs, Control Flow, And State
The tests exercise pieces such as binary logging command construction and close helper behavior using local inputs rather than starting a full shim/container. They validate expected arguments/environment/extra-file conventions and error aggregation/closing semantics. Persistent state is limited to temporary test resources.

## Dependencies And Integration
Uses Go testing facilities and the process IO helper functions. It is a regression signal for the pluggable logger contract consumed by `io.go` and `runc/platform.go`.

## Risks And Test Signals
The file itself signals important risks: URI parsing, logger binary invocation compatibility, and close behavior. Additional tests would be valuable for binary-v2 readiness, FIFO/file copy behavior, same-file stdout/stderr, and partial startup cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/io_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/io_util.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/io_util.go

## Purpose
Contains utility helpers for shim binary IO, command construction, pipe wrappers, file closing, and conditional runc IO creation.

## Important APIs, Control Flow, And State
The file provides helpers used by `io.go` and console logging paths: creating OS pipe structs, closing groups of files, constructing the logging binary command from a `binary://` or `binary-v2://` URI, and selecting conditional stdin/stdout/stderr pipe creation based on stdio config. It centralizes low-level fd and command details so both terminal and nonterminal logging can pass the expected extra file descriptors. State is OS file descriptors and spawned command configuration; no daemon metadata is mutated.

## Dependencies And Integration
Depends on OS/exec/url/filepath-style primitives, go-runc IO options, and stdio configuration. It is tightly integrated with `NewBinaryIO` and `linuxPlatform.CopyConsole`.

## Risks And Test Signals
Risks include URI-to-command compatibility, fd ordering mismatches with logger binaries, failure to close all descriptors on errors, and nil/empty stdio handling. Tests should cover command args/env, close error aggregation, conditional IO options, and malformed URI inputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/io_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/process.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/process.go

## Purpose
Defines the common shim-side `Process` interface implemented by init and exec process types.

## Important APIs, Control Flow, And State
The interface covers identity, PID, exit status/time, stdin closer, stdio metadata, status, wait, resize, start, delete, kill, and `SetExited`. It establishes the contract used by `runc.Container` and task service without embedding runc-specific concrete types. No control flow or persistence exists in this file; it is a type boundary.

## Dependencies And Integration
Depends on `context`, `io`, `time`, `console`, and containerd `stdio`. It is implemented by `Init` and `Exec`, stored in container process maps, and driven by ttrpc task service methods.

## Risks And Test Signals
Risks are interface drift and inconsistent semantics between init and exec implementations. Compile-time assertions or targeted tests should ensure both concrete process types satisfy the interface and agree on wait/delete/status behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/process.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/types.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/types.go

## Purpose
Defines configuration data structures passed into shim process creation, exec, and checkpoint operations.

## Important APIs, Control Flow, And State
`Mount` mirrors mount data needed by runc creation. `CreateConfig` carries container ID, bundle, runtime, rootfs mounts, stdio paths, checkpoint paths, parent checkpoint, terminal flag, and runtime options. `ExecConfig` carries exec ID, terminal/stdio fields, and process spec. `CheckpointConfig` carries CRIU work/path and option flags such as exit, TCP, external Unix sockets, terminal, file locks, and empty namespaces. These are pure data structs; runtime state changes happen in `Init`, `Exec`, and `runc.Container`.

## Dependencies And Integration
Uses protobuf `Any` for runtime options/spec data. The structs bridge task service requests to process implementation code.

## Risks And Test Signals
Risks include field mapping drift from task API requests and incomplete checkpoint option propagation. Tests should validate request-to-config conversion in `runc.Container` and option propagation into runc create/restore/checkpoint calls.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/utils.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/utils.go

## Purpose
Provides small shared utilities for process state naming, PID file handling, runtime error wrapping, wait group timeouts, and related shim process helpers.

## Important APIs, Control Flow, And State
Utilities support creating/reading `init.pid` or exec pid files, converting concrete state type names into stable status/debug names, wrapping go-runc errors with useful context, and waiting for IO goroutines with a timeout. State touched by this file is local filesystem PID files and synchronization primitives; it does not manipulate container metadata directly.

## Dependencies And Integration
Used by `Init`, `Exec`, and state files. It integrates with go-runc error reporting and the IO drain path before runtime deletion.

## Risks And Test Signals
Risks include stale/missing pid files, timeout behavior masking stuck IO, and brittle state-name reflection if type names change. Tests should cover pid file read/write/remove behavior, timeout paths, and state-name outputs for each state type.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/runc/container.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/runc/container.go

## Purpose
Wraps a runc container and its init/exec processes for the shim task service, handling create-time options, rootfs mounts, cgroups, process maps, and operation delegation.

## Important APIs, Control Flow, And State
`NewContainer` decodes runc options, converts rootfs mounts, creates `rootfs`, writes `options.json` and `runtime`, mounts rootfs components, constructs `process.Init`, calls `Create`, stores cgroup info, and returns a `Container`. Helpers read/write `options.json` and `runtime`. `Container` uses a mutex to manage init process, exec process map, and reserved exec IDs. Methods delegate start/delete/exec/pause/resume/resize/kill/closeIO/checkpoint/update to the process layer and remove execs on delete. `loadProcessCgroup` loads cgroup v1 or v2 by PID. Persistent state includes bundle option/runtime files, rootfs mounts, runc state, cgroup references, and process maps in memory.

## Dependencies And Integration
Uses task v3 API, runc options, cgroups v1/v2, mounts, namespaces, stdio platform, process package, errdefs/errgrpc, and typeurl. It is the object stored in `task.service.containers`.

## Risks And Test Signals
Risks include partial create cleanup, rootfs mount leaks, option file compatibility, concurrent exec ID races, cgroup load failures, and type assertions to `*process.Init`. Tests should cover create failure cleanup, rootfs mount/unmount, exec reservation, process lookup, cgroup modes, and checkpoint/update delegation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/runc/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/runc/platform.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/runc/platform.go

## Purpose
Implements Linux platform console handling for shim terminal IO using an epoller and optional pluggable logging binaries.

## Important APIs, Control Flow, And State
`NewPlatform` creates a console epoller and starts its wait loop. `linuxPlatform.CopyConsole` adds a console to epoll, optionally copies stdin from FIFO, parses stdout URI, and either starts a binary/binary-v2 logger with expected extra fds and readiness protocol or copies console output to a FIFO. It returns an epoll console for resize/shutdown. `ShutdownConsole` asserts `EpollConsole` and closes through the epoller; `Close` closes the epoller. State includes epoll fd, FIFOs, OS pipes, logger processes, copy goroutines, and wait groups.

## Dependencies And Integration
Uses console, fifo, stdio platform interface, namespaces, and process logging command helpers. It is used by `process.Init` and `process.Exec` terminal create paths.

## Risks And Test Signals
Risks include epoller lifecycle leaks, logger readiness failures, FIFO open blocking, fd ordering contract breaks, and shutdown type assertion errors. Tests should cover platform initialization, binary-v2 readiness, FIFO console copy, stdin shutdown, epoller close, and error cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/runc/platform.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/runc/util.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/runc/util.go

## Purpose
Provides utility logic for deciding whether the shim should kill all remaining processes when the container init exits.

## Important APIs, Control Flow, And State
`ShouldKillAllOnExit` reads the bundle's OCI `config.json`; on read errors it logs and returns true. If the spec has a Linux private PID namespace (`type=pid` with empty path), it returns false because child processes should be reaped with the namespace. Otherwise it returns true to kill remaining processes, especially for shared PID namespace cases. `readSpec` opens and JSON-decodes `config.json`. State is read-only bundle filesystem access.

## Dependencies And Integration
Uses OCI runtime spec, logging, and JSON/filepath helpers. It is called by `task.service.handleInitExit` before waiting for exec exits and publishing init exit.

## Risks And Test Signals
Risks include conservative kill-all on malformed specs, namespace interpretation errors, and bundle path assumptions. Tests should cover missing/malformed config, private PID namespace, shared PID namespace, non-Linux specs, and logging/error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/runc/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/task/plugin/plugin_linux.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/task/plugin/plugin_linux.go

## Purpose
Registers the runc v2 shim task service plugin for Linux builds.

## Important APIs, Control Flow, And State
`init` registers a plugin with the containerd plugin registry under the shim task service type and runc v2 service ID. The init function constructs the service by calling `task.NewTaskService` with shim publisher and shutdown service dependencies. Persistent state is plugin registry registration; runtime service state is created later per shim.

## Dependencies And Integration
Uses the task package, shim/shutdown services, containerd plugin registry, and plugin ID constants. The blank import in `main.go` relies on this side effect so the shim exposes the ttrpc task API.

## Risks And Test Signals
Risks include registration ID/type drift, missing required dependencies, and Linux-only build coverage. Tests should confirm plugin registration, service construction from an init context, and shim startup exposing task v3.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/task/plugin/plugin_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/task/service.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/task/service.go

## Purpose
Implements the shim's ttrpc task service for runc containers, bridging containerd task API calls to `runc.Container` and process state while publishing lifecycle/OOM events.

## Important APIs, Control Flow, And State
`NewTaskService` initializes OOM watchers, reaper subscription, process maps, platform, event forwarding, and shutdown socket cleanup. `service` stores containers, running PID mappings, exec counters, init exit stashes, exit subscribers, and event publisher. `Create`, `Start`, `Delete`, `Exec`, `State`, `Pause`, `Resume`, `Kill`, `Pids`, `CloseIO`, `Checkpoint`, `Update`, `Wait`, `Connect`, `Shutdown`, and `Stats` implement task API operations. `preStart` and `processExits` handle exit/start races by subscribing to early reaper events. `handleInitExit` kills remaining processes when needed and delays init exit publication until exec exits are published. Persistent/runtime state includes process maps, cgroup/OOM watchers, reaper events, task events, and shim shutdown callbacks.

## Dependencies And Integration
Uses task v3 API, event types, cgroups v1/v2, go-runc reaper, process/runc packages, OOM packages, namespace/event publishers, protobuf/typeurl, errgrpc, ttrpc, and shutdown service. It is the core runtime service used by containerd for runc v2 tasks.

## Risks And Test Signals
Risks include PID reuse races, missed early exits, event ordering regressions, exec counters not decremented on start failure, OOM watcher leaks, cgroup stat type mismatches, and shutdown before events flush. Tests should cover lifecycle API paths, early exit/start races, init-exit ordering with execs, OOM publishing, stats for cgroup modes, delete cleanup, and event forwarding during shutdown.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/task/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/cri_worker.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-stress/cri_worker.go

## Purpose
Implements the CRI-based worker used by `containerd-stress` to repeatedly create and remove pod sandboxes through the Kubernetes CRI API.

## Important APIs, Control Flow, And State
`criWorker` tracks worker ID, counts, failures, CRI runtime client, runtime handler, snapshotter, and commit label. `run` loops until the timeout context is done, creates a sandbox ID, times `runSandbox`, records metrics on success, and increments errors on non-deadline failures. `runSandbox` builds `PodSandboxConfig`, calls `RunPodSandbox`, defers stop/remove, and starts a ticker goroutine that polls sandbox status until timeout. `criCleanup` lists sandboxes with the stress namespace label and stops/removes them. State is remote CRI sandbox state plus local counters.

## Dependencies And Integration
Uses integration `remote.RuntimeService`, CRI runtime v1 API, internal CRI ID utility, logging, and shared metrics from `main.go`.

## Risks And Test Signals
Risks include the ticker status condition appearing inverted, leaked ticker goroutines, cleanup aborting on first failure, and unsynchronized counters if accessed concurrently. Tests should cover run loop cancellation, sandbox config fields/labels, cleanup filtering, error counting, and polling goroutine exit.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/cri_worker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/density.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-stress/density.go

## Purpose
Adds the `density` subcommand, which creates many containers and reports process memory map/stat information for density analysis.

## Important APIs, Control Flow, And State
`densityCommand` validates count, creates a client in the `density` namespace, cleans previous containers, pulls/unpacks the image, then loops creating containers/tasks with sleep specs while collecting PIDs until count or signal interruption. It writes JSON results when requested and includes helpers `getMaps`, `getppid`, `parseStat`, and `Stat` for reading `/proc/<pid>/maps` and `/proc/<pid>/stat` style data. Persistent state is temporary containers/tasks/snapshots in the density namespace and host procfs reads.

## Dependencies And Integration
Uses the client package, `cio`, OCI spec helpers, namespaces, CLI flags inherited from the main app, JSON, procfs file reads, and signal handling.

## Risks And Test Signals
Risks include Linux `/proc` assumptions, cleanup after signal interruption, stat parsing edge cases with process names, and resource exhaustion at high counts. Tests should cover count validation, stat parsing, map aggregation, cleanup behavior, and JSON output shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/density.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/exec_worker.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-stress/exec_worker.go

## Purpose
Implements stress workers that repeatedly create a container and run an exec process inside it.

## Important APIs, Control Flow, And State
`execWorker` embeds `ctrWorker`. `exec` loops until timeout, creates a container/task using the embedded worker path, then calls `runExec` with a generated process spec, tracking counts, failures, and exec timing metrics. `runExec` creates an exec process, starts it, waits for completion, and handles cleanup with task/container deletion paths. State includes remote container/task/exec lifecycle and local counters.

## Dependencies And Integration
Uses containerd client, `cio`, OCI helpers, runtime spec process definitions, syscall signals, logging, and metrics from `main.go`. It complements normal `ctrWorker` stress to exercise exec-specific shim paths.

## Risks And Test Signals
Risks include cleanup gaps if exec creation or start fails, blocking waits after timeout, and shared counter access through the final result. Tests should cover exec success, create/start/wait failures, timeout cancellation, and cleanup ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/exec_worker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/main.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-stress/main.go

## Purpose
Defines the `containerd-stress` CLI, global metrics, configuration, main run modes, cleanup, and result aggregation for containerd load tests.

## Important APIs, Control Flow, And State
`init` registers metrics, raises rlimits, and customizes CLI help/version flags. `main` builds CLI flags for address, concurrency, duration, CRI, exec, image, metrics, runtime, snapshotter, and JSON, then dispatches to metrics server, CRI test, normal test, or density subcommand. `serve` starts an HTTP metrics endpoint and records binary sizes. `criTest` and `test` set namespaces, create clients, cleanup old resources, pull images for non-CRI, start worker goroutines for the duration, gather counts, log and optionally JSON-encode results. `cleanup` deletes existing stress namespace containers/tasks/snapshots. State includes remote containerd/CRI resources, metrics registry, HTTP server, and worker counters.

## Dependencies And Integration
Uses containerd client/defaults/plugins/version, CRI remote service, namespaces, Docker metrics, urfave/cli, OS signals, and worker implementations.

## Risks And Test Signals
Risks include cleanup deleting all containers in the stress namespace, no graceful HTTP server shutdown, unsynchronized counters by design, divide-by-zero if no completions, and long-running resource pressure. Tests should cover CLI config mapping, JSON output, cleanup fallback, signal cancellation, metrics handler startup, and result aggregation with zero totals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/rlimit_freebsd.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-stress/rlimit_freebsd.go

## Purpose
Raises process file descriptor limits for the stress tool on FreeBSD.

## Important APIs, Control Flow, And State
`setRlimit` reads `RLIMIT_NOFILE`, sets current limit to max, and writes it back with `syscall.Setrlimit`. The effect is process-level resource limit mutation before stress workers run.

## Dependencies And Integration
Uses FreeBSD syscall rlimit APIs and is selected by build tags. Called from `main.go` init.

## Risks And Test Signals
Risks include permission failures, platform-specific max semantics, and panics from init if raising limits fails. Platform tests should cover successful no-op/high-limit cases and error propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/rlimit_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/rlimit_unix.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-stress/rlimit_unix.go

## Purpose
Raises process file descriptor limits for non-FreeBSD Unix stress runs.

## Important APIs, Control Flow, And State
`setRlimit` reads `RLIMIT_NOFILE`, sets current and max to a high value appropriate for stress workloads, and calls `syscall.Setrlimit`. This mutates the stress process resource limits so many containers, FIFOs, and sockets can be active.

## Dependencies And Integration
Uses Unix syscall rlimit APIs and is called from `main.go` init through build selection.

## Risks And Test Signals
Risks include insufficient privileges, OS-specific hard limits, and failing the entire tool during init. Tests should validate build constraints and error propagation; integration runs should confirm high-concurrency tests do not hit file descriptor exhaustion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/rlimit_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/rlimit_windows.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-stress/rlimit_windows.go

## Purpose
Provides the Windows implementation of stress-tool rlimit setup.

## Important APIs, Control Flow, And State
`setRlimit` is a no-op returning nil because Windows does not use the Unix `setrlimit` API in this context. It mutates no state.

## Dependencies And Integration
Has no imports and is selected for Windows builds to keep `main.go` portable.

## Risks And Test Signals
Risk is that Windows stress runs may encounter resource limits not handled here. Build tests should verify compilation; platform integration tests should exercise high concurrency on Windows separately.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/rlimit_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/size.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-stress/size.go

## Purpose
Records binary size metrics for selected containerd executables when the stress metrics server is enabled.

## Important APIs, Control Flow, And State
`binaries` lists default binary names under `/usr/local/bin/`. `checkBinarySizes` stats each path and updates `binarySizeGauge` with byte sizes, logging warnings when stat fails. It reads local filesystem metadata and mutates only the metrics registry.

## Dependencies And Integration
Uses `os.Stat`, logging, and the `binarySizeGauge` defined in `main.go`. Called by `serve` before running stress mode with metrics.

## Risks And Test Signals
Risks include hard-coded install path assumptions and missing binaries producing noisy warnings. Tests should cover gauge updates for temp files and warning behavior for absent files; configuration could be added if alternate install paths matter.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/size.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/worker.go -->
# Research: sources/cloud-native/containerd/cmd/containerd-stress/worker.go

## Purpose
Implements the base non-CRI stress worker that repeatedly creates, starts, waits for, and deletes containers.

## Important APIs, Control Flow, And State
`ctrWorker` stores worker identity, counts, failures, client, image, commit, and snapshotter. `run` loops until timeout, calls `runContainer`, records metrics on success, and logs/counts non-deadline failures. `runContainer` creates a container with image spec and snapshot, creates a task with null IO, starts it, waits for exit, and deletes task/container with snapshot cleanup in defers. `getID` produces deterministic IDs from worker and count. State is remote container/task/snapshot lifecycle plus local counters.

## Dependencies And Integration
Uses containerd client APIs, `cio`, OCI spec helpers, logging, and metrics from `main.go`. It is the primary worker for normal stress runs and a base for exec workers.

## Risks And Test Signals
Risks include cleanup failures after partial creation, snapshot accumulation, blocking waits, and unsynchronized counter reads. Tests should cover successful lifecycle, create/task/start failures, deadline handling, cleanup defers, and ID generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd-stress/worker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/btrfs_linux.go -->
# Research: sources/cloud-native/containerd/cmd/containerd/builtins/btrfs_linux.go

## Purpose
Registers the btrfs snapshotter plugin in Linux builds via blank import.

## Important APIs, Control Flow, And State
The file has no functions; importing the btrfs snapshotter plugin triggers its package initializer to register with containerd's plugin registry. Runtime state is plugin registry entries and later plugin instances.

## Dependencies And Integration
Build-tagged for Linux and integrated by importing the `builtins` package from the daemon command.

## Risks And Test Signals
Risks include plugin package path drift and build tag coverage. Tests should verify Linux daemon builds include the btrfs snapshotter when dependencies are available.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/btrfs_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/builtins.go -->
# Research: sources/cloud-native/containerd/cmd/containerd/builtins/builtins.go

## Purpose
Registers the core cross-platform built-in containerd plugins by blank import.

## Important APIs, Control Flow, And State
The import list registers runtime v2, content, events, GC, image verifier, leases, metadata, mount, NRI, restart, sandbox, debug/grpc/metrics/ttrpc servers, service plugins for containers/content/diff/events/health/images/introspection/leases/mounts/namespaces/opt/sandbox/snapshots/streaming/tasks/transfer/version/warning, and transfer/streaming plugins. There are no functions; package initialization performs registration. State is global plugin registry entries.

## Dependencies And Integration
This package is imported by `cmd/containerd` so the daemon knows which plugins are available without dynamic loading.

## Risks And Test Signals
Risks include missing critical plugin imports, unwanted side effects from init functions, and registry ID conflicts. Tests should load the plugin graph and confirm required services are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/builtins.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_freebsd.go -->
# Research: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_freebsd.go

## Purpose
Registers FreeBSD-specific daemon builtins.

## Important APIs, Control Flow, And State
Blank imports register the walking diff plugin and ZFS plugin for FreeBSD builds. No direct functions or local state are defined; registration happens in imported package initializers.

## Dependencies And Integration
Selected by FreeBSD build constraints and included through the daemon's `builtins` package.

## Risks And Test Signals
Risks include missing snapshot/diff support on FreeBSD if imports drift or dependencies fail. Build and plugin graph tests on FreeBSD should verify registrations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_linux.go -->
# Research: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_linux.go

## Purpose
Registers Linux-specific daemon builtins for runc options, cgroup metrics, diff, mounts, and snapshotters.

## Important APIs, Control Flow, And State
Blank imports register runc option type support, cgroups metrics collectors, EROFS/walking diff plugins, EROFS mount support, and blockfile, EROFS, native, and overlay snapshotters. The file has no runtime functions; state is plugin/type registry side effects.

## Dependencies And Integration
Selected for Linux builds and included through `cmd/containerd/builtins`.

## Risks And Test Signals
Risks include missing overlay/native snapshotter registrations, cgroup metrics omissions, or duplicate registration conflicts. Linux build and plugin graph tests should assert expected plugin IDs and typeurl registrations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_unix.go -->
# Research: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_unix.go

## Purpose
Registers Unix non-Linux builtins shared across supported Unix platforms.

## Important APIs, Control Flow, And State
Blank imports register EROFS and walking diff plugins plus blockfile, EROFS, and native snapshotters. There are no functions; imported package init functions update the plugin registry.

## Dependencies And Integration
Applies through Unix build tags where Linux-specific file does not replace the needed set. It keeps daemon plugin availability aligned across Unix variants.

## Risks And Test Signals
Risks include platform build tag overlap/omission and plugin dependency portability. Platform build tests should confirm the intended imports compile and plugin graph contains expected diff/snapshotter plugins.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_windows.go -->
# Research: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_windows.go

## Purpose
Registers Windows-specific daemon diff and snapshotter plugins.

## Important APIs, Control Flow, And State
Blank imports register LCOW and Windows diff plugins plus LCOW and Windows snapshotters. There are no functions or direct local state; plugin registration happens through package init side effects.

## Dependencies And Integration
Selected for Windows builds and included through the daemon builtins package.

## Risks And Test Signals
Risks include missing Windows/LCOW plugin registration or build breakage from platform APIs. Windows build and plugin graph tests should verify expected plugins are registered.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/cri.go -->
# Research: sources/cloud-native/containerd/cmd/containerd/builtins/cri.go

## Purpose
Registers the CRI plugin set in containerd daemon builds.

## Important APIs, Control Flow, And State
Blank imports register the main CRI plugin, CRI image integration, and CRI runtime integration. The file has no direct functions; global plugin registry side effects make CRI available when the daemon starts.

## Dependencies And Integration
Integrated through daemon builtins and the plugin registry. It connects Kubernetes CRI service support to the default containerd binary.

## Risks And Test Signals
Risks include CRI unintentionally absent from builds or registration conflicts. Tests should check plugin graph availability and CRI service startup under default configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/cri.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/devmapper_linux.go -->
# Research: sources/cloud-native/containerd/cmd/containerd/builtins/devmapper_linux.go

## Purpose
Registers the devmapper snapshotter plugin in Linux daemon builds.

## Important APIs, Control Flow, And State
The file is a Linux-only blank import; plugin initializer side effects register devmapper with the plugin registry. No direct state or functions exist here.

## Dependencies And Integration
Integrated through the daemon `builtins` package. It makes devmapper available when compiled with its dependencies.

## Risks And Test Signals
Risks include plugin path drift and dependency/platform build failures. Linux plugin graph tests should confirm devmapper registration where expected.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/devmapper_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/tracing.go -->
# Research: sources/cloud-native/containerd/cmd/containerd/builtins/tracing.go

## Purpose
Registers the containerd tracing plugin in daemon builds.

## Important APIs, Control Flow, And State
The file consists of a blank import of `pkg/tracing/plugin`, causing tracing plugin registration during init. There are no functions and no local state.

## Dependencies And Integration
Integrated through the daemon builtins package and plugin registry. It provides observability configuration support to the main daemon.

## Risks And Test Signals
Risks include accidental removal disabling tracing or plugin init side effects changing startup. Tests should verify tracing plugin registration and daemon startup with tracing configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/tracing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/zfs_linux.go -->
# Research: sources/cloud-native/containerd/cmd/containerd/builtins/zfs_linux.go

## Purpose
Registers the ZFS plugin in Linux daemon builds.

## Important APIs, Control Flow, And State
The Linux-only file blank-imports `github.com/containerd/zfs/v2/plugin`, which registers through package init. No direct functions or local state are present.

## Dependencies And Integration
Included through the daemon builtins package. It exposes ZFS snapshotter functionality where supported.

## Risks And Test Signals
Risks include platform dependency failures and missing plugin registration. Linux build and plugin graph tests should verify ZFS registration under supported build environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/builtins/zfs_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/config.go -->
# Research: sources/cloud-native/containerd/cmd/containerd/command/config.go

## Purpose
Implements `containerd config` subcommands for default config generation, config dumping with imports, and migration-style output.

## Important APIs, Control Flow, And State
`outputConfig` loads plugins for a config, decodes plugin configs into `config.Plugins`, fills default timeout strings, sets the config version to the current max, and TOML-encodes to stdout. `configCommand` defines `default`, `dump`, and `migrate` subcommands. `dumpConfig` starts from defaults, builds a plugin registration sequence from the registry graph, loads the configured file and imports when present, and outputs the resulting config. `platformAgnosticDefaultConfig` sets root/state/plugin defaults, default include pattern, stream processors, and grpc server address/message limits. `streamProcessors` defines ocicrypt decoder entries for encrypted gzip and tar layers. State read includes config files and plugin registrations; output is stdout only.

## Dependencies And Integration
Uses server/plugin loading, server config types, defaults, timeout registry, version, plugin registry graph, TOML encoder, OCI/image media types, and urfave/cli. It is part of the main containerd command tree.

## Risks And Test Signals
Risks include generated defaults drifting from server expectations, plugin config decode failures, imports not represented in migration, and stream processor path/env assumptions. Tests should cover default output TOML, dump with missing config, plugin config inclusion, timeout defaults, version setting, and ocicrypt stream processor entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/config.go -->
