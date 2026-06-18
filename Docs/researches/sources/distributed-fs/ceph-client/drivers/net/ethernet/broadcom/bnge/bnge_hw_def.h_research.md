# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hw_def.h

## Purpose
This header defines hardware descriptor and completion layouts for the Broadcom `bnge` network driver. It is the low-level contract used by TX, RX, TPA/GRO, RSS, VLAN, checksum, and asynchronous-event paths to encode or decode values shared with firmware and NIC DMA rings.

## Important APIs, Types, And Functions
The exported surface is macro-heavy. Important structures are `tx_bd_ext`, `rx_cmp`, `rx_cmp_ext`, `rx_agg_cmp`, `rx_tpa_start_cmp`, `rx_tpa_start_cmp_ext`, `rx_tpa_end_cmp`, and `rx_tpa_end_cmp_ext`. Important helpers include `TX_CMP_SQ_CONS_IDX`, `RX_CMP_L4_CS_OK`, `RX_CMP_METADATA0_TCI`, `RX_CMP_V3_HASH_TYPE`, `RX_CMP_VLAN_VALID`, `RX_CMP_HASH_TYPE`, `TPA_START_*`, `TPA_END_*`, and async-event decoding helpers such as `EVENT_DATA1_RESET_NOTIFY_FATAL`.

## Control Flow
There is no executable control flow beyond macro expansion. Runtime paths in `bnge_txrx.c`, `bnge_netdev.c`, and HWRM event handling read DMA completions into these packed layouts, mask little-endian fields, and translate them into SKB checksum status, VLAN metadata, RSS hash type, TPA aggregation bookkeeping, and link/reset event handling.

## State And Persistence
The file defines transient hardware-visible ring state. State persists only in DMA descriptors and completion memory populated by the NIC. Valid bits, opaque indices, aggregate IDs, VLAN tags, and error bitfields must be interpreted against the producer/consumer ring indices held in `bnge_net` ring structures.

## Dependencies And Integration Points
It depends on Linux bit helpers, endian helpers, and HSI constants from `<linux/bnge/hsi.h>` included through adjacent headers. `bnge_netdev.h` includes this header so ring structures and NAPI/TXRX code can share descriptor constants.

## Risks
The largest risk is bitfield drift against firmware/HW specifications. Endian mistakes or incorrect masks can silently corrupt packet metadata. `RX_TPA_END_CMP_FLAGS_PLACEMENT_ANY_GRO` uses a bitwise AND of two placement constants; reviewers should confirm this matches the intended hardware encoding. TPA and RSS-v3 macros also depend on capability bits in `bnge_dev`.

## Test Signals
Useful signals are RX/TX traffic with checksum offload, VLAN strip/insert, RSS hash reporting, GRO/LRO/TPA traffic, jumbo frames, tunnel traffic, and async reset/link events. Packet counters, SKB checksum status, VLAN tags, and absence of DMA/completion errors are the practical validation points.
