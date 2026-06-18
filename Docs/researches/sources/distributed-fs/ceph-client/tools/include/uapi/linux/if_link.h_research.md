# sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_link.h

Purpose: large rtnetlink link-configuration ABI for network device attributes, statistics, link kinds, virtual devices, bridge/bond/VLAN/tunnel/SR-IOV settings, XDP attachment, and link stats queries.

Important APIs/types: core stats structures are `rtnl_link_stats`, `rtnl_link_stats64`, `rtnl_hw_stats64`, `rtnl_link_ifmap`, and `if_stats_msg`. Top-level `IFLA_*` attributes cover addresses, name, MTU, qdisc, master, netns, stats, carrier, phys port/switch IDs, alt names, parent device, offload sizes, devlink port, DPLL, and pacing horizon. Nested families cover IPv4/IPv6 `AF_SPEC`, bridge and bridge-port options, `IFLA_INFO_*` link-kind data, VLAN, MACVLAN, VRF, MACsec, XFRM, IPVLAN, netkit, VXLAN/VNI filters, Geneve, bareudp, PPP, GTP, bonding and bond slaves, SR-IOV VF config/stats, VF ports, IPoIB, HSR/PRP, offload stats, XDP, TUN, rmnet, MCTP, and DSA.

Control flow, state, and persistence: userspace sends rtnetlink `RTM_NEWLINK`, `DELLINK`, `GETLINK`, and stats requests with nested attributes. Kernel validates link-kind-specific payloads, mutates netdev/bridge/bond/tunnel state, and emits notifications. Most settings persist for the life of the netdev or network namespace; stats are counters.

Dependencies and integration points: depends on `types.h` and `netlink.h`. It is central to iproute2, network managers, container runtimes, virtual networking, XDP loaders, SR-IOV tooling, switchdev/offload drivers, and tunnel configuration.

Risks and test signals: risks include nested attribute misalignment, wrong attribute family for a link kind, enum value drift, 32-bit stats overflow if `STATS64` is ignored, destructive bridge/bond changes, and unsupported XDP mode combinations. Tests should create/dump/change representative links for each major kind, verify netns moves, stats filters, XDP attach/replace semantics, SR-IOV VF attributes, and unknown-attribute compatibility.
