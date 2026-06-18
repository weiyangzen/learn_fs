# File Research: sources/block-storage/stratisd/src/jsonrpc/client/filesystem.rs

## Purpose

Provides client-side wrappers for `stratis-min filesystem` commands.

## Main Types and Behavior

- `filesystem_create`, `filesystem_destroy`, and `filesystem_rename` use `do_request_standard!` and require a changed result.
- `filesystem_list` requests `FsList`, formats used bytes, device paths, UUIDs, and prints a table.
- `filesystem_origin` requests `FsOrigin`, converts nonzero return codes to `StratisError`, and returns `"None"` when no origin exists.

## Integration Points

Maps CLI-style filesystem operations to `StratisParamType::Fs*` requests and presents response tuples in terminal-friendly output.

## Notable Semantics

A missing `used` value is displayed as `FAILURE`, preserving partial list output while signaling a failed usage query.
