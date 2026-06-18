# File Research: sources/block-storage/linux-dm/drivers/md/dm-init.c

## Role
Implements early-boot creation of mapped devices from the `dm-mod.create=` kernel/module parameter.

## Input Format
- Top-level format is `<name>,<uuid>,<minor>,<flags>,<table>[,<table>+][;<device>...]`.
- Each table entry is `<start_sector> <num_sectors> <target_type> <target_args>`.
- Maximums are 256 devices, 256 targets per device, and a 4096-byte input string.

## Parser Flow
- `dm_init_init()` duplicates the `create` string, parses devices, waits for device probing, then calls `dm_early_create()` for each parsed device.
- `dm_parse_devices()` splits device entries on semicolons and allocates `struct dm_device` records.
- `dm_parse_device_entry()` splits name, UUID, minor, flags, and table; `ro` sets read-only and `rw` is accepted as writable.
- `dm_parse_table()` loops comma-separated table entries.
- `dm_parse_table_entry()` parses start, length, target type, and target args, allocates a `dm_target_spec`, validates the target type, and stores a duplicated argument string.
- `dm_setup_cleanup()` frees all allocated specs, argument strings, and device records.

## Safety and Scope
- Allowed early-boot targets are restricted to `crypt`, `delay`, `linear`, `snapshot-origin`, `striped`, and `verity`.
- `str_field_delimit()` trims leading/trailing whitespace but explicitly does not support escaped separator characters.
- Supplying a minor number sets `DM_PERSISTENT_DEV_FLAG`.

## Important Invariants
- The parameter string must fit within `DM_MAX_STR_SIZE`; oversized input is rejected before parsing.
- Each parsed table target must be one of the allowlisted target types.
- Target args are copied with `kstrndup()` before the temporary parse string is freed.

## Filesystem/Storage Relevance
This file enables initramfs-less or early userspace storage stacks, such as encrypted or verified root devices, to be configured directly by the kernel command line before normal userspace tooling is available.

## Notable Risks
- The grammar is intentionally simple and lacks escaped separators, so names, UUIDs, and target args must avoid unescaped delimiters in this early-boot path.
- Creation stops at the first `dm_early_create()` failure, but the parser returns the parse result rather than per-device create status.
