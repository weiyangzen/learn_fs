# File Research: sources/block-storage/stratisd/src/jsonrpc/server/filesystem.rs

## Purpose

Implements server-side filesystem operations for the min JSON-RPC API.

## Main Types and Behavior

- `filesystem_create` resolves a pool by name, obtains a mutable pool guard, and calls `create_filesystems`.
- `filesystem_list` walks all pools and accumulates pool names, filesystem names, used bytes, creation timestamps, devnodes, and UUIDs.
- `filesystem_destroy` resolves filesystem UUID by name and calls `destroy_filesystems`.
- `filesystem_rename` resolves filesystem UUID and calls `rename_filesystem`.
- `filesystem_origin` returns the origin UUID as a simple string if present.

## Integration Points

Called from `StratisParams::process` in `server/server.rs`. Blocking pool operations are wrapped with `tokio::task::block_in_place`.

## Notable Semantics

Lookup failures produce explicit `StratisError::Msg` values naming the missing pool or filesystem.
