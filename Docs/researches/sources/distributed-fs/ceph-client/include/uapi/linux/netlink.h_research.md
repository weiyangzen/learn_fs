# sources/distributed-fs/ceph-client/include/uapi/linux/netlink.h

## Purpose

`netlink.h` defines the core AF_NETLINK userspace ABI: socket address layout, message headers, flags, attributes, multicast controls, mmap rings, capability flags, and helper macros. The file is 383 lines and is part of the netlink core/diagnostic ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/const.h`, `linux/socket.h`, `linux/types.h`. Exported structures include `sockaddr_nl`, `nlmsghdr`, `nlmsgerr`, `nl_pktinfo`, `nl_mmap_req`, `nl_mmap_hdr`, `nlattr`, `nla_bitfield32`. Enumerations include `nlmsgerr_attrs`, `nl_mmap_status`, `anonymous enum`, `netlink_attribute_type`, `netlink_policy_type_attr`. Prominent attribute, command, flag, or constant names include `NLMSGERR_ATTR_UNUSED`, `NLMSGERR_ATTR_MSG`, `NLMSGERR_ATTR_OFFS`, `NLMSGERR_ATTR_COOKIE`, `NLMSGERR_ATTR_POLICY`, `NLMSGERR_ATTR_MISS_TYPE`, `NLMSGERR_ATTR_MISS_NEST`, `NLMSGERR_ATTR_MAX`, `NL_MMAP_STATUS_UNUSED`, `NL_MMAP_STATUS_RESERVED`, `NL_MMAP_STATUS_VALID`, `NL_MMAP_STATUS_COPY`, `NL_MMAP_STATUS_SKIP`, `NETLINK_UNCONNECTED`, `NETLINK_CONNECTED`, `NL_ATTR_TYPE_INVALID`, `NL_ATTR_TYPE_FLAG`, `NL_ATTR_TYPE_U8`, `NL_ATTR_TYPE_U16`, `NL_ATTR_TYPE_U32`, `NL_ATTR_TYPE_U64`, `NL_ATTR_TYPE_S8`, and 25 more. Macros expose `_UAPI__LINUX_NETLINK_H`, `NETLINK_ROUTE`, `NETLINK_UNUSED`, `NETLINK_USERSOCK`, `NETLINK_FIREWALL`, `NETLINK_SOCK_DIAG`, `NETLINK_NFLOG`, `NETLINK_XFRM`, `NETLINK_SELINUX`, `NETLINK_ISCSI`, `NETLINK_AUDIT`, `NETLINK_FIB_LOOKUP`, `NETLINK_CONNECTOR`, `NETLINK_NETFILTER`, `NETLINK_IP6_FW`, `NETLINK_DNRTMSG`, `NETLINK_KOBJECT_UEVENT`, `NETLINK_GENERIC`, and 61 more. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

AF_NETLINK control flow is message based: user space writes `nlmsghdr` records with flags and optional attributes, kernel families parse and respond, and multipart or acknowledgement behavior is controlled by message flags. Mmap ring structures define an alternate packetized producer/consumer flow for sockets that use netlink mmap.

## State and Persistence Behavior

The header has no storage of its own. State lives in netlink sockets, routing nexthop objects, NFC devices, or diagnostic snapshots maintained by kernel subsystems and userspace daemons. The declared numeric values and structure layouts are persistent UAPI contracts.

## Dependencies and Integration Points

It integrates with AF_NETLINK sockets, generic netlink, rtnetlink, sock_diag, libmnl/libnl-style parsers, and kernel netlink family implementations. It directly includes `linux/const.h`, `linux/socket.h`, `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: leave room for NETLINK_DM (DM Events); struct nlmsghdr - fixed format metadata header of Netlink messages; @nlmsg_len:   Length of message including header.
