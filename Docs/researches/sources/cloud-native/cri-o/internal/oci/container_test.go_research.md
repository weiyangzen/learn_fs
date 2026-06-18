# sources/cloud-native/cri-o/internal/oci/container_test.go

## Purpose
Ginkgo/Gomega unit coverage for the container model, PID state handling, stop coordination, resource projection, and exec PID tracking.

## Important Test Coverage
Tests validate field accessors, spec assignment, ID mappings, volumes, seccomp profile path, mount point, start-failure state, checkpoint restore flags, stop-signal parsing including realtime signals and invalid defaults, Linux resource projection to CRI resources, `FromDisk` success/failure and old-state PID upgrade, `Living`, `ProcessState`, `Pid`, `SetInitPid`, `/proc` stat parser edge cases, `DeleteExecPID`, `KillExecPIDs`, `StartExecCmd`, `SetAsDoneStopping`, watcher notification, and spoofed containers.

## Control Flow, Dependencies, and Risks
The tests use live PIDs (`1`, a high non-running PID), rootless skips where needed, temporary state files, and the test-only injection helpers. Important regression signals include PID wrap detection, stopped-runtime `Pid == 0` handling, avoiding PID 0 kill, rejecting exec starts after kill-loop begins, and ensuring `WaitOnStopTimeout` does not panic after stop completion. Some signal behavior is only indirectly observed because syscall killing is not mocked.
