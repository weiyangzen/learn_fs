# sources/distributed-fs/juicefs/pkg/vfs/backup.go

Purpose: periodically dumps JuiceFS metadata to object storage and rotates old backups.

Important APIs and types: Prometheus gauges `LastBackupTimeG` and `LastBackupDurationG`; functions `Backup`, `backup`, `cleanupBackups`, and `rotate`.

Control flow and state: `Backup` loops forever with jitter, reads the root xattr `lastBackup`, skips until the interval elapses, optionally refuses frequent backups on very large inode counts, writes a new timestamp xattr, dumps metadata, starts cleanup after success, and updates gauges. `backup` writes a gzip JSON dump under the local temp `meta/` directory, chooses more dump threads for TiKV metadata, then copies it to `blob` as `meta/dump-YYYY-MM-DD-HHMMSS.json.gz`. `cleanupBackups` lists `meta/` and deletes objects selected by `rotate`.

Persistence and integration: state persists in metadata xattr `lastBackup`, temporary local dump files, and object storage backup files. It integrates with `meta.Meta`, `object.ObjectStorage`, and `pkg/sync.CopyData`.

Risks and test signals: failed backups still leave `lastBackup` advanced because the xattr is set before dumping. Rotation parses names by fixed length. `backup_test.go` covers rotation policy and that a backup object appears.
