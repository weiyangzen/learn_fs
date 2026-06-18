# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters_types.h

This header defines runtime counter storage.

Key type:
- `struct bch_fs_counters` stores mount-time snapshots, per-cpu current counter values, a 20-sample recent-history matrix, and delayed work for periodic sampling.

The structure is embedded in `struct bch_fs` and coordinated by `counters.c`.
