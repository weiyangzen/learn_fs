# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_0/props.rs

Manager r0 property helpers.

Properties:
- `version_prop()` returns `stratis::VERSION`.
- `locked_pools_prop()` returns `engine.locked_pools().await`.

Used by manager r0 and r1.
