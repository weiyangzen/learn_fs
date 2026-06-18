# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_desc.h

## Purpose

`hal_desc.h` defines the Wi-Fi 7 HAL descriptor ABI shared between host software and ath12k hardware/firmware. It contains TLV tag IDs, RX/TX/REO/TCL/WBM/CE/monitor descriptor layouts, bit masks for packed fields, and comments describing producer/consumer ownership and hardware semantics.

## Important APIs, Types, and Constants

- `enum hal_tlv_tag` enumerates hundreds of hardware TLV tags, including PHY/MAC TX/RX, REO commands/statuses, monitor, MLO, EHT, ranging, and command-wrapper tags. `HAL_TCL_DATA_CMD` is explicitly marked with a FIXME for correct assignment.
- RX descriptors include `struct rx_mpdu_desc`, `struct rx_msdu_desc`, `struct rx_msdu_ext_desc`, `struct hal_reo_dest_ring`, `struct hal_reo_entrance_ring`, `struct hal_rx_msdu_link`, `struct hal_rx_reo_queue`, `struct hal_rx_reo_queue_ext`, and `struct hal_rx_reo_queue_1k`.
- REO command/status descriptors include `struct hal_reo_cmd_hdr`, `struct hal_reo_get_queue_stats`, `struct hal_reo_get_queue_stats_qcc2072`, `struct hal_reo_flush_queue`, `struct hal_reo_flush_cache`, `struct hal_reo_update_rx_queue`, `struct hal_reo_unblock_cache`, and status structures for queue stats, flush queue/cache, unblock cache, timeout list, and threshold reached.
- TCL/TX descriptors include `struct hal_tcl_data_cmd`, `struct hal_tcl_gse_cmd`, `struct hal_tcl_status_ring`, `struct hal_tx_msdu_ext_desc`, `struct hal_tx_rate_stats`, and `struct hal_tx_msdu_metadata`.
- CE descriptors include `struct hal_ce_srng_src_desc`, `struct hal_ce_srng_dest_desc`, and `struct hal_ce_srng_dst_status_desc`.
- WBM descriptors include RX/TX completion and release rings, cookie-converted RX release format, generic release ring, buffer ring, and release reason enums.
- Monitor/PPE descriptors include `struct hal_sw_monitor_ring`, `struct hal_mon_dest_desc`, `struct hal_reo_to_ppe_ring`, and `struct hal_tcl_entrance_from_ppe_ring`.
- All hardware-facing structs are packed where needed and store fields in `__le32`/`__le16` form for DMA-visible little-endian ABI compatibility.

## Control Flow Role

This header is declarative, but it drives control flow in the implementation files. `hal.c` writes CE/WBM descriptors using these layouts. `hal_rx.c` encodes REO commands and decodes REO statuses with these masks. Chip-specific files extract RX metadata from descriptor substructures and fill `hal_rx_desc_data`. Ring entry sizes in chip SRNG config are calculated from these structs, so descriptor size changes directly affect DMA ring programming.

## State and Persistence

The structures represent persistent DMA ring entries and hardware-owned descriptor state. Ownership transitions are documented in comments: RXDMA, REO, WBM, TCL, TQM, SW, FW, PPE, TxMon, and RxMon each produce or consume selected descriptors. Fields track physical addresses, software cookies, return buffer managers, ring IDs, loop counts, MPDU/MSDU sequence and length metadata, PN and crypto status, REO queue bitmaps/counters, error codes, and status correlation command numbers.

## Dependencies and Integration Points

`hal_desc.h` includes `../core.h` for common ath12k/kernel types and is consumed by the Wi-Fi 7 HAL, TX, RX, and chip-specific modules. It depends on Linux bitfield macros (`BIT`, `GENMASK`) and endian-annotated types. It also integrates with descriptors defined elsewhere, notably `struct ath12k_buffer_addr`, `struct hal_wbm_link_desc`, and `struct hal_rx_desc_*` formats from related ath12k headers.

## Risks

- This is an ABI boundary. Reordering fields, changing packing, or using the wrong endian helper can corrupt DMA descriptors or make hardware parse entries incorrectly.
- TLV tag values must match firmware/hardware documentation. The explicit FIXME for `HAL_TCL_DATA_CMD` is a correctness risk if that tag is consumed by active paths.
- The QCC2072-specific REO queue stats command/status wrappers differ from the generic TLV64 shape, increasing risk that entry sizes or status pointer offsets get out of sync.
- Several comments reference hardware behavior and must be kept aligned with silicon revisions; stale documentation can lead to wrong upper-layer assumptions.
- Bit masks reused across multiple implementations must match extraction code in `hal_rx.c`, `hal_qcn9274.c`, and `hal_qcc2072.c`.
- Any struct size used in SRNG `entry_size` calculations must remain dword-aligned and match firmware expectations.

## Test Signals

Strong signals include compile-time size/offset assertions against hardware specs, sparse endian checks, RX/TX traffic with descriptor dumps, REO command/status round trips, monitor ring capture, WBM release/error handling, and chip-specific tests for QCN9274 vs QCC2072 TLV32/TLV64 differences. Regression tests should include malformed/error descriptors to validate error-code parsing and buffer-manager checks.
