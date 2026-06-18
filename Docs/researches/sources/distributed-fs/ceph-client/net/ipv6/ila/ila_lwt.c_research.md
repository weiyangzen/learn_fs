# sources/distributed-fs/ceph-client/net/ipv6/ila/ila_lwt.c

## Purpose
Implements ILA lightweight tunnel encapsulation for IPv6 routes. It lets routes translate destination locators on output or input, optionally cache the next dst for connected routes, and expose ILA parameters through lwtunnel netlink attributes.

## Important APIs, Types, and Functions
`struct ila_lwt` stores `struct ila_params`, a `dst_cache`, and flags for connected/output mode. Main callbacks are `ila_output()`, `ila_input()`, `ila_build_state()`, `ila_destroy_state()`, `ila_fill_encap_info()`, `ila_encap_nlsize()`, and `ila_encap_cmp()`. Registration uses `ila_lwt_init()` and `ila_lwt_fini()` with `LWTUNNEL_ENCAP_ILA`.

## Control Flow
Output validates IPv6, applies locator translation when configured for route output, then either calls the original route output for gateway/cache routes or looks up a route to the translated nexthop, applies XFRM lookup, optionally caches the dst, replaces skb dst, and sends via `dst_output()`. Input validates IPv6 and applies reverse translation for route-input hooks before calling original input. State build parses nested ILA attributes, validates IPv6 family, locator, identifier type, hook type, checksum mode, and checksum-neutral constraints, allocates lwtunnel state, initializes dst cache, precomputes checksum delta from route destination locator, sets redirect flags, and returns the new state.

## State and Persistence
Per-route lwtunnel state holds translation parameters and a dst cache. Connected routes may cache dsts if no reference loop is created. State is kernel route configuration, recreated from netlink route operations, not stored by this file.

## Dependencies and Integration Points
Depends on lwtunnel core, IPv6 route output, XFRM lookup, dst cache, netlink attributes from `linux/ila.h`, and `ila_update_ipv6_locator()`. It integrates with `ip -6 route encap ila ...` style route configuration.

## Risks and Test Signals
Risks include dst cache loops, route lookup after destination mutation, unsupported identifier formats, checksum-neutral invalid inputs, input/output hook confusion, and non-IPv6 skb drops. Test signals include route add/dump/delete with ILA encap, output and input hook translation, connected route cache hit/miss, XFRM interaction, invalid attr rejection, locator/checksum mode dump round-trip, and packet checksum validation.
