<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/RegisterLeaseManagerTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/RegisterLeaseManagerTest.java

**Purpose:** Verifies `RegisterLeaseManager` acquisition, reuse, release, expiration, capacity limits, and non-JVM lease behavior.

**Important APIs/types/functions:** Uses `RegisterLeaseManager.tryAcquireLease`, `hasLease`, `releaseLease`, `GetRegisterLeasePRequest`, `RegisterLease`, and configuration keys `MASTER_WORKER_REGISTER_LEASE_COUNT`, `MASTER_WORKER_REGISTER_LEASE_TTL`, and `MASTER_WORKER_REGISTER_LEASE_RESPECT_JVM_SPACE`.

**Control flow:** `before` configures two concurrent leases, 3s TTL, and disables JVM-space checks. `acquireVerifyRelease` acquires a lease for worker 1, observes `hasLease`, releases, and verifies absence. `recycleExpiredLease` fills both lease slots, sleeps beyond TTL, then verifies workers 3 and 4 can acquire recycled leases and worker 5 is blocked. `findExistingLease` verifies repeat acquisition by the same worker returns a present lease without consuming another slot.

**State and persistence behavior:** All state is in the manager's in-memory lease table; there is no journal persistence. Expiration is time-based and lazy, occurring on later acquisition checks.

**Dependencies and integration points:** Integrates Alluxio configuration and gRPC lease requests. It is the core unit counterpart to handler-level lease enforcement tests.

**Risks:** Uses 5s sleeps for a 3s TTL, making the test slower and potentially flaky under severe scheduling delays. It does not cover enabled JVM-space rejection, because that is delegated to `JvmSpaceReviewerTest`.

**Test signals:** Expected signals are present optionals for allowed acquisitions, `hasLease` matching live lease ownership, absent optional when capacity is exhausted, and expired worker leases removed after recycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/RegisterLeaseManagerTest.java -->
