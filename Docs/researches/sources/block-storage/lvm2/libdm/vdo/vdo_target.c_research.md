# File Research: sources/block-storage/lvm2/libdm/vdo/vdo_target.c

Purpose: validates VDO target parameter ranges before constructing or loading VDO device-mapper targets.

Read coverage: complete file read, 162 lines.

Key responsibilities:
- Validates minimum I/O size, block map cache size, block map era length, index memory size, slab size, max discard, VDO thread counts, write policy, and logical VDO size.
- Enforces that hash-zone, logical, and physical thread counts are either all zero or all nonzero.
- Logs specific errors for every invalid parameter while continuing validation to report multiple problems.
- Returns a boolean-like aggregate validity result.

Important entry point:
- `dm_vdo_validate_target_params(const struct dm_vdo_target_params *vtp, uint64_t vdo_size)`

Dependencies:
- Includes `libdm/misc/dmlib.h`, which supplies public VDO target parameter constants and logging.

Risk and edge cases:
- Validation depends on public constant ranges staying synchronized with kernel target expectations.
- `vdo_size` is in sectors; error formatting converts the maximum to TiB and excess to KiB.
- Unknown write-policy enum values are treated as internal errors.
