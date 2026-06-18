# `sources/distributed-fs/ceph-client/drivers/md/dm-init.c`

## Purpose

`dm-init.c` implements early boot creation of mapped devices from kernel module parameters. It parses `dm-mod.create=...` table descriptions and optional `dm-mod.waitfor=...` device names, waits for dependencies, and invokes `dm_early_create()`.

## Important APIs, Types, and Functions

`struct dm_device` wraps `struct dm_ioctl`, an array of up to `DM_MAX_TARGETS` target specs, an array of target argument strings, and a list node. `dm_allowed_targets` restricts early boot setup to `crypt`, `delay`, `linear`, `snapshot-origin`, `striped`, and `verity`. `str_field_delimit()` splits and trims fields in place. `dm_parse_table_entry()` parses `<start_sector> <num_sectors> <target_type> <target_args>`. `dm_parse_device_entry()` parses `name,uuid,minor,flags,table`. `dm_parse_devices()` builds the list of requested devices. `dm_init_init()` is registered as a `late_initcall`.

## Control Flow

If `create` is unset, initialization exits. Otherwise the string is length-checked, duplicated, parsed into `dm_device` objects, and device probing is waited for. Each `waitfor` path is repeatedly resolved through `early_lookup_bdev()` with a short sleep until available. Then every parsed device is passed to `dm_early_create()` with its ioctl header, target specs, and target argument strings. Cleanup frees all allocated specs, argument strings, devices, and the duplicated input buffer.

## State and Persistence Behavior

This file has no persistent metadata of its own. It creates mapped devices during boot; their persistence depends on the resulting DM targets and userspace policy. Parser allocations are marked `__init` flow and freed after setup.

## Dependencies and Integration Points

It integrates with module parameters `create` and `waitfor`, kernel initcall ordering, block-device probing, `early_lookup_bdev()`, device-mapper ioctl structures, and `dm_early_create()`. It deliberately limits target types for early boot safety and availability.

## Risks and Edge Cases

Parsing is in-place and currently lacks escaped-character support, so names, UUIDs, and target arguments cannot contain delimiters that need escaping. Fixed limits cap devices, targets, wait-for entries, and string length. Error handling aborts on malformed fields or disallowed targets, but devices parsed before the error are cleaned up. The wait loop has no timeout, so a missing `waitfor` device can stall boot indefinitely.

## Test Signals

Tests should cover valid single and multi-device strings, multi-target tables, empty UUID/minor handling, persistent minor encoding, read-only/read-write flags, disallowed target rejection, malformed delimiters, length and count limits, waitfor behavior, and cleanup after mid-parse allocation or validation failures.
