## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerGatherSlave.h

### Purpose
`BuddyResyncerGatherSlave.h` declares the candidate discovery worker and its bounded work queue for buddy resync. It separates path scheduling from filesystem traversal.

### Important APIs, Types, And Functions
`BuddyResyncerGatherSlaveWorkQueue` offers `add()`, `fetch()`, `queueEmpty()`, and `clear()` with a `GATHERSLAVEQUEUE_MAXSIZE` backpressure limit. `BuddyResyncerGatherSlave` exposes `run()`, static `handleDiscoveredEntry()`, `getCounters()`, running-state accessors, and idle-only termination controls.

### Control Flow, State, And Persistence
The queue stores pending scan roots in a `StringList`, tracks length separately to avoid repeated `size()`, and uses two condition variables: one for path arrival and one for fetch completion. Worker state includes atomics for discovered/matched chunks and directories, a static mutex-protected map from thread names to workers for `nftw`, and a reference to the target being scanned.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on BeeGFS logging/threading, sync candidates, and POSIX `ftw.h`. Owners rely on friend access for shutdown waiting. Risks include lock contention/backpressure when many paths are enqueued and static worker-map lifetime. Tests should validate queue blocking/unblocking, termination while waiting, counter snapshots, and callback routing to the correct worker.
