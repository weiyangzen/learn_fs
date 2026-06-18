# sources/control-plane/longhorn-engine/app/cmd/system_backup.go

## Purpose
Exposes backupstore system-backup operations under the Longhorn CLI.

## Important APIs, Types, and Functions
- `SystemBackupCmd()` returns `system-backup` with upload, delete, download, list, and get-config subcommands from `github.com/longhorn/backupstore/cmd`.

## Control Flow
No local action logic. The CLI delegates entirely to backupstore command constructors.

## State and Persistence Behavior
Persistence is owned by backupstore system-backup commands and their target stores. This wrapper only mounts them into Longhorn CLI.

## Dependencies and Integration Points
Depends directly on backupstore CLI package. It integrates system-level backups distinct from per-volume backup commands.

## Risks and Edge Cases
Local validation is absent; any argument, credential, or storage errors are handled by backupstore subcommands.

## Test Signals
No tests for system-backup commands appear in the listed subset.
