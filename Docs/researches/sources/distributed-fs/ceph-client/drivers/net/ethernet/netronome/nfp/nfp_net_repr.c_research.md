# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_repr.c

## Purpose

`nfp_net_repr.c` implements NFP representor netdevices for physical ports, PF ports, and VF ports. Representors expose switch-facing ports to Linux, forward transmitted skbs to a lower PF netdev using metadata destination port IDs, provide hardware and CPU-hit statistics, inherit supported offloads from lower-device representor capability TLVs, and manage representor allocation/cleanup sets.

## Important APIs, Types, and Functions

Public functions include `nfp_repr_get_locked()`, `nfp_repr_inc_rx_stats()`, `nfp_repr_transfer_features()`, `nfp_repr_init()`, `nfp_repr_free()`, `nfp_repr_alloc_mqs()`, `nfp_repr_clean_and_free()`, `nfp_reprs_clean_and_free()`, `nfp_reprs_clean_and_free_by_type()`, `nfp_reprs_alloc()`, and `nfp_reprs_resync_phys_ports()`. `nfp_repr_netdev_ops` binds open, stop, xmit, MTU, stats, offload-stats, phys-port naming, TC, VF controls, feature fixing, MAC setting, and parent-ID ops.

## Control Flow

Initialization assigns lockdep classes, stores port/app pointers, allocates a `metadata_dst` with `METADATA_HW_PORT_MUX`, records the firmware control-message port ID and lower PF netdev, configures feature flags from `nn->tlv_caps.repr_cap`, calls app-specific init, and registers the netdev. TX drops any previous dst, attaches the representor metadata dst, rewrites `skb->dev` to the lower device, queues via `dev_queue_xmit()`, and records per-CPU TX stats or drops. Open/stop configure the physical port and call app-specific representor hooks.

## State and Persistence Behavior

Persistent state lives in `struct nfp_repr`: netdev pointer, metadata dst, associated `struct nfp_port`, app pointer, per-CPU stats, and app-private data. `struct nfp_reprs` stores RCU-protected representor netdev arrays. Cleanup unregisters the netdev, calls app cleanup/preclean hooks, releases metadata dst, frees ports, synchronizes RCU when removing app references, and frees per-CPU stats/netdev memory.

## Dependencies and Integration Points

Representors depend on Linux netdev metadata dst support, RCU, per-CPU u64 stats, lower PF netdev capabilities, `nfp_app` representor hooks, NFP port helpers, SR-IOV ndo wrappers, MAC stats offsets, vNIC stats offsets from `nfp_net_ctrl.h`, and ethtool port ops.

## Risks and Edge Cases

Feature transfer must intersect with lower-device features while preserving software and HW TC flags. Statistics are switch-perspective for vNIC ports, so RX/TX counters are intentionally flipped. `nfp_reprs_resync_phys_ports()` removes invalid physical-port representors in place and must synchronize RCU before freeing. TX always returns `NETDEV_TX_OK`; errors are reflected in representor stats, not netdev queue backpressure.

## Test Signals

Exercise physical/PF/VF representor creation, packet TX/RX CPU-hit stats, hardware stats on MAC and vNIC ports, MTU propagation, feature changes on lower devices, TC offload enable/disable, VF ndo passthrough, port invalidation during ETH-table refresh, and teardown under concurrent RCU readers.
