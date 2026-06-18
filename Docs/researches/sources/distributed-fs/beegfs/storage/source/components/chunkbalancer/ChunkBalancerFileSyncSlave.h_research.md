## sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerFileSyncSlave.h

### Purpose
`ChunkBalancerFileSyncSlave.h` declares the concrete `ChunkFileResyncer` used by `ChunkBalancerJob`. It specializes generic resync for chunk migration and metadata stripe update workflows.

### Important APIs, Types, And Functions
The class constructor accepts a target ID, shared candidate store, and slave ID. It overrides `syncLoop()` and `getFD()`, and declares helpers `removeChunk()` and `sendRemoveChunkPathsMessage()`. State includes the shared `ChunkSyncCandidateStore*`, current `targetID`, and `isBuddyMirrorChunk`.

### Control Flow, State, And Persistence
The `isBuddyMirrorChunk` flag controls whether the inherited copy uses the mirror FD or normal chunk FD and whether remote removal is flagged as buddy mirror removal. The header exposes only vector typedefs to owners; lifecycle and counters come from the base class.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on sync candidates, BeeGFS storage errors/threading, and `ChunkFileResyncer`. `ChunkBalancerJob` is a friend because it manages worker internals. Risks include per-candidate mutable `isBuddyMirrorChunk` affecting inherited operations and no public ownership abstraction around the raw candidate-store pointer. Tests should validate FD selection and helper behavior for mirrored and non-mirrored candidates.
