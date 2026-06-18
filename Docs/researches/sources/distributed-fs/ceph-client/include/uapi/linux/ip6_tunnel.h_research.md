# sources/distributed-fs/ceph-client/include/uapi/linux/ip6_tunnel.h

## Purpose
`ip6_tunnel.h` defines the UAPI configuration structures and flags for IPv6 tunnel devices.

## Important APIs, Types, and Functions
`IPV6_TLV_TNL_ENCAP_LIMIT` and `IPV6_DEFAULT_TNL_ENCAP_LIMIT` describe tunnel encapsulation-limit behavior. Flags include ignore encapsulation limit, use original traffic class, use original flow label, mobile IPv6 device, receive DSCP copy, use original fwmark, and allow local/remote addresses. `struct ip6_tnl_parm` holds name, link, proto, encapsulation limit, hop limit, flowinfo, flags, and local/remote IPv6 addresses. `struct ip6_tnl_parm2` extends it with fwmark.

## Control Flow
Userspace supplies these structures through tunnel configuration paths such as netlink or ioctl-style tooling. The kernel creates or modifies tunnel netdevices, then uses the fields when encapsulating or decapsulating packets.

## State and Persistence
Tunnel configuration persists in kernel netdevice state until device deletion or network namespace teardown. No state is stored in the header itself.

## Dependencies and Integration Points
It includes `<linux/types.h>`, `<linux/if.h>`, and `<linux/in6.h>`. It integrates with IPv6 tunnel drivers, iproute2 tunnel configuration, net namespaces, fwmark routing, and IPv6 extension header processing.

## Risks and Test Signals
Tests should cover old and extended parameter structures, `IFNAMSIZ` name truncation, local/remote address validation, flow-label and traffic-class inheritance, fwmark preservation, and compatibility when `ip6_tnl_parm2` is passed to older tooling.
