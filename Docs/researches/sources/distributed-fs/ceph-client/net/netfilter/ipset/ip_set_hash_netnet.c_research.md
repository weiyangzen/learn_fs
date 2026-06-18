# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netnet.c

## Purpose

`ip_set_hash_netnet.c` implements `hash:net,net`, a two-dimensional ipset type storing two network prefixes. It supports `nomatch`, IPv4 range expansion on either network dimension, and create-time netmask/bitmask handling.

## Important APIs, types, and functions

IPv4 elements store two addresses in a union with a combined comparison field, plus two CIDRs and `nomatch`; IPv6 elements store two `union nf_inet_addr` values and combined CIDR comparison. `hash_netnet{4,6}_data_equal()` compares both normalized networks and both CIDRs. `data_reset_elem()` restores the inner network during generic multi-network matching. `data_netmask()` masks either outer or inner network based on the `inner` flag. `hash_netnet{4,6}_init()` sets both CIDRs to host width. `kadt` functions extract two packet address dimensions and apply netmask plus bitmask. `uadt` functions parse `IP`, `IP2`, `CIDR`, `CIDR2`, optional ranges, flags, and extensions.

## Control flow

The file sets `IPSET_NET_COUNT 2`, `IP_SET_HASH_WITH_NETS`, `IP_SET_HASH_WITH_NETMASK`, and `IP_SET_HASH_WITH_BITMASK` before including the generic hash code. Packet tests use host-width CIDRs for lookup and normalize both packet addresses. IPv4 userspace operations either perform a single normalized ADT call or expand outer and inner ranges by repeatedly converting ranges to CIDR blocks. IPv6 rejects `IP_TO` and `IP2_TO`; it masks both addresses by CIDR and bitmask, rejects all-zero host-width first addresses, and dispatches one operation.

## State and persistence behavior

Persistent set state includes two-prefix elements, bitmask/netmask configuration, `nomatch` bits, generic extensions, and hash network metadata for two network dimensions. Retry state stores both IP dimensions in `h->next`. There is no separate module-level mutable state after registration.

## Dependencies and integration points

The module integrates with generic ipset hash code for multi-network lookup and create policies. It depends on prefix/range helpers, IPv4/IPv6 masking helpers, and netlink attribute parsing. It registers features `IPSET_TYPE_IP | IPSET_TYPE_IP2 | IPSET_TYPE_NOMATCH`.

## Risks

Range expansion across two dimensions can generate many CIDR blocks and hit `IPSET_MAX_RANGE`. IPv6 does not support range input. Bitmask normalization can reject or alter user-provided host-width IPv6 addresses, especially all-zero first addresses. Because two CIDRs participate in equality, tests must verify both prefix lengths, not only addresses.

## Test signals

Tests should add/test/delete IPv4 and IPv6 network pairs, list both CIDRs, verify `nomatch`, exercise IPv4 `IP_TO` and `IP2_TO` expansion including retries, validate IPv6 range rejection, cover netmask/bitmask create options, and run packet-path tests selecting source/destination dimensions independently.
