# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipportnet.c

## Purpose

`ip_set_hash_ipportnet.c` implements `hash:ip,port,net`, a three-dimensional ipset type matching an address, protocol/port, and a second address interpreted as a network. It supports `nomatch` entries and range expansion for IPv4 inputs, and it packs the `nomatch` flag into CIDR storage through the generic hash net support.

## Important APIs, types, and functions

IPv4 and IPv6 elements hold first IP, second network IP, port, CIDR, `nomatch`, and protocol. `hash_ipportnet{4,6}_data_equal()` compares IPs, CIDR, port, and protocol. `do_data_match()` returns `-ENOTEMPTY` for `nomatch` elements so the generic matcher can invert the result. `data_set_flags()` and `data_reset_flags()` translate `IPSET_FLAG_NOMATCH` between command flags and element state. `data_netmask()` normalizes `ip2` by CIDR and stores `cidr - 1`; `data_list()` emits `CIDR2`, `CADT_FLAGS`, protocol, port, and both IPs. The `kadt` functions build packet tuples from dimensions one, two, and three. The `uadt` functions parse IP, IP2, CIDR/CIDR2, port/proto, flags, ranges, and extensions.

## Control flow

For packet tests, the selected `ip2` address is masked by the default or lookup CIDR before calling the generated ADT operation; tests use host-width CIDR to allow generic net lookup across stored prefixes. Userspace single operations normalize `ip2` with `ip_set_hostmask(e.cidr + 1)` and apply `ip_set_enomatch()` so `nomatch` entries return the expected negative match. IPv4 range operations can expand the first IP range, port range, and second-IP range; the second range is converted to CIDR blocks with `ip_set_range_to_cidr()`. IPv6 rejects IP ranges and supports only port range expansion plus explicit `CIDR2` masking.

## State and persistence behavior

Generic hash state tracks per-CIDR network lookup metadata through `IP_SET_HASH_WITH_NETS` and packed CIDR layout. IPv4 retry state records first IP, port, and second IP in `h->next` for large Cartesian expansions. The stored `nomatch` bit is persistent element state and is serialized back through `CADT_FLAGS`.

## Dependencies and integration points

The file depends on `ip_set_getport.h`, `pfxlen.h`, ipset core netlink helpers, `ip_set_hash.h`, and generic hash macros `IP_SET_HASH_WITH_NETS_PACKED`, `IP_SET_HASH_WITH_PROTO`, and `IP_SET_HASH_WITH_NETS`. It registers the `hash:ip,port,net` module with `IPSET_TYPE_NOMATCH` so callers know negative entries are supported.

## Risks

The `cidr - 1` representation forbids CIDR zero for this packed type, so input validation is critical. IPv4 range products can grow quickly across first IP, port, and second network ranges; `IPSET_MAX_RANGE` only bounds per operation, not user surprise. `nomatch` handling depends on the caller passing and interpreting flags correctly. Protocols without ports force port zero except ICMP.

## Test signals

Tests should cover exact and network matches, `nomatch` behavior for add/test/list, IPv4 first-IP and second-IP range conversion into CIDR blocks, port range expansion and retry, IPv6 range rejection, `CIDR2` masking, ICMP/ICMPv6 and non-port protocol normalization, timeout/counter/comment/skbinfo listing, and packet-path dimension direction flags.
