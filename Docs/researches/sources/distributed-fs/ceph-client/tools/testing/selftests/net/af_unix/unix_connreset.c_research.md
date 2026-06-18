# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/unix_connreset.c

Purpose: Documents AF_UNIX close/reset behavior for stream, datagram, and seqpacket sockets.

Important APIs/types/functions: Uses pathname AF_UNIX sockets, nonblocking clients, `listen()/accept()` for stream/seqpacket, `recv()`, and expected `EOF`, `ECONNRESET`, or `EAGAIN`.

Control flow: Fixture binds `/tmp/af_unix_connreset.sock`, listens for connection-oriented types, creates a nonblocking client, and connects. `eof` closes the peer normally and checks stream/seqpacket return EOF while datagram returns `EAGAIN`. `reset_unread_behavior` leaves unread data and checks stream/seqpacket `ECONNRESET` while datagram again sees `EAGAIN`. `reset_closed_embryo` closes the unaccepted server socket and expects reset for stream/seqpacket, marking datagram as XFAIL.

State and persistence behavior: Uses server, client, and accepted child descriptors. The socket pathname is unlinked before setup and in teardown.

Dependencies and integration points: Requires AF_UNIX connection semantics in the kernel and kselftest harness.

Risks: Uses a fixed `/tmp` socket path, so concurrent runs can interfere. Nonblocking datagram expectations rely on no queued data after server close.

Test signals: Passing tests confirm Linux's intended reset/EOF distinctions across AF_UNIX socket types.
