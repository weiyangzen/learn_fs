# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_6/methods.rs

Purpose: Implements the r6 manager `stop_pool_method`.

Key behavior:
- Accepts `id` and `id_type`, supporting `uuid` and `name`.
- Captures blockdev and filesystem UUIDs before stopping.
- Calls `engine.stop_pool(id.clone(), true)`.
- After stop attempt, compares remaining devices/filesystems and unregisters removed D-Bus objects.
- On full or partial stop, unregisters the pool object and emits stopped-pools signals.
- Emits locked-pools signals when stopped-pool metadata indicates lock information is available.

Return semantics:
- `Identity`: OK with default result.
- `Stopped`: OK with stopped pool UUID string.
- `Partial`: error return string explaining some component devices were not torn down.
- `CleanedUp`: marked unreachable in this code path.
- Engine errors are converted to D-Bus error tuples.

Important detail:
- Cleanup logic runs for `Stopped`, `Partial`, and even `Err(_)` to remove objects that disappeared despite the final action status.
