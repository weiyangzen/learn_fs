# sources/cloud-native/moby/daemon/debugtrap_unix.go

## Purpose
Installs a Unix SIGUSR1 trap that writes goroutine stack dumps to the daemon root/exec-root area.

## Important APIs, Types, And Functions
- `setupDumpStackTrap` creates a signal channel, registers `syscall.SIGUSR1`, and starts a goroutine.
- The goroutine calls `stackdump.DumpToFile(root)` for each signal.

## Control Flow
Daemon startup calls this once with the selected stack-dump directory. The goroutine blocks on the signal channel and logs any dump failure.

## State And Persistence
Persists stack dump files in the provided root directory when SIGUSR1 is received. It also installs process-level signal notification.

## Dependencies And Integration Points
Uses Go `os/signal`, Unix `syscall.SIGUSR1`, containerd logging, and Moby stackdump utility. Called from `NewDaemon`.

## Risks And Edge Cases
If the dump directory is unwritable, signal handling remains installed but dumps log errors. Signal behavior is Unix-specific and absent on unsupported targets.

## Test Signals
No direct unit tests; operational signal is successful stack dump creation after SIGUSR1.
