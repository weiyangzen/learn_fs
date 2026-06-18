# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_common.c

Purpose: owns mlx5e global NIC resources shared by all mlx5e netdevices on a core device: protection domain, transport domain, mkey, BlueFlame doorbells, TIS objects, crypto DEK private state, and TIR loopback refresh.

Important APIs, types, and functions: `mlx5e_mkey_set_relaxed_ordering()` encodes relaxed ordering bits from device and PCI capabilities. `mlx5e_create_mkey()` creates a physical-address-mode mkey with local read/write. `mlx5e_create_tis()` wraps core TIS creation with transport domain and LACP affinity. `mlx5e_create_mdev_resources()` allocates the shared resource bundle. `mlx5e_destroy_mdev_resources()` tears it down. `mlx5e_modify_tirs_lb()` and `mlx5e_refresh_tirs()` update self-loopback behavior for all TIRs in the transport domain list.

Control flow: resource creation allocates PD, TD, mkey, doorbell records up to the devlink configured count and max channels, optional per-port/per-TC TISes, initializes the TD TIR list lock, and initializes crypto DEK support. Failure unwinds in reverse order. Destruction cleans crypto, TISes, bfregs, mkey, TD, PD, and clears the resource struct.

State and persistence: resources persist in `mdev->mlx5e_res.hw_objs` for the device lifetime. TIRs are tracked in a list under `td.list_lock`. `tisn_valid`, `num_bfregs`, and `dek_priv` record which optional resources were created.

Dependencies and integration points: depends on devlink params, mlx5 core PD/TD/mkey/TIS/bfreg APIs, LAG helpers, crypto DEK init/cleanup, and TIR builder/modify helpers. kTLS, MACsec, PSP, queues, and TIR/TIS users rely on these shared objects.

Risks: partial doorbell allocation is tolerated, so later code must respect `num_bfregs`. DEK init failure is logged but not fatal, which can disable crypto offloads later. TIS affinity logic depends on LAG port count and capabilities. TIR refresh is skipped when firmware supports TIS/TIR TD ordering.

Test signals: probe/remove resource lifecycle, devlink num-doorbells variation, LAG affinity, TIS creation failure unwind, DEK init failure, TIR loopback modification, and repeated reloads.
