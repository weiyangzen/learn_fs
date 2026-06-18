# sources/cloud-native/containerd/internal/cleanup/context.go

## Purpose

`context.go` provides a small cleanup utility that runs cleanup callbacks with a context detached from caller cancellation but bounded by a timeout.

## Important APIs, Types, and Functions

- `Do(ctx context.Context, do func(context.Context))` wraps `context.WithoutCancel(ctx)` in a 10-second timeout, calls the callback, and then cancels the timeout context.

## Control Flow

`Do` creates the derived timeout context, invokes the callback synchronously, and calls `cancel` after the callback returns.

## State and Persistence Behavior

The function does not persist state. It preserves values from the parent context while clearing cancellation/deadline/error state and adding its own 10-second deadline.

## Dependencies and Integration Points

It depends only on Go `context` and `time`. It is intended for cleanup paths that should proceed even if request contexts are already canceled.

## Risks and Edge Cases

Because the callback is synchronous, a callback that ignores context cancellation can still block longer than 10 seconds; the timeout only signals through `ctx.Done()`.

## Test Signals

`context_test.go` verifies detached cancellation, value preservation, nested cancellation, and timeout behavior.
