# File Research: sources/block-storage/stratisd/src/jsonrpc/server/key.rs

## Purpose

Implements server-side key management for min JSON-RPC.

## Main Types and Behavior

- `key_set` delegates to the engine key handler with a received FD and maps `MappingCreateAction` to `Option<bool>`.
- `key_unset` delegates to the key handler and maps deletion identity to false.
- `key_list` collects key descriptions from the engine key handler.

## Integration Points

Consumes file descriptors validated by `expects_fd!` in request dispatch. It is the server counterpart to `client/key.rs`.

## Notable Semantics

`key_set` uses `Some(false)` for first creation, `Some(true)` for value update, and `None` for identity.
