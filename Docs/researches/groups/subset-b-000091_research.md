# Research: subset-b-000091

This grouped report covers CRI-O OCI runtime/container lifecycle code and OCI artifact stores. Each source file section is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container.go -->
# sources/cloud-native/cri-o/internal/oci/container.go

## Purpose
Defines CRI-O's in-memory container model, persisted container state, CRI projection helpers, PID identity verification, stop coordination, exec PID tracking, runtime-user/resource snapshots, checkpoint metadata, and monitor-process recovery. It is the shared state object consumed by OCI, conmon-rs pod, and VM runtime implementations.

## Important APIs, Types, and Functions
`Container` stores CRI metadata, paths (`bundlePath`, `dir`, log path), runtime handler, OCI spec, volumes, Linux resources, PID namespace handle, checkpoint/restore fields, and locks. `ContainerState` embeds `specs.State` and adds created/started/finished timestamps, exit/OOM/seccomp status, immutable init PID/start-time identity, checkpoint time, and `ContainerMonitorProcess`. `NewContainer`, `NewSpoofedContainer`, `CRIContainer`, `CRIAttributes`, `SetSpec`, `Spec`, accessors, `FromDisk`, `ContainerState.SetInitPid`, `Living`, `Pid`, `ProcessState`, `verifyPid`, `SetAsStopping`, `WaitOnStopTimeout`, `SetAsDoneStopping`, `StartExecCmd`, `DeleteExecPID`, `KillExecPIDs`, and `SetMonitorProcess` are the key APIs.

## Control Flow and State
Creation seeds CRI protobuf metadata and an empty state. `SetSpec` stores the OCI spec and derives CRI resources and runtime user. `FromDisk` decodes `state.json`, upgrading old state that only had `Pid` by recording `InitPid` and `InitStartTime`. PID use flows through `pid()`: state must exist, `InitPid` and runtime `Pid` must be valid, `kill(pid, 0)` must succeed, process start time must match saved start time, and zombie/dead states are treated as not found. Stop flow is coordinated by `stopLock`, a timeout channel, watcher channels, and a `stopKillLoopBegun` barrier that prevents new exec processes once SIGKILL looping starts.

## Persistence and Dependencies
Persistent state is `dir/state.json`; exit state is `dir/exit`; checkpoints live under `dir/checkpoint`. PID identity depends on OS-specific `getPidStartTime`/`getPidStatData`. The file integrates Kubernetes CRI protobufs, OCI runtime-spec, CRI-O storage image IDs and image references, namespace manager cleanup, checkpointctl metadata, goccy JSON, Podman signal parsing, and cgroups/runtime helpers through platform files.

## Integration Points
All runtime implementations mutate `ContainerState` under `opLock`. Server/image layers read CRI projections and resources. Runtime code reads `RuntimePathForPlatform`, log/bundle paths, exec cgroup paths, monitor process fields, stop signal, checkpoint paths, volumes, and PID identity helpers.

## Risks and Test Signals
High-risk areas are lock ordering, stop timeout channel closure, PID reuse/wrap protection, PID 0 exec registration, stale conmon PID reuse, and returning internal maps/pointers without deep copies. `container_test.go` covers accessors, resource projection, state reload upgrade, PID liveness and start-time mismatch, stop watcher races, exec PID tracking, and spoofed container behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container_freebsd.go -->
# sources/cloud-native/cri-o/internal/oci/container_freebsd.go

## Purpose
Provides FreeBSD+cgo process start-time lookup for container PID identity checks. This keeps `Container.verifyPid` useful on FreeBSD without requiring `/proc`.

## Important APIs, Control Flow, and Dependencies
`getPidStartTime` delegates to `getPidStatDataFromSysctl`; `getPidStatData` returns only start time and an empty process state. `getPidStatDataFromSysctl` calls `unix.SysctlRaw("kern.proc.pid", pid)`, checks the returned byte length against `C.sizeof_struct_kinfo_proc`, casts to `struct kinfo_proc`, and formats `ki_start` seconds/microseconds. `SetRuntimeUser` is a no-op on this platform.

## State, Integration, Risks, and Tests
This file feeds `ContainerState.InitStartTime` and PID-wrap protection. It does not report process state, so zombie/defunct filtering in `container.go` cannot work on this path. The cgo unsafe cast and FreeBSD kernel structure size are the main portability risks; no dedicated FreeBSD test appears in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container_freebsd_nocgo.go -->
# sources/cloud-native/cri-o/internal/oci/container_freebsd_nocgo.go

## Purpose
Provides the FreeBSD non-cgo fallback for process start-time lookup using procfs.

## Important APIs, Control Flow, and Dependencies
`getPidStartTime` formats `/proc/<pid>/status` and delegates to `getPidStatDataFromFile`. That parser reads the file, splits by whitespace, and returns field index 7 as the start time. `getPidStatData` returns an empty process state plus start time. `SetRuntimeUser` is a no-op.

## State, Integration, Risks, and Tests
The code supports PID identity tracking for `ContainerState.InitStartTime`, but requires FreeBSD procfs to be mounted and does not bounds-check the split before indexing. Missing process-state support limits zombie detection. Tests in this subset exercise Linux parsing only, not this FreeBSD fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container_freebsd_nocgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container_linux.go -->
# sources/cloud-native/cri-o/internal/oci/container_linux.go

## Purpose
Implements Linux-specific container helpers: conmon cgroup cleanup, seccomp profile path storage, `/proc/<pid>/stat` PID identity parsing, and CRI runtime-user projection from the OCI process spec.

## Important APIs and Control Flow
`CleanupConmonCgroup` loads and deletes the recorded conmon cgroupfs path unless the container is spoofed or no path was recorded. `SetSeccompProfilePath`/`SeccompProfilePath` store seccomp path metadata. `GetPidStartTimeFromFile`, `getPidStartTime`, `getPidStatData`, and `getPidStatDataFromFile` parse `/proc/<pid>/stat` by finding the last `)` to safely skip command names containing spaces, then reading state and start-time fields. `SetRuntimeUser` converts OCI UID/GID/additional groups into CRI `ContainerUser`.

## Dependencies, Integration, Risks, and Tests
Depends on Podman cgroups, OCI spec, CRI types, and CRI-O logging. It is directly used by `Container.SetSpec`, `ContainerState.SetInitPid`, `Container.verifyPid`, and cgroup cleanup paths. Risks include proc stat format assumptions and 4 KiB read limit. Tests cover malformed stat files, missing files, successful start time extraction, and runtime-user/resource-adjacent behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container_test.go -->
# sources/cloud-native/cri-o/internal/oci/container_test.go

## Purpose
Ginkgo/Gomega unit coverage for the container model, PID state handling, stop coordination, resource projection, and exec PID tracking.

## Important Test Coverage
Tests validate field accessors, spec assignment, ID mappings, volumes, seccomp profile path, mount point, start-failure state, checkpoint restore flags, stop-signal parsing including realtime signals and invalid defaults, Linux resource projection to CRI resources, `FromDisk` success/failure and old-state PID upgrade, `Living`, `ProcessState`, `Pid`, `SetInitPid`, `/proc` stat parser edge cases, `DeleteExecPID`, `KillExecPIDs`, `StartExecCmd`, `SetAsDoneStopping`, watcher notification, and spoofed containers.

## Control Flow, Dependencies, and Risks
The tests use live PIDs (`1`, a high non-running PID), rootless skips where needed, temporary state files, and the test-only injection helpers. Important regression signals include PID wrap detection, stopped-runtime `Pid == 0` handling, avoiding PID 0 kill, rejecting exec starts after kill-loop begins, and ensuring `WaitOnStopTimeout` does not panic after stop completion. Some signal behavior is only indirectly observed because syscall killing is not mocked.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container_test_inject.go -->
# sources/cloud-native/cri-o/internal/oci/container_test_inject.go

## Purpose
Provides test-only hooks compiled with the `test` build tag for manipulating unexported OCI container/runtime internals.

## Important APIs and Integration
`Container.SetState` replaces internal state. `SetStateAndSpoofPid` fills PID/start-time data with PID 1 when missing, then replaces state. `RuntimeOCI` exposes a wrapper around `runtimeOCI`, and `NewRuntimeOCI` constructs it for tests with a supplied `Runtime` and handler.

## Risks and Test Signals
These helpers bypass production locking and validation, so they should remain build-tag restricted. They enable the container and runtime tests in this subset to exercise private stop/status behavior without starting full CRI-O.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container_test_inject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container_unsupported.go -->
# sources/cloud-native/cri-o/internal/oci/container_unsupported.go

## Purpose
Fallback implementation for platforms that are neither Linux nor FreeBSD.

## Behavior, Integration, and Risks
`getPidStartTime` always returns `"0", nil`, allowing code to compile and PID initialization to proceed but disabling meaningful PID reuse protection. Because `Container.verifyPid` depends on start-time equality, this fallback is intentionally weak and should not be treated as equivalent to Linux/FreeBSD support. No direct tests cover this unsupported path.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/container_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/finished.go -->
# sources/cloud-native/cri-o/internal/oci/finished.go

## Purpose
Linux non-32-bit implementation for deriving container finish time from the conmon exit file's inode metadata.

## Behavior and Integration
`getFinishedTime` asserts `os.FileInfo.Sys()` to `*syscall.Stat_t` and returns `time.Unix(st.Ctim.Sec, st.Ctim.Nsec)`. It is called by `updateContainerStatusFromExitFile` in `runtime_oci.go` to populate `ContainerState.Finished`.

## Risks and Tests
The code assumes Linux `ctime` is the desired finish marker and that `FileInfo.Sys()` has the expected type. The 32-bit variant handles type conversion separately. Runtime status tests indirectly cover exit-file reading but not architecture-specific stat behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/finished.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/finished_32.go -->
# sources/cloud-native/cri-o/internal/oci/finished_32.go

## Purpose
Linux arm/386 implementation for deriving finish time from exit-file ctime with explicit integer conversion.

## Behavior, Integration, and Risks
`getFinishedTime` mirrors the main Linux implementation but converts `st.Ctim.Sec` and `st.Ctim.Nsec` to `int64`. It supports `runtime_oci.go` exit-file status handling on 32-bit builds. Risk is limited to stat type assumptions and ctime semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/finished_32.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/finished_unsupported.go -->
# sources/cloud-native/cri-o/internal/oci/finished_unsupported.go

## Purpose
Non-Linux fallback for container finish time extraction.

## Behavior, Integration, and Risks
`getFinishedTime` returns `fi.ModTime()` instead of platform-specific creation/change time. It keeps exit-file status code portable but may be less semantically accurate than Linux ctime. It is used by `runtime_oci.go` when reading `dir/exit`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/finished_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/oci.go -->
# sources/cloud-native/cri-o/internal/oci/oci.go

## Purpose
Defines the runtime abstraction used by CRI-O to dispatch container operations to OCI, VM, or pod-level conmon-rs implementations while centralizing runtime handler lookup and feature queries.

## Important APIs and Types
`Runtime` stores config and a per-container `runtimeImplMap` guarded by `runtimeImplMapMutex`. `RuntimeImpl` is the lifecycle interface: create/start/exec/exec-sync/update/stop/delete/status/pause/stats/attach/port-forward/log-reopen/checkpoint/restore/alive/probe/serve streaming. `New`, `ValidateRuntimeHandler`, `getRuntimeHandler`, feature query methods, `newRuntimeImpl`, `RuntimeImpl`, and wrapper lifecycle methods are the core APIs. `ExecSyncError` preserves stdout/stderr/exit code around exec-sync failures.

## Control Flow and State
`New` ensures the exec notification directory exists. Handler lookup defaults to configured default runtime unless the container has a runtime handler. `newRuntimeImpl` chooses VM for `RuntimeTypeVM`, pod for `RuntimeTypePod`, otherwise OCI. `CreateContainer` constructs a fresh implementation and stores it by container ID; most other methods retrieve the cached implementation. `DeleteContainer` removes the cached implementation only after successful deletion.

## Dependencies and Integration
Integrates CRI-O config, seccomp config, runtime feature detection, cgroup stats, OCI specs, CRI streaming, and Kubernetes CRI types. Server-level CRI operations call this file rather than concrete runtime implementations.

## Risks and Test Signals
Risks include stale implementation cache entries after failed delete, panic potential in pod runtime creation if infra runtime is absent, and defaults when runtime type is empty. `oci_test.go` covers creation, runtime handler validation, type queries, seccomp, allowed annotations, privileged-without-host-devices, and checkpoint/restore failure paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/oci.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/oci_linux.go -->
# sources/cloud-native/cri-o/internal/oci/oci_linux.go

## Purpose
Linux platform support for OCI runtime creation: conmon cgroup placement, process attributes, and sync-pipe creation.

## Important APIs and Control Flow
`InfraContainerName` is `POD`. `runtimeOCI.createContainerPlatform` builds a small generated spec, applies infra cpuset when configured and monitor cgroup is pod-scoped, mutates the conmon spec from workload annotations, moves conmon to the configured cgroup via the cgroup manager, and records the cgroupfs path for cleanup. `sysProcAttrPlatform` sets a new process group. `newPipe` creates a Unix socketpair used for conmon sync and start pipes.

## Integration, Risks, and Tests
Called from `runtimeOCI.CreateContainer` and `runtimePod.CreateContainer`. It depends on runtime-tools generate, CRI-O workload annotation mutation, cgroup manager, and Unix socketpairs. Risks are cgroup placement failures and mismatched assumptions about monitor cgroup names. Runtime tests use injected `RuntimeOCI`, but this exact cgroup path is mostly integration-tested outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/oci_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/oci_test.go -->
# sources/cloud-native/cri-o/internal/oci/oci_test.go

## Purpose
Unit tests for the runtime dispatcher and selected checkpoint/restore behavior.

## Test Signals
The suite verifies `New` with default config, runtime map retrieval, handler validation, default/VM runtime type reporting, seccomp lookup failures, allowed annotation filtering, privileged-without-host-devices behavior, and checkpoint/restore behavior when CRIU is available. Restore tests cover missing checkpoint inventory and expected failures when runtime/conmon paths are dummy binaries.

## Dependencies and Risks
Uses CRI-O default config, temporary attach dirs, CRIU availability skips, runtime-spec inputs, and test helper containers. It gives good signals for configuration dispatch but does not exercise real runtime lifecycle success paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/oci_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/oci_unix.go -->
# sources/cloud-native/cri-o/internal/oci/oci_unix.go

## Purpose
Unix non-Windows helper code for TTY exec handling and process killing.

## Important APIs and Control Flow
`ptyStarter` adapts `pty.Start` to `ExecStarter`. `Kill` sends SIGKILL and ignores ESRCH. `setSize` applies terminal window size with `TIOCSWINSZ`. `ttyCmd` starts an exec command in a PTY through `Container.StartExecCmd`, tracks/deletes the exec PID, closes stdout and PTY, handles resize events, copies stdin/stdout concurrently, and waits for process exit.

## Integration, Risks, and Tests
Used by `runtimeOCI.ExecContainer` when TTY is requested. Risks include goroutine copy races, stdout close expectations, and terminal resize errors being logged only. Stop/exec PID tests indirectly cover the `ExecStarter` tracking pattern; TTY IO itself is not deeply tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/oci_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/oci_unsupported.go -->
# sources/cloud-native/cri-o/internal/oci/oci_unsupported.go

## Purpose
Non-Linux platform fallback for runtime platform setup and Linux-specific container metadata methods.

## Behavior and Integration
Defines `InfraContainerName`, no-op `createContainerPlatform`, empty `SysProcAttr`, `os.Pipe`-backed `newPipe`, no-op conmon cgroup cleanup, empty seccomp profile accessors, nil container stats placeholder, and no-op `setSysProcAttr`.

## Risks
This preserves compilation but removes Linux cgroup, seccomp, and socketpair semantics. Any non-Linux runtime behavior relying on these features is degraded and should be treated as unsupported/limited.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/oci_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/oci_windows.go -->
# sources/cloud-native/cri-o/internal/oci/oci_windows.go

## Purpose
Windows-specific stubs for process kill, exit-code extraction, and TTY command support.

## Behavior, Integration, and Risks
`kill` finds and kills a Windows process. `getExitCode` unwraps `exec.ExitError` and `windows.WaitStatus`. `ttyCmd` returns unsupported. The function names do not fully mirror Unix exports in this subset, indicating Windows support is limited and may only satisfy build needs. No tests cover this path.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/oci_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_oci.go -->
# sources/cloud-native/cri-o/internal/oci/runtime_oci.go

## Purpose
Implements the standard conmon-backed OCI runtime lifecycle: create, start, exec, exec-sync, update, stop, delete, status, pause, stats, attach, log reopen, checkpoint/restore, monitor probing, and runtime command execution.

## Important APIs and Control Flow
`runtimeOCI` embeds `Runtime` plus runtime root and handler. `CreateContainer` builds conmon args, creates sync/start pipes, starts conmon, moves conmon to the right cgroup through `createContainerPlatform`, waits for conmon JSON with the init PID, records `InitPid`/start time and conmon monitor process, and cleans up log/runtime resources on failure. `StartContainer` calls runtime `start`. `ExecContainer` writes a temporary process spec and runs direct runtime `exec`, using cgroup FD placement when configured and `ttyCmd` for TTY. `ExecSyncContainer` runs conmon in exec mode, reads conmon exit JSON, handles timeout as CRI response, truncates/parses CRI log output, and returns stdout/stderr/exit code. `StopContainer` starts `StopLoopForContainer`; the loop sends the configured stop signal, accepts updated shorter timeouts, watches PID liveness, logs blocked processes, then retries SIGKILL with backoff. `UpdateContainerStatus` combines runtime `state`, exit file waiting, exit-code parsing, OOM marker detection, and node-level PID namespace cleanup. Attach and log reopen use conmon control/socket files. Checkpoint/restore use CRIU/runc support checks and checkpoint metadata paths.

## State, Persistence, and Dependencies
Persists conmon pidfile, container pidfile, attach/ctl/winsz files, `dir/exit`, log files, checkpoint directories, dump/restore logs, and OOM marker files. Depends on conmon config, CRIU utilities, fsnotify, OCI spec, cmdrunner, CRI-O metrics/log/config/cgroup manager, Kubernetes wait/exec helpers, Unix signals, and platform pipe/cgroup helpers.

## Integration Points
Selected by `Runtime.newRuntimeImpl` for ordinary OCI handlers and embedded by `runtimePod` for shared behavior. It depends heavily on `Container` lock/state methods, stop coordination, PID identity verification, monitor process fields, and resource paths. Server code observes exit files in `ContainerExitsDir`.

## Risks and Test Signals
High-risk areas include conmon pipe ordering, cleanup after partial create, exec PID registration during stops, output truncation, exit-file race handling, kill-loop timing, node-level PID namespace cleanup, and monitor liveness false positives. `runtime_oci_test.go` covers stop-loop timeout behavior, fallback SIGKILL, timeout updates, context cancellation, output truncation, and waiting for fast-exit files before defaulting to 255.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_oci.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_oci_linux.go -->
# sources/cloud-native/cri-o/internal/oci/runtime_oci_linux.go

## Purpose
Linux-specific OCI runtime helpers for port forwarding into a container network namespace and cgroup-FD process placement for exec commands.

## Important APIs and Control Flow
`PortForwardContainer` enters `netNsPath` with CNI `ns.WithNetNSPath`, dials `localhost:<port>` with Happy Eyeballs fallback disabled, copies bytes bidirectionally between the client stream and namespace TCP connection, handles context cancellation, and gives the second copy direction one second to finish. `setSysProcAttr` sets `UseCgroupFD` and `CgroupFD` on an `exec.Cmd`.

## Integration, Risks, and Tests
Called through `Runtime.PortForwardContainer` for OCI and delegated by pod runtime. Risks include namespace entry failures, half-closed stream behavior, localhost IPv4/IPv6 ordering, and goroutine copy errors. No dedicated tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_oci_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_oci_test.go -->
# sources/cloud-native/cri-o/internal/oci/runtime_oci_test.go

## Purpose
Tests critical `runtimeOCI` stop/status utility behavior using mocked command runners and real short-lived processes.

## Test Signals
Stop-loop tests verify early return when runtime kill fails but the process is already gone, graceful stop before timeout, SIGKILL fallback after timeout, shorter timeout updates overriding longer waits, longer updates not extending an earlier target, many concurrent timeout updates, and context cancellation. `TruncateAndReadFile` tests validate size-capped reads. `UpdateContainerStatus` tests verify fast-exit race handling: wait for `dir/exit` and read code 0 instead of immediately defaulting to 255; also verify default 255 when no exit file appears.

## Dependencies and Risks
Uses mock `cmdrunner`, temporary attach/socket/container dirs, actual `sleep` processes, and test-only `RuntimeOCI`. These tests strongly cover concurrency timing but remain sensitive to host process and timer behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_oci_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_pod.go -->
# sources/cloud-native/cri-o/internal/oci/runtime_pod.go

## Purpose
Implements the pod-level conmon-rs runtime adapter. It manages a conmon-rs server per pod/infra container while delegating much OCI behavior to an embedded `runtimeOCI`.

## Important APIs and Control Flow
`newRuntimePod` returns the infra container's runtime for workload containers by looking up the sandbox implementation; for infra containers it configures a conmon-rs client with runtime path/root, cgroup manager, tracing, log driver, and heaptrack options parsed from monitor env. `CreateContainer` moves the conmon-rs process to the desired cgroup for infra/spoofed containers, creates the container through conmon-rs, records init PID and monitor process start time. Most lifecycle methods delegate to embedded OCI behavior. `ExecSyncContainer`, `AttachContainer`, `ReopenContainerLog`, `ServeExecContainer`, and `ServeAttachContainer` use conmon-rs RPCs directly. Deleting the infra container shuts down the conmon-rs client.

## State, Dependencies, and Integration
State is shared with `Container`; server files and attach sockets live under the pod server directory. Depends on `github.com/containers/conmon-rs/pkg/client`, CRI-O tracing/config/logging, Podman resize utilities, and conmon timeout constants. Selected when a handler has `RuntimeTypePod`.

## Risks and Test Signals
The non-infra lookup panics if the sandbox runtime was not created first. Environment parsing accepts only known key/value options. The hybrid delegation means conmon-rs and OCI assumptions must stay compatible for status, stop, and checkpoint paths. No direct tests for this file are in the subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_pod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_vm.go -->
# sources/cloud-native/cri-o/internal/oci/runtime_vm.go

## Purpose
Implements CRI-O's VM/containerd-shim-v2 runtime path, aimed at Kata/VM-based containers where host PID assumptions differ from standard OCI.

## Important APIs and Control Flow
`runtimeVM` holds shim path/config, FIFO dir, exits path, ttrpc client/task service, runtime handler, and tracked `ContainerIO`. `newRuntimeVM` registers type URLs for OCI spec/process/resources. `CreateContainer` starts the shim daemon, creates FIFO-backed IO/loggers, builds `CreateTaskRequest`, optionally injects Kata guest-pull virtual-volume metadata, calls task `Create` with timeout, and records init PID. `StartContainer` starts the task and launches a wait goroutine that writes an exit marker and updates status. Exec flows through `execContainerCommon`: create exec FIFOs, attach streams, marshal process spec, task `Exec`, `Start`, resize, wait, timeout kill, and delete. `StopContainer` checks state, optionally sends stop signal, waits, then SIGKILLs with a fixed kill timeout. Status reconnects from bundle `address` if needed, reads task state, restores IO tracking, maps task status to CRI-O state, records exit code/PID, and marks OOM from bundle marker. Attach, log reopen, pause/unpause, update, low-level start/wait/kill/remove/resize/closeIO, and Kata virtual volume base64 encoding are also defined.

## State, Persistence, and Dependencies
Persists shim address/log files in the bundle, FIFO files under runtime root, CRI log output, exit markers in `ContainerExitsDir`, and bundle `oom` markers. Depends on containerd task v2/ttrpc/cio/fifo/typeurl/protobuf, Kata virtual volume types, OCI spec, CRI types, CRI-O logging/metrics/errdefs, and conmon timeout message constants for CRI-compatible exec-sync timeouts.

## Integration Points
Selected for handlers with `RuntimeTypeVM`. It uses `Container` state/locks/spec/log paths but deliberately avoids `Container.Living` for liveness because VM PID semantics differ. Linux stats are implemented in `runtime_vm_linux.go`; non-Linux stats are unsupported.

## Risks and Test Signals
Risks include shim connection lifecycle, cleanup after partial create, `ctrs` map consistency, nil `containerInfo` during forced cleanup, FIFO file leaks, timeout goroutines, error mapping from ttrpc/gRPC, guest-pull annotations, and unimplemented checkpoint/restore/serve streaming. No direct tests for this file appear in the subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_vm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_vm_linux.go -->
# sources/cloud-native/cri-o/internal/oci/runtime_vm_linux.go

## Purpose
Linux VM runtime stats implementation, translating shim-returned cgroup v1/v2 metrics into CRI-O `stats.CgroupStats`.

## Important APIs and Control Flow
`runtimeVM.CgroupStats` calls task `Stats`, unmarshals the protobuf `Any`, accepts either containerd cgroups v1 or v2 metrics, and dispatches to `metricsV1ToCgroupStats` or `metricsV2ToCgroupStats`. `DiskStats` returns an empty stats object. The translation functions map CPU usage/throttling, memory/cache/swap/kernel fields, pids, hugetlb stats, and `SystemNano`.

## Dependencies, Integration, Risks, and Tests
Depends on containerd cgroup metrics, opencontainers cgroups stats, typeurl, and CRI-O errdefs/logging. The code accounts for guest cgroup version differing from host cgroup version. Risks are incomplete metric field mapping and empty disk stats. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_vm_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_vm_unsupported.go -->
# sources/cloud-native/cri-o/internal/oci/runtime_vm_unsupported.go

## Purpose
Non-Linux fallback for VM runtime stats.

## Behavior and Risks
`CgroupStats` and `DiskStats` both return unsupported errors. This preserves build portability while making VM stats Linux-only. No direct tests cover this path.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/runtime_vm_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/suite_test.go -->
# sources/cloud-native/cri-o/internal/oci/suite_test.go

## Purpose
Shared Ginkgo test framework setup for the OCI package tests.

## Important APIs and State
`TestOci` registers the Gomega fail handler and runs framework specs. Global test state includes `TestFramework`, gomock controller, container storage mock, a reusable container, and config. `beforeEach` creates a basic container. `getTestContainer` creates a richer container with image reference and storage image ID. `BeforeSuite`/`AfterSuite` set up and tear down the test framework and mocks.

## Integration and Risks
This file underpins `container_test.go`, `oci_test.go`, and `runtime_oci_test.go`. Global state makes test ordering and cleanup important; gomock finish is centralized here.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/artifact.go -->
# sources/cloud-native/cri-o/internal/ociartifact/artifact.go

## Purpose
Wraps `libartifact.Artifact` with CRI-O metadata: root path, parsed named reference, pinned status, digest accessors, canonical naming, and CRI image projection.

## Important APIs and Control Flow
`unknownRef` is a fallback named reference. `Artifact` embeds libartifact data and stores `rootPath`, `namedRef`, and `pinned`. `Store.newArtifact` parses artifact names when present, falls back to `unknown`, and combines forced pinning with regex-based pinning. `Reference`, `CanonicalName`, `Digest`, `RootPath`, and `CRIImage` expose metadata; `CRIImage` maps digest to CRI image ID, size to total artifact size, tag when the reference is tagged, canonical repo digest, and pinned flag.

## Integration, Risks, and Tests
Used by artifact listing/status and datastore reads. Bad artifact names are tolerated with warnings but produce `unknown@digest` canonical names. Pinning depends on `Store.isArtifactPinned`. No direct tests in this subset target this wrapper.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/artifact.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/datastore/impl.go -->
# sources/cloud-native/cri-o/internal/ociartifact/datastore/impl.go

## Purpose
Defines an abstraction layer over image-reference, OCI layout, blob, and short-name operations for the OCI artifact data store.

## Important APIs and Behavior
`Impl` exposes parsing, docker/layout reference construction, image source creation/closing, manifest layer enumeration, blob retrieval, reader draining, and candidate resolution. `defaultImpl` delegates to containers/image docker/reference/layout APIs and manifest helpers. `CandidatesForPotentiallyShortImageName` rejects short names and requires fully qualified artifact names, returning a tag-normalized candidate.

## Integration, Risks, and Tests
`datastore.Store` uses this interface for test injection and all external I/O. Rejecting short names is a security/clarity choice for artifacts. `store_test.go` mocks this interface for pull reference error paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/datastore/impl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/datastore/store.go -->
# sources/cloud-native/cri-o/internal/ociartifact/datastore/store.go

## Purpose
Extends the OCI artifact store with data retrieval: pulling artifacts, locating them by digest/name, reading artifact layer blobs into memory, enforcing size limits, and verifying layer digests.

## Important APIs and Control Flow
`ArtifactData` wraps raw bytes. `Store` embeds `ociartifact.Store`, stores system context, and uses an injectable `Impl`. `New` creates a main artifact store without additional read-only stores. `PullOptions` controls config media type placeholder, max in-memory size, and copy options. `PullData` sanitizes options, resolves a docker reference, pulls through `ociartifact.Store.Pull`, then loads layer data by manifest digest. `artifactData` resolves digest/name, opens an OCI layout image source, iterates manifest layer infos, reads each blob, and enforces cumulative size. `readBlob` checks known blob size, reads at most `max+1`, and verifies the digest with `verifyDigest`. `getByNameOrDigest` accepts full or short digests of at least 3 chars, otherwise resolves fully qualified named candidates and compares reference/canonical name. `getImageReference` normalizes and tags image names before creating docker references.

## State, Persistence, Dependencies, and Integration
Artifact bytes remain in memory; blobs persist in the embedded OCI artifact store under `<root>/artifacts`. Depends on containers/image, libimage copy options, blob info cache, manifest APIs, and `ociartifact.Store`. This is likely used by CRI-O features that need small artifact payloads such as profiles/config snippets.

## Risks and Test Signals
The `EnforceConfigMediaType` option is defined but not enforced in this file. Short digest matching can be ambiguous because it returns the first listed match. Size enforcement is both per-layer and cumulative, but a `ReadAll` error from `LimitReader` must be interpreted carefully. Digest verification is strong. Tests cover parse and docker-reference failure injection only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/datastore/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/datastore/store_test.go -->
# sources/cloud-native/cri-o/internal/ociartifact/datastore/store_test.go

## Purpose
Unit tests for datastore `PullData` reference-resolution failures.

## Test Signals
The tests create a datastore in a temporary artifact root, inject a mocked `Impl`, and verify that `PullData` returns errors when `ParseNormalizedNamed` fails and when `DockerNewReference` fails. They assert returned data is nil and error strings include the expected wrapping context.

## Dependencies and Risks
Uses gomock, Ginkgo/Gomega, and mocked datastore implementation. Coverage is narrow; blob reading, digest verification, max-size enforcement, name/digest lookup, and pull success paths are not covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/datastore/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/datastore/store_test_inject.go -->
# sources/cloud-native/cri-o/internal/ociartifact/datastore/store_test_inject.go

## Purpose
Test-only injection helpers for the OCI artifact datastore.

## APIs and Integration
`Store.SetImpl` replaces the datastore implementation interface with a mock. `ArtifactData.SetData` mutates raw data for tests. Both are compiled only with the `test` build tag and support `store_test.go` plus future datastore tests.

## Risks
The helpers bypass production encapsulation and should remain test-build-only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/datastore/store_test_inject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/datastore/suite_test.go -->
# sources/cloud-native/cri-o/internal/ociartifact/datastore/suite_test.go

## Purpose
Ginkgo suite bootstrap for datastore tests.

## Behavior and Integration
`TestRun` registers failure handling and runs framework specs named `DataStore`. Suite setup/teardown initializes the shared CRI-O test framework. This is required for `store_test.go`.

## Risks
Global framework state is small here; failures would mostly affect test setup/cleanup rather than production code.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/datastore/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/impl.go -->
# sources/cloud-native/cri-o/internal/ociartifact/impl.go

## Purpose
Abstracts manifest retrieval and platform-specific manifest-list resolution for the OCI artifact store.

## APIs and Behavior
`Impl` defines `ChooseInstance` for selecting a manifest digest from a multi-image list and `GetManifestFromRef` for fetching manifest bytes and MIME type, optionally for a selected instance digest. `defaultImpl` delegates to containers/image `manifest.List.ChooseInstance` and `ImageReference.NewImageSource().GetManifest`.

## Integration, Risks, and Tests
Used by `Store.EnsureNotContainerImage` to distinguish OCI artifacts from ordinary images before pulling. The abstraction makes manifest classification testable. Risks are mostly external-reference I/O errors and platform selection mismatches. Direct tests are outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/impl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/libartifact_store.go -->
# sources/cloud-native/cri-o/internal/ociartifact/libartifact_store.go

## Purpose
Defines a small interface around `libartifact.ArtifactStore` so CRI-O artifact store logic can be tested and can access the underlying system context.

## APIs and Integration
`LibartifactStore` includes `Remove`, `List`, `Pull`, `Inspect`, and `SystemContext`. `artifactStore` embeds `*libartifact.ArtifactStore` and exposes its `SystemContext` field via a method. `Store.NewStore` wraps the main and additional stores with this interface.

## Risks and Tests
The interface is straightforward but central to testability and additional-store behavior. Any libartifact API change must be mirrored here. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/libartifact_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/store.go -->
# sources/cloud-native/cri-o/internal/ociartifact/store.go

## Purpose
Implements CRI-O's OCI artifact store: pull validation, main and read-only additional store support, listing, status lookup, removal, blob mount path discovery, and artifact pinning.

## Important APIs and Control Flow
`NewStore` creates the main `<root>/artifacts` libartifact store, opens additional read-only artifact stores, stores an injectable manifest `Impl`, and initializes pinned regexps atomically. `Pull` first calls `EnsureNotContainerImage`, skips pulling when the artifact already exists in an additional store, otherwise pulls into the main store. `EnsureNotContainerImage` fetches the root manifest, resolves manifest lists for the current platform, parses the selected manifest, and returns `ErrIsAnImage` when manifest/config media types match standard container images and no OCI `artifactType` is present. `List` reads additional stores first, then main store, wraps artifacts with root/pinning metadata, and deduplicates by reference with additional stores winning. `Status` checks additional stores before main. `Remove` only removes from the main writable store. `BlobMountPaths` opens the artifact's OCI layout, resolves local blob paths for layers, and names mountable blobs from OCI title or ModelPack filepath annotations. `SetPinnedImageRegexps`, `isArtifactPinned`, and `RootPath` round out the API.

## State, Persistence, Dependencies, and Integration
Artifacts persist under `<root>/artifacts`; additional stores are read-only and force-pinned. Uses libartifact/libimage, containers/image manifest/layout/types, OCI image spec, ModelPack annotations, atomic regex pointer reloads, and CRI-O logging. `Artifact.CRIImage` turns these objects into CRI image-like records.

## Risks and Test Signals
Classification depends on MIME type and OCI artifactType interpretation; unusual images/artifacts can be misclassified. Additional store errors are warned and skipped for list/status. Deduplication by `Reference()` may collapse `unknown` references. Pinning regexps match both reference and canonical name. No tests for this file are included in the listed subset, so edge cases are under-covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/store.go -->
