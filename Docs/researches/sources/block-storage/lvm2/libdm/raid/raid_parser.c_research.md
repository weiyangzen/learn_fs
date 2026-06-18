# File Research: sources/block-storage/lvm2/libdm/raid/raid_parser.c

## Summary
Reads and optionally clears failed-device bitmaps in dm-raid metadata superblocks stored on RAID metadata volumes. It understands the original and v1.9.0-extended dm-raid superblock layout enough to count or clear failed-device flags.

## Main Responsibilities
- Defines the relevant on-disk dm-raid superblock fields and constants.
- Detects whether extended v1.9.0 failed-device bitmap fields are present.
- Counts set bits in failed-device fields.
- Opens a metadata volume with direct I/O, reads the first 4 KiB, validates the dm-raid magic, and optionally writes a cleared superblock back.

## Key APIs
- `dm_raid_count_failed_devices()`
- `dm_raid_clear_failed_devices()`

## Important Behavior
The superblock magic is `"DmRd"` and compatible feature flag `FEATURE_FLAG_SUPPORTS_V190` indicates that extended fields are present. `_get_sb_size()` uses that flag to choose either the pre-extension size or the full struct size.

Counting starts with the legacy `failed_devices` field. For extended superblocks, it iterates `extended_failed_devices` and keeps the maximum hweight observed rather than summing all words.

Clearing zeroes `failed_devices`, all extended failed-device words when present, and all bytes after the meaningful superblock size in the 4 KiB I/O buffer before writing.

## State and Lifetime
Each operation allocates a 4 KiB aligned buffer with `posix_memalign()`, opens the metadata path with `O_EXCL | O_DIRECT` and either read-only or read-write mode, then closes and frees everything before returning.

## Risks
The source comments call out endianness uncertainty around magic validation. The copied superblock layout is intentionally trimmed and may drift from kernel `drivers/md/dm-raid.c`. Clearing writes the first 4 KiB of the metadata device and should only be used on the intended rmeta volume.
