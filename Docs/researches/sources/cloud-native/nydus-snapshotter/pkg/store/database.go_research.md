<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/database.go -->
## sources/cloud-native/nydus-snapshotter/pkg/store/database.go

Purpose: implements the persistent BoltDB store for nydus daemon states and RAFS filesystem instances under `<root>/nydus.db`. It is the durable restart/recovery layer for snapshotter-managed daemons and mounted instances.

Important APIs/types: `Database`, `NewDatabase`, `Close`, daemon CRUD (`SaveDaemon`, `UpdateDaemon`, `DeleteDaemon`, `CleanupDaemons`, `WalkDaemons`), RAFS CRUD (`AddRafsInstance`, `UpdateRafsInstance`, `DeleteRafsInstance`, `WalkRafsInstances`), and `NextInstanceSeq`. Helpers define the `v1` root bucket, `version` key, `daemons` bucket, `instances` bucket, JSON `putObject/updateObject/getObject`, and directory creation.

Control flow and persistence: `NewDatabase` creates the root directory, opens Bolt with a four-second timeout, then `initDatabase` creates `v1/daemons` and `v1/instances`. If the old non-v1 layout is detected it invokes `tryTranslateRecords`; if version is `v1.0` it invokes `tryUpgradeRecords` to add daemon mode metadata and writes `v1.1`. Write APIs use Bolt update transactions and JSON serialize domain structs keyed by daemon ID or snapshot ID. `NextInstanceSeq` uses Bolt bucket sequence allocation.

Dependencies/integration: depends on bbolt, containerd logging, project `daemon`, `rafs`, and `errdefs`. `snapshot.NewSnapshotter` constructs it and passes it into manager/cache layers.

Risks and test signals: JSON schema changes must remain backward compatible. `DeleteDaemon`/`DeleteRafsInstance` do not report not-found as an error. `NextInstanceSeq` starts a manual transaction and only rolls back when its local `err` is non-nil, so future edits must preserve commit/rollback correctness. `database_test.go` covers daemon CRUD plus legacy translation/upgrade.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/database.go -->
