# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/port_sel.c

Purpose: Builds hardware port-selection steering for mlx5 LAG. It creates match definers and hash-split flow tables so traffic buckets can forward to chosen uplink VHCA IDs, with optional inner-tunnel classification.

Important APIs and flow: `mlx5_lag_port_sel_create()` maps the requested `netdev_lag_hash` to traffic types, creates outer and optional inner definers for each TTC type, then creates inner and outer TTC tables. Definer setup chooses firmware match-definer formats for IPv4/IPv6, L4, MAC, VLAN, and inner/outer header fields. `mlx5_lag_create_port_sel_table()` creates a port-selection table, hash flow group, and one rule per LAG port/bucket with destination VHCA ID from the `ports[]` map. `mlx5_lag_port_sel_modify()` updates rule destinations for changed bucket mappings; `mlx5_lag_port_sel_destroy()` tears down TTCs, groups, tables, rules, and definers.

State and dependencies: `ldev->port_sel` owns the traffic-type bitmap, tunnel flag, outer/inner TTC handles, and definer arrays. The code depends on firmware port-selection namespace, match definers, TTC helpers from `lib/fs_ttc`, LAG bucket/v2p maps, VHCA IDs, and eswitch-enabled builds.

Risks and test signals: Error unwinding is nested across definer creation, tables, flow groups, and hundreds of rules; partial cleanup must preserve index math. Tests should exercise hash modes `L23`, `L34`, `E23`, `E34`, VLAN+src MAC, unsupported namespace/caps, tunnel inner TTC support, bucket remap modifications, and destroy after partial create failures.
