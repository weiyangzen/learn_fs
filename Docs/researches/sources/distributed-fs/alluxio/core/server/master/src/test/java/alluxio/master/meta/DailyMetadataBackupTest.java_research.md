# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/DailyMetadataBackupTest.java

Purpose: verifies daily metadata backup scheduling and backup-file retention deletion.

Important APIs/types/functions: uses `DailyMetadataBackup`, `MetaMaster.backup`, `BackupStatus`, `BackupPStatus`, `BackupState.Completed`, `UfsManager`, `UfsClient`, `UnderFileSystem`, `ControllableScheduler`, and backup filename format from `BackupManager`.

Control flow: setup mocks `MetaMaster.backup` to return a completed backup under `/tmp/test/alluxio_backups`, mocks a local UFS and root UFS client, and creates a controllable scheduler. The test enables daily backup, sets backup directory and retained-file count to one, starts `DailyMetadataBackup`, then for three simulated days updates `listStatus` to return one, two, and three generated backup files. After each `jumpAndExecute(1, DAYS)`, it verifies backup invocation count and cumulative delete calls based on `total - retain`.

State and persistence behavior: no real backups are written. Existing backup state is mocked as `UfsFileStatus` arrays; deletion is observed through mocked UFS calls.

Dependencies and integration points: covers scheduler interaction, meta master backup command, UFS root acquisition, backup naming, and retention policy.

Risks: generated backup timestamps are random and based on current time, but ordering behavior is not deeply asserted. Test verifies call counts, not exact deleted paths. It mixes `deleteFile` and `deleteExistingFile` expectations, reflecting implementation transition details.

Test signals: good signal that daily scheduled execution runs backups and enforces file-retention counts over repeated runs.
