# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_2/props.rs

Manager r2 property helper.

Key behavior:
- `stopped_pools_prop()` returns `engine.stopped_pools().await` wrapped in `dbus::types::ManagerR2`.

This backs the manager r2 `StoppedPools` D-Bus property.
