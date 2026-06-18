# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_9/methods.rs

Purpose: Implements r9 manager `start_pool_method`.

Key behavior:
- Extends r8 start behavior with `remove_cache: bool`.
- Supports `uuid` and `name` id types.
- Accepts optional nested unlock method and optional key fd.
- Calls `engine.start_pool(..., key_fd, remove_cache)`.
- Registers filesystems first, then pool and blockdevs.
- Emits locked-pools signals for encrypted pools and stopped-pools signals after start.

Version-specific note:
- The only visible r9 method change here is exposing `remove_cache` through D-Bus start-pool semantics.

Failure handling:
- Unknown id types, UUID parse failures, missing newly started pool, registration failures, and engine errors return structured D-Bus tuples.
