## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeLayoutSubLockStrategy.java

Purpose: implements `DataSetSubLockStrategy` using the DataNode block-ID-based directory layout. It maps a block ID to the subdirectory suffix that should guard that block in the dataset lock hierarchy.

Important APIs and functions: `blockIdToSubLock(long blockid)` delegates to `DatanodeUtil.idToBlockDirSuffix(blockid)`. `getAllSubLockNames()` delegates to `DatanodeUtil.getAllSubDirNameForDataSetLock()`.

Control flow: callers provide a block ID when they need a directory-level dataset sub-lock. The strategy computes the same 32-by-32 layout suffix used by on-disk block placement, allowing lock partitioning to align with actual finalized block directories. The all-names method returns the complete set of subdirectory lock names needed to pre-create or iterate all directory-level locks.

State and persistence: stateless. It has no fields and persists nothing. Its correctness is tied to the deterministic `DatanodeUtil` block directory mapping and the DataNode layout version that uses block-ID-based directories.

Dependencies and integration points: implements `DataSetSubLockStrategy` and integrates with lock managers or dataset code that need to convert block IDs into lock-resource names. It depends on `DatanodeUtil`, which is also used by storage layout code, so it avoids divergent lock names.

Risks: if `DatanodeUtil` layout mapping changes without a corresponding migration or lock strategy update, directory-level locking could protect the wrong partition. Returning all names must remain consistent with `blockIdToSubLock`; otherwise pre-created locks can miss active block directories.

Test signals: targeted tests should compare representative block IDs, boundary IDs, and the complete name list against the actual DataNode directory layout and `DataStorage` block-ID layout upgrade output.
