# sources/control-plane/rook/pkg/util/exec/test/mockexec.go

## Purpose
`mockexec.go` provides a mock implementation of the exec `Executor` interface and a helper process pattern for realistic exec errors in tests.

## Important APIs, Types, and Functions
`MockExecutor` exposes function fields for each executor method. Its methods call configured functions or return zero values. `MockExecCommandReturns()` reruns the current test binary with environment variables controlling stdout, stderr, and return code. `TestMockExecHelperProcess()` implements the helper process. `FakeTimeoutError()` builds an error string recognized by `exec.IsTimeout()`.

## Control Flow, State, and Persistence
Mock methods are in-memory callbacks. The helper process uses environment variables and exits with a requested code. It writes stderr before stdout by design.

## Dependencies and Integration Points
It depends on Go `os/exec`, `os`, `testing`, and time. It is used by sys tests and exec tests to simulate command behavior without invoking real system tools.

## Risks
`ExecuteCommandWithStdin()` checks `MockExecuteCommand` but calls `MockExecuteCommandWithStdin`, so if only stdin callback is set and `MockExecuteCommand` is nil, it returns nil without invoking the callback. `ExecuteCommandWithTimeout()` passes `time.Second` to the callback instead of the caller's timeout. Helper-process env values are raw strings, so embedded newlines or special values need care.

## Test Signals
The helper process is imported by `exec_test.go`. Sys tests use `MockExecutor` callbacks to control `lsblk`, `udevadm`, and other command outputs.
