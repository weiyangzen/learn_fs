# File Research: sources/block-storage/stratisd/src/engine/strat_engine/crypt/mod.rs

Read status: complete, 21 lines.

## Purpose

This is the module declaration and public export surface for `strat_engine::crypt`.

## Module Structure

It declares:

- `macros` with `#[macro_use]`
- `consts`
- `handle`
- `shared`

## Public Re-exports

From `consts`:

- `CLEVIS_LUKS_TOKEN_ID`
- `CLEVIS_TANG_TRUST_URL`
- `DEFAULT_CRYPT_DATA_OFFSET_V2`
- `LUKS2_TOKEN_ID`

From `handle::v1`:

- `crypt_metadata_size`

From `shared`:

- `back_up_luks_header`
- `manual_wipe`
- `register_clevis_token`
- `restore_luks_header`
- `set_up_crypt_logging`

## Role In The Tree

This file exposes stable crypt helpers and constants while keeping most implementation details inside `consts`, `handle`, and `shared`.
