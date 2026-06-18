# File Research: sources/block-storage/stratisd/src/stratis/run.rs

## Purpose

Implements the main daemon startup and task orchestration loop.

## Main Types and Behavior

- `signal_thread` waits for Ctrl-C/SIGINT.
- `run(sim)` optionally unshares the mount namespace, sets up crypt logging, registers Clevis token support, creates process keyring, builds a multi-thread Tokio runtime, and starts the engine.
- `start_threads` starts udev monitoring, IPC support, signal handling, devicemapper event monitoring, timed checks, and volume-key loading.
- Uses `tokio::select!` to shut down when a task exits, errors, or SIGINT arrives.
- Real mode initializes `StratEngine`; simulation mode uses `SimEngine`.

## Integration Points

This is the primary entrypoint re-exported by `stratis/mod.rs`. It wires together engine, IPC, D-Bus/min feature variants, DM, udev, timers, key management, and shutdown notification.

## Notable Semantics

If running as PID 1, the daemon skips mount namespace unsharing because container PID 1 behavior makes that unnecessary or ineffective. On shutdown, it sends a broadcast notification to blocking udev threads.
