# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/bridge.h

Purpose: declares representor bridge-offload lifecycle hooks with compile-time stubs.

Important APIs/functions: `mlx5e_rep_bridge_init` and `mlx5e_rep_bridge_cleanup`, real when `CONFIG_MLX5_BRIDGE` is enabled and no-op otherwise.

Control flow: representor setup can call init/cleanup unconditionally; configuration controls whether switchdev bridge offload support is installed.

State and persistence: no header state. Implementation state is eswitch bridge offload context and notifiers.

Dependencies and integration: includes `en.h`; integrates representor initialization with optional eswitch bridge support.

Risks: non-bridge builds skip all bridge offload logic, so tests must cover both stub and enabled paths.

Test signals: build configurations with and without `CONFIG_MLX5_BRIDGE` and representor bridge lifecycle.
