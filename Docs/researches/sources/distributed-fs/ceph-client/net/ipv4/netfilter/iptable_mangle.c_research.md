# sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_mangle.c

## Purpose
`iptable_mangle.c` instantiates the legacy IPv4 `mangle` table and reroutes locally generated packets when rules change routing-relevant fields.

## Important APIs, Types, And Functions
Important functions are `ipt_mangle_out()`, `iptable_mangle_hook()`, `iptable_mangle_table_init()`, and module init/exit. The table is `packet_mangler`.

## Control Flow
All five IPv4 hooks use the mangle table. For `LOCAL_OUT`, the module snapshots source, destination, mark, and TOS before `ipt_do_table()`. If the packet is not dropped/stolen and any value changed, it calls `ip_route_me_harder()` and converts routing errors into `NF_DROP_ERR()`.

## State And Persistence
State is the per-net xt table plus static hook-ops pointer. It does not store packet history; reroute decisions are per packet.

## Dependencies And Integration Points
It integrates with `ip_tables.c`, `ip_route_me_harder()` from IPv4 netfilter glue, IPv4 route output, and all major IPv4 netfilter hooks at mangle priority.

## Risks
Risks include missing a route-affecting field change, unnecessary reroutes, incorrect handling of `NF_STOLEN`, route failure drops, and skb mutation by targets that changes header pointers.

## Test Signals
Test LOCAL_OUT changes to mark/TOS/source/destination, unchanged no-op rules, drop/stolen verdicts, route lookup failure, all hook registrations, and namespace cleanup.
