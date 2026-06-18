## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/PinListSync.java

### Purpose
`PinListSync` is a heartbeat executor that periodically fetches pinned file ids from the file-system master and updates the block worker’s pin list so eviction avoids pinned file blocks.

### Important APIs and Types
- Constructor takes `BlockWorker` and `FileSystemMasterClient`.
- `heartbeat(long)` calls `getPinList()` and `updatePinList`.
- `close()` is a no-op.

### Control Flow
Each heartbeat requests the current pin list from the master. On success it updates the worker. Exceptions are logged at warn/debug and do not propagate, allowing later heartbeats to retry.

### State and Persistence
No internal mutable state beyond dependencies. The persistent effect is indirect: updated in-memory pin set in the block store, which affects future eviction.

### Dependencies and Integration Points
Started by `DefaultBlockWorker.start` in a heartbeat thread. Feeds `TieredBlockStore.updatePinnedInodes`, which is read by `BlockMetadataEvictorView`.

### Risks
- A failed heartbeat leaves the previous pin list in effect, which can either over-protect old pins or fail to protect new pins until the next successful sync.
- It fetches the complete pin list each time; large pin sets can create memory/serialization pressure.

### Test Signals
`PinListSyncTest` covers successful update and exception-tolerant heartbeat behavior.
