## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/PinListSyncTest.java

**Purpose:** Tests synchronization of pinned inode lists from the file-system master into the block worker.

**Important APIs:** Exercises `PinListSync`, `FileSystemMasterClient.getPinList`, and `BlockWorker.updatePinList`.

**Control flow:** The test uses a temporary folder/rule fixture, mocks a file-system master client returning a pin set, constructs the sync task with a block worker, runs the heartbeat/sync method, and verifies the worker receives the exact set.

**State and persistence:** No durable state. Runtime state is the pin set returned by the master client and the worker's update call.

**Dependencies and integration:** Integrates worker heartbeat-side synchronization with file-system master metadata and block eviction protection. Often paired indirectly with `BlockMetadataEvictorView` tests that enforce pinned-block filtering.

**Risks:** Missed or stale pin-list updates could let eviction remove blocks for pinned files. Error handling is important because master calls are remote and can fail in production.

**Test signals:** Focused signal that the sync task delegates master pin data to the block worker update hook.
