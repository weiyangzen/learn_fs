# sources/distributed-fs/juicefs/pkg/vfs/backup_test.go

Purpose: tests metadata backup retention and basic periodic backup execution.

Important APIs and types: `TestRotate` exercises `rotate`; `TestBackup` uses `createTestVFS`, `Backup`, `object.WithPrefix`, and `object.ListAll`.

Control flow and state: `TestRotate` simulates twice-daily backups across 200 half-day increments, applying rotation each time, then compares the retained set against expected monthly/weekly/daily/recent samples. `TestBackup` starts `Backup` with a 100 ms interval against a memory-backed VFS/blob, waits briefly, lists the `meta/` prefix, and expects at least one dump file.

Persistence and integration: tests use memory-backed JuiceFS components and object storage, avoiding external services.

Risks and test signals: `TestBackup` starts a goroutine that runs indefinitely for the process lifetime. Timing is short and may be sensitive under heavy load. It verifies existence, not dump content or cleanup after failures.
