## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/connect_close.c

Purpose: TCP connection churn helper for netfilter tests. It repeatedly creates nonblocking loopback TCP connections while another process repeatedly accepts, useful for racing connection setup/teardown behavior.

Important APIs and types: uses `socket(AF_INET, SOCK_STREAM)`, `fcntl(... O_NONBLOCK)`, `connect`, `bind`, `listen`, `accept`, `setsockopt(SO_REUSEADDR/SO_REUSEPORT)`, `fork`, `alarm`, and `sigaction`.

Control flow: `parse_opts()` accepts timeout and port. `main()` forks; the parent runs `accept_loop()` and the child runs `connect_loop()`. Both configure a SIGALRM timeout. The accept side repeatedly creates a listening socket on 127.0.0.1:port, accepts one connection if present, and closes. The connect side repeatedly creates a nonblocking socket, initiates connect to the same address, and closes immediately.

State and persistence: only process-local options and loopback sockets; no files or netns are created. Dependencies are local TCP stack and signal delivery. Risks include ignoring many syscall errors by design, potentially hiding environment problems, and high churn causing resource pressure. Test signal is exit status: SIGALRM maps to success via `_exit(0)`, other signals map to failure, fork failure returns 111.
