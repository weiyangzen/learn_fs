<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/meta/MasterWorkerInfoTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/meta/MasterWorkerInfoTest.java

**Purpose:** Unit-tests `MasterWorkerInfo`, the master-side model for worker capacity, usage, storage tiers, block membership, remove queues, and wire report generation.

**Important APIs/types/functions:** Covers `register`, `getFreeBytesOnTiers`, `addBlock`, `removeBlockFromWorkerMeta`, `generateWorkerInfo`, `updateToRemovedBlock`, `updateUsedBytes(Map)`, and `updateUsedBytes(String,long)`. Uses `StorageTierAssoc`, `DefaultStorageTierAssoc`, `WorkerInfo`, `WorkerState`, and `GetWorkerReportOptions.WorkerInfoField.ALL`.

**Control flow:** `before` registers a worker with MEM and SSD tiers, total and used bytes, and blocks 1 and 2. Tests verify registration-derived totals, free bytes, re-registration returning removed blocks, tier-count validation exception text, add/remove block idempotency, wire report fields, to-remove block queue behavior, and usage recalculation by map or tier.

**State and persistence behavior:** The test mutates only the `MasterWorkerInfo` object. It verifies derived aggregate state such as total capacity, total used bytes, per-tier free bytes, current block set, and to-remove set. No journal or master registry is involved.

**Dependencies and integration points:** Integrates Alluxio constants, storage tier association, worker report options, and wire `WorkerInfo`. The object under test is consumed by `DefaultBlockMaster` worker reports and heartbeat command generation.

**Risks:** Does not cover concurrent updates even though worker metadata is accessed by concurrent master paths. It validates an exact exception message for tier mismatch, which can be brittle under wording changes.

**Test signals:** Expected signals include exact maps for total/used/free tier bytes, aggregate byte counts, removed block set after re-register, matching `WorkerInfo` fields, empty to-remove set after block removal, and updated used bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/meta/MasterWorkerInfoTest.java -->
