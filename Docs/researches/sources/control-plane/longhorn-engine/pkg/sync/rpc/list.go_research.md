# sources/control-plane/longhorn-engine/pkg/sync/rpc/list.go

Purpose: maintains bounded in-memory FIFO-like lists for backup status records and snapshot hash jobs in the sync-agent RPC server.

Important APIs/types/functions: `BackupList` stores `BackupInfo` entries keyed by backup ID. `BackupAdd`, `BackupGet`, `BackupDelete`, `remove`, and `refresh` implement CRUD and retention. `retainBackupStateCounts` keeps the newest 5 complete and 10 error backups. `SnapshotHashList` stores `SnapshotHashInfo` entries keyed by snapshot name. `Add`, `Get`, `Delete`, `GetSize`, `refresh`, `purgePartialRetained`, and `remove` implement job retention with `MaxSnapshotHashJobSize` per terminal state.

Control flow: adding a backup removes any existing record, appends, updates high-water mark, then refreshes terminal entries. Backup refresh walks from newest to oldest per terminal state and removes older entries beyond retention. Snapshot hash add rejects duplicate in-progress jobs, replaces completed/error jobs for the same snapshot, appends the new job, and refreshes completed/error retention. Get also refreshes before lookup.

State and persistence: state is process-local and protected by RWMutexes. No status survives process restart.

Dependencies and integration points: used by sync-agent backup and snapshot hash RPC handlers. Depends on replica progress states and hash job objects.

Risks: `backupListHighWaterMark` is package-global and not synchronized with list locks. Retention loops decrement indexes inside loops after removal, which is delicate. Snapshot hash retention keeps up to `MaxSnapshotHashJobSize` for each terminal state, not total. In-progress hash jobs are never purged by retention and can accumulate until completed/cancelled/deleted.

Test signals: `list_test.go` covers snapshot hash CRUD and retention refresh on add/get. BackupList retention is not covered in this subset.
