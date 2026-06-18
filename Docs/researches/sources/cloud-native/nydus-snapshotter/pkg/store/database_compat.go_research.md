<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/database_compat.go -->
## sources/cloud-native/nydus-snapshotter/pkg/store/database_compat.go

Purpose: migrates pre-v1 snapshotter database records into the current v1 daemon/RAFS schema and upgrades v1.0 daemon records to v1.1 by filling `DaemonMode`.

Important APIs/types: `SharedNydusDaemonID`, `CompatDaemon`, `WalkCompatDaemons`, `RedirectInstanceConfig`, `tryTranslateRecords`, and `tryUpgradeRecords`. `CompatDaemon` models legacy daemon rows with config/socket/log directories, snapshot/image IDs, fs driver, pid, and optional mount points.

Control flow and persistence: `WalkCompatDaemons` scans the legacy top-level `daemons` bucket. `tryTranslateRecords` first detects whether a shared daemon record exists. In shared mode it writes one shared daemon config state and converts per-instance records into `rafs.Rafs` entries pointing at the shared daemon, copying legacy config files into the new shared-daemon directory. In dedicated mode it writes one daemon and one RAFS instance per record. `tryUpgradeRecords` walks current daemons; if `DaemonMode` is missing it infers shared/dedicated from fs driver and mountpoint, updates each daemon, then writes `version=v1.1`.

Dependencies/integration: tightly coupled to `config` constants for fscache/fusedev and root mountpoint, plus `daemon.ConfigState` and `rafs.Rafs`. Called only from `Database.initDatabase`.

Risks and test signals: legacy optional pointer fields are dereferenced according to detected mode; malformed legacy rows can panic if required pointers are nil. Config file redirect failures are logged as warnings, not hard failures. `database_test.go` exercises both multiple dedicated daemon migration and shared daemon migration, including copied config files.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/database_compat.go -->
