<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_ip_encap.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_ip_encap.c

Purpose: end-to-end LWT BPF IP/GRE and IPv6/GRE encapsulation test over a three-namespace topology, with optional VRF routing and GSO regression coverage.

Important APIs and functions: `create_ns()`, `set_top_addr()`, `set_bottom_addr()`, `configure_vrf()`, `configure_ns1/2/3()`, and `setup_network()` build the topology. `lwt_ip_encap()` installs BPF LWT routes using `test_lwt_ip_encap.bpf.o` sections `encap_gre` or `encap_gre6`. `check_ping_ok()`, `check_ping_fails()`, `remove_routes_to_gredev()`, `add_unreachable_routes_to_gredev()`, and `test_gso_fix()` validate positive and negative paths.

Control flow: each exported test selects IPv4/IPv6 encapsulation and VRF/no-VRF plus egress/ingress subtests. The helper creates three netns, configures top and bottom veth paths plus GRE/IP6GRE devices, confirms baseline ping, removes the direct destination route, installs LWT BPF replacement routes, confirms ping recovery, optionally sends a large TCP payload to test GSO, then breaks GRE reachability and expects ping failure.

State and persistence: heavy external state includes three netns, veth pairs, VRF devices, GRE devices, routes, and sockets. Cleanup deletes all namespaces via `SYS_NOFAIL` regardless of partial failure.

Dependencies and integration: depends on `ip`, ping/ping6, network helpers, root network privileges, `test_lwt_ip_encap.bpf.o`, and GRE/IP6GRE kernel support.

Risks and test signals: pings and large TCP read/write counts are the main signals. Risks are environmental flakiness, route timing, VRF source-selection limitations, and cleanup sensitivity after partial setup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_ip_encap.c -->
