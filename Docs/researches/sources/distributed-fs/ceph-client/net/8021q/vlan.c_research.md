<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlan.c

This file is the main VLAN module lifecycle and legacy ioctl control plane. It registers per-net namespace state, netdevice notifiers, GVRP/MVRP helpers, rtnetlink ops, and the legacy VLAN ioctl handler.

Key functions are `register_vlan_dev()`, `unregister_vlan_dev()`, `vlan_check_real_dev()`, `register_vlan_device()`, `vlan_device_event()`, and `vlan_ioctl_handler()`. Device registration adds the VID to the real device, initializes GVRP/MVRP applicants when the first VLAN appears, preallocates the VLAN group array slot, registers the netdevice, links it as an upper device, publishes it in the VLAN group, and updates features. Unregistration withdraws GVRP/MVRP, clears the group slot, unlinks the upper device, queues netdevice unregister, tears down applicants when the last VLAN leaves, and drops the VID reference.

Netdevice notifier flow propagates lower-device state to VLAN devices: address changes update inherited or unicast-filtered addresses; MTU changes clamp VLAN MTUs; feature changes refresh offloads; lower down/up closes or opens VLANs unless loose binding is set; unregister removes all VLAN uppers; filter push/drop events program hardware VIDs. It also auto-adds VID 0 to hardware CTAG filters while devices are up.

State includes per-net `struct vlan_net`, per-real-device `struct vlan_info`, VLAN group arrays, proc entries, GVRP/MVRP applicants, and device upper links. Synchronization relies on RTNL, RCU-published `vlan_info`, and netdevice notifier ordering. Dependencies are VLAN core helpers, rtnetlink, procfs, GARP/MRP, net namespaces, and capability checks.

Risks include registration unwind leaks, notifier ordering during device unregister, VID 0 auto-filter imbalance, address-filter churn, and legacy ioctl validation. Tests should cover netlink and ioctl creation/deletion, duplicate VID rejection, lower device up/down/changeaddr/changemtu/feat-change/unregister, GVRP/MVRP flag behavior, and namespace proc initialization/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan.c -->
