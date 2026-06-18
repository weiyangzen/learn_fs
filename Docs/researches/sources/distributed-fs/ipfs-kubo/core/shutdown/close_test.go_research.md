# sources/distributed-fs/ipfs-kubo/core/shutdown/close_test.go

Purpose: validates `CloseWithCtx` behavior. Important tests are `TestCloseWithCtx_finishesBeforeDeadline`, `TestCloseWithCtx_propagatesCloseError`, and `TestCloseWithCtx_timesOut`.

Control flow: first two tests use real timeout contexts and assert nil/error propagation. The timeout test runs under `synctest`, creates a short fake deadline, blocks the close function until after assertions, verifies elapsed fake time equals the deadline, checks `context.DeadlineExceeded`, then releases the goroutine so synctest can finish cleanly.

State and persistence: no external state.

Dependencies/integration: context, errors, testing/synctest, time. It protects bounded shutdown semantics used by many node lifecycle hooks.

Risks signaled: production intentionally leaks close goroutines on timeout, so tests need explicit release to avoid fake-clock blocked-goroutine failure.
