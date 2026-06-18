# File Research: sources/cow-pools/nilfs-utils/sbin/nilfs-tune.c

## Purpose
`nilfs-tune.c` implements `nilfs-tune`, a utility for displaying and modifying NILFS superblock tunables such as label, UUID, commit interval, segment creation block threshold, and selected feature flags.

## Main Interfaces
- Includes NILFS on-disk definitions through `linux/nilfs2_ondisk.h`.
- Uses `nilfs_sb_read`, `nilfs_sb_write`, `nilfs_feature2string`, and `nilfs_edit_feature`.
- Uses `check_mount` to prevent dangerous writes to mounted filesystems unless forced.

## Options and Modes
Usage modes:
- `nilfs-tune -l device`: display superblock information.
- `nilfs-tune [-f] [-i interval] [-m block_max] [-L volume_name] [-O [^]feature[,...]] [-U UUID] device`: modify fields.
- `nilfs-tune [-h|-V]`.

Option effects:
- `-l`: display current superblock data.
- `-f`: force write operations even if mounted.
- `-i`: set commit interval.
- `-m`: set block count threshold for segment creation.
- `-L`: set volume label, truncating to the fixed on-disk field size.
- `-O`: edit allowed feature bits.
- `-U`: set UUID.
- `-V`: version.

## Data Model
`struct nilfs_tune_options` carries:
- Open flags (`O_RDONLY` or `O_RDWR`).
- Display flag.
- Superblock write mask.
- Force flag.
- Tunable values.
- Label buffer.
- UUID bytes.
- Feature edit string.

The mask uses NILFS superblock field masks such as:
- `NILFS_SB_COMMIT_INTERVAL`
- `NILFS_SB_BLOCK_MAX`
- `NILFS_SB_LABEL`
- `NILFS_SB_UUID`
- `NILFS_SB_FEATURES`

## Display Behavior
`show_nilfs_sb` prints:
- Volume name and UUID.
- Magic and revision.
- Feature flags.
- State, OS type, block size, timestamps.
- Mount counts.
- Reserve UID/GID with name lookup.
- Inode/DAT/checkpoint/segment usage sizes.
- Segment count, device size, first data block, blocks per segment.
- Reserved segment percentage.
- Last checkpoint, last block address, last sequence.
- Free block count.
- Commit interval and segment creation block limit.
- CRC fields.

Filesystem check interval display code exists but is disabled with `#if 0`.

## Feature Editing
- Only `NILFS_FEATURE_COMPAT_RO_BLOCK_COUNT` is allowed in the read-only compatible feature set.
- `ok_features` and `clear_ok_features` both allow only that feature.
- Invalid feature edits report whether a feature is not allowed to be set or cleared.

## Write Flow
`modify_nilfs`:
1. Opens the device read-only or read-write depending on requested operation.
2. Reads the superblock.
3. Warns about unknown incompatible or read-only-compatible features.
4. Applies requested field changes in memory.
5. Writes superblocks with `nilfs_sb_write` if the mask is nonzero.
6. Displays the resulting superblock if `-l` was requested.

`main` blocks write operations on mounted filesystems unless `-f` is supplied, warning that mounted tuning can cause severe damage.

## Notable Risks and Edge Cases
- Numeric parsing for `-i` and `-m` uses `atol` without strong validation, range checking, or negative rejection before storing into unsigned 32-bit fields.
- The device is taken as `argv[argc - 1]` after option parsing, so the command assumes the final argument is the device.
- Label truncation is intentional and may omit a terminating NUL on disk.
- UUID parsing expects exactly canonical 36-character lowercase/uppercase hex plus hyphens layout.
