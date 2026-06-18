<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_helpers.h -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_helpers.h

Purpose: shared helper header for LWT program tests, providing namespace setup macros, ICMP packet filtering, and packet wait utilities.

Important APIs and functions: `log_err()` wraps error printing with function/line context. `RUN_TEST(name)` creates/deletes the configured `NETNS`, switches into it with `open_netns()`, runs a named helper, and closes the namespace. `netns_create()` and `netns_delete()` shell out to `ip netns`. `__expect_icmp_ipv4()` validates ICMP payload length/type. `wait_for_packet()` loops on a fd until a filter accepts a packet or timeout expires.

Control flow: LWT tests include this header after defining `NETNS`, then invoke `RUN_TEST()` from a worker thread. Packet capture helpers are called after ping or socket send operations.

State and persistence: namespace state is external and named by `NETNS`; helpers delete/recreate it per subtest. `wait_for_packet()` consumes packets from fds without persistent state.

Dependencies and integration: depends on `test_progs.h`, Linux ICMP headers, `network_helpers.h` namespace functions, and the `ip` tool.

Risks and test signals: risks are macro side effects, hard-coded namespace names, and timeout sensitivity. Test signal is binary: namespace operations succeed and expected ICMP packets are observed before timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_helpers.h -->
