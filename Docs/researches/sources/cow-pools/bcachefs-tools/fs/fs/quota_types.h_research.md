# File Research: sources/cow-pools/bcachefs-tools/fs/fs/quota_types.h

## Purpose
Defines in-memory quota ids, accounting modes, counters, radix tables, per-type locks, and superblock-derived runtime limits.

## Main Contents
- `struct bch_qid`, an array of qids indexed by quota type.
- `enum quota_acct_mode` with modes for prealloc, warn, and nocheck accounting.
- `struct memquota_counter`, containing current usage, hard/soft limits, grace timer, warning count, and warning-issued bitset.
- `struct bch_memquota`, grouping space/inode counters.
- `bch_memquota_table`, a generic radix tree mapping qid to in-memory quota counters.
- `struct quota_limit`, carrying timelimit and warnlimit.
- `struct bch_memquota_type`, grouping limits, radix table, and mutex for one quota type.

## Integration Notes
`struct bch_fs` owns an array of `bch_memquota_type` instances. `quota.c` allocates radix entries on demand and locks quota types in stable nested order when charging or transferring usage.

## Risks and Edge Cases
- `memquota_counter.v` is unsigned but accounting deltas are signed; limit paths must prevent underflow.
- Warning-issued state is in-memory and distinct from persistent warning counters/timers.
