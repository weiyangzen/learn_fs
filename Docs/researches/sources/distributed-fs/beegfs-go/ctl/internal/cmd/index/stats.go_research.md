
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/stats.go

- Purpose: implements `index stats <stat>` for Hive Index aggregate statistics.
- Important APIs: package-level `stat`, `newGenericStatsCmd`, `newStatsCmd`, and `runPythonExecStats`.
- Control flow/state: requires at least one stat argument, defaults path to cwd when needed, wraps stats flags, appends output format, and execs `bee stats`.
- Dependencies/integration: uses `bflag`, Viper output config, external Hive Index stats command, and logger.
- Risks/tests: package-level `stat`/`path` state is shared across command instances; `MarkHidden` errors only panic at command construction. No direct tests.
