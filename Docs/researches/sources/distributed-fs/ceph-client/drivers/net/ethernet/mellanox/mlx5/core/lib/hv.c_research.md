# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv.c

Purpose: Wraps Hyper-V PCI config block access for mlx5 devices and exposes invalidate callback registration.

Important APIs and flow: `mlx5_hv_read_config()` and `mlx5_hv_write_config()` call a shared validator that requires block-aligned offsets and exact `HV_CONFIG_BLOCK_SIZE_MAX` length, computes block ID, invokes Hyper-V read/write helpers, verifies read byte count, and logs failures. `mlx5_hv_register_invalidate()` registers a block invalidate callback; unregister clears it.

State and dependencies: No persistent state is stored here; operations are immediate calls against `dev->pdev`. Depends on `CONFIG_PCI_HYPERV_INTERFACE`, Linux Hyper-V PCI helpers, and mlx5 logging.

Risks and test signals: Partial reads become `-EIO`, and invalid sizes/offsets return `-EINVAL`. Tests should cover alignment, block ID mapping, read byte count mismatch, callback register/unregister, and Hyper-V-disabled builds via the header.
