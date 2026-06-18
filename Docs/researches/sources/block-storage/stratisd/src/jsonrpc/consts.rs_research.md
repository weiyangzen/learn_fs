# File Research: sources/block-storage/stratisd/src/jsonrpc/consts.rs

## Purpose

Defines constants for the min JSON-RPC protocol.

## Main Types and Behavior

- `OP_OK` is `0`.
- `OP_ERR` is `1`.
- `OP_OK_STR` is `"OK"`.
- `RPC_SOCKADDR` is `/run/stratisd/stratisd-min-jsonrpc`.

## Integration Points

Used by client/server utilities and socket listener setup.
