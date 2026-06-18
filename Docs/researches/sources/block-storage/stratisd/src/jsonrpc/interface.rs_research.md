# File Research: sources/block-storage/stratisd/src/jsonrpc/interface.rs

## Purpose

Defines the serialized request and response protocol between min JSON-RPC client and server.

## Main Types and Behavior

- `PoolListType` and `FsListType` are tuple aliases for list responses.
- `StratisParamType` enumerates all supported key, pool, filesystem, and report requests.
- `StratisParams` combines a serialized request type with an optional received file descriptor.
- `IpcResult<T>` is `Result<T, String>`.
- `StratisRet` enumerates all response variants and their payload tuple shapes.

## Integration Points

Both client macros and server dispatch pattern-match these variants. The request and response variant names must stay synchronized.

## Notable Semantics

File descriptors are intentionally not serialized; `StratisParams` carries `fd_opt` out-of-band after socket ancillary-data handling.
