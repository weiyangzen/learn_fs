# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netport.c

## Purpose

`ip_set_hash_netport.c` implements `hash:net,port`, matching an IP network with protocol/port. It supports `nomatch`, IPv4 network and port ranges, IPv6 port ranges, and packed CIDR storage.

## Important APIs, types, and functions

Elements contain IP, port, protocol, packed CIDR, and `nomatch`. `hash_netport{4,6}_data_equal()` compares normalized network, port, protocol, and CIDR. `do_data_match()`, `data_set_flags()`, and `data_reset_flags()` implement `nomatch`. `data_netmask()` masks IP and stores `cidr - 1`. `data_list()` emits IP, port, `CIDR`, protocol, and optional flags. Packet-path `kadt` functions read packet port/protocol from dimension two, read the selected packet IP from dimension one, mask by current CIDR, and dispatch. Userspace `uadt` functions parse network, port, protocol, flags, optional ranges, and extensions.

## Control flow

The module enables `IP_SET_HASH_WITH_PROTO`, `IP_SET_HASH_WITH_NETS`, and `IP_SET_HASH_WITH_NETS_PACKED`. IPv4 single operations normalize `ip` by `ip_set_hostmask(e.cidr + 1)` and handle `nomatch` result translation. Range operations expand the IP range into CIDR blocks and loop through a port range when the protocol has ports. IPv6 rejects IP ranges, masks by CIDR, and only loops over ports. Non-port protocols store port zero except ICMP/ICMPv6.

## State and persistence behavior

State is in the generic hash table and per-element extensions. The packed CIDR representation is persistent on elements but serialized as `cidr + 1`. IPv4 retry state stores next IP and port. The module has no standalone mutable state.

## Dependencies and integration points

Dependencies include ipset core, generic hash code, transport port extraction helpers, prefix helpers, and netlink policies. The registered type advertises `IPSET_TYPE_IP | IPSET_TYPE_PORT | IPSET_TYPE_NOMATCH`.

## Risks

CIDR zero is not supported because `cidr - 1` is stored. Large IPv4 network x port expansions can hit `IPSET_MAX_RANGE`. Non-port protocols silently normalize port to zero after validation. Correct `nomatch` behavior requires `CADT_FLAGS` to be preserved through add/test/list.

## Test signals

Tests should cover IPv4 and IPv6 network/port matches, protocol handling for TCP/UDP/SCTP/UDPLITE/ICMP, port range expansion, IPv4 network range expansion and retry, IPv6 IP range rejection, `nomatch`, CIDR validation, timeout and extension listing, and packet direction flags.
