## sources/cloud-native/moby/daemon/internal/distribution/xfer/transfer_test.go

Purpose: Validates the internal transfer scheduler and progress watcher machinery.

Important tests and helpers: Test-local `makeXferFunc` factories create `newTransfer` instances and progress goroutines. `TestTransfer` confirms progress flows to consumers and reaches the final value. `TestConcurrencyLimit` uses `atomic.Int32` to prove active transfers never exceed the limit. `TestInactiveJobs` closes `inactive` after progress so queued jobs can start before the original goroutine fully exits. `TestWatchRelease` attaches several watchers to one long-running transfer, releases them one by one, and expects transfer cancellation plus closed `released`/`done` channels. `TestWatchFinishedTransfer` verifies watchers created after completion can be released safely. `TestDuplicateTransfer` starts five requests with the same key and confirms the transfer factory runs once while all watchers see progress.

Control flow and state: The tests use unbuffered channels and timed sleeps to exercise scheduling interleavings. Consumers drain progress channels into maps or close notifications to avoid blocking writer goroutines.

Dependencies and integration: Uses the daemon `progress` package and Go atomics. It tests unexported types in-package.

Risks covered: Duplicate work, progress loss, cancelled-transfer reuse, active slot accounting, and watcher lifecycle leaks. Residual risk remains around rare races not reached by timing-based tests; running with `-race` is valuable for this package.

Persistence: None; all state is test-local memory.
