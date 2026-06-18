<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/Fsck.cc -->
# sources/distributed-fs/eos/mgm/fsck/Fsck.cc

## Purpose

`Fsck.cc` implements the MGM fsck engine. It collects error sets from QuarkDB, enriches them with namespace-derived offline/no-replica/dark-file accounting, reports them in monitor or JSON form, and optionally submits repair jobs through `FsckEntry`.

## Important APIs, Types, and Functions

Configuration and lifecycle are handled by `Fsck()`, `Stop()`, `ApplyConfig()`, `StoreConfig()`, and `Config()`. Worker loops are `CollectErrs()` and `RepairErrs()`. Reporting uses `PrintOut()`, `Report()`, `ReportJsonFormat()`, `ReportMonitorFormat()`, and `GetFidFormat()`. Error accounting includes `QueryQdb()`, `ResetErrorMaps()`, `AccountOfflineReplicas()`, `AccountNoReplicaFiles()`, `AccountOfflineFiles()`, `AccountDarkFiles()`, `PrintOfflineReplicas()`, and `PrintErrorsSummary()`. Repair backend cleanup uses `RepairEntry()`, `NotifyFixedErr()`, and `ForceCleanQdbOrphans()`.

## Control Flow

`ApplyConfig()` parses stored `fsck` config, supports old and new key names, and calls `Config()`. Enabling collection starts `CollectErrs`; enabling repair requires collection and starts `RepairErrs`. Collector waits for namespace boot and MGM master role, reads all `fsck:<error>` QDB sets into a temporary map, swaps it into `eFsMap`, optionally performs heavy namespace accounting, logs a summary, publishes logs, signals repair, and sleeps for the configured interval. Repair waits for master and `mStartProcessing`, copies `eFsMap`, submits prioritized repair jobs to `mThreadPool`, rate-limits by queue size, cleans orphan entries for missing filesystems, flushes fixed-error notifications, and clears the processing flag.

## State and Persistence Behavior

Configuration is persisted in `FsView::gFsView` global config under `fsck`. Error state is in-memory maps guarded by `mErrMutex`, refreshed from QuarkDB `fsck:*` sets. Successful repair notifications are batched in static local maps inside `NotifyFixedErr()` and removed from QuarkDB by `QSet::srem()` on count, timeout, or forced flush. Logs are in-memory strings guarded by `mLogMutex`.

## Dependencies and Integration Points

The engine depends on global `gOFS`, `FsView`, namespace prefetchers and views, QuarkDB qclient/QSet, JSONCPP, EOS thread pool/assisted thread/logging helpers, `IdTrackerWithValidity`, and `FsckEntry`. It integrates with CLI/admin commands for config, stats, reports, and repair.

## Risks and Edge Cases

The collector and repair loops run only on master, but master transitions during queued work require careful draining. `Log()`/`LogMonitor()` use fixed buffers and `vsprintf`, which is unsafe for long formatted strings. Heavy accounting paths can scan large namespace structures and are explicitly noted as expensive. `RepairErrs()` copies potentially large error maps and submits many jobs. `ForceCleanQdbOrphans()` appears to miss a semicolon after an `eos_static_info` call. `RepairEntry()` assumes `mQcl` is initialized.

## Test Signals

Test signals include config parsing for old/new keys, collect/repair enable transitions, collection interval conversion, QDB parse errors, report formatting in JSON and monitor modes, offline/no-replica/dark-file accounting on synthetic views, repair prioritization/category filtering, fixed-error flush behavior, and master-role stop behavior with queued jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/Fsck.cc -->
