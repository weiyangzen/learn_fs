# File Research: sources/cow-pools/bcachefs-tools/fs/util/time_stats.c

Purpose: Collects and formats duration and inter-arrival-time statistics.

Key APIs and behavior:
- Chooses display units from ns through years/eon.
- Updates duration and frequency stats with exact mean plus median/MAD estimates.
- Optional quantile estimator uses Eytzinger-indexed entries.
- Automatically switches to per-CPU buffering for frequent events unless disabled.
- Emits human-readable text and JSON through `seq_buf`.
- Provides reset, init, no-percpu init, and exit.

Integration:
- Implements `time_stats.h`.
- Uses `mean_and_variance`, `eytzinger`, percpu buffers, local clock, and spinlocks.
- Used by writeback throttling and diagnostics.

Risks and invariants:
- Buffered per-CPU events are flushed under the main stats lock before rendering.
- `__bch2_time_stats_clear_buffer()` iterates the full fixed entry array, not just `nr`, which can process zeroed entries after init/reset.
- Min fields initialize to `U64_MAX`; JSON maps that to zero for empty output.
