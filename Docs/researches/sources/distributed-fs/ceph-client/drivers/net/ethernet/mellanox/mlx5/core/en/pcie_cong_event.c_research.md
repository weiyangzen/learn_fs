# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/pcie_cong_event.c

Purpose: creates a firmware PCIe congestion event object, handles object-change events, and exposes high/low/stale transition counters through the mlx5e stats framework.

Important APIs/functions: `mlx5e_pcie_cong_event_init`, `mlx5e_pcie_cong_event_cleanup`, firmware command helpers for create/destroy/query, threshold config retrieval/validation, the EQ notifier, and stats group callbacks.

Control flow: init exits if unsupported, reads driverinit devlink threshold parameters, validates low < high for inbound/outbound directions, allocates state, creates a general object of type `PCIE_CONG_EVENT`, registers an OBJECT_CHANGE notifier, and stores it in `priv->cong_event`. Events queue work that queries the object, compares new inbound/outbound high-state bits with the last state, increments transition counters, and counts stale events when no bit changed. Cleanup unregisters the notifier, cancels work, destroys the object, and frees memory.

State and persistence: `struct mlx5e_pcie_cong_event` holds the firmware object id, last state, notifier/work, and ethtool stats. Firmware configuration persists while the object exists.

Dependencies and integration: uses devlink params from `devlink.h`, mlx5 general-object commands, EQ notifier infrastructure, and the mlx5e stats group macro system.

Risks: threshold parameters are driverinit values, so runtime changes may require reinit. Query initializes `new_cong_state` in the caller, and stale event counts can reveal duplicate notifications. Destroy errors are logged but cannot be repaired.

Test signals: unsupported devices, invalid threshold devlink values, create/register rollback, simulated object-change events, stale events, and cleanup with pending work.
