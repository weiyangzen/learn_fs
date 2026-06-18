# File Research: sources/block-storage/stratisd/src/jsonrpc/server/utils.rs

## Purpose

Provides server-side JSON-RPC utility macro and result conversion helper.

## Main Types and Behavior

- `expects_fd!` validates whether a method requires or forbids a received file descriptor.
- If an FD is forbidden but received, the macro attempts to close it and returns a protocol error.
- `stratis_result_to_return` converts `StratisResult<T>` into `(T, rc, message)` tuples using `OP_OK`, `OP_ERR`, and `OP_OK_STR`.

## Integration Points

Used by `server/server.rs` dispatch for every request returning a standard tuple.
