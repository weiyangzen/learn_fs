# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/net/debug.c

Purpose: debugfs support for mlx5 vDPA net devices, exposing TIR/RX flow-table identifiers and optional steering counters.

Important APIs/types/functions: `mlx5_vdpa_add_debugfs()` creates a per-vDPA debugfs dir under the mlx5 device root and an `rx` child. `mlx5_vdpa_add_tirn()`/remove expose `tirn`; `mlx5_vdpa_add_rx_flow_table()`/remove expose RX table id. Under `CONFIG_MLX5_VDPA_STEERING_DEBUG`, counter files expose packets/bytes from `mlx5_fc_query()` for unicast and multicast rules.

Control flow: vnet setup creates debugfs early, then adds flow table and TIR entries when those resources exist. Teardown removes the same dentries. Counter nodes are created per MAC/VLAN steering node and recursively removed with the node.

State and persistence: debugfs dentries are cached in `mlx5_vdpa_net`, resource structs, and `macvlan_node` counters. Values are live hardware queries; no persistence.

Dependencies and integration: called from `mlx5_vnet.c` setup/teardown and steering rule management. Depends on debugfs, mlx5 flow counters, and mlx5 device debugfs root.

Risks: debugfs creation failures are mostly tolerated, so callers must not assume dentries exist. Counter creation has partial-failure paths where one child may be missing.

Test signals: debugfs tree after vDPA add, TIR/table files after setup, counter files with steering debug enabled, hot remove cleanup, and counter query error handling.
