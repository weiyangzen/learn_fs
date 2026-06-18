# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipport.c

## Purpose

`ip_set_hash_ipport.c` implements the `hash:ip,port` ipset type. It matches an IP address plus transport protocol/port, with create-time netmask and bitmask support. The module handles packet decoding for IPv4 and IPv6 and userspace netlink add/delete/test operations, while generic hash mechanics come from `ip_set_hash_gen.h`.

## Important APIs, types, and functions

`struct hash_ipport4_elem` stores IPv4 address, port, protocol, and padding. `struct hash_ipport6_elem` stores IPv6 address, port, and protocol. `hash_ipport{4,6}_data_equal()` compares IP, port, and protocol; `data_list()` emits `IPSET_ATTR_IP`, `IPSET_ATTR_PORT`, and `IPSET_ATTR_PROTO`; and `data_next()` captures IP/port progress for range retries. `hash_ipport{4,6}_kadt()` extracts packet ports with `ip_set_get_ip{4,6}_port()`, extracts the configured packet address dimension, applies `h->bitmask`, rejects all-zero masked IPs, and dispatches the operation. `hash_ipport{4,6}_uadt()` validates netlink protocol/port/IP attributes, parses optional IP and port ranges, and handles protocols without ports by zeroing the port unless the protocol is ICMP/ICMPv6.

## Control flow

The file sets `IP_SET_HASH_WITH_NETMASK` and `IP_SET_HASH_WITH_BITMASK` before including the hash generator for IPv4 and IPv6. Userspace IPv4 control flow validates required IP and port attributes, gets extensions, masks the IP, parses `IPSET_ATTR_PROTO`, decides whether port ranges are meaningful, and either performs a single ADT call or nests IP and port loops. `IPSET_ATTR_CIDR` converts the IPv4 IP dimension into a host-order range; `IPSET_ATTR_PORT_TO` expands only for protocols with ports. IPv6 rejects IP ranges and non-host CIDR, but supports port range expansion for port protocols. The registered type advertises dimension two and features `IPSET_TYPE_IP | IPSET_TYPE_PORT`.

## State and persistence behavior

Stored elements are normalized by protocol and address bitmask. Generic hash state persists table allocation, timeouts, comments/counters/skbinfo extensions, bucket size, initval, resize policy, and range retry cursor. No file-local persistent data exists after registration.

## Dependencies and integration points

The module depends on `ip_set_getport.h` to parse packet ports, ipset netlink helpers for userspace attributes, `pfxlen.h` for CIDR/range conversion, and generic hash infrastructure. It is loaded via `MODULE_ALIAS("ip_set_hash:ip,port")` and used by iptables/nftables set match/target paths.

## Risks

The port field becomes zero for protocols without ports, which is correct but can surprise users who supply a port with AH/ESP-like protocols. ICMP and ICMPv6 use the port field to hold type/code style data and are special-cased. All-zero masked IPs are rejected, so broad bitmasks can make entries invalid. Large IPv4 IP x port products are bounded and require retry handling.

## Test signals

Tests should cover TCP/UDP/SCTP/UDPLITE port matching, ICMP and ICMPv6 behavior, non-port protocol normalization to port zero, IPv4 IP and port range expansion, IPv6 port range with rejected IP ranges, bitmask/netmask create options, all-zero masked IP rejection, extension preservation during list output, and packet-path source/destination dimension selection.
