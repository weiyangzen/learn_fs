<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/trap/testfiles/main.go -->
# sources/cloud-native/moby/daemon/command/trap/testfiles/main.go

## Purpose
Provides a tiny test binary that self-signals to exercise the trap package behavior in a separate process.

## Important APIs, Types, And Functions
`main` installs `trap.Trap`, maps `SIGNAL_TYPE` to `SIGTERM`, `SIGQUIT`, or interrupt, and uses `IF_MULTIPLE` to choose one signal or a tight signal loop.

## Control Flow
Cleanup sleeps one second and exits `99`. A goroutine finds the current process and sends the requested signal(s). The main goroutine sleeps long enough for trap behavior to decide the exit path.

## State And Persistence Behavior
Process-only signal state. No filesystem writes.

## Dependencies And Integration Points
Built by `trap_linux_test.go` and imports `daemon/command/trap`.

## Risks And Test Signals
Signals are exit code `99` for first SIGTERM/SIGINT cleanup and `128+signal` for repeated forced termination. SIGQUIT is sent but not part of trap's notify list.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/trap/testfiles/main.go -->
