# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_enet.h

## Purpose
This header is the shared NIC-side contract for the HNS3 Ethernet driver. It defines NIC state bits, register offsets, descriptor layouts, packet type enums, ring/vector/private data structures, ring helpers, interrupt coalescing structures, hardware error/reset mapping types, and exported function prototypes used between the main netdev implementation, ethtool support, debug/DCB modules, and tracepoints.

## Important APIs, Types, and Functions
- `enum hns3_nic_state` defines private state bits for testing, resetting, initialized/down/disabled/removing states, service flags, hardware TX checksum, advanced RX descriptor layout, and TX push.
- Register macros define RX/TX ring base address, descriptor count/length, head/tail, free descriptor count, packet record, error, TQP enable, RX/TX enable, vector GL/RL/QL offsets, CQ period mode registers, and hardware buffer-size encodings.
- Descriptor bit macros define TX fields for L3/L4 types, checksum, VLAN, TSO, header lengths, outer tunnel metadata, FE/VLD/timestamp bits, MSS, and hardware checksum mode; RX fields define parsed packet metadata, error bits, GRO fields, timestamp bits, VLAN strip indicators, and packet type.
- `struct hns3_desc` is the packed hardware descriptor union for TX, RX, checksum, and timestamp views.
- `struct hns3_desc_cb` tracks driver-side ownership for each descriptor: DMA address, CPU buffer, private pointer, page offset or sent bytes, length, reuse/refill flags, descriptor type, and pagecnt bias.
- `struct ring_stats`, `struct hns3_tx_spare`, `struct hns3_enet_ring`, `struct hns3_enet_ring_group`, `struct hns3_enet_tqp_vector`, and `struct hns3_nic_priv` define the main runtime data model.
- Inline helpers and macros include `ring_space()`, register read/write wrappers, reset-state check, `ring_to_*` conversions, page sizing, ring iteration, AE op accessors, GL/RL unit conversion, and stats update helpers.
- Prototypes expose ethtool setup, channel changes, ring init/reset/cleanup, TX/RX fast paths, coalescing setters, promisc update requests, reset notifications, debug/DCB hooks, trace helper `hns3_shinfo_pack()`, and external loopback helpers.

## Control Flow
This header has no standalone executable flow, but it strongly shapes the control flow in `hns3_enet.c` and `hns3_ethtool.c`. TX setup fills `struct hns3_desc` using the TX bitfield macros, records buffer ownership in `struct hns3_desc_cb`, advances indices in `struct hns3_enet_ring`, and checks capacity through `ring_space()`. RX setup uses the same descriptor and control-block pair to map pages, reuse fragments, parse packet metadata, and refill hardware descriptors. Vector control flows iterate `struct hns3_enet_ring_group` through `hns3_for_each_ring()`, and reset/open/close paths rely on `struct hns3_nic_priv` state bits to gate operations.

## State and Persistence
The header declares all major in-memory persistent state for a netdev instance. `struct hns3_nic_priv` persists for the `net_device` lifetime. Ring descriptors and descriptor callbacks persist across open state until ring teardown or reset uninit. Ring indices, pending buffers, TX spare indices, RX SKB assembly scratch state, and coalescing/DIM counters are mutable runtime state. The register constants describe hardware state that persists in device registers until reset or driver reprogramming.

The descriptor control block `type` flags are critical persistence metadata because they determine whether cleanup uses skb freeing, page unmapping, page-pool return, TX spare reclaim, or scatterlist unmap. `ring_stats` is shared with ethtool and netdev stats, while `u64_stats_sync` provides a stable read protocol.

## Dependencies and Integration Points
The header includes Linux DIM, VLAN, page_pool type definitions, barriers, and `hnae3.h`. It is consumed by the main enet file, ethtool file, trace header, debug code, and optional DCB support. It integrates directly with kernel types such as `net_device`, `sk_buff`, `napi_struct`, `ethtool_channels`, `page_pool`, `dim`, `pci_dev`, and DMA addresses. Hardware capability and reset types come from HNAE3, so this header is tightly coupled to the AE layer ABI.

## Risks and Edge Cases
The packed descriptor layout must match hardware exactly; changing alignment, field order, or endian types would corrupt DMA descriptors. Several macros encode fields by shifts and masks rather than typed bitfield helpers, so callers must pass values within hardware ranges. `ring_space()` assumes exactly one unused descriptor and relies on release/acquire pairing with completion, making memory ordering part of the ABI. `struct hns3_enet_ring` uses unions for TX and RX-only fields; using the wrong half for a ring type would corrupt unrelated state.

RX page sizing depends on PAGE_SIZE and `buf_size`, with higher-order pages only for small page kernels and larger RX buffers. Descriptor counts must stay aligned to `HNS3_RING_BD_MULTIPLE` and within min/max pending limits. Feature state bits must stay synchronized with actual AE capabilities; advertising TX push, advanced RX layout, or hardware TX checksum without matching hardware support would misprogram descriptors.

## Test Signals
Compile-time layout and type checks are important because this file underpins tracepoints, ethtool, and the main driver. Runtime signals include correct descriptor DMA programming, stable TX/RX under ring wrap, accurate ethtool queue stats, correct feature advertisement, successful coalescing register programming, reset/open/close state transitions, page reuse behavior for 2K and 4K RX buffers, TX push on capable devices, and absence of DMA mapping leaks during ring teardown.
