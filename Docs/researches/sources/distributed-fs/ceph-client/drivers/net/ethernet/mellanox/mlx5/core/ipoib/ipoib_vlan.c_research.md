# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ipoib_vlan.c

## Purpose
`ipoib/ipoib_vlan.c` implements pkey child-interface support for mlx5 IPoIB. It provides a QPN-to-netdev hash table shared with the parent, child netdev operations, and a child mlx5e profile that reuses parent RX resources while creating child-specific TX QP/TIS state.

## Important APIs, Types, And Functions
- `struct qpn_to_netdev` and `struct mlx5i_pkey_qpn_ht` implement a small hash table guarded by `spin_lock_bh`.
- Public hash APIs are `mlx5i_pkey_qpn_ht_init`, cleanup, add, delete, and lookup.
- Child netdev operations implement open, close, init, cleanup, MTU change, stats, and hardware timestamp get/set.
- `mlx5i_pkey_nic_profile` overrides parent profile behavior for pkey devices.
- `mlx5i_pkey_get_profile` returns the child profile to `ipoib.c`.

## Control Flow And State
Parent device initialization allocates the QPN hash table. Child `ndo_init` obtains and references the parent with RTNL held, verifies the child has at least as many RX queues as the parent, copies the parent's QPN hash pointer, and then calls common `mlx5i_dev_init` to set address bytes and add its QPN mapping.

Child open transitions the underlay QP, adds its QPN to RX flow steering, creates a child TIS, opens channels, refreshes RX, and activates channels. Close reverses those operations. Child RX init/cleanup are no-ops because RX resources are owned by the parent. Child MTU change only writes the netdev MTU under state lock rather than switching shared RX parameters.

## State And Persistence Behavior
State includes parent `num_sub_interfaces`, child `parent_dev`, shared QPN hash table, child underlay QPN/TISN, and mlx5e channel state. Hardware state includes per-child underlay QP, child TIS, and RX underlay QPN steering entry. There is no persistent storage.

## Dependencies And Integration Points
The file depends on `ipoib.h`, Linux hash lists, RTNL parent lookup, mlx5e channel helpers, flow steering underlay QPN APIs, and the common IPoIB functions in `ipoib.c`. RX handlers can use the hash table to map packets by underlay QPN.

## Risks And Edge Cases
`mlx5i_pkey_del_qpn` looks up before taking the hash lock, while the table is documented as synchronized with NAPI; changes here need careful concurrency review. Child init must release parent references on failures. Shared RX resources mean child queue counts and MTU behavior are constrained by the parent. Open failure unwinding must destroy TIS and remove QPN steering in the right order.

## Test Signals
Create/delete pkey child interfaces, open/close them under traffic, validate QPN lookup, parent channel-change rejection while children exist, child MTU updates, failure injection in QP/TIS/channel creation, and parent reference/hash cleanup after child removal.
