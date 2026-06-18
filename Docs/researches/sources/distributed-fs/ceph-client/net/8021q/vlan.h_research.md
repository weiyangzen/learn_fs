<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan.h -->
# sources/distributed-fs/ceph-client/net/8021q/vlan.h

This internal header defines the VLAN layer's core data structures and helper APIs. It establishes the VLAN protocol index space, the sparse fixed-range `struct vlan_group` array layout, `struct vlan_info` for a real device, per-net `struct vlan_net`, and prototypes shared among `vlan.c`, `vlan_core.c`, `vlan_dev.c`, netlink, procfs, GVRP, and MVRP code.

Important inline helpers are `vlan_proto_idx()`, `__vlan_group_get_device()`, `vlan_group_get_device()`, `vlan_group_set_device()`, `vlan_find_dev()`, `vlan_tnl_features()`, `vlan_group_for_each_dev`, and `vlan_get_ingress_priority()`. The group array is split into eight parts to give constant-time VID lookups while allocating only chunks that are needed. `__vlan_group_get_device()` pairs an `smp_rmb()` with preallocation's write barrier so readers see initialized arrays.

State is not allocated here, but the header codifies persistent in-memory state: real-device VLAN groups, VID lists, optional proc entries, and namespace naming policy. Optional GVRP/MVRP and procfs APIs compile to stubs when disabled.

Risks include invalid protocol handling, memory-order assumptions for group array publication, and callers using `vlan_find_dev()` without RTNL or RCU. Tests should cover protocol index validation, lookup after preallocation/publication, optional configuration builds, and ingress priority mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan.h -->
