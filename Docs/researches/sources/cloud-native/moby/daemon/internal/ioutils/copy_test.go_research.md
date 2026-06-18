## sources/cloud-native/moby/daemon/internal/ioutils/copy_test.go

Purpose: Tests that `CopyCtx` responds to context cancellation even when the source reader blocks.

Important test/helper: `blockingReader.Read` sleeps for one second and returns no data. `TestCopyCtx` creates a context with a 5 ms timeout, calls `CopyCtx` in a goroutine, and requires it to finish within 100 ms.

Control flow and state: The test does not inspect returned byte count or error; it only validates liveness.

Dependencies and integration: Uses `bytes.Buffer`, context timeouts, and time-based select.

Risks covered: The primary cancellation path in `CopyCtx`. It does not assert the documented `-1` byte count, context error, or goroutine cleanup behavior after return.

Persistence: None.
