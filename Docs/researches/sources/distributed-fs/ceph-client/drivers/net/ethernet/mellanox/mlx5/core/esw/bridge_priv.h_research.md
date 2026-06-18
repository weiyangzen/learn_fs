# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge_priv.h

Purpose: Defines private bridge-offload table sizing, flow-table levels, flags, keys, state objects, and internal function contracts shared by `bridge.c`, `bridge_mcast.c`, `bridge_debugfs.c`, and bridge tracepoints.

Important APIs/types/functions: Defines large fixed group sizes and index ranges for ingress, egress, skip, and multicast tables, with static asserts for total sizes. Key state types are `mlx5_esw_bridge_fdb_entry`, `mlx5_esw_bridge_mdb_entry`, `mlx5_esw_bridge_vlan`, `mlx5_esw_bridge_port`, and `mlx5_esw_bridge`. It declares helper functions for table creation, port keys, multicast/MDB init/cleanup, debugfs, and bridge multicast enable/disable.

Control flow and integration: The table constants are used directly when creating hardware flow groups so group ordering matches match specificity. Private structs link software bridge state to flow handles, counters, packet reformat objects, modify headers, rhashtables, xarrays, and list nodes. The declarations define how unicast, multicast, debugfs, and tracepoint files interoperate without exposing internals in public `bridge.h`.

State and persistence: This header defines all persistent in-memory bridge offload state. FDB entries hold ingress/egress/filter flow handles and counters; VLANs own push/pop/mcast resources; ports own VLAN xarrays and multicast tables; bridges own FDB/MDB tables and egress resources.

Risks and test signals: Risks include changing group size/index constants without preserving total table sizes, adding fields without cleanup coverage, or using port keys inconsistently across xarrays. Test signals include build-time static asserts, runtime bridge table creation, VLAN and multicast behavior across all table groups, and leak-free cleanup on bridge destruction.
