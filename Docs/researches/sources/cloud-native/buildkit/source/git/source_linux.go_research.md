# sources/cloud-native/buildkit/source/git/source_linux.go

## Purpose
Runs Git subprocesses on Linux with a standard `0022` umask while isolating filesystem attributes from other goroutines and ensuring cancellation kills the whole process group.

## Important APIs, Types, And Functions
- `runWithStandardUmask(ctx, cmd)` launches a locked goroutine and delegates to `unshareAndRun`.
- `unshareAndRun` calls `syscall.Unshare(CLONE_FS)`, sets `Umask(0022)`, and runs the process group.
- `runProcessGroup` sets `Setpgid` and `Pdeathsig`, starts the command, and escalates from SIGTERM to SIGKILL after 10 seconds on context cancellation.

## Control Flow
`gitCLI` in `source.go` injects `runWithStandardUmask` as the executor. Each Git invocation is executed in its own process group; when the context is canceled, a goroutine signals the negative PID to terminate the group and starts a delayed kill fallback.

## State And Persistence
No cache state. It mutates only the child-thread umask after `CLONE_FS`, avoiding global process umask leakage.

## Dependencies And Integration Points
Uses `runtime.LockOSThread`, `syscall`, `os/exec`, `time`, and `x/sys/unix`. It is critical to Git snapshot mode tests that assume host test umask is reset to zero but Git output still uses standard permissions.

## Risks And Edge Cases
`CLONE_FS` failure aborts the Git command. Signal handling assumes process groups were created successfully. The SIGKILL fallback runs asynchronously after `Wait` coordination, so command implementations that spawn detached children remain a residual risk.

## Test Signals
Indirectly tested by the broad Git source suite and specifically by compatibility/file-mode tests that depend on stable Git-created permissions.
