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
