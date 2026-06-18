## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/ChunkFileResyncer.h

### Purpose
`ChunkFileResyncer.h` declares the abstract base thread for copying chunk files between storage targets. It centralizes lifecycle, counters, and copy/removal helpers shared by buddy resync and chunk balancing workers.

### Important APIs, Types, And Functions
The `ChunkFileResyncerMode` enum distinguishes buddy mirror copy, normal chunk balance copy, and mirrored chunk balance copy. Subclasses must implement `syncLoop()` and `getFD()`. Protected helpers are `doResync()` and `removeChunkUnlocked()`. Public methods expose idle-only termination, synced chunk count, error count, and running status.

### Control Flow, State, And Persistence
The class owns status synchronization (`statusMutex`, `isRunningChangeCond`), atomic counters, target identifiers, a path string, and an FD field used during copy. Persistence is not in the header itself, but the abstract `getFD()` decides whether copy reads from normal or mirror chunk storage.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on BeeGFS node, storage error, thread, and storage target abstractions. Friend classes (`BuddyResyncer`, `BuddyResyncJob`, `ChunkBalancerJob`) coordinate worker lifecycle. Risks include subclasses sharing mutable base fields, `getIsRunning()` returning `uint64_t` despite exposing a boolean, and mode flag naming that maps enum values to message flags indirectly. Tests should validate subclass mode behavior, status signaling, and counter reset on `run()`.
