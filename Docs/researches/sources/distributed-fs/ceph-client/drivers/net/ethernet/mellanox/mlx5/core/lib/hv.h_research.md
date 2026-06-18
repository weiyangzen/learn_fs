# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv.h

Purpose: Declares Hyper-V config block access functions for mlx5 when the PCI Hyper-V interface is enabled.

Important APIs and types: Exports read/write config helpers and invalidate callback registration/unregistration under `CONFIG_PCI_HYPERV_INTERFACE`. The callback reports a block mask to a caller-provided context.

State and dependencies: Includes Hyper-V and mlx5 driver headers only in the enabled branch, leaving no declarations otherwise.

Risks and test signals: Users must guard calls by config availability or include paths that only compile when declarations exist. Build tests should include Hyper-V interface enabled and disabled.
