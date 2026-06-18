# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_8/props.rs

Purpose: Provides the r8 manager stopped-pools property adapter.

Key behavior:
- Calls `engine.stopped_pools().await`.
- Wraps the result in `dbus::types::ManagerR8<StoppedPoolsInfo>`.

Dependencies:
- `Arc<dyn Engine>`.
- `StoppedPoolsInfo`.
- `types::ManagerR8`.

Role in API evolution:
- Separates r8 stopped-pools serialization from older `ManagerR2` serialization.
