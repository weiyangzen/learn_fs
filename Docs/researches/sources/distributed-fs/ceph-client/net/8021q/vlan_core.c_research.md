<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_core.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlan_core.c

This file implements VLAN receive demux, VID bookkeeping, hardware filter programming, and VLAN GRO offload support. It exports lookup and VID-management APIs used by drivers and the VLAN module.

`vlan_do_receive()` maps an skb's hardware-accelerated VLAN tag to a VLAN device, clones if needed, drops if the VLAN is down, optionally reinserts the VLAN header when reorder is disabled, maps ingress priority, clears the accel tag, and updates per-CPU RX stats. `__vlan_find_dev_deep_rcu()` searches a device's VLAN group or recurses to a master upper. Accessors expose real device, VLAN id, and VLAN protocol.

VID state is held in `struct vlan_info` attached to the real device and a `vid_list` of `struct vlan_vid_info` reference-counted entries. `vlan_vid_add()` allocates `vlan_info` on demand, programs hardware filters through `ndo_vlan_rx_add_vid`, increments refcounts, and publishes with RCU. `vlan_vid_del()` decrements, removes hardware filters, and frees the whole `vlan_info` via RCU when no VIDs remain. Bulk helpers copy/drop VID filters between devices.

GRO integration registers packet offloads for 802.1Q and 802.1ad. `vlan_gro_receive()` parses VLAN headers, compares VLAN headers across candidate flows, pulls the VLAN header, and delegates to inner IPv4/IPv6 GRO. `vlan_gro_complete()` delegates completion by inner ethertype.

Dependencies include skb VLAN metadata, netdevice hardware filter ops, RCU, RTNL, per-CPU u64 stats, GRO APIs, and VLAN header parsing. Risks include refcount imbalance, filter programming unwind, RCU lifetime mistakes, down-device skb drops, and GRO parsing of malformed headers. Tests should cover RX demux with reorder on/off, down VLAN drops, priority maps, VID add/del refcounts, hardware filter push/drop/unwind, master-upper recursive lookup, and VLAN GRO aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_core.c -->
