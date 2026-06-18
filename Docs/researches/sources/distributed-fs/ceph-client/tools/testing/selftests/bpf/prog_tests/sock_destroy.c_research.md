<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_destroy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_destroy.c

Purpose: `sock_destroy.c` tests BPF socket destruction from iterator programs for TCP and UDP client/server sockets. It verifies that iterator-triggered destruction produces expected application-visible errors and that invalid destruction programs fail via `RUN_TESTS(sock_destroy_prog_fail)`.

Important APIs/types/functions: `start_iter_sockets()` attaches a BPF iterator program, creates an iterator FD, and drains it to execute socket-destroy logic. `test_tcp_client()`, `test_tcp_server()`, `test_udp_client()`, and `test_udp_server()` create sockets and invoke specific iterator programs from `sock_destroy_prog.skel.h`. `test_sock_destroy()` manages cgroup/netns setup and subtest dispatch.

Control flow: the top-level test loads the skeleton, joins `/sock_destroy`, attaches a cgroup `sock_connect` program, creates and enters netns `sock_destroy_netns`, then runs TCP client, TCP server, UDP client, and UDP server subtests. TCP client/server tests establish connections, send once, run the destroy iterator, then assert the next send fails with `ECONNABORTED` for destroyed client or `ECONNRESET` for destroyed server. UDP server starts a reuseport group, destroys all server sockets by port, then asserts reads fail with `ECONNABORTED`.

State and persistence: state includes the named netns, cgroup link, BPF iterator links/FDs, listener/client/accepted sockets, skeleton BSS `serv_port`, and reuseport FD arrays. Cleanup closes netns and deletes it with `ip netns del`.

Dependencies: depends on BPF iterators over sockets, `bpf_sock_destroy()` behavior in the BPF object, cgroup connect hook support, IPv6 loopback networking, reuseport UDP helpers, and network namespace tooling.

Integration points: integrates cgroup hooks that mark or filter sockets with iterator programs that walk and destroy sockets, then validates visible userspace socket error semantics.

Risks: errno expectations depend on TCP/UDP state and kernel destroy semantics. Iterator drain relies on reading until EOF; partial iterator failures could leave sockets alive. Netns cleanup uses `SYS_NOFAIL`, so leaked state is unlikely but still possible if process dies abruptly.

Test signals: failed send/read after iterator destruction with expected errno, successful destruction of all reuseport UDP server sockets, and expected failures from `sock_destroy_prog_fail` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_destroy.c -->
