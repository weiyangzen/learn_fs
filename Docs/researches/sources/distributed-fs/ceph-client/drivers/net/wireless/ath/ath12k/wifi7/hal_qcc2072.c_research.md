# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcc2072.c

## Purpose

`hal_qcc2072.c` provides the QCC2072-specific Wi-Fi 7 HAL binding. It supplies QCC2072 register offsets, adapts WCN7850-style SRNG configuration for QCC2072 REO TLV sizes, implements QCC2072 RX descriptor accessors, and exposes `hal_qcc2072_ops` for the common HAL initializer.

## Important APIs and Data

- `qcc2072_regs` defines per-block register offsets for TCL, REO, WBM, PPE, CE, PCIe, hot reset, and QRTR node id.
- RX descriptor helpers operate on `desc->u.qcc2072`, including MSDU length mutation, 802.11 header reconstruction, crypto header reconstruction, end-TLV copy, L3 padding, MPDU PPDU id, payload pointer, first/last MSDU flags, encryption/decap/mesh metadata, sequence/control validity, packet length/rate/bandwidth/frequency/NSS/TID/peer id, addr2 validity, multicast/broadcast detection, checksum/decrypt done state, and MPDU error bitmap mapping.
- `ath12k_hal_extract_rx_desc_data_qcc2072()` consolidates many raw descriptor fields into `struct hal_rx_desc_data` for upper RX processing.
- `ath12k_hal_srng_create_config_qcc2072()` calls `ath12k_hal_srng_create_config_wcn7850()` and then overrides REO command/status entry sizes for QCC2072-specific TLV32 descriptor wrappers.
- `ath12k_hal_reo_status_dec_tlv_hdr_qcc2072()` decodes a TLV32 status and skips `tlv32_padding` to return the embedded generic queue stats status.
- `hal_qcc2072_ops` binds the chip-specific accessors and common Wi-Fi 7 helpers into the HAL operation table.
- Public offset helpers return `offsetof(struct hal_rx_desc_qcc2072, mpdu_start_tag)` and `offsetof(struct hal_rx_desc_qcc2072, msdu_end_tag)`.

## Control Flow

The common `ath12k_wifi7_hal_init()` selects `hal_qcc2072_ops` for `ATH12K_HW_QCC2072_HW10`. SRNG setup then enters `ath12k_hal_srng_create_config_qcc2072()`, inherits WCN7850 ring config, and corrects REO command/status ring entry sizes for QCC2072's TLV32 command/status layout.

RX processing uses the function pointers in `hal_qcc2072_ops`. The extraction path reads fields from first and last descriptors (`rx_desc` and `ldesc`), resolves encryption and decapsulation state, copies rate/PHY/TID/peer fields, computes NSS with `hweight8()`, and translates hardware error bits into `HAL_RX_MPDU_ERR_*` bits. Crypto header reconstruction branches by encryption type, handles TKIP/CCMP/GCMP PN byte ordering, inserts key id, and returns without modification for open/WEP/WAPI cases.

REO status decoding is chip-specific: the code decodes a TLV32 header, treats the payload as `struct hal_reo_get_queue_stats_status_qcc2072`, and returns a pointer to the nested `status` after padding.

## State and Persistence

`qcc2072_regs` and `hal_qcc2072_ops` are immutable global configuration. Runtime state is updated through inherited common helpers for ring registers, descriptors, cookie conversion, and RX buffer address management. Descriptor helpers read and mutate DMA-visible RX descriptor memory, notably MSDU length and copied end TLVs. SRNG config allocation occurs through the WCN7850 helper and is then modified in `hal->srng_config`.

## Dependencies and Integration Points

The file includes `hal_qcc2072.h` and `hal_wcn7850.h`, relying on the WCN7850 SRNG setup and TCL-to-WBM mapping selected in `hal.c` for QCC2072. It uses common Wi-Fi 7 helpers from `hal.c`, TX DSCP/TID mapping from `hal_tx`, TLV32 helpers from common HAL code, and descriptor masks from RX descriptor headers and `hal_desc.h`.

## Risks

- QCC2072 inherits WCN7850 SRNG config and params in the hardware map; any QCC2072 divergence outside the REO command/status entry sizes may be missed.
- Some register members are `ATH12K_HW_REG_UNDEFINED`, including `reo1_qdesc_lut_base0/1` and `wbm_sw1_release_ring_base_lsb`; common helpers that write those registers would be unsafe unless never called on this target.
- `ath12k_hal_rx_desc_get_msdu_src_link_qcc2072()` returns `0`, so multi-link source-link metadata is unavailable or intentionally unsupported on this chip path.
- `ath12k_hal_rx_desc_copy_end_tlv_qcc2072()` copies `sizeof(struct rx_msdu_end_qcn9274)` into a QCC2072 descriptor field; this depends on layout compatibility.
- TLV32 padding handling is fragile. A mismatch in `hal_reo_get_queue_stats_status_qcc2072` size or firmware status format would shift decoded fields.

## Test Signals

Validation should include QCC2072 probe, RX descriptor extraction tests on encrypted/open frames, checksum/decrypt/error paths, 802.11 header reconstruction with and without addr4, REO command/status round trips confirming TLV32 entry size and padding, and traffic tests that exercise inherited WCN7850 ring configuration. Runtime register traces should confirm that undefined register entries are not touched on active QCC2072 paths.
