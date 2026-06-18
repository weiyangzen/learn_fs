# subset-b-000179 research

Grouped research report for the requested Moby daemon internals. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/local_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/local/local_windows.go

Purpose: implements the legacy in-process Windows libcontainerd client using HCS/hcsshim rather than the remote containerd task service. It provides Docker's daemon-facing `types.Client`, `Container`, `Task`, and `Process` behavior for Windows container creation, task/exec lifecycle, stats, pause/resume, restore cleanup, and event delivery.

Important APIs and types: `client`, `container`, `task`, and `process` back the libcontainerd interfaces. `NewClient`, `NewContainer`, `createWindows`, `extractResourcesFromSpec`, `NewTask`, `Exec`, `Kill`, `Pause`, `Resume`, `Stats`, `Summary`, `LoadContainer`, `Delete`, `ForceDelete`, `Status`, `shutdownContainer`, `terminateContainer`, and `reap` are the key functions. Helpers such as `setCommandLineAndArgs`, `escapeArgs`, `newIOFromProcess`, `getHCSContainer`, and `assertIsCurrentTask` encapsulate HCS-specific details.

Control flow: container creation validates Windows OCI spec shape, maps resources, networking, layers, mounts, credentials, devices, process-vs-Hyper-V isolation, and root paths into `hcsshim.ContainerConfig`, creates and starts the HCS container, then queues a create event. `NewTask` constructs the initial HCS process from `spec.Process`, attaches stdio, stores the current task, queues a start event, and starts a `reap` goroutine. `Exec` mirrors process creation for secondary processes and emits exec-added/exec-started events. Stop handling maps `SIGKILL` to HCS terminate and other signals to shutdown. Reaping waits for process exit, reads exit code, closes HCS resources, records a `containerd.ExitStatus`, closes `waitCh`, and queues an exit event.

State and persistence: state is in-memory and protected by `process.mu` and `container.mu`; HCS owns the persistent compute system/process state. `ociSpec == nil` marks a loaded/restored container that cannot be started. `task` tracks the current task, `hcsContainer` becomes nil after deletion, `hcsProcess` becomes nil after exit, and `waitCh` synchronizes exit status visibility. `queue.Queue` serializes backend callbacks per container ID.

Dependencies and integration: depends on `hcsshim`, containerd client types, Docker errdefs, Windows syscall support, OCI specs, `cio.DirectIO`, and the daemon backend callback. It is the Windows-local counterpart to `remote/client.go` and feeds daemon container state through `libcontainerd/types`.

Risks: the file has complex lock ordering (`process.mu` before container mutex), so changes can deadlock if that invariant is violated. Windows HCS error normalization is partial, especially around pending/already-stopped/broken-pipe cases. Restore behavior force-terminates HCS state rather than reattaching. Many unsupported paths return generic errors or no-ops, including checkpoints and resource updates. Hyper-V and process isolation validate different spec fields, making OCI spec changes risky.

Test signals: direct coverage in this subset is limited to environment parsing in `utils_windows_test.go`; most behavior requires Windows/HCS integration coverage outside this subset. Event ordering and reaping are indirectly protected by the per-container queue design but not unit-tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/local_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/process_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/local/process_windows.go

Purpose: provides small Windows HCS process I/O helpers used by the local libcontainerd implementation.

Important APIs and types: `autoClosingReader` wraps an `io.ReadCloser` and closes it once a read returns an error. `createStdInCloser` wraps an HCS process stdin pipe so closing Docker's writer also closes HCS stdin.

Control flow: `autoClosingReader.Read` delegates to the wrapped reader and uses `sync.Once` to close it on any read error. `createStdInCloser` closes the pipe first, then calls `process.CloseStdin`; it suppresses expected HCS not-exist/already-closed and selected invalid-state errors.

State and persistence: no persistent state; `sync.Once` prevents duplicate close calls. It mutates HCS process state through `CloseStdin`.

Dependencies and integration: depends on `hcsshim` error classification and Docker `ioutils.NewWriteCloserWrapper`. `local_windows.go` uses these helpers when converting HCS process stdio into `cio.DirectIO`.

Risks: any HCS error classification drift can expose benign shutdown races as user-visible errors. Closing on every read error assumes EOF/error means no future data should be read.

Test signals: no direct test in this subset; behavior is exercised only through Windows process I/O integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/process_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/utils_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/local/utils_windows.go

Purpose: converts OCI-style environment string slices into the map form required by HCS.

Important APIs and types: `setupEnvironmentVariables(a []string) map[string]string`.

Control flow: iterates each string, splits once on the first `=`, and records key/value pairs only when a separator exists. Values may contain further `=` characters.

State and persistence: creates a fresh map and has no persistent state. Duplicate keys are overwritten by the last value seen.

Dependencies and integration: used by `local_windows.go` for both initial task and exec process `hcsshim.ProcessConfig.Environment`.

Risks: entries without `=` are silently dropped. Empty keys are accepted if present in input. Duplicate key behavior is implicit map overwrite.

Test signals: `utils_windows_test.go` verifies normal entries and values containing `=`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/utils_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/utils_windows_test.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/local/utils_windows_test.go

Purpose: validates Windows environment parsing for the local HCS executor.

Important APIs and types: `TestEnvironmentParsing` exercises `setupEnvironmentVariables`.

Control flow: builds `[]string{"foo=bar", "car=hat", "a=b=c"}`, parses it, and asserts the expected three-entry map.

State and persistence: no persistent state; test operates on an in-memory slice and map.

Dependencies and integration: package-local test for `utils_windows.go`; it supports the process environment path used by `local_windows.go`.

Risks: coverage is narrow. It does not cover malformed entries, duplicate keys, empty keys, or missing separators.

Test signals: confirms `strings.Cut` first-separator behavior and map population for ordinary Docker environment entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/utils_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/queue/queue.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/queue/queue.go

Purpose: serializes asynchronous callbacks by string ID, mainly container ID, while allowing different IDs to proceed concurrently.

Important APIs and types: `Queue` embeds `sync.Mutex` and holds `fns map[string]chan struct{}`. `Append(id string, f func())` is the only exported operation.

Control flow: `Append` creates a `done` channel, swaps it into the map for `id`, and launches a goroutine. If a previous channel existed, the goroutine waits for it before running `f`. After `f` returns, it closes `done` and removes the map entry if it is still the latest channel for that ID.

State and persistence: queue state is in-memory only. Channels encode dependency order. The map is lazily initialized and pruned when work drains.

Dependencies and integration: used by local and remote libcontainerd clients to deliver backend events in order per container.

Risks: `f` is not recovered; a panic would prevent close/delete and block later callbacks for the same ID. Long-running callbacks back up only their ID. There is no cancellation or bounded queue length.

Test signals: `queue_test.go` verifies same-ID callbacks observe serialized ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/queue/queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/queue/queue_test.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/queue/queue_test.go

Purpose: verifies per-ID serialization behavior for `Queue.Append`.

Important APIs and types: `TestSerialization` appends three callbacks with the same ID.

Control flow: the first callback sleeps to create overlap pressure, each callback checks and advances a shared integer, and the test sleeps long enough for expected completion.

State and persistence: in-memory shared integer and goroutines only.

Dependencies and integration: uses `gotest.tools/assert` and `time.Sleep`; it targets event ordering relied on by libcontainerd event delivery.

Risks: timing-based sleep makes the test less deterministic than using explicit synchronization. It does not test parallelism across different IDs or panic behavior.

Test signals: provides a basic regression signal that callbacks for the same container ID do not run concurrently or out of order.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/queue/queue_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client.go

Purpose: implements the remote containerd-backed libcontainerd client used by the daemon. It wraps containerd client/container/task/process APIs, adapts Docker event semantics, manages bundle paths and stdio I/O, and handles checkpoint content transfer.

Important APIs and types: `client`, `container`, `task`, and `process` wrap containerd objects. Key functions include `NewClient`, `Version`, `NewContainer`, `LoadContainer`, `AttachTask`, `NewTask`, `Start`, `Exec`, `Kill`, `Pause`, `Resume`, `Stats`, `Summary`, `Delete`, `ForceDelete`, `Status`, `CreateCheckpoint`, `Task`, `createIO`, `closeStdin`, `processEventStream`, `writeContent`, and `bundleDir`. The `DockerContainerBundlePath` label links container metadata to the bundle directory.

Control flow: `NewClient` stores the underlying containerd client and starts an event subscription goroutine. `NewContainer` composes containerd options for spec, runtime, and bundle label creation. `NewTask` optionally uploads a checkpoint tar to the content store, reads container metadata/spec without refreshed metadata, builds platform FIFO/named-pipe config, creates I/O, and creates the task with checkpoint and platform options. `Exec` builds I/O for a secondary process, registers and starts it, and deletes the exec process if start fails. `Stats` and `Summary` convert typeurl metrics/process info into daemon types. `CreateCheckpoint` asks containerd for a checkpoint image, reads the checkpoint descriptor from content, applies it to a directory, and deletes the temporary image. Event stream handling subscribes to task topics in the namespace and converts create/start/exit/OOM/exec/pause/resume events into backend callbacks through `queue.Queue`.

State and persistence: state includes containerd metadata, bundle directories under `stateDir`, temporary checkpoint content/images, and in-memory event queue state. Delete removes the bundle directory unless `LIBCONTAINERD_NOCLEAN=1`. Stdin close synchronization uses a channel because the process object may not exist when the I/O writer is closed.

Dependencies and integration: depends on containerd client/content/images/archive/cio APIs, OCI specs, runc options, typeurl/protobuf, OpenTelemetry spans, Docker errdefs, and the backend event interface. Platform files provide `WithBundle`, FIFO construction, direct I/O, summary conversion, log-level options, and resource updates.

Risks: it assumes container labels and spec do not change between container creation and task/exec operations by using `WithoutRefreshedMetadata`. Event stream restart logic depends on `IsServing` and can duplicate subscriptions only by starting a new goroutine after failure. Temporary checkpoint cleanup is best-effort. `createIO` has subtle stdin-close races and intentionally ignores "transport is closing" errors. Bundle cleanup relies on the label value.

Test signals: no direct tests in this subset. Integration is exercised through daemon/containerd tests elsewhere; platform-specific unit coverage is absent here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_io_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_io_windows.go

Purpose: implements Windows named-pipe stdio setup for the remote containerd client.

Important APIs and types: `delayedConnection` implements `Read`, `Write`, and `Close` over an eventually accepted pipe connection. `stdioPipes` groups stdin/stdout/stderr. `newStdioPipes` creates and accepts the named pipes from a `cio.FIFOSet`.

Control flow: for each configured pipe path, the client calls `winio.ListenPipe`, creates a `delayedConnection`, and starts a goroutine to accept the shim connection. Reads/writes block on a `WaitGroup` until accept succeeds or close unblocks waiters. On setup failure, deferred cleanup closes already-created listeners/connections.

State and persistence: state is in-memory listener/connection state plus Windows named pipe endpoints. `sync.Once` ensures waiters are unblocked once.

Dependencies and integration: used by `client_windows.go` `newDirectIO`, which adapts named pipes into `cio.NewDirectIOFromFIFOSet`.

Risks: failed accept closes the delayed connection and future I/O gets `net.ErrClosed`. Callers must close pipes to unblock waiters. There is no explicit accept timeout, so leaked listeners could block I/O users.

Test signals: no direct tests in this subset; behavior is platform integration with runhcs/containerd shims.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_io_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_linux.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_linux.go

Purpose: supplies Linux-specific behavior for the remote libcontainerd client: bundle ownership under user namespaces, FIFO paths, resource updates, and user ID mapping for runc I/O ownership.

Important APIs and types: `summaryFromInterface`, `UpdateResources`, `hostIDFromMap`, `getSpecUser`, `WithBundle`, `withLogLevel`, `newFIFOSet`, and `newDirectIO`.

Control flow: `getSpecUser` detects user namespace mappings and maps container root UID/GID to host IDs. `WithBundle` sets the Docker bundle path label and creates bundle directories, using suffixes like `.uid.gid` when intermediate paths are not accessible to mapped root. `newFIFOSet` builds stdin/stdout/stderr FIFO paths under the bundle and supplies a closer that removes them. `UpdateResources` calls containerd `Task.Update`.

State and persistence: creates bundle directories and FIFO files under the state directory. The bundle path actually used may differ from the requested path when user namespace ownership requires a suffixed directory.

Dependencies and integration: depends on containerd containers/cio, runc specs, Docker user helpers, and `log`. It is compiled into the remote client on Linux.

Risks: directory accessibility checks are path-component based and sensitive to existing permissions. `summaryFromInterface` is a no-op because Linux process summary is not used, so callers expecting docker-top details must use other paths. `withLogLevel` panics if called on Linux, relying on `remote/client.go` to call it only on Windows.

Test signals: no direct tests here; user namespace bundle behavior depends on integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_windows.go

Purpose: supplies Windows-specific behavior for the remote containerd/runhcs client: bundle directories, named pipe names, runhcs debug options, stats summary conversion, and unsupported resource update stubs.

Important APIs and types: `summaryFromInterface`, `WithBundle`, `withLogLevel`, `pipeName`, `newFIFOSet`, `newDirectIO`, `UpdateResources`, and `getSpecUser`.

Control flow: `WithBundle` creates a bundle directory and writes its path to the Docker bundle label. `newFIFOSet` derives deterministic pipe names from container ID, process ID, and stream name. `newDirectIO` creates named-pipe listeners via `newStdioPipes` and wraps them in `cio.DirectIO`. `summaryFromInterface` maps runhcs `options.ProcessDetails` into daemon `Summary` fields.

State and persistence: creates bundle directories; stdio state exists as Windows named pipes. Resource updates and user mapping intentionally do not mutate state.

Dependencies and integration: depends on hcsshim runhcs options, containerd containers/cio, Docker libcontainerd types, and `log`. It complements `client_io_windows.go`.

Risks: `UpdateResources` and `getSpecUser` silently no-op, so callers must not assume Windows resource updates are applied. Unknown summary payload types produce errors. Named pipe names include IDs and must stay within Windows pipe naming constraints.

Test signals: no direct tests in this subset; docker top/process summary and runhcs I/O require Windows integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/replace.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/replace.go

Purpose: creates a container while cleaning up stale containerd state if the requested ID already exists.

Important APIs and types: `ReplaceContainer(ctx, client, id, spec, shim, runtimeOptions, opts...)`.

Control flow: first tries `client.NewContainer`. On non-conflict success/failure it returns immediately. On conflict, it loads the stale container, loads its task if present, force-deletes the task, deletes the container, then retries creation. Not-found during cleanup is treated as a race that can proceed.

State and persistence: mutates containerd state by deleting stale task/container objects and creating a replacement. It does not persist state itself.

Dependencies and integration: used by the plugin containerd executor and likely other daemon container creation paths. It depends on the abstract `libcontainerd/types.Client` and `errdefs` classification.

Risks: if task loading fails with an unknown error, the function refuses to delete the container because deletion would likely hit the same task error. Force-deleting a stale task is destructive by design. Errors are wrapped, so callers need errdefs-aware unwrapping.

Test signals: no direct tests in this subset; correctness depends on integration with containerd error mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/replace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/shimopts/convert.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/shimopts/convert.go

Purpose: converts generic daemon runtime option maps into containerd shim option protobuf structs that can be typeurl-marshaled by the containerd client.

Important APIs and types: `Generate(runtimeType string, opts map[string]any) (any, error)`.

Control flow: selects an output struct based on runtime type: runc v2 options, runhcs v1 options, or generic runtimeoptions. It TOML-marshals the map and TOML-unmarshals into the selected struct to handle loose numeric/map conversion.

State and persistence: no persistent state; pure conversion.

Dependencies and integration: depends on hcsshim runhcs options, containerd runc/runtimeoptions, containerd plugin runtime constants, and `go-toml/v2`. Its output is passed to `containerd.WithRuntime`.

Risks: TOML round-tripping can reject field names/types differently than JSON/YAML config paths. Unknown runtime types get generic options, which may silently ignore runtime-specific fields.

Test signals: no direct tests in this subset; runtime option coverage is integration-driven.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/shimopts/convert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon.go

Purpose: starts, configures, monitors, restarts, and stops a child `containerd` daemon for Docker.

Important APIs and types: `remote` embeds containerd `config.Config` and tracks config file, daemon binary path, pid, pid file, logger, and lifecycle channels. `Daemon`, `DaemonOpt`, `Start`, `WaitTimeout`, `Address`, `getContainerdConfig`, `startContainerd`, and `monitorDaemon` are central.

Control flow: `Start` builds a default config with root/state/grpc/debug paths, applies options, creates state dir, launches `monitorDaemon`, and waits up to `startupTimeout`. `startContainerd` reuses an existing pid from the pid file if present; otherwise writes config TOML, starts `containerd --config`, redirects logs to Docker stdout/stderr, strips `NOTIFY_SOCKET`, locks the OS thread around `cmd.Start`/`Wait` on Linux-sensitive paths, writes the pid file, and records the process pid. `monitorDaemon` loops until context cancellation, starts/restarts containerd, creates a monitoring client, checks `IsServing`, reports initial startup, waits for daemon exit, retries transient failures, kills unresponsive daemons, and performs cleanup on exit.

State and persistence: writes `containerd.toml` and `containerd.pid` under state dir, owns child process state, and removes pid/socket resources during cleanup. Lifecycle channels coordinate startup and shutdown with callers.

Dependencies and integration: depends on containerd config/defaults/client/dialer, gRPC interceptors, Docker pidfile/process helpers, platform-specific address/stop/cleanup utilities, and TOML encoding. It is the daemon's local supervisor for the remote containerd runtime.

Risks: pid-file reuse assumes the recorded process is still the intended containerd. Startup and health-check timeouts are fixed constants. Restart loops must avoid tight spinning; the file uses delays but process liveness races remain. On startup failure after initial success, errors are logged and restart continues rather than surfacing to the original caller.

Test signals: no direct tests in this subset; behavior is system/integration tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_linux.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_linux.go

Purpose: provides Linux-specific containerd supervisor constants, socket path derivation, stop/kill behavior, and cleanup.

Important APIs and types: constants `binaryName`, `sockFile`, `debugSockFile`; functions `defaultGRPCAddress`, `defaultDebugAddress`, `stopDaemon`, `killDaemon`, and `platformCleanup`.

Control flow: addresses are Unix socket paths under state dir. `stopDaemon` sends SIGTERM, waits up to `shutdownTimeout`, and SIGKILLs if still alive. `killDaemon` sends SIGUSR1 for a stack trace, waits briefly, then kills. `platformCleanup` removes the gRPC socket path.

State and persistence: mutates process state and removes socket files.

Dependencies and integration: used by `remote_daemon.go`; depends on `syscall` and Docker `process.Alive/Kill`.

Risks: signal delivery can affect an unrelated process if pid reuse occurs after stale pid-file reuse. Socket cleanup ignores errors.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_options.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_options.go

Purpose: exposes option functions for configuring the supervised containerd daemon.

Important APIs and types: `WithLogLevel`, `WithLogFormat`, `WithCRIDisabled`, and `WithDetectLocalBinary`.

Control flow: options mutate the `remote` config before startup. Info log level is normalized to an empty containerd debug level. CRI is disabled by appending its plugin ID. Local binary detection looks beside the running dockerd executable and overrides `daemonPath` when a non-directory containerd binary is found.

State and persistence: affects generated containerd config and executable path; no standalone persistence.

Dependencies and integration: consumed by `Start`; depends on containerd log format and `os.Executable`.

Risks: local binary detection is path-sensitive and returns an error if a directory exists with the expected binary name. Option ordering can matter if multiple options change the same fields.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_windows.go

Purpose: provides Windows-specific containerd supervisor addresses and process stop behavior.

Important APIs and types: constants `binaryName`, `grpcPipeName`, `debugPipeName`; functions `defaultGRPCAddress`, `defaultDebugAddress`, `stopDaemon`, `killDaemon`, and `platformCleanup`.

Control flow: gRPC/debug addresses are fixed named pipes. `stopDaemon` finds the process, kills it, and waits. `killDaemon` delegates to Docker process kill. Cleanup is a no-op because named pipes do not need socket-file removal.

State and persistence: mutates the child process state; does not remove filesystem resources.

Dependencies and integration: used by `remote_daemon.go` on Windows.

Risks: stop is forceful rather than graceful. Fixed pipe names can conflict if multiple daemon instances run on the same host.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/utils_linux.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/utils_linux.go

Purpose: defines Linux process attributes for starting supervised containerd.

Important APIs and types: `containerdSysProcAttr() *syscall.SysProcAttr`.

Control flow: returns attributes with `Setsid: true` and `Pdeathsig: SIGKILL`.

State and persistence: no persistent state; affects child process/session behavior.

Dependencies and integration: called by `remote_daemon.go` before `exec.Command.Start`.

Risks: `Pdeathsig` is sensitive to Go runtime thread behavior; `remote_daemon.go` locks the OS thread to avoid premature child death.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/utils_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/utils_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/utils_windows.go

Purpose: supplies Windows process attributes for supervised containerd startup.

Important APIs and types: `containerdSysProcAttr() *syscall.SysProcAttr`.

Control flow: returns nil; no special process attributes are used on Windows.

State and persistence: none.

Dependencies and integration: called by `remote_daemon.go`.

Risks: absence of process-group/death-signal semantics means cleanup relies on explicit supervisor stop/kill paths.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/utils_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/types/types.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/types/types.go

Purpose: defines the daemon's abstraction boundary over local/remote containerd implementations.

Important APIs and types: `EventType` constants, `EventInfo`, `Backend`, `Process`, `Client`, `Container`, `Task`, and `StdioCallback`.

Control flow: no executable control flow beyond interface contracts. Implementations report lifecycle events to `Backend.ProcessEvent`, expose container/task/process lifecycle methods, attach stdio through `StdioCallback`, and return platform-specific `Stats`, `Summary`, and `Resources` types from companion files.

State and persistence: none in this file; it specifies how implementations expose state.

Dependencies and integration: imported by local/remote libcontainerd clients, plugin executor, and daemon code that should not depend directly on containerd implementation details.

Risks: interface changes have wide blast radius across Linux, Windows, plugin executor, and tests. Event names are string contracts consumed by daemon event handling.

Test signals: covered indirectly by compile-time implementation satisfaction and integration paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/types/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/types/types_linux.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/types/types_linux.go

Purpose: defines Linux-specific libcontainerd data types.

Important APIs and types: `Summary struct{}`, `Stats`, `InterfaceToStats`, `Resources = specs.LinuxResources`, and `Checkpoints struct{}`.

Control flow: `InterfaceToStats` wraps containerd metrics payload and read timestamp in a `Stats` value.

State and persistence: none; structs carry task metrics/resources data.

Dependencies and integration: used by `remote/client_linux.go` and daemon stats/resource-update code. Linux `Summary` is empty because process details are handled elsewhere.

Risks: `Metrics any` requires downstream type assertions for cgroup v1/v2 metrics. Alias to OCI `LinuxResources` couples Docker resource update API to runtime-spec shape.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/types/types_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/types/types_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/types/types_windows.go

Purpose: defines Windows-specific libcontainerd stats, process summaries, resources, and checkpoint metadata.

Important APIs and types: `Summary` aliases runhcs `options.ProcessDetails`; `Stats` holds read time plus HCS statistics; `InterfaceToStats`; empty `Resources`; `Checkpoint`; and `Checkpoints`.

Control flow: `InterfaceToStats` type-asserts the payload to `*hcsshim.Statistics` and wraps it.

State and persistence: none; structs transport HCS data.

Dependencies and integration: used by Windows local and remote clients for stats/top-like summaries and by daemon code that accepts the platform-specific types.

Risks: `InterfaceToStats` will panic for unexpected payload types. Windows resource updates are modeled as an empty struct, so code must handle unsupported behavior elsewhere.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/types/types_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/metrics/metrics.go -->
# sources/cloud-native/moby/daemon/internal/metrics/metrics.go

Purpose: declares Docker daemon Prometheus/go-metrics instruments and a custom collector for container state counts.

Important APIs and types: package variables such as `ContainerActions`, `NetworkActions`, `HostInfoFunctions`, `ImageActions`, `EngineInfo`, `EngineCPUs`, `EngineMemory`, health check counters/timers, `StateCtr`, event metrics, `StartTimer`, and `StateCounter`.

Control flow: `init` preinitializes selected container action labels to zero and registers the namespace. `StateCounter` stores container ID to state label mappings; `Collect` emits running/paused/stopped gauges.

State and persistence: metrics are process-global. `StateCounter` protects its map with an RW mutex and has no disk persistence.

Dependencies and integration: depends on `docker/go-metrics` and Prometheus. Used throughout daemon operations to expose engine metrics.

Risks: state labels are stringly typed and only three labels are counted. Global registration in `init` can complicate tests or multiple daemon instances in one process.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/metrics/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/metrics/plugin_unix.go -->
# sources/cloud-native/moby/daemon/internal/metrics/plugin_unix.go

Purpose: enables metrics collector plugins on Unix by exposing the daemon metrics endpoint on a Unix socket and notifying plugin lifecycle hooks.

Important APIs and types: `Plugin`, `metricsPluginAdapter`, `makePluginAdapter`, `RegisterPlugin`, `CleanupPlugin`, package variable `listener`, and helper `listen`.

Control flow: `RegisterPlugin` creates the Unix listener, registers a runtime option that bind-mounts the metrics socket into plugins, and registers a handler that looks up a metrics plugin and calls `StartMetrics`. `CleanupPlugin` concurrently calls `StopMetrics` for all managed metrics plugins and closes the listener. `listen` serves `/metrics` with `gometrics.Handler`.

State and persistence: creates/removes a Unix socket path and stores a package-level listener. Plugin state lives outside this package.

Dependencies and integration: integrates daemon plugin store, Docker plugin client calls, OCI spec mount mutation, HTTP server, and go-metrics.

Risks: package-level listener means only one active socket is expected. Cleanup logs plugin stop failures but continues. The metrics socket is bind-mounted read-only, but plugins can scrape sensitive daemon metrics.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/metrics/plugin_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/metrics/plugin_unsupported.go -->
# sources/cloud-native/moby/daemon/internal/metrics/plugin_unsupported.go

Purpose: provides Windows stubs for metrics plugin registration and cleanup.

Important APIs and types: `RegisterPlugin` and `CleanupPlugin`.

Control flow: both functions no-op; registration returns nil.

State and persistence: none.

Dependencies and integration: preserves cross-platform build compatibility for callers that register metrics plugins unconditionally.

Risks: callers may interpret nil as enabled metrics plugin support, while Windows behavior is silently disabled.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/metrics/plugin_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mod/mod.go -->
# sources/cloud-native/moby/daemon/internal/mod/mod.go

Purpose: extracts display-friendly module versions from `debug.BuildInfo` without importing `golang.org/x/mod`.

Important APIs and types: `Version`, `moduleVersion`, `getVersion`, `normalize`, `splitMetadata`, `splitPseudo`, `isTimestamp`, and `parseSemVer`.

Control flow: `Version` reads build info once. `moduleVersion` checks the main module then dependencies. `getVersion` rejects nonmatching modules, replaced modules with a replacement version, empty versions, and `(devel)`. `normalize` strips `+incompatible`, preserves other metadata, tracks `+dirty`, and converts Go pseudo-versions into `<base>+<shortrev>`, including patch decrement for release pseudo-versions.

State and persistence: `readBuildInfo` caches runtime build info via `sync.OnceValues`; otherwise stateless.

Dependencies and integration: intended for display values such as default User-Agent versions. Uses only `runtime/debug`, string parsing, and `strconv`.

Risks: pseudo-version parsing is a local reimplementation of x/mod semantics and can drift. Replaced modules intentionally return empty, which may surprise callers. `parseSemVer` handles only strict `vX.Y.Z` cores.

Test signals: `mod_test.go` covers devel mode, tagged versions, pseudo versions, dirty metadata, dependencies, and replaced dependency behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mod/mod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mod/mod_test.go -->
# sources/cloud-native/moby/daemon/internal/mod/mod_test.go

Purpose: validates module version extraction and normalization from synthetic Go build-info text.

Important APIs and types: `TestModuleVersion` table-drives calls to `moduleVersion`.

Control flow: each case parses build info text with `debug.ParseBuildInfo`, runs `moduleVersion`, and compares the returned display version.

State and persistence: no persistent state; test avoids the process-global `Version` cache by calling `moduleVersion` directly.

Dependencies and integration: covers `mod.go` behavior for Docker and BuildKit module paths.

Risks: tests focus on selected pseudo-version forms; malformed semver and additional metadata combinations are less covered.

Test signals: strong signal for intended display normalization and the deliberate empty return for replaced modules.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mod/mod_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mountref/counter.go -->
# sources/cloud-native/moby/daemon/internal/mountref/counter.go

Purpose: maintains reference counts for graphdriver mount paths while accounting for paths that may already be mounted before the counter sees them.

Important APIs and types: `Counter`, `Checker`, `NewCounter`, `Increment`, `Decrement`, and internal `minfo`.

Control flow: `Increment`/`Decrement` call `incdec`, which initializes per-path state, checks `isMounted` only on first access, seeds the count if already mounted, applies the increment/decrement operation, deletes state at zero or below, and returns the current count.

State and persistence: in-memory map keyed by path; protected by mutex. Existing kernel mount state is sampled once per map entry.

Dependencies and integration: used by graphdriver Get/Put-style mount management and supplied with a mount checker.

Risks: if actual mount state changes outside the counter after first access, the counter does not recheck until state is deleted and recreated. Decrement can delete entries at zero or negative, masking extra decrements.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mountref/counter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mounttree/switchroot_linux.go -->
# sources/cloud-native/moby/daemon/internal/mounttree/switchroot_linux.go

Purpose: switches the current process into a new root mount tree using `pivot_root` when possible, falling back to `chroot`.

Important APIs and types: `SwitchRoot(path string) error` and `realChroot`.

Control flow: if `path` is not already mounted, it tries an rbind mount onto itself and falls back to `chroot` if that fails. It creates a temporary pivot directory under the new root, calls `unix.PivotRoot`, changes directory to `/`, makes the old-root mount private, detach-unmounts it, and removes the temporary directory. On pivot failure it removes the temp dir and falls back to chroot.

State and persistence: mutates the calling process root, cwd, and mount namespace. Temporary pivot directory is removed during cleanup.

Dependencies and integration: depends on `moby/sys/mount`, `mountinfo`, and Linux `unix` syscalls. Used for extraction or daemon operations that need a temporary root tree.

Risks: this is process/mount-namespace destructive and must be called in the correct isolated context. Deferred cleanup writes to the named return `err` pattern imperfectly because `SwitchRoot` does not use a named return; cleanup errors may not propagate in all paths. Propagation mode must be prepared by caller.

Test signals: no direct tests in this subset; requires privileged namespace integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mounttree/switchroot_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/multierror/multierror.go -->
# sources/cloud-native/moby/daemon/internal/multierror/multierror.go

Purpose: joins multiple errors like `errors.Join` but formats multi-error messages as bullet lists with indentation.

Important APIs and types: `Join`, `joinError`, `Error`, and `Unwrap`.

Control flow: `Join` filters nil errors, returns nil if none, and returns a `joinError`. `Error` returns the trimmed single error when only one error exists; for multiple errors it prefixes each error with `* ` and indents embedded newlines. `Unwrap` exposes the slice for `errors.Is/As`.

State and persistence: immutable in-memory slice of errors.

Dependencies and integration: used where user-facing configuration or validation errors need better formatting while preserving multi-error unwrapping.

Risks: formatting is intentionally different from Go stdlib joins, so callers comparing exact strings must account for bullets. Single-error trimming can remove meaningful surrounding whitespace.

Test signals: `multierror_test.go` covers single nested and multiple nested formatting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/multierror/multierror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/multierror/multierror_test.go -->
# sources/cloud-native/moby/daemon/internal/multierror/multierror_test.go

Purpose: verifies custom multi-error formatting.

Important APIs and types: `TestErrorJoin` covers `Join`.

Control flow: subtest `single` wraps one joined error and expects no bullet formatting. Subtest `multiple` joins a plain error with a nested multi-error and expects bullet/indent formatting.

State and persistence: none.

Dependencies and integration: uses `gotest.tools/assert`.

Risks: exact string tests are sensitive to formatting changes, but that is the contract of this package.

Test signals: confirms newline indentation and single-error trimming behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/multierror/multierror_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/netipstringer/stringer.go -->
# sources/cloud-native/moby/daemon/internal/netipstringer/stringer.go

Purpose: provides safe string conversions for `netip` values that return an empty string for invalid addresses/prefixes.

Important APIs and types: `Addr(netip.Addr) string` and `Prefix(netip.Prefix) string`.

Control flow: each function checks `IsValid` and returns `""` for invalid input; otherwise delegates to `String`.

State and persistence: none.

Dependencies and integration: useful for API/config output paths where invalid zero values should serialize as empty fields.

Risks: empty string can conflate invalid values with intentional empty values in callers.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/netipstringer/stringer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/netiputil/netiputil.go -->
# sources/cloud-native/moby/daemon/internal/netiputil/netiputil.go

Purpose: provides conversion, arithmetic, comparison, and optional parsing helpers around Go `net/netip` values for daemon networking code.

Important APIs and types: `ToIPNet`, `ToPrefix`, `HostID`, `SubnetRange`, `AddrPortFromNet`, `LastAddr`, `PrefixCompare`, `PrefixAfter`, `Unmap`, `ParseCIDR`, `MaybeParse`, `MaybeParseAddr`, `MaybeParsePrefix`, and `MaybeParseCIDR`.

Control flow: conversions bridge `net.IPNet` and `netip.Prefix`; arithmetic delegates bit operations to `daemon/libnetwork/ipbits`. `PrefixAfter` computes the next prefix after a previous allocation and returns invalid prefix on address overflow. `Unmap` reproduces Docker's historical IPv4-mapped IPv6 CIDR semantics by unmapping the address and truncating mask length. `MaybeParse` decorates parse functions so empty input returns zero value without error.

State and persistence: pure functions; no state.

Dependencies and integration: used by networking and option parsing paths that are migrating to `netip`.

Risks: `HostID` documents undefined behavior when bits exceed address bit length. `SubnetRange` uses shifts derived from prefix size and assumes valid inputs. `Unmap` intentionally preserves historical quirks that may surprise new callers.

Test signals: `netiputil_test.go` covers last address, next prefix, unmap invalid zero, CIDR parsing compatibility, and optional parse behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/netiputil/netiputil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/netiputil/netiputil_test.go -->
# sources/cloud-native/moby/daemon/internal/netiputil/netiputil_test.go

Purpose: validates key `netiputil` address arithmetic and parsing compatibility.

Important APIs and types: `TestLastAddr`, `TestPrefixAfter`, `TestUnmap`, `TestParseCIDR`, and `TestMaybeParse`.

Control flow: table tests verify IPv4/IPv6 broadcast-like last addresses and prefix sequencing, including overflow. CIDR parsing compares against legacy `net.ParseCIDR` behavior after setting `net.IP` to the parsed IP. Optional parsing checks empty, invalid, and valid inputs.

State and persistence: none.

Dependencies and integration: uses `gotest.tools/assert` and Go `net/netip`.

Risks: tests do not cover `ToIPNet`, `ToPrefix`, `HostID`, `SubnetRange`, or `AddrPortFromNet`.

Test signals: good coverage of the most contract-sensitive address math and historical IPv4-mapped CIDR behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/netiputil/netiputil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/nri/logshim.go -->
# sources/cloud-native/moby/daemon/internal/nri/logshim.go

Purpose: adapts containerd NRI framework logging to Docker's contextual logger.

Important APIs and types: `logShim` implements `nrilog.Logger` with `Debugf`, `Infof`, `Warnf`, and `Errorf`.

Control flow: each method prefixes messages with `NRI: ` and delegates to `log.G(ctx)`.

State and persistence: none.

Dependencies and integration: `nri.go` installs this logger with `nrilog.Set` when NRI starts.

Risks: format strings and arguments pass through directly; caller-controlled strings are logged as format strings by design.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/nri/logshim.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/nri/nri.go -->
# sources/cloud-native/moby/daemon/internal/nri/nri.go

Purpose: integrates Docker daemon container creation and state synchronization with containerd's NRI framework, allowing trusted plugins to observe containers and apply a limited set of create-time adjustments.

Important APIs and types: `NRI`, `ContainerLister`, `Config`, `NewNRI`, `GetInfo`, `Shutdown`, `PrepareReload`, `CreateContainer`, `syncFn`, `updateFn`, `setDefaultPaths`, `nriOptions`, `containerToNRI`, `stateToNRI`, `applyAdjustments`, `checkForUnsupportedAdjustments`, `applyEnvVars`, and `applyMounts`.

Control flow: startup checks `DaemonConfig.Enable`, fills default plugin/config paths based on rootless state, installs the logging shim, creates an adaptation instance, and starts it. Create notifications convert Docker container state to NRI pod/container objects, call `CreateContainer`, reject update/evict responses, and apply supported adjustments. Plugin sync takes a write lock, snapshots all containers from `ContainerLister`, converts them while locking each container state, invokes the NRI sync callback, and rejects returned updates. Reload prepares a new adaptation and swaps it under lock before starting.

State and persistence: `NRI` holds config and the active adaptation behind an RW mutex. Plugin state is external; Docker container config/hostconfig may be mutated by env and mount adjustments before container creation. Default paths depend on rootless environment.

Dependencies and integration: depends on containerd NRI adaptation, Docker container types, daemon opts, rootless/homedir helpers, Docker version, and system-info API types.

Risks: implementation is intentionally incomplete: many NRI fields are nil/empty, asynchronous updates are not implemented, and most plugin adjustments are rejected. Plugins are trusted and can influence container env/mounts. `stateToNRI` logs at error level for every mapping, which may be noisy. Lock ordering with container state must remain careful during sync.

Test signals: no tests in this subset; coverage should include supported adjustments, rejected unsupported adjustments, reload, rootless path defaults, and sync ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/nri/nri.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/host_gateway_opts.go -->
# sources/cloud-native/moby/daemon/internal/opts/host_gateway_opts.go

Purpose: validates daemon host-gateway IP configuration.

Important APIs and types: `ValidateHostGatewayIPs([]netip.Addr) error`.

Control flow: iterates addresses and allows at most one IPv4 and at most one non-IPv4 address, returning explicit errors for duplicates.

State and persistence: none.

Dependencies and integration: used by daemon option validation for `host-gateway-ip`-style settings.

Risks: invalid `netip.Addr{}` is treated as non-IPv4 and can count as IPv6-like unless callers validate parsing beforehand.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/host_gateway_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/named_iplist_opts.go -->
# sources/cloud-native/moby/daemon/internal/opts/named_iplist_opts.go

Purpose: implements a named CLI/config option that appends parsed IP addresses to a referenced `[]netip.Addr`.

Important APIs and types: `NamedIPListOpts`, `NewNamedIPListOptsRef`, `String`, `Set`, `Type`, and `Name`.

Control flow: `Set` parses the value with `netip.ParseAddr` and appends it to the underlying slice. `String` returns `""` for no values or Go's slice formatting otherwise.

State and persistence: mutates the caller-provided slice pointer; no disk persistence.

Dependencies and integration: follows Docker daemon option interfaces and is used for named IP-list settings.

Risks: storing a pointer to a slice means caller lifetime matters. No duplicate filtering or IPv4/IPv6 cardinality validation is applied here.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/named_iplist_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/opts.go -->
# sources/cloud-native/moby/daemon/internal/opts/opts.go

Purpose: implements boolean set/map daemon options with optional names for config reflection.

Important APIs and types: `SetOpts`, `NewSetOpts`, `Set`, `GetAll`, `String`, `Type`, `NamedSetOpts`, `NewNamedSetOpts`, and `Name`.

Control flow: `Set` splits input on `=`, rejects empty keys, treats missing value as true, parses present values with `strconv.ParseBool`, and writes the map. `NewSetOpts` initializes nil maps. `NamedSetOpts` embeds `SetOpts` and implements `opts.NamedOption`.

State and persistence: mutates an in-memory map supplied by caller or created on construction.

Dependencies and integration: used by daemon config/flag parsing for named feature-like maps.

Risks: map is not synchronized; callers must serialize option parsing. String output uses Go map formatting, which is not stable for user-facing ordering.

Test signals: `opts_test.go` covers true/false syntax, missing value, errors, and named option behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/opts_test.go -->
# sources/cloud-native/moby/daemon/internal/opts/opts_test.go

Purpose: validates boolean set option parsing and named option metadata.

Important APIs and types: `TestSetOpts` and `TestNamedSetOpts`.

Control flow: both tests parse `=1`, `=true`, `=0`, `=false`, and bare key forms, compare the resulting map and string, then assert parse errors for invalid bools, empty bools, and empty keys.

State and persistence: uses in-memory maps only.

Dependencies and integration: uses `gotest.tools/assert`.

Risks: expected string depends on map formatting and insertion behavior, which can be brittle if Go map display changes.

Test signals: good coverage of accepted and rejected option syntaxes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/opts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/baggage.go -->
# sources/cloud-native/moby/daemon/internal/otelutil/baggage.go

Purpose: provides helpers for constructing static OpenTelemetry baggage members and baggage values.

Important APIs and types: constant `TriggerKey`, `MustNewBaggage`, and `MustNewMemberRaw`.

Control flow: each helper calls the OTel constructor and logs fatal on error. Comments warn not to use dynamic values.

State and persistence: none.

Dependencies and integration: used by tracing instrumentation for static baggage such as trigger metadata.

Risks: fatal logging exits the process on invalid input, so callers must only pass compile-time/static values.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/baggage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/environ_carrier.go -->
# sources/cloud-native/moby/daemon/internal/otelutil/environ_carrier.go

Purpose: implements an OpenTelemetry text-map carrier for propagating trace context through environment variables.

Important APIs and types: `EnvironCarrier`, `Get`, `Set`, `Keys`, `Environ`, and `PropagateFromEnvironment`.

Control flow: supports only `traceparent` and `tracestate` keys. `Environ` emits uppercase `TRACEPARENT`/`TRACESTATE` entries for non-empty values. `PropagateFromEnvironment` reads those env vars.

State and persistence: carrier stores two strings in memory and serializes to environment entries.

Dependencies and integration: used when daemon code needs to pass trace context to child processes.

Risks: unsupported keys are silently ignored. It does not parse or validate trace context values.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/environ_carrier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/provider.go -->
# sources/cloud-native/moby/daemon/internal/otelutil/provider.go

Purpose: creates an OpenTelemetry tracer provider for Docker with BuildKit's exporter detection and baggage copying.

Important APIs and types: `NewTracerProvider(ctx, allowNoop)`.

Control flow: attempts to detect a span exporter. On detection failure, returns noop only when allowed; otherwise it proceeds with the possibly nil/none exporter path. If noop is allowed and exporter is explicitly none, returns noop. Otherwise builds an SDK provider with default resource, sync recorder, batch exporter, and baggage-copy span processor.

State and persistence: returns provider and shutdown function; no package state.

Dependencies and integration: depends on BuildKit tracing detection, OTel SDK, baggagecopy processor, and Docker logging.

Risks: behavior when exporter detection fails and `allowNoop` is false depends on downstream exporter value. Sync recorder plus batcher must be shut down by caller.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/status.go -->
# sources/cloud-native/moby/daemon/internal/otelutil/status.go

Purpose: records error status on an OpenTelemetry span.

Important APIs and types: `RecordStatus(span trace.Span, err error)`.

Control flow: if `err` is non-nil, records the error and sets span status to `codes.Error` with the error string. Nil errors leave span status unchanged.

State and persistence: mutates span state only.

Dependencies and integration: small helper for daemon tracing instrumentation.

Risks: error messages may include sensitive data if callers pass unredacted errors.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/otelutil/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform.go -->
# sources/cloud-native/moby/daemon/internal/platform/platform.go

Purpose: exposes runtime host architecture and possible CPU IDs with platform-specific implementations.

Important APIs and types: `Architecture`, `PossibleCPU`, package variables `arch` and `onceArch`.

Control flow: `Architecture` calls `runtimeArchitecture` once and logs errors. `PossibleCPU` returns platform `possibleCPUs` if available; otherwise it falls back to a slice from 0 through `runtime.NumCPU()`.

State and persistence: caches architecture for process lifetime. CPU list may be cached in platform-specific code.

Dependencies and integration: used by daemon info/resource code that needs host rather than compiler architecture.

Risks: fallback loop uses `<= runtime.NumCPU()`, producing one more CPU index than conventional 0..N-1. Architecture errors leave cached `arch` empty.

Test signals: Linux parsing is covered in `platform_linux_test.go`; generic fallback is not.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform_linux.go -->
# sources/cloud-native/moby/daemon/internal/platform/platform_linux.go

Purpose: implements Linux host architecture and possible CPU discovery.

Important APIs and types: `possibleCPUs`, `parsePossibleCPUs`, and `runtimeArchitecture`.

Control flow: `possibleCPUs` reads `/sys/devices/system/cpu/possible`, trims whitespace, and parses comma-separated single CPU IDs or ranges. `runtimeArchitecture` calls `unix.Uname` and returns the machine string.

State and persistence: possible CPU list is cached with `sync.OnceValue`.

Dependencies and integration: used by `platform.go`.

Risks: parser returns nil for any malformed segment and does not validate range start <= end beyond loop behavior. Cached nil means transient read failures persist for process lifetime.

Test signals: `platform_linux_test.go` covers continuous, non-continuous, single, empty, invalid, and malformed inputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform_linux_test.go -->
# sources/cloud-native/moby/daemon/internal/platform/platform_linux_test.go

Purpose: validates Linux possible-CPU range parsing.

Important APIs and types: `TestParsePossibleCPUs`.

Control flow: table-driven cases pass strings such as `0-3`, `0-2,4,6-7`, `5`, empty input, invalid tokens, and malformed ranges to `parsePossibleCPUs`.

State and persistence: none.

Dependencies and integration: uses `gotest.tools/assert`.

Risks: does not test reversed ranges or whitespace around segments.

Test signals: confirms primary supported `/sys` formats and nil-on-malformed behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform_windows.go -->
# sources/cloud-native/moby/daemon/internal/platform/platform_windows.go

Purpose: implements Windows host architecture and processor count detection.

Important APIs and types: `systeminfo`, Windows architecture constants, `runtimeArchitecture`, `NumProcs`, and `possibleCPUs`.

Control flow: calls `GetSystemInfo` through `syscall.SyscallN`, maps processor architecture codes to strings, returns processor count, and leaves possible CPU discovery unimplemented.

State and persistence: lazy DLL/proc handles are package globals; no other state.

Dependencies and integration: used by `platform.go` on Windows.

Risks: TODO notes `GetNativeSystemInfo` would be more accurate for WOW64 processes. Unknown architecture returns an error. `possibleCPUs` nil forces generic fallback.

Test signals: no direct Windows tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/plugin/executor/containerd/containerd.go -->
# sources/cloud-native/moby/daemon/internal/plugin/executor/containerd/containerd.go

Purpose: implements the Docker plugin executor using containerd/libcontainerd containers and tasks.

Important APIs and types: `ExitHandler`, `Executor`, `c8dPlugin`, `New`, `Create`, `Restore`, `IsRunning`, `Signal`, `ProcessEvent`, `deleteTaskAndContainer`, `rio`, and `attachStreamsFunc`.

Control flow: `New` creates a libcontainerd remote client with the executor as backend. `Create` replaces any stale plugin container, creates a task with stdout/stderr attachment, starts it, and stores plugin state. `Restore` loads an existing container, attaches to its task, checks status, cleans up stopped/missing tasks, and stores live state. `ProcessEvent` handles only exit events: it deletes task/container resources and delegates to `ExitHandler`.

State and persistence: in-memory `plugins` map tracks active plugin ID to container/task handles under mutex. Actual plugin runtime state persists in containerd until cleanup.

Dependencies and integration: depends on containerd client/cio, libcontainerd replace/client/types, Docker errdefs, plugin exit handling, and OCI specs.

Risks: `attachStreamsFunc` panics if stdin exists because plugin stdin should never be created. `ProcessEvent` calls exit handler even for unknown plugin exits. `Create` stores plugin only after task start, so early exit events could race with insertion.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/plugin/executor/containerd/containerd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/progress/progress.go -->
# sources/cloud-native/moby/daemon/internal/progress/progress.go

Purpose: defines daemon progress messages and output abstractions for transfers and other long-running operations.

Important APIs and types: `Progress`, `Output`, `ChanOutput`, `DiscardOutput`, `Update`, `Updatef`, `Message`, `Messagef`, and `Aux`.

Control flow: channel output writes progress to a channel and recovers from panics, preserving historical behavior around closed channels. Convenience helpers construct action, message, or auxiliary progress records.

State and persistence: progress records are transient. Channel output writes to caller-owned channel.

Dependencies and integration: used by image pull/push/load/save and similar daemon operations.

Risks: `chanOutput.WriteProgress` suppresses panics and always returns nil, so closed channels can drop progress silently. `Aux` payload is untyped.

Test signals: progress reader tests cover progress emission via channel output indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/progress/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/progress/progressreader.go -->
# sources/cloud-native/moby/daemon/internal/progress/progressreader.go

Purpose: wraps an `io.ReadCloser` and emits throttled progress updates as bytes are read.

Important APIs and types: `Reader`, `NewProgressReader`, `Read`, `Close`, and `updateProgress`.

Control flow: `Read` advances `current`, chooses an update threshold of 512 KiB or 1 percent of known size if smaller, emits progress when threshold is exceeded or an error occurs, and marks last update when read returns error with no bytes. `Close` emits a full progress bar if closing before the expected size, then closes the underlying reader. `updateProgress` rate-limits updates to 100 ms unless final or exactly complete.

State and persistence: tracks current bytes, size, last update offset, ID/action, output, and rate limiter in memory.

Dependencies and integration: used by transfer paths to report progress through `progress.Output`.

Risks: when size is small, threshold can become zero and cause frequent updates, mitigated by rate limiter. Close treats premature close as complete for display. Output errors are ignored.

Test signals: `progressreader_test.go` verifies premature close emits progress and complete read closes silently.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/progress/progressreader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/progress/progressreader_test.go -->
# sources/cloud-native/moby/daemon/internal/progress/progressreader_test.go

Purpose: tests progress reader close behavior.

Important APIs and types: `TestOutputOnPrematureClose` and `TestCompleteSilently`.

Control flow: the premature-close test reads only part of a short stream, drains prior progress, closes the reader, and expects a new progress update. The complete test reads all bytes, drains progress, closes, and expects no new update.

State and persistence: in-memory `bytes.Reader` and buffered channel.

Dependencies and integration: validates interaction between `NewProgressReader`, `ChanOutput`, `Read`, and `Close`.

Risks: tests do not verify rate limiting, exact progress fields, or underlying close errors.

Test signals: focused regression signal for user-visible progress completion behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/progress/progressreader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/errors.go -->
# sources/cloud-native/moby/daemon/internal/quota/errors.go

Purpose: defines the quota-not-supported error used across quota implementations.

Important APIs and types: `ErrQuotaNotSupported` and `errQuotaNotSupported`, which implements Docker `errdefs.ErrNotImplemented`.

Control flow: no control flow beyond `Error` and marker method `NotImplemented`.

State and persistence: none.

Dependencies and integration: returned by unsupported quota builds and by Linux project quota setup when prerequisites are missing.

Risks: message text is generic and may not identify whether filesystem, kernel, namespace, or build tags caused lack of support.

Test signals: indirectly exercised by quota tests when skipped/unsupported.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/projectquota.go -->
# sources/cloud-native/moby/daemon/internal/quota/projectquota.go

Purpose: implements Linux XFS project quota controls for assigning per-directory quota limits, compiled only on Linux with cgo and without `exclude_disk_quota`.

Important APIs and types: C quota/ioctl constants, `pquotaState`, `getPquotaState`, `updateMinProjID`, `NewControl`, `SetQuota`, `GetQuota`, `setProjectQuota`, `getProjectID`, `setProjectID`, `findNextProjectID`, `makeBackingFsDev`, and `hasQuotaSupport`.

Control flow: `NewControl` rejects user namespaces, creates a backing block device node under the base path, checks project quota support via `quotactl`, reads the base project ID, tests setting quota on the next ID, initializes `Control`, updates global next-ID state, and scans existing directories to avoid reusing project IDs. `SetQuota` assigns a new project ID to a target directory if not already known, increments global `nextProjectID`, records it in the control map, and sets the block hard/soft limit. `GetQuota` looks up the target's project ID and reads quota limits. Helper functions use `opendir`, `dirfd`, FSGETXATTR/FSSETXATTR ioctls, mknod, and quotactl.

State and persistence: project IDs and inherit flags persist as filesystem extended attributes; quota limits persist in filesystem quota state. `Control.quotas` maps target paths to project IDs, and global `pquotaState` allocates IDs process-wide.

Dependencies and integration: used by storage drivers such as overlay that apply project quotas to container directories. Depends on cgo, Linux quota headers, XFS project quota support, `moby/sys/userns`, and privileged syscalls.

Risks: requires root-like privileges and a filesystem with project quota accounting/enforcement enabled. Global next-ID allocation can race with external quota tools or other daemon instances. `makeBackingFsDev` creates a block device node inside the storage root. Scanning only immediate children and grandchildren assumes storage-driver layout.

Test signals: `projectquota_test.go` and `testhelpers.go` create an XFS loopback image and verify support detection, enforcement, and retrieval when environment permits.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/projectquota.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/projectquota_test.go -->
# sources/cloud-native/moby/daemon/internal/quota/projectquota_test.go

Purpose: integration-tests Linux project quota behavior on an XFS loopback filesystem.

Important APIs and types: `TestBlockDev`, `testBlockDevQuotaDisabled`, `testBlockDevQuotaEnabled`, `testSmallerThanQuota`, `testBiggerThanQuota`, `testRetrieveQuota`, and constant `testQuotaSize`.

Control flow: skips when quota tests cannot run, creates a sparse XFS image, mounts it with and without `prjquota`, checks support detection, sets quotas, verifies writing below quota succeeds, writing above quota fails, and quota retrieval returns expected size.

State and persistence: creates temporary image files, mounts loopback filesystems, writes test files, sets filesystem project quota state, and unmounts in helpers.

Dependencies and integration: requires Linux, root, `mkfs.xfs`, mount support, and quota-enabled XFS.

Risks: environment-heavy test can skip or fail due to host kernel/userspace capabilities. Writing a file above quota may return different error shapes; the test only asserts an error exists.

Test signals: strong end-to-end signal where supported, but often skipped in unprivileged CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/projectquota_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/projectquota_unsupported.go -->
# sources/cloud-native/moby/daemon/internal/quota/projectquota_unsupported.go

Purpose: provides quota stubs for unsupported builds/platforms.

Important APIs and types: `NewControl`, `SetQuota`, and `GetQuota`.

Control flow: all functions return `ErrQuotaNotSupported`.

State and persistence: none.

Dependencies and integration: compiled when not Linux, when cgo is disabled, or when disk quota is excluded.

Risks: methods on a nil `*Control` can still return not-supported without dereferencing state, but callers should not assume quota support after `NewControl` fails.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/projectquota_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/testhelpers.go -->
# sources/cloud-native/moby/daemon/internal/quota/testhelpers.go

Purpose: supplies privileged Linux helpers for project quota integration tests.

Important APIs and types: `CanTestQuota`, `PrepareQuotaTestImage`, `WrapMountTest`, and `WrapQuotaTest`.

Control flow: `CanTestQuota` requires UID 0 and `mkfs.xfs`. `PrepareQuotaTestImage` creates a 300 MiB sparse file and formats it with compatibility options. `WrapMountTest` mounts the image with loop and optional `prjquota`, creates a backing block device and temp directory, invokes the test function, and unmounts. `WrapQuotaTest` creates a `Control` and quota test subdir for nested test functions.

State and persistence: creates temporary sparse files, filesystems, mounts, device nodes, and directories, then cleans them up.

Dependencies and integration: used by `projectquota_test.go`; depends on external `mkfs.xfs` and `mount`.

Risks: privileged mount helpers can fail for host-policy reasons; cleanup failures call `Fatalf`. The sparse image size is fixed to satisfy XFS minimums.

Test signals: provides the scaffolding that makes quota tests realistic rather than mocked.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/testhelpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/types.go -->
# sources/cloud-native/moby/daemon/internal/quota/types.go

Purpose: defines shared quota data structures.

Important APIs and types: `Quota` with `Size`, and `Control` with backing block device, embedded RW mutex, and target-path-to-project-ID map.

Control flow: no functions in this file.

State and persistence: `Control` carries in-memory quota bookkeeping; actual quota state is applied by platform implementation.

Dependencies and integration: used by supported and unsupported quota implementations and storage drivers.

Risks: embedding `sync.RWMutex` means `Control` must not be copied after use. Path keys require callers to use consistent canonical paths.

Test signals: exercised indirectly by project quota tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/refstore/errors.go -->
# sources/cloud-native/moby/daemon/internal/refstore/errors.go

Purpose: defines typed errors for image reference store operations.

Important APIs and types: `notFoundError`, `invalidTagError`, and `conflictingTagError`, implementing Docker/containerd errdefs marker methods.

Control flow: each type returns its string message and exposes marker methods `NotFound`, `InvalidParameter`, or `Conflict`.

State and persistence: none.

Dependencies and integration: used by `store.go` so callers can classify reference errors through errdefs helpers.

Risks: marker methods have no payload beyond string text; callers needing structured context must parse or wrap elsewhere.

Test signals: `store_test.go` checks conflict and invalid-argument classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/refstore/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/refstore/store.go -->
# sources/cloud-native/moby/daemon/internal/refstore/store.go

Purpose: implements Docker's JSON-backed image reference store, mapping repository references to image digests and supporting reverse lookup by digest.

Important APIs and types: `Association`, `Store`, `refStore`, `repository`, sorting types, `NewReferenceStore`, `AddTag`, `AddDigest`, `favorDigest`, `addReference`, `Delete`, `Get`, `References`, `ReferencesByName`, `save`, and `reload`.

Control flow: `NewReferenceStore` resolves the JSON path, initializes maps, reloads existing JSON or creates a new file. Adds normalize tag-only refs, favor digest over tag+digest refs, reject ambiguous `sha256` repo tags, enforce digest immutability, optionally force tag overwrites, update reverse cache, and save atomically. Delete normalizes the ref, removes it from repository and reverse cache, prunes empty maps, and saves. Get gives digest precedence for tag+digest references. Reload decodes JSON and rebuilds reverse cache.

State and persistence: repositories persist as JSON at `jsonPath`, written by `atomicwriter.WriteFile` with mode 0600. In-memory state is guarded by RW mutex and includes `referencesByIDCache`.

Dependencies and integration: used by image management code to track tags/digests independent of containerd metadata. Depends on distribution/reference, OCI digest, and atomicwriter.

Risks: JSON corruption prevents store creation. Cache rebuild skips unparsable refs silently even though that should not happen. Save marshals the store struct, relying on exported `Repositories` and unexported fields being ignored. Force applies only to tags, never digests.

Test signals: `store_test.go` covers load/save exact JSON, add/delete/get, lexical sorting, force rules, digest immutability, not-found, invalid tags, and errdefs classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/refstore/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/refstore/store_test.go -->
# sources/cloud-native/moby/daemon/internal/refstore/store_test.go

Purpose: verifies JSON reference store persistence, lookup, mutation, sorting, and error classification.

Important APIs and types: `TestLoad`, `TestSave`, `TestAddDeleteGet`, `TestInvalidTags`, shared `saveLoadTestCases`, and expected marshaled JSON.

Control flow: load test writes fixture JSON and verifies every reference resolves. Save test adds tags/digests and compares exact output JSON. Add/delete/get test exercises name-only tags, multiple refs per digest, duplicate adds, digest conflict behavior, force tag overwrite, reverse lookups, repository lookups, not-found paths, and deletion. Invalid-tag test rejects `sha256` repo ambiguity and adding digest refs as tags.

State and persistence: uses temporary JSON files and real `NewReferenceStore` persistence.

Dependencies and integration: uses distribution/reference, OCI digest, containerd errdefs, and gotest assertions.

Risks: exact JSON comparison depends on deterministic map marshaling for string keys. Tests do not cover corrupted JSON reload or concurrent access.

Test signals: strong coverage of core store contract and on-disk compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/refstore/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/restartmanager/restartmanager.go -->
# sources/cloud-native/moby/daemon/internal/restartmanager/restartmanager.go

Purpose: decides if and when a container should restart according to Docker restart policies, with exponential backoff and cancellation.

Important APIs and types: `RestartManager`, `ErrRestartCanceled`, constants for backoff timing, `New`, `SetPolicy`, `ShouldRestart`, and `Cancel`.

Control flow: `ShouldRestart` rejects none policy, canceled managers, and concurrent active restarts. It resets backoff after executions of at least 10 seconds, otherwise doubles timeout up to one minute. It evaluates always, unless-stopped, and on-failure/max-retry policies. When restart is needed, it increments restart count, marks active, starts a goroutine that waits for either cancellation or timeout, closes the returned channel, and clears active after timeout. `Cancel` closes the cancel channel once.

State and persistence: in-memory policy, restart count, timeout, active/canceled flags, and cancel channel protected by mutex/once. Restart count may be initialized from persisted container metadata by caller.

Dependencies and integration: used by daemon container supervision after exits.

Risks: caller must wait for the returned channel before acting; calling `ShouldRestart` while active is an error. Backoff and restart count are not persisted here. Cancel sends `ErrRestartCanceled` on the channel and closes it.

Test signals: `restartmanager_test.go` covers initial timeout and timeout reset after long execution; policy matrix is tested elsewhere if at all.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/restartmanager/restartmanager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/restartmanager/restartmanager_test.go -->
# sources/cloud-native/moby/daemon/internal/restartmanager/restartmanager_test.go

Purpose: verifies restart backoff initialization and reset behavior.

Important APIs and types: `TestRestartManagerTimeout` and `TestRestartManagerTimeoutReset`.

Control flow: tests create an always policy manager, call `ShouldRestart`, and inspect `rm.timeout`. The reset test preloads a five-second timeout and uses a ten-second execution duration to confirm reset to default.

State and persistence: directly inspects in-memory manager fields.

Dependencies and integration: uses Docker container restart policy type.

Risks: tests do not wait on the returned restart channel, so active goroutines may briefly remain. They do not cover cancellation, on-failure, unless-stopped, max retry, or active-call errors.

Test signals: narrow but useful coverage of backoff timing contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/restartmanager/restartmanager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/mountopts/mountopts_linux.go -->
# sources/cloud-native/moby/daemon/internal/rootless/mountopts/mountopts_linux.go

Purpose: computes mount flags locked by `CL_UNPRIVILEGED` for a path so rootless bind mounts can preserve required options.

Important APIs and types: `UnprivilegedMountFlags(path string) ([]string, error)`.

Control flow: calls `unix.Statfs`, checks selected mount flag bits, and returns option strings for readonly, nodev, noexec, nosuid, noatime, relatime, and nodiratime.

State and persistence: reads filesystem mount state; no mutation.

Dependencies and integration: used by rootless mount setup to avoid kernel rejections when remounting with options.

Risks: returned flag order depends on map iteration, so callers should not rely on ordering. It only includes a known subset of locked flags.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/mountopts/mountopts_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/rootless.go -->
# sources/cloud-native/moby/daemon/internal/rootless/rootless.go

Purpose: detects whether Docker is running under RootlessKit.

Important APIs and types: `RunningWithRootlessKit() bool`.

Control flow: returns true when `ROOTLESSKIT_STATE_DIR` is non-empty.

State and persistence: reads process environment.

Dependencies and integration: used by NRI path defaults and rootless behavior toggles.

Risks: environment-variable detection can be spoofed or missing in unusual launch setups.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/rootless.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/rootless_linux.go -->
# sources/cloud-native/moby/daemon/internal/rootless/rootless_linux.go

Purpose: provides Linux helpers for RootlessKit detached network namespace handling and tracking threads already executing in container sandbox namespaces.

Important APIs and types: `DetachedNetNS`, `detachedNetNS`, `RunInNetNS`, `MarkInSandboxNS`, `UnmarkInSandboxNS`, `InSandboxNS`, and `sandboxNSThreads`.

Control flow: `detachedNetNS` checks `ROOTLESSKIT_STATE_DIR/netns`. `RunInNetNS` runs the function directly if no namespace path is supplied; otherwise it starts a goroutine, locks its OS thread, opens target and original namespaces, enters target namespace, runs the function, attempts to restore original namespace, and deliberately leaves the thread locked if restoration fails. Mark/unmark track current TID in a sync map.

State and persistence: reads environment and namespace files. Maintains process-global map of TIDs currently marked as sandbox namespace threads.

Dependencies and integration: used by rootless networking and iptables/nft wrapper decisions. Depends on `vishvananda/netns`, runtime thread locking, and Linux TIDs.

Risks: namespace switching is thread-affine; incorrect unlock/restore can taint runtime threads. `DetachedNetNS` caches results with `sync.OnceValues`, so changes to env/files after first call are ignored. Mark/unmark require callers to be on the same locked OS thread.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/rootless_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/specconv/specconv_linux.go -->
# sources/cloud-native/moby/daemon/internal/rootless/specconv/specconv_linux.go

Purpose: mutates OCI runtime specs to be compatible with rootless Docker and rootful-in-rootless Docker.

Important APIs and types: `ToRootfulInRootless`, `ToRootless`, `getCurrentOOMScoreAdj`, `toRootless`, `isHostNS`, `bindMountHostProcfs`, `bindMountHostIPC`, and `removeSysfs`.

Control flow: rootful-in-rootless only raises `OOMScoreAdj` to at least the daemon's current value. Full rootless conversion removes unsupported cgroup settings when no cgroup v2 controllers are delegated, prunes resource sections for missing controllers when delegated, clears devices/hugepage/network resources, raises OOMScoreAdj, detects host PID/IPC/network namespaces, bind-mounts host `/proc`, `/dev/shm`, and `/dev/mqueue` where needed, and removes sysfs mounts for host networking with RootlessKit detached netns.

State and persistence: mutates the passed `specs.Spec` in memory. Reads `/proc/self/oom_score_adj`, namespace symlinks, and RootlessKit state.

Dependencies and integration: used before creating rootless containers with runc. Depends on rootless namespace helpers, OCI specs, `/proc`, and Docker logging.

Risks: namespace detection compares symlink targets and returns host namespace if a namespace type is absent from the spec. Slice filtering mutates mount/path slices in place. Missing controller handling must stay aligned with runtime/kernel support. Removing sysfs is conditional on detecting an existing sysfs mount.

Test signals: no direct tests in this subset; high-value coverage would include cgroup controller pruning and host namespace mount rewrites.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/specconv/specconv_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/config.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/config.go

Purpose: decodes container create requests from JSON, fills daemon-side defaults, and validates platform-specific options.

Important APIs and types: `DecodeCreateRequest`, `decodeCreateRequest`, `validateCreateRequest`, and `loadJSON`.

Control flow: `DecodeCreateRequest` decodes then validates. `decodeCreateRequest` reads JSON into `container.CreateRequest`, rejects missing `Config`, initializes nil maps/configs for volumes, host config, port bindings, networking config, and endpoints, and defaults non-Windows empty network mode to `default`. `validateCreateRequest` delegates to network mode, isolation, QoS, resources, privileged, and readonly-rootfs validators. `loadJSON` wraps decoder errors as invalid JSON and rejects extra JSON values using `dec.More`.

State and persistence: no persistence; mutates returned request defaults in memory.

Dependencies and integration: used by daemon API create-container path. Depends on API container/network types and sysinfo.

Risks: `dec.More` is not a full trailing-token check outside arrays/objects, so extra JSON detection may be incomplete. Defaults preserve backward-compatible API behavior and are platform-sensitive. Validation split across platform files must stay in sync.

Test signals: `config_test.go` covers fixture decoding, isolation validation, and Windows privileged validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/config_test.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/config_test.go

Purpose: tests container create request decoding and selected daemon-side validation.

Important APIs and types: `TestDecodeCreateRequest`, `TestDecodeCreateRequestIsolation`, and `TestDecodeCreateRequestPrivileged`.

Control flow: fixture tests decode Unix and Windows API 1.24 JSON and assert image, entrypoint, and memory. Isolation tests marshal minimal requests and assert platform-dependent acceptance of default/process/hyperv/invalid values. Privileged test asserts Windows rejects privileged mode and non-Windows accepts it.

State and persistence: reads fixture JSON files; no persistence.

Dependencies and integration: uses API container types, sysinfo, runtime GOOS checks, containerd errdefs, and gotest assertions.

Risks: tests depend on current platform, so Windows-only rejection paths are not exercised on Linux except through conditional expectations. Fixture coverage is broad but asserts only a few decoded fields.

Test signals: validates backward-compatible request decoding for old fixtures and key platform validation paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/errors.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/errors.go

Purpose: centralizes runconfig validation and invalid JSON error types.

Important APIs and types: `validationError` and `invalidJSONError`.

Control flow: `validationError` creates containerd invalid-argument errors. `invalidJSONError` prefixes JSON decode errors, unwraps the original error, and implements `InvalidParameter`.

State and persistence: none.

Dependencies and integration: used by create request decoding and validation so API handlers can classify errors.

Risks: callers comparing exact error strings will see `invalid JSON: ` prefix. Validation errors carry only message text.

Test signals: indirectly covered by runconfig tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/fixtures/unix/container_config_1_24.json -->
# sources/cloud-native/moby/daemon/internal/runconfig/fixtures/unix/container_config_1_24.json

Purpose: fixture representing an API 1.24 Unix container create request.

Important APIs and types: JSON fields include command/entrypoint, exposed ports, host config resources, bind mounts, capabilities, DNS, links, logging, memory, network mode, port bindings, restart policy, volumes-from, labels, MAC address, networking config, stdin/TTY settings, and volumes.

Control flow: no executable flow; consumed by `TestDecodeCreateRequest`.

State and persistence: static test data preserving older API request shape.

Dependencies and integration: validates `runconfig.DecodeCreateRequest` compatibility with historical Unix Docker run options.

Risks: fixture may lag current API fields by design; tests assert only selected decoded values.

Test signals: confirms broad JSON unmarshalling remains compatible for Unix create requests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/fixtures/unix/container_config_1_24.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/fixtures/windows/container_config_1_24.json -->
# sources/cloud-native/moby/daemon/internal/runconfig/fixtures/windows/container_config_1_24.json

Purpose: fixture representing an API 1.24 Windows container create request.

Important APIs and types: JSON mirrors the Unix fixture but uses Windows image/entrypoint and Windows-style bind/volume paths.

Control flow: no executable flow; consumed by `TestDecodeCreateRequest`.

State and persistence: static compatibility test data.

Dependencies and integration: validates `runconfig.DecodeCreateRequest` compatibility with historical Windows create request payloads.

Risks: contains fields that may be ignored or invalid for modern Windows behavior; the decoding test only checks a subset.

Test signals: confirms Windows fixture decodes with expected image, entrypoint, and memory values.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/fixtures/windows/container_config_1_24.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/hostconfig.go

Purpose: validates network-mode conflicts common to all platforms, focused on container network mode.

Important APIs and types: `validateNetContainerMode`.

Control flow: returns nil unless `NetworkMode` is exactly container mode or container-like. It then requires a target container ID/name and rejects conflicts with hostname, links, DNS, extra hosts, port publishing, publish-all, and exposed ports.

State and persistence: none.

Dependencies and integration: called by platform-specific `validateNetMode` functions in create request validation.

Risks: FIXME notes a network named `container` without colon is not treated as container-mode by one check. Conflict messages are API-visible.

Test signals: no direct tests in this subset for this helper.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_test.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_test.go

Purpose: tests non-Windows resource validation for host config.

Important APIs and types: `TestValidateResources`.

Control flow: table tests build `HostConfig.Resources` and `sysinfo.SysInfo` combinations, then call `validateResources`, expecting invalid-argument errors for unsupported CPU realtime settings, realtime runtime greater than period, and negative CPU shares when CPU shares are supported.

State and persistence: none.

Dependencies and integration: Linux/Unix build only; uses API container resources and sysinfo.

Risks: does not cover memory, blkio, cpuset, or Windows validators. Because CPU shares negative validation depends on support flag, unsupported systems may still pass invalid values to lower layers.

Test signals: focused coverage of CPU realtime and shares validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_unix.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_unix.go

Purpose: implements non-Windows create-request hostconfig validation.

Important APIs and types: `validateNetMode`, `validateIsolation`, `validateQoS`, `validateResources`, `validatePrivileged`, and `validateReadonlyRootfs`.

Control flow: network validation adds UTS/hostname and host-network/links conflict checks after common container-mode validation. Isolation allows only valid default-like isolation. QoS rejects I/O maximum bandwidth/IOPS. Resource validation checks CPU realtime support and period/runtime ordering and rejects negative CPU shares only when CPU shares are supported. Privileged and readonly-rootfs are accepted.

State and persistence: none.

Dependencies and integration: called by `validateCreateRequest` in `config.go`.

Risks: some unsupported resource settings are intentionally not rejected for backward compatibility and may fail later at runtime. Error text includes `runtime.GOOS`.

Test signals: `hostconfig_test.go` covers selected resource cases; `config_test.go` covers isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_windows.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_windows.go

Purpose: implements Windows create-request hostconfig validation.

Important APIs and types: `validateNetMode`, `validateIsolation`, `validateQoS`, `validateResources`, `validatePrivileged`, and `validateReadonlyRootfs`.

Control flow: network validation applies common container-mode checks and additionally rejects container network mode with Hyper-V isolation. Isolation allows default/process/hyperv. QoS is accepted. Resource validation rejects CPU realtime period/runtime. Privileged and readonly rootfs are rejected.

State and persistence: none.

Dependencies and integration: called by `config.go` on Windows.

Risks: Windows-specific constraints are API-visible and must match daemon/runtime capabilities. QoS validation is permissive while non-Windows rejects I/O maximums.

Test signals: `config_test.go` conditionally covers isolation and privileged behavior depending on GOOS.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stack/stackdump.go -->
# sources/cloud-native/moby/daemon/internal/stack/stackdump.go

Purpose: dumps all goroutine stacks to stderr or a timestamped file for diagnostics.

Important APIs and types: `Dump`, `DumpToFile`, `dump`, and constant `stacksLogNameTemplate`.

Control flow: `Dump` writes to stderr. `DumpToFile` opens a `goroutine-stacks-<timestamp>.log` file in the supplied directory or uses stderr for empty dir, then syncs/closes file and calls `dump`. `dump` repeatedly grows a buffer until `runtime.Stack` fits, then writes it.

State and persistence: writes diagnostic stack logs to disk when a directory is supplied.

Dependencies and integration: used by daemon diagnostics and signal handling paths.

Risks: file mode is 0666 subject to umask. Timestamp removes colons but can still collide if called multiple times in the same second. Dumping all goroutines may include sensitive stack data.

Test signals: `stackdump_test.go` confirms stderr path and file contains `goroutine`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stack/stackdump.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stack/stackdump_test.go -->
# sources/cloud-native/moby/daemon/internal/stack/stackdump_test.go

Purpose: validates stack dump helpers.

Important APIs and types: `TestDump`, `TestDumpToFile`, and `TestDumpToFileWithEmptyInput`.

Control flow: tests call `Dump`, write a dump to a temp directory and check file contents include `goroutine`, and call `DumpToFile("")` expecting stderr name.

State and persistence: creates a temp diagnostic file in one test and writes to stderr in others.

Dependencies and integration: uses gotest assertions.

Risks: `Dump` writes to test stderr. Tests do not cover file open/write failures or timestamp collisions.

Test signals: basic coverage for successful dump paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stack/stackdump_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stdcopymux/stdcopy_example_test.go -->
# sources/cloud-native/moby/daemon/internal/stdcopymux/stdcopy_example_test.go

Purpose: documents and tests example usage of `stdcopymux.NewStdWriter` with Docker's `stdcopy.StdCopy` demultiplexer.

Important APIs and types: `ExampleNewStdWriter`.

Control flow: creates an `io.Pipe`, starts a goroutine demuxing to stdout/stderr, writes alternating stdout and stderr messages through mux writers, writes a `Systemerr` message, waits for demux completion, and verifies example output.

State and persistence: uses in-memory pipe and process stdout for example output.

Dependencies and integration: demonstrates interoperability between daemon `stdcopymux` writer and API `stdcopy` reader.

Risks: example sleeps to interleave output and writes to `os.Stdout`; timing changes could affect perceived behavior, though expected output is deterministic by write order.

Test signals: executable documentation that system-error frames terminate demuxing with an error message.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stdcopymux/stdcopy_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stdcopymux/stdcopy_test.go -->
# sources/cloud-native/moby/daemon/internal/stdcopymux/stdcopy_test.go

Purpose: tests mux writer framing and compatibility/error behavior with `stdcopy.StdCopy`.

Important APIs and types: `TestNewStdWriter`, `TestWriteWithUninitializedStdWriter`, `TestWriteWithNilBytes`, `TestWrite`, `errWriter`, `TestWriteWithWriterError`, `TestWriteDoesNotReturnNegativeWrittenBytes`, `getSrcBuffer`, `TestStdCopyWriteAndRead`, `customReader`, and many `StdCopy` error-path tests plus `BenchmarkWrite`.

Control flow: tests validate writer construction, nil/uninitialized writes, header-adjusted byte counts, negative count clamping, round-trip multiplexing of large stdout/stderr frames, read header/frame errors, truncated/corrupted frame behavior, invalid header handling, write errors, short writes, and system-error stream propagation. Benchmark repeatedly writes framed data to discard.

State and persistence: in-memory buffers/readers/writers only.

Dependencies and integration: tests `stdcopymux.NewStdWriter` against public `github.com/moby/moby/api/pkg/stdcopy.StdCopy`.

Risks: tests call into API package demuxer, so failures may reflect reader or writer changes. They do not exercise concurrent writes to the same underlying writer.

Test signals: strong coverage of mux frame format, byte accounting, and error propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stdcopymux/stdcopy_test.go -->
