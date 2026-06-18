# sources/distributed-fs/ceph-client/net/ipv4/netlink.c

## Purpose
Validates the optional IP protocol selector for rtnetlink route-get requests. It centralizes accepted protocol values for route lookup parsing.

## Important APIs, types, and functions
The exported function is `rtm_getroute_parse_ip_proto(struct nlattr *attr, u8 *ip_proto, u8 family, struct netlink_ext_ack *extack)`. It reads a `u8` netlink attribute and accepts TCP, UDP, IPv4 ICMP for `AF_INET`, and ICMPv6 for `AF_INET6` when IPv6 is enabled.

## Control flow
The function stores `nla_get_u8(attr)` in the caller output and switches on it. Valid protocol/family combinations return zero. Unsupported combinations set `"Unsupported ip proto"` in extack and return `-EOPNOTSUPP`.

## State and persistence
No state. The function only writes the output byte and optional extended ack.

## Dependencies and integration points
Depends on netlink attributes, rtnetlink route-get handlers, protocol constants, and `netlink_ext_ack`. Exported as GPL for shared route parsing.

## Risks
The allowlist is narrow; support for more transports requires updating this validator. Callers must pass the effective address family to avoid false rejection.

## Test signals
Validate TCP/UDP, ICMP with IPv4 only, ICMPv6 with IPv6 AF_INET6 only, unsupported values, extack content, and boundary `u8` values.
