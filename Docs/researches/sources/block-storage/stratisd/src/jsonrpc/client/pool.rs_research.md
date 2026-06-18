# File Research: sources/block-storage/stratisd/src/jsonrpc/client/pool.rs

## Purpose

Provides client-side wrappers for `stratis-min pool` operations.

## Main Types and Behavior

- Supports pool create, start, stop, cache initialization, rename, data/cache add, destroy, list, encryption-state queries, and keyring/Clevis bind/unbind/rebind.
- `pool_start` can prompt for a password and pass it through a pipe FD.
- `pool_list` formats physical size as total/used/free and prints property flags for cache/encryption.
- Query helpers return booleans after checking JSON-RPC return codes.

## Integration Points

Maps CLI operations to `StratisParamType::Pool*` variants using shared request macros. Encryption operations use `PoolIdentifier`, `OptionalTokenSlotInput`, `KeyDescription`, `TokenUnlockMethod`, and JSON Clevis config.

## Notable Semantics

`properties_string` uses compact `Ca/~Ca` and `Cr/~Cr` flags for cache and encryption. `size_string` displays `FAILURE` when used/free values are unavailable.
