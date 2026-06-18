# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/scm_inq.c

Purpose: Tests `SO_INQ`/`SCM_INQ` ancillary reporting for AF_UNIX sockets and confirms it is stream-only.

Important APIs/types/functions: Uses `socketpair(AF_UNIX, type|SOCK_NONBLOCK)`, `setsockopt(SOL_SOCKET, SO_INQ)`, `recvmsg()` control messages, `SCM_INQ`, and `ioctl(SIOCINQ)`.

Control flow: The fixture runs variants for stream, datagram, and seqpacket socketpairs. The test enables `SO_INQ`; non-stream variants expect `ENOPROTOOPT`. For streams, it sends 100 chunks of 256 bytes, receives each with `recvmsg()`, extracts the `SCM_INQ` integer, and verifies it equals `SIOCINQ` after that receive.

State and persistence behavior: Only two socket descriptors. Queue depth is kernel socket receive buffer state.

Dependencies and integration points: Requires kernel support for AF_UNIX stream `SO_INQ` ancillary data and the kselftest harness.

Risks: The expected value depends on when `SCM_INQ` is sampled relative to the consumed message. Nonblocking sends assume the socket buffer can accept the configured total data.

Test signals: Passing stream test proves `SCM_INQ` is emitted and matches `SIOCINQ`; passing datagram/seqpacket variants prove unsupported types reject `SO_INQ`.
