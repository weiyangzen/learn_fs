# File Research: sources/block-storage/stratisd/src/engine/sim_engine/blockdev.rs

This file defines the simulated block device implementation `SimDev`.

State:
- `devnode`
- optional `user_info`
- optional `hardware_info`
- `initialization_time`

Trait implementation:
- Implements `BlockDev`.
- `devnode()` and `metadata_path()` both return the simulated path.
- `size()` always reports 1 GiB.
- `new_size()` always returns `None`.
- `metadata_version()` always returns `StratSigblockVersion::V2`.

Construction and mutation:
- `SimDev::new()` creates a new random `DevUuid` and records timestamp using `now_to_timestamp()`.
- `set_user_info()` uses the shared macro to update only on change.

Serialization:
- Converts `&SimDev` into JSON containing path and size.

Role in architecture:
- This is the simulator’s minimal `BlockDev` implementation. It provides stable, fake blockdev metadata sufficient for tests and D-Bus/report behavior without touching real devices.
