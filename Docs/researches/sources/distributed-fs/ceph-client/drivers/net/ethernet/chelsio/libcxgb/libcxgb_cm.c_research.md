# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_cm.c

## Purpose

`libcxgb_cm.c` provides common Chelsio connection-management helpers for parsing passive-open tuples and finding routes that egress through a Chelsio-owned interface. The functions are exported for other Chelsio upper-layer drivers.

## Important APIs, Types, and Functions

- `cxgb_get_4tuple()` parses `struct cpl_pass_accept_req` to extract IPv4/IPv6 local and peer addresses and TCP ports. It accounts for T5-and-earlier versus T6 header length field layouts.
- `cxgb_find_route()` builds an IPv4 route with `ip_route_output_ports()`, looks up the neighbour, and accepts the route only if the real egress device belongs to the Chelsio LLDI ports or is loopback.
- `cxgb_find_route6()` builds an IPv6 route with `ip6_route_output()`, handles link-local scope ID, and applies the same Chelsio-interface/loopback filter.
- `cxgb_our_interface()` is a local helper that normalizes real devices through a callback and compares against `lldi->ports[]`.

## Control Flow

Consumers pass a hardware PASS_ACCEPT request to `cxgb_get_4tuple()` to decode peer/local tuple data. For active route validation, consumers call the IPv4 or IPv6 finder with local/peer tuple and a callback that maps VLAN/bond devices to real devices. The function releases routes/neighbours and returns `NULL` if routing fails, neighbour lookup fails, or egress is not associated with the Chelsio adapter.

## State and Persistence Behavior

The file stores no long-lived state. Returned `dst_entry` references must be released by callers. Neighbour references are short-lived and released before return.

## Dependencies and Integration Points

It depends on Linux IPv4/IPv6 route APIs, neighbour lookup, ECN/TOS helpers, Chelsio CPL layout macros, and `cxgb4_lld_info`. Symbols are exported with `EXPORT_SYMBOL`.

## Risks and Edge Cases

- In `cxgb_find_route()`, if `dst_neigh_lookup()` fails, the route is returned neither released nor passed back; this is a potential leak pattern unless route internals handle it elsewhere.
- IPv6 support is wrapped in `IS_ENABLED(CONFIG_IPV6)`; when disabled, `cxgb_find_route6()` returns `NULL`.
- Interface filtering depends on the caller's `get_real_dev` callback handling VLAN or stacked devices correctly.

## Test Signals

Test tuple parsing for T5/T6 header length encodings, IPv4 and IPv6 PASS_ACCEPT requests, VLAN real-device mapping, non-Chelsio route rejection, loopback acceptance, IPv6 link-local scope, and route/neighbour failure cleanup.
