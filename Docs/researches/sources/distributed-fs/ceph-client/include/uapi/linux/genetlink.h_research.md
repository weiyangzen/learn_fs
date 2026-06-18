<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/genetlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/genetlink.h

## Purpose
`genetlink.h` defines the generic netlink wire ABI: message header shape, static family ID ranges, operation flags, and the controller family used to discover families, operations, multicast groups, and policy dumps.

## Important APIs, types, and functions
The core message prefix is `struct genlmsghdr` with `cmd`, `version`, and `reserved`. Constants include `GENL_NAMSIZ`, `GENL_MIN_ID`, `GENL_MAX_ID`, `GENL_ID_CTRL`, `GENL_START_ALLOC`, and operation flags such as `GENL_ADMIN_PERM`, `GENL_CMD_CAP_DO`, `GENL_CMD_CAP_DUMP`, `GENL_CMD_CAP_HASPOL`, and `GENL_UNS_ADMIN_PERM`. Controller enums define `CTRL_CMD_*`, `CTRL_ATTR_*`, `CTRL_ATTR_OP_*`, `CTRL_ATTR_MCAST_GRP_*`, and `CTRL_ATTR_POLICY_*`.

## Control flow
Generic netlink messages travel as normal netlink messages whose payload starts with `genlmsghdr`, followed by family-specific attributes. User space queries the controller family with `CTRL_CMD_GETFAMILY` or policy commands before issuing family-specific commands.

## State and persistence behavior
The header declares no storage. Runtime state lives in registered kernel generic-netlink families, their dynamic IDs, multicast groups, and operation policies.

## Dependencies and integration points
It depends on `<linux/types.h>` and `<linux/netlink.h>`. It is the common discovery layer used by many headers in this subset, including GTP and handshake.

## Risks and test signals
Risks include treating dynamic family IDs as stable, missing admin-permission checks, policy nesting mismatches, and older tools not understanding newer controller attributes. Test signals are `genl-ctrl-list`, YNL policy dumps, strict attribute validation, multicast group discovery, and 32/64-bit header alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/genetlink.h -->
