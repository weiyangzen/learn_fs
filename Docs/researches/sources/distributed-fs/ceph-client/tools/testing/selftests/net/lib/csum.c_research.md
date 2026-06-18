# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/csum.c

## Purpose
`csum.c` is a standalone checksum-offload exerciser for IPv4/IPv6 TCP and UDP receive and transmit paths. It can craft good, bad, zero-disabled, zero-sum, raw IP, UDP-socket, or PF_PACKET/VNET_HDR packets to verify NIC and kernel checksum behavior.

## Important APIs and Functions
Configuration is stored in `cfg_*` globals populated by `parse_args`. Packet construction flows through `build_packet_ipv4`, `build_packet_ipv6`, `build_packet_udp`, `build_packet_tcp`, `build_packet_udp_encap`, and `build_packet`, using `checksum_nofold`, `checksum_fold`, and `checksum` for pseudo-header and transport checksums. Transmit paths use `open_inet`, `open_packet`, `send_inet`, and `send_packet`. Receive paths use `recv_prepare_udp`, `recv_prepare_packet`, `recv_prepare_packet_filter`, `recv_packet`, `recv_udp`, and protocol-specific validators such as `recv_verify_packet_ipv4`, `recv_verify_packet_ipv6`, `recv_verify_packet_udp`, and `recv_verify_packet_tcp`.

## Control Flow and State
`main` parses options, opens receive sockets before transmitting, optionally transmits `cfg_num_pkt` packets, then polls for packets until `cfg_timeout_ms` expires. The sender either writes payload via UDP socket, raw socket, or PF_PACKET with `PACKET_VNET_HDR` to request `CHECKSUM_PARTIAL`. The receiver consumes both UDP socket delivery and PF_PACKET auxdata, counting matching packets and validating checksums. Runtime state lives entirely in process globals and sockets; no persistent files are written.

## Dependencies and Integration
The program depends on Linux raw sockets, PF_PACKET, `PACKET_AUXDATA`, optional `PACKET_VNET_HDR`, BPF socket filters, UAPI headers, and kselftest helpers. It is built by `lib/Makefile` and intended for hardware/NIC checksum testing, not a default single-host kselftest.

## Risks and Test Signals
It requires privileges and accurate source/destination addresses and MACs for PF_PACKET mode. Randomization can change payload length per packet and may interact with GRO, so GSO packets with `TP_STATUS_CSUMNOTREADY` are skipped for checksum validation. Important pass signals are stderr `OK`, observed PF_PACKET count at least `cfg_num_pkt`, UDP delivery for good UDP checksums, no UDP delivery for bad checksums, and `TP_STATUS_CSUM_VALID` never being reported for intentionally bad checksums.
