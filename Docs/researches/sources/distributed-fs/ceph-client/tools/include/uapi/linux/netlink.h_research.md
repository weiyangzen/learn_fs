# sources/distributed-fs/ceph-client/tools/include/uapi/linux/netlink.h

Purpose: defines the core Netlink socket ABI: protocol numbers, socket/message headers, request flags, alignment helpers, error/extended-ack attributes, socket options, mmap ring structs, generic attribute headers, and bitfield attributes.

Important APIs/types: `sockaddr_nl` identifies netlink family, port ID, and multicast groups. `nlmsghdr` is the common message header with length/type/flags/sequence/pid. Macros handle request/dump/create/delete flags, ACK flags, `NLMSG_ALIGN`, `NLMSG_LENGTH`, `NLMSG_SPACE`, `NLMSG_DATA`, `NLMSG_NEXT`, `NLMSG_OK`, and `NLMSG_PAYLOAD`. `nlmsgerr` and `nlmsgerr_attrs` support ACK/error reporting. Socket options include memberships, packet info, broadcast errors, no-ENOBUFS, mmap rings, namespace listening, capped ACK, extended ACK, and strict checking. `nlattr` plus `NLA_*` flags/macros define nested/network-order TLVs; `nla_bitfield32` carries masked bit updates.

Control flow, state, and persistence: userspace sends datagrams containing one or more aligned `nlmsghdr` messages and nested attributes; kernel replies with ACKs, dumps, multicast notifications, or errors. Socket membership and mmap ring state persist for the socket lifetime; subsystem state is managed by protocol-specific families.

Dependencies and integration points: depends on kernel/socket/types headers and underpins rtnetlink, Generic Netlink, netfilter netlink, audit, uevent, crypto, RDMA, and many management tools.

Risks and test signals: risks include length/alignment bugs, infinite/unsafe message iteration on malformed lengths, lost multicast notifications, stale sequence handling, strict-check incompatibilities, and nested attribute flag misuse. Tests should parse malformed messages, validate multi-part dumps and ACK TLVs, join/drop multicast groups, use strict checking, and fuzz nested attributes.
