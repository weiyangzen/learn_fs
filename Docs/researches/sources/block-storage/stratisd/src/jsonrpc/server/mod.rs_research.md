# File Research: sources/block-storage/stratisd/src/jsonrpc/server/mod.rs

## Purpose

Declares the JSON-RPC server module tree.

## Main Types and Behavior

- Imports server-side utility macros.
- Declares filesystem, key, pool, report, and module-inception `server`.
- Re-exports `run_server`.

## Integration Points

Used by `jsonrpc/mod.rs` and IPC setup.
