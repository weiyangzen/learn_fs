# sources/distributed-fs/ceph-client/net/bridge/br_vlan_options.c

## Purpose
Handles user-visible bridge VLAN options for per-entry and global VLAN database netlink operations: VLAN STP state, tunnel mapping, neighbor suppression, per-port multicast limits/router state, global multicast snooping parameters, and MST instance assignment.

## Important APIs, Types, And Functions
Important functions include `br_vlan_opts_eq_range`, `br_vlan_opts_fill`, `br_vlan_opts_nl_size`, `br_vlan_process_options`, `br_vlan_global_opts_can_enter_range`, `br_vlan_global_opts_fill`, and `br_vlan_rtm_process_global_options`. Internal helpers include `br_vlan_modify_state`, `br_vlan_modify_tunnel`, `br_vlan_process_one_opts`, `br_vlan_global_opts_notify`, and `br_vlan_process_global_one_opts`.

## Control Flow
Per-VLAN option processing validates the requested VLAN or range exists, then walks each VLAN and applies requested netlink attributes. State changes are rejected for kernel STP and MST-enabled bridges, tunnel changes require a port VLAN with `BR_VLAN_TUNNEL`, multicast max-groups require active per-port VLAN snooping context, and neighbor suppression is port-only. Changed VLANs are coalesced into notification ranges when flags/options allow. Global processing is bridge-device-only and `RTM_NEWVLAN`-only; it validates ID/range attributes, applies multicast and MST attributes, and emits global option notifications in compatible ranges.

## State And Persistence Behavior
The file mutates existing in-memory `net_bridge_vlan` fields: `state`, PVID state cache, `priv_flags`, tunnel mappings through `br_vlan_tunnel_info`, multicast context fields and timers, multicast router state, and `msti`. It emits rtnetlink notifications but does not persist data outside kernel memory.

## Dependencies And Integration Points
Integrates with the VLAN DB netlink path in `br_vlan.c`, tunnel helpers in `br_vlan_tunnel.c`, multicast bridge code under `CONFIG_BRIDGE_IGMP_SNOOPING`, MST helpers, rtnetlink nested attribute policy validation, and clock/jiffies conversion for multicast timers.

## Risks And Test Signals
Risks include partial range updates before an error, incorrect range coalescing after option changes, invalid direct state mutation while STP/MST owns state, tunnel ID arithmetic across VLAN ranges, and global multicast timer unit conversion. Tests should exercise netlink set/dump round trips for single VLANs and ranges, rejected non-port tunnel/neigh options, missing attributes, MST assignments, multicast snooping toggles, and notification content for option-only changes.
