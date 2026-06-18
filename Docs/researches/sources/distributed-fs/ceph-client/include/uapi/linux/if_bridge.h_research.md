<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_bridge.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_bridge.h

## Purpose
`if_bridge.h` defines the Linux bridge userspace ABI: legacy bridge ioctl constants, sysfs names, STP state structures, bridge netlink attributes for VLANs, MRP, CFM, MST, multicast database management, xstats, boolean options, and multicast querier state.

## Important APIs, types, and functions
Legacy pieces include `BRCTL_*`, bridge state constants, `struct __bridge_info`, `__port_info`, and `__fdb_entry`. Netlink definitions include `IFLA_BRIDGE_*`, `struct bridge_vlan_info`, VLAN tunnel and xstats attrs, extensive MRP attrs and structs (`br_mrp_instance`, `br_mrp_ring_state`, `br_mrp_ring_role`, `br_mrp_start_test`, `br_mrp_in_state`, `br_mrp_in_role`, `br_mrp_start_in_test`), CFM attrs, MST attrs, `struct bridge_stp_xstats`, VLAN database message/attrs, MDB/router attrs, `struct br_port_msg`, `struct br_mdb_entry`, MDB set/get/source attrs, `struct br_mcast_stats`, `enum br_boolopt_id`, `struct br_boolopt_multi`, and querier attrs.

## Control flow
User space configures bridges and ports through rtnetlink attributes under `IFLA_AF_SPEC`, manages VLAN and tunnel entries through VLAN database messages, controls MRP/CFM/MST features with nested attributes, manipulates MDB entries, and reads FDB/MDB/VLAN/STP/multicast stats. Legacy brctl ioctls provide older bridge and port management paths.

## State and persistence behavior
Bridge state includes STP timers and port states, FDB entries, VLAN membership and per-VLAN options, multicast snooping/querier/MDB/router state, MRP ring/interconnect roles, CFM maintenance points, MST states, boolean options, and per-VLAN/multicast/STP counters. These are live netdevice state until changed or removed.

## Dependencies and integration points
It depends on `<linux/types.h>`, `<linux/if_ether.h>`, and `<linux/in6.h>`. It integrates with rtnetlink, bridge driver, switchdev/offload drivers, iproute2 `bridge`, sysfs bridge files, multicast snooping, MRP/CFM protocols, and xstats.

## Risks and test signals
Risks include nested attribute policy drift, range VLAN semantics errors, offload failure notification handling, stale legacy ioctl behavior, CFM/MRP role mismatch, MDB source-list ambiguity, and boolean option updates missing sysfs handlers. Test signals include bridge/VLAN/MDB iproute2 tests, switchdev offload tests, multicast snooping/querier cases, STP transition counters, MRP ring failover, CFM peer status, MST state dumps, and strict netlink validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_bridge.h -->
