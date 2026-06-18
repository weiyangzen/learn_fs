<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioMasterProcess.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioMasterProcess.java

## Purpose
Implements the core Alluxio master runtime: journal lifecycle, leader election, master registry startup, safe mode, gRPC/web/metrics/JVM services, primary promotion/demotion, backup restore, and emergency backup handling.

## Important APIs, Types, And Functions
- Constructor validates formatted journals, builds `CoreMasterContext`, creates registered masters through `MasterUtils`, and registers primacy timestamp gauges.
- `createBaseRpcServer`, `createRpcExecutorService`, `createWebServer`, `getSafeModeManager`, and `isInSafeMode` customize `MasterProcess`.
- `start()` drives the standby/primary loop.
- `promote()` gains journal primacy and starts masters as leader; `demote()` loses primacy and restarts standby components.
- `startMasterComponents`, `stopMasterComponents`, `initFromBackup`, `takeEmergencyBackup`, and `stop()` manage operational state.
- `Factory.create()` chooses a primary selector based on ZooKeeper, embedded Raft, or UFS journal mode and registers simple services.

## Control Flow
Startup starts the journal, launches standby master components, starts services, optionally waits for journal catchup, then starts leader selection. The loop waits for `PRIMARY`, records gain time, promotes through `mJournalSystem.gainPrimacy`, promotes services, waits for `STANDBY`, records lose time, demotes services and journal, and restarts standby unless configured to exit on demotion.

## State And Persistence Behavior
Persistent state is journal-managed metadata and optional backup restore data. Safe mode is reset when primary starts and later cleared by RPC server/worker wait timing. Backup initialization reads from local or root UFS and can mark root as needing sync. Metrics gauges expose start time, RPC queue/thread state, and primacy timestamps.

## Dependencies And Integration Points
Integrates `JournalSystem`, `PrimarySelector`, `MasterRegistry`, `BackupManager`, `MasterUfsManager`, metastore factories, `RpcServerService`, `WebServerService`, `MetricsService`, `JvmMonitorService`, Ratis/UFS journal selectors, and network address utilities.

## Risks And Edge Cases
Promotion handles unstable leadership during slow journal primacy gain by demoting or exiting. Corruption can trigger emergency backup. Restore-from-backup only runs on an empty journal. Stop is synchronized around `mIsStopped`, but comments acknowledge a failed first stop may require retry.

## Test Signals
Signals include HA failover tests, journal catchup tests, backup restore tests, safe mode behavior, metrics registration, and service readiness checks inherited from `MasterProcess`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioMasterProcess.java -->
