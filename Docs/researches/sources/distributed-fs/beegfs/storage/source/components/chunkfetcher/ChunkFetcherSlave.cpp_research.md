## sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcherSlave.cpp

### Purpose
`ChunkFetcherSlave.cpp` implements one fsck chunk walker per storage target. It recursively scans normal chunk directories and, when this target is the primary of a buddy group, the buddy mirror directory.

### Important APIs, Types, And Functions
`run()` sets running state, registers signal handling, and calls `walkAllChunks()`. `walkAllChunks()` finds the target path, walks `chunks`, determines primary buddy status, and optionally walks `buddymirror` with the buddy group ID. `walkChunkPath()` recursively uses `opendir`, `readdir`, `stat`, and directory recursion; file entries are converted to `FsckChunk` objects and queued through `ChunkFetcher::addChunk()`.

### Control Flow, State, And Persistence
For each file, the relative chunk path is derived from `basePathLen`, `dirname()` supplies the saved path, and stat fields populate size, blocks, ctime, mtime, atime, uid, gid, target ID, and buddy group ID. `ENOENT` after `readdir()` is ignored to tolerate online deletions. The worker sets the fetcher's bad flag on open/stat/read failures or termination.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include POSIX directory APIs, `StorageTargets`, `MirrorBuddyGroupMapper`, `FsckChunk`, and `ChunkFetcher`. Risks include recursion depth, symlink/stat behavior, deprecated `readdir_r` path handling, allocation from `strdup()`, and marking termination as bad. Tests should cover normal and mirrored traversal, online delete races, unreadable directories, recursive paths, queue backpressure, and buddy group ID population.
