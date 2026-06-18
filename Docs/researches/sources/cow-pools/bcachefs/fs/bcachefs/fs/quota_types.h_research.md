# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota_types.h

This header defines in-memory quota types.

Key elements:
- `struct bch_qid` stores user/group/project ids in a fixed array.
- `enum quota_acct_mode` distinguishes preallocation, warning/enforced, and no-check accounting.
- `struct memquota_counter` tracks current usage, hard/soft limits, timer, warning count, and warning-issued bits.
- `struct bch_memquota` groups counters for one quota id.
- `bch_memquota_table` is a generic radix tree of memory quota records.
- `struct quota_limit` stores global timer/warn limits.
- `struct bch_memquota_type` contains per-counter limits, the radix table, and the mutex for one quota type.

Role:
- Provides the runtime accounting backing used by `quota.c`; persistent bkeys store limits, while this layer tracks current usage and warning state.
