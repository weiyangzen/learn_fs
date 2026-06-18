# sources/distributed-fs/ceph-client/include/uapi/linux/netlink_diag.h

## Purpose

`netlink_diag.h` defines the netlink socket diagnostic ABI used by sock_diag to request and report AF_NETLINK socket state. The file is 67 lines and is part of the netlink core/diagnostic ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `netlink_diag_req`, `netlink_diag_msg`, `netlink_diag_ring`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `NETLINK_DIAG_MEMINFO`, `NETLINK_DIAG_GROUPS`, `NETLINK_DIAG_RX_RING`, `NETLINK_DIAG_TX_RING`, `NETLINK_DIAG_FLAGS`. Macros expose `_UAPI__NETLINK_DIAG_H__`, `NETLINK_DIAG_MAX`, `NDIAG_PROTO_ALL`, `NDIAG_SHOW_MEMINFO`, `NDIAG_SHOW_GROUPS`, `NDIAG_SHOW_RING_CFG`, `NDIAG_SHOW_FLAGS`, `NDIAG_FLAG_CB_RUNNING`, `NDIAG_FLAG_PKTINFO`, `NDIAG_FLAG_BROADCAST_ERROR`, `NDIAG_FLAG_NO_ENOBUFS`, `NDIAG_FLAG_LISTEN_ALL_NSID`, `NDIAG_FLAG_CAP_ACK`. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

sock_diag clients send `netlink_diag_req` filters and receive `netlink_diag_msg` records plus optional memory, group, ring, and flag attributes. The header defines request/report shape only; collection occurs in the netlink diagnostic subsystem.

## State and Persistence Behavior

The header has no storage of its own. State lives in netlink sockets, routing nexthop objects, NFC devices, or diagnostic snapshots maintained by kernel subsystems and userspace daemons. The declared numeric values and structure layouts are persistent UAPI contracts.

## Dependencies and Integration Points

It integrates with AF_NETLINK sockets, generic netlink, rtnetlink, sock_diag, libmnl/libnl-style parsers, and kernel netlink family implementations. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: NETLINK_DIAG_NONE, standard nl API requires this attribute!; deprecated since 4.6.
