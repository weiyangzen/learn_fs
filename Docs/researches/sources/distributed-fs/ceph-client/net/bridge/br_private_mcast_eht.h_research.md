# sources/distributed-fs/ceph-client/net/bridge/br_private_mcast_eht.h

## Purpose
`br_private_mcast_eht.h` defines Explicit Host Tracking structures and helpers for multicast snooping. EHT tracks hosts and per-source sets for a bridge port group so IGMPv3/MLDv2 source-filtering state can be managed per listener.

## Important APIs, types, and functions
- `BR_MCAST_DEFAULT_EHT_HOSTS_LIMIT` sets the default host-count cap.
- `union net_bridge_eht_addr` stores IPv4 or optional IPv6 addresses.
- `net_bridge_group_eht_host` tracks one host's set entries, filter mode, entry count, and parent port group.
- `net_bridge_group_eht_set_entry` connects one host to one per-source set and carries a timer plus multicast GC hook.
- `net_bridge_group_eht_set` represents a source set with an rb-tree of host entries, timer, parent group, bridge pointer, and GC hook.
- `br_multicast_eht_clean_sets()`, `br_multicast_eht_handle()`, and `br_multicast_eht_set_hosts_limit()` are the main implementation entry points when snooping is enabled.

## Control flow
The multicast implementation calls `br_multicast_eht_handle()` when processing source-filter capable reports. Host/set rbtrees are updated, timers drive expiry, and GC hooks handle deferred destruction. Inline helpers decide whether fast-leave can delete a port group after the last tracked host, enforce host limits, and increment/decrement per-port host counters.

## State and persistence
EHT state lives under each `net_bridge_port_group` in `eht_set_tree` and `eht_host_tree`, with per-port counts in `multicast_eht_hosts_cnt` and limits in `multicast_eht_hosts_limit`. It is in-memory multicast snooping state only.

## Dependencies and integration points
The header depends on bridge multicast structures from `br_private.h`, rbtrees, timers, and optional IPv6. It is consumed by multicast code and exposed through port netlink/sysfs attributes for EHT host limits/counts.

## Risks and edge cases
Host-limit enforcement must avoid counter leaks on partial allocation failures. Fast-leave deletion depends on the host tree being truly empty. Timer/GC teardown must avoid use-after-free while multicast reports and port-group deletion race.

## Test signals
Use IGMPv3/MLDv2 include/exclude report sequences from multiple hosts, host-limit exhaustion, fast-leave behavior, timer expiry, IPv4/IPv6 builds, and port group deletion with active EHT entries.
