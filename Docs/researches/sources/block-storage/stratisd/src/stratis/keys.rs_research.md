# File Research: sources/block-storage/stratisd/src/stratis/keys.rs

## Purpose

Runs an async task that reacts to newly added key descriptions and attempts to load volume keys for matching encrypted pools.

## Main Types and Behavior

- `load_vks` waits on an optional key-description receiver.
- For each key description, it scans active pools for encrypted pools whose encryption info contains the sent key description.
- For each matching pool UUID, it obtains a mutable pool guard and runs `load_volume_key` in a blocking task.
- Logs success, recoverable load failures, join failures, and missing pools.

## Integration Points

Started from `stratis/run.rs` with a receiver created during real `StratEngine` initialization.

## Notable Semantics

If no receiver is provided, the task awaits forever using `futures::future::pending()`, which keeps the runtime branch alive without consuming CPU.
