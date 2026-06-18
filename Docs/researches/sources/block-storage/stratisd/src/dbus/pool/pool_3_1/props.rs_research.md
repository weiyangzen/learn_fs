# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_1/props.rs

Purpose: Implements r1 pool property adapters and setter signal hooks.

Properties:
- `fs_limit_prop`: returns pool filesystem limit.
- `enable_overprovisioning_prop`: returns overprovisioning mode.
- `no_alloc_space_prop`: returns whether the pool is out of allocation space.

Setters:
- `set_fs_limit_prop` calls `p.set_fs_limit(&name, uuid, fs_limit)`.
- `set_enable_overprovisioning_prop` calls `p.set_overprov_mode(&name, enable_overprov)`.

Signal hooks:
- `send_fs_limit_signal_on_change` emits the fs-limit property signal for the pool path.
- `send_enable_overprovisioning_signal_on_change` emits overprovisioning change signal.
- Missing pool path is logged as a warning.
