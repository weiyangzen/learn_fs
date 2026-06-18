# sources/distributed-fs/ceph-client/include/net/udp.h

## Purpose

`udp.h` is the shared UDP core header for IPv4 and IPv6. It defines UDP socket hash tables, checksum helpers, socket initialization and receive queues, lookup/send/receive prototypes, GSO/GRO segmentation helpers, SNMP counters, proc iteration, encapsulation static keys, and BPF integration hooks.

## Important APIs, types, and functions

Key types are `struct udp_skb_cb`, `struct udp_hslot`, `struct udp_hslot_main`, `struct udp_table`, `struct udp_dev_scratch`, `struct udp_seq_afinfo`, and `struct udp_iter_state`. Important helpers include `udp_hashslot()`, `udp_hashslot2()`, hash4 helpers, `udp_lib_checksum_complete()`, `udp_csum_outgoing()`, `udp_csum()`, `udp_v4_check()`, `udp_csum_pull_header()`, `udp_lib_init_sock()`, `udp_drops_inc()`, `udp_flow_src_port()`, `udp_rqueue_get()`, `udp_sk_bound_dev_eq()`, `skb_recv_udp()`, `udp_skb_len()`, `udp_skb_csum_unnecessary()`, `copy_linear_skb()`, `udp_rcv_segment()`, and `udp_post_segment_fix_csum()`.

## Control flow

Socket creation calls `udp_lib_init_sock()` to initialize drop counters, reader queues, tunnel list nodes, forwarding thresholds, custom sockopt behavior, and per-NUMA producer queues. Bind/connect operations insert sockets into primary, secondary, and optionally connected-socket hash4 tables. Send paths use checksum helpers and push/flush pending frames. Receive paths perform early demux, checksum verification, queue accounting, possible GRO/GSO receive segmentation via `udp_rcv_segment()`, and dequeue through `__skb_recv_udp()`. Encapsulation users enable static keys so UDP receive can dispatch tunnel callbacks.

## State and persistence behavior

Persistent state includes global `udp_table`, per-socket `udp_sock` queues/counters/tunnel fields, per-net MIB counters, sysctl memory thresholds, static keys for encapsulation, and optional hash4 connected-socket tables. `udp_dev_scratch` stores short-lived per-SKB receive metadata in `skb->dev_scratch`.

## Dependencies and integration points

It depends on inet sockets, GSO, SNMP, IP, IPv6, poll, seq_file, indirect call wrappers, BPF, and NUMA allocation helpers. It integrates with IPv4/IPv6 UDP protocols, UDP-Lite style checksum paths, UDP tunnel receive/transmit, `/proc/net/udp*`, BPF psock updates, GRO/GSO, and socket sysctls.

## Risks and test signals

Risks include hash-table races during rehash/lookup, disabled `CONFIG_BASE_SMALL` hash4 assumptions, checksum state corruption after tunnel/GRO paths, wrong receive queue accounting with forward deficit, per-NUMA queue allocation failure, and static-key leaks for encapsulation. Tests should cover bind/connect/reconnect lookup, IPv4/IPv6 checksum success/failure, UDP_SEGMENT and GRO loopback cases, UDP tunnel decapsulation, proc output, memory pressure/drop counters, BPF psock proto update, and `CONFIG_BASE_SMALL` builds.
