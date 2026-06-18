# `sources/distributed-fs/ceph-client/drivers/md/dm-ima.c`

## Purpose

`dm-ima.c` implements Integrity Measurement Architecture support for device mapper. It builds structured measurements for table load, resume, remove, table clear, and rename events so IMA can record security-relevant DM device and target metadata.

## Important APIs, Types, and Functions

`fix_separator_chars()` escapes backslash, semicolon, equals, and comma so generated key-value records can be parsed safely. `dm_ima_alloc()` optionally wraps allocation in `memalloc_noio_save()` for paths that cannot recurse into IO. `dm_ima_alloc_and_copy_name_uuid()`, `dm_ima_alloc_and_copy_device_data()`, and `dm_ima_alloc_and_copy_capacity_str()` build metadata strings. `dm_ima_measure_data()` calls `ima_measure_critical_data()`. Public lifecycle functions are `dm_ima_reset_data()`, `dm_ima_measure_on_table_load()`, `dm_ima_measure_on_device_resume()`, `dm_ima_measure_on_device_remove()`, `dm_ima_measure_on_table_clear()`, and `dm_ima_measure_on_device_rename()`.

## Control Flow

On table load, the file allocates buffers, prefixes the DM version and device metadata, calls each target's `STATUSTYPE_IMA` status callback, emits one or more `dm_table_load` measurements if the fixed buffer fills, and computes a SHA-256 hash over measured table data. That hash and device metadata are stored as the inactive table state. On resume with table swap, inactive table hash and metadata become active before measuring `dm_device_resume` with current capacity. Remove measures all active/inactive metadata and hashes, then frees and resets IMA state. Table clear measures inactive table state and, for `new_map`, moves active state into inactive slots. Rename rebuilds active device metadata and measures old plus new identity.

## State and Persistence Behavior

IMA data is not block-device metadata; it is measurement-log evidence. `struct mapped_device` carries active and inactive table metadata strings, hashes, lengths, target counts, and DM version length. Ownership is transferred between active/inactive slots during resume and table clear; remove frees all owned buffers and resets the structure.

## Dependencies and Integration Points

The implementation depends on `dm-core.h`, `dm-ima.h`, Linux IMA, SHA-256 helpers, mapped-device naming helpers, disk capacity, and each target's `STATUSTYPE_IMA` status. It is compiled only when `CONFIG_IMA` enables the non-stub declarations in the header.

## Risks and Edge Cases

Measurements are best-effort: allocation failure generally skips measurement rather than failing table operations. Fixed buffer lengths require chunking on table load; correctness depends on hashing exactly what was measured. String escaping must cover all separators used by the key-value format. Pointer-sharing between active and inactive slots is explicitly checked before freeing to avoid double-free, so table swap and clear paths need careful ownership tests.

## Test Signals

Tests should exercise table loads with many targets, targets with long IMA status strings, resume with and without swap, table clear with and without `new_map`, rename, remove-all versus single remove, allocation failure paths, separator escaping in names/UUIDs/status strings, and hash stability for identical tables.
