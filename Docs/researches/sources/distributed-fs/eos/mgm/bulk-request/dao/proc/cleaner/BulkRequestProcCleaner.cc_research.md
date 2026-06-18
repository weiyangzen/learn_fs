## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleaner.cc

Purpose: implements a background assisted thread that periodically removes stale proc-directory bulk requests.

Important flow: `Start()` resets the assisted thread; `Stop()` joins it. `backgroundThread()` logs startup, waits for namespace boot, waits until this MGM becomes master, then loops until termination. On each interval, if still master, it creates a `ProcDirectoryDAOFactory`, gets an `IBulkRequestDAO`, calls `deleteBulkRequestNotQueriedFor(PREPARE_STAGE, configured age)`, and logs deletion counts. `IntervalStopwatch` and five-second waits make sleep interruptible.

State/dependencies: depends on global `gOFS`, `IMaster`, proc locations, cleaner config, DAO factory, and `PersistencyException`. Risks include global pointer reliance, only cleaning `PREPARE_STAGE`, repeated DAO construction, waiting for master before main loop but not handling long slave periods except by skipping work, and destructor calling `Stop()`. Tests should cover start/stop idempotence, master-only cleanup, exception logging, interval wake behavior, and configured age propagation.
