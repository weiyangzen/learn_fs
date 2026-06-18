# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/RpcContextTest.java

## Purpose
Unit tests for `RpcContext` close semantics and cancellation tracking. It verifies close order, exception propagation/suppression, and how operation-context call trackers mark an RPC as cancelled.

## Important APIs/types/functions
- Mocks `BlockDeletionContext`, `JournalContext`, and `OperationContext`.
- Constructs `RpcContext(mMockBDC, mMockJC, mMockOC)`.
- Tests `close`, `isCancelled`, and `throwIfCancelled`.
- Uses custom `CallTracker` implementations through `InternalOperationContext.withTracker`.

## Control flow
- Basic close test calls `close()` with no exceptions.
- Order test records close calls and asserts journal context closes before block deletion context.
- Dual exception tests make both close calls throw, expecting the journal exception as primary and block deletion exception suppressed.
- Single exception tests verify both resources are still closed.
- Cancellation test adds one always-cancelled tracker and one active tracker, then expects `isCancelled()` true and `throwIfCancelled()` to throw.

## State and persistence behavior
- No persistent state; tests are resource-lifecycle and cancellation-state checks.
- Suppressed exceptions preserve secondary close failure context.

## Dependencies and integration points
- Integrates with journal and block deletion resource contracts and operation context call trackers used by file master RPC paths.

## Risks and edge cases
- Exact primary exception depends on close order; intentional but sensitive to resource ordering changes.
- Cancellation test expects any cancelled tracker to cancel the RPC, regardless of tracker type.

## Test signals
- Strong signal for safe cleanup under failures and correct cancellation propagation from client/state-lock trackers.
