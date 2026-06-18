# File Research: sources/block-storage/mdadm/sysfs.c

## Purpose
Provides mdadm’s sysfs access layer for reading md array/member state, writing md attributes, applying configured sysfs rules, adding disks, freezing arrays, and checking selected kernel/device parameters.

## Main Responsibilities
- Reads sysfs files with newline trimming through `load_sys()`.
- Builds and frees `struct mdinfo` trees from `/sys/block/<md>/md`.
- Reads array fields: metadata version, level, layout, raid disks, component size, chunk size, cache, mismatch count, safe-mode delay, bitmap location, array state, and consistency policy.
- Reads member devices under `dev-*`, including slot, major/minor, state, offsets, size, and errors.
- Provides typed helpers for sysfs string/numeric reads and writes.
- Adds disks to arrays through `new_dev`, then configures offsets, size, slot, PPL, recovery, state, and external bad blocks.
- Implements sysfs member-state helpers for `remove`, `faulty`, `in_sync`, `external_bbl`, etc.
- Parses `SYSFS` config lines and applies them by device name or UUID with path containment checks.
- Provides utility helpers such as SCSI ID extraction, holder uniqueness, array freeze, sysfs wait, and libata `allow_tpm` check.

## Integration
This file is used throughout assemble/manage/grow paths to prefer sysfs over older md ioctls. It depends on mdadm’s mapping tables, `struct mdinfo`, `xmalloc`, UUID comparison, and shared sysfs state enums.

## Notable Behavior
- External metadata versions are represented as `major=-1`, `minor=-2`, with `text_version` carrying the external metadata string.
- `sysfs_set_array()` preserves an external metadata readonly marker when updating metadata version during reshape.
- `sysfs_rules_apply_check()` resolves real paths and ensures configured sysfs writes stay under the md sysfs directory.

## Risks and Edge Cases
- Several functions use fixed-size path buffers; most use `snprintf`, but path length limits remain important.
- In the `GET_ERROR` branch of `sysfs_read()`, the code writes `"errors"` into `buf` rather than the path suffix pointer, which appears suspicious because `load_sys()` then reads the prior `fname`.
- Sysfs state can race hot removal; the reader has special cases for disappearing member devices, but callers must still tolerate `NULL`.
