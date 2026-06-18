# File Research: sources/block-storage/stratisd/src/jsonrpc/server/pool.rs

## Purpose

Implements server-side pool operations for min JSON-RPC.

## Main Types and Behavior

- Pool lifecycle: `pool_create`, `pool_destroy`, `pool_start`, `pool_stop`, `pool_rename`.
- Device operations: `pool_init_cache`, `pool_add_data`, `pool_add_cache`, internal `add_blockdevs`.
- Listing: `pool_list` returns names, physical total/used, cache/encryption flags, and UUIDs.
- Encryption bindings: bind/unbind/rebind keyring and Clevis.
- State queries: `pool_is_encrypted`, `pool_is_stopped`, `pool_has_passphrase`, and `pool_is_bound`.

## Integration Points

Called from `StratisParams::process`. It translates engine action enums into boolean changed status for the min protocol.

## Notable Semantics

Stopped-pool queries inspect both active engine pools and `engine.stopped_pools()`. For V1 stopped metadata, encryption is inferred from presence of encryption info; for V2 it is read from `features`. Passphrase and Clevis queries handle both current `EncryptionInfo` and legacy/inconsistent `PoolEncryptionInfo`.
