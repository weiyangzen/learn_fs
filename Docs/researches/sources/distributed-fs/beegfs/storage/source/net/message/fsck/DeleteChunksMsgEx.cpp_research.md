## sources/distributed-fs/beegfs/storage/source/net/message/fsck/DeleteChunksMsgEx.cpp

### Purpose
`DeleteChunksMsgEx.cpp` handles fsck-driven deletion of chunk files from storage targets. It removes requested chunks and reports which deletions failed.

### Important APIs, Types, And Functions
`processIncoming()` iterates over `FsckChunkList` from `getChunks()`, builds `<savedPath>/<chunkID>`, resolves the target, selects mirror or normal FD based on `buddyGroupID`, calls `unlinkat()`, optionally prunes the empty chunk directory through `ChunkStore::rmdirChunkDirPath()`, and responds with `DeleteChunksRespMsg`.

### Control Flow, State, And Persistence
Unknown targets and unlink failures other than `ENOENT` add the chunk to `failedDeletes`. `ENOENT` is considered already deleted. Successful unlink is persistent and may be followed by directory cleanup.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on fsck message types, `StorageTargets`, `ChunkStore`, and target directory FDs. Risks include deleting mirrored chunks based only on buddy group ID presence, path construction from fsck-provided saved paths, and online races. Tests should cover unknown targets, normal and mirrored deletion, `ENOENT`, unlink errors, failed directory pruning tolerance, and response failure lists.
