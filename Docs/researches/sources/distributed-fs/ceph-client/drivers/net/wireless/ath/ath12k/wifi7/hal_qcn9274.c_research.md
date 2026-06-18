# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcn9274.c

## Purpose

`hal_qcn9274.c` provides the QCN9274-family Wi-Fi 7 HAL implementation used by QCN9274 v1/v2 and related IPQ5332/IPQ5424 targets. It defines SRNG templates, chip register tables, RX descriptor accessors, HAL parameter blocks, TCL-to-WBM mappings, SRNG config creation, and `hal_qcn9274_ops`.

## Important APIs and Data

- `hw_srng_config_template[]` defines the ring type inventory: REO destination/exception/reinject/cmd/status, TCL data/cmd/status, CE src/dst/status, WBM idle and release rings, RXDMA buffers/monitor/status/direct buffers, PPE2TCL, PPE release, and TX/RX monitor destination rings.
- Register tables include `qcn9274_v1_regs`, `qcn9274_v2_regs`, `ipq5332_regs`, and `ipq5424_regs`. They map common register-table members to chip-specific offsets and CE base calculations.
- RX descriptor helpers operate on `desc->u.qcn9274_compact`, including first/last MSDU, L3 padding, encryption validity/type, decap/mesh state, MPDU sequence/control validity, MSDU length/rate/bandwidth/frequency/NSS/TID/peer id, payload pointer, addr2/addr4 handling, checksum/decryption status, and MPDU error bitmap extraction.
- Public helpers expose descriptor size, MPDU start/MSDU end offsets, source-link id, MPDU start and MSDU end word masks, crypto header reconstruction, 802.11 header reconstruction, and consolidated RX descriptor extraction.
- `ath12k_hw_hal_params_qcn9274` and `ath12k_hw_hal_params_ipq5332` set RX buffer RBM and enabled WBM2SW cookie conversion rings.
- `ath12k_hal_srng_create_config_qcn9274()` duplicates the SRNG template and fills per-ring register starts/sizes using `hal->regs`.
- `ath12k_hal_tcl_to_wbm_rbm_map_qcn9274[]` maps TCL rings to WBM ring numbers and RBM ids.
- `hal_qcn9274_ops` binds chip-specific RX accessors, SRNG creation, TLV64 REO command/status handlers, and common Wi-Fi 7 helpers.

## Control Flow

Common HAL init selects this ops table for QCN9274, IPQ5332, and IPQ5424 revisions. SRNG setup starts by `kmemdup()`-ing the template, then fills register groups for each host-accessible ring from `hal->regs`. Multi-ring types compute `reg_size[]` by subtracting adjacent ring base/HP offsets; single-ring types only set `reg_start[]`.

RX processing goes through `hal_qcn9274_ops.extract_rx_desc_data`. The function reads fields from `rx_desc` and `ldesc`, normalizes them into `struct hal_rx_desc_data`, computes NSS from MIMO stream bitmap, and maps hardware error bits from `RX_MSDU_END_INFO13_*` to generic `HAL_RX_MPDU_ERR_*` values. Crypto and 802.11 header helpers reconstruct software-visible headers from MPDU start metadata.

REO command/status rings use TLV64 layout on this chip family: ring entry sizes include `struct hal_tlv_64_hdr`, command-ring initialization uses `ath12k_wifi7_hal_reo_init_cmd_ring_tlv64`, and ops point to `ath12k_hal_encode_tlv64_hdr` / `ath12k_hal_decode_tlv64_hdr`.

## State and Persistence

The register tables, HAL params, TCL/WBM mapping, and ops table are immutable globals. Runtime state is allocated into `hal->srng_config`. Register programming is performed later through common helpers using the starts/sizes created here. RX descriptor helpers read and sometimes mutate DMA-visible descriptor memory, especially MSDU length and end-TLV copy. Cookie conversion state is controlled by the HAL params used by common `ath12k_wifi7_hal_cc_config()`.

## Dependencies and Integration Points

The file includes `hal_desc.h`, `hal_qcn9274.h`, `hw.h`, `hal.h`, and `hal_tx.h`. It integrates with common Wi-Fi 7 HAL functions from `hal.c`, REO/RX helpers from `hal_rx.c`, TX DSCP/TID mapping, common TLV64 helpers, and the ath12k hardware revision table. IPQ5332/IPQ5424 use the same ops but different register tables and, for CE, base subtraction constants from `hal.h`.

## Risks

- SRNG register size derivation assumes adjacent ring offsets are valid and ordered for every register table.
- `kmemdup()` failure returns `-ENOMEM`; callers must stop setup cleanly and avoid using an uninitialized `hal->srng_config`.
- The same HAL params are reused for IPQ5332/IPQ5424; any future per-chip cookie conversion or RBM differences need separate params.
- Descriptor extraction relies on QCN9274 compact layout and masks; mixing descriptor size/ops with the wrong hardware revision would corrupt RX parsing.
- Register table omissions are hazardous because common helpers dereference many members through macros.
- Crypto header reconstruction intentionally returns for WEP/WAPI/open cases; upper layers must understand when no header bytes were produced.

## Test Signals

Test with QCN9274 v1, QCN9274 v2, IPQ5332, and IPQ5424 probe paths. Validate SRNG config starts/sizes against hardware docs, run RX/TX traffic over all TCL/WBM rings, exercise REO command/status TLV64 handling, confirm RX descriptor parsing for encrypted, multicast, checksum-fail, and error frames, and inspect debug dumps for correct ring IDs/loop counts. Build-time checks should assert descriptor sizes and offsets used by this file.
