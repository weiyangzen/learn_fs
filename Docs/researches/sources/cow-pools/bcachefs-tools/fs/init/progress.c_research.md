# File Research: sources/cow-pools/bcachefs-tools/fs/init/progress.c

Simple mount/recovery progress indicator implementation for btree iteration workloads.

Key responsibilities:
- `bch2_progress_init()`:
  - Clears indicator state.
  - Stores stripped message prefix.
  - Sets first print time to 10 seconds in the future.
  - Estimates total nodes using disk accounting for selected leaf and inner btree masks.
  - Uses metadata replica count and btree node size to estimate nodes when upgraded accounting counters are missing.
- `progress_update_p()`:
  - Prints at most once every 10 seconds.
- `bch2_progress_update_iter()`:
  - Checks for recovery cancellation.
  - Extracts current btree node from the iterator path.
  - Counts a node when it advances past the previous `bbpos`.
  - Emits progress through `bch_info()` if not silent and the interval elapsed.
- `bch2_progress_to_text()`:
  - Formats percentage, nodes seen/total, and current `bbpos`.

Important interactions:
- Reads accounting via `bch2_accounting_mem_read()`.
- Uses btree iterator/path internals to determine the current node.
- Uses `bch2_recovery_cancelled()` so long-running passes stop promptly during RO/shutdown.
- Intended for older or mount-time code paths that cannot yet report progress through richer userspace mechanisms.

Notable behavior:
- Total node count is explicitly approximate because node replica counts may vary.
- Missing/unupgraded accounting degrades to a disk-sector-based estimate or zero rather than using misleading totals.
