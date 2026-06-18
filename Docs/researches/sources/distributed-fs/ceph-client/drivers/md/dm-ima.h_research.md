# `sources/distributed-fs/ceph-client/drivers/md/dm-ima.h`

## Purpose

`dm-ima.h` defines the data structures, buffer limits, version string, and public hooks for device-mapper IMA measurements. It also provides no-op inline stubs when IMA support is disabled.

## Important APIs, Types, and Functions

The header defines fixed buffer sizes for full measurements, device metadata, target metadata, target data, and capacity strings. `DM_IMA_VERSION_STR` encodes the device-mapper major/minor/patchlevel into the measurement prefix. Under `CONFIG_IMA`, `struct dm_ima_device_table_metadata` stores device metadata, table hash, and target count for one table slot, while `struct dm_ima_measurements` contains active and inactive slots plus version-string length. Public hooks cover reset, table load, device resume, device remove, table clear, and device rename.

## Control Flow

Core device-mapper code calls these hooks at lifecycle points. With IMA enabled, the implementation in `dm-ima.c` emits measurements and updates active/inactive hashes. With IMA disabled, inline stubs compile away the calls, keeping call sites simple and avoiding conditional code in the DM core.

## State and Persistence Behavior

The header describes in-memory measurement state embedded in `struct mapped_device`. It does not define persistent block metadata. Measurement results are intended for IMA logs through the implementation.

## Dependencies and Integration Points

It depends on DM version macros and forward declarations of `struct mapped_device` and `struct dm_table` from the including DM core context. The target status integration is indirect: table-load measurement code requests `STATUSTYPE_IMA` from each target.

## Risks and Edge Cases

The fixed buffer-size contract means implementation and target IMA status output must stay within expected limits or measurement chunking/truncation behavior becomes relevant. Stub functions must exactly match enabled prototypes so call sites remain build-stable across `CONFIG_IMA`.

## Test Signals

Build tests should cover `CONFIG_IMA=y` and `CONFIG_IMA=n`. Runtime tests should verify active/inactive state transitions, version-string formatting, target status inclusion, and no-op behavior when IMA is disabled.
