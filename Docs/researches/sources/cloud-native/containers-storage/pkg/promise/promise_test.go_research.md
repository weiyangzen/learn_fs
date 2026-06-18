# sources/cloud-native/containers-storage/pkg/promise/promise_test.go

Purpose: tests the minimal promise helper.

Important APIs, types, and functions: `TestGo`, `functionWithError`, and `functionWithNoError`.

Control flow: calls `Go` with an error-returning function, reads the channel, checks error text, then repeats with a nil-returning function and checks nil.

State and persistence: no persistence. State is a buffered channel result.

Dependencies and integration points: depends on `errors`, `testing`, and `testify/require`.

Risks and edge cases: tests do not cover panic behavior, unread channels, or timing.

Test signals: verifies that `Go` executes the function asynchronously and returns the exact error value through the channel.
