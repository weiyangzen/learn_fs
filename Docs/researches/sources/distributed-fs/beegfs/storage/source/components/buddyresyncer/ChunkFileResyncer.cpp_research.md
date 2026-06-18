## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/ChunkFileResyncer.cpp

### Purpose
`ChunkFileResyncer.cpp` implements the reusable block-wise chunk copy engine used by buddy resync and chunk balancing. It reads a local chunk file, sends `ResyncLocalFileMsg` blocks to a destination target, handles sparse regions and final attributes, and optionally removes a stale destination chunk when the source disappeared.

### Important APIs, Types, And Functions
`run()` manages thread lifecycle and counters, while concrete subclasses implement `syncLoop()` and `getFD()`. `doResync()` is the copy workhorse. It resolves the destination node, locks the local chunk by basename, opens the chunk with `openat()`, reads up to `SYNC_BLOCK_SIZE`, detects sparse blocks using `RESYNCER_SPARSE_BLOCK_SIZE`, sends `ResyncLocalFileMsg`, and retries while the destination target is not offline. `removeChunkUnlocked()` sends `RmChunkPathsMsg` for missing chunks.

### Control Flow, State, And Persistence
The copy loop advances `offset` until a short read or error. At the last block it uses `fstat()` to attach mode, owner, group, mtime, and atime, and sets truncation flags if a concurrent truncate makes the logical size smaller. Persistent effects occur on the destination target through network messages; local state is chunk locks, file descriptors, offsets, and counters.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include target/node mappers, `ChunkLockStore`, storage target FDs, `MessagingTk`, and resync message types. Risks include `goto` cleanup paths, offset arithmetic when `readRes` is negative, sparse detection only by fixed zero-block comparisons, retry loops during shutdown, and concurrent local truncation/deletion. Tests should cover missing source behavior in buddy versus balancing modes, sparse chunks, short reads, final attribute propagation, destination offline state, and chunk lock release on every path.
