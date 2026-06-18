# File Research: sources/cow-pools/bcachefs-tools/fs/fs/quota.h

## Purpose
Public quota header for bcachefs quota bkey operations, id derivation, enabled-type calculation, accounting APIs, and quotactl integration.

## Main Contents
- Declaration of `bch_sb_field_ops_quota`.
- Bkey validation/text declarations and `bch2_bkey_ops_quota` descriptor with minimum value size 32 bytes.
- `bch_qid()`, which derives user/group/project quota ids from an unpacked inode. Project id uses the inode option +1 bias, so stored zero maps to project id zero and nonzero maps to `bi_project - 1`.
- `enabled_qtypes()`, which produces a bitmask from filesystem options `usrquota`, `grpquota`, and `prjquota`.
- Under `CONFIG_BCACHEFS_QUOTA`, declarations for accounting, transfer, lifecycle, mount-time read, and `bch2_quotactl_operations`.
- Stub no-op implementations when quota support is disabled.

## Integration Notes
Callers can unconditionally call `bch2_quota_acct()` and `bch2_quota_transfer()` because the header provides no-op stubs for builds without quota support. Inode and namespace code use `bch_qid()` to charge ownership changes consistently with project-id encoding.

## Risks and Edge Cases
- The project-id bias must remain consistent with inode option handling in `inode.h` and synthetic xattr handling in `xattr.c`.
- Disabled quota builds silently skip accounting and quota initialization.
