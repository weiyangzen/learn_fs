<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/sctp_collision.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/sctp_collision.c

## Purpose
This helper program creates an SCTP one-to-one collision scenario between a server and client using `SOCK_SEQPACKET`. It coordinates delayed connects and message exchange to reproduce SCTP conntrack or association collision behavior used by surrounding netfilter tests.

## Important APIs, Types, And Functions
The single `main()` uses `socket(AF_INET, SOCK_SEQPACKET, IPPROTO_SCTP)`, `bind()`, `listen()`, `setsockopt(SO_RCVTIMEO)`, `connect()`, `sendto()`, `recvfrom()`, `sleep()`, `usleep()`, `inet_addr()`, `htons()`, and `close()`.

## Control Flow
The program expects `server|client LOCAL_IP LOCAL_PORT REMOTE_IP REMOTE_PORT`. Both roles bind and listen on their local address and configure a receive timeout. The server sleeps to allow the client INIT, connects to the peer, receives a message, and echoes it. The client waits briefly for listening, connects, sleeps to delay data until after the server's INIT_ACK timing, sends `hello`, and waits for the echoed response.

## State, Persistence, And Dependencies
State is one SCTP socket and stack SCTP address structures. There is no filesystem persistence. It depends on kernel SCTP support and the test harness to create addresses, routes, and concurrent server/client processes.

## Integration Points
The helper is intended for netfilter/SCTP collision tests that need deterministic bidirectional SCTP setup and controlled timing. Its output strings are simple harness-readable milestones.

## Risks
Timing uses fixed sleeps, which can be fragile on slow or heavily loaded systems. Error handling prints generic messages without `errno`, making diagnostics limited. `inet_addr()` supports only IPv4 dotted decimal and cannot report all parse errors distinctly.

## Test Signals
Successful server output is `Server: sent!` and successful client output is `Client: rcvd!`, with return code 0. Any socket, bind, listen, connect, send, receive, or timeout failure returns nonzero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/sctp_collision.c -->
