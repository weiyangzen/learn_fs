# sources/control-plane/longhorn-engine/pkg/replica/backup_test.go

Purpose: tests backup snapshot reading and changed-block mapping for replica chains with and without backing files.

Important APIs/types/functions: constants define MiB and default 2 MiB backup block size. `TestBackup` builds a simple replica, snapshots data, opens it through `BackupStatus`, and verifies mappings. `TestBackupWithBackups`, `TestBackupWithBackupsAndBacking`, and helper `testBackupWithBackups` construct a layered write/snapshot pattern and compare mappings between snapshot pairs.

Control flow: tests create temporary replica directories, chdir into them because backup open code uses cwd, write deterministic byte regions, snapshot, open snapshots through `NewBackup`, read full snapshot contents, and compare returned mappings against expected offsets.

State and persistence: creates temporary sparse disk files, snapshot metadata, optional backing file, and removes them afterward. Changes process cwd and does not restore it in this file, which can affect later tests if not isolated by the test runner.

Dependencies and integration points: exercises `New`, `Snapshot`, `BackupStatus.OpenSnapshot`, `ReadSnapshot`, `CompareSnapshot`, and `CloseSnapshot`. Uses test backing-file helpers from `replica_test.go`.

Risks: cwd mutation is global. Tests depend on filesystem FIEMAP behavior through preload/mapping, so unusual filesystems may fail. They validate mapping offsets/sizes but not backup upload or remote backupstore behavior.

Test signals: strong coverage for incremental mapping semantics, base/backing comparisons, and read-only snapshot reconstruction.
