# File Research: sources/block-storage/stratisd/src/engine/strat_engine/engine.rs

This file implements `StratEngine`, the main async Stratis engine for real block storage.

Key responsibilities:
- Holds active pools in `AllOrSomeLock<PoolUuid, AnyPool>`.
- Holds discovered-but-not-active devices in `LiminalDevices`.
- Tracks devicemapper event numbers per watched pool device.
- Owns the kernel keyring action handler.
- Initializes the engine by setting up private namespace filesystem state, verifying external executables, discovering devices, and assembling started pools.

Major operations:
- `create_pool()` validates name, paths, key descriptions, integrity settings, existing ownership, and sector-size compatibility, then initializes V2 pools.
- Test-only `create_pool_legacy()` creates V1 pools for legacy coverage.
- `destroy_pool()` refuses pools with filesystems, removes the pool from the active table, attempts destruction, and on non-restorable failure moves remaining devices to liminal stopped state.
- `rename_pool()` updates pool metadata, reinserts the pool under the new name, and emits udev pool changes.
- `unlock_pool()` starts locked encrypted liminal pools enough to unlock devices and return unlocked device UUIDs.
- `start_pool()` delegates to `LiminalDevices::start_pool()` and moves the result into active pools.
- `stop_pool()` moves active pools into stopped or partially constructed liminal state.
- `refresh_state()` discards current engine state and rebuilds it from device discovery.
- `get_events()`, `pool_evented()`, and `fs_evented()` coordinate devicemapper event checks and timer-based checks.

Concurrency model:
- Async locks protect engine tables.
- Blocking storage and devicemapper work is run through `spawn_blocking`.
- Event handling intentionally takes broad write locks while promoting liminal devices into active pools to avoid duplicate pool registration.

Reporting:
- Implements `Into<Value>` and `Report` to expose active pools, stopped pools, partially constructed pools, and liminal lookup maps.

Tests:
- Integration-style tests cover setup persistence, pool rename, start/stop behavior, and rollback across keyring/Clevis bind, rebind, unbind, and cache cases using loopback and real-device harnesses.
