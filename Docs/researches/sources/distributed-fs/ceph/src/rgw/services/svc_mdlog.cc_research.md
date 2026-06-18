<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_mdlog.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_mdlog.cc

Purpose: Implements the RGW metadata log service, including period-aware metadata log selection, oldest-log-period history persistence, coroutine wrappers for async system-object reads/writes, and metadata log entry completion.

Important APIs, types, and functions: `RGWSI_MDLog::init()` wires RADOS, zone, sysobj, cls, and async processor. `do_start()` creates the current period log, `RGWPeriodPuller`, and `RGWPeriodHistory`. `read_history()` and `write_history()` serialize `RGWMetadataLogHistory`. The `mdlog` namespace defines `SysObjReadCR`, `SysObjWriteCR`, `ReadHistoryCR`, `WriteHistoryCR`, and `TrimHistoryCR`. Public operations include `find_oldest_period()`, `init_oldest_log_period()`, `read_oldest_log_period()`, `read_oldest_log_period_cr()`, `trim_log_period_cr()`, `get_log()`, `add_entry()`, `complete_entry()`, `get_shard_id()`, and `pull_period()`.

Control flow: Startup obtains the zone's current period, creates or retrieves the associated `RGWMetadataLog`, and initializes period history. If sync is enabled and the zone needs sync, it initializes oldest-log history. Synchronous history reads fetch `RGWMetadataLogHistory::oid` from the log pool, decode it, and remove empty corrupt objects. Coroutine history reads/writes queue async sysobj operations and update cursors or object versions. Trimming reads existing history, rejects older trim attempts, then writes the next cursor. Metadata completion encodes `RGWMetadataLogData` with `MDLOG_STATUS_COMPLETE` and appends it to the current log using a hash key of `section:key`.

State and persistence: `md_logs` caches per-period `RGWMetadataLog` objects in memory. `current_log` points to the current period log. `RGWMetadataLogHistory` persists oldest period id and realm epoch in the zone log pool. Metadata entries persist in cls log-backed metadata log shards. Version trackers protect history updates.

Dependencies and integration points: Depends on `RGWSI_Zone`, `RGWSI_SysObj`, `RGWSI_Cls`, `RGWAsyncRadosProcessor`, `RGWMetadataLog`, `RGWPeriodHistory`, `RGWPeriodPuller`, `RGWCoroutine`, and config store period reads. User and metadata services call `complete_entry()` when metadata object mutations are committed.

Risks and test signals: `init_oldest_log_period()` contains an early return after the rewrite path in this snapshot, leaving the later pull-by-period-id block unreachable from visible control flow. History corruption, empty history objects, concurrent trims, and missing predecessor periods are high-risk cases. Tests should cover single-period and multi-period startup, sync-enabled oldest period initialization, concurrent trim conflict (`-ECANCELED`), metadata completion shard selection, and decode failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_mdlog.cc -->
