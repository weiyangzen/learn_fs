# File Research: sources/block-storage/stratisd/src/stratis/ipc_support/dbus_support.rs

## Purpose

Sets up D-Bus-specific IPC support and udev event processing.

## Main Types and Behavior

- Registers existing pools with the D-Bus udev handler at startup.
- Logs D-Bus API availability.
- Spawns a loop that calls `udev.process_udev_events()`.
- Uses `tokio::select!` to return if the udev task exits.

## Integration Points

Selected by `ipc_support/mod.rs` when `dbus_enabled` is active. Called from `stratis/run.rs`.

## Notable Semantics

If D-Bus udev processing exits, setup reports the task failure through `StratisError`.
