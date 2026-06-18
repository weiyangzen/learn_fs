# sources/distributed-fs/ceph-client/include/uapi/linux/nexthop.h

## Purpose

`nexthop.h` defines rtnetlink nexthop object attributes, group flags, resilient group controls, and notifier event constants for shared routing nexthop management. The file is 157 lines and is part of the routing nexthop netlink ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `nhmsg`, `nexthop_grp`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `NEXTHOP_GRP_TYPE_MPATH`, `NEXTHOP_GRP_TYPE_RES`, `NHA_UNSPEC`, `NHA_ID`, `NHA_GROUP`, `NHA_GROUP_TYPE`, `NHA_BLACKHOLE`, `NHA_OIF`, `NHA_GATEWAY`, `NHA_ENCAP_TYPE`, `NHA_ENCAP`, `NHA_GROUPS`, `NHA_MASTER`, `NHA_FDB`, `NHA_RES_GROUP`, `NHA_RES_BUCKET`, `NHA_OP_FLAGS`, `NHA_GROUP_STATS`, `NHA_HW_STATS_ENABLE`, `NHA_HW_STATS_USED`, `NHA_RES_GROUP_UNSPEC`, `NHA_RES_GROUP_PAD`, and 15 more. Macros expose `_UAPI_LINUX_NEXTHOP_H`, `NEXTHOP_GRP_TYPE_MAX`, `NHA_OP_FLAG_DUMP_STATS`, `NHA_OP_FLAG_DUMP_HW_STATS`, `NHA_OP_FLAG_RESP_GRP_RESVD_0`, `NHA_MAX`, `NHA_RES_GROUP_MAX`, `NHA_RES_BUCKET_MAX`, `NHA_GROUP_STATS_MAX`, `NHA_GROUP_STATS_ENTRY_MAX`. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

Routing daemons create, replace, delete, and dump nexthop objects over rtnetlink using the attributes defined here. Group and resilient-group attributes describe selection buckets and idle/unbalanced timers, while notifier types report replace and delete events.

## State and Persistence Behavior

The header has no storage of its own. State lives in netlink sockets, routing nexthop objects, NFC devices, or diagnostic snapshots maintained by kernel subsystems and userspace daemons. The declared numeric values and structure layouts are persistent UAPI contracts.

## Dependencies and Integration Points

It integrates with rtnetlink route management, fib nexthop objects, resilient hashing, routing daemons, and netlink parsers in iproute2-style tooling. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: entry in a nexthop group; default type if not specified; Response OP_FLAGS..
