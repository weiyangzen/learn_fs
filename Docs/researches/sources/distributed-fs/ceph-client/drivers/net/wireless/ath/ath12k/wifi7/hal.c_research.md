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
