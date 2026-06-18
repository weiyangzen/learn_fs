# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_eth_io_defs.h

## Purpose
`ena_eth_io_defs.h` is the generated/contract-style hardware ABI for ENA Ethernet I/O descriptors and per-CQ interrupt/NUMA registers. It defines protocol indices, TX/RX descriptor layouts, completion descriptor layouts, and bit masks/shifts used by the common ENA code to encode and decode device-visible rings.

## Important APIs, Types, And Functions
The main types are `struct ena_eth_io_tx_desc`, `struct ena_eth_io_tx_meta_desc`, `struct ena_eth_io_tx_cdesc`, `struct ena_eth_io_rx_desc`, `struct ena_eth_io_rx_cdesc_base`, `struct ena_eth_io_rx_cdesc_ext`, `struct ena_eth_io_intr_reg`, and `struct ena_eth_io_numa_node_cfg_reg`. Enums `ena_eth_io_l3_proto_index` and `ena_eth_io_l4_proto_index` define device protocol identifiers for IPv4, IPv6, TCP, UDP, RoCE, and unknown traffic. The mask/shift macros cover descriptor length, request ID split fields, phase bits, first/last/completion flags, checksum/TSO flags, header length, RX status, hash metadata, interrupt delay, and NUMA enablement.

## Control Flow, State, And Integration
There is no executable control flow. State is the packed little hardware state shared between driver memory and device DMA/MMIO. TX descriptors carry buffer addresses, offload protocol flags, and header sizing; metadata descriptors carry L3/L4 offsets and MSS for TSO; TX completion descriptors return request IDs and phase. RX descriptors publish buffers to hardware; RX completion descriptors return status, length, request ID, packet offset, hash, and checksum status. `ena_eth_com.h`, `ena_com`, `ena_netdev.c`, and `ena_xdp.c` rely on these exact fields.

## Dependencies
The file assumes kernel `BIT()` and `GENMASK()` helpers are available through including layers. It is coupled to ENA firmware/hardware ABI and to admin feature negotiation that reports max descriptors, LLQ layout, and interrupt moderation granularity.

## Risks And Test Signals
The major risk is ABI drift: a wrong bit mask, phase bit, request ID split, or length interpretation corrupts DMA rings. Test signals include descriptor packing tests in common code, RX checksum/hash validation, TSO and partial-checksum traffic, 64 KiB page-size RX buffers, interrupt moderation changes, and long stress tests that force phase-bit wrap.
