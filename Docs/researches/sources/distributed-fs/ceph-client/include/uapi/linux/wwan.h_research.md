<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wwan.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/wwan.h

Purpose: defines rtnetlink attributes for WWAN network device link metadata.

Important APIs and types: the enum defines `IFLA_WWAN_LINK_ID` as a u32 attribute and `IFLA_WWAN_MAX` for validation.

Control flow, state, and persistence: userspace reads or sets WWAN link attributes through rtnetlink when creating or inspecting WWAN netdevices. The header contains no runtime state; per-link state is stored in netdevice/driver structures.

Dependencies and integration points: integrates WWAN core, netlink link attributes, modem drivers, and network management tools.

Risks and test signals: risks are mainly attribute-number drift and missing validation for link IDs. Test netlink dump/newlink paths, multiple WWAN links, invalid attribute lengths, and userspace manager compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wwan.h -->
