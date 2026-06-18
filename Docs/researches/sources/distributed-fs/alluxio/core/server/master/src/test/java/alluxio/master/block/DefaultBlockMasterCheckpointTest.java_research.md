<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/DefaultBlockMasterCheckpointTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/DefaultBlockMasterCheckpointTest.java

**Purpose:** Verifies `DefaultBlockMaster` checkpoint write and restore paths for both stream-based and directory-based checkpoint APIs, across heap and RocksDB-backed block metastores.

**Important APIs/types/functions:** Parameterizes over `MetastoreType.HEAP` and `MetastoreType.ROCKS`. Uses `writeToCheckpoint(OutputStream)`, `restoreFromCheckpoint(CheckpointInputStream)`, `writeToCheckpoint(File, ExecutorService)`, `restoreFromCheckpoint(File, ExecutorService)`, `processJournalEntry`, `getJournaledNextContainerId`, and `getBlockInfo`.

**Control flow:** `before` sets `MASTER_BLOCK_METASTORE`, constructs a fresh block master with block and inode store factories, replays journal entries for next container id, two block infos, and a delete for block 1. `testOutputStream` writes a checkpoint to a temp file, restores into a new master, and checks generator and block state. `testDirectory` performs the same validation through the asynchronous directory checkpoint API with a single-thread executor.

**State and persistence behavior:** This is a persistence-focused test. It confirms that checkpoint state includes the next container id and live block 2 length, but excludes deleted block 1. It verifies journal-derived in-memory state is serialized in a way compatible with both metastore implementations.

**Dependencies and integration points:** Uses `MasterTestUtils`, `MasterUtils.getBlockStoreFactory`, `MasterUtils.getInodeStoreFactory`, `NoopJournalSystem`, `MetricsMasterFactory`, checkpoint streams, and Alluxio journal protobuf entries.

**Risks:** Executor shutdown is not explicit in `testDirectory`, so future executor lifecycle changes could leave resource warnings. The test covers only a tiny block metadata set and one delete edge, not worker-location checkpointing or large checkpoints.

**Test signals:** Restored master reports `mNextContainerId`, throws `BlockInfoException` for deleted block 1, and returns block 2 with persisted length `mBlockLength`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/DefaultBlockMasterCheckpointTest.java -->
