# File Research: sources/block-storage/stratisd/src/stratis/udev_monitor.rs

## Purpose

Monitors udev block-device events and forwards them into the daemon’s async event channel.

## Main Types and Behavior

- `udev_thread` runs blocking udev polling in `spawn_blocking`.
- Creates a libudev context and block-subsystem monitor.
- Polls with a 100 ms timeout so it can periodically check shutdown broadcast state.
- On events, converts libudev events to `UdevEngineEvent` and sends them through an unbounded channel.
- `UdevMonitor` wraps `libudev::MonitorSocket` and implements `AsFd`.

## Integration Points

Started by `stratis/run.rs`; consumed by D-Bus, JSON-RPC, or dummy IPC support depending on feature selection.

## Notable Semantics

Shutdown notification failure due to closed or lagged broadcast receiver is treated as a daemon-shutdown error.
