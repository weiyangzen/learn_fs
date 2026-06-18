# File Research: sources/block-storage/stratisd/src/engine/strat_engine/mod.rs

## Purpose

`strat_engine/mod.rs` is the module root and public facade for the Stratis engine implementation. It declares the internal implementation modules and re-exports the engine types and helpers used by the rest of stratisd.

## Declared Modules

- `backstore`
- `cmd`
- `crypt`
- `device`
- `devlinks`
- `dm`
- `engine`
- `keys`
- `liminal`
- `metadata`
- `names`
- `ns`
- `pool`
- `serde_structs`
- `shared`
- `thinpool`
- `udev`
- `writing`

## Public Re-exports

Always exported:

- `integrity_meta_space`
- crypt token helpers and constants
- `get_dm`, `get_dm_init`
- `StratEngine`
- process keyring helpers and `StratKeyActions`
- `StaticHeader`, `StaticHeaderResult`, `BDA`
- `unshare_mount_namespace`
- `ThinPoolSizeParams`

With `extras` feature:

- `ProcessedPathInfos`
- `pool_inspection`
- v1 `StratPool`

## Role

The file controls module visibility for the engine and exposes selected implementation details without making all submodules public.
