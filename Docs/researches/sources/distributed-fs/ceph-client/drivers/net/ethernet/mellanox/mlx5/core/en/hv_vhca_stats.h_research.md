# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/hv_vhca_stats.h

Purpose: provides the conditional public entry points for mlx5e Hyper-V vHCA stats export.

Important APIs/functions: declares `mlx5e_hv_vhca_stats_create` and `mlx5e_hv_vhca_stats_destroy` when `CONFIG_PCI_HYPERV_INTERFACE` is enabled; otherwise supplies no-op inline stubs.

Control flow: main driver code can call create/destroy unconditionally, with the compile-time option deciding whether a real vHCA stats agent is installed.

State and persistence: no state in the header; the implementation stores its agent state in `mlx5e_priv`.

Dependencies and integration: includes `en.h` for `struct mlx5e_priv`; bridges mlx5e channel stats with the Hyper-V PCI interface.

Risks: no-op stubs mean tests on non-Hyper-V builds do not exercise agent lifecycle or delayed-work cancellation.

Test signals: build both enabled and disabled configurations, and verify callers do not need additional ifdefs.
