# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/fs_tcp.c

Purpose: builds accelerated TCP flow-steering tables used primarily by kTLS RX to direct selected TCP sockets to dedicated TIRs before default TTC handling.

Important APIs/types/functions: `mlx5e_accel_fs_tcp_create`, `mlx5e_accel_fs_tcp_destroy`, `mlx5e_accel_fs_add_sk`, and `mlx5e_accel_fs_del_sk`. Internals include IPv4/IPv6 match builders, default rule creation, grouped flow table creation, TTC enable/disable, and table destroy helpers.

Control flow and state: create allocates `struct mlx5e_accel_fs_tcp`, builds IPv4 and IPv6 TCP tables with a large exact-match group and one default group, inserts default rules forwarding to TTC defaults, then modifies TTC TCP traffic types to point at acceleration tables. Per-socket add builds a flow spec from socket local/remote addresses and ports, selects IPv4 or IPv6 table including v4-mapped IPv6 handling, sets optional flow tag, and forwards to the socket TIR. Destroy disables TTC redirection, deletes default rules/tables, and clears the fs pointer.

Dependencies and integration: depends on mlx5 flow steering core, TTC tables, `mlx5e_flow_steering` accel TCP storage, Linux socket address state, and kTLS RX rule work.

Risks and test signals: address/port direction is easy to invert because RX matching uses remote source to local destination; TTC must be restored on destroy; IPv6 support is conditional. Test create without outer IP version capability, add IPv4/IPv6/v4-mapped socket rules, default fallthrough, destroy during active TLS contexts, and rule add failures.
