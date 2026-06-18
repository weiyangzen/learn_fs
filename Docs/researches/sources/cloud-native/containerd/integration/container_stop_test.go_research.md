# sources/cloud-native/containerd/integration/container_stop_test.go

## Purpose

This file tests container stop behavior in shared PID namespace scenarios and cancellation behavior when the CRI request context expires before the stop timeout. It protects against incorrect task killing and premature cleanup under cancellation.

## Important APIs, Types, And Functions

- `TestSharedPidMultiProcessContainerStop` covers host PID and pod PID sandbox modes.
- `TestContainerStopCancellation` uses a raw CRI gRPC client to cancel `StopContainer` earlier than its requested timeout.
- Shared helpers `WithHostPid`, `WithPodPid`, `RawRuntimeClient`, `Eventually`, and `Consistently` support the tests.

## Control Flow

The shared-PID test creates sandboxes in host and pod PID modes, starts a BusyBox shell that launches two `sleep` processes, calls `StopContainer` with timeout zero, and asserts the state becomes exited. The cancellation test starts a container that traps and ignores SIGTERM, calls raw `StopContainer` with a one-second context timeout and a three-second CRI stop timeout, expects an error, verifies for five seconds that the container remains running, then stops it normally with a one-second timeout.

## State And Persistence Behavior

The tests observe runtime task state only. The cancellation scenario specifically verifies that a canceled RPC does not asynchronously complete the stronger kill path after the client has gone away.

## Dependencies And Integration Points

They integrate with CRI stop handling, raw gRPC request contexts, PID namespace configuration, and container status reporting. Linux-only cancellation behavior is skipped on Windows.

## Risks And Edge Cases

Timing is central: cancellation must happen before the CRI stop timeout and status must be sampled long enough to catch delayed kills. The shell trap semantics depend on PID 1 behavior inside the container namespace.

## Test Signals

Passing indicates multi-process containers stop correctly in shared PID modes and canceled stop requests leave the container running until a subsequent explicit stop.
