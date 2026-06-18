# File Research: sources/block-storage/stratisd/src/stratis/ipc_support/jsonrpc_support.rs

## Purpose

Sets up min JSON-RPC IPC support and udev event forwarding.

## Main Types and Behavior

- `handle_udev` spawns a task that batches udev events and calls `engine.handle_events`.
- `setup` starts both udev handling and the JSON-RPC server.
- A `tokio::select!` returns if either the udev handler or server task exits.

## Integration Points

Selected by `ipc_support/mod.rs` when `min` is active and D-Bus is not. Uses `jsonrpc::run_server`.

## Notable Semantics

JSON-RPC has no persistent IPC-side object model, so event handling ignores returned data structure updates.
