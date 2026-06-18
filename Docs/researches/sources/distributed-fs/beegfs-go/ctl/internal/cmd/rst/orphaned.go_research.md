# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/orphaned.go

Purpose: implements `beegfs remote cleanup-orphaned`, which removes BeeGFS Remote database entries for paths that no longer exist in BeeGFS.

Important APIs/types/functions: `cleanupOrphanedConfig` holds front-end flags; `newCleanupOrphanedCmd` wires `--yes`, `--recurse`, and `--verbose`; `runCleanupOrphanedCmd` consumes the backend result stream from `rst.CleanupOrphaned`.

Control flow: Cobra requires one path prefix. Recurse mode is blocked unless `--yes` is present. The runner gets result and wait channels, counts scanned/deleted/skipped/error rows, prints verbose rows for deletes/skips and all error rows, prints a summary, waits for backend completion, and returns a partial-success `CtlError` if per-entry errors occurred.

State and persistence: mutates only the Remote database, not BeeGFS files or remote objects. With `--recurse`, all entries matching the prefix may be deleted. It requires a mount to verify path existence; unmounted mode errors are annotated with a hint.

Dependencies and integration points: uses `ctl/pkg/ctl/rst.CleanupOrphaned`, `common/filesystem.ErrUnmounted`, `cmdfmt`, Viper debug flag, and `internal/util.NewCtlError`.

Risks: destructive database cleanup is gated but still prefix-based; users can delete many Remote DB records with one command. Summary waits until after rows are printed, so a backend wait error appears after output. Verbose defaults to debug, which may expose many paths.

Test signals: no direct tests. Valuable tests would cover recurse without `--yes`, unmounted error wrapping, result counting, partial-success exit code, and verbose/non-verbose row emission.
