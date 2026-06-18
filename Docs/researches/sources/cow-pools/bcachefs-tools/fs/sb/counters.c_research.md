# File Research: sources/cow-pools/bcachefs-tools/fs/sb/counters.c

This file implements persistent and runtime filesystem counters.

Key responsibilities:
- Builds counter name, flag, and stable-ID maps from `BCH_PERSISTENT_COUNTERS()`.
- Provides superblock field ops for counters.
- Loads persistent counters from the superblock into per-CPU runtime counters.
- Stores per-CPU runtime counters back into the superblock.
- Samples recent counter history periodically for diagnostics.
- Prints persistent counters and recent activity deltas.
- Initializes and tears down filesystem counter state.
- Resets a selected counter.
- Implements `bch2_ioctl_query_counters()` when chardev support is enabled.

Important behavior:
- Stable counter IDs determine on-disk slots, not enum order.
- Missing counters default to zero when reading older superblocks.
- `bch2_sb_counters_from_cpu()` resizes the counters field if it has fewer than `BCH_COUNTER_NR` entries.
- Recent samples shift a fixed history window every `HZ / 2`.
- The ioctl can return either current runtime counters or mount-time counters depending on flags.

Important invariants:
- Runtime `now[]` counters are per-CPU u64 values.
- `mount[]` stores the counter values at mount/read time.
- Counter superblock validation is currently permissive.
- Counter query rejects unknown flags and nonzero padding.

Dependencies:
- Uses superblock field resize/get, percpu u64 helpers, delayed work, user copy helpers, and counter format definitions.

Research notes:
- Counter IDs are explicitly stable to preserve user-visible and on-disk compatibility across enum reordering.
