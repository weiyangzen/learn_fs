# File Research: sources/block-storage/linux-dm/drivers/md/dm-ima.c

## Role
Implements IMA measurement support for device-mapper. It serializes DM device/table metadata into key-value strings, measures them through `ima_measure_critical_data()`, and stores hashes tying later device events to measured table state.

## Serialization Helpers
- `fix_separator_chars()` escapes backslash, semicolon, equals, and comma characters in names/UUIDs so key-value lists remain parseable.
- `dm_ima_alloc()` optionally wraps allocations in `memalloc_noio_save()` for no-IO contexts.
- `dm_ima_alloc_and_copy_name_uuid()` copies and escapes mapped-device name and UUID.
- `dm_ima_alloc_and_copy_device_data()` builds common device metadata: name, UUID, major, minor, minor count, and target count.
- `dm_ima_alloc_and_copy_capacity_str()` records current disk capacity.

## Table Load Measurement
- `dm_ima_measure_on_table_load()` builds one or more `dm_table_load` IMA records.
- Each record starts with `DM_IMA_VERSION_STR` and device metadata, then appends per-target metadata: index, begin sector, length, and target-specific `STATUSTYPE_IMA` status.
- If the measurement buffer would overflow, the current buffer is measured and hashed, then a new record starts again with device metadata.
- A SHA-256 hash over the measured table-load buffers is stored as the inactive table hash.
- Inactive table device metadata and target count are also saved on the mapped device.

## Device Event Measurements
- `dm_ima_measure_on_device_resume()` optionally swaps inactive table metadata/hash into the active table, then measures active table metadata, active table hash, and capacity. If no table data exists, it records name/UUID with `device_resume=no_data`.
- `dm_ima_measure_on_device_remove()` measures active/inactive table metadata and hashes, `remove_all`, and capacity, then frees all stored IMA table state and resets the structure.
- `dm_ima_measure_on_table_clear()` measures inactive table data or a no-data record, capacity, and optionally repoints inactive state to active state for a new map.
- `dm_ima_measure_on_device_rename()` updates active device metadata after rename and measures old metadata plus new name/UUID and capacity.

## Important Invariants
- Stored active/inactive metadata pointers may alias; free paths check pointer identity to avoid double-free.
- Target-specific IMA data comes from each target’s `status(..., STATUSTYPE_IMA, ...)` hook and is best-effort.
- Measurements include the DM version string prefix from `dm_ima_reset_data()`.
- Table-load hash uses the same buffers submitted to IMA, allowing later events to refer to an already measured table.

## Filesystem/Storage Relevance
This file adds measured-boot/attestation visibility for DM device configuration. For encrypted, verified, or stacked storage, it lets integrity policy observe not only device nodes but also the DM table attributes that define the block device seen by filesystems.

## Notable Risks
- Measurement is best-effort; allocation, crypto setup, or target status failures can skip or truncate measurement paths.
- Fixed-size buffers require chunking table-load measurements and careful no-data fallback paths.
