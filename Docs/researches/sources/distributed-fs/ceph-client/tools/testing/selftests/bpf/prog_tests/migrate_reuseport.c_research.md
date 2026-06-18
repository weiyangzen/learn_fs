<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/migrate_reuseport.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/migrate_reuseport.c

Purpose: comprehensive reuseport migration test for child TCP sockets across listener shutdown/relisten flows and TCP states (`ESTABLISHED`, `SYN_RECV`, `NEW_SYN_RECV`) for IPv4 and IPv6.

Important APIs and functions: `setup_fastopen()` temporarily rewrites `/proc/sys/net/ipv4/tcp_fastopen`. `drop_ack()` attaches an XDP program to loopback to hold requests in SYN states; `pass_ack()` detaches it. `start_servers()` creates five `SO_REUSEPORT` listeners and attaches `migrate_reuseport` with `SO_ATTACH_REUSEPORT_EBPF`. `start_clients()` creates 25 clients and writes a fixed message. `update_maps()` maps listener cookies to migration targets. `migrate_dance()` uses shutdown/listen/epoll to force migrations. `count_requests()` accepts all requests and compares userspace and BPF counters.

Control flow: `serial_test_migrate_reuseport()` loads the skeleton and runs eight test cases. `run_test()` resets counters, handles fastopen setup, creates servers/clients, optionally drops final ACKs, updates maps, performs migration dance, optionally waits for SYN+ACK timer or resumes ACKs, counts accepted requests, and restores/cleans all fds/sysctls.

State and persistence: substantial transient state includes listener/client fds, reuseport maps, XDP link, TCP fastopen sysctl value, BSS counters, and TCP request queues. Cleanup closes fds, detaches XDP, and restores fastopen when used.

Dependencies and integration: depends on loopback XDP attach, TCP fast open, reuseport eBPF, epoll, network helpers, and `test_migrate_reuseport.skel.h`.

Risks and test signals: all 25 client messages must arrive at the migration target and matching BPF migration counters must equal 25. Risks include timing in SYN timer tests, sysctl permissions, loopback XDP support, and subtle TCP state-machine changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/migrate_reuseport.c -->
