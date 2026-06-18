# sources/distributed-fs/ceph-client/net/ipv4/tcp_offload.c

## Purpose

`tcp_offload.c` provides IPv4 TCP segmentation and receive offload glue. It registers TCPv4 GSO/GRO callbacks with the IPv4 protocol offload table and implements common TCP GSO/GRO helpers that split large TCP SKBs on transmit and aggregate compatible TCP packets on receive.

## Important APIs, Types, and Functions

Transmit segmentation paths include `tcp4_gso_segment()`, `tcp_gso_segment()`, `__tcp4_gso_segment_list()`, `__tcpv4_gso_segment_list_csum()`, `__tcpv4_gso_segment_csum()`, and `tcp_gso_tstamp()`. Receive aggregation paths include `tcp_gro_lookup()`, `tcp_gro_receive()`, `tcp_gro_complete()`, `tcp4_check_fraglist_gro()`, `tcp4_gro_receive()`, and `tcp4_gro_complete()`. `tcpv4_offload_init()` installs these callbacks into `net_hotdata.tcpv4_offload` and calls `inet_add_offload()`.

## Control Flow

`tcp4_gso_segment()` first verifies the SKB is TCPv4 GSO and has a pullable TCP header. For fraglist GSO, it can segment via list processing if the frame is already a valid single-MSS fraglist and not dodgy; otherwise it forces checksum recomputation. If checksum state is not partial, it builds the TCPv4 pseudo-header checksum before delegating to `tcp_gso_segment()`.

`tcp_gso_segment()` validates header length and checksum start, pulls the TCP header, checks MSS, and either lets hardware handle robust GSO or software-segments with `skb_segment()`. It updates sequence numbers, FIN/PSH/CWR flags, checksums, transmit timestamp ownership, `ooo_okay`, and TCP Small Queue destructor/accounting so completion accounting follows the final segment.

`tcp_gro_receive()` searches for an existing same-flow packet by TCP ports, compares flags, ACK sequence, options, network flush criteria, MSS, sequence continuity, and decrypted state, then aggregates through SKB GRO helpers when safe. It forces flush on small final segments and on urgent, push, reset, SYN, or FIN flags. `tcp_gro_complete()` marks the aggregate as checksum-partial GSO and carries AccECN CWR state in the GSO type.

`tcp4_check_fraglist_gro()` enables fraglist GRO only when the device supports it and no established socket is found for the flow. `tcp4_gro_complete()` finalizes either fraglist GSO metadata or normal TCPv4 pseudo-header checksum and fixed-IP-ID flags.

## State and Persistence

The file has no long-lived per-flow state. It mutates SKB metadata, shared-info GSO/GRO fields, checksums, destructor/sk ownership, timestamp flags, and NAPI GRO control blocks. Registration state persists in the IPv4 offload table after `tcpv4_offload_init()`.

## Dependencies and Integration Points

Dependencies include SKB segmentation/GRO core, checksum helpers, NAPI GRO metadata, IPv4 pseudo-header checksum, protocol offload registration, established socket lookup for fraglist GRO, netdevice feature flags, TCP Small Queues destructor `tcp_wfree`, and GSO type flags including TCPv4, fraglist, fixed IP ID, and AccECN.

## Risks

Offload code is high-risk for checksum, sequence, and accounting bugs. Incorrect segmentation can corrupt TCP streams, misplace FIN/PSH/CWR flags, lose transmit timestamps, or break TCP Small Queue memory accounting. GRO aggregation must reject flows with differing options, ACKs, flags, encryption state, MSS, or sequence continuity. Fraglist GRO depends on socket lookup and device support; wrong selection can hand unsupported packet shapes to the stack or hardware.

## Test Signals

Validate software GSO and hardware GSO fallback, fraglist GSO checksum rewriting after address/port changes, GRO aggregation and forced flush cases, AccECN CWR propagation, transmit timestamp selection across segments, TSQ destructor/accounting under large writes, checksum correctness with CHECKSUM_PARTIAL and CHECKSUM_NONE inputs, GRO fraglist behavior with and without established sockets, and packetdrill or selftests for segmented FIN/PSH/SYN/RST boundaries.
