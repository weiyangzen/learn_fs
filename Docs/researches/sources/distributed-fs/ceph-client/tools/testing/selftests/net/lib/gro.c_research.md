# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/gro.c

## Purpose
`gro.c` is a raw-packet GRO conformance helper. It sends or receives crafted Ethernet/IP/TCP packets and validates whether GRO coalesces or flushes packets for data, ACK, TCP flag, TCP option, checksum, IPv4/IPv6 header, extension-header, fragmentation, size-limit, and capacity cases.

## Important APIs and Functions
`parse_args` selects IPv4, IPv6, IP-in-IP, IPv6-in-IPv6, sender/receiver mode, test name, interface, addresses, MACs, flow count, and verbosity. Packet generation is centered on `create_packet`, `fill_datalinklayer`, `fill_networklayer`, `fill_transportlayer`, `tcp_checksum`, and `write_packet`. Specialized senders include `send_data_pkts`, `send_flags`, `send_changed_checksum`, `send_changed_seq`, `send_changed_ts`, `send_diff_opt`, `send_ip_options`, `send_fragment4`, `send_fragment6`, `send_flush_id_case`, `send_ipv6_exthdr`, `send_large`, `send_ack`, and `send_capacity`. Receiver validation uses `setup_sock_filter`, `bind_packetsocket`, `check_recv_pkts`, and `check_capacity_pkts`.

## Control Flow and State
After argument parsing, `main` computes `tcp_offset`, `total_hdr_len`, and Ethernet protocol based on encapsulation mode. Sender mode uses a PF_PACKET raw socket, optional `SO_TXTIME`, and a large branch on `testname` to emit the exact packet sequence followed by a FIN marker. Receiver mode creates a filtered PF_PACKET socket, calls `ksft_ready`, then validates received packet geometry against expected coalesced payload sizes for the same `testname`. State is process-local globals; there is no disk persistence.

## Dependencies and Integration
The helper depends on Linux PF_PACKET raw sockets, classic BPF socket filters, `SO_TXTIME`, Ethernet/IP/TCP headers, and `ksft_ready` from `ksft.h` for parent/child synchronization. It is built by `lib/Makefile` and used by GRO-focused selftests that coordinate separate sender and receiver instances.

## Risks and Test Signals
Timing is intentionally acknowledged as flaky because GRO windows are time-sensitive. Tests require root, correct MAC/interface parameters, and traffic isolation. Header offsets vary with IPv4 options and IPv6 extension headers; mistakes in offset calculation can cause false failures. Pass signals are `Test succeeded` or `Gro::<test> test passed`; capacity tests additionally print `STATS: received=... wire=... coalesced=...` and fail if expected coalescing, packet ordering, or payload geometry differs.
