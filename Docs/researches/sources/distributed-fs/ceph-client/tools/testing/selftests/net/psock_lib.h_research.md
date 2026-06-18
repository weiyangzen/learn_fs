<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_lib.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_lib.h

## Purpose

`psock_lib.h` is a small shared helper library for packet-socket selftests. It provides common UDP traffic generation and a packet BPF filter that selects the synthetic UDP payloads used by fanout and TPACKET tests.

## Important APIs, Types, and Functions

The key constants are `DATA_LEN=100`, `DATA_CHAR='a'`, `DATA_CHAR_1='b'`, and `PORT_BASE=8000`. `pair_udp_setfilter` attaches a classic `SO_ATTACH_FILTER` program that accepts IPv4 UDP packets with minimum length 100 and payload byte at offset 80 equal to `a` or `b`. `pair_udp_open` creates two bound IPv4 UDP sockets on loopback and connects the sender to the receiver. `pair_udp_send_char`, `pair_udp_send`, and `pair_udp_close` send, receive, validate, and close the UDP pair.

## Control Flow

Callers attach the filter to packet sockets, open UDP pairs on selected ports, send a fixed number of payloads, and rely on the helper to synchronously read back from the receiving UDP socket so the traffic is fully delivered while packet sockets observe it. Any socket, bind, connect, send, receive, or data mismatch terminates the process.

## State and Persistence Behavior

State is limited to caller-owned socket FDs and attached classic BPF filters. The header uses `static __maybe_unused` helpers so each including C file gets private helper definitions and no external symbols.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include IPv4 loopback, UDP sockets, classic socket filters, and kselftest's `ARRAY_SIZE`/`__maybe_unused` definitions. Integration is with packet-socket tests that need deterministic payloads and packet filtering. Risks are hard-coded packet offsets that assume Ethernet/IP/UDP layout on loopback packet sockets, synchronous send/recv lacking EINTR/EAGAIN retry, and port conflicts around `PORT_BASE`. Signals are no helper aborts and payload `memcmp` success for every generated datagram.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_lib.h -->
