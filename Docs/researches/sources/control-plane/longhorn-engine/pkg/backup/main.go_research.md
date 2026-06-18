<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backup/main.go -->
## sources/control-plane/longhorn-engine/pkg/backup/main.go

Purpose: backup/restore helper logic for Longhorn replica delta backups.

Important APIs/types/functions: `CreateBackupParameters` captures backup request fields. `ResponseLogAndError` and `ResponseOutput` provide CLI-friendly error/output formatting. `DoBackupInit` validates inputs, parses labels, reads volume metadata, opens optional backing file, creates `replica.BackupStatus`, and assembles `backupstore.DeltaBackupConfig`. `DoBackupCreate` calls `backupstore.CreateDeltaBlockBackup`. `DoBackupRestore` and `DoBackupRestoreIncrementally` call backupstore restore functions. `CreateNewSnapshotMetafile` atomically writes a minimal snapshot meta file.

Control flow: backup init requires volume name, snapshot name, and destination URL, validates volume naming, reads `volume.meta` from cwd through `replica.ReadInfo`, and packages metadata. Restore unescapes backup URLs and delegates to backupstore with concurrency limits.

State and persistence: reads current working directory metadata, may open backing files, writes `<file>.tmp` then renames in `CreateNewSnapshotMetafile`, and backupstore operations read/write backup targets and local delta files.

Dependencies and integration points: integrates with `github.com/longhorn/backupstore`, `pkg/replica`, `pkg/backingfile`, and util label/time/url helpers.

Risks: cwd-sensitive volume metadata can break if invoked from the wrong directory. Backup labels and provider parameters need validation by downstream backupstore. Atomic metafile write only covers same-directory rename; partial cleanup of `.tmp` on errors is not explicit.

Test signals: backup CLI/integration tests, backupstore provider tests, and snapshot metafile unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backup/main.go -->
