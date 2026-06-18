# sources/distributed-fs/ceph-client/tools/include/uapi/linux/genetlink.h

Purpose: defines the Generic Netlink message header and controller ABI used to discover and manage netlink families, operations, multicast groups, and policy metadata.

Important APIs/types: `struct genlmsghdr` carries command, version, and reserved fields after a netlink header. Macros define family name length, ID ranges, header length, command capability flags, and reserved static family IDs. Controller enums define commands (`CTRL_CMD_NEWFAMILY`, `GETFAMILY`, `GETOPS`, `GETPOLICY`), family attributes, operation attributes, multicast-group attributes, and policy dump attributes.

Control flow, state, and persistence: userspace sends `NETLINK_GENERIC` messages with an `nlmsghdr`, `genlmsghdr`, and TLV attributes. The controller reports dynamic family IDs and capabilities that userspace caches for later requests. Persistent state is kernel-registered generic netlink families, not in this header.

Dependencies and integration points: depends on `<linux/types.h>` and `netlink.h`. It integrates with all Generic Netlink families, including generated YNL families such as `netdev`, and with libnl/iproute2-style discovery.

Risks and test signals: risks include stale cached family IDs, incorrect `GENL_HDRLEN` alignment, unknown controller attributes, and privilege flag handling. Tests should query `GENL_ID_CTRL`, dump families/ops/groups/policies, validate nested attributes, and check permission failures for admin-only operations.
