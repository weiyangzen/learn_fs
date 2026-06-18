# File Research: sources/block-storage/libblkid-rs/src/utils.rs

Purpose: Provides unit wrappers and convenience helpers for libblkid evaluation and uevent operations.

Key APIs:
- `BlkidSectors`
- `BlkidBytes`
- `send_uevent`
- `evaluate_tag`
- `evaluate_spec`

Implementation notes:
- Uses a fixed sector size of 512 for sector/byte conversion.
- `evaluate` shares implementation for parsed tag lookup and unparsed spec lookup.
- Frees strings allocated by `blkid_evaluate_tag` and `blkid_evaluate_spec`.

Notable risks:
- `send_uevent` uses `Path::display().to_string()`, which can be lossy for non-UTF-8 paths.
- `BlkidSectors::bytes` can overflow the underlying signed offset type for very large values.
- `BlkidBytes::sectors` rejects byte counts not divisible by 512, matching the wrapper’s fixed-sector abstraction.
