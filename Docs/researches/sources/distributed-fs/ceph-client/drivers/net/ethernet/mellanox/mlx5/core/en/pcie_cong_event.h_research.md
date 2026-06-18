# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/pcie_cong_event.h

Purpose: declares the PCIe congestion event lifecycle hooks for mlx5e.

Important APIs/functions: `mlx5e_pcie_cong_event_init` and `mlx5e_pcie_cong_event_cleanup`.

Control flow: the driver calls init during private feature setup and cleanup during teardown; unsupported hardware returns success without installing state.

State and persistence: no header state; implementation stores `priv->cong_event` and a firmware general object.

Dependencies and integration: assumes `struct mlx5e_priv` is available to callers through mlx5e core headers.

Risks: callers must pair cleanup with successful or partially successful init paths because init can allocate and then fail during notifier/object setup.

Test signals: build coverage, init/cleanup pairing, and stats group visibility when `priv->cong_event` is present.
