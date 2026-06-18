# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lan_tx_rx.h

## Purpose
Defines LAN Tx/Rx descriptor formats, filter-programming descriptor fields, queue context structures, timestamp descriptor structures, and bit masks used by the `ice` datapath and queue setup code.

## Important APIs, types, and functions
- Rx descriptors: `union ice_32byte_rx_desc`, `union ice_32b_rx_flex_desc`, `struct ice_32b_rx_flex_desc_nic`, and `struct ice_32b_rx_flex_desc_nic_2`.
- Rx descriptor metadata enums: `enum ice_rxdid`, `enum ice_flex_mdid_pkt_flags`, `enum ice_flex_rx_mdid`, `enum ice_flg64_bits`, and status/error bit enums.
- Flow Director/filter programming: `struct ice_fltr_desc` and `ICE_FXD_FLTR_*` masks for queue index, completion reporting, stats, destination queue, drop, flex metadata, command, VSI, FDID, and writeback status.
- Rx queue context: `struct ice_rlan_ctx` plus header split enums and field shift constants.
- Tx descriptors: `struct ice_tx_desc`, `enum ice_tx_desc_dtype_value`, `enum ice_tx_desc_cmd_bits`, length/offset masks, and maximum encoded header lengths.
- Tx context descriptor: `struct ice_tx_ctx_desc`, generic checksum descriptor masks, context command bits, and tunnel/offload encoding.
- Tx queue context: `struct ice_tlan_ctx` with base, port/PF/VF identity, completion queue, interrupt, shaping, TSO, and cache profile fields.
- Timestamping/TxTime: `struct ice_ts_desc`, `ICE_TS_DESC()`, `struct ice_txtime_ctx`, and TxTime queue/profile constants.

## Control flow
There is no executable flow. Datapath code fills these packed hardware structures and writes descriptors or queue contexts to DMA/MMIO areas. The descriptor unions model read and writeback layouts for the same 32-byte hardware descriptor memory.

## State and persistence behavior
The structures describe DMA-visible ring descriptors and firmware/hardware queue contexts. State persists in device queues and host descriptor rings until queue teardown or reset. Endianness annotations (`__le16`, `__le32`, `__le64`) are part of the hardware ABI.

## Dependencies and integration points
Consumed by Tx/Rx hot paths (`ice_txrx.c`, XDP/XSK, ethtool tests), queue context programming, Flow Director, timestamping, and TxTime support. It depends on common bit helpers and shared constants such as byte/word scaling and register macros.

## Risks
This is ABI-level hardware layout. Field shifts, masks, endianness, or struct packing mistakes can break packet I/O, checksum offload, RSS, Flow Director, VLAN tagging, timestamping, or queue setup. The header intentionally avoids helpers, so callers must compose fields consistently and respect hardware limits such as queue counts and maximum encoded lengths.

## Test signals
Signals include packet Rx/Tx across legacy and flex descriptors, RSS hash and flow ID correctness, VLAN tag extraction/insertion, checksum and TSO offload, XDP/XSK Tx descriptor use, Flow Director add/delete completion writebacks, timestamp descriptor processing, TxTime queue setup, and queue context programming across PF/VF/VMQ modes.
