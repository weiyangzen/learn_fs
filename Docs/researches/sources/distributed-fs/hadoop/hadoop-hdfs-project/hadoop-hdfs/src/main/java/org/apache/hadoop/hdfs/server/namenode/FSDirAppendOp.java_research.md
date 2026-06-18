# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirAppendOp.java

## Purpose
`FSDirAppendOp` implements the namespace side of appending to existing HDFS files. It validates append eligibility, recovers or establishes a lease, converts the file to under construction, handles last-block behavior, updates quota usage, and logs the append/open operation.

## Important APIs and Types
The static APIs are `appendFile` and `prepareFileForAppend`; private helpers verify and compute quota delta for converting a complete block to under construction. The class uses `FSNamesystem`, `FSDirectory`, `INodesInPath`, `INodeFile`, `BlockManager`, `BlockInfo`, `LocatedBlock`, `QuotaCounts`, and `NameNodeLayoutVersion.Feature.APPEND_NEW_BLOCK`.

## Control Flow
`appendFile` asserts the global write lock, takes the FSDirectory write lock, resolves the path, rejects directories and missing files, enforces write permission, rejects EC append without `NEW_BLOCK`, rejects lazy-persist files, recovers the lease, checks the last block's replication/UC state, then calls `prepareFileForAppend`. `prepareFileForAppend` verifies quota for a preferred-size UC block, records modification, converts the file to under construction, adds a lease, either converts the last block to UC or returns the last complete block when appending with a new block, updates quota counts if needed, and logs `logAppendFile` or legacy `logOpenFile`.

## State and Persistence
Persistent state changes include inode under-construction state, lease manager state, block UC conversion, quota cache updates, and edit-log records. During edit-log loading, quota checks may be skipped because the image is not fully loaded.

## Dependencies and Integration
It integrates with block management, lease recovery, FSDirectory locking, quota verification, storage policy suite, edit logs, retry cache logging, and client protocol append semantics.

## Risks and Test Signals
Append behavior differs for striped EC files and older layout versions. Quota delta assumes preferred block size minus current last-block size; appending to an over-preferred block is guarded by a state check when quota is updated. Tests should cover missing path, directory path, permission denial, EC append with/without new block, lazy-persist rejection, COMMITTED last-block retriable failure, insufficient replication, quota update for partial block, retry-cache edit logging, and legacy layout fallback.
