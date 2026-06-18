# File Research: sources/cow-pools/bcachefs-tools/src/commands/migrate.rs

## Purpose
Implements in-place migration from an existing mounted filesystem to bcachefs, plus the follow-up `migrate-superblock` command that installs default superblock locations after validation.

## Main Interfaces
- Raw command export: `CMD_MIGRATE`
- Typed command export: `CMD_MIGRATE_SUPERBLOCK`
- Main functions:
  - `cmd_migrate`
  - `migrate_fs`
  - `migrate_superblock`
  - `reserve_new_fs_space`
  - `mark_unreserved_space`
  - `add_default_sb_layout`

## Behavior
- `migrate` requires `-f <filesystem-root>`.
- Verifies the path is a filesystem mount root via `/proc/self/mountinfo`.
- Resolves the underlying block device using `/sys/dev/block/<major>:<minor>`.
- Creates/reserves a `bcachefs` metadata file inside the old filesystem, using fallocate and FIEMAP.
- Formats a bcachefs filesystem in the reserved extents, with superblocks located inside those extents rather than default offsets.
- Marks all unreserved space as no-use so old filesystem data is protected.
- Starts the new filesystem, sets `BCH_FEATURE_no_default_sb`, copies the old filesystem tree into bcachefs, exits, and reopens read-only to run a basic fsck/open check.
- Prints instructions for mounting by explicit `sb=` offset and later running `migrate-superblock`.
- `migrate-superblock` reads the migrated superblock at an explicit offset, adds default layout entries, zeros the start of disk to remove old superblock data, reopens bcachefs, clears `no_default_sb`, marks new superblock buckets, starts the fs, then applies layout changes.

## Dependencies and Coupling
- Uses `fiemap` crate to discover reserved physical extents.
- Uses raw C helper `rust_set_bit` to mark buckets no-use.
- Uses `copy_fs::copy_fs` with migrate-specific state.
- Uses format utilities for picking block/bucket sizes and formatting.
- Uses `super_io::__bch2_super_read` and superblock layout wrappers.

## Important Implementation Notes
- Reserved metadata file size starts at device size and halves on ENOSPC down to 10% of device size.
- FIEMAP extents must be aligned to the selected block size.
- Default superblock layout reserves sector `BCH_SB_SECTOR` and the following superblock-size offset.
- `migrate_superblock` sets `BCH_FS_may_upgrade_downgrade` manually because fs init already ran before clearing `no_default_sb`.

## Risks and Edge Cases
- This is highly invasive and depends on correct physical extent reporting by the source filesystem.
- `path_is_fs_root` compares raw mountinfo mountpoint strings and does not unescape mountinfo path escaping.
- Marking no-use buckets relies on accurate extent and device-size calculations.
- Superblock migration zeros the beginning of the disk before reopening bcachefs.
- `migrate_superblock` calls `add_default_sb_layout` before and after opening; the first validates/readies the buffer, the second mutates the live per-device superblock.
