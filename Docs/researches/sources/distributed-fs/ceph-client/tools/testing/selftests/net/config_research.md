# sources/distributed-fs/ceph-client/tools/testing/selftests/net/config

Purpose: this is the broad kernel configuration manifest for networking selftests. It declares modules and built-in features needed by many tests in `tools/testing/selftests/net`, including namespaces, virtual devices, tunnels, bridge/VRF/VLAN, netfilter/nftables, qdiscs, classifiers, actions, CAN, MPTCP, TLS, XFRM, MPLS, Open vSwitch, drop monitor, and BPF-related support.

Important entries: the files in this subset directly rely on entries such as `CONFIG_NET_NS`, `CONFIG_DUMMY`, `CONFIG_VETH`, `CONFIG_VLAN_8021Q`, `CONFIG_BRIDGE`, `CONFIG_BRIDGE_VLAN_FILTERING`, `CONFIG_NET_VRF`, `CONFIG_VXLAN`, `CONFIG_GENEVE`, `CONFIG_NET_DROP_MONITOR`, `CONFIG_NETDEVSIM`, `CONFIG_NET_SCH_FQ`, `CONFIG_NET_CLS_FLOWER`, `CONFIG_NET_ACT_GACT`, `CONFIG_CAN`, `CONFIG_CAN_DEV`, `CONFIG_CAN_VCAN`, and IPv4/IPv6 netfilter options. Busy-poll and NAPI tests additionally depend on netdev/YNL kernel interfaces not fully expressed by this manifest.

Control flow and state: the file is declarative; it is consumed by kselftest tooling or humans to prepare a kernel. It does not execute or persist runtime state.

Dependencies and integration points: it integrates at the repository/test-suite level rather than with one binary. The manifest helps CI builders avoid running tests against kernels missing mandatory features.

Risks and test signals: config coverage is necessary but not sufficient. User-space tools (`ip`, `bridge`, `tc`, `jq`, `tcpdump`, `tshark`, `dwdump`, `mausezahn`, generated helpers) must also exist and be recent enough. A strong signal is that skip paths in the scripts are not reached and the underlying kernel options match the features being exercised.
