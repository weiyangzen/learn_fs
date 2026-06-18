# sources/distributed-fs/ceph-client/include/net/if_inet6.h

Purpose: defines IPv6 per-interface address, multicast, anycast, and device state structures. It is the main header for `inet6_dev` and `inet6_ifaddr` state.

Important APIs/types: `struct inet6_ifaddr` stores IPv6 address, peer, timers, prefix lengths, scope, flags, lifetimes, timestamps, route pointer, device pointer, hash/list nodes, and refcount/RCU. Multicast structures include socket source filters, per-device multicast entries, and anycast entries. `struct inet6_dev` stores device pointer, address/multicast/anycast lists, sysctl/devconf pointers, stats, token, stable secret, locks, timers, ND/RS/RA state, refcounts, and RCU. Inline helpers map IPv6 multicast addresses to Ethernet, ARCnet, InfiniBand, and GRE multicast link-layer forms.

Control flow and state: address configuration code adds/removes `inet6_ifaddr` objects under locks and RCU; timers manage DAD, lifetimes, and multicast reports. `inet6_dev` persists as per-netdevice IPv6 state until device teardown.

Dependencies and integration: depends on SNMP, IPv6, refcounting, netdevice, timers, RCU, and device configuration. It integrates with IPv6 addrconf, multicast listener discovery, neighbor discovery, routing, and socket source selection.

Risks: address lifetime timers, RCU teardown, and multicast source-filter lists are race-prone. Tests should cover address add/delete, DAD, temporary/stable privacy addresses, multicast joins/leaves, stats access, link-layer multicast mapping, device unregister, and refcount leaks.
