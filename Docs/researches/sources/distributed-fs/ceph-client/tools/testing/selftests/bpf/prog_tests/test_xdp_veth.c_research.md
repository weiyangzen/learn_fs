<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xdp_veth.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xdp_veth.c

Purpose: end-to-end XDP redirect suite over three veth pairs and four namespaces, covering chained redirect, broadcast/multicast redirect flags, and devmap egress programs.

Important APIs/types/functions: `struct veth_configuration`, `struct net_configuration`, `struct prog_configuration`, `create_network()`, `cleanup_network()`, `attach_programs_to_veth_pair()`, `xdp_veth_redirect()`, `xdp_veth_broadcast_redirect()`, and `xdp_veth_egress()`. Uses skeletons `xdp_dummy`, `xdp_redirect_map`, `xdp_redirect_multi_kern`, and `xdp_tx`, plus `bpf_xdp_attach()`, devmap updates, and ping.

Control flow: network creation copies a default topology, appends tid suffixes to namespace names, creates one ns0 namespace plus three remote namespaces and veth pairs. Redirect test loads dummy/tx/redirect-map programs, populates a tx-port map with next local ifindexes, attaches local and remote XDP programs, and pings destination. Broadcast test loads multi-redirect programs, configures redirect flags and devmap entries, pings a neighbor address, and checks per-interface receive counts with and without `BPF_F_EXCLUDE_INGRESS`. Egress test configures devmap egress program and magic MAC map, pings, then checks stored rx MACs.

State and persistence: creates multiple netns and veths, attaches XDP programs in ns0 and remote namespaces, updates BPF maps with ifindexes, flags, counters, and MACs. Cleanup removes namespaces and destroys skeletons; close_netns is used around namespace switches.

Dependencies and integration: requires XDP attach in generic/driver/SKB modes, devmap and devmap egress support, iproute2, ping, network namespaces, generated skeletons, and root privileges. Exposes three entry points: `test_xdp_veth_redirect`, `test_xdp_veth_broadcast_redirect`, and `test_xdp_veth_egress`.

Risks: driver mode can be unsupported on veth depending on kernel/config. A failure before `create_network()` initializes `net_config` can still call cleanup with uninitialized names in some paths. Egress test calls `attach_programs_to_veth_pair()` with `VETH_REDIRECT_SKEL_NB` instead of `VETH_EGRESS_SKEL_NB`; values are both 3 today, but the coupling is fragile.

Test signals: XDP attach success, redirect/devmap update success, ping success, exact receive counts (`4` or `0` for excluded ingress), and magic MAC comparisons for egress results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xdp_veth.c -->
