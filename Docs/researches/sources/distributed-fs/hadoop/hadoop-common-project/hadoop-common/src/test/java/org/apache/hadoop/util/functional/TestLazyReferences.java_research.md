# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestLazyReferences.java

Purpose: Tests lazy single-evaluation references and lazy auto-closeable references. It verifies supplier integration, cached evaluation, exception wrapping/retry behavior, close idempotency, closed-state guards, and cleanup when close itself fails.

Important APIs/types/functions: Tests use `LazyAtomicReference`, `LazyAutoCloseableReference`, `lazyAtomicReferenceFromSupplier()`, `lazyAutoCloseablefromSupplier()`, `eval()`, `apply()`, `get()`, `isSet()`, `isClosed()`, `getReference()`, and `close()`. Fixtures `CloseableClass` and `CloseableRaisingException` implement `AutoCloseable`.

Control flow: Lazy atomic tests assert constructors do not invoke suppliers, first `eval()`/`get()` increments the counter once, and later `apply()` returns the cached value. Failure handling throws `UnknownHostException` from the supplier, verifies it is wrapped in `UncheckedIOException`, leaves the reference unset, and retries on the next call. Auto-closeable tests evaluate the reference, close it, assert the underlying object is closed and the inner reference cleared, then verify later eval/get/apply calls fail with "Reference is closed". Failure-close tests assert the first close reports the IO failure but clears state so a second close is harmless.

State and persistence behavior: `AtomicInteger counter` records supplier invocations. Lazy references persist either an evaluated value, unset state after failure, or closed state after close. Auto-closeable references clear their internal atomic reference on close, even when the resource close throws.

Dependencies and integration points: Depends on Hadoop functional lazy reference classes, Hadoop `Preconditions.checkState`, AssertJ, JUnit, and `LambdaTestUtils`. These references support delayed initialization of resources that may throw IO-related failures and need deterministic cleanup.

Risks: Concurrency is implied by `LazyAtomicReference` but not stress-tested across multiple racing threads. Exception wrapping leaves the reference unset, which is useful for retry but can repeatedly trigger expensive failing suppliers. Closing after failed resource close deliberately suppresses future close attempts because the reference has been nulled.

Test signals: Counter values, `isSet()` transitions, cause verification for `UnknownHostException`, closed flags on wrapper and underlying resource, cleared inner reference, and first-close-only exception behavior are primary signals.
