# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/status.go

Purpose: implements `beegfs remote status`, which checks whether BeeGFS files are synchronized with configured or specified Remote targets.

Important APIs/types/functions: `statusConfig`; `newStatusCmd`; `runStatusCmd`; flags for remote targets, recursion, stdin delimiter, verbose, summarize, verify-remote, and filter expression through backend config.

Control flow: the command validates at least one path, enables verbose/debug backend details, determines a `PathInputMethod` from args/recurse/stdin delimiter, calls `rst.GetStatus`, drains result records, categorizes each by sync status, prints only unsynced/not-attempted/warnings by default, prints all in verbose, skips directory rows, prints a summary, waits for backend completion, verifies count consistency, and returns partial success if any files are unsynchronized.

State and persistence: read-only. It can query local Remote DB state and optionally verify against remote storage depending on backend config.

Dependencies and integration points: uses `internal/util.DeterminePathInputMethod`, `ctl/pkg/ctl/rst.GetStatus`, filesystem filter flag support, `cmdfmt`, CTL partial-success errors, Viper global debug/emoji settings, and zap debug logging.

Risks: parallel backend processing can return rows out of input order unless worker count is configured to one. A warning forces row printing even in non-verbose mode. The command treats unsynchronized files as partial success but not no-target/not-supported files.

Test signals: no direct tests. Useful tests would cover path input selection, summary counts, directory skipping, warning row emission, partial-success behavior, and no-target info printing.
