<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tc_tunnel.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tc_tunnel.c

Purpose: end-to-end TC tunnel suite comparing BPF encapsulation and decapsulation against kernel tunnel decapsulation for many IPv4/IPv6, Ethernet, MPLS, GRE, VXLAN, IPIP, SIT, UDP/FOU, and GSO variants.

Important APIs/types/functions: `struct subtest_cfg` describes tunnel type, iproute type, MAC mode, IP protocol, FOU/MPLS/GSO flags, addresses, program fds, and server fd. Helpers include `set_subtest_progs()`, `run_server()`, `send_and_test_data()`, `configure_kernel_decapsulation()`, `configure_ebpf_decapsulation()`, `setup()`, `subtest_setup()`, and `subtest_cleanup()`. Uses generated `test_tc_tunnel.skel.h` and `tc_prog_attach()`.

Control flow: global setup creates client/server netns, veth pair, and random tx buffer. Each config builds a subtest name, resolves BPF encap/decap program fds, configures veth addresses/routes, starts a TCP server, verifies plain connectivity, attaches BPF encap to client egress and expects connectivity to require decap, optionally configures a kernel tunnel device for decap and verifies traffic, then replaces/removes it with BPF decap on server ingress and verifies traffic again. Cleanup removes qdiscs, addresses, kernel tunnels, FOU ports, MPLS routes, and namespaces.

State and persistence: creates two netns, veth devices, `testtun0`, FOU ports, MPLS sysctls/routes, qdiscs, sockets, and BPF TC links. Random tx data is process-global. Cleanup is substantial and mostly best-effort.

Dependencies and integration: requires iproute2 tunnel support, ethtool, TC, TCP sockets, network privileges, BPF TC programs, optional MPLS and FOU kernel support, and generated skeleton. Integrated as `test_tc_tunnel`.

Risks: broad environment surface and many kernel modules/features. Some configs set `expect_kern_decap_failure` and skip kernel decap assertions. GSO path sends 2000 bytes but checks only default receive size, matching current helper behavior. Failures can leave netns/tunnel state if cleanup is bypassed before global cleanup.

Test signals: per-subtest connectivity assertions for plain, kernel-decap, and BPF-decap paths; exact received data comparisons; setup/attach command assertions; and cleanup after each subtest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tc_tunnel.c -->
