# File Research: sources/block-storage/lvm2/tools/lvrename.c

## Purpose
Implements `lvrename`, including support for renaming historical logical volumes.

## Key Structures
- `struct lvrename_params` stores:
  - whether the target is historical
  - old LV name
  - new LV name
- `_historical_lv` is a dummy `struct logical_volume` used to represent historical LV metadata for rename processing.

## Argument Handling
Supports:
- `lvrename VG old new`
- `lvrename VG/LV new`
- New name may include VG path only if it matches the old VG.
- Strips path components from LV names after extracting VG.
- Detects `HISTORICAL_LV_PREFIX` on old and new names.

## Validation
- Validates VG name.
- Ensures old/new VG names match.
- Enforces maximum LV name length based on `NAME_LEN - strlen(vg_name) - 3`.
- Rejects blank names.
- Applies LV name restrictions and generic name validation.
- Rejects identical old and new names.
- Rejects mixing live old LV with historical new LV prefix.

## Rename Flow
`_lvrename_single()`:
- Finds live LV or historical GLV.
- Rejects direct rename of RAID image/metadata LVs.
- Rejects rename while RAID is tracking a split image.
- Acquires transient exclusive lvmlockd LV lock to ensure the LV is not active elsewhere.
- Calls `lv_rename()`.
- Prints success with historical prefix when applicable.

## Important Details
- `cmd->include_historical_lvs` is enabled for this command.
- Processing is VG-scoped through `process_each_vg()` with `READ_FOR_UPDATE`.
