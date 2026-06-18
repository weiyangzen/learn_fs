<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/trap/trap_linux_test.go -->
# sources/cloud-native/moby/daemon/command/trap/trap_linux_test.go

## Purpose
Integration-tests trap behavior by compiling and executing the helper program.

## Important APIs, Types, And Functions
`buildTestBinary` runs `go build` for `testfiles/main.go`. `TestTrap` runs cases for TERM and INT, single and repeated.

## Control Flow
Each case starts the helper executable with signal environment variables, waits for it to exit, type-asserts `*exec.ExitError`, and extracts the Unix wait status exit code.

## State And Persistence Behavior
Build artifacts live under `t.TempDir`. Child process signal behavior is isolated from the test process.

## Dependencies And Integration Points
Depends on Go toolchain, Unix signals, `os/exec`, and `gotest.tools`. It tests the public `trap.Trap` function via process exit behavior.

## Risks And Test Signals
Repeated-signal cases use an unbounded loop in the helper goroutine, so timing matters. Passing signals are exit `99` for single cleanup and `128+signal` for forced exit.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/trap/trap_linux_test.go -->
