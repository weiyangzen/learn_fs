# File Research: sources/block-storage/stratisd/src/stratis/ipc_support/dummy.rs

## Purpose

Provides IPC-less udev handling for builds without D-Bus and without min JSON-RPC.

## Main Types and Behavior

- Receives `UdevEngineEvent` values from a channel.
- Batches the first awaited event plus any immediately available queued events.
- Calls `engine.handle_events(events)` and ignores returned IPC-layer state.

## Integration Points

Selected only when neither `dbus_enabled` nor `min` is active.

## Notable Semantics

Channel shutdown is treated as an error because the dummy handler would no longer receive udev events.
