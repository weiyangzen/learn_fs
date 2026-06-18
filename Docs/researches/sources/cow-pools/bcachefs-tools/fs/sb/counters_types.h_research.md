# File Research: sources/cow-pools/bcachefs-tools/fs/sb/counters_types.h

This header defines runtime counter storage.

Key definitions:
- `struct bch_fs_counters`
  - `mount[]`: counter values captured at mount/load time.
  - `now`: per-CPU current counters.
  - `recent[NR_RECENT_COUNTERS][BCH_COUNTER_NR]`: fixed history window for recent deltas.
  - `work`: delayed work used to refresh recent samples.
- `NR_RECENT_COUNTERS` is 20.

Important invariants:
- `now` must be allocated/freed by counter lifecycle code.
- Recent samples store absolute snapshots; text output computes deltas between snapshots.

Research notes:
- This is intentionally small and tied to counter enum size from `counters_format.h`.
