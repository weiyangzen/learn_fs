# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/gid.c

Purpose: Manages reserved RoCE GID table indices and programs RoCE address entries into mlx5 firmware.

Important APIs and flow: `mlx5_init_reserved_gids()` initializes an IDA and positions the reserved range at the end of the firmware GID table. `mlx5_core_reserve_gids()` moves the reserved start downward and increases count with exhaustion checks; `mlx5_core_unreserve_gids()` reverses it. `mlx5_core_reserved_gid_alloc()` allocates a concrete index from the reserved range; `mlx5_core_reserved_gid_free()` releases it. `mlx5_core_roce_gid_set()` builds and sends `SET_ROCE_ADDRESS`, optionally filling VLAN, MAC, GID, RoCE version/L3 type, and VHCA port number.

State and dependencies: State lives in `dev->roce.reserved_gids` (`ida`, start, count). Dependencies include RoCE capabilities, Ethernet port type, Linux IDA, ether address helpers, mlx5 command layout, and exported symbols for RDMA users.

Risks and test signals: Reserve/unreserve is not internally locked here, so callers must serialize if needed. Tests should cover table exhaustion, max reserved limit, alloc/free range bounds, cleanup warning on leaked IDs, clearing a GID by passing NULL, VLAN programming, non-Ethernet rejection, and multi-vHCA port programming.
