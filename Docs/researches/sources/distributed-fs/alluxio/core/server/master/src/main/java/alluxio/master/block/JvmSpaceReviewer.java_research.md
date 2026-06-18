# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/JvmSpaceReviewer.java

## Purpose
`JvmSpaceReviewer` is a heap-admission guard for worker registration leases. It estimates the temporary heap needed to process a register request from the request block count and rejects requests likely to overcommit the master JVM.

## Important APIs and Types
- `BLOCK_COUNT_MULTIPLIER = 400` estimates bytes of heap allocation per reported block.
- Constructor accepts a `Runtime`, package-visible for tests and `RegisterLeaseManager`.
- `reviewLeaseRequest(GetRegisterLeasePRequest)` returns whether the request can be admitted.
- `getAvailableBytes()` computes `maxMemory - (totalMemory - freeMemory)`.

## Control Flow
On each lease request, the reviewer reads `request.getBlockCount()`, estimates space as block count multiplied by the multiplier, computes available JVM heap, logs the decision, and returns true only when available bytes exceed the estimate.

## State and Persistence Behavior
The reviewer is stateless except for the `Runtime` reference. It persists nothing and participates only in runtime lease admission.

## Dependencies and Integration Points
It depends on the gRPC lease request type and Java `Runtime`. `RegisterLeaseManager` creates it when `MASTER_WORKER_REGISTER_LEASE_RESPECT_JVM_SPACE` is enabled.

## Risks and Edge Cases
The estimate is intentionally coarse and derived from observed tests; it may be conservative or insufficient for different payload shapes. Multiplication uses `long` operands after widening `blockCount`, but extremely large counts could still overflow. The strict `>` comparison rejects exact-fit requests, favoring safety.

## Test Signals
`JvmSpaceReviewerTest` mocks `Runtime`, verifies available heap math, and checks accept/reject behavior around the multiplier threshold.
