# sources/cloud-native/containerd/integration/failpoint/const.go

## Purpose

This package defines shared environment variable names used by failpoint-enabled runc exec delay tests. It keeps the test code and `runc-fp` helper binary aligned.

## Important APIs, Types, And Functions

- `DelayExecReadyEnv` names the FIFO path env var used by `runc-fp` to signal that an exec reached the delay point.
- `DelayExecDelayEnv` names the FIFO path env var used by tests to release the delayed exec.

## Control Flow

The file is declarative and contains no runtime control flow.

## State And Persistence Behavior

The constants describe process environment state. They do not persist data.

## Dependencies And Integration Points

They are consumed by `failpoint/cmd/runc-fp/delayexec.go` and by tests that populate exec process environments with FIFO paths.

## Risks And Edge Cases

Renaming either constant without updating all producers/consumers would break delay-exec coordination. The leading underscore convention reduces collision risk but does not prevent user-specified environment conflicts.

## Test Signals

Tests that exercise delayed runc exec implicitly validate these constants by successfully synchronizing through the expected FIFOs.
