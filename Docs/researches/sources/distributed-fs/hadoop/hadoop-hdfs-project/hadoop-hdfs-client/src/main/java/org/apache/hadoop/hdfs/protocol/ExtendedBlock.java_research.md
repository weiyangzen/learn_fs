# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ExtendedBlock.java

## Purpose
`ExtendedBlock` identifies a block uniquely across block pools by pairing a block-pool ID with a local `Block` containing block ID, length, and generation stamp.

## APIs and Behavior
Constructors create empty, copied, pool+ID, pool+`Block`, or full block instances. Pool IDs are interned when non-null. Getters and setters delegate block fields, `set(poolId, blk)` replaces both fields, `getLocalBlock()` exposes the contained `Block`, and static `getLocalBlock()` handles null input. Equality compares the local block plus nullable pool ID; hash and `toString()` include both.

## State, Dependencies, and Integration
The class is mutable and wraps `Block`, used by block-location, write-pipeline, recovery, and DataNode transfer protocols. Persistence is external in block maps, edit logs, and DataNode storage.

## Risks and Test Signals
Because `getLocalBlock()` returns the mutable `Block`, callers can mutate identity after use in collections. Tests should cover equality/hash under mutation, null pool IDs, copy-constructor isolation, generation-stamp updates during pipeline recovery, and interning behavior where many blocks share pool IDs.
