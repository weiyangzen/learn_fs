# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_inq.c

## Purpose
`tcp_inq.c` is a compact example and selftest for `TCP_INQ` ancillary data. It verifies that after a partial receive, the control message reports the remaining bytes in the TCP receive queue.

## Important APIs, Types, And Functions
The file defines `setup_loopback_addr()`, `start_server()`, and `main()`. It uses `TCP_INQ`, `TCP_CM_INQ`, `recvmsg()`, `cmsghdr` parsing, pthreads, loopback sockets, and `SO_REUSEADDR`.

## Control Flow
`main()` parses `-4`, `-6`, and `-p`, starts a listening socket on loopback, launches a server thread, connects a client, enables `TCP_INQ`, and performs a `recvmsg()` for half of an 8192-byte payload. The server accepts, sends exactly 8192 bytes, sleeps for one second to avoid FIN-related overestimation, and closes. The client scans control messages for `SOL_TCP/TCP_CM_INQ` and expects the in-queue value to equal the unsent half of the buffer.

## State, Persistence, And Dependencies
State is transient sockets, one server thread, and heap buffers. No persistent files are written. The test depends on Linux TCP_INQ support, pthreads, IPv4/IPv6 loopback, and control-message delivery from `recvmsg()`.

## Integration Points
This file validates the userspace API contract for TCP receive queue reporting through cmsg data. It is independent of namespace harnesses and can run directly against loopback.

## Risks
The server buffer is allocated but not initialized, which is acceptable because content is irrelevant. The server thread loops forever, but process exit ends it after the client test. The one-second sleep is a timing workaround for FIN overestimation and could be sensitive on very slow systems.

## Test Signals
Passing signal is `PASSED` and exit code zero. Failure signals include missing control message, `MSG_CTRUNC`, a receive length different from 4096, or `inq` not equal to 4096.
