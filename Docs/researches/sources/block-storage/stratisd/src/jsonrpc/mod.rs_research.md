# File Research: sources/block-storage/stratisd/src/jsonrpc/mod.rs

## Purpose

Declares the JSON-RPC module tree and public exports.

## Main Types and Behavior

- Exposes `client`.
- Keeps `consts`, `interface`, and `server` internal to the module.
- Re-exports constants and `run_server`.

## Integration Points

The daemon IPC support imports `jsonrpc::run_server`; client code imports through `jsonrpc::client`.
