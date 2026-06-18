<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/daemonstore.go -->
## sources/cloud-native/nydus-snapshotter/pkg/store/daemonstore.go

Purpose: provides `DaemonRafsStore`, a narrow adapter that exposes daemon and RAFS instance persistence through the underlying Bolt-backed `Database`. It is the storage facade used by manager/recovery code so callers do not manipulate Bolt buckets directly.

Important APIs: `NewDaemonRafsStore`, `AddDaemon`, `UpdateDaemon`, `DeleteDaemon`, `WalkDaemons`, `CleanupDaemons`, `AddRafsInstance`, `UpdateRafsInstance`, `DeleteRafsInstance`, `WalkRafsInstances`, and `NextInstanceSeq`. Each method forwards to `Database` with `context.TODO()` for write helpers or passes the caller context for walkers/cleanup.

Control flow and state: the wrapper has no independent state beyond `db *Database`; persistence is entirely delegated to the `daemons` and `instances` buckets in `database.go`. Duplicate daemon insertion propagates `ErrAlreadyExists`; missing update/delete behavior follows database semantics.

Dependencies and integration: imports daemon and rafs domain types and is consumed by manager/filesystem recovery paths that need durable daemon process state and RAFS mount metadata.

Risks and test signals: the adapter itself is thin and untested directly; coverage comes from `database_test.go`. Risk lies in the silent use of `context.TODO()` on writes, which ignores caller cancellation/deadlines.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/daemonstore.go -->
