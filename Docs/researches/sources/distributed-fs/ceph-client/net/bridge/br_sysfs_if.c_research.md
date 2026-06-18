# sources/distributed-fs/ceph-client/net/bridge/br_sysfs_if.c

## Purpose
`br_sysfs_if.c` exposes legacy per-bridge-port sysfs attributes under each port's `brport` kobject and maintains symlinks from the bridge's `brif` directory. It provides read/write access to STP state, timers, path cost, priority, port flags, group forwarding mask, backup port, and multicast router settings.

## Important APIs, types, and functions
- `struct brport_attribute` wraps sysfs attributes with numeric or raw store callbacks.
- Macros `BRPORT_ATTR`, `BRPORT_ATTR_RAW`, and `BRPORT_ATTR_FLAG` define port attributes and flag toggles.
- `store_flag()` validates hardware-offloadable flag changes through `br_switchdev_set_port_flag()` before committing `p->flags` and calling `br_port_flags_change()`.
- `brport_show()` and `brport_store()` implement `sysfs_ops`.
- `br_sysfs_addif()` creates the `bridge` link, all `brport` files, and the bridge `brif/<ifname>` symlink.
- `br_sysfs_renameif()` renames the `brif` symlink when a port device is renamed.

## Control flow
Reads call the attribute-specific show callback and format live `struct net_bridge_port` fields. Writes require CAP_NET_ADMIN and RTNL. Raw stores, such as `backup_port`, copy the user buffer and call the callback under `br->lock`; numeric stores parse `unsigned long` and call the setter under `br->lock`. Successful writes emit `br_ifinfo_notify(RTM_NEWLINK, NULL, p)`.

Port attributes include STP path cost/priority and designated/root state, timers, flush, hairpin, BPDU guard, root block, learning, flooding controls, proxy ARP, multicast flags, neighbor suppression, isolation, group forwarding mask, backup port, and multicast router when snooping is enabled.

## State and persistence
The file mutates per-port in-memory fields such as `flags`, `path_cost`, `priority`, `group_fwd_mask`, backup port pointer, multicast router mode, and FDB contents. `p->sysfs_name` stores the current symlink name for rename tracking. No persistent configuration is written.

## Dependencies and integration points
It depends on sysfs/kobject support, RTNL, namespace CAP_NET_ADMIN, switchdev port-flag validation/offload, STP setters, FDB flush, backup-port management, multicast snooping, and bridge netlink notifications.

## Risks and edge cases
Some file creation errors in `br_sysfs_addif()` return immediately after partial creation; caller teardown must remove the kobject/files. Raw backup-port input strips a newline and resolves the device by name in the port namespace. Switchdev rejection must prevent software flag drift from hardware. `simple_strtoul()` accepts partial numeric input, matching legacy sysfs behavior.

## Test signals
Test all flag toggles with and without switchdev support, path-cost/priority bounds, backup-port set/clear/unknown device, FDB flush, multicast router writes, symlink creation and rename rollback, CAP_NET_ADMIN failures, and netlink notification emission after successful writes.
