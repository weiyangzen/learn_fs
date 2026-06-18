# sources/cloud-native/containerd/internal/cleanup/context_test.go

## Purpose

`context_test.go` validates the cleanup context wrapper behavior in `internal/cleanup`.

## Important APIs, Types, and Functions

- `TestDo` covers canceled parent context, context value preservation, nested cancellation, and timeout cancellation.
- `contextError` non-blockingly returns `ctx.Err()` when the context is done.

## Control Flow

The test creates a valued context, cancels it, then runs parallel subtests. One ensures `Do` clears parent cancellation while retaining values, one ensures a nested child cancel still works, and one waits for the 10-second timeout signal and verifies the callback ran.

## State and Persistence Behavior

Only in-memory context values, cancellation channels, and test channels are used.

## Dependencies and Integration Points

It uses Go testing, context, time, and testify assertions.

## Risks and Edge Cases

The timeout subtest takes about 10 seconds by design, so it contributes fixed latency. It assumes scheduler timing allows observing the timeout within an additional second.

## Test Signals

Failures show that cleanup contexts no longer detach from parent cancellation, preserve values, or enforce the intended timeout.
