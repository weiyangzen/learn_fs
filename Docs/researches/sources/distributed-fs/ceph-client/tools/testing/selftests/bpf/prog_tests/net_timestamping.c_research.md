<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/net_timestamping.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/net_timestamping.c

Purpose: validates socket timestamping visibility and BPF-provided timestamp fields for TCP traffic under cgroup programs.

Important APIs and functions: `timespec_to_ns64()`, `validate_key()`, and `validate_timestamp()` check timestamp ordering and tolerance. `test_socket_timestamp()` validates individual `scm_timestamping` entries. `test_recv_errmsg_cmsg()` parses error-queue control messages. `socket_recv_errmsg()` reads error queue data. `test_socket_timestamping()` configures socket timestamping. `test_tcp()` creates IPv4/IPv6 TCP traffic with optional userspace socket timestamping. `test_net_timestamping()` loads/attaches `net_timestamping` and runs subtests.

Control flow: attach cgroup programs, create TCP client/server pairs for IPv4 and IPv6, send data, receive error-queue timestamp messages, validate timestamp keys/types/order and BPF BSS fields, then cleanup sockets and cgroup.

State and persistence: state includes cgroup attachment, sockets, error queue messages, global `usr_ts`, BSS timestamp fields, and flags such as `SK_TS_SCHED`, `SK_TS_TXSW`, `SK_TS_ACK`.

Dependencies and integration: depends on `linux/net_tstamp.h`, error-queue control message format, network helpers, cgroup support, and `net_timestamping.skel.h`.

Risks and test signals: valid keys, monotonic timestamps within tolerance, and expected timestamp types are signals. Risks are timestamp timing variability, kernel timestamping support, and error queue delivery differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/net_timestamping.c -->
