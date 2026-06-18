# File Research: sources/block-storage/stratisd/src/stratis/ipc_support/mod.rs

## Purpose

Selects the correct IPC support implementation based on Cargo features.

## Main Types and Behavior

- Declares `dbus_support` for `dbus_enabled`.
- Declares `dummy` when neither `dbus_enabled` nor `min` is active.
- Declares `jsonrpc_support` for `min`.
- Re-exports the appropriate `setup`.

## Integration Points

Used by `stratis/run.rs` without needing feature-specific code at the call site.

## Notable Semantics

If both `dbus_enabled` and `min` are enabled for clippy, D-Bus wins for the exported `setup`.
