# File Research: sources/block-storage/stratisd/src/systemd/mod.rs

## Purpose

Provides systemd compatibility helpers for readiness notification and syslog forwarding.

## Main Types and Behavior

- `serialize_pairs` converts key/value pairs into systemd notify payload lines.
- `notify` serializes pairs, converts to `CString`, calls `sd_notify`, and maps negative returns to IO errors.
- `syslog` converts a Rust log `Record` message to `CString` and calls system `syslog`.

## Integration Points

`jsonrpc/server/server.rs` calls `notify` with `READY=1` when systemd compatibility is enabled. Logging infrastructure can route records through `syslog`.

## Notable Semantics

`syslog` silently returns if the log message cannot be represented as a C string due to interior NUL bytes.
