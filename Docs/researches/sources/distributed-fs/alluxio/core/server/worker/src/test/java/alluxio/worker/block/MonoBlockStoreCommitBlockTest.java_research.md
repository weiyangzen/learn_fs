## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/MonoBlockStoreCommitBlockTest.java

**Purpose:** Tests commit event ordering and failure boundaries in `MonoBlockStore.commitBlock`, where local commit and master commit are separate domains.

**Important APIs:** Exercises `MonoBlockStore.commitBlock`, `TieredBlockStore.commitBlockInternal`, `BlockMasterClient.commitBlock`, `registerBlockStoreEventListener`, and listener callbacks `onCommitBlockToLocal` and `onCommitBlockToMaster`.

**Control flow:** Setup builds metadata, lock manager, mocked block master client/pool, a test storage dir, and a spied event listener. `prepareBlockStore` creates a temp block, writes data through a block writer, and registers the listener. Tests cover both commits succeeding, master commit failing after local commit, and local commit failing before master notification.

**State and persistence:** Creates a real temp block file and updates local metadata. Master state is mocked; event listener invocations are the main observable side effect.

**Dependencies and integration:** Depends on `TieredBlockStoreTestUtils`, `BlockWriter`, `UfsManager`, `AtomicReference` worker ID, Mockito answers, and Alluxio status exceptions.

**Risks:** Incorrect listener ordering can cause heartbeat/reporting inconsistencies. A master failure after local commit leaves local state changed but should not emit a master-commit event.

**Test signals:** Focused coverage of local/master commit callback semantics under success and both failure points.
