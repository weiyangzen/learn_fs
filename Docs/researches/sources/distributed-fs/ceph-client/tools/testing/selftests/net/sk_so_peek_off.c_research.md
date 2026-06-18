<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_so_peek_off.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_so_peek_off.c

## Purpose

`sk_so_peek_off.c` validates `SO_PEEK_OFF` receive peek offset behavior for TCP and UDP over IPv4 and IPv6.

## Important APIs, Types, and Functions

Functions include `afstr`, `sk_peek_offset_probe`, `sk_peek_offset_set`, `sk_peek_offset_get`, `sk_peek_offset_test`, `do_test`, and `main`. It uses `setsockopt/getsockopt(SO_PEEK_OFF)`, `socket`, `bind`, `getsockname`, `listen`, `connect`, `accept`, `send`, and `recv` with `MSG_PEEK` and `MSG_TRUNC`.

## Control Flow

For each protocol, `do_test` probes IPv4 and IPv6 support. If neither family supports the option, the protocol is skipped. Supported families run a socket-pair style test: set initial peek offset to 0, send `ab`, peek one byte and expect offset 1, peek beyond the last byte and expect only `b` plus offset 2, then consume/truncate the message and expect offset reset to 0.

## State and Persistence Behavior

All state is per-socket. The key persistent-in-kernel state under test is the receive socket's peek offset, which advances on peek and rewinds after consuming data. It is destroyed when the socket closes.

## Dependencies and Integration Points

The program depends on Linux `SO_PEEK_OFF` support for stream/datagram sockets and kselftest exit codes. It integrates with protocol receive queue behavior and socket option plumbing.

## Risks and Edge Cases

`SO_PEEK_OFF` may be unsupported for a family/protocol combination, so the test distinguishes skip from failure. TCP uses `accept` and a separate receive socket, while UDP receives on the bound socket; cleanup must handle both. The test sends only a two-byte message, so it covers basic offset mechanics rather than large queue behavior.

## Test Signals

Expected output reports that TCP/UDP with MSG_PEEK_OFF works correctly for supported families. Exit is `KSFT_PASS`, `KSFT_FAIL`, or `KSFT_SKIP` depending on support and validation results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_so_peek_off.c -->
