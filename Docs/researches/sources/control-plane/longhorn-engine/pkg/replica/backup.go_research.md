# sources/control-plane/longhorn-engine/pkg/replica/backup.go

Purpose: manages replica-side backup status and read-only snapshot access for backup creation and incremental mapping.

Important APIs/types/functions: `BackupStatus` tracks backup identity, backing file, opened read-only replica, volume/snapshot IDs, progress, URL, state, and incremental/open flags. `NewBackup` normalizes backup and snapshot names. `UpdateBackupStatus` validates the volume/snapshot pair, updates progress/URL/error, and forces complete/error terminal states. `OpenSnapshot`, `ReadSnapshot`, `CloseSnapshot`, and `CompareSnapshot` expose snapshot contents and changed-block mappings. `findIndex` maps snapshot disk names to active disk-chain indexes, with empty compare snapshot resolving to base/backing index.

Control flow: backup reads open a read-only replica rooted at the snapshot disk in the current working directory. `CompareSnapshot` asserts the snapshot is open, locks the replica, preloads sector locations, and emits block-size-aligned mappings for sectors whose owning disk index is newer than the compare snapshot and at or below the requested snapshot.

State and persistence: `BackupStatus` is in-memory, but `OpenSnapshot` reads existing replica metadata and disk files. It does not persist backup status itself; external backupstore/sync agents own durable backup metadata.

Dependencies and integration points: depends on `backingfile`, backupstore mapping types, backupstore name generation, and disk name helpers. Used by sync-agent backup create/status paths.

Risks: `OpenSnapshot` depends on process current working directory, making caller cwd critical. `CompareSnapshot` assumes `Preload(false)` has accurate FIEMAP support and that block size alignment semantics are acceptable; it coalesces only adjacent sectors with identical aligned offset. `UpdateBackupStatus` ignores later updates after terminal state, so late correction is impossible.

Test signals: `backup_test.go` covers full and incremental mapping across multi-snapshot chains, reads of snapshot data, and backing-file behavior.
