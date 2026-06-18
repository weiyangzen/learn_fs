<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestLocatedBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestLocatedBlock.java

Purpose: Verifies `LocatedBlock.addCachedLoc` rejects cached locations when the block has no storage locations.

Important APIs/types/functions: `LocatedBlock`, `ExtendedBlock`, `DatanodeInfo.EMPTY_ARRAY`, `DatanodeDescriptor`, and `DatanodeID`.

Control flow: Single test constructs a `LocatedBlock` with an empty location array, creates a `DatanodeDescriptor`, calls `addCachedLoc`, and expects `IllegalArgumentException`.

State and persistence behavior: In-memory protocol object only.

Dependencies and integration points: Guards client/protocol block-location invariants used by cache reporting and block metadata propagation.

Risks: The test uses manual try/fail rather than `assertThrows`, but behavior is clear. It only covers the empty-location error path.

Test signals: Passing means cached locations cannot be attached to a `LocatedBlock` lacking base datanode locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestLocatedBlock.java -->
