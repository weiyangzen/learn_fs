# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota.h

This header defines quota API glue and conditional no-op fallbacks.

Key elements:
- Registers quota bkey operations with validation, text formatting, and `min_val_size = 32`.
- `bch_qid()` maps an unpacked inode to user/group/project quota ids; project id is stored with a `+1` bias in inode options, so quota id uses `project - 1` or zero.
- `enabled_qtypes()` builds a bitmask from mount options `usrquota`, `grpquota`, and `prjquota`.
- Under `CONFIG_BCACHEFS_QUOTA`, declares accounting, transfer, init/exit/read, and `bch2_quotactl_operations`.
- Without quota support, all accounting and initialization functions become no-ops.

Role:
- Keeps callers quota-aware without forcing conditional compilation throughout inode/write paths.
