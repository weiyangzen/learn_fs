<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Locks.cc -->
# sources/distributed-fs/eos/mgm/FuseServer/Locks.cc

Purpose: Implements the FUSE lock registry wrapper that maps inodes to `LockTracker` instances and provides cleanup/listing operations by PID or client owner.

Important APIs/types/functions: `getLocks(id)` lazily creates and returns the shared `LockTracker` for an inode. `purgeLocks()` removes trackers whose `inuse()` is false. `dropLocks(id, pid)` removes locks for a process on one inode. `dropLocks(owner)` removes all locks owned by a client UUID/string across all inodes. `lsLocks(owner, rlocks, wlocks)` gathers read/write PID sets for diagnostics.

Control flow: Each method uses `XrdSysMutexHelper` to protect `lockmap`. Drop methods mutate trackers under lock, release the lock, then call `purgeLocks()` to clean empty trackers. Listing iterates every inode tracker and merges owner-specific read/write locks into caller-provided maps.

State and persistence behavior: `lockmap` is volatile and process-local: `inode -> shared LockTracker`. Lock state is not persisted; it is tied to live eosxd client sessions and is dropped during offline/eviction paths in `Clients.cc`.

Dependencies and integration points: Depends on `mgm/fuse-locks/LockTracker.hh`, XRootD mutex helpers, and MGM logging. `Clients::MonitorHeartBeat()` drops all locks for offline/evicted UUIDs, admin `Fusex` commands can drop inode/PID locks, and `Clients::Print("k")` lists locks per client.

Risks: `getLocks()` returns a shared tracker after releasing the wrapper lock, so correctness depends on `LockTracker`'s own synchronization and lifetime behavior. `lsLocks()` creates empty entries in output maps even when no locks exist for an inode. `dropLocks(owner)` always returns 0 even if no locks matched. Tests should cover lazy creation, purge after last lock removal, owner-wide eviction cleanup, concurrent get/drop, and diagnostics for clients with no locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Locks.cc -->
