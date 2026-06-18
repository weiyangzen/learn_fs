# File Research: sources/block-storage/stratisd/src/jsonrpc/client/report.rs

## Purpose

Provides the client-side report request.

## Main Types and Behavior

- `report()` sends `Report` and returns a `serde_json::Value`.

## Integration Points

Used by min JSON-RPC clients that need the engine state report directly as JSON.
