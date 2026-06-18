# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcn9274.h

## Purpose

`hal_qcn9274.h` exposes the QCN9274-family HAL public surface: ops, register tables, TCL/WBM mapping, HAL params, RX descriptor accessors, descriptor offset/size helpers, crypto/header extractors, and consolidated RX descriptor extraction.

## Important APIs

- Extern globals: `hal_qcn9274_ops`, `qcn9274_v1_regs`, `qcn9274_v2_regs`, `ipq5332_regs`, `ipq5424_regs`, `ath12k_hal_tcl_to_wbm_rbm_map_qcn9274[]`, `ath12k_hw_hal_params_qcn9274`, and `ath12k_hw_hal_params_ipq5332`.
- RX descriptor helpers: L3 padding, end-TLV copy, MPDU PPDU id, MSDU length set, payload pointer, descriptor start/end offsets, descriptor size, source link id, MPDU/MSDU word masks, crypto header extraction, 802.11 header extraction, and `ath12k_hal_extract_rx_desc_data_qcn9274()`.

## Control Flow Role

The header provides declarations for common HAL selection and RX processing. `hal.c` uses the exported globals to populate `ath12k_wifi7_hw_ver_map`. Upper RX code and ops tables use the descriptor helper declarations when interpreting QCN9274-family RX descriptors.

## State and Persistence

No storage is defined here. The exported register tables and HAL params define persistent chip configuration, while descriptor helper prototypes operate on DMA-visible RX descriptor state.

## Dependencies and Integration Points

It includes Linux 802.11/Ethernet headers and ath12k common/Wi-Fi 7 headers: `<linux/ieee80211.h>`, `<linux/etherdevice.h>`, `../hal.h`, `hal_rx.h`, and `hal.h`. It is implemented by `hal_qcn9274.c` and consumed by `hal.c` and RX descriptor users.

## Risks

- Any signature change must stay synchronized with `hal_ops` expectations and call sites.
- The header exports IPQ5332 params but no separate IPQ5424 params; IPQ5424 currently reuses IPQ5332 params through `hal.c`.
- Public descriptor helpers are tied to `struct hal_rx_desc_qcn9274_compact`; using them with a non-QCN9274 descriptor layout is invalid.

## Test Signals

Build coverage should ensure all declarations match definitions and `hal_ops` assignments. Runtime tests should verify QCN9274-family hardware revision selection, descriptor size/offset consumers, and RX data extraction across the chips that include this header.
