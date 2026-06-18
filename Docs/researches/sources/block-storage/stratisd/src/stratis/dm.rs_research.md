# File Research: sources/block-storage/stratisd/src/stratis/dm.rs

## Purpose

Runs the devicemapper event monitoring task and routes device-mapper events into engine pool/filesystem event handlers.

## Main Types and Behavior

- `dm_event_thread` starts an async task when a real engine is present; with `None`, it logs that monitoring is disabled for the sim engine.
- `process_dm_event` waits for DM FD readiness, clears readiness, arms DM polling, gets engine events, and invokes pool/filesystem event processing.
- D-Bus builds send background signals for pool and filesystem diffs; min/non-D-Bus builds ignore return diffs.
- `setup_dm` initializes DM, requires minor version at least 37, adjusts FD flags, and wraps the DM FD in `AsyncFd`.

## Integration Points

Started from `stratis/run.rs` alongside udev, IPC, timer, signal, and key-loading tasks.

## Notable Semantics

The code clears async readiness without reading from the DM FD because the devicemapper library manages event state through `arm_poll()`/event APIs.
