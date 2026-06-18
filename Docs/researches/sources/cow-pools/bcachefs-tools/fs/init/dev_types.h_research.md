# File Research: sources/cow-pools/bcachefs-tools/fs/init/dev_types.h

## Purpose
Defines lightweight device-init data structures shared across bcachefs initialization and device management code.

## Main Contents
- `struct bch_sb_handle_holder`, linking an opened block-device holder back to a `struct bch_fs`.
- `struct bch_sb_handle`, the opened superblock/device handle. It stores the loaded superblock, block device file and pointer, display name, scratch bio, holder, buffer size, block open mode, layout/bio/fs-superblock flags, and sequence.
- `struct bch_devs_mask`, a bitmask over possible superblock member slots.
- `struct bch_devs_list`, a compact list of device indexes capped by bkey pointer count.

## Integration Notes
`bch_sb_handle` is passed among superblock IO, device add/online, attach, and mount discovery code. The holder pointer is used by block holder callbacks in `dev.c` to recover the owning filesystem during block-layer events. Device masks represent online/RW/allowed member sets.

## Risks and Edge Cases
- `bch_sb_handle` ownership is transfer-like in attach paths: `__bch2_dev_attach_bdev()` copies the handle into `ca->disk_sb` and clears the source handle.
- The bitmask size depends on `BCH_SB_MEMBERS_MAX`; list storage depends on `BCH_BKEY_PTRS_MAX`.
