# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_4/methods.rs

Purpose: Implements the r4 manager `start_pool_method`.

Key behavior:
- Accepts an `id` plus `id_type` string.
- Supports `id_type == "uuid"` via `PoolUuid::parse_str`.
- Supports `id_type == "name"` via `Name::new`.
- Rejects unknown id types with `DbusErrorEnum::ERROR`.
- Converts the optional unlock tuple into `TokenUnlockMethod`.
- Calls `engine.start_pool(..., None, false)`.

D-Bus object lifecycle:
- On `StartAction::Started`, fetches the pool, registers each filesystem, then registers the pool and block devices.
- Emits locked-pools signals for encrypted pools.
- Emits stopped-pools signals after successful start.
- Returns identity as OK with the default false/empty result.

Failure handling:
- Converts parsing, registration, and engine errors through `engine_to_dbus_err_tuple`.
