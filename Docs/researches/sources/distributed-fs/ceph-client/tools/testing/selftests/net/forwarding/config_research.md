# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/config

## Purpose
`config` is a Kconfig fragment for the forwarding selftest suite. It lists kernel options and modules needed by bridge, tunnel, VRF, traffic-control, BPF, netfilter, routing, and virtual-interface tests in this directory.

## Important APIs, Types, and Integration Points
The file is declarative rather than executable. It requests core namespace and interface support (`CONFIG_NET_NS`, `CONFIG_NAMESPACES`, `CONFIG_VETH`, `CONFIG_DUMMY`, `CONFIG_MACVLAN`, `CONFIG_NET_VRF`), bridge features (`CONFIG_BRIDGE`, `CONFIG_BRIDGE_VLAN_FILTERING`, `CONFIG_BRIDGE_IGMP_SNOOPING`), IPv4/IPv6 forwarding and multicast routing features, GRE/IPIP/VXLAN tunnels, VLAN 802.1Q, team load-balancing, XFRM user API, nf_tables/conntrack/flowtable, BPF syscall and cgroup BPF, and many tc classifiers/actions/qdiscs (`flower`, `u32`, `matchall`, `mirred`, `vlan`, `skbedit`, `police`, `ingress`, `prio`, `tbf`, etc.).

## State, Dependencies, Risks, and Test Signals
There is no runtime state or control flow. The file integrates with kselftest build/config tooling that can merge fragments into a kernel config. Missing options translate into skipped or failed runtime tests in scripts that expect bridge snooping, VRFs, tunnels, tc filters, or packet manipulation modules. The main risk is configuration drift: new forwarding tests may require additional kernel symbols, and stale entries may mask missing coverage until runtime.
