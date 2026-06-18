<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Locks.hh -->
# sources/distributed-fs/eos/mgm/FuseServer/Locks.hh

Purpose: Declares `FuseServer::Lock`, the mutex-protected inode-to-lock-tracker map used by FUSE server code to coordinate POSIX-style locks held by eosxd clients.

Important APIs/types/functions: `shared_locktracker` aliases `std::shared_ptr<LockTracker>`, and `lockmap_t` maps inode IDs to trackers. Public APIs are `getLocks()`, `purgeLocks()`, two overloads of `dropLocks()`, and `lsLocks()`.

Control flow: The implementation lazily materializes trackers and performs coarse locking around map operations. Actual read/write lock ownership details are delegated to `LockTracker`, while this wrapper handles object lookup and lifecycle.

State and persistence behavior: `lockmap` is in-memory only and should reflect live client/session state. Empty trackers are purged after removals to keep memory bounded.

Dependencies and integration points: Includes `mgm/Namespace.hh`, `mgm/fuse-locks/LockTracker.hh`, `<map>`, `<memory>`, and XRootD mutex wrappers. It is exposed through the FUSE server singleton and used by heartbeat eviction, admin lock drop commands, and client diagnostics.

Risks: The class privately inherits `XrdSysMutex`, which makes lock ownership implicit. Returning shared trackers allows work outside the map mutex; tests must depend on `LockTracker` behavior as well as this wrapper. Test signals include tracker reuse for the same inode, independent trackers for different inodes, purge behavior, owner-wide drop, and list output separation between read/write lock maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Locks.hh -->
