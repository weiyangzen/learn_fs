<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/socket_cookie.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/socket_cookie.c

Purpose: `socket_cookie.c` tests socket-cookie collection and update across cgroup and tracing programs. It validates that a TCP client socket cookie maps to a value derived from the client's local port.

Important APIs/types/functions: `struct socket_cookie` mirrors map values with `cookie_key` and `cookie_value`. `test_socket_cookie()` opens `socket_cookie_prog.skel.h`, joins `/socket_cookie`, attaches cgroup and tracing programs, creates a TCP IPv6 loopback connection, looks up `socket_cookies` by client FD, obtains the client's local port with `getsockname()`, and computes the expected value.

Control flow: load skeleton, join cgroup, attach `set_cookie` and `update_cookie_sockops` to the cgroup, attach tracing updater, start server, connect client, look up map value, read local port, assert `cookie_value == (ntohs(port) << 8) | 0xFF`, then close sockets/cgroup and destroy skeleton.

State and persistence: state includes cgroup links, tracing link, server/client sockets, skeleton map `socket_cookies`, and one looked-up cookie value. No durable output is created.

Dependencies: depends on socket cookie helpers, cgroup attach support, sock_ops/tracing programs in the skeleton, IPv6 loopback TCP, and map lookup by socket FD.

Integration points: combines cgroup socket hooks, sock_ops/tracing updates, map entries keyed by socket reference, and userspace validation from socket metadata.

Risks: the expected value encodes BPF-side policy; if the BPF object changes, userspace must change with it. Map lookup by socket FD requires the BPF map type/key semantics to match the kernel's socket-storage or socket-cookie behavior.

Test signals: successful attachment of all three programs, successful TCP connection, successful map lookup, and exact computed cookie value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/socket_cookie.c -->
