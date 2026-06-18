# File Research: sources/block-storage/stratisd/src/engine/sim_engine/engine.rs

This file implements `SimEngine`, an in-memory implementation of the `Engine` trait.

State:
- `pools`: active pools in an `AllOrSomeLock` table.
- `key_handler`: simulated keyring.
- `stopped_pools`: locked table of stopped pools.

Reporting:
- Converts active and stopped pools into JSON arrays.
- `engine_state_report()` returns full simulator state.
- `get_report(StoppedPools)` returns stopped pool state only.

Core engine behavior:
- `create_pool()`:
  - validates name and paths;
  - validates integrity spec;
  - converts input encryption info, checking simulated keyring when available;
  - returns identity for identical existing pool specs;
  - requires at least one blockdev;
  - deduplicates input blockdev paths.
- `destroy_pool()`:
  - refuses to destroy pools with filesystems;
  - removes active pool and calls `destroy()`;
  - returns identity for absent pool.
- `rename_pool()`:
  - uses shared rename precheck;
  - removes and reinserts pool under new name.
- `unlock_pool()`:
  - returns empty success; simulator has no real locked-device setup.
- `start_pool()`:
  - returns identity for already active pools after validating unlock/passphrase consistency.
  - moves stopped pools back to active.
  - can clear cache when `remove_cache` is requested.
- `stop_pool()`:
  - returns identity if already stopped.
  - moves active pool to stopped table.
  - errors if missing.
- Event/diff methods return empty sets/maps because the simulator has no real udev/device-mapper events.
- `refresh_state()` is a no-op.
- `is_sim()` returns true.

Stopped pool metadata:
- `stopped_pools()` builds `StoppedPoolsInfo` from stopped simulator pools, including devices, metadata version v2, and feature flags derived from encryption state.

Locking:
- Implements trait guard methods by converting simulator guards into dyn `Pool` guards.
- `upgrade_pool()` delegates to table upgrade logic.

Tests:
- Cover missing pool lookups, destroy behavior, create idempotence/conflicts, duplicate devices, and rename cases.

Role in architecture:
- `SimEngine` lets D-Bus and higher-level logic exercise the real `Engine` contract without requiring real block devices, cryptsetup, or device-mapper state.
