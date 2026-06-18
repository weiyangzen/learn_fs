<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_netlink.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlan_netlink.c

This file implements the rtnetlink `kind = "vlan"` interface for creating, changing, deleting, and dumping VLAN devices. It is the modern control plane for VLAN configuration.

Validation is handled by `vlan_validate()`, which checks link-layer address length/validity, required data, VLAN protocol (`ETH_P_8021Q` or `ETH_P_8021AD`), VID range, flag mask, and nested QoS map policies. `vlan_newlink()` resolves the lower device, fills `vlan_dev_priv`, defaults to header reordering, validates the real device, computes MTU limits, applies initial changes, and calls `register_vlan_dev()`. `vlan_changelink()` applies flag changes plus ingress and egress QoS maps. `vlan_fill_info()` serializes protocol, id, flags, and QoS maps for dumps. `vlan_get_link_net()` reports the lower device's net namespace.

State mutated here lives in the VLAN netdevice private area: flags, VLAN protocol/id, real device pointer, and priority maps. Egress map allocations are freed on newlink failure. Dependencies include rtnetlink policies, net namespace lookup, extack messages, VLAN registration, and RCU/RTNL access to priority maps.

Risks include incomplete unwind after failed QoS-map allocation, allowing invalid MTUs, bad nested attribute validation, and mismatch between dump size calculation and emitted attributes. Tests should cover netlink create with missing link/id, bad protocol/id/address/flags/QoS, 802.1Q and 802.1ad creation, change flags/QoS, dump round trips, and failure paths that free egress mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_netlink.c -->
