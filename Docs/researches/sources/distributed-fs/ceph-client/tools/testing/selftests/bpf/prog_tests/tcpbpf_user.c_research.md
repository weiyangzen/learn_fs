# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcpbpf_user.c

Purpose: `tcpbpf_user.c` is a userspace harness for the TCP BPF sockops test program. It establishes an IPv6 loopback TCP connection in a test cgroup, transfers data in both directions, performs ordered shutdown, and verifies global BPF counters for sockops events, bytes, segments, callback return tests, listen/close counts, and TCP socket options.

Important APIs/types/functions: `verify_result()` checks `struct tcpbpf_globals` from skeleton BSS against expected event and counter values. `run_test()` creates a server with `start_server()`, connects a client with `connect_to_fd()`, accepts the connection, sends 1000 bytes client-to-server and 500 bytes server-to-client, then shuts down accepted socket first to force deterministic close/accounting order. `test_tcpbpf_user()` loads `test_tcpbpf_kern.skel.h`, joins cgroup `/tcpbpf-user-test`, attaches `bpf_testcb`, and runs the traffic scenario.

Control flow: after BPF attach, the test sends payloads, receives them fully, performs FIN sequencing, closes sockets, and only calls `verify_result()` if the socket flow completed without error. Cleanup closes the cgroup fd and destroys the skeleton.

State and persistence: runtime state is the cgroup link, skeleton BSS global counters, one TCP listener, one client, one accepted socket, and data buffers. There is no persistent storage.

Dependencies: depends on generated `test_tcpbpf_kern.skel.h`, shared `test_tcpbpf.h`, cgroup sockops support, IPv6 loopback TCP, BPF helpers that read/write TCP sockopts, and `network_helpers.h`.

Integration points: this is a classic TCP BPF selftest that validates kernel sockops callbacks through userspace-observable BSS fields. It overlaps conceptually with `tcp_hdr_options.c` but focuses on general sockops events and counters.

Risks: exact byte and close-event counts depend on the BPF program and on controlled shutdown order; the code explicitly shuts down the accepted side first to reduce nondeterminism. It assumes IPv6 loopback is available. If socket creation fails early, result verification is skipped, so the preceding assertions must carry diagnostics.

Test signals: expected BSS values include a precise event bitmask, 501 bytes received, 1002 bytes acked, one data segment in/out, bad callback return value `0x80`, good callback return 0, one listen event, three close events, `tcp_save_syn` 0, `tcp_saved_syn` 1, and client/server window clamp values of 9216.
