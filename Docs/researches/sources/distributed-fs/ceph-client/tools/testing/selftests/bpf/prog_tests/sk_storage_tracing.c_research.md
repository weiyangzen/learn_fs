<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_storage_tracing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_storage_tracing.c

Purpose: `sk_storage_tracing.c` tests BPF socket storage from tracing programs while TCP sockets transition through listen, shutdown, and close-related states. It also verifies that a program attempting to trace itself with sk_storage is rejected or unavailable as expected.

Important APIs/types/functions: `struct sk_stg` mirrors BPF map values containing `pid`, `last_notclose_state`, and `comm`. `check_sk_stg()` looks up per-socket storage and validates state, PID, and task command. `do_test()` creates a TCP IPv6 loopback connection, seeds `del_sk_stg_map`, performs half-closes, and validates storage cleanup and state capture. `serial_test_sk_storage_tracing()` is the serial entry point.

Control flow: the serial test records `my_pid`, attempts to open/load `test_sk_storage_trace_itself` and expects a null result, opens/loads `test_sk_storage_tracing`, attaches tracing programs, and runs `do_test()`. `do_test()` starts an IPv6 server, connects to it, inserts the active socket into a delete map, accepts the passive side, performs active and passive `shutdown(SHUT_WR)` operations with EOF reads, confirms the delete map no longer contains the active socket, and validates captured states for listener (`BPF_TCP_LISTEN`), active (`BPF_TCP_FIN_WAIT2`), and passive (`BPF_TCP_LAST_ACK`) sockets.

State and persistence: state lives in skeleton maps `sk_stg_map` and `del_sk_stg_map`, BSS `task_comm`, process PID, and transient TCP socket FDs. No persistent output is produced. The test is serial because tracing hooks and global socket-storage observations can interfere with parallel tests.

Dependencies: depends on IPv6 loopback TCP support, selftest `start_server()`/`connect_to_fd()` helpers, BPF sk_storage maps, tracing program attach support, TCP state constants, and libbpf skeletons for both accepted and rejected BPF objects.

Integration points: integrates tracing hooks with socket storage, kernel TCP state tracking, process identity reporting through BPF, and map deletion semantics keyed by socket FDs.

Risks: TCP close state timing is sensitive; different kernel state transitions could alter expected `FIN_WAIT2` or `LAST_ACK` observations. The `read()` assertions use `ASSERT_OK(err)` after EOF reads, so the intended zero-byte EOF path matters. It also depends on `TEST_COMM`/task command alignment with the BPF-side captured comm.

Test signals: the rejected `test_sk_storage_trace_itself` load, successful tracing skeleton attach, deletion of `del_sk_stg_map` entry, and exact `sk_stg_map` state/PID/comm matches for listen, active, and passive sockets are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_storage_tracing.c -->
