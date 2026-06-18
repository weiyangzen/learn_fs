# sources/distributed-fs/ceph-client/net/bridge/br_sysfs_br.c

## Purpose
`br_sysfs_br.c` exposes legacy bridge master attributes in sysfs. It lets privileged users read and update bridge STP, FDB, multicast, netfilter, VLAN, and group-address settings, and creates the bridge sysfs group, FDB binary file, and `brif` directory.

## Important APIs, types, and functions
- `store_bridge_parm()` is the common numeric store path: CAP_NET_ADMIN check, parse, `rtnl_trylock()`, call a setter, notify netdevice state change, and log extack messages.
- Attribute pairs expose `forward_delay`, `hello_time`, `max_age`, `ageing_time`, `stp_state`, `group_fwd_mask`, `priority`, IDs/root state, timers, `group_addr`, `flush`, `no_linklocal_learn`, multicast settings, bridge netfilter toggles, and VLAN filtering settings.
- `brforward_read()` exports the FDB as binary `struct __fdb_entry` records through `SYSFS_BRIDGE_FDB`.
- `br_sysfs_addbr()` and `br_sysfs_delbr()` create/remove the bridge attribute group, FDB binary attribute, and port-link directory.

## Control flow
Read attributes directly format fields from `struct net_bridge`, often converting jiffies to clock ticks or using `br_timer_value()`. Numeric writes pass through `store_bridge_parm()` and the same core setters used by netlink where possible. `group_addr_store()` is custom because it parses a MAC address and validates link-local group-address restrictions before updating under `br->lock`. `flush` writes call `br_fdb_flush()` for non-static entries.

Creation first creates the `"bridge"` attribute group on the netdevice kobject, then the FDB binary file, then the `brif` kobject. Failure unwinds earlier sysfs additions.

## State and persistence
Sysfs writes mutate in-memory bridge state. Sysfs files are views over live kernel state and are recreated with the device; they are not persistent configuration. The `ifobj` kobject pointer is stored in `struct net_bridge`.

## Dependencies and integration points
The file depends on sysfs, netdevice kobjects, RTNL, namespace CAP_NET_ADMIN checks, STP, multicast snooping, VLAN filtering, bridge netfilter, FDB helpers, and bridge option toggles. The source warns that new bridge options should use netlink rather than new sysfs files.

## Risks and edge cases
`rtnl_trylock()` can return `restart_syscall()`, so userspace must retry. Some sysfs setters directly mutate fields and are legacy surfaces parallel to netlink. Group address and forwarding mask validation protect reserved link-local protocols. FDB binary reads require record-aligned offsets. Sysfs creation failure must unwind cleanly.

## Test signals
Test CAP_NET_ADMIN enforcement, invalid numeric/MAC inputs, RTNL contention retry behavior, every writable attribute versus equivalent netlink behavior, FDB binary alignment, sysfs add/remove failure injection, and builds with multicast/netfilter/VLAN options disabled.
