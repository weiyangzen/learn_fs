# sources/cloud-native/containers-storage/pkg/promise/promise.go

Purpose: provides a minimal async helper that runs an error-returning function in a goroutine.

Important APIs, types, and functions: `Go(f func() error) chan error`.

Control flow: creates a buffered error channel of size one, starts a goroutine, sends `f()` result, and returns the channel immediately.

State and persistence: no persistence. The returned channel is the only synchronization state.

Dependencies and integration points: no imports. Used where callers want to launch work and later wait for one error result.

Risks and edge cases: no panic recovery, cancellation, context, or channel close. The channel buffer prevents the goroutine from blocking if caller never reads one result, but further protocol is absent.

Test signals: `promise_test.go` verifies both error and nil paths.
