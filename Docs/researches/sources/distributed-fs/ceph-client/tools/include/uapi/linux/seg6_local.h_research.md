<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/seg6_local.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/seg6_local.h

Purpose: this header defines netlink attributes and action IDs for SRv6 local segment endpoint behaviors.

Important APIs/types: `SEG6_LOCAL_*` attributes describe action, SRH, table, IPv4/IPv6 nexthops, input/output interfaces, and BPF configuration. `SEG6_LOCAL_ACTION_*` enumerates endpoint behaviors such as End, End.X, End.T, End.DX2/DX4/DX6, End.DT4/DT6, End.B6, End.B6.Encap, End.BM, End.S, End.AS, End.AM, and End.BPF. `SEG6_LOCAL_BPF_PROG*` attributes attach BPF program descriptors and names.

Control flow: userspace route tools encode these values in rtnetlink encapsulation/local-action attributes. Kernel SRv6 local processing dispatches the configured behavior when packets match a local SID.

State and persistence: configured SRv6 local actions persist as routing entries or lightweight tunnel state in the kernel. This file only defines the ABI values.

Dependencies/integration: includes `linux/seg6.h`; integrated with IPv6 routing, lightweight tunnels, BPF, and `iproute2` SRv6 commands.

Risks and test signals: risks include mismatched action IDs, missing mandatory attributes for a chosen action, BPF attachment compatibility, and route-table interactions. Test by adding/dumping each local action type and verifying packet forwarding/decapsulation behavior for nexthop/table/SRH cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/seg6_local.h -->
