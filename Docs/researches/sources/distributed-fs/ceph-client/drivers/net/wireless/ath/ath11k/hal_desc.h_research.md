# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_desc.h

## Purpose
`hal_desc.h` defines the packed hardware descriptor ABI used by ath11k HAL, DP, CE, TCL, REO, RXDMA, and WBM paths. It maps device-produced and host-produced ring entries to C structs and bit masks. The file is declarative: TLV tags, buffer address layouts, RX/TX command descriptors, CE source/destination/status descriptors, WBM release descriptors, REO queue descriptors, REO commands, and REO status records.

## Important APIs, types, and data
The foundational type is `struct ath11k_buffer_addr`, which carries a 40-bit DMA address, return buffer manager, and software cookie. `enum hal_tlv_tag` enumerates hardware TLV tags used by monitor status, RX/TX data, REO/TQM, CCE, and PHY/MAC status streams. `struct hal_tlv_hdr` defines the common TLV header.

RX-facing descriptors include `struct rx_mpdu_desc`, `struct rx_msdu_desc`, `struct hal_reo_dest_ring`, `struct hal_reo_entrance_ring`, `struct hal_sw_monitor_ring`, `struct hal_rx_msdu_link`, `struct hal_rx_reo_queue`, and `struct hal_rx_reo_queue_ext`. TX-facing descriptors include `struct hal_tcl_data_cmd`, `struct hal_tcl_gse_cmd`, and `struct hal_tcl_status_ring`. CE descriptors include `struct hal_ce_srng_src_desc`, `struct hal_ce_srng_dest_desc`, and `struct hal_ce_srng_dst_status_desc`. WBM completion/release data is represented by `struct hal_wbm_release_ring`, `struct hal_tx_rate_stats`, and related release/status enums.

## Control flow
There is no executable control flow. The descriptors are written by HAL/DP/CE helpers and consumed from DMA rings by DP RX/TX and monitor paths.

## State and persistence behavior
The structs represent state in DMA rings or descriptors shared with hardware. Ownership fields, return buffer managers, ring ids, loop counts, PN/bitmap/stat counters, and release details persist only while descriptors live in host/device memory. There is no disk persistence.

## Dependencies and integration points
The header includes `core.h` and relies on kernel bitfield helpers and packed layout semantics. It must stay synchronized with firmware/hardware interface definitions and with `hal.h`. `hal_rx.c`, `hal_tx.c`, `hal.c`, CE, DP RX, and DP TX are direct consumers.

## Risks
Hardware ABI drift is the main risk. Wrong masks, field widths, struct order, packed attributes, enum values, or descriptor sizes can corrupt DMA interpretation. Chip-specific variants must be parsed through the right hardware op. The apparent `HAL_RX_REO_QUEUE_INFO2_MSDU_COUNT` definition lacks `GENMASK`, which is a local risk if used as a mask.

## Test signals
Clean firmware boot, CE/HTC messaging, TCL enqueue and TX completion, RX buffer recycling, REO queue setup, REO status processing, monitor-mode radiotap data, and absence of DMA/RBM/descriptor warnings are useful signals. Compile tests only validate references, not hardware semantics.
