## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncJob.h

Purpose: Declares the storage buddy resync job thread and its coordination state.

Important APIs/types/functions: `BuddyResyncJob` derives from `PThread`, exposes `run()`, `abort()`, `getJobStats()`, `getTargetID()`, `getStatus()`, `isRunning()`, and `setTargetOffline()`. Private methods walk directories, start/join slaves, set status, and inform the buddy. Defines `GATHERSLAVEQUEUE_MAXSIZE` and `BuddyResyncJobMap`.

Control flow: Header inline methods lock status for reads and writes; `setTargetOffline()` atomically marks offline observation for the running job.

State and persistence: Holds target ID, status mutex/status, timing, sync candidate structures, slave vectors, counters, abort flag, and target-offline flag. Persistence is mediated by cpp through storage target state.

Dependencies and integration: Includes resync gather/file/dir slave headers and buddy resync stats type. Owned by `BuddyResyncer` and observed by debug/status message paths.

Risks and test signals: `GenericDebugMsgEx` friendship exposes internals for debugging. Tests should verify status locking and `setTargetOffline()` influence final job state.
