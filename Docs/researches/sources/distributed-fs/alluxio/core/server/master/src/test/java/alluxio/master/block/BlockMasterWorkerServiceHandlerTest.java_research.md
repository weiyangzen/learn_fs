<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterWorkerServiceHandlerTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterWorkerServiceHandlerTest.java

**Purpose:** Exercises `BlockMasterWorkerServiceHandler`, the gRPC-facing worker service wrapper around `BlockMaster`, with emphasis on register-lease enforcement and validation of duplicate block locations in register and heartbeat requests.

**Important APIs/types/functions:** The fixture creates `DefaultBlockMaster`, `MetricsMaster`, `MasterRegistry`, `ManualClock`, and `BlockMasterWorkerServiceHandler`. It builds `RegisterWorkerPRequest`, `BlockHeartbeatPRequest`, `LocationBlockIdListEntry`, `BlockIdList`, `BlockStoreLocationProto`, and `GetRegisterLeasePRequest` messages. Test methods cover `registerWorker`, `blockHeartbeat`, `tryAcquireRegisterLease`, and `releaseRegisterLease`.

**Control flow:** `before` calls `initServiceHandler(true)`, enabling one register lease with a 3s TTL and disabling JVM-space gating. `registerWithNoLeaseIsRejected` sends a valid-looking registration without acquiring a lease and records the observer error. `registerWorkerFailsOnDuplicateBlockLocation` creates two `LocationBlockIdListEntry` values with the same location key, acquires a lease sized to both lists, and expects an `AssertionError`. `registerLeaseExpired` acquires a lease, waits past TTL, lets another worker acquire the recycled lease, then verifies the original registration is rejected. `registerLeaseTurnedOff` rebuilds the handler with leases disabled and verifies registration succeeds without a lease. `workerHeartbeatFailsOnDuplicateBlockLocation` sends duplicate added-block locations in heartbeat and expects an assertion.

**State and persistence behavior:** Tests run against `NoopJournalSystem`; they validate in-memory lease table and worker/block registration behavior rather than durable journal recovery. The lease tests mutate global `Configuration` keys and live master state; teardown stops the registry.

**Dependencies and integration points:** Integrates gRPC proto request/response types, `StreamObserver`, Alluxio configuration, `RegisterLease`, `BlockStoreLocation`, and the master registry lifecycle. It verifies handler-level request validation before worker state reaches normal block metadata paths.

**Risks:** Uses `SleepUtils.sleepMs(5000)` for TTL expiry, so it is wall-clock-sensitive. Duplicate-location behavior is asserted as Java `AssertionError`, so behavior depends on assertions being enabled in the test runtime or on implementation throwing assertion errors explicitly. Global configuration mutations can leak if test isolation fails.

**Test signals:** Strong signals are rejection message containing "does not have a lease or the lease has expired", empty error queue when leases are disabled, and assertion failures for duplicate block location maps in both registration and heartbeat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterWorkerServiceHandlerTest.java -->
