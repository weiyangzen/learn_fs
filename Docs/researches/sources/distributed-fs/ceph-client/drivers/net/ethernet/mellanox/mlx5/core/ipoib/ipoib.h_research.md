# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ipoib.h

## Purpose
`ipoib/ipoib.h` is the internal interface for mlx5 enhanced IPoIB support. It defines IPoIB private state, wire-format constants, TX WQE layout, profiles, ethtool ops, QPN hash APIs, underlay QP/TIS APIs, and parent-child reference helpers.

## Important APIs, Types, And Functions
- `struct mlx5i_priv` extends `rdma_netdev` and stores underlay QPN, TISN, subinterface state, qkey, pkey index, QPN-to-netdev hash table, parent netdev, and flexible storage for embedded `mlx5e_priv`.
- Constants describe IPoIB GRH, encapsulation, pseudo-header, hard-header length, and single-TC limit.
- `struct mlx5i_tx_wqe` lays out IPoIB TX WQEs with control, datagram, pad, Ethernet segment, and data segments.
- Declarations cover TIS/QP lifecycle, pkey hash-table operations, shared netdev operations, profile lifecycle, RX update, pkey profile lookup, TX, stats, and parent ref management.
- `mlx5i_epriv(netdev)` extracts the embedded `mlx5e_priv`.

## Control Flow And State
The header supports a two-layer private layout where `struct mlx5i_priv` is the netdev private object and the embedded/flexible `mlx5e_priv` carries common Ethernet-channel machinery. Parent devices own RX resources and QPN mapping; pkey child devices reference parent resources and use the hash table to map underlay QPNs back to netdevs.

## Dependencies And Integration Points
It is compiled only under `CONFIG_MLX5_CORE_IPOIB`, depends on mlx5 flow steering and `en.h`, and is consumed by `ipoib.c`, `ipoib_vlan.c`, ethtool support, RX handlers, and TX implementation. It bridges RDMA netdev callbacks with mlx5e infrastructure.

## Risks And Edge Cases
The private layout relies on `mlx5i_priv` being first-compatible with `rdma_netdev` and on `mlx5i_epriv` pointer arithmetic. Parent/child QPN hash access must be synchronized with NAPI and RTNL assumptions. The TX WQE layout must match firmware expectations exactly.

## Test Signals
Build with and without `CONFIG_MLX5_CORE_IPOIB`, validate private-size allocation, parent and pkey netdev setup, QPN hash lookup during receive, TX WQE posting, and correct behavior when child devices outlive or release parent references.
