# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_io.c

## Purpose

`qlcnic_io.c` implements the qlcnic packet data path. It builds TX descriptors, maps/unmaps SKB DMA fragments, supports checksum/TSO/VXLAN offloads, handles firmware-assisted MAC learning, processes TX completions, refills RX buffers, parses 82xx and 83xx RX/LRO/status descriptors, dispatches firmware async messages, and wires these operations into NAPI poll handlers and diagnostic receive paths.

## Important APIs, Types, And Functions

- TX descriptor macros encode VLAN, port/context, opcode, fragment count, and packet length fields in `struct cmd_desc_type0`.
- Status descriptor macros decode owner, opcode, packet length, checksum status, ring handle, VLAN, LRO, and 83xx-specific fields.
- `qlcnic_xmit_frame()` is the netdev TX entry point.
- `qlcnic_tx_pkt()` builds regular Ethernet/checksum/TSO descriptors.
- `qlcnic_tx_encap_pkt()` builds VXLAN encapsulated checksum/LSO descriptors.
- `qlcnic_map_tx_skb()` and `qlcnic_unmap_buffers()` manage TX DMA mappings.
- `qlcnic_process_cmd_ring()` handles TX completions and queue wakeup.
- `qlcnic_alloc_rx_skb()`, `qlcnic_post_rx_buffers_nodb()`, and `qlcnic_post_rx_buffers()` allocate/map/post RX buffers.
- `qlcnic_process_rxbuf()` unmaps RX DMA and applies checksum state.
- 82xx RX paths: `qlcnic_process_rcv()`, `qlcnic_process_lro()`, and `qlcnic_process_rcv_ring()`.
- 83xx RX paths: `qlcnic_83xx_process_rcv()`, `qlcnic_83xx_process_lro()`, and `qlcnic_83xx_process_rcv_ring()`.
- `qlcnic_handle_fw_message()` handles link events, loopback responses, and DCB AENs.
- MAC-learning helpers add/delete learned firmware filters from TX/RX observations.
- NAPI helpers add, delete, enable, and disable family-specific RX/TX pollers.

## Control Flow

TX starts in `qlcnic_xmit_frame()`: check device-up and MAC spoofing policy, select TX ring, normalize fragment count for non-TSO packets, stop queue on low descriptors, map SKB DMA, write descriptor buffer addresses, choose regular or VXLAN descriptor formatting, optionally append learned MAC filter commands, update stats, issue a write barrier, and ring the producer doorbell.

Regular TX descriptor building handles VLAN-in-packet, hardware VLAN tags, port VLAN insertion, multicast address copy, TSO header copying, and IPv4/IPv6 TCP/UDP checksum opcodes. VXLAN TX descriptor building handles inner/outer header offsets and encapsulated LSO header copies.

TX completion polling compares software and firmware consumers, unmaps all completed SKB fragments, frees SKBs, advances the software consumer, and wakes stopped queues when descriptors recover.

RX status polling drains descriptors until budget or firmware ownership. Packet paths validate ring/handle, unmap RX buffers, set checksum state, process MAC learning, size and pull SKBs, handle VLAN/PVID policy, set protocol, attach VLAN tags, and deliver to GRO or the stack. Completed buffers are moved to free lists, reallocated, spliced back to RDS rings, and reposted.

Firmware response descriptors are interleaved with RX completions. The handler reconstructs message words and dispatches link, loopback, and DCB events.

## State And Persistence Behavior

Data-path state includes ring producers/consumers, command buffers, DMA fragment arrays, RX free lists, NAPI objects, IRQ vector bindings, link state, loopback diagnostics, learned filter hashes, VLAN/PVID settings, SKB checksum/GSO metadata, and adapter/ring statistics. Device-visible state includes descriptor rings, MMIO doorbells, interrupt masks, and firmware-programmed MAC filters.

## Dependencies And Integration Points

The file depends on Linux SKB, VLAN, checksum, GRO, NAPI, DMA, IPv4/IPv6, and netdevice queue APIs. It integrates with `qlcnic_main.c` through netdev TX, attach/detach, NAPI, and interrupt scheduling, and with `qlcnic_hw.c` through MAC filter programming and interrupt enable/disable operations.

## Risks

- Descriptor accounting for TSO, VLAN TSO templates, and VXLAN LSO is subtle and can corrupt rings if producer movement is wrong.
- DMA unwind paths must exactly match completed mappings.
- VLAN/PVID policy intentionally drops some tagged packets and can look like RX loss.
- MAC-learning filter state can diverge from firmware on command failures.
- 82xx and 83xx descriptor formats are different; shared changes must preserve format-specific parsing.
- RX invalid descriptor handling consumes descriptors but only some paths update explicit counters.

## Test Signals

Exercise plain/checksum/TSO/TSO6/VLAN/VXLAN/VXLAN-GSO TX, RX checksum/GRO/LRO, VLAN add/delete and PVID behavior, multicast/promisc changes, TX queue stop/wake under stress, NAPI budget behavior, legacy/MSI/MSI-X interrupts, SR-IOV VF traffic, loopback diagnostics, link events, and counters for DMA map errors, allocation failures, dropped packets, LRO, and encapsulation checksum.
