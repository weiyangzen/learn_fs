# subset-b-000055 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/plugins/plugins.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/plugins/plugins.go

## Purpose
Implements `ctr plugins` and `ctr plugins inspect-runtime` for introspecting containerd plugin registrations and runtime metadata.

## Important APIs, Types, And Functions
Exports `Command`; defines `listCommand`, `inspectRuntimeCommand`, and `prettyPlatforms` for deduplicating and sorting platform strings.

## Control Flow
The list action opens a containerd client, calls `IntrospectionService().Plugins`, then chooses quiet, detailed, or tabular output. Runtime inspection resolves runtime options, calls `client.RuntimeInfo`, and emits indented JSON.

## State And Persistence
Read-only against containerd daemon state; output is written to stdout/app writer only.

## Dependencies And Integration Points
Uses containerd introspection and runtime info APIs, OCI platform formatting, gRPC error codes, tabwriter, and `containerd/plugin` skip detection.

## Risks And Test Signals
Status classification relies on substring matching the skip-plugin error text; detailed output exposes plugin exports and init errors. No local unit tests in this file; covered indirectly by CLI/integration tests. Source size reviewed: 197 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/plugins/plugins.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof.go

## Purpose
Defines `ctr pprof` subcommands that proxy Go pprof and trace endpoints from containerd debug server to stdout.

## Important APIs, Types, And Functions
Exports `Command`, `Client`, profile helpers for goroutine/heap/profile/trace/block/threadcreate, `getPProfClient`, and `httpGetRequest`.

## Control Flow
Each subcommand builds an HTTP client using the platform dialer, formats a `/debug/pprof/...` path with debug or duration arguments, validates HTTP 200, and streams the response body.

## State And Persistence
Does not persist state; it reads live debug endpoint data and writes raw profile or text output to stdout.

## Dependencies And Integration Points
Depends on `defaults.DefaultDebugAddress`, net/http transport Dial hook, and platform-specific `getPProfDialer`.

## Risks And Test Signals
Long profile/trace calls block until the debug endpoint responds; non-200 responses become errors. Test signal is dependency-injected `Client`, but this file has no direct test. Source size reviewed: 281 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof_unix.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof_unix.go

## Purpose
Unix implementation of the pprof dialer for containerd debug sockets.

## Important APIs, Types, And Functions
Implements `(*pprofDialer).pprofDial` and `getPProfDialer`.

## Control Flow
`getPProfDialer` records `unix` plus socket address; `pprofDial` ignores the HTTP pseudo host and dials the configured Unix socket.

## State And Persistence
No persistence; opens a transient Unix-domain socket connection.

## Dependencies And Integration Points
Uses Go net package and is selected by `!windows` build tag.

## Risks And Test Signals
Requires the debug socket path to exist and be accessible. Covered indirectly by `ctr pprof` behavior. Source size reviewed: 29 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof_windows.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof_windows.go

## Purpose
Windows implementation of the pprof dialer using named pipe transport.

## Important APIs, Types, And Functions
Implements `(*pprofDialer).pprofDial` and `getPProfDialer` with `npipe` protocol.

## Control Flow
The dialer stores `npipe` plus address and calls `winio.DialPipe` with no timeout when net/http needs a connection.

## State And Persistence
No persistence; opens a transient named-pipe connection.

## Dependencies And Integration Points
Depends on Microsoft go-winio and is selected by the `windows` build tag.

## Risks And Test Signals
A nil timeout means connection behavior is delegated to named-pipe dialing. Tested only through Windows pprof integration paths. Source size reviewed: 31 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/resolver.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/resolver.go

## Purpose
Builds registry resolvers and static credential helpers from ctr global registry flags.

## Important APIs, Types, And Functions
Exports `PushTracker`, `GetResolver`, `NewStaticCredentials`, and `staticCredentials.GetCredentials`; internal helpers handle password prompting and TLS config.

## Control Flow
Credentials are parsed from `--user` or `--refresh`, prompting with echo disabled when needed. Host options wire credentials, plain HTTP, TLS roots/client certs, hosts-dir overrides, and optional request dumping before constructing a Docker resolver.

## State And Persistence
Maintains process-local push tracking in memory; reads certificate files and terminal input but does not write persistent data.

## Dependencies And Integration Points
Uses containerd remotes/docker config, registry credential helper interfaces, console echo controls, x509/tls, and HTTP debug dumping.

## Risks And Test Signals
`--skip-verify` weakens TLS; prompting assumes an interactive console. Static credentials return only for the exact ref. No direct tests visible here. Source size reviewed: 199 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/run/run.go

## Purpose
Defines the cross-platform `ctr run` command, argument validation, mount parsing, IO setup, task start/wait, cleanup, and label merging.

## Important APIs, Types, And Functions
Exports `Command`; provides `withMounts`, `parseMountFlag`, and `buildLabels`.

## Control Flow
The action resolves image/rootfs/config arguments, rejects incompatible `--rm` and `--detach`, creates a container via platform `NewContainer`, optionally dumps the OCI spec, configures terminal/raw mode or null/log FIFO IO, creates and starts the task, optionally waits and propagates exit code, and cleans up CNI/container state for `--rm`.

## State And Persistence
Creates container metadata, snapshots, tasks, CNI metadata, FIFO paths, and optional dumped spec files. Cleanup removes task/container/snapshot when configured.

## Dependencies And Integration Points
Integrates console, cio, containerd client, task helpers, CNI metadata, OCI spec options, label validation, and platform-specific run files.

## Risks And Test Signals
Run is a high-blast-radius command: leaked containers/snapshots/FIFOs are possible on partial failure; terminal raw mode must reset. `parseMountFlag` relies on CSV parsing and rejects unknown keys. Tests are mainly in platform helper tests. Source size reviewed: 312 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run_unix.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/run/run_unix.go

## Purpose
Unix/Linux container construction for `ctr run`, including image unpacking, snapshots, namespaces, security, resources, devices, CDI/GPU, and runtime options.

## Important APIs, Types, And Functions
Defines Unix `platformRunFlags`, `NewContainer`, ID mapping parsers, namespace validation, `getNetNSPath`, GPU vendor/device helpers, CDI registry option, and `withCDIDeviceRequests`.

## Control Flow
Builds OCI spec opts from image or rootfs/config, unpacks image if needed, creates writable or userns-remapped snapshots, applies env/mounts/process/tty/privileged/net-host/seccomp/apparmor/cgroups/resources/devices/CDI/blockio/RDT/hostname/rlimits, records CNI extension metadata, resolves runtime options, and calls `client.NewContainer`.

## State And Persistence
Persists container metadata, snapshot metadata, unpacked layers, CNI extension metadata, and runtime options in containerd; reads host files for env/seccomp/apparmor/blockio/CDI and probes `/proc` for netns paths.

## Dependencies And Integration Points
Depends on containerd image/snapshot/diff/OCI packages, apparmor/seccomp contrib packages, goresctrl blockio, CDI libraries, OCI runtime spec, and platform defaults.

## Risks And Test Signals
Security-sensitive options can grant host devices, host networking, capabilities, or disabled cgroups. User namespace flags must be paired; CDI vendor detection only supports NVIDIA and AMD. Tests cover GPU helper behavior in `run_unix_test.go`. Source size reviewed: 593 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run_unix_test.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/run/run_unix_test.go

## Purpose
Unit tests for Unix GPU helper behavior used by `ctr run --gpus`.

## Important APIs, Types, And Functions
Defines `TestDetectGPUVendor` and `TestGpuDeviceNames`.

## Control Flow
Table-driven cases validate nil/empty/unknown vendor lists, NVIDIA/AMD precedence, multiple vendors, empty vendor errors, no IDs, and multiple GPU ID formatting.

## State And Persistence
No persistence; pure helper tests.

## Dependencies And Integration Points
Uses Go testing and `context.Background` against unexported package functions.

## Risks And Test Signals
Tests cover helper logic but not actual CDI registry refresh or OCI spec injection. Good regression signal for vendor precedence and CDI device name format. Source size reviewed: 156 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run_windows.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/run/run_windows.go

## Purpose
Windows container construction for `ctr run`, including Windows/LCOW spec setup, snapshots, networking, isolation, resource limits, devices, and runtime options.

## Important APIs, Types, And Functions
Defines Windows `platformRunFlags`, `NewContainer`, and Windows `getNetNSPath`.

## Control Flow
Chooses default Windows or LCOW spec based on snapshotter, applies env/mount/process/user/tty settings, unpacks the image, creates a snapshot, rejects host networking, optionally creates a netns for CNI, applies Hyper-V isolation and Windows CPU/memory/device options, and creates the container with runhcs runtime options when selected.

## State And Persistence
Persists container metadata, snapshots, unpacked image layers, and optional Windows network namespace paths/extensions.

## Dependencies And Integration Points
Uses hcsshim runhcs options, containerd image/snapshot/diff APIs, Windows OCI helpers, netns, console sizing, and runtime flags.

## Risks And Test Signals
CNI namespace creation must be cleaned by task teardown paths; devices require strict `IDType://ID` format. No direct tests in this file. Source size reviewed: 202 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/sandboxes/sandboxes.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/sandboxes/sandboxes.go

## Purpose
Implements `ctr sandboxes` for sandbox runtime lifecycle and metadata inspection.

## Important APIs, Types, And Functions
Exports `Command`; defines run/create, list, remove, and info subcommands.

## Control Flow
Run reads a JSON OCI sandbox spec, creates a sandbox with runtime and spec, starts it, and prints the ID. List queries the sandbox store with filters. Remove loads each sandbox, stops it, optionally ignores stop failures, and shuts it down. Info prints metadata JSON.

## State And Persistence
Creates, starts, stops, shuts down, and reads sandbox records in containerd; no local persistence beyond stdout/logging.

## Dependencies And Integration Points
Uses containerd sandbox client/store APIs, default runtime, OCI spec JSON, tabwriter, log, and errdefs.

## Risks And Test Signals
Remove logs and continues across IDs, so partial deletion is possible. Input spec validation is just JSON unmarshal into OCI spec. Test signal is integration-level only. Source size reviewed: 222 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/sandboxes/sandboxes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/shim/io_unix.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/shim/io_unix.go

## Purpose
Provides Unix FIFO plumbing for direct shim exec attachment.

## Important APIs, Types, And Functions
Defines `bufPool` and `prepareStdio`.

## Control Flow
For stdin/stdout/stderr FIFO paths, opens FIFOs, starts goroutines to copy between process stdio and FIFO handles, and returns a WaitGroup for attached mode.

## State And Persistence
Opens existing FIFO paths and transfers bytes; does not create persistent files itself.

## Dependencies And Integration Points
Uses `cio.OpenFifos`, os stdio, pooled buffers, sync.WaitGroup, and Unix build tag.

## Risks And Test Signals
Incorrect FIFO paths can block/open-fail; goroutine copy errors are not propagated beyond attach wait behavior. Exercised indirectly by `ctr shim exec --attach`. Source size reviewed: 93 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/shim/io_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/shim/pprof.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/shim/pprof.go

## Purpose
Adds `ctr shim pprof` subcommands that reuse generic pprof helpers against a shim debug socket.

## Important APIs, Types, And Functions
Defines shim pprof CLI commands and `getPProfClient`.

## Control Flow
Each subcommand delegates to the pprof package with a shim-specific HTTP client. The client resolves the shim socket from namespace, daemon address, and task ID, then installs it as the transport dialer.

## State And Persistence
Read-only live diagnostics; streams profile bytes/text to stdout.

## Dependencies And Integration Points
Integrates `cmd/ctr/commands/pprof`, namespace context, shim socket address calculation, Unix sockets, and net/http.

## Risks And Test Signals
Requires `--id` or address context that resolves to a live shim. Time-based profiles block. No direct tests in file. Source size reviewed: 165 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/shim/pprof.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/shim/shim.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/shim/shim.go

## Purpose
Implements direct low-level TTRPC interaction with containerd shim task services.

## Important APIs, Types, And Functions
Exports `Command`; defines start/delete/shutdown/state/exec subcommands plus `getTaskService`, `getTaskServiceV2`, and `getTTRPCClient`.

## Control Flow
Connection resolution tries explicit shim address, current socket scheme, and legacy abstract socket. Subcommands call task v2/v3 TTRPC methods; exec reads an OCI process spec, prepares FIFOs, sends Exec/Start, optionally attaches and resizes TTY.

## State And Persistence
Mutates live shim task/process state directly; reads process spec files and FIFO paths; does not go through containerd metadata APIs.

## Dependencies And Integration Points
Uses ttrpc, task v2/v3 APIs, typeurl/protobuf Any, console, namespaces, shim socket helpers, and runtime spec types.

## Risks And Test Signals
Bypasses higher-level client safety and can leak the TTRPC connection as noted in code. Wrong API version or socket can fail late. Integration/manual diagnostic command rather than unit-tested path. Source size reviewed: 373 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/shim/shim.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/signals.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/signals.go

## Purpose
Common signal forwarding helper used by interactive ctr task commands.

## Important APIs, Types, And Functions
Defines `killer`, `ForwardAllSignals`, and `StopCatch`.

## Control Flow
Registers for all signals, loops in a goroutine, skips ignorable signals via platform helper, logs forwarding, and calls task `Kill` for each signal until channel close.

## State And Persistence
Process-local signal subscription only; mutates target task by sending signals.

## Dependencies And Integration Points
Uses os/signal, syscall signal list, containerd log, and platform-specific `canIgnoreSignal`.

## Risks And Test Signals
Forwarding all signals is broad; platform helpers prevent forwarding signals that would break the CLI. Indirectly tested through task/run integration. Source size reviewed: 61 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/signals.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/signals_linux.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/signals_linux.go

## Purpose
Linux policy for signals that ctr should not forward to tasks.

## Important APIs, Types, And Functions
Implements `canIgnoreSignal` for Linux.

## Control Flow
Returns true for SIGURG because Go runtime uses it internally; all other signals are eligible for forwarding.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Linux build tag and syscall constants.

## Risks And Test Signals
A too-small ignore list can forward unexpected runtime/control signals; SIGURG coverage protects Go runtime behavior. Source size reviewed: 27 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/signals_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/signals_notlinux.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/signals_notlinux.go

## Purpose
Non-Linux fallback policy for signal forwarding.

## Important APIs, Types, And Functions
Implements `canIgnoreSignal` for non-Linux builds.

## Control Flow
Always returns false so no signal is filtered by the helper.

## State And Persistence
No persistence.

## Dependencies And Integration Points
`!linux` build tag.

## Risks And Test Signals
Non-Linux behavior may forward signals that should be filtered on specific platforms; coverage is integration/manual. Source size reviewed: 25 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/signals_notlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/snapshots/snapshots.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/snapshots/snapshots.go

## Purpose
Implements `ctr snapshots` lifecycle, inspection, diffing, mount command generation, tree display, labels, and unpacking.

## Important APIs, Types, And Functions
Exports `Command`; defines list/diff/usage/delete/prepare/view/mounts/commit/tree/info/label/unpack commands, `withMounts`, snapshot tree helpers, and `printMounts`.

## Control Flow
Commands open a client and selected snapshotter, then call snapshot service methods. Diff creates a lease, compares mounted snapshots or rootfs diff, optionally roots content with labels, and streams layer bytes. Prepare/view/commit create snapshot records with optional GC root labels. Mounts prints mount commands, optionally via mount manager activation. Unpack locates an image by digest and applies layers.

## State And Persistence
Mutates snapshot metadata, content store uploads, leases, labels, mounts, and unpacked rootfs state; prints JSON/table/mount shell lines to stdout.

## Dependencies And Integration Points
Containerd snapshot/content/diff/rootfs APIs, leases, mount manager, progress formatting, digest parsing, OCI descriptors, tabwriter.

## Risks And Test Signals
`printMounts` is Unix-specific despite command availability; temporary view keys are best-effort removed; diff with `--keep` roots content with GC labels. No direct tests here; behavior is integration-sensitive. Source size reviewed: 680 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/snapshots/snapshots.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/attach.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/attach.go

## Purpose
Implements `ctr tasks attach` for attaching local stdio to a running task.

## Important APIs, Types, And Functions
Defines `attachCommand`.

## Control Flow
Loads container/spec, detects terminal mode, sets local console raw for TTY, attaches with `cio.NewAttach`, waits for task exit, forwards resize or signals, deletes task on return, and exits with task status.

## State And Persistence
Attaches to live task IO and deletes the task at the end; local terminal state is temporarily changed.

## Dependencies And Integration Points
containerd client/task APIs, console, cio, signal/resize helpers, cli exit codes.

## Risks And Test Signals
`defer task.Delete` can remove task after attach exit, which is destructive; terminal reset must run on errors. Integration covered. Source size reviewed: 86 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/attach.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/checkpoint.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/checkpoint.go

## Purpose
Implements task checkpointing with CRIU/runc-specific options.

## Important APIs, Types, And Functions
Defines `checkpointCommand` and `withCheckpointOpts`.

## Control Flow
Validates container ID, opens client with selected runtime default, loads task and container info, attaches checkpoint options for exit/image/work paths, calls `task.Checkpoint`, and prints checkpoint name unless an image path was requested.

## State And Persistence
Creates checkpoint image/content or external CRIU image/work files; may stop the task with `--exit`.

## Dependencies And Integration Points
containerd checkpoint API and runc checkpoint options type.

## Risks And Test Signals
Options are documented as suitable only for runc; type assertion ignores non-runc option mismatch. Tested by contrib checkpoint scripts rather than unit tests. Source size reviewed: 104 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/checkpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/delete.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/delete.go

## Purpose
Deletes tasks or individual exec processes and reports their exit status.

## Important APIs, Types, And Functions
Defines `deleteCommand` and `loadTask`.

## Control Flow
Builds delete options from `--force`, then either loads a named exec process and deletes it or iterates containers, loads tasks, deletes them, prints exit status/PID/time, and returns the last error.

## State And Persistence
Mutates live task/process state; forced delete sends kill before removal.

## Dependencies And Integration Points
containerd client process/task deletion APIs, cio namespace for loading tasks, log output.

## Risks And Test Signals
Partial failures across multiple containers are possible; force is destructive. Integration tests usually cover task lifecycle. Source size reviewed: 113 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/exec.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/exec.go

## Purpose
Implements `ctr tasks exec` for starting an additional process inside a running container.

## Important APIs, Types, And Functions
Defines `execCommand` and `stdinCloser`.

## Control Flow
Validates args, builds process spec options for cwd/env/user/tty/args, creates a new process with IO options, starts it, either detaches or waits while forwarding resize/signals, closes stdin on read EOF, and returns process exit code.

## State And Persistence
Creates live exec process records and FIFO/log IO paths; local console may enter raw mode.

## Dependencies And Integration Points
containerd task/process API, cio, oci process spec helpers, console, signal/resize handling.

## Risks And Test Signals
Exec ID must be unique; detached processes outlive the CLI. Stdin closer behavior is subtle. Covered by integration more than unit tests. Source size reviewed: 209 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/kill.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/kill.go

## Purpose
Signals tasks or exec processes and removes CNI networking when terminating primary task paths.

## Important APIs, Types, And Functions
Defines `defaultSignal`, `RemoveCniNetworkIfExist`, and `killCommand`.

## Control Flow
Parses signal name with platform map, loads container/task, optionally removes CNI network for non-exec primary task, then sends signal either to all task processes, a named exec process, or the main task.

## State And Persistence
Mutates live process state and may tear down CNI network namespace/configuration.

## Dependencies And Integration Points
containerd task/process APIs, CNI helpers, command signal map, errdefs, log.

## Risks And Test Signals
Removing CNI before signal completion can affect still-running processes if kill fails; `--all` is broad. Test signal is integration-level. Source size reviewed: 138 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/kill.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/list.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/list.go

## Purpose
Lists containerd tasks from the task service.

## Important APIs, Types, And Functions
Defines `listCommand`.

## Control Flow
Calls `TaskService().List`, then prints either IDs only or a tabular task/PID/status view.

## State And Persistence
Read-only daemon query; stdout only.

## Dependencies And Integration Points
Task service API and tabwriter.

## Risks And Test Signals
No filters; output reflects task service state only. Simple CLI behavior with integration coverage. Source size reviewed: 72 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/metrics.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/metrics.go

## Purpose
Fetches and renders a single task metrics sample for cgroup v1, cgroup v2, or Windows stats.

## Important APIs, Types, And Functions
Defines `metricsCommand`, format constants, and table renderers for cgroup and Windows metrics.

## Control Flow
Loads container/task, calls `task.Metrics`, chooses the concrete Any payload by typeurl, unmarshals, then prints table or JSON.

## State And Persistence
Read-only metrics query; no persistence.

## Dependencies And Integration Points
containerd metrics API, typeurl, cgroups v1/v2 stats, hcsshim Windows stats, JSON/tabwriter.

## Risks And Test Signals
Unsupported metric payloads fail hard; table output only prints selected fields. No direct tests here. Source size reviewed: 204 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/pause.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/pause.go

## Purpose
Pauses a running task.

## Important APIs, Types, And Functions
Defines `pauseCommand`.

## Control Flow
Loads the named container and task, then calls `task.Pause`.

## State And Persistence
Mutates task runtime state to paused.

## Dependencies And Integration Points
containerd client task API.

## Risks And Test Signals
Runtime must support pause; no fallback. Integration tested through task lifecycle. Source size reviewed: 44 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/pause.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/ps.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/ps.go

## Purpose
Lists processes within a task.

## Important APIs, Types, And Functions
Defines `psCommand`.

## Control Flow
Loads task, calls platform `TaskPids`, and prints process IDs and info in a table.

## State And Persistence
Read-only live task query.

## Dependencies And Integration Points
containerd task API and platform-specific process enumeration.

## Risks And Test Signals
Process info shape differs by platform. Covered by platform helpers/integration. Source size reviewed: 72 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/ps.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/resume.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/resume.go

## Purpose
Resumes a paused task.

## Important APIs, Types, And Functions
Defines `resumeCommand`.

## Control Flow
Loads the named container and task, then calls `task.Resume`.

## State And Persistence
Mutates task runtime state from paused toward running.

## Dependencies And Integration Points
containerd client task API.

## Risks And Test Signals
Runtime must support resume and task must be paused. Integration covered. Source size reviewed: 44 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/resume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/start.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/start.go

## Purpose
Starts an existing created task and optionally waits attached to its exit.

## Important APIs, Types, And Functions
Defines `startCommand`.

## Control Flow
Loads container/task, starts it, prints PID, returns immediately when detached, otherwise waits, handles TTY resize or signal forwarding, and exits with task status.

## State And Persistence
Mutates live task state by starting it; may alter local terminal mode.

## Dependencies And Integration Points
containerd task API, console, cio attach conventions, signal/resize helpers.

## Risks And Test Signals
Start on already running tasks errors; terminal state handling is critical. Integration tested. Source size reviewed: 145 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks.go

## Purpose
Registers the `ctr tasks` command group and its subcommands.

## Important APIs, Types, And Functions
Exports `Command` with aliases `task`, `t` and subcommands attach/checkpoint/delete/exec/kill/list/metrics/pause/ps/resume/start.

## Control Flow
No action itself; dispatch is handled by urfave/cli to child command handlers.

## State And Persistence
No direct state changes.

## Dependencies And Integration Points
urfave/cli and sibling task command files.

## Risks And Test Signals
Registration omissions hide commands; no direct tests besides command tree generation/manpages. Source size reviewed: 47 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks_unix.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks_unix.go

## Purpose
Unix task helper implementations for console resize and process listing.

## Important APIs, Types, And Functions
Defines Unix `HandleConsoleResize` and `TaskPids` helpers.

## Control Flow
Resize registers SIGWINCH and sends current terminal size to task pty. Process listing calls task `Pids` and prints OS process IDs plus info.

## State And Persistence
Process-local signal watch; reads live task process state; sends resize RPCs.

## Dependencies And Integration Points
console, syscall, containerd task APIs, tabwriter.

## Risks And Test Signals
Resize goroutine must stop with context; process info formatting depends on runtime payloads. Indirect integration coverage. Source size reviewed: 129 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks_windows.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks_windows.go

## Purpose
Windows task helper implementations for console resize and process listing.

## Important APIs, Types, And Functions
Defines Windows `HandleConsoleResize` and `TaskPids`.

## Control Flow
Resize support is effectively a no-op/limited helper; process listing adapts Windows process info from task `Pids` for tabular output.

## State And Persistence
Read-only process query except any supported resize RPCs.

## Dependencies And Integration Points
Windows build tag, containerd task APIs, tabwriter.

## Risks And Test Signals
Feature parity differs from Unix; tests are platform/integration dependent. Source size reviewed: 88 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/version/version.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/version/version.go

## Purpose
Implements `ctr version`, reporting client and server version/revision/go runtime details.

## Important APIs, Types, And Functions
Exports `Command`.

## Control Flow
Prints client metadata from compiled version package, then connects to containerd and prints server version if reachable.

## State And Persistence
Read-only; stdout output only.

## Dependencies And Integration Points
containerd version service/client, Go runtime, tabwriter.

## Risks And Test Signals
Server connection failure returns an error after client info; useful health-check command with integration coverage. Source size reviewed: 67 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/main.go -->
# sources/cloud-native/containerd/cmd/ctr/main.go

## Purpose
Entrypoint for the `ctr` binary and command registration.

## Important APIs, Types, And Functions
Defines `pluginCmds` and `main`.

## Control Flow
Constructs the urfave/cli app from common command package metadata, registers built-in command groups plus optional plugin commands, and runs with process args.

## State And Persistence
No persistent state beyond invoking commands; exits through cli error handling.

## Dependencies And Integration Points
All `cmd/ctr/commands/...` packages, urfave/cli app setup.

## Risks And Test Signals
Command registration order and omissions affect CLI surface. Manpage generation is a secondary test signal. Source size reviewed: 36 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/gen-manpages/main.go -->
# sources/cloud-native/containerd/cmd/gen-manpages/main.go

## Purpose
Utility that generates ctr/containerd manpages from CLI command definitions.

## Important APIs, Types, And Functions
Defines `main` and `run`.

## Control Flow
Builds the CLI app/commands, creates the target directory, and writes generated man pages for selected commands.

## State And Persistence
Writes manpage files to the filesystem.

## Dependencies And Integration Points
urfave/cli manpage support and ctr command tree.

## Risks And Test Signals
Generated docs can drift if command registration changes; failures surface in docs/release workflows. Source size reviewed: 67 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/gen-manpages/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/go-buildtag/main.go -->
# sources/cloud-native/containerd/cmd/go-buildtag/main.go

## Purpose
Command-line utility for adding or checking Go build tags on source files.

## Important APIs, Types, And Functions
Defines `main` and `handle`.

## Control Flow
Parses flags for write/check/tag list, reads each file, uses build constraint parsing/editing logic, optionally rewrites files or reports needed changes.

## State And Persistence
May rewrite Go source files when write mode is enabled; otherwise read-only/check output.

## Dependencies And Integration Points
Go build constraint APIs, filesystem reads/writes, flag parsing.

## Risks And Test Signals
Incorrect tag insertion can affect build selection; should be run in CI/check mode to detect drift. Source size reviewed: 96 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/go-buildtag/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/protoc-gen-go-fieldpath/generator.go -->
# sources/cloud-native/containerd/cmd/protoc-gen-go-fieldpath/generator.go

## Purpose
Generator logic for protoc plugin that emits Go field-path helper methods for protobuf messages.

## Important APIs, Types, And Functions
Defines `generator`, `newGenerator`, `genFieldMethod`, `isMessageField`, `isLabelsField`, `isAnyField`, `collectChildlen`, and `generate`.

## Control Flow
Walks protobuf messages, discovers child message fields, labels maps, and Any fields, then emits methods that join field paths and optionally unmarshal Any values for nested path resolution.

## State And Persistence
Writes generated Go code through `protogen.GeneratedFile`; no runtime persistence.

## Dependencies And Integration Points
protogen, protobuf descriptors, fieldpath helpers, fmt/string formatting imports.

## Risks And Test Signals
The function name `collectChildlen` is misspelled but internal. Generator correctness depends on descriptor shape; tested through generated-code compilation. Source size reviewed: 201 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/protoc-gen-go-fieldpath/generator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/protoc-gen-go-fieldpath/main.go -->
# sources/cloud-native/containerd/cmd/protoc-gen-go-fieldpath/main.go

## Purpose
Entrypoint for the fieldpath protoc plugin.

## Important APIs, Types, And Functions
Defines `main`.

## Control Flow
Configures `protogen.Options` and runs generation for each requested file, delegating to `generate`.

## State And Persistence
Writes generated output through protoc plugin protocol.

## Dependencies And Integration Points
google.golang.org/protobuf/compiler/protogen.

## Risks And Test Signals
Failures affect code generation pipeline; test signal is protoc invocation/compile of generated files. Source size reviewed: 37 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/protoc-gen-go-fieldpath/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/codecov.yml -->
# sources/cloud-native/containerd/codecov.yml

## Purpose
Disables Codecov pull-request comments.

## Important APIs, Types, And Functions
Single YAML key `comment: false`.

## Control Flow
Codecov reads this repository config during coverage processing.

## State And Persistence
No runtime state; affects external coverage service behavior.

## Dependencies And Integration Points
Codecov configuration schema.

## Risks And Test Signals
Minimal; loss of PR coverage comments may hide coverage feedback elsewhere. Validation is Codecov-side. Source size reviewed: 1 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/containerd.service -->
# sources/cloud-native/containerd/containerd.service

## Purpose
Systemd unit for running containerd as a Linux service.

## Important APIs, Types, And Functions
Defines Unit, Service, and Install sections with `ExecStart=/usr/local/bin/containerd`.

## Control Flow
Starts after network/local filesystems, delegates cgroups, adjusts OOM score and limits, preloads overlay module, and restarts according to systemd policy.

## State And Persistence
Systemd manages process lifecycle, logs, cgroups, and enabled target symlink state.

## Dependencies And Integration Points
systemd, modprobe overlay, `/usr/local/bin/containerd`.

## Risks And Test Signals
Hard-coded binary path must match installation; high resource limits and Delegate are required for containers. Tested by packaging/system integration. Source size reviewed: 41 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/containerd.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/cri-in-userns/docker-entrypoint.sh -->
# sources/cloud-native/containerd/contrib/Dockerfile.test.d/cri-in-userns/docker-entrypoint.sh

## Purpose
Entrypoint for CRI tests running containerd inside a user namespace test image.

## Important APIs, Types, And Functions
Shell script with setup steps for containerd, rootless/userns environment, and test command execution.

## Control Flow
Validates environment, prepares directories/config, starts required services/daemons, then executes the provided test workflow.

## State And Persistence
Mutates container filesystem paths, daemon sockets, runtime directories, and process tree inside the test container.

## Dependencies And Integration Points
bash, containerd, CRI tooling, user namespace support, mounted cgroup/runtime directories.

## Risks And Test Signals
Requires privileged/userns-capable environment; cleanup depends on container lifecycle. Test signal is the CRI-in-userns job. Source size reviewed: 63 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/cri-in-userns/docker-entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/cri-in-userns/etc_containerd_config.toml -->
# sources/cloud-native/containerd/contrib/Dockerfile.test.d/cri-in-userns/etc_containerd_config.toml

## Purpose
Containerd config fixture for CRI-in-userns test container.

## Important APIs, Types, And Functions
TOML config enabling containerd/CRI settings for that environment.

## Control Flow
Read by containerd on startup from the entrypoint.

## State And Persistence
Controls daemon runtime behavior; no execution by itself.

## Dependencies And Integration Points
containerd config schema and CRI plugin.

## Risks And Test Signals
Schema drift can break tests; validated only when the test container starts. Source size reviewed: 10 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/cri-in-userns/etc_containerd_config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/critest.sh -->
# sources/cloud-native/containerd/contrib/Dockerfile.test.d/critest.sh

## Purpose
Runs CRI conformance tests inside Dockerfile.test environment under a generated systemd service.

## Important APIs, Types, And Functions
Shell functions `echo_exit_code` and `start` plus embedded service unit content.

## Control Flow
Writes/enables a service for docker-entrypoint, starts it, tails or reports logs, and exits with captured status.

## State And Persistence
Creates systemd unit files and test logs inside the image/container.

## Dependencies And Integration Points
bash, systemd, crictl/critest environment, docker-entrypoint script.

## Risks And Test Signals
Assumes systemd is available in the test container. Failures require log inspection. Source size reviewed: 47 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/critest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/docker-entrypoint.sh -->
# sources/cloud-native/containerd/contrib/Dockerfile.test.d/docker-entrypoint.sh

## Purpose
Default CRI test image entrypoint that launches containerd test prerequisites.

## Important APIs, Types, And Functions
Shell setup script.

## Control Flow
Sets strict bash options, prepares cgroup/runtime directories and daemon startup, then hands off to requested command/test.

## State And Persistence
Mutates container runtime directories and starts processes inside test image.

## Dependencies And Integration Points
bash, containerd, CRI tools, Linux cgroups.

## Risks And Test Signals
Environment-specific; missing privileges or cgroups cause early failures. Validated by Dockerfile.test jobs. Source size reviewed: 28 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/docker-entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/cri-containerd.yaml -->
# sources/cloud-native/containerd/contrib/ansible/cri-containerd.yaml

## Purpose
Top-level Ansible playbook for provisioning a host with containerd CRI and Kubernetes dependencies.

## Important APIs, Types, And Functions
Ansible play referencing vars and task files.

## Control Flow
Loads shared variables, runs bootstrap, binary install, and Kubernetes task includes according to target distribution.

## State And Persistence
Mutates remote hosts: packages, directories, binaries, repos, and services.

## Dependencies And Integration Points
Ansible, distro package managers, Kubernetes repositories, containerd release artifacts.

## Risks And Test Signals
Versions are pinned/old in vars; playbook is contrib and may drift from current install guidance. Validated by manual/provisioning runs. Source size reviewed: 66 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/cri-containerd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/binaries.yaml -->
# sources/cloud-native/containerd/contrib/ansible/tasks/binaries.yaml

## Purpose
Ansible tasks for downloading containerd and preparing CNI directories.

## Important APIs, Types, And Functions
Tasks using `unarchive`/file modules and shared vars.

## Control Flow
Fetches the containerd release tarball into root, creates CNI binary and config directories.

## State And Persistence
Writes binaries/directories on remote hosts.

## Dependencies And Integration Points
Ansible modules, GitHub release URL, vars `containerd_release_version`, `cni_*_dir`.

## Risks And Test Signals
Network/version drift and root permissions. Tested by running playbook. Source size reviewed: 12 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/binaries.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/bootstrap_centos.yaml -->
# sources/cloud-native/containerd/contrib/ansible/tasks/bootstrap_centos.yaml

## Purpose
CentOS bootstrap package installation for CRI/containerd test hosts.

## Important APIs, Types, And Functions
Ansible package task list.

## Control Flow
Installs required packages via yum/dnf.

## State And Persistence
Mutates system package set.

## Dependencies And Integration Points
CentOS package manager and repositories.

## Risks And Test Signals
Package names/repos can drift. Manual provisioning coverage. Source size reviewed: 12 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/bootstrap_centos.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/bootstrap_ubuntu.yaml -->
# sources/cloud-native/containerd/contrib/ansible/tasks/bootstrap_ubuntu.yaml

## Purpose
Ubuntu bootstrap package installation for CRI/containerd test hosts.

## Important APIs, Types, And Functions
Ansible apt task list.

## Control Flow
Installs required base packages using apt.

## State And Persistence
Mutates system package set.

## Dependencies And Integration Points
Ubuntu apt repositories.

## Risks And Test Signals
Package availability changes across releases. Manual provisioning coverage. Source size reviewed: 12 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/bootstrap_ubuntu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/k8s.yaml -->
# sources/cloud-native/containerd/contrib/ansible/tasks/k8s.yaml

## Purpose
Ansible tasks for configuring Kubernetes repositories and installing kubelet/kubeadm/kubectl.

## Important APIs, Types, And Functions
Tasks for apt/yum repo keys, SELinux handling, and Kubernetes package installation.

## Control Flow
Branches on distro family: Ubuntu adds gpg key/source and apt update; CentOS adds yum repo, disables SELinux, and installs Kubernetes packages.

## State And Persistence
Writes repo files/keys, changes SELinux config, installs packages.

## Dependencies And Integration Points
Kubernetes package repos, distro package managers, Ansible facts.

## Risks And Test Signals
Repository key URLs and package names are time-sensitive; disabling SELinux is broad. Manual/provisioning test signal. Source size reviewed: 52 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/k8s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/vars/vars.yaml -->
# sources/cloud-native/containerd/contrib/ansible/vars/vars.yaml

## Purpose
Shared Ansible variables for containerd release and CNI directories.

## Important APIs, Types, And Functions
Defines `containerd_release_version`, `cni_bin_dir`, and `cni_conf_dir`.

## Control Flow
Consumed by playbook/task includes during provisioning.

## State And Persistence
No execution; controls remote filesystem paths and download version.

## Dependencies And Integration Points
Ansible variable resolution.

## Risks And Test Signals
Pinned version `1.5.5` may be stale for modern containerd tests. Source size reviewed: 4 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/vars/vars.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor.go -->
# sources/cloud-native/containerd/contrib/apparmor/apparmor.go

## Purpose
Linux AppArmor OCI spec integration for applying existing or generated default profiles.

## Important APIs, Types, And Functions
Provides `WithProfile` and `WithDefaultProfile` spec opts on supported builds.

## Control Flow
Spec opts ensure Linux config exists, optionally generate/load default profile, and set `s.Process.ApparmorProfile`.

## State And Persistence
May load AppArmor policy into kernel via parser and reads/writes profile data through template helpers.

## Dependencies And Integration Points
OCI spec opts, AppArmor parser/template helpers, Linux/AppArmor availability.

## Risks And Test Signals
Requires AppArmor and parser on host; profile load failures affect container creation. Tests/fuzzer cover default profile generation. Source size reviewed: 95 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor_fuzzer_test.go -->
# sources/cloud-native/containerd/contrib/apparmor/apparmor_fuzzer_test.go

## Purpose
Fuzzes AppArmor default profile loading/generation paths.

## Important APIs, Types, And Functions
Defines `FuzzLoadDefaultProfile`.

## Control Flow
Feeds fuzzed profile names through profile-loading logic to catch panics and malformed handling.

## State And Persistence
May interact with temp/generated profile data depending on helper behavior; test-scoped.

## Dependencies And Integration Points
Go fuzzing and AppArmor helper functions.

## Risks And Test Signals
Environment sensitivity if parser/AppArmor unavailable; useful panic regression signal. Source size reviewed: 40 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor_fuzzer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor_test.go -->
# sources/cloud-native/containerd/contrib/apparmor/apparmor_test.go

## Purpose
Unit test coverage for dumping/loading default AppArmor profile content.

## Important APIs, Types, And Functions
Defines `TestDumpDefaultProfile`.

## Control Flow
Exercises template generation and validates non-empty/default behavior.

## State And Persistence
Test-scoped output only.

## Dependencies And Integration Points
Go testing and local template helpers.

## Risks And Test Signals
Does not prove kernel-level profile load; covers template generation path. Source size reviewed: 36 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor_unsupported.go -->
# sources/cloud-native/containerd/contrib/apparmor/apparmor_unsupported.go

## Purpose
Unsupported-platform stubs for AppArmor OCI spec options.

## Important APIs, Types, And Functions
Defines `WithProfile` and `WithDefaultProfile` returning no-op/error behavior for unsupported builds.

## Control Flow
Build-tag selected when AppArmor support is unavailable; functions prevent Linux-specific implementation from compiling into other targets.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Build tags and OCI spec option type.

## Risks And Test Signals
Callers may assume profile enforcement that is unavailable on the platform; compile-time selection is the guard. Source size reviewed: 43 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/template.go -->
# sources/cloud-native/containerd/contrib/apparmor/template.go

## Purpose
Generates, loads, and checks containerd AppArmor profile templates.

## Important APIs, Types, And Functions
Defines `defaultTemplate`, `data`, `cleanProfileName`, `loadData`, `generate`, `load`, `macroExists`, `aaParser`, and `isLoaded`.

## Control Flow
Builds template data from profile name and AppArmor macro availability, renders a profile, invokes apparmor parser for loading, and checks loaded profiles.

## State And Persistence
Reads `/etc/apparmor.d`, invokes system parser, and affects kernel AppArmor profile state.

## Dependencies And Integration Points
text/template, os/exec, AppArmor filesystem/proc interfaces.

## Risks And Test Signals
Shelling out to parser and host-specific macros make behavior environment-dependent. Tests cover name cleaning/template basics. Source size reviewed: 205 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/template.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/template_test.go -->
# sources/cloud-native/containerd/contrib/apparmor/template_test.go

## Purpose
Tests AppArmor profile-name sanitization.

## Important APIs, Types, And Functions
Defines `TestCleanProfileName`.

## Control Flow
Checks replacement/cleaning cases for profile names.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Go testing and `cleanProfileName`.

## Risks And Test Signals
Narrow but useful guard against unsafe profile names. Source size reviewed: 18 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/template_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/autocomplete/ctr -->
# sources/cloud-native/containerd/contrib/autocomplete/ctr

## Purpose
Bash completion shim for the `ctr` CLI.

## Important APIs, Types, And Functions
Defines `_cli_bash_autocomplete` and registers it with `complete`.

## Control Flow
When completing, invokes the current ctr command prefix with `--generate-bash-completion`, then feeds options into `compgen`.

## State And Persistence
Shell-session only; no files written.

## Dependencies And Integration Points
bash completion, ctr binary support for urfave/cli completion.

## Risks And Test Signals
Executes partially typed command words; quoting/word-splitting is simple. Manual shell test signal. Source size reviewed: 22 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/autocomplete/ctr -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/aws/snapshotter_bench_cf.yml -->
# sources/cloud-native/containerd/contrib/aws/snapshotter_bench_cf.yml

## Purpose
CloudFormation template for launching an EC2 host with EBS volumes for snapshotter benchmarking.

## Important APIs, Types, And Functions
Defines parameters for key, AMI, security groups, instance type, volume IOPS/size/type, and resources for EC2 plus block devices.

## Control Flow
CloudFormation provisions an EBS-optimized instance with root and multiple benchmark volumes, including a device-mapper thin-pool-oriented volume.

## State And Persistence
Creates AWS EC2/EBS infrastructure and associated costs until deleted.

## Dependencies And Integration Points
AWS CloudFormation/EC2/EBS, Amazon Linux 2 AMI assumption, SSH security groups.

## Risks And Test Signals
Default AMI and instance type may be obsolete; running template incurs spend. Validation is stack creation/manual benchmark run. Source size reviewed: 144 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/aws/snapshotter_bench_cf.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/checkcriu.go -->
# sources/cloud-native/containerd/contrib/checkpoint/checkcriu.go

## Purpose
Small prerequisite checker for CRIU availability used by checkpoint restore scripts.

## Important APIs, Types, And Functions
Defines `main`.

## Control Flow
Attempts to execute/query CRIU support and exits non-zero on failure.

## State And Persistence
No persistence beyond process exit status.

## Dependencies And Integration Points
CRIU installed in PATH and host kernel support.

## Risks And Test Signals
Only checks availability, not full checkpoint success. Used by shell integration scripts. Source size reviewed: 32 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/checkcriu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/checkpoint-restore-cri-test.sh -->
# sources/cloud-native/containerd/contrib/checkpoint/checkpoint-restore-cri-test.sh

## Purpose
End-to-end CRI checkpoint/restore test using crictl and containerd.

## Important APIs, Types, And Functions
Shell functions `cleanup`, `test_from_archive`, and `test_from_oci`.

## Control Flow
Builds `checkcriu`, validates tools, starts isolated containerd socket, creates pod/container fixtures, mutates rootfs, checkpoints, restores from archive and OCI image paths, verifies logs/files, and reports PASS/FAIL.

## State And Persistence
Creates temp directories, containerd sockets/logs, CRI pods/containers, checkpoint archives/images, and may kill containerd during cleanup.

## Dependencies And Integration Points
bash, go, CRIU, crictl, jq, ctr/containerd, testdata JSON, ghcr.io image.

## Risks And Test Signals
Requires root and host checkpoint support; cleanup is destructive to test containerd processes. Strong integration test signal. Source size reviewed: 229 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/checkpoint-restore-cri-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/checkpoint-restore-kubernetes-test.sh -->
# sources/cloud-native/containerd/contrib/checkpoint/checkpoint-restore-kubernetes-test.sh

## Purpose
End-to-end Kubernetes checkpoint/restore test using kubectl, crictl, ctr, and local checkpoint image.

## Important APIs, Types, And Functions
Shell `cleanup` plus linear test workflow.

## Control Flow
Validates CRIU/tools, applies a sleeper pod, observes counter output, checkpoints/restores through Kubernetes/containerd paths, imports/restores image, and validates continued behavior.

## State And Persistence
Mutates Kubernetes cluster pods, local images, temp files, and checkpoint artifacts.

## Dependencies And Integration Points
kubectl, crictl, ctr, CRIU, Kubernetes admin kubeconfig, testdata pod YAML.

## Risks And Test Signals
Requires a live cluster and root/runtime privileges; can delete pod `sleeper`. Strong but environment-heavy test signal. Source size reviewed: 231 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/checkpoint-restore-kubernetes-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/container_sleep.json -->
# sources/cloud-native/containerd/contrib/checkpoint/testdata/container_sleep.json

## Purpose
CRI container config fixture for checkpoint/restore tests.

## Important APIs, Types, And Functions
JSON describing container metadata, image, command loop, env, annotations, log path, TTY/stdin flags, and Linux resources/security.

## Control Flow
Consumed by `crictl create` in checkpoint scripts.

## State And Persistence
No execution by itself; controls created CRI container behavior.

## Dependencies And Integration Points
CRI runtime config schema and `ghcr.io/containerd/alpine` image.

## Risks And Test Signals
Image availability and resource/security fields affect portability. Validated by checkpoint scripts. Source size reviewed: 49 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/container_sleep.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/sandbox_config.json -->
# sources/cloud-native/containerd/contrib/checkpoint/testdata/sandbox_config.json

## Purpose
CRI pod sandbox config fixture for checkpoint/restore tests.

## Important APIs, Types, And Functions
JSON metadata, DNS, resources, labels, annotations, and Linux namespace/SELinux settings.

## Control Flow
Patched with a log directory by scripts then passed to `crictl runp`.

## State And Persistence
Controls test sandbox creation; no standalone persistence.

## Dependencies And Integration Points
CRI sandbox config schema.

## Risks And Test Signals
SELinux/namespace settings may be host-specific; integration scripts validate. Source size reviewed: 50 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/sandbox_config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/sleep-restore.yaml -->
# sources/cloud-native/containerd/contrib/checkpoint/testdata/sleep-restore.yaml

## Purpose
Kubernetes pod manifest for restoring from a local checkpoint image.

## Important APIs, Types, And Functions
Pod `sleeper` with container image `localhost/checkpoint-image:latest` and `IfNotPresent` pull policy.

## Control Flow
Applied by Kubernetes checkpoint restore script after local image import/tagging.

## State And Persistence
Creates/updates a Kubernetes pod when applied.

## Dependencies And Integration Points
Kubernetes API and local image availability.

## Risks And Test Signals
Name collides with test pod; assumes image is present on node. Validated by script. Source size reviewed: 10 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/sleep-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/sleep.yaml -->
# sources/cloud-native/containerd/contrib/checkpoint/testdata/sleep.yaml

## Purpose
Kubernetes source pod manifest used before checkpointing.

## Important APIs, Types, And Functions
Pod `sleeper` running `quay.io/adrianreber/counter:latest`.

## Control Flow
Applied by the Kubernetes checkpoint script to create a counter workload.

## State And Persistence
Creates a Kubernetes pod when applied.

## Dependencies And Integration Points
Kubernetes API and external image registry.

## Risks And Test Signals
External image availability can break tests; script validates readiness/output. Source size reviewed: 8 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/sleep.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/diffservice/service.go -->
# sources/cloud-native/containerd/contrib/diffservice/service.go

## Purpose
Adapter that exposes containerd diff Applier/Comparer implementations as a gRPC Diff service.

## Important APIs, Types, And Functions
Defines `service`, `FromApplierAndComparer`, `Apply`, and `Diff`.

## Control Flow
Apply forwards request descriptors/mounts/options to the applier and returns applied digest. Diff forwards mount sets and media/ref/label options to comparer and returns descriptor.

## State And Persistence
May mutate content store/snapshots through underlying applier/comparer; service itself stores only interfaces.

## Dependencies And Integration Points
containerd diff interfaces, diff service protobuf API, OCI descriptors, mount types.

## Risks And Test Signals
Trusts underlying implementations for validation and persistence; thin adapter has little direct test coverage. Source size reviewed: 111 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/diffservice/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/archive_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/archive_fuzz_test.go

## Purpose
Fuzzes archive apply/import index paths using synthetic tar streams.

## Important APIs, Types, And Functions
Defines `FuzzApply` and `FuzzImportIndex`.

## Control Flow
Consumes fuzz data to build tar entries/blobs and invokes archive apply/import index logic, checking for panics and path issues.

## State And Persistence
Uses test temp directories/content only.

## Dependencies And Integration Points
go-fuzz-headers, archive/tar helpers, containerd archive import code.

## Risks And Test Signals
Generated tar structures may be invalid by design; useful for robustness, not semantic correctness. Source size reviewed: 138 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/archive_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins.go -->
# sources/cloud-native/containerd/contrib/fuzz/builtins.go

## Purpose
Shared fuzz build hooks/registrations for non-platform-specific fuzz targets.

## Important APIs, Types, And Functions
Package-level initialization/import glue for fuzz builds.

## Control Flow
Compiled into fuzz package to ensure required built-in plugins or dependencies are linked.

## State And Persistence
No runtime persistence.

## Dependencies And Integration Points
Containerd plugin/import side effects.

## Risks And Test Signals
Missing imports can make fuzz harnesses fail to initialize realistic services. Source size reviewed: 52 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins_linux.go -->
# sources/cloud-native/containerd/contrib/fuzz/builtins_linux.go

## Purpose
Linux-specific fuzz build imports/registrations.

## Important APIs, Types, And Functions
Build-tag selected package glue.

## Control Flow
Links Linux-only snapshotter/runtime/plugin pieces needed by fuzz targets.

## State And Persistence
No direct persistence.

## Dependencies And Integration Points
Linux build tags and containerd builtins.

## Risks And Test Signals
Fuzz coverage differs by platform; compile failures expose stale imports. Source size reviewed: 27 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins_unix.go -->
# sources/cloud-native/containerd/contrib/fuzz/builtins_unix.go

## Purpose
Unix-specific fuzz build imports/registrations shared by non-Windows platforms.

## Important APIs, Types, And Functions
Build-tag selected package glue.

## Control Flow
Links Unix-only components into fuzz binaries.

## State And Persistence
No direct persistence.

## Dependencies And Integration Points
Unix build constraints and containerd plugin side effects.

## Risks And Test Signals
Platform-specific initialization can drift; build is the main signal. Source size reviewed: 25 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins_windows.go -->
# sources/cloud-native/containerd/contrib/fuzz/builtins_windows.go

## Purpose
Windows-specific fuzz build imports/registrations.

## Important APIs, Types, And Functions
Build-tag selected package glue.

## Control Flow
Links Windows-only components for fuzz binaries.

## State And Persistence
No direct persistence.

## Dependencies And Integration Points
Windows build tags and hcsshim/containerd builtins.

## Risks And Test Signals
Coverage differs from Unix; compile/build signal only. Source size reviewed: 25 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/containerd_import_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/containerd_import_fuzz_test.go

## Purpose
Fuzzes containerd image import command paths.

## Important APIs, Types, And Functions
Defines `fuzzContext` and `FuzzContainerdImport`.

## Control Flow
Creates a namespace context, consumes fuzz bytes as import input/options, and invokes import logic against test stores.

## State And Persistence
Test-scoped temp content/metadata state.

## Dependencies And Integration Points
containerd import code, fuzz headers, namespace helpers.

## Risks And Test Signals
Focuses crash resistance; malformed archives are expected. Fuzz build/test signal. Source size reviewed: 65 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/containerd_import_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/content_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/content_fuzz_test.go

## Purpose
Fuzzes content store walking and archive export with generated blob stores.

## Important APIs, Types, And Functions
Defines blob validation/population helpers plus `FuzzCSWalk` and `FuzzArchiveExport`.

## Control Flow
Generates digest-to-bytes maps, writes blobs to local content store, verifies paths, walks content, and attempts archive export.

## State And Persistence
Uses temp local content stores and blobs.

## Dependencies And Integration Points
containerd content/local store, digest validation, archive export.

## Risks And Test Signals
Digest/path checks defend against malformed content paths; semantic image validity is limited. Fuzzing provides crash/regression signal. Source size reviewed: 163 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/content_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/cri_server_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/cri_server_fuzz_test.go

## Purpose
Fuzzes CRI runtime and image service API sequences against a local containerd daemon.

## Important APIs, Types, And Functions
Defines `FuzzCRIServer`, fake runtime service, service registration, execution logging, dispatcher `fuzzCRI`, and per-CRI-method fuzz wrappers.

## Control Flow
Requires root, starts daemon once, constructs CRI image/runtime services, chooses up to 40 random operations, generates request structs, invokes methods, and logs execution order on panic.

## State And Persistence
Mutates the fuzz daemon, image store, pods/containers/sandboxes depending on generated calls.

## Dependencies And Integration Points
containerd client/CRI server, Kubernetes CRI API, grpc instrumentation, go-fuzz-headers, daemon helper.

## Risks And Test Signals
Root/environment-heavy and broad stateful fuzzing; errors are mostly ignored to find panics. Strong crash signal but not deterministic semantics. Source size reviewed: 470 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/cri_server_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/daemon.go -->
# sources/cloud-native/containerd/contrib/fuzz/daemon.go

## Purpose
Shared helper for starting a containerd daemon for fuzz targets.

## Important APIs, Types, And Functions
Defines default address/root/state constants, `initDaemon`, and `startDaemon`.

## Control Flow
Creates temp-like runtime paths, launches containerd with configured address/root/state, and waits for readiness for fuzz clients.

## State And Persistence
Starts a background daemon and creates root/state directories under configured paths.

## Dependencies And Integration Points
containerd binary availability, os/exec, sync.Once, defaults.

## Risks And Test Signals
Can leave daemon/process state if fuzz process is interrupted; required by CRI/import fuzzers. Source size reviewed: 93 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/diff_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/diff_fuzz_test.go

## Purpose
Fuzzes diff apply and compare operations.

## Important APIs, Types, And Functions
Defines `FuzzDiffApply` and `FuzzDiffCompare`.

## Control Flow
Builds fuzzed mount/content/archive inputs and invokes diff service paths looking for crashes.

## State And Persistence
Uses temp directories/content stores; may create snapshot-like filesystem trees during tests.

## Dependencies And Integration Points
containerd diff/archive/mount helpers and fuzz headers.

## Risks And Test Signals
Requires OS filesystem behavior; malformed inputs are expected. Fuzz signal is panic resistance. Source size reviewed: 104 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/diff_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/exchange_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/exchange_fuzz_test.go

## Purpose
Fuzzes content exchange/transfer behavior.

## Important APIs, Types, And Functions
Defines `FuzzExchange`.

## Control Flow
Generates descriptors/content data and drives exchange logic to catch malformed graph or descriptor handling issues.

## State And Persistence
Test-scoped content state only.

## Dependencies And Integration Points
containerd transfer/exchange packages and fuzz headers.

## Risks And Test Signals
Limited semantic assertions; useful for crash/pathological input discovery. Source size reviewed: 57 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/exchange_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/images_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/images_fuzz_test.go

## Purpose
Fuzzes image validation/check logic.

## Important APIs, Types, And Functions
Defines `FuzzImagesCheck`.

## Control Flow
Generates image/descriptor-like structures and calls image check routines.

## State And Persistence
No persistent state beyond test-scoped objects.

## Dependencies And Integration Points
containerd image package and fuzz headers.

## Risks And Test Signals
Crash-resistance focus; does not prove images are runnable. Source size reviewed: 45 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/images_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/metadata_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/metadata_fuzz_test.go

## Purpose
Stateful fuzz coverage for metadata image store, lease manager, container store, and content store.

## Important APIs, Types, And Functions
Defines `testEnv`, `FuzzImageStore`, `FuzzLeaseManager`, `FuzzContainerStore`, `testOptions`, `testDB`, and `FuzzContentStore`.

## Control Flow
Each fuzz target creates temporary bbolt/metadata stores, chooses up to 50 operations from a set, generates structs/strings/resources, and invokes create/list/update/delete/commit APIs while ignoring normal errors.

## State And Persistence
Creates temporary bbolt databases, native snapshotters, local content stores, leases, images, containers, and content writes.

## Dependencies And Integration Points
bbolt, containerd metadata DB/stores, native snapshotter, local content store, namespaces, go-fuzz-headers.

## Risks And Test Signals
Stateful operation ordering catches panics but ignores most semantic errors. Good regression signal for metadata invariants under malformed input. Source size reviewed: 433 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/metadata_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/oss_fuzz_build.sh -->
# sources/cloud-native/containerd/contrib/fuzz/oss_fuzz_build.sh

## Purpose
OSS-Fuzz build script for compiling containerd native and libFuzzer Go fuzz targets.

## Important APIs, Types, And Functions
Defines `compile_fuzzers` shell function and build steps.

## Control Flow
Installs Go/protoc/runc dependencies, patches paths for `/tmp/containerd`, removes vendor, compiles fuzz functions discovered by git grep with native or go-fuzz builders, and sets CGO/architecture.

## State And Persistence
Mutates OSS-Fuzz build workspace, downloads toolchains, edits source files with sed, compiles binaries.

## Dependencies And Integration Points
OSS-Fuzz env vars/tools, wget, git, Go, protoc, runc build, compile_go_fuzzer helpers.

## Risks And Test Signals
Downloads pinned tool versions; source patching is build-context-specific. Validated by OSS-Fuzz build. Source size reviewed: 101 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/oss_fuzz_build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/gce/cloud-init/master.yaml -->
# sources/cloud-native/containerd/contrib/gce/cloud-init/master.yaml

## Purpose
GCE cloud-init config for bootstrapping a Kubernetes/containerd master node.

## Important APIs, Types, And Functions
Cloud-init users, write_files for systemd units/config scripts, and runcmd startup commands.

## Control Flow
Creates service units for containerd installation/runtime/target and Kubernetes master installation, downloads metadata-provided configure scripts, enables targets, and runs bootstrapping commands.

## State And Persistence
Writes systemd units, users, scripts, services, and starts installation on a VM.

## Dependencies And Integration Points
GCE metadata server, systemd, curl, Kubernetes/containerd install artifacts.

## Risks And Test Signals
Metadata script URLs and legacy Kubernetes assumptions can drift; running it mutates a VM heavily. Validation is cloud-init boot success. Source size reviewed: 200 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/gce/cloud-init/master.yaml -->
