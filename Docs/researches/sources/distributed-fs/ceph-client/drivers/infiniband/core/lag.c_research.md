# sources/distributed-fs/ceph-client/drivers/infiniband/core/lag.c

## Purpose
This file implements RDMA LAG helper logic for selecting the correct transmit slave for RoCEv2 address handles over bonded netdevices. It synthesizes a minimal Ethernet/IP/UDP packet from an RDMA address handle so the networking stack's bond hashing logic can choose the same egress slave that real traffic should use.

## Important APIs, Types, And Functions
The public APIs are `rdma_lag_get_ah_roce_slave()` and `rdma_lag_put_ah_roce_slave()`. Internal helpers are `rdma_build_skb()` and `rdma_get_xmit_slave_udp()`. Inputs are `struct ib_device`, `struct rdma_ah_attr`, GRH/GID attributes, RoCE destination MAC, and the source GID's netdevice.

## Control Flow
`rdma_lag_get_ah_roce_slave()` filters to RoCE UDP-encap AHs with nonzero flow label, reads and holds the source GID netdevice under RCU, and returns NULL if it is not a bond master. For bond masters, it builds a temporary skb with Ethernet, IPv4 or IPv6, and UDP headers. UDP source port is derived from the RDMA flow label, destination port is RoCEv2, IP addresses come from SGID/DGID, and MAC addresses come from GID L2 fields and AH attributes. The skb is passed to `netdev_get_xmit_slave()`, the selected slave is referenced, and callers release it with `rdma_lag_put_ah_roce_slave()`.

## State And Persistence
No persistent state is owned here. The helper takes temporary references on the master and selected slave netdevices and allocates a temporary skb for hashing. `device->lag_flags` influences whether bond hashing may use all slaves through `RDMA_LAG_FLAGS_HASH_ALL_SLAVES`.

## Dependencies And Integration Points
The file depends on RDMA address handle/GID cache helpers, RoCEv2 UDP constants, Linux skbuff/header helpers, RCU, and bonding/LAG netdevice APIs. It is used by RDMA paths that need a concrete egress slave for AH operations in bonded RoCE configurations.

## Risks And Test Signals
Risks include synthetic headers choosing a different slave than real packets, zero flow labels bypassing selection, incorrect IPv4-mapped IPv6 detection, GID netdevice lifetime races, NULL/error returns from `netdev_get_xmit_slave()`, and source MAC extraction mismatches for VLAN/bond setups. Tests should cover IPv4-mapped and IPv6 RoCEv2 AHs over bonds, non-bond devices, zero flow label, non-RoCE GIDs, hash-all-slaves behavior, skb allocation failure, MAC validation, reference balance, and comparison with real UDP flow hashing.
