## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerFileSyncSlave.h

### Purpose
`BuddyResyncerFileSyncSlave.h` declares the buddy resync file worker as a concrete `ChunkFileResyncer`. It specializes the generic chunk copy primitive for the mirror directory of a local target.

### Important APIs, Types, And Functions
The class exposes a constructor/destructor and overrides `syncLoop()` plus `getFD()`. It stores a `ChunkSyncCandidateStore*` supplied by the resync job. Typedefs provide list and vector containers for owners managing multiple workers.

### Control Flow, State, And Persistence
Most state and counters live in `ChunkFileResyncer`; this header adds only the shared queue pointer. The overridden `getFD()` is the key persistence boundary because it chooses whether the base reads from normal chunks or the mirror directory.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `SyncCandidateStore`, storage errors, BeeGFS threading, and `ChunkFileResyncer`. Friend access lets `BuddyResyncer` and `BuddyResyncJob` coordinate worker shutdown. Tests should focus on correct FD selection and base-class status/counter behavior when running as a buddy mirror worker.
