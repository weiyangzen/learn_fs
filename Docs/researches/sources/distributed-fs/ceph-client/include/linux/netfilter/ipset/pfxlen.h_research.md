# sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/pfxlen.h

## Purpose
`pfxlen.h` provides prefix-length-to-mask helpers for ipset IPv4 and IPv6 network matching and range-to-CIDR conversion.

## Important APIs, Types, and Functions
It declares `ip_set_netmask_map[]`, `ip_set_hostmask_map[]`, and `ip_set_range_to_cidr()`. Inline helpers are `ip_set_netmask()`, `ip_set_netmask6()`, `ip_set_hostmask()`, `ip_set_hostmask6()`, `ip_set_mask_from_to()`, and `ip6_netmask()`.

## Control Flow
Callers convert a prefix length into network or host masks, apply masks to addresses, and use `ip_set_range_to_cidr()` to represent ranges as CIDR blocks. `ip6_netmask()` applies four 32-bit IPv6 mask words in place.

## State and Persistence
The only state is external constant mask tables. No mutable or durable state is declared.

## Dependencies and Integration Points
It depends on byteorder definitions, `union nf_inet_addr` from netfilter, and TCP/network headers. It integrates with ipset set types that support `net` dimensions or range compression.

## Risks
Prefix length must be validated before indexing tables; otherwise out-of-bounds reads are possible. IPv4 hostmask uses forced host-order conversion, so byte-order mistakes are easy. In-place IPv6 masking mutates the caller's address.

## Test Signals
Validate masks for prefix lengths 0, 1, 31/32, 127/128; test range-to-CIDR edge cases; check IPv4 byte order on little- and big-endian builds; and verify IPv6 in-place masking behavior.
