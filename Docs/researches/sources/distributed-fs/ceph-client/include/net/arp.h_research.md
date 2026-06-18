# sources/distributed-fs/ceph-client/include/net/arp.h

## Purpose

`arp.h` exposes IPv4 ARP neighbor-table operations, ARP packet creation/transmission helpers, multicast address mapping, ioctl handling, and fast neighbor lookup helpers.

## Important APIs, Types, and Functions

`arp_tbl` is the global ARP `neigh_table`. `arp_hashfn()` hashes an IPv4 key with the device pointer and per-table random seed. `__ipv4_neigh_lookup_noref()` maps loopback/point-to-point lookups to `INADDR_ANY` and performs a no-reference neighbor lookup when `CONFIG_INET` is enabled. `__ipv4_neigh_lookup()` wraps that lookup with RCU and increments the neighbor refcount if possible. `__ipv4_confirm_neigh()` confirms reachability without taking a caller-visible reference. Exported functions cover initialization, ioctls, packet send/create/xmit, multicast mapping, device down cleanup, and forced invalidation.

## Control Flow

IPv4 output or neighbor users call lookup helpers under RCU to find ARP entries. Successful referenced lookups survive beyond the RCU read-side critical section; no-ref lookups are transient. ARP packet paths use `arp_create()` to build an skb and `arp_xmit()` or `arp_send()` to transmit. Device teardown calls `arp_ifdown()` to flush neighbor state.

## State and Persistence Behavior

ARP entries live in the neighbor table and age according to neighbor subsystem timers. No filesystem persistence exists. Refcounts and RCU protect neighbor lifetimes; loopback/point-to-point devices intentionally share `INADDR_ANY` lookup semantics.

## Dependencies and Integration Points

The header depends on net devices, `if_arp.h`, hashing, neighbor core, RCU, and IPv4 configuration. It integrates with IPv4 routing/output, device lifecycle, userspace ARP ioctls, and multicast hardware-address mapping.

## Risks and Edge Cases

No-ref lookups are only safe inside RCU read-side sections. Callers that ignore the loopback/point-to-point key rewrite may see surprising aliasing. Hash quality depends on per-table randomization and device pointer hashing. `CONFIG_INET=n` stubs return `NULL`, so code must handle absence of ARP.

## Test Signals

Exercise referenced and no-ref lookups, loopback and point-to-point key behavior, refcount failure races, ARP send/create for request/reply, multicast mapping per device type, ioctl add/delete/query, device down cleanup, invalidation with and without force, and `CONFIG_INET` disabled builds.
