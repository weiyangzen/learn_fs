# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/io_types.h

This header defines the CPU-format superblock summary stored in `struct bch_fs`.

Key fields:
- Internal and user UUIDs.
- Current, minimum, incompatible, allowed incompatible, and upgrade-complete versions.
- Device count, clean flag, multi-device flag, and encryption type.
- Extent type sizing/known metadata and backpointer shift.
- Time base/precision conversion fields.
- Feature and compat bitmaps.
- Required recovery passes, silent fsck errors, and btrees with lost data.

This structure is refreshed by `bch2_sb_update()` after reading or writing the on-disk superblock.
