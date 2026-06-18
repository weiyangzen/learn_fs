# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota_format.h

This header defines persistent quota formats.

Key elements:
- Quota types:
  - user
  - group
  - project
- Quota counters:
  - space
  - inode count
- `struct bch_quota_counter` stores hard and soft limits.
- `struct bch_quota` is the on-disk bkey value containing counters for space and inodes.
- Superblock quota field structs store per-type flags plus timer and warning limits per counter.

Role:
- Separates durable quota limits and global quota policy from in-memory usage counters.
- Uses little-endian fields and packed/aligned layout for on-disk compatibility.
