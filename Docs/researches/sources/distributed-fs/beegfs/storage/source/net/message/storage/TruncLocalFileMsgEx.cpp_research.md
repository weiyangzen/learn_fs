## sources/distributed-fs/beegfs/storage/source/net/message/storage/TruncLocalFileMsgEx.cpp

### Purpose
`TruncLocalFileMsgEx.cpp` handles chunk truncation and extension requests. It supports normal and buddy-mirrored chunks, creates missing chunks when extending, forwards primary mirror operations to the secondary, and returns dynamic attributes with storage versions.

### Important APIs, Types, And Functions
`processIncoming()` resolves target IDs and FDs, validates mirrored consistency through `getTargetFD()`, forwards to secondary with `forwardToSecondary()`, builds chunk paths via `StorageTk::getChunkDirChunkFilePath()`, calls `truncFile()`, and returns `TruncLocalFileRespMsg`. `truncFile()` uses `MsgHelperIO::truncateAt()`, creates missing files through `ChunkStore::openChunkFile()` with quota info, retries chmod for quota owner issues, and calls `ftruncate()`. Attribute helpers use `SyncedStoragePaths`.

### Control Flow, State, And Persistence
For mirrored primary requests, the message is reused with the secondary flag set. If the secondary is offline or reports unknown target, local truncation proceeds and the target is marked needing resync. If buddy resync is in progress, the chunk is locked around forwarding/local work. Persistent effects include truncating or creating chunk files, setting buddy-needs-resync, and possible quota-aware directory/file creation.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include storage targets, mirror mappers, target states, chunk store, quota stores, synchronized paths, and `MessagingTk`. Risks include reused message mutation, complex response suppression for `GenericResponseMsg`, lock release on all branches, zero-size missing-file fake attributes, and partial success when secondary differs from primary. Tests should cover normal shrink/extend, missing zero-size truncation, create-and-truncate, quota errors, mirrored secondary online/offline/unknown, non-good primary consistency, resync chunk locking, and dynamic attribute storage versions.
