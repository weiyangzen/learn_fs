# sources/distributed-fs/ceph-client/include/trace/events/bridge.h

## Purpose
`bridge.h` traces Linux bridge forwarding database and multicast database events. It helps diagnose FDB add/delete/update paths, externally learned entries, and MDB capacity issues.

## Important APIs, types, and functions
Events are `br_fdb_add`, `br_fdb_external_learn_add`, `fdb_delete`, `br_fdb_update`, and `br_mdb_full`. They record bridge/port device names, MAC addresses, VLAN ids, netlink flags, FDB flags, and multicast group identity.

## Control flow
Bridge management and learning paths emit FDB events during netlink add, external learn, delete, and update operations. `br_mdb_full` records multicast group information, converting IPv4 addresses to IPv4-mapped IPv6 arrays and handling raw MAC groups when no protocol is set.

## State and persistence behavior
The header stores no state. Records snapshot names, MAC/group bytes, flags, VLAN ids, and address family at the point of bridge database mutation or failure.

## Dependencies and integration points
It depends on `<linux/netdevice.h>`, tracepoint support, and bridge private structures via `../../../net/bridge/br_private.h`. It integrates with network tracing, netlink bridge management, multicast snooping diagnostics, and BPF consumers.

## Risks and test signals
Risks include private-header coupling, IPv6 fields being compiled only when `CONFIG_IPV6` is enabled, and device-name snapshots changing after rename. Test signals are bridge FDB netlink operations, learned source updates, FDB delete paths, and MDB-full reproductions with IPv4, IPv6, and MAC groups.
