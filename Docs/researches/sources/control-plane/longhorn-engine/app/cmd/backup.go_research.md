# sources/control-plane/longhorn-engine/app/cmd/backup.go

## Purpose
Defines the `backup`/`backups` CLI command group for creating, restoring, inspecting, listing, removing, and checking Longhorn backups. It also wires backupstore-provided subcommands for cleanup, metadata, volume inspection, and backing image operations.

## Important APIs, Types, and Functions
- `BackupCmd()` assembles the command group and includes local commands plus `github.com/longhorn/backupstore/cmd` commands.
- `BackupCreateCmd()`, `BackupStatusCmd()`, `BackupRestoreCmd()`, and `RestoreStatusCmd()` define CLI flags and fatal error handling.
- `createBackup()` validates destination, snapshot, labels, block size, credentials, and delegates to `sync.Task.CreateBackup`.
- `checkBackupStatus()` locates the replica that owns a backup status, validates it is `types.RW`, then calls `sync.FetchBackupStatus`.
- `restoreBackup()` unescapes the backup URL, loads backup credentials, and calls `sync.Task.RestoreBackup`.
- `restoreStatus()` calls `sync.Task.RestoreStatus` and prints JSON.
- `getReplicaModeMap()` converts controller replica list output into address-to-mode lookup.

## Control Flow
CLI actions are thin wrappers: parse flags and args, construct controller or sync-task clients, call package-level services, marshal results to JSON, and log fatal errors on failure. Backup creation obtains object-store credentials before task creation and passes user labels, backing image metadata, compression method, concurrency, storage class, and `LonghornBackupParameterBackupBlockSize`. Backup status first lists controller replicas; if no `--replica` is supplied it probes RW replicas until one returns the requested backup status.

## State and Persistence Behavior
This file does not persist state directly. It initiates persistence in the backupstore via `sync.Task` and backupstore credentials. `backup-block-size` is converted from MiB to bytes through `resource.Quantity` and stored in backup parameters. Status and restore state are read from replica/controller task state and serialized to stdout.

## Dependencies and Integration Points
Depends on Longhorn backupstore, `go-common-libs/backup`, controller and replica clients, `pkg/sync`, `pkg/types`, and CLI/global flags such as `--url`, `--volume-name`, and `--engine-instance-name`. Integration tests call these paths through `integration/common/cmd.py` helpers such as `backup_create`, `backup_status`, `backup_restore`, and `restore_status`.

## Risks and Edge Cases
Replica auto-discovery for status ignores instance name and probes only RW replicas, so mixed health or stale backup status can affect discovery. A supplied `--replica` must still be RW according to controller state. Error reporting in restore attempts to marshal task errors and may print plain error strings for non-structured errors. Invalid labels and nonpositive block size are rejected early.

## Test Signals
Coverage is mostly integration-level: `integration/core/test_cli.py` exercises create/status/inspect/list/remove/restore flows, corrupt backup metadata handling, and backup volume deletion. `integration/data/test_backup.py` stresses incremental/full backup logic, backing-image backups, deletion/GC locks, block deduplication, S3 missing-backup behavior, and restore data integrity.
