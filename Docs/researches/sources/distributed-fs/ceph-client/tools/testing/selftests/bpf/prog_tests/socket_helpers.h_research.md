<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/socket_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/socket_helpers.h

Purpose: `socket_helpers.h` provides reusable socket utilities for BPF socket selftests. It centralizes assertion-reporting wrappers, loopback address initialization, timed accept/recv/connect helpers, socket pair creation across address families, automatic FD cleanup, and socket-kind stringification.

Important APIs/types/functions: failure macros `_FAIL`, `FAIL`, `FAIL_ERRNO`, and `FAIL_LIBBPF` report via `error_at_line()` and `CHECK_FAIL()`. `xaccept_nonblock`, `xbind`, `xclose`, `xconnect`, `xgetsockname`, `xgetsockopt`, `xlisten`, `xsetsockopt`, `xsend`, `xrecv_nonblock`, and `xsocket` wrap syscalls with assertions. `init_addr_loopback*()` build AF_INET, AF_INET6, AF_UNIX, and AF_VSOCK loopback addresses. `socket_loopback_reuseport()` creates a bound/listening or datagram socket and optionally attaches a reuseport BPF program. `create_pair()` and `create_socket_pairs()` build connected endpoint pairs. `socket_kind_to_str()` returns compact family/type labels.

Control flow: helpers generally initialize a sockaddr, create sockets, bind/connect/listen as needed, and return either FDs or negative errors while marking selftest failures. `create_pair()` creates a server and client, handles nonblocking/in-progress connects through `poll_connect()`, then for datagram sockets connects the server back to the client, while stream/seqpacket sockets accept a peer. Cleanup uses `take_fd()` and `__close_fd` to transfer ownership safely.

State and persistence: the header itself persists no state. Callers receive live socket FDs and must close them or use cleanup attributes. Helper timeouts use `IO_TIMEOUT_SEC = 30`; error string buffers use `MAX_STRERR_LEN = 256`.

Dependencies: depends on POSIX sockets, `select()`, Unix sockets, Linux vsock definitions, libbpf error formatting, and the BPF selftest assertion framework. It includes compatibility definitions for `VMADDR_CID_LOCAL`, `auto`, and cleanup-style helpers.

Integration points: used by sockmap and kTLS tests to reduce repeated socket setup and error handling. It bridges standard socket APIs with selftest reporting conventions.

Risks: wrappers mark failures but still return syscall values; callers must check them. `poll_connect()` uses `select()` and `SO_ERROR`, which is adequate for selftests but not a general event loop. AF_UNIX loopback initialization only sets `sa_family_t` length, so callers needing named paths must override it. VSOCK support depends on local kernel/transport support.

Test signals: indirect signals come from users such as sockmap tests. A helper works when connected pairs can send/receive data, timeouts catch stalled I/O, and wrapper failures include useful syscall context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/socket_helpers.h -->
