## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncer.h

Purpose: Declares the storage buddy resync controller.

Important APIs/types/functions: `startResync(uint16_t)` starts a job for a target. `getResyncJob(uint16_t)` returns an existing job under lock. Private `addResyncJob()` creates or returns a job while reporting whether it is new.

Control flow: Map operations are protected by `resyncJobMapMutex`. The class itself is not a thread component; jobs are thread components.

State and persistence: Maintains only in-memory job map. Persistent resync effects are delegated to `BuddyResyncJob` and `StorageTarget`.

Dependencies and integration: Included by `App` and `InternodeSyncer`; depends on `BuddyResyncJob`.

Risks and test signals: Raw pointers require careful destructor cleanup and make ownership non-obvious. Tests should cover map locking under concurrent job lookup/start and no duplicate running jobs per target.
