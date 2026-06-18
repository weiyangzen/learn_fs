<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/trap/trap.go -->
# sources/cloud-native/moby/daemon/command/trap/trap.go

## Purpose
Implements Unix command-style graceful shutdown on first interrupt/terminate and forced process exit after repeated signals.

## Important APIs, Types, And Functions
`forceQuitCount` is `3`. `Trap(cleanup func())` installs `signal.Notify` for `os.Interrupt` and `SIGTERM`.

## Control Flow
A goroutine counts received signals. The first signal launches `cleanup` once in a goroutine. Signals up to the threshold are logged and ignored after cleanup starts. A later signal exits immediately with `128 + signal`.

## State And Persistence Behavior
Installs process-wide signal notification and keeps interrupt count in the goroutine. No disk persistence.

## Dependencies And Integration Points
Uses containerd logging and Go signal/syscall packages. Used by the dockerd process to coordinate graceful cleanup.

## Risks And Test Signals
Risks include off-by-one force-exit semantics, cleanup goroutine still running during repeated signals, and process-wide signal handler interactions. Linux trap tests assert expected exit codes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/trap/trap.go -->
