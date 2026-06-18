# File Research: sources/cow-pools/bcachefs-tools/fs/fs/quota_format.h

## Purpose
Defines persistent quota bkey and superblock quota field formats.

## Main Contents
- `enum quota_types`: user, group, project, and count.
- `enum quota_counters`: space, inode, and counter count.
- `struct bch_quota_counter`, storing hardlimit and softlimit.
- `struct bch_quota`, the quota bkey value containing counters for space and inodes.
- Superblock quota field structures:
  - `struct bch_sb_quota_counter` with timelimit and warnlimit.
  - `struct bch_sb_quota_type` with flags and counter limits.
  - `struct bch_sb_field_quota` containing settings for all quota types.

## Integration Notes
`quota.c` validates, prints, loads, and updates these structures. Quota btree keys use key position inode as quota type and offset as qid. Superblock quota fields store grace/warning policy, while btree quota values store per-qid hard/soft limits.

## Risks and Edge Cases
- Endian annotations are part of the disk format and must be preserved.
- `struct bch_sb_field_quota` validation expects the full structure size.
