# File Research: sources/block-storage/cryptsetup/src/integritysetup.c

## Purpose
Main `integritysetup` CLI implementation for dm-integrity devices. It supports formatting, opening, closing, status reporting, metadata dump, and resizing integrity-protected volumes.

## Main Actions
- `action_format()` formats an integrity device with checksum/MAC algorithm, tag size, sector size, journal/bitmap/inline settings, optional detached data device, optional integrity/journal keys, blkid signature wiping, and initial checksum wipe unless `--no-wipe`.
- `action_open()` loads and activates an integrity device, building activation flags for no-journal, bitmap mode, recovery, recalculate, reset recalculate, and discards.
- `action_close()` deactivates an active mapping, with deferred and cancel-deferred support.
- `action_status()` reports active state, type, tag size, algorithm, data and metadata devices, sector/interleave sizes, failures, bitmap/journal/inline flags, and discards.
- `action_dump()` loads on-disk integrity metadata and calls `crypt_dump()`.
- `action_resize()` resizes active mappings and either wipes newly exposed space or reactivates with recalculate flags.

## Key Handling
- `_read_keys()` loads optional integrity key, journal integrity key, and journal encryption key from files.
- Key file options must be paired with explicit key-size options; journal key files also require corresponding journal algorithms.
- Loaded keys are freed with `crypt_safe_free`.

## Wipe And Progress
- `_wipe_data_device()` creates a temporary private mapping and calls `crypt_wipe()` with `tools_progress`.
- Format wipe initializes all integrity checksums.
- Resize wipe initializes only the newly extended region when `--wipe` is set.

## Argument Flow
- Uses `integritysetup_args.h` for option definitions and static `tool_core_args`.
- `main()` parses popt options, handles legacy aliases `create` to `open` and `remove` to `close`, validates action arity, runs `tools_check_args()`, enforces option conflicts, enables debug, and dispatches.
- `needs_size_conversion()` applies human-size parsing only to `--journal-size` and `--device-size`.

## Validation Rules
- Integrity key file and size must both be specified.
- Journal integrity/encryption key file and size must both be specified.
- Journal key files require their journal algorithms.
- Recovery and bitmap mode are mutually exclusive.
- Journal options cannot be combined with bitmap mode.
- Bitmap options require bitmap mode.
- Inline mode excludes journal/bitmap options and a separate data device.
- Deferred and cancel-deferred are mutually exclusive.

## Dependencies
Uses common cryptsetup helpers for logging, confirmation, progress, blkid probing, key reads, and argument parsing. Links libcryptsetup functions such as `crypt_format`, `crypt_format_inline`, `crypt_load`, `crypt_activate_by_volume_key`, `crypt_resize`, and `crypt_get_integrity_info`.

## Notes
The default integrity algorithm is `crc32c` via `DEFAULT_ALG_NAME`.
