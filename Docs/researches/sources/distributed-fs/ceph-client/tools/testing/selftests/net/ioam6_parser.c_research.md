# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ioam6_parser.c

Purpose: Packet-level validator for `ioam6.sh`. It listens on a packet socket, filters for the expected IPv6 Hop-by-Hop packet, and validates IOAM preallocated trace header and trace data for one named test case.

Important APIs and types: Uses `AF_PACKET`/`SOCK_DGRAM`, `SO_BINDTODEVICE`, `SO_RCVTIMEO`, Linux `struct ioam6_hdr`, `struct ioam6_trace_hdr`, `struct ipv6hdr`, `struct ipv6_hopopt_hdr`, endian helpers, and a private `struct ioam_config` mirroring Alpha and Beta shell configuration.

Control flow: `main` parses interface, test name, source, destination, trace type, trace size, namespace ID, and mode. It computes expected Hop-by-Hop length, receives packets until one matches the IPv6 source/destination and Hop-by-Hop header, validates next-header, padding, IOAM option type and size, optional trailing padding, then dispatches `check_ioam_trace`. `str2id` maps shell test names to enums. `check_header` encodes expected overflow, node length, and remaining length for every case. `check_data` walks the trace fields in bit order and validates IDs, timestamps/non-default fields, namespace data, wide data, and schema data padding.

State and persistence: No persistent state. Static node configs are the expected values; all packet data is stack-local.

Dependencies and integration: Tightly coupled to `ioam6.sh`, Linux IOAM UAPI definitions, and exact IOAM option wire format.

Risks: The explicit name-to-enum table and expected-header switch are large and must be updated with any shell test change. Padding checks and trace pointer arithmetic are sensitive to UAPI layout changes.

Test signals: Exit status zero means the observed packet matches the selected IOAM case exactly; nonzero means missing packet, malformed headers, or wrong trace data.
