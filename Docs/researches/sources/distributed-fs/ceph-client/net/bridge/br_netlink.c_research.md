# sources/distributed-fs/ceph-client/net/bridge/br_netlink.c

## Purpose
`br_netlink.c` is the bridge driver's rtnetlink control plane. It registers the `"bridge"` link kind, validates bridge link attributes, creates/deletes bridge devices, applies bridge-wide and per-port changes, dumps bridge/port state, emits link notifications, and parses `AF_BRIDGE` nested attributes for VLANs, VLAN tunnel mappings, MRP, CFM, and MST state.

## Important APIs, types, and functions
- `br_link_ops` wires bridge setup, validation, `newlink`, `changelink`, `dellink`, bridge attribute sizing/fill, link xstats, and slave port operations into rtnetlink.
- `br_netlink_init()` / `br_netlink_fini()` register/unregister bridge VLAN rtnetlink support, `rtnl_af_ops`, and `rtnl_link_ops`.
- `br_getlink()`, `br_fill_ifinfo()`, `br_info_notify()`, and `br_ifinfo_notify()` build `RTM_NEWLINK` payloads for bridge masters and bridge ports.
- `br_setlink()` and `br_dellink()` process legacy and nested `IFLA_PROTINFO`/`IFLA_AF_SPEC` requests for ports and bridge masters.
- `br_changelink()` applies bridge-wide `IFLA_BR_*` options such as STP timing, STP state/mode, VLAN filtering/protocol/default PVID, group forwarding masks/address, FDB flush/limits, multicast options, netfilter toggles, and boolean option batches.
- `br_setport()` applies `IFLA_BRPORT_*` attributes including state, cost, priority, hairpin, guard/protect, flood/learning flags, VLAN tunnel mode, neighbor suppression, isolation, locked/MAB mode, backup port, EHT host limit, multicast router, and backup nexthop ID.
- `br_process_vlan_info()` and `br_afspec()` handle singleton and ranged VLAN add/delete operations, generate `RTM_NEWVLAN`/`RTM_DELVLAN` notifications, and dispatch optional MRP/CFM/MST/tunnel nested attributes.
- `br_get_size()`, `br_fill_info()`, `br_port_info_size()`, `br_port_fill_attrs()`, `br_get_link_af_size_filtered()`, and link xstats helpers keep netlink dump size accounting aligned with actual `nla_put*()` output.

## Control flow
Bridge creation enters through `br_dev_newlink()`: register the netdevice, optionally adopt a user MAC into the STP bridge ID, then call `br_changelink()` so creation-time attributes are applied through the same path as later changes. A failure after registration calls `br_dev_delete()`.

Per-port updates through `br_setlink()` first parse `IFLA_PROTINFO`; nested modern attributes are validated against `br_port_policy`, then `br_setport()` runs under `br->lock`. A non-nested byte remains supported for old RSTP state changes. `IFLA_AF_SPEC` is then parsed by `br_afspec()` for VLAN, VLAN tunnel, MRP, CFM, and MST subcommands. Any effective change triggers `br_ifinfo_notify(RTM_NEWLINK, ...)`.

Bridge-wide updates through `br_changelink()` are ordered and fail-fast. STP timing calls `br_set_forward_delay()`, `br_set_hello_time()`, `br_set_max_age()`, and `br_set_ageing_time()`. STP mode cannot change while STP is enabled unless the same request turns STP off. VLAN operations are delegated to VLAN helpers, multicast operations to multicast helpers, netfilter toggles to `br_opt_toggle()`, and boolean batches to `br_boolopt_multi_toggle()`.

Dump paths precompute enough space, open nested attributes only when requested, use RCU for VLAN and backup-port reads, and cancel empty `IFLA_AF_SPEC` nests. Link xstats support restart by updating `*prividx` on `-EMSGSIZE`.

## State and persistence
All state is in kernel memory in `struct net_bridge`, `struct net_bridge_port`, VLAN groups, timers, and FDB/multicast tables. Netlink changes do not persist across bridge destruction or reboot. State visibility is via rtnetlink notifications/dumps and xstats. Synchronization uses RTNL, `br->lock`, RCU, `READ_ONCE`/`WRITE_ONCE` for selected fields, and helper-specific locks.

## Dependencies and integration points
This file integrates with rtnetlink, `AF_BRIDGE`, VLAN, MST, MRP, CFM, multicast snooping, bridge netfilter, switchdev, STP, FDB, netdevice core, and uapi bridge attributes. `br_switchdev_set_port_flag()` is called before committing hardware-offloadable port flag changes, so driver rejection rolls back software flags.

## Risks and edge cases
Size accounting must match every emitted attribute; mismatches surface as `-EMSGSIZE` warnings or truncated dumps. Range handling for VLANs and tunnel mappings must reset the pending range after an end marker and reject malformed ranges. MAB requires locked ports with learning enabled and flushes locked FDB entries when disabled. Group forwarding masks reject restricted link-local protocols on bridge masters and MAC pause on ports. Changing STP mode while active is guarded to avoid control-plane ownership ambiguity.

## Test signals
Useful coverage includes `ip link add type bridge` with creation attributes, repeated `ip link set type bridge` changes, port `IFLA_BRPORT_*` toggles, invalid VLAN/tunnel ranges, compressed VLAN dumps, xstats dump restart behavior, STP mode/state transitions, MAB enable/disable FDB flushing, bridge multicast/netfilter option toggles with configs on/off, and switchdev driver rejection paths.
