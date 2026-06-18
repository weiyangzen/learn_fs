<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/meta/BlockContainerIdGeneratorTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/meta/BlockContainerIdGeneratorTest.java

**Purpose:** Unit-tests monotonic ID generation for `BlockContainerIdGenerator`.

**Important APIs/types/functions:** Uses `BlockContainerIdGenerator.getNewContainerId` and `setNextContainerId`.

**Control flow:** `before` creates a fresh generator. `getNewContainerId` asserts the default sequence starts at 0 and increments to 1 and 2. `setNextContainerId` resets next id to `TEST_ID` and verifies subsequent calls return `TEST_ID`, `TEST_ID + 1`, and `TEST_ID + 2`.

**State and persistence behavior:** Tests only in-memory next-id state. Persistence is covered indirectly by `DefaultBlockMasterCheckpointTest`, which verifies journaled next container id restoration.

**Dependencies and integration points:** Simple JUnit unit test with no master lifecycle. It guards a primitive used by block id/container allocation and journaling.

**Risks:** Does not test invalid reset values, overflow, concurrent access, or journal serialization. It assumes sequential single-threaded usage.

**Test signals:** Exact id sequence values demonstrate initial state and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/meta/BlockContainerIdGeneratorTest.java -->
