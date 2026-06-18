# sources/control-plane/longhorn-engine/pkg/sync/backup.go

Purpose: orchestrates backup creation, backup status retrieval, restore fan-out, restore reset, and restore status aggregation across controller replicas.

Important APIs/types/functions: data structs `BackupCreateInfo`, `BackupStatusInfo`, and sync-level `RestoreStatus` define API output. `Task.CreateBackup` validates the target snapshot, gets volume info, finds an RW replica, and calls `createBackup`. `findRWReplica` scans controller replicas. `FetchBackupStatus` wraps replica backup status. `Task.RestoreBackup` validates volume/frontend/replica/purge state, determines restore snapshot layout and incremental mode, inspects backup metadata, validates volume size, and calls `restoreBackup` concurrently on all replicas. `Reset` and `RestoreStatus` manage/collect sync-agent restore state.

Control flow: backups are created from a single RW replica after verifying the snapshot disk exists there. Restores require the frontend to be down, no normal rebuilds, and no active purge. Snapshot layout determines whether a new random restore snapshot is needed, an existing system snapshot is reused, or purge must run first. Restore RPCs fan out concurrently and aggregate per-replica errors into `TaskError`.

State and persistence: orchestrator state is transient. Durable effects are remote backupstore objects and replica-side restore files/status. Backup inspect reads backupstore metadata. Restore status is collected from sync-agent servers.

Dependencies and integration points: depends on controller client APIs, `replica/client`, `backupstore`, Longhorn common LUKS size constants, UUID helper, and disk name utilities. It is a high-level control-plane bridge between controller state and replica sync-agent RPCs.

Risks: creating replica clients without instance names weakens identity validation. Incremental restore layout assumptions are strict and return BUG-style errors for unexpected chains. A restore can partially start on some replicas if others fail, with errors aggregated only after all goroutines finish. Size handling for encrypted volumes depends on caller-supplied correction flag. Snapshot purge may be started and then restore returns an error asking caller to retry later.

Test signals: no direct tests in this file. Restore/backup orchestration needs controller/replica fakes to cover fan-out, partial failures, snapshot layouts, and encrypted-size correction.
