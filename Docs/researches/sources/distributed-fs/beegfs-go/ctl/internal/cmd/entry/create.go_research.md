
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/create.go

- Purpose: provides `entry create file` and `entry create directory` for direct BeeGFS entry creation with explicit metadata/striping settings.
- Important APIs: `newCreateCmd`, `newCreateFileCmd`, `newCreateDirCmd`, and `PrintCreateEntryResult`.
- Control flow/state: each subcommand fills `entry.CreateEntryCfg`, validates paths, calls `entry.CreateEntry`, and prints per-path status; file flags cover targets, buddy groups, pool, stripe pattern, RSTs, permissions, UID/GID, and force.
- Dependencies/integration: depends on custom flag parsers from `flags.go`, remote target flag helper, backend create APIs, and `cmdfmt`.
- Risks/tests: creation bypasses filesystem modification events per help text; defaults for UID/GID/permissions are set by flag constructors. Partial per-entry failures return a generic error after table output. No direct tests observed.
