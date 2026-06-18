# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_inq.c

## Purpose
`mptcp_inq.c` is a focused kernel selftest helper for the `TCP_INQ` receive control-message and output-queue ioctl behavior when a TCP or MPTCP socket is used at either side of a loopback transfer. It creates a local client/server pair, enables `TCP_INQ` on the accepted socket, and verifies that `recvmsg()` returns `TCP_CM_INQ` ancillary data that matches bytes still queued for read, including EOF/FIN semantics.

## Important APIs, Types, And Functions
The helper uses `socket()`, `bind()`, `listen()`, `accept()`, `connect()`, `socketpair(AF_UNIX, SOCK_DGRAM)`, `recvmsg()`, `setsockopt(IPPROTO_TCP, TCP_INQ)`, `ioctl(TIOCOUTQ)`, `ioctl(SIOCOUTQNSD)`, and `ioctl(FIONREAD)`. It defines fallback constants for `IPPROTO_MPTCP` and `SOL_MPTCP`, and keeps global protocol selectors `pf`, `proto_tx`, and `proto_rx`. Key functions are `sock_listen_mptcp()`, `sock_connect_mptcp()`, `wait_for_ack()`, `connect_one_server()`, `get_tcp_inq()`, `process_one_client()`, `server()`, `client()`, and `main()`.

## Control Flow
`parse_opts()` accepts `-6`, `-t tcp|mptcp`, and `-r tcp|mptcp`. `main()` creates a Unix datagram socketpair, forks a server, waits for a `"conn"` readiness token, then forks a client. The server binds `127.0.0.1:15432` or `::1:15432`, accepts one connection, enables `TCP_INQ`, and runs `process_one_client()`. The client connects with the requested transmit protocol and runs `connect_one_server()`. The Unix socket coordinates phases: an initial small random transfer, a multi-megabyte transfer, and the final close path. The receiver polls `FIONREAD`, reads one byte through `recvmsg()`, checks `TCP_CM_INQ == expected_len - 1`, drains the rest, then repeatedly validates that in-queue values never exceed remaining data during the large transfer. After peer close, it checks the documented FIN behavior where `TCP_CM_INQ` reports `1` both before and after EOF.

## State, Persistence, And Dependencies
All state is transient: forked processes, loopback sockets, random buffers, and Unix-socket phase messages. There are no persistent files. The test depends on Linux TCP ancillary data support, MPTCP protocol support when selected, loopback availability, and libc/kernel headers with `linux/tcp.h` and sockios constants. `init_rng()` seeds children with `getrandom()` so payload sizes vary across runs.

## Integration Points
`mptcp_sockopt.sh` invokes this binary from a network namespace after checking for `mptcp_ioctl` support in `/proc/kallsyms`. That script runs protocol-mixed cases such as TCP sender to MPTCP receiver and MPTCP sender to TCP receiver, over IPv4 and IPv6. The helper therefore acts as the low-level assertion engine for shell-level MPTCP TCP_INQ coverage.

## Risks
The helper uses `assert()` for protocol invariants, so compiling with `NDEBUG` would remove important checks. It has fixed port `15432`, fixed 15-second alarms, and timing loops for queue drain/readiness, making it sensitive to slow or heavily loaded CI systems. `wait_for_ack()` assumes `TIOCOUTQ`/`SIOCOUTQNSD` convergence within five seconds. The test also relies on exact current `TCP_INQ` FIN semantics.

## Test Signals
Pass signals are zero exit status from both child processes and successful assertions for small-transfer, large-transfer, output-queue, and FIN cases. Failure signals include missing ancillary data, mismatched in-queue byte counts, queue values larger than expected data, short writes, connection setup failures, child signal termination, and timeout alarms.
