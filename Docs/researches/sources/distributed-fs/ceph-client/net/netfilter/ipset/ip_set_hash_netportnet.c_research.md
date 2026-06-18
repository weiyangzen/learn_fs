# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netportnet.c

## Purpose

`ip_set_hash_netportnet.c` implements `hash:net,port,net`, matching an outer network, protocol/port, and inner network. It supports two network dimensions, `nomatch`, IPv4 range expansion including `/0`, and IPv6 exact-prefix operations.

## Important APIs, types, and functions

IPv4 and IPv6 elements contain two IP addresses, port, two CIDRs, `nomatch`, and protocol. `hash_netportnet{4,6}_data_equal()` compares both networks, both CIDRs, port, and protocol. `data_reset_elem()` restores the inner network during generated multi-network matching. `data_netmask()` masks either network depending on the `inner` flag. `hash_netportnet4_range_to_cidr()` special-cases the full IPv4 range as CIDR zero, unlike the standard range helper. `kadt` functions extract packet network dimensions one and three plus port dimension two. `uadt` functions parse two IPs, two CIDRs, optional two IP ranges, port/proto, flags, and extensions.

## Control flow

The module configures `IP_SET_HASH_WITH_PROTO`, `IP_SET_HASH_WITH_NETS`, `IPSET_NET_COUNT 2`, and `IP_SET_HASH_WITH_NET0`. Packet operations initialize both CIDRs from the set net metadata, use host-width CIDRs during tests, mask both packet IPs, and dispatch. IPv4 userspace single operations normalize both networks and translate `nomatch` results. Range operations nest outer network blocks, port values, and inner network blocks, storing retry progress in `h->next`. IPv6 rejects both IP range attributes and can only expand ports for port-bearing protocols.

## State and persistence behavior

The set stores two-prefix tuple elements, generic extensions, timeout state, and `nomatch`. IPv4 retry state includes outer IP, port, and inner IP. `/0` support is part of state semantics through `IP_SET_HASH_WITH_NET0` and the local range helper. There is no module-global runtime state beyond type registration.

## Dependencies and integration points

The file depends on the ipset generic hash/multi-network implementation, port extraction, prefix helpers, and netlink attribute policy. It registers as `hash:net,port,net` with features `IPSET_TYPE_IP | IPSET_TYPE_PORT | IPSET_TYPE_IP2 | IPSET_TYPE_NOMATCH`.

## Risks

IPv4 Cartesian expansion can be large because it combines two network ranges and a port range. `/0` support means full-range inputs are valid here and need special handling. Protocols without ports collapse port to zero. IPv6 users cannot use range attributes. `nomatch` and two-CIDR equality make regressions easy if list/test paths drop flags or prefix lengths.

## Test signals

Tests should cover exact tuple add/test/delete, outer and inner `/0`, IPv4 `IP_TO` and `IP2_TO` expansion, port ranges, retry after `IPSET_MAX_RANGE`, IPv6 range rejection, `nomatch`, list output for both CIDRs and flags, and packet-path dimension selection.
