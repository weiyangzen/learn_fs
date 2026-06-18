# sources/distributed-fs/ceph-client/net/bridge/br_nf_core.c

## Purpose
`br_nf_core.c` provides the fake routing destination used by bridge netfilter. Bridged packets sometimes travel through IPv4 netfilter code that expects route/dst metadata, so the bridge initializes a synthetic `rtable` with enough fields for PMTU/refragmentation and targets such as `REJECT`.

## Important APIs, types, and functions
- `fake_dst_ops` is a minimal `dst_ops` implementation with no-op PMTU/redirect, null metrics copy-on-write/neighbour lookup, and MTU derived from `dst->dev->mtu`.
- `br_netfilter_rtable_init()` initializes `br->fake_rtable` and bridge metric storage.
- `br_nf_core_init()` and `br_nf_core_fini()` register/destroy `fake_dst_ops` accounting through `dst_entries_init()` and `dst_entries_destroy()`.

## Control flow
Module initialization prepares the dst operations. Per-bridge initialization calls `br_netfilter_rtable_init()`, sets an initial reference, points `dst.dev` at the bridge device, initializes metrics from `br->metrics`, stores MTU, sets `DST_NOXFRM | DST_FAKE_RTABLE`, and attaches `fake_dst_ops`.

## State and persistence
State is per-bridge in-memory route/dst metadata and a static global `dst_ops`. No persistent storage exists. The fake route is valid only for the bridge lifetime.

## Dependencies and integration points
The file depends on the route/dst infrastructure and is compiled through `CONFIG_BRIDGE_NETFILTER`. `br_private.h` exposes `br_netfilter_rtable_init()` as a stub when bridge netfilter is disabled.

## Risks and edge cases
The fake route intentionally leaves many operations inert. Future netfilter code that expects additional dst behavior would require extending this file. MTU must track bridge device MTU at initialization and any later updates handled elsewhere.

## Test signals
Bridge netfilter tests should include IPv4/IPv6/ARP netfilter paths, PMTU-sensitive fragmented traffic, bridge MTU changes, and iptables/nftables reject/forwarding cases with `br_netfilter` enabled.
