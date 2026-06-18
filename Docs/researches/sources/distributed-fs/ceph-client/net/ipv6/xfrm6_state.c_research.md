# sources/distributed-fs/ceph-client/net/ipv6/xfrm6_state.c

## Purpose
Provides IPv6-specific XFRM state address matching operations. This is a small AF adapter used by generic XFRM state management to compare IPv6 addresses and prefix lengths.

## Important APIs, types, and functions
Defines `xfrm6_state_addr_cmp`, `xfrm6_state_addr_check`, and `xfrm6_state_afinfo`. The AF info binds `.family = AF_INET6`, `.proto = IPPROTO_IPV6`, and the two address callbacks.

## Control flow
`xfrm6_state_addr_cmp` calls `ipv6_prefix_equal` for destination and source address pairs using the selector prefix lengths, returning mismatch on either failed comparison. `xfrm6_state_addr_check` calls the same comparator for state properties and selector values.

## State and persistence behavior
No state is allocated or persisted. It only reads `struct xfrm_tmpl`, `struct xfrm_state`, and `struct flowi` address fields.

## Dependencies and integration points
Depends on generic XFRM state core and IPv6 prefix comparison helpers. The `xfrm6_state_afinfo` object is consumed by IPv6 XFRM initialization elsewhere in the stack.

## Risks and test signals
The main risk is incorrect selector matching for non-/128 prefixes or swapped source/destination checks. Test with IPv6 IPsec policies using exact and prefix selectors, wildcard source/destination states, and flows that differ only outside selector prefix length.
