
# sources/distributed-fs/ceph-client/include/uapi/linux/if_packet.h

## Purpose

`if_packet.h` defines the AF_PACKET socket ABI for raw link-layer access, including socket address layouts, packet type IDs, ring-buffer versions, mmap ring headers, status bits, fanout, multicast membership, and packet statistics. The complete 320-line file was read.

## Important APIs, Types, and Functions

Key structs and unions are `sockaddr_pkt`, `sockaddr_ll`, `tpacket_stats`, `tpacket_stats_v3`, `tpacket_rollover_stats`, `tpacket_stats_u`, `tpacket_auxdata`, `tpacket_hdr`, `tpacket2_hdr`, `tpacket_hdr_variant1`, `tpacket3_hdr`, `tpacket_bd_ts`, `tpacket_hdr_v1`, `tpacket_block_desc`, `tpacket_req`, `tpacket_req3`, `tpacket_req_u`, `packet_mreq`, and `fanout_args`. Macros define `PACKET_*` socket options, fanout modes/flags, `TP_STATUS_*`, `TPACKET_*` alignment/header sizes, membership types, and `TPACKET_V1..V3`.

## Control Flow

No executable flow is defined. Packet socket code uses these layouts when user space binds an AF_PACKET socket, configures options with `setsockopt`, maps RX/TX rings, waits for status-bit ownership transfer between kernel and user space, and optionally fans out traffic across sockets.

## State and Persistence Behavior

Runtime state is in packet sockets and mmap rings. `TP_STATUS_KERNEL`/`TP_STATUS_USER` style bits coordinate per-frame/block ownership, while membership and fanout options persist for the life of the socket or until changed.

## Dependencies and Integration Points

The header includes `asm/byteorder.h` and `linux/types.h`. It integrates with AF_PACKET sockets, network drivers through skb delivery, BPF fanout selectors, VLAN auxiliary data, timestamping, and tools such as tcpdump/libpcap.

## Risks and Edge Cases

Ring layouts are ABI-sensitive and alignment-dependent. Risks include incorrect TPACKET version handling, stale status-bit ownership causing packet loss or corruption, endian-sensitive `fanout_args`, VLAN metadata validity bits, timestamp source ambiguity, and user buffers sized incorrectly for variable block/frame layout.

## Test Signals

AF_PACKET selftests should exercise V1/V2/V3 RX rings, TX rings, rollover stats, auxdata VLAN fields, fanout modes including BPF, membership changes, timestamp flags, and 32/64-bit layout compatibility.
