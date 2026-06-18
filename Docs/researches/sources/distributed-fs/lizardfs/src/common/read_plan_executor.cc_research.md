<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_plan_executor.cc -->
# sources/distributed-fs/lizardfs/src/common/read_plan_executor.cc

## Purpose
Implements execution of a `ReadPlan` across chunkserver connections, waves, prefetches, failures, and final post-processing. The source was read completely for this report.

## Important APIs, Types, And Functions
`startReadOperation`, `startPrefetchOperation`, `startReadsForWave`, `startPrefetchForWave`, `waitForData`, `readSomeData`, `executeReadOperations`, `checkPlan`, and `executePlan` are implemented. Static atomic execution counters are defined.

## Control Flow
Execution resizes the output buffer to the full plan size, starts wave 0 reads, prefetches next waves, polls active fds, advances per-fd executors, marks available/failed parts, starts later waves on timeout/failure, and stops when the plan says enough parts are available. Then it runs post-processing and shrinks the buffer to final size.

## State And Persistence Behavior
State includes active fd-to-executor map, available parts, networking failures, last failed server, stats counters, and the owned plan.

## Dependencies And Integration Points
Depends on chunk connector/pool, stats, sockets, protocol serializers, read operation executor, block/xor and exception types. Integrates client reads with chunkserver health tracking.

## Risks And Edge Cases
Cleanup on non-`Exception` throws may skip buffer rollback because catch catches `Exception&` only. Prefetch failures are ignored by design. Poll/wave timing controls read latency and redundancy load.

## Test Signals
Needs integration tests with fake connectors for wave progression, failure recovery, timeout, prefetch behavior, stats updates, buffer rollback, and post-processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_plan_executor.cc -->
