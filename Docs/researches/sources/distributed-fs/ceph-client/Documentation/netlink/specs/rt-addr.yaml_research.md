# sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-addr.yaml

Purpose: this raw rtnetlink schema documents address configuration messages for IPv4/IPv6 interface addresses and multicast addresses. It maps `RTM_NEWADDR`, `RTM_DELADDR`, `RTM_GETADDR`, and multicast address dumping onto YAML netlink metadata.

Important APIs, types, and functions: fixed header `ifaddrmsg` carries address family, prefix length, `ifa-flags`, scope, and interface index. `ifa-cacheinfo` stores preferred/valid lifetimes and timestamps. `ifa-flags` defines secondary, nodad, optimistic, dadfailed, homeaddress, deprecated, tentative, permanent, managetempaddr, noprefixroute, mcautojoin, and stable-privacy. `addr-attrs` includes address, local, label, broadcast, anycast, cacheinfo, multicast, flags, route priority, target netns id, and protocol.

Control flow: `newaddr` value 20 adds or announces an address using address, label, local, and cacheinfo. `deladdr` value 21 removes an address by address/local. `getaddr` value 22 is dump-only and replies as value 20 with the common address attributes. `getmulticast` value 58 supports do and dump flows with multicast and cacheinfo replies.

State and persistence: interface address state is maintained by the networking stack and persists until deleted, interface teardown, namespace teardown, or address lifetime expiry. Cache info exposes lifetime and timestamp behavior but is not stored by this YAML.

Dependencies and integration: depends on `linux/rtnetlink.h`, raw netlink protocol number 0, generated schema consumers, and rtnetlink multicast groups `rtnlgrp-ipv4-ifaddr` and `rtnlgrp-ipv6-ifaddr` for change notifications.

Risks: address payloads are binary and family-dependent; broadcast is explicitly big-endian IPv4 while address/local are generic IPv4-or-IPv6. Dumps can race with concurrent address changes. Test signals include add/delete/dump round trips in a disposable namespace, IPv4/IPv6 payload rendering, flag bitmask validation, lifetime/cacheinfo formatting, and multicast notification observation.
