# sources/distributed-fs/ceph-client/net/l3mdev/l3mdev.c

## Purpose
`l3mdev.c` implements core helpers for devices that act as L3 routing masters, especially VRF-style devices. It lets drivers register table-id lookup callbacks, derives a flow's L3 master device, and dispatches route-table and IPv6 link-scope lookups through device-provided `l3mdev_ops`.

## Important APIs, Types, and Functions
`struct l3mdev_handler` stores a `lookup_by_table_id_t` callback per `enum l3mdev_type`. Exported functions include `l3mdev_table_lookup_register()`, `l3mdev_table_lookup_unregister()`, `l3mdev_ifindex_lookup_by_table_id()`, `l3mdev_master_ifindex_rcu()`, `l3mdev_master_upper_ifindex_by_index_rcu()`, `l3mdev_fib_table_rcu()`, `l3mdev_fib_table_by_index()`, `l3mdev_link_scope_lookup()`, `l3mdev_fib_rule_match()`, and `l3mdev_update_flow()`.

## Control Flow
Handler registration validates the l3mdev type and installs one callback under `l3mdev_lock`, rejecting duplicates with `-EBUSY`. Lookups copy the registered callback under the same lock and call it to map table ids to ifindexes. Device helpers use RCU lookup of net devices, climb upper-device links for slaves, and call master `l3mdev_ops` for FIB table or link-scope route lookups. `l3mdev_update_flow()` fills `flowi_l3mdev` from output or input interface and clears `flowi_oif` when the output interface itself is an L3 master so FIB lookup uses the master table instead of an oif match.

## State and Persistence
Runtime state consists of the global handler array protected by `l3mdev_lock`; per-device state lives in `net_device` flags and `l3mdev_ops`. Flow updates mutate `struct flowi` fields transiently during route lookup.

## Dependencies and Integration Points
The implementation depends on netdevice master/slave relationships, RCU device lookup, `net/l3mdev.h`, and FIB rule plumbing. It is used by VRF drivers and by IPv4/IPv6 route lookup paths to enforce per-L3-domain routing tables.

## Risks and Edge Cases
Several helpers require callers to hold RCU, and `l3mdev_link_scope_lookup()` warns if they do not. `l3mdev_ifindex_lookup_by_table_id()` calls driver callbacks while holding a spinlock, so callbacks must not sleep or re-enter registration. Const casts are used only to call upper-device RCU helpers, but changes to netdevice APIs could affect those assumptions. Incorrect `flowi_oif` clearing can route traffic through the wrong table.

## Test Signals
VRF route lookup tests should validate table selection for master and slave devices, link-local IPv6 lookup, FIB rule matching, and flow update behavior for input and output interfaces. Concurrency tests should cover handler register/unregister while route lookups run.
