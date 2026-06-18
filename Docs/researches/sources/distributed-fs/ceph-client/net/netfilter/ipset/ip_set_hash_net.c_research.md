# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_net.c

## Purpose

`ip_set_hash_net.c` implements `hash:net`, an ipset type whose element is one IP network prefix. It supports IPv4 range input, IPv6 exact-prefix input, and `nomatch` entries for negative matches.

## Important APIs, types, and functions

`struct hash_net4_elem` and `struct hash_net6_elem` store IP, CIDR, and `nomatch`. `hash_net{4,6}_data_equal()` compares normalized network address and CIDR. `do_data_match()`, `data_set_flags()`, and `data_reset_flags()` implement `IPSET_FLAG_NOMATCH`. `data_netmask()` masks the stored address to the requested prefix. `data_list()` serializes the address, `IPSET_ATTR_CIDR`, and optional `CADT_FLAGS`. `hash_net{4,6}_kadt()` extracts source or destination packet IP and masks it by the current lookup CIDR. `hash_net{4,6}_uadt()` parses userspace attributes, extensions, CIDR, flags, and optional IPv4 ranges.

## Control flow

The generic hash include is configured with `IP_SET_HASH_WITH_NETS`, so the generated lookup code can search stored prefixes. Packet tests use host-width CIDR to let generic net lookup iterate candidate prefixes. IPv4 userspace `uadt` converts a single entry into network form with `ip_set_hostmask(e.cidr)`, or expands `IP_TO` ranges by repeatedly selecting the largest CIDR block via `ip_set_range_to_cidr()`. IPv6 rejects `IP_TO` and only accepts explicit CIDR values from 1 to 128. Results pass through `ip_set_enomatch()` and `ip_set_eexist()` handling for consistent `nomatch` and `-exist` semantics.

## State and persistence behavior

The set stores normalized prefix entries, `nomatch` bits, and generic extensions. The IPv4 retry cursor stores the next IP in `h->next.ip`. Timed entries are handled by generic hash timeout machinery. The module does not persist state outside the ipset object.

## Dependencies and integration points

Dependencies include ipset core, generic hash, prefix length helpers, netlink address parsers, and packet IP address accessors. The registered type advertises `IPSET_TYPE_IP | IPSET_TYPE_NOMATCH`, dimension one, and supports revision features up to bucketsize/initval.

## Risks

CIDR zero is rejected for this type, so it cannot represent `/0` here. IPv4 `IP_TO` covering the entire 32-bit space is rejected by the overflow guard. `nomatch` behavior can invert tests unexpectedly if callers ignore `CADT_FLAGS`. Prefix normalization means listing may show masked network addresses rather than the exact input host.

## Test signals

Tests should cover IPv4 and IPv6 prefix add/test/delete, IPv4 range-to-CIDR decomposition, CIDR validation including zero rejection, `nomatch` outcomes, timeout cleanup, extension list output, packet source/destination lookups, and retry behavior for large IPv4 ranges.
