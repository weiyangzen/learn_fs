# Group Research: subset-b-004750

This grouped report covers the Wi-Fi 7 ath12k HAL sources listed in subset `subset-b-004750`. Sections are source-tree aligned and wrapped for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal.c

## Purpose

`hal.c` is the common Wi-Fi 7 ath12k HAL implementation for chip-independent ring programming, CE descriptor helpers, WBM idle-link setup, REO queue LUT/cookie-conversion setup, and hardware revision binding. It translates `ab->hw_rev` into the active `ath12k_hal` operation table, descriptor size, TCL-to-WBM return-buffer-manager mapping, register table, and HAL parameter block.

## Important APIs and Data

- `ath12k_wifi7_hal_init()` zeroes `ab->hal` and selects `hal_ops`, `hal_desc_sz`, `tcl_to_wbm_rbm_map`, `regs`, and `hal_params` from `ath12k_wifi7_hw_ver_map`.
- `ath12k_wifi7_hw_ver_map[]` binds QCN9274 v1/v2, WCN7850, IPQ5332, QCC2072, and IPQ5424 to their chip-specific ops, RX descriptor formats, register tables, and HAL params.
- `ath12k_wifi7_hal_srng_dst_hw_init()` and `ath12k_wifi7_hal_srng_src_hw_init()` program SRNG base addresses, MSI configuration, entry size/ring size, interrupt thresholds, host shadow pointer addresses, initial HP/TP values, endian/swap flags, and enable bits.
- `ath12k_wifi7_hal_srng_get_ring_id()` maps ring type, ring number, and PMAC MAC id into a global SRNG ring id with range checks.
- `ath12k_wifi7_hal_srng_update_shadow_config()` allocates a shadow register slot, stores the target HP/TP register address, and redirects the in-memory SRNG HP/TP pointer to the shadow register window.
- CE helpers include `ath12k_wifi7_hal_ce_dst_setup()`, `ath12k_wifi7_hal_ce_get_desc_size()`, `ath12k_wifi7_hal_ce_src_set_desc()`, `ath12k_wifi7_hal_ce_dst_set_desc()`, and `ath12k_wifi7_hal_ce_dst_status_get_length()`.
- RX/WBM helpers include `ath12k_wifi7_hal_set_link_desc_addr()`, `ath12k_wifi7_hal_setup_link_idle_list()`, and `ath12k_wifi7_hal_get_idle_link_rbm()`.
- REO helpers include `ath12k_wifi7_hal_reoq_lut_addr_read_enable()`, `ath12k_wifi7_hal_reoq_lut_set_max_peerid()`, `ath12k_wifi7_hal_write_reoq_lut_addr()`, `ath12k_wifi7_hal_write_ml_reoq_lut_addr()`, and `ath12k_wifi7_hal_cc_config()`.

## Control Flow

Initialization starts at `ath12k_wifi7_hal_init()`, where the selected hardware revision determines all later register and operation dispatch. Ring setup is then driven through the selected `hal_ops` callbacks: destination rings use REO-style offsets for MSI, ring identity, producer interrupt setup, HP address, and misc enable; source rings use TCL-style offsets and consumer interrupt setup. Both flows write ring base LSB/MSB, zero hardware HP/TP registers, update the host-side shadow pointer, and set swap/enable bits last.

Shadow-register setup is opt-in through `ath12k_wifi7_hal_srng_update_shadow_config()`. It derives a target HP register from the SRNG config register group and ring number, adjusts to TP for destination rings, stores that target in `hal->shadow_reg_addr[]`, and rewires the SRNG pointer to the local `HAL_SHADOW_REG(index)` address.

`ath12k_wifi7_hal_setup_link_idle_list()` chains scattered idle-link buffers by writing each scatter buffer's next physical address into the tail of the previous buffer, programs WBM idle-list mode and size, sets base/head/tail pointer registers, advances the hardware HP to `2 * tot_link_desc`, and enables the idle-link SRNG.

`ath12k_wifi7_hal_cc_config()` programs REO and WBM cookie conversion, unless FTM mode is active. It uses QMI CMEM base memory, fixed cookie bit partition constants, and `hal->hal_params->wbm2sw_cc_enable` to enable conversion on selected WBM2SW rings.

## State and Persistence

The file mutates in-memory driver state in `ab->hal`: selected ops/params/registers, `num_shadow_reg_configured`, `shadow_reg_addr[]`, and SRNG HP/TP pointer fields. Persistent hardware state is MMIO register programming via `ath12k_hif_write32()` and `ath12k_hif_read32()`: SRNG registers, WBM idle-list registers, TCL bank registers, REO queue descriptor LUT registers, and cookie conversion registers. CE and link descriptor helpers write DMA-visible descriptor memory in little-endian format.

## Dependencies and Integration Points

This file depends on common ath12k core/HIF/DP types (`ath12k_base`, `ath12k_hal`, `hal_srng`, `hal_srng_config`), Linux bitfield helpers (`u32_encode_bits`, `le32_encode_bits`, `GENMASK`, `BIT`), DMA address conventions, and chip-specific exports from `hal_qcn9274.h`, `hal_wcn7850.h`, and `hal_qcc2072.h`. It is integrated through chip `hal_ops` tables in the chip-specific source files and through the broader ath12k DP/HIF setup path that allocates rings and descriptors before enabling traffic.

## Risks

- Register offsets are hardware ABI. A wrong `ath12k_hw_regs` binding or offset delta can program the wrong ring register and break DMA or interrupts.
- `ath12k_wifi7_hw_ver_map[ab->hw_rev]` assumes `ab->hw_rev` is valid for the table; invalid enum values would index out of bounds unless constrained earlier.
- Shadow register accounting only checks the maximum before incrementing. Duplicate calls for the same ring consume slots and can exhaust `HAL_SHADOW_NUM_REGS_MAX`.
- Idle-link setup assumes `nsbufs > 0` and valid `sbuf[0]`; callers must enforce allocation success.
- `ath12k_wifi7_hal_cc_config()` depends on valid QMI CMEM metadata and skips all cookie conversion in FTM mode.
- CE destination status length extraction clears the length bits in `desc->flags`, so callers must not expect to read the length repeatedly.

## Test Signals

Useful validation includes boot/probe on each mapped hardware revision, ring initialization traces showing correct base/HP/TP/MSI registers, TX/RX traffic through TCL/REO/WBM, interrupt delivery on MSI and non-MSI paths, WBM idle-link pool exhaustion/recovery tests, cookie-conversion error-ring tests, and debug logs from shadow register setup. Static checks should verify that all selected `ath12k_hw_regs` members used by this file are defined for each mapped revision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal.h

## Purpose

`hal.h` is the common Wi-Fi 7 HAL register/mask/API contract. It defines BAR-relative register addresses, chip-register-table access macros, SRNG field masks, WBM cookie-conversion masks, REO command/update flags, REO status structures, and prototypes for the common functions implemented by `hal.c` and `hal_rx.c`.

## Important APIs and Types

- Register address macros cover WCSS UMAC REO/TCL/WBM, CE bases, TCL rings, REO rings, CE rings, WBM idle/release rings, PPE rings, and shadow registers.
- Register-table indirection macros, such as `HAL_TCL1_RING_BASE_LSB(hal)` and `HAL_REO1_QDESC_ADDR(hal)`, dereference `hal->regs` so common code can work across QCN9274, IPQ5332/IPQ5424, QCC2072, and WCN7850-style layouts.
- Offset macros such as `HAL_TCL1_RING_MSI1_BASE_LSB_OFFSET(hal)` derive per-ring register offsets from the base LSB register.
- Field masks define ring size, address MSBs, entry size, MSI enable/swap, host/FW swap, data TLV swap, interrupt thresholds, REO misc controls, cookie conversion, WBM idle-list mode, and queue LUT control.
- REO command flag macros (`HAL_REO_CMD_FLG_*`) and update masks (`HAL_REO_CMD_UPD0_*`, `HAL_REO_CMD_UPD1_*`, `HAL_REO_CMD_UPD2_*`) mirror the hardware command descriptor fields encoded in `hal_rx.c`.
- Status types include `struct hal_reo_status`, nested status payloads for queue stats, flush queue/cache, unblock cache, timeout list, and descriptor threshold reached.
- Exported prototypes include common HAL init/setup helpers, CE descriptor helpers, WBM idle-list helpers, REO LUT helpers, and `ath12k_wifi7_hal_reo_qdesc_size()`.

## Control Flow Role

This header does not execute control flow directly, but it determines how implementation files compute register addresses and encode/decode hardware command/status fields. The common ring setup code in `hal.c` uses this header to calculate target registers and enable bits. The REO command/status code in `hal_rx.c` uses the command flags and status structures here to provide a hardware-independent status shape to upper DP code.

## State and Persistence

`hal.h` defines no storage. It describes state that persists in hardware registers, DMA descriptors, and driver-owned status structures. The most important persistent state surfaces are shadow register slots, HP/TP register values, cookie-conversion enablement, REO queue descriptors, and `struct hal_reo_status` values returned to higher layers.

## Dependencies and Integration Points

The header includes ath12k core/common HAL headers and Wi-Fi 7 descriptor headers: `../core.h`, `../hal.h`, `hal_desc.h`, `hal_tx.h`, `hal_rx.h`, and `hal_rx_desc.h`. It is included by common and chip-specific HAL implementations and by DP code that needs Wi-Fi 7-specific REO status or ring helpers.

## Risks

- Macros are tightly coupled to hardware register layouts. Incorrect values can silently direct MMIO writes to unrelated blocks.
- `HAL_REO_CMD_UPD*` masks must stay aligned with the hardware descriptor masks in `hal_desc.h`; divergence would update the wrong queue fields.
- `HAL_RX_REO_QUEUE_INFO2_MSDU_COUNT` is written as `(31, 7)` rather than a `GENMASK`, which is suspicious and should be checked before use.
- Several register macros dereference `hal->regs`; any chip register table member left undefined can cause invalid MMIO programming if the common helper still uses it.
- Fixed constants such as cookie partition MSBs and default REO timeouts are policy baked into the HAL and need hardware/firmware agreement.

## Test Signals

Build coverage should include all files using these macros with sparse/endian warnings enabled. Runtime validation should compare ring register programming against chip documentation, exercise REO queue update/status commands, verify cookie conversion and shadow registers, and run traffic on every supported hardware revision using this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_desc.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcc2072.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcc2072.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcc2072.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcc2072.h

## Purpose

`hal_qcc2072.h` is the small public interface for the QCC2072 Wi-Fi 7 HAL implementation. It exposes the QCC2072 register table, operation table, and RX descriptor offset helpers to common ath12k code.

## Important APIs

- `extern const struct ath12k_hw_regs qcc2072_regs;`
- `extern const struct hal_ops hal_qcc2072_ops;`
- `ath12k_hal_rx_desc_get_mpdu_start_offset_qcc2072()`
- `ath12k_hal_rx_desc_get_msdu_end_offset_qcc2072()`

## Control Flow Role

The header has no runtime control flow. It allows `hal.c` to reference QCC2072 ops/registers in `ath12k_wifi7_hw_ver_map` and allows other code to query QCC2072 descriptor offsets without exposing the full implementation.

## State and Persistence

The exported globals are immutable configuration. The offset helpers return compile-time layout offsets from `struct hal_rx_desc_qcc2072`, which are used to interpret persistent DMA descriptor memory.

## Dependencies and Integration Points

It includes `../hal.h` and the Wi-Fi 7 `hal.h`, so it depends on common HAL types and the shared Wi-Fi 7 register/API contract. It is consumed by `hal.c` and implemented by `hal_qcc2072.c`.

## Risks

- The header lacks its own include guard, unlike `hal_qcn9274.h`; repeated inclusion currently depends on included headers being safe.
- Exposed offset helpers must stay synchronized with `struct hal_rx_desc_qcc2072`; stale offsets would break descriptor parsing.
- Because this header only exports a minimal surface, any new QCC2072-specific helper needed by shared code must be added deliberately rather than relying on static functions in the `.c` file.

## Test Signals

Build tests should include repeated inclusion and all QCC2072 call sites. Runtime signals are indirect: successful QCC2072 HAL selection, descriptor offset consumers parsing correct MPDU start/MSDU end locations, and RX traffic without descriptor misalignment symptoms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcc2072.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcn9274.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcn9274.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcn9274.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcn9274.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_rx.c

## Purpose

`hal_rx.c` implements common Wi-Fi 7 RX and REO helper logic for ath12k. It encodes REO commands, decodes REO status descriptors, handles RX buffer/link descriptor address fields, parses REO/WBM error descriptors, sizes and initializes REO queue descriptors, initializes REO command rings, and programs basic REO hardware behavior.

## Important APIs and Functions

- REO command encoding: `ath12k_wifi7_hal_reo_cmd_send()`, `ath12k_wifi7_hal_reo_cmd_queue_stats()`, `ath12k_wifi7_hal_reo_cmd_flush_cache()`, and `ath12k_wifi7_hal_reo_cmd_update_rx_queue()`.
- Descriptor address helpers: `ath12k_wifi7_hal_rx_buf_addr_info_set()`, `ath12k_wifi7_hal_rx_buf_addr_info_get()`, `ath12k_wifi7_hal_rx_reo_ent_paddr_get()`, and `ath12k_wifi7_hal_rx_reo_ent_buf_paddr_get()`.
- RX list/link helpers: `ath12k_wifi7_hal_rx_msdu_link_info_get()`, `ath12k_wifi7_hal_rx_msdu_list_get()`, and `ath12k_wifi7_hal_rx_msdu_link_desc_set()`.
- Error parsing: `ath12k_wifi7_hal_desc_reo_parse_err()` and `ath12k_wifi7_hal_wbm_desc_parse_err()`.
- REO status decoding: queue stats, flush queue, flush cache, unblock cache, flush timeout list, descriptor threshold reached, and update RX queue status functions.
- REO queue setup: `ath12k_wifi7_hal_reo_qdesc_size()` and `ath12k_wifi7_hal_reo_qdesc_setup()`.
- Command ring initialization: `ath12k_wifi7_hal_reo_init_cmd_ring_tlv64()` and `ath12k_wifi7_hal_reo_init_cmd_ring_tlv32()`.
- Hardware setup: `ath12k_wifi7_hal_reo_hw_setup()` and `ath12k_wifi7_hal_reo_shared_qaddr_cache_clear()`.

## Control Flow

REO command submission locks the source ring, begins SRNG access, obtains the next entry, encodes the selected command, ends access, and unlocks. Queue stats encode queue address and optional clear/status flags. Flush cache optionally reserves a blocking resource using `ffz(hal->avail_blk_resource)` and `hal->current_blk_index`, then encodes cache address, forward/flush/block flags, and 1K descriptor handling. Update RX queue encodes a large set of update-enable bits and new values, normalizes PN size values of 24/48/128 into hardware enums, and clamps BA window size to hardware expectations.

RX descriptor parsing flows decode DMA addresses and software cookies from `ath12k_buffer_addr`. REO error parsing validates push reason, updates `dp->device_stats.reo_error[err_code]`, extracts the link descriptor bank from the cookie, and returns the physical address. WBM error parsing distinguishes normal and hardware-cookie-converted release formats, verifies descriptor type and return buffer manager, fills `hal_rx_wbm_rel_info`, and captures source-specific push reason/error code.

REO status handlers decode uniform command number/status first and then populate the matching `struct hal_reo_status` union payload. Flush/unblock cache status also updates `hal->avail_blk_resource` based on the current blocking resource index.

REO queue descriptor setup writes a REO-owned descriptor header, queue number, valid/link counter/access category, BA window size, PN policy, ignore-AMPDU flag, optional SSN, and extension descriptor headers for QoS TIDs. Command ring initialization pre-fills each entry's command number for TLV64 or TLV32 layouts.

`ath12k_wifi7_hal_reo_hw_setup()` enables REO aging/flush, routes fragment and BAR frames to REO2SW0, programs aging thresholds, and writes destination ring hash maps. `ath12k_wifi7_hal_reo_shared_qaddr_cache_clear()` toggles the clear bit in the queue descriptor address register under `dp->dp_lock`.

## State and Persistence

The file mutates `hal->avail_blk_resource`, `hal->current_blk_index`, REO command ring entries, REO queue descriptors, RX/WBM release info, DP error counters, SRNG producer/consumer state, and REO hardware registers. It reads/writes DMA-visible descriptor memory in little-endian form and uses spinlocks around command-ring access. Persistent hardware state includes REO aging enablement, destination ring routing, aging thresholds, hash maps, and queue descriptor cache clear toggling.

## Dependencies and Integration Points

It depends on common ath12k debug/HAL/HIF headers, Wi-Fi 7 `hal_tx.h`, `hal_rx.h`, `hal_desc.h`, and `hal.h`. It integrates with chip-specific `hal->ops->reo_cmd_enc_tlv_hdr()` implementations, SRNG access helpers, DP lock/state, device stats, and upper RX/TID management that allocates and updates REO queue descriptors.

## Risks

- Unsupported REO commands (`FLUSH_QUEUE`, `UNBLOCK_CACHE`, `FLUSH_TIMEOUT_LIST`) return `-EOPNOTSUPP` from the send path even though status decoders exist; callers must not assume full command support.
- Blocking resource accounting uses a single `current_blk_index`; overlapping flush/unblock operations may be fragile if multiple commands are outstanding.
- `ath12k_wifi7_hal_reo_flush_timeout_list_status()` reads `FWD_BUF_COUNT` from `desc->info0` while the mask is named for `INFO1`, suggesting a possible decode bug.
- `ath12k_wifi7_hal_rx_msdu_list_get()` modifies `rx_msdu_info.info0` in the link descriptor to force first/last flags while building software lists.
- WBM error parsing expects `HAL_RX_BUF_RBM_SW3_BM`; chips with different RX buffer RBM policy must ensure `hal_params` and hardware release descriptors agree.
- Queue descriptor setup always initializes three extension descriptors for QoS TIDs despite size calculation supporting more cases; allocation and initialization policy must remain consistent with callers.

## Test Signals

Key tests include REO command-ring exhaustion (`-ENOBUFS`), queue stats/flush cache/update queue command encoding, blocking resource exhaustion (`-ENOSPC`), REO/WBM error descriptor parsing with valid and invalid RBMs, RX MSDU list extraction for empty, single, multi-MSDU, and continuation cases, REO queue descriptor setup across BA window sizes and TIDs, TLV32/TLV64 command ring initialization, and REO hardware setup register readback. Lockdep should cover `ath12k_wifi7_hal_reo_shared_qaddr_cache_clear()` under `dp_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_rx.c -->
