# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/mod.rs

Read status: complete, 24 lines.

## Purpose

This is the module declaration and public re-export surface for the `strat_engine::backstore` subsystem.

## Module Structure

It declares:

- `backstore`
- `blockdev`
- `blockdevmgr`
- `cache_tier`
- `data_tier`
- `devices`
- `range_alloc`
- `shared`

Only selected symbols are re-exported.

## Public Re-exports

From `blockdev::v2`:

- `integrity_meta_space`

From `devices`:

- `find_stratis_devs_by_uuid`
- `get_devno_from_path`
- `get_logical_sector_size`
- `ProcessedPathInfos`
- `UnownedDevices`

Under `#[cfg(test)]`, it also re-exports:

- `initialize_devices`
- `initialize_devices_legacy`

## Role In The Tree

This file intentionally hides most backstore internals while exposing device discovery and block-device utility APIs needed outside the submodule.
