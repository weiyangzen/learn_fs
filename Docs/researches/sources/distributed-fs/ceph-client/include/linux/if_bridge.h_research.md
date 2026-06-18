# `sources/distributed-fs/ceph-client/include/linux/if_bridge.h`

Purpose: internal bridge integration API for multicast snooping, VLAN filtering, MST state, FDB lookup/offload cleanup, bridge ioctl hooks, and bridge-port flag/state queries.

Important APIs/types/functions: `struct br_ip`, `struct br_ip_list`, bridge port flag bits (`BR_HAIRPIN_MODE`, `BR_LEARNING`, `BR_PORT_LOCKED`, etc.), `brioctl_set`, `br_ioctl_call`, multicast query/list helpers, VLAN getters (`br_vlan_get_pvid`, `br_vlan_get_info`), MST getters, `br_fdb_find_port`, `br_fdb_clear_offload`, `br_port_flag_is_set`, `br_port_get_stp_state`, and `br_get_ageing_time`.

Control flow and state: the header exposes live bridge state through `net_device` lookups. When relevant configs are disabled it provides stubs returning false, zero, `NULL`, or `-EINVAL`.

Dependencies/integration: depends on netdevice, UAPI bridge definitions, bitops, IPv6 conditionals, and feature configs `CONFIG_BRIDGE`, `CONFIG_BRIDGE_IGMP_SNOOPING`, and `CONFIG_BRIDGE_VLAN_FILTERING`.

Risks: callers must tolerate stubs under disabled configs; RCU-specific getters (`*_rcu`) require correct read-side locking; FDB and VLAN results are bridge-lifetime dependent; port flags are bit ABI shared across bridge, switchdev, and drivers.

Test signals: build matrix for bridge/snooping/VLAN/MST configs, switchdev offload FDB clear paths, multicast router/querier behavior, VLAN PVID/proto/info lookups under RCU, and STP state fallbacks when bridge is disabled.
