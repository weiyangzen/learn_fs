<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/JvmSpaceReviewerTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/JvmSpaceReviewerTest.java

**Purpose:** Unit-tests `JvmSpaceReviewer`, which gates worker register leases based on estimated JVM memory available for processing a requested number of blocks.

**Important APIs/types/functions:** Uses `JvmSpaceReviewer.reviewLeaseRequest`, `JvmSpaceReviewer.BLOCK_COUNT_MULTIPLIER`, `Runtime.maxMemory/freeMemory/totalMemory`, and `GetRegisterLeasePRequest`.

**Control flow:** The test mocks runtime memory so available space is effectively 1000 bytes, computes `maxBlocks` from available bytes divided by `BLOCK_COUNT_MULTIPLIER`, and validates three requests: zero blocks accepted, exactly max accepted, max plus one rejected.

**State and persistence behavior:** Pure in-memory unit test with no master or journal state. It constructs unused metric gauges, but the active reviewer instance is driven by mocked `Runtime`.

**Dependencies and integration points:** Depends on Mockito, Dropwizard metric types, and Alluxio gRPC lease request messages. It represents the JVM-space branch used by `RegisterLeaseManager` when `MASTER_WORKER_REGISTER_LEASE_RESPECT_JVM_SPACE` is enabled.

**Risks:** The mocked `MetricRegistry` is not passed into the reviewer and may be vestigial; future reviewer implementation changes that use metrics could make this test incomplete. It validates only threshold boundaries and not negative/overflow memory values.

**Test signals:** `reviewLeaseRequest` returns true for zero and boundary block counts and false when requested blocks exceed estimated available memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/JvmSpaceReviewerTest.java -->
