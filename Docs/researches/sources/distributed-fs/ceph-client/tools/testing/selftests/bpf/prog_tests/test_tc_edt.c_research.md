<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tc_edt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tc_edt.c

Purpose: end-to-end test for BPF-based Earliest Departure Time flow shaping by measuring TCP transfer rate through a TC program.

Important APIs/types/functions: netns helpers, `tc_prog_attach()`, `test_tc_edt` skeleton, `start_server()`, `connect_to_fd()`, `send_recv_data()`, `get_time_ns()`, and BSS `target_rate`. Constants set 5 Mbps target, 1 MB transfer, and 2 percent acceptable error.

Control flow: load skeleton, create client/server namespaces with veth pair, configure IPv4 addresses, add `fq` qdisc on server veth, attach TC program to server veth, write target rate into BSS, start a server in server namespace, connect from client namespace, transfer bytes, compute Mbps from elapsed time, and assert error threshold.

State and persistence: creates two named netns, veth pair, qdisc, TC attachment, sockets, and BSS rate. Cleanup removes namespaces after run; early setup failures remove partial namespaces.

Dependencies and integration: requires iproute2, fq qdisc, TC attach helpers, network privileges, and timing stability. Integrated as `test_tc_edt`.

Risks: performance/timing tests are noisy under CPU contention or virtualized networking. Cleanup is skipped if setup fails after skeleton load because `test_tc_edt()` returns early without destroying the skeleton in that path. Rate computation assumes byte/usec conversion matches `TARGET_RATE_MBPS`.

Test signals: namespace/network setup assertions, server/client fd assertions, transfer success, and `ASSERT_LE(rate_error, RATE_ERROR_PERCENT)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tc_edt.c -->
