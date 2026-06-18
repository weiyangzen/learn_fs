# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LocatedBlock.java

## Purpose
`LocatedBlock` associates an `ExtendedBlock` with replica locations, storage IDs/types, cached locations, file start offset, corruption status, and a block access token.

## APIs and Control Flow
Constructors convert `DatanodeInfo[]` to `DatanodeInfoWithStorage[]`, defaulting offset to `-1` and no corruption. Accessors expose block token, block, locations, storage arrays, offset, block size, corruption flag, and cached locations. `updateCachedStorageInfo()` synchronizes storage arrays after location mutation. `moveProvidedToEnd(activeLen)` stable-sorts provided-storage replicas after normal storage. `addCachedLoc()` avoids duplicates, reuses an existing located DataNode object when possible, and requires a backing disk replica for cached-only additions. `isStriped()` and `getBlockType()` default to contiguous.

## State, Dependencies, and Integration
The class is mutable and central to read/write pipeline setup, token authorization, DataNode selection, and block reports returned by `ClientProtocol`. It depends on `StorageType`, `Token<BlockTokenIdentifier>`, `DatanodeInfoWithStorage`, and utility collection/precondition helpers.

## Risks and Test Signals
Returned location arrays are mutable by contract, but callers must remember to update cached storage arrays. Constructor conversion assumes storage arrays are at least as long as the locations array when non-null. Tests should cover provided-storage ordering, cached-location duplicate handling, storage array sync after mutation, null location handling, corrupt flag filtering expectations, token set/get, and subclass behavior for striped blocks.
