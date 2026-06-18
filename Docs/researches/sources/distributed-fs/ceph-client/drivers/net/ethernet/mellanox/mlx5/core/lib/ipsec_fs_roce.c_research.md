# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/ipsec_fs_roce.c

Purpose: Builds RoCE-specific IPsec flow steering for RX and TX, including MPV slave/master alias flow-table support for cross-vHCA forwarding.

Important APIs and flow: `mlx5_ipsec_fs_roce_init()` discovers RDMA RX/TX IPsec namespaces and stores devcom access. RX create builds a NIC table with RoCE UDP dport rule and miss rule, creates RDMA destination table, and in MPV slave mode creates master-side NIC/RDMA tables plus an alias/goto table. TX create builds an RDMA TX table forwarding to the policy table, or in MPV slave mode creates an alias to the master policy table and matches source VHCA port. Destroy functions remove rules, groups, tables, and aliases. Support helpers include `mlx5_ipsec_fs_roce_ft_get()` and `mlx5_ipsec_fs_is_mpv_roce_supported()`.

State and dependencies: `struct mlx5_ipsec_fs` owns IPv4 RX, IPv6 RX, TX, and a devcom pointer. RX/TX state holds flow tables, groups, rules, alias IDs, access keys, namespaces, and master-side tables. Dependencies include flow steering core/cmds, RDMA and NIC IPsec namespaces, devcom peer iteration, MPV core helpers, random access key generation, and firmware cross-vHCA alias commands.

Risks and test signals: Alias creation is cross-device and has asymmetric allow/create/destroy ownership. MPV event recreation passes `from_event` to reuse alias keys. Tests should cover non-MPV and MPV RX/TX, missing peer or peer IPsec, alias capability failures, IPv4/IPv6 level differences, default destination as flow table with ignore-flow-level, partial create cleanup, double destroy after event cleanup, and support predicate behavior when MP is enabled without alias caps.
