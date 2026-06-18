# File Research: sources/cow-pools/bcachefs-tools/src/commands/timestats.rs

Implements the `bcachefs timestats` command for one-shot, JSON, and interactive terminal display of kernel time statistics exposed through `/sys/fs/bcachefs/<fs>/time_stats_json`, `internal/btree_trans_stats_json`, and per-device latency JSON files.

Key structures mirror kernel JSON: `DurationStats`, `EwmaStats`, `TimeStats`, and `BtreeTransFnStats`. Runtime display groups stats into `FsSnapshot` sections across three pages: base operation stats, btree transaction stats, and per-device I/O latency.

Major behavior:
- Resolves either all mounted bcachefs sysfs directories or one filesystem via `BcachefsHandle::open`.
- Reads `time_stats_json`, partitioning names beginning with `blocked_` into a "Slowpath" section.
- Optionally reads device latency stats from `dev-*/io_latency_stats_read_json` and `io_latency_stats_write_json`.
- Emits raw JSON with a map of filesystem label to stat name to `TimeStats`.
- Uses `run_tui` and `crossterm` for an interactive alternate-screen UI with sorting, paging, reverse sort, pause, interval changes, and mean-vs-EWMA view switching.

Notable implementation details:
- `fmt_duration` uses coarse integer unit conversion and chooses larger units only when the value is at least 10 units.
- `sort_entries` sorts numeric columns descending by default; name sorts lexicographically.
- Interactive device stats are collected only while on the devices page to reduce sysfs cost.
- Non-interactive mode is selected by `--once` or when stdout is not a terminal.

Potential concerns:
- `SortBy::col_index` names do not map cleanly to displayed columns after `DurTotal`: the table has duration mean/stddev then frequency mean/stddev, while variants are `MeanSince`, `MeanRecent`, `StddevSince`, `StddevRecent`. The active `View` decides mean vs recent, so these CLI names may be misleading.
- Interactive collection uses `collect_stats(...).unwrap_or_default()`, so transient read/parse failures can silently clear the display instead of surfacing an error.
