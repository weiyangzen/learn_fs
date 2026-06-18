# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_custom_syncookie.c

Purpose: `tcp_custom_syncookie.c` validates a TC ingress BPF program that handles custom TCP syncookie logic for both IPv4 and IPv6 loopback TCP connections. It ensures the program sees both SYN and final ACK traffic and that the connection remains usable for bidirectional data transfer.

Important APIs/types/functions: `test_tcp_custom_syncookie_case` describes address family, socket type, address, and subtest name. `setup_netns()` unshares a fresh net namespace, brings loopback up, and enables ECN through `/proc/sys/net/ipv4/tcp_ecn`. `setup_tc()` creates a clsact hook on `lo` and attaches `skel->progs.tcp_custom_syncookie` to ingress. `transfer_message()` sends and receives `"Hello World"`. `create_connection()` starts a server, connects a client, accepts the child socket, and verifies traffic both directions. `test_tcp_custom_syncookie()` orchestrates setup, skeleton loading, TC attachment, per-family subtests, BSS flag reset, and cleanup.

Control flow: after namespace and TC setup, the top-level test iterates over IPv4 and IPv6 test cases. For each subtest it clears `handled_syn` and `handled_ack` in skeleton BSS, creates a TCP connection to the loopback server, transfers a small message client-to-server and server-to-client, then asserts both flags became true. At the end it deletes the loopback clsact qdisc through `tc qdisc del dev lo clsact` and destroys the skeleton.

State and persistence: state is limited to a process-local network namespace, loopback qdisc/filter state, TCP ECN sysctl in that namespace, server/client sockets, and BSS flags. No files are persisted. Namespace unshare confines link and sysctl changes to the test process/thread context.

Dependencies: depends on generated `test_tcp_custom_syncookie.skel.h`, TC clsact support, libbpf TC APIs, `ip`, `tc`, loopback IPv4/IPv6 TCP, ECN sysctl availability, and `network_helpers.h` server/connect helpers.

Integration points: combines TC ingress BPF with normal TCP socket-helper connections. The BPF side must parse SYN/ACK paths correctly while preserving TCP connection semantics visible to userspace.

Risks: the test calls `unshare(CLONE_NEWNET)` in the current thread, so it must be run in a context where later tests are not harmed by namespace change. It assumes IPv6 loopback works inside the namespace. Cleanup uses `system("tc qdisc del dev lo clsact")` without checking its return. If `setup_tc()` fails after hook creation but before attach, qdisc cleanup depends on later top-level paths.

Test signals: success is demonstrated by skeleton load, clsact hook creation and TC attach, valid TCP connections for IPv4 and IPv6, exact send/receive message length and content, and BSS flags `handled_syn` and `handled_ack` both true after each connection.
