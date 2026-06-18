## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncer.cpp

Purpose: Implements the frontend that starts and cleans up per-target buddy resync jobs.

Important APIs/types/functions: Destructor aborts and joins running jobs before deleting all jobs. `startResync(uint16_t)` obtains or creates a `BuddyResyncJob`, rejects if the existing job is running, otherwise starts it.

Control flow: `startResync()` calls `addResyncJob()`, checks `isNewJob` and `isRunning()`, starts the job thread, and returns `SUCCESS` or `INUSE`.

State and persistence: Owns an in-memory map of target ID to job. Resync job objects handle persistent target state.

Dependencies and integration: Uses `BuddyResyncJob` and is owned by `App`. Called by internode sync logic when mgmtd marks a buddy target `NEEDS_RESYNC`.

Risks and test signals: Completed jobs remain in the map and may be restarted; this depends on `BuddyResyncJob::run()` supporting repeated runs. Tests should cover repeated start after success/failure, destructor with running jobs, and concurrent `startResync()` calls.
