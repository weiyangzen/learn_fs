<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_rcv_listener.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_rcv_listener.c

## Purpose

`so_rcv_listener.c` validates receive-side ancillary reporting for socket metadata set on sent packets: `SO_RCVMARK` receives `SO_MARK`, and `SO_RCVPRIORITY` receives `SO_PRIORITY`.

## Important APIs, Types, and Functions

`struct options` stores the selected value, sender option name, receiver cmsg type, host, and service. `parse_args` selects `-M` for mark or `-P` for priority. `main` creates an IPv4 or IPv6 UDP socket, enables the receive option, binds, receives one datagram with `recvmsg`, and scans control messages.

## Control Flow

The program is a listener. It chooses AF_INET6 when the host string contains `:`, otherwise AF_INET. After binding, it blocks in `recvmsg` and looks for a `SOL_SOCKET` cmsg whose type is the corresponding sender option (`SO_MARK` or `SO_PRIORITY`) and whose payload equals the requested value.

## State and Persistence Behavior

State is per-socket. The receive option configures ancillary delivery for one socket and disappears on close. No sender is created by this program; it must be paired with an external transmitter.

## Dependencies and Integration Points

It depends on kernel support for `SO_RCVMARK` and `SO_RCVPRIORITY` and on a test harness that sends UDP packets with `SO_MARK` or `SO_PRIORITY` set. It integrates with cmsg delivery in UDP receive paths for IPv4 and IPv6.

## Risks and Edge Cases

The option names are easy to confuse: the received cmsg type is checked against the sender-side option identifier stored in `opt.name`, while the receiver is configured with `opt.rcvname`. The program blocks until a packet arrives and has no timeout. It accepts numeric services only despite usage mentioning service names.

## Test Signals

Success prints `Received value: N` and exits zero. Failures include bind/setsockopt/recv errors, missing cmsg, or mismatched received value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_rcv_listener.c -->
