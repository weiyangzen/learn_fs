## sources/cloud-native/moby/daemon/internal/ioutils/copy.go

Purpose: Provides context-aware reader/copy helpers for long-running stream operations.

Important APIs/types: `CopyCtx(ctx, dst, src)` wraps `io.Copy` and returns early on context cancellation. `NewCtxReader(ctx, r)` wraps reads with context checks. `readerCtx` implements `Read`.

Control flow: `CopyCtx` wraps `src`, starts `io.Copy` in a goroutine, and races copy completion against `ctx.Done()`. On cancellation it returns `-1, ctx.Err()` without closing the writer and without waiting for the copy goroutine. `readerCtx.Read` checks `ctx.Err()` before and after the underlying `Read`, returning context error if cancellation is observed.

State and persistence: No persistent state. It can leave a goroutine blocked if the underlying reader or writer blocks after cancellation, as documented.

Dependencies and integration: Used by tar load/save and archive handling to make stream operations cancellable at API boundaries.

Risks: Goroutine lifetime is intentionally not guaranteed after cancellation. If underlying IO ignores cancellation and blocks forever, resources may remain. Partial bytes read concurrently with cancellation are discarded by returning zero and context error from `readerCtx`.

Test signals: `copy_test.go` validates that `CopyCtx` returns promptly when a blocking reader is paired with a cancelled context.
