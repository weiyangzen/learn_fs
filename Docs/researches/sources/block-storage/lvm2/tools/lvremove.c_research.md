# File Research: sources/block-storage/lvm2/tools/lvremove.c

## Purpose
Implements `lvremove`, removing logical volumes selected by explicit arguments or `--select`.

## Main Flow
- Requires at least one LV path unless `--select` is set.
- Enables:
  - `cmd->handles_missing_pvs`
  - `cmd->include_historical_lvs`
- Initializes a processing handle with `struct lvremove_params`, including `removed_uuids`.
- Calls `process_each_lv()` with `READ_FOR_UPDATE` and `lvremove_single`.
- If LV scanning and devices file are enabled, calls `device_id_lvremove()` to update device IDs for removed LV UUIDs.
- Destroys processing handle and returns processing result.

## Important Details
- Historical LVs are included so removal-related operations can account for history records.
- Device-file cleanup is conditional on scan/devices-file mode.
