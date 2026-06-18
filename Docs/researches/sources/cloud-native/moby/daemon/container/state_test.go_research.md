<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/state_test.go -->
# sources/cloud-native/moby/daemon/container/state_test.go

## Purpose
Tests container state transitions and wait-channel behavior.

## Important APIs, Types, And Functions
`mockTask`, `TestStateRunStop`, `TestStateTimeoutWait`, and `TestCorrectStateWaitResultAfterRestart`.

## Control Flow
Tests start waits before and after state transitions, manually lock and mutate state through setters, then assert exit codes, PID values, timeout errors, and removal notification. Restart regression ensures waiters receive the exit code from the restart event even after state returns to running.

## State And Persistence Behavior
In-memory only. Uses context timeouts to prevent leaked waits.

## Dependencies And Integration Points
Depends on container API wait conditions and libcontainerd task interface. It guards daemon wait API correctness.

## Risks And Test Signals
Signals include immediate not-running waits for created/exited state, blocking waits while running, timeout exit code `-1`, final removal exit code, and restart wait exit code preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/state_test.go -->
