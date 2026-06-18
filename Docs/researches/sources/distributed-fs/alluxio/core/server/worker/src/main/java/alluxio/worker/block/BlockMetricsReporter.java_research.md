## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetricsReporter.java

### Purpose
`BlockMetricsReporter` is a thread-safe block-store event listener that translates local block events into worker metrics counters and an eviction-rate meter.

### Important APIs and Types
- Extends `AbstractBlockStoreEventListener`.
- Overrides `onAccessBlock`, `onMoveBlockByClient`, `onRemoveBlockByClient`, `onMoveBlockByWorker`, `onRemoveBlockByWorker`, `onAbortBlock`, and `onBlockLost`.
- Uses static `MetricsSystem.counter` and `meterWithTags` registrations for worker block metrics.

### Control Flow
Event callbacks increment counters. Move callbacks compare old/new tier ordinals and increment promoted-block count when a block moves to tier ordinal 0 from another tier. Worker removals increment both evicted-block counter and eviction-rate meter; client removals increment deleted-block counter.

### State and Persistence
Only metrics are mutated. There is no durable state and no block metadata mutation.

### Dependencies and Integration Points
`DefaultBlockWorker` registers this listener with the block store. It relies on `BlockMetadataManager.WORKER_STORAGE_TIER_ASSOC` to interpret promotion.

### Risks
- Promotion semantics are hard-coded to tier ordinal 0.
- Static metric objects are process-wide; tests must reset metrics if they assert counts.

### Test Signals
`BlockWorkerMetricsTest` covers worker metrics gauges. Event counter behavior is indirectly exercised by block-store tests that register listeners and by metric integration tests.
