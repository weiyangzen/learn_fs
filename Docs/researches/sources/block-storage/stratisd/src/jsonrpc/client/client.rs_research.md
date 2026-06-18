# File Research: sources/block-storage/stratisd/src/jsonrpc/client/client.rs

## Purpose

Implements the minimal Unix-socket JSON-RPC client transport used by `stratis-min`.

## Main Types and Behavior

- `send_request` serializes a request to JSON, optionally sends one file descriptor with `SCM_RIGHTS`, reads up to 65536 bytes of response data, and deserializes it.
- `StratisClient` wraps a `UnixStream`.
- `StratisClient::connect` connects to the configured socket path.
- `StratisClient::request` sends a `StratisParams` request and returns an `IpcResult<StratisRet>`.

## Integration Points

The request macros in `client/utils.rs` use `StratisClient` for all key, pool, filesystem, and report operations. FD passing supports keyfile/passphrase transfer.

## Notable Semantics

Responses are read with a fixed 64 KiB buffer and one read call, so this protocol assumes responses fit in one read.
