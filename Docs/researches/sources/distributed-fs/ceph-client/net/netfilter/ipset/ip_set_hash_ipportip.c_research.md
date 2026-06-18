# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipportip.c

## Purpose

`ip_set_hash_ipportip.c` implements `hash:ip,port,ip`, a three-dimensional ipset type for an address, transport protocol/port, and a second address. It is used when rules need to match tuples such as client address, service port, and peer address without the second address being interpreted as a network.

## Important APIs, types, and functions

`struct hash_ipportip4_elem` contains `ip`, `ip2`, `port`, and `proto`; the IPv6 variant uses two `union nf_inet_addr` fields. `hash_ipportip{4,6}_data_equal()` compares both addresses, port, and protocol. `data_list()` emits `IPSET_ATTR_IP`, `IPSET_ATTR_IP2`, `IPSET_ATTR_PORT`, and `IPSET_ATTR_PROTO`. Packet path `kadt` functions extract the port from dimension two and IP addresses from dimensions one and three. Userspace `uadt` functions require `IP`, `IP2`, `PORT`, and `PROTO`, support extension parsing, normalize non-port protocols to port zero, and expand first-address and port ranges where supported.

## Control flow

The module includes `ip_set_hash_gen.h` twice, once for IPv4 and once for IPv6. IPv4 userspace operations can expand `IPSET_ATTR_IP_TO` or `CIDR` for the first address and can expand `PORT_TO` for protocols with ports. The second address is parsed as a single address, not a range. IPv6 operations reject IP ranges and require any CIDR to equal `/128`, but still allow port range expansion. Single operations and `IPSET_TEST` go straight to the generated ADT path.

## State and persistence behavior

The generic hash layer stores normalized tuple elements and all enabled ipset extensions. IPv4 retry state stores the next first-address and port in `h->next`; IPv6 retry state stores only the next port. There is no global state beyond the registered `ip_set_type`.

## Dependencies and integration points

The file integrates with ipset core APIs, netlink attribute policies, packet port extraction helpers, and the generic hash implementation. Its type registration advertises `IPSET_TYPE_IP | IPSET_TYPE_PORT | IPSET_TYPE_IP2`, dimension three, and `NFPROTO_UNSPEC`, allowing both address families under one module alias.

## Risks

Only the first IP dimension is range-expanded; users expecting `IP2_TO` support will not get it because the policy does not include it. Protocol handling mirrors `hash:ip,port`, so non-port protocols collapse the port to zero. Very large IPv4 IP/port expansions are capped by `IPSET_MAX_RANGE` and depend on retry cursor correctness.

## Test signals

Tests should add/test/delete IPv4 and IPv6 tuples, verify source/destination flag mapping for all three dimensions, exercise IPv4 first-IP CIDR/range plus port ranges, confirm IPv6 IP range rejection and port range acceptance, validate missing/zero protocol errors, and check list output for both IP attributes.
