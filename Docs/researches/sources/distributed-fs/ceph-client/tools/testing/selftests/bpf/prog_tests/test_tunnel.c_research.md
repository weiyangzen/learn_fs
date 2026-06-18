<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tunnel.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tunnel.c

Purpose: broad end-to-end tunnel metadata selftest for BPF tunnel helpers over VXLAN, IPv6 VXLAN, IPIP/FOU/GUE, XFRM, GRE/GRETAP, IP6GRE/IP6GRETAP, ERSPAN/IP6ERSPAN, Geneve/IP6Geneve, and IP6TNL.

Important APIs/types/functions: topology helpers `config_device()` and `cleanup()`, tunnel add/delete helpers, `tc_prog_attach()`, `bpf_xdp_attach()` for XFRM, map `local_ip_map`, ping helpers, and generated `test_tunnel_kern.skel.h`. `RUN_TEST` wraps per-subtest network setup/test/cleanup. `test_tunnel()` runs all tests in a pthread to isolate namespace mount changes from `open_netns()`.

Control flow: each subtest creates base netns/veth topology, adds a specific tunnel pair with one native tunnel in `at_ns0` and one metadata/external tunnel in root, loads BPF programs that set/get tunnel metadata, attaches them to tunnel or veth TC/XDP hooks, optionally updates maps or XFRM state, then pings overlay/underlay addresses to validate encapsulation and decapsulation. Cleanup deletes tunnel devices and netns for each subtest.

State and persistence: creates namespace `at_ns0`, veth pair, many named tunnel devices, FOU ports, XFRM states/policies, IPv4/IPv6 addresses, routes, neighbor entries, and BPF links. Cleanup is repeated per subtest and uses `SYS_NOFAIL`.

Dependencies and integration: depends on many kernel tunnel drivers, XFRM, XDP attach, TC, iproute2, ping commands, generated skeleton, and privilege to modify network namespaces. Integrated as `test_tunnel`.

Risks: very environment-sensitive, especially module availability and IPv6/DAD timing. Cleanup is best-effort and may leave XFRM or tunnel state if command behavior changes. `ping6_dev1()` calls `test_ping(AF_INET, IP6_ADDR_TUNL_DEV1)`, which appears suspicious because it passes an IPv6 address with `AF_INET`.

Test signals: setup command assertions, BPF attach assertions, ping command success, XFRM BSS fields (`reqid`, `spi`, `remote_ip`, `replay_window`), and per-subtest harness assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tunnel.c -->
