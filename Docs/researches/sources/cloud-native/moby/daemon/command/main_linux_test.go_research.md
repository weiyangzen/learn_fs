<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/main_linux_test.go -->
# sources/cloud-native/moby/daemon/command/main_linux_test.go

## Purpose
Registers Linux-only reexec helper commands before command package tests run.

## Important APIs, Types, And Functions
`TestMain` registers `testListenerNoAddrCmdPhase1` and `testListenerNoAddrCmdPhase2` with `reexec.Register`, then exits early if `reexec.Init` handles a helper process.

## Control Flow
Test process initialization first wires helper names to functions, then either runs the reexec helper path or invokes `m.Run`.

## State And Persistence Behavior
Mutates process-level reexec registry. No durable state.

## Dependencies And Integration Points
Depends on `github.com/moby/sys/reexec`. Supports listener inheritance tests in adjacent Linux command files.

## Risks And Test Signals
Risk is missing helper registration causing subprocess tests to run the normal test binary path. The signal is successful Linux listener tests that depend on these names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/main_linux_test.go -->
