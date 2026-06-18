# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 2511-4961

## Purpose

This chunk is a generated AMD DCE 12.0 register shift/mask section. It contains no executable code; it defines preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for memory-mapped display-engine registers. Consumers use these constants with the paired DCE 12.0 register-address headers and AMDGPU/DC register access helpers to compose, read, update, and decode 32-bit MMIO register fields.

The covered range starts at the tail of `DCE_VERSION` and then covers a large block of display clock generator (`DCCG`) and pixel-rate controls, frame buffer compression (`FBC`), display pipe and DSI/DCFEV power gating, display memory interface (`DMIF`) arbitration and buffering, DCI memory/clock/power controls, DVMM page-table and fault controls, DCHUB aperture/status registers, writeback/capture (`WB`/`CNV`) and writeback scaler (`WBSCL`) controls, and the beginning of the display microcontroller (`DMCU`) firmware/RAM/interrupt register block. The chunk ends mid-register at `DMCU_INTERRUPT_TO_UC_EN_MASK__VBLANK3_INT_TO_UC_EN__SHIFT`; the remaining masks and any subsequent DMCU fields must be reconciled with the following chunk.

## Important APIs, Types, and Register Domains

The public API surface is entirely macro names. There are no functions, structs, enums, storage declarations, or inline helpers in this range.

Major macro groups:

- DCE/DCCG timing and clocking: `DCE_VERSION`, `PHYPLLG_PIXCLK_RESYNC_CNTL`, `PHYPLLF_PIXCLK_RESYNC_CNTL`, `PIXCLK0/1/2_RESYNC_CNTL`, `DCCG_GTC_*`, `DENTIST_DISPCLK_CNTL`, `MILLISECOND_TIME_BASE_DIV`, `MICROSECOND_TIME_BASE_DIV`, `DISPCLK_FREQ_CHANGE_CNTL`, `DCCG_PERFMON_CNTL`, `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DISPCLK_CGTT_BLK_CTRL_REG`, `SCLK_CGTT_BLK_CTRL_REG`, `SYMCLK_CGTT_BLK_CTRL_REG`, `DCCG_SOFT_RESET`, `SYMCLKA` through `SYMCLKF_CLOCK_ENABLE`, `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO0/1_PHASE`, and `DCCG_AUDIO_DTO0/1_MODULE`.
- CRTC and link-rate DTO programming: repeated `CRTC0` through `CRTC5_PIXEL_RATE_CNTL`, `DP_DTO0` through `DP_DTO5_PHASE/MODULO`, and `CRTC0` through `CRTC5_PHYPLL_PIXEL_RATE_CNTL` fields select pixel-rate sources, enable DP DTOs, apply add/drop pixel correction, report DISP output FIFO errors, and select PHYPLL/pixel-rate PLL sources.
- Legacy and panel clock helpers: `MIPI_DTO_*`, `DAC_CLK_ENABLE`, `DVO_CLK_ENABLE`, `DVOACLKC/DVOACLKD_*`, `AVSYNC_COUNTER_*`, `SMU_CONTROL`, `SMU_INTERRUPT_CONTROL`, and `DMCU_SMU_INTERRUPT_CNTL`.
- Frame buffer compression: `FBC_CNTL`, `FBC_IDLE_FORCE_CLEAR_MASK`, `FBC_START_STOP_DELAY`, `FBC_COMP_CNTL`, `FBC_COMP_MODE`, `FBC_IND_LUT0` through `FBC_IND_LUT15`, CSM region offsets, client region masks, `FBC_DEBUG_COMP`, `FBC_MISC`, `FBC_STATUS`, `FBC_ALPHA_CNTL`, and `FBC_ALPHA_RGB_OVERRIDE`.
- Power gating and power interrupts: repeated `PIPE0` through `PIPE5_PG_CONFIG/ENABLE/STATUS`, `DSI_PG_*`, `DCFEV0_PG_*`, `DCFEV1_PG_*`, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_CONTROL`, `DCPG_INTERRUPT_CONTROL2`, `DC_IP_REQUEST_CNTL`, and `DC_PGCNTL_STATUS_REG`.
- Display memory interface and arbitration: `DMIFV_STATUS`, `DMIF_CONTROL`, `DMIF_STATUS`, `DMIF_ARBITRATION_CONTROL`, `PIPE0` through `PIPE7_ARBITRATION_CONTROL3`, `DMIF_P_VMID`, `DMIF_ADDR_CALC`, `DMIF_STATUS2`, `PIPE0` through `PIPE7_MAX_REQUESTS`, `LOW_POWER_TILING_CONTROL`, `MCIF_CONTROL`, `MCIF_WRITE_COMBINE_CONTROL`, phase outstanding counters, `CC_DC_PIPE_DIS`, `SMU_WM_CONTROL`, `RBBMIF_TIMEOUT`, `RBBMIF_STATUS`, `RBBMIF_TIMEOUT_DIS`, `RBBMIF_STATUS_FLAG`, and `DMIF_URG_OVERRIDE`.
- DCI clocking, memory power, and reset: `DCI_CLK_CNTL`, `DCI_CLK_CNTL2`, `DCI_MEM_PWR_CNTL`, `DCI_MEM_PWR_CNTL2`, `DCI_MEM_PWR_CNTL3`, `DCI_MEM_PWR_CNTL4`, `DCI_MEM_PWR_STATUS`, `DCI_MEM_PWR_STATUS2`, `DCI_MEM_PWR_STATUS3`, and `DCI_SOFT_RESET`.
- DVMM and DCHUB address translation: `DVMM_REG_RD_STATUS`, `DVMM_REG_RD_DATA`, `DVMM_PTE_REQ`, `DVMM_CNTL`, `DVMM_FAULT_STATUS`, `DVMM_FAULT_ADDR`, `FMON_CTRL`, `DVMM_PTE_PGMEM_CONTROL`, `DVMM_PTE_PGMEM_STATE`, and DCHUB framebuffer, AGP, DRAM aperture, and control/status fields.
- Writeback/capture and scaler: `WB_ENABLE`, `WB_EC_CONFIG`, `CNV_MODE`, `CNV_WINDOW_START`, `CNV_WINDOW_SIZE`, `CNV_UPDATE`, `CNV_SOURCE_SIZE`, `CNV_CSC_*`, `CNV_TEST_*`, `CNV_INPUT_SELECT`, `WB_SOFT_RESET`, `WB_WARM_UP_MODE_CTL1/2`, `WBSCL_COEF_RAM_SELECT`, `WBSCL_COEF_RAM_TAP_DATA`, `WBSCL_MODE`, `WBSCL_TAP_CONTROL`, destination size, horizontal/vertical scale ratios and initial phases, round/clamp, overflow and coefficient-conflict interrupts, outside-pixel strategy, test CRCs, backpressure counter, MCIF backpressure counter, and RAM shutdown.
- Display microcontroller: `DMCU_CTRL`, `DMCU_STATUS`, firmware start/end/ISR/checksum address fields, host access to ERAM/IRAM through `DMCU_RAM_ACCESS_CTRL` plus read/write control/data registers, event trigger bits, `DMCU_UC_INTERNAL_INT_STATUS`, static-screen interrupt control/status, `DMCU_INTERRUPT_STATUS`, `DMCU_INTERRUPT_TO_HOST_EN_MASK`, and the first part of `DMCU_INTERRUPT_TO_UC_EN_MASK`.

## Control Flow and State Behavior

This header has no runtime control flow. The control flow exists in driver consumers that perform read-modify-write sequences against MMIO registers using these shift/mask definitions. The field names reveal several state machines and sequencing contracts:

- Clock changes use toggle/done/status fields such as `DENTIST_DISPCLK_CHGTOG`, `DENTIST_DISPCLK_DONETOG`, `DENTIST_DISPCLK_CHG_DONE`, DP reference clock change bits, and `DISPCLK_FREQ_RAMP_DONE`. Callers must program divider/source fields and then poll or sequence against completion bits.
- Pixel-rate programming is replicated per CRTC. `CRTCn_PIXEL_RATE_SOURCE`, `DP_DTOn_ENABLE`, DTO phase/modulo, add/drop pixel correction, half-rate output, FIFO-error, and error-count fields are tied to mode-set and link-clock programming order.
- Power gating has force-on, gate request, desired state, and PGFSM status fields for pipes, DSI, and DCFEV blocks. Interrupt status/control registers expose power-up/down occurrence, mask, and clear bits, so callers need explicit clear-after-observe behavior.
- FBC state is persistent in hardware until disabled, invalidated, reset, or fault-cleared. Control fields enable compression, select compressor behavior, define memory regions/LUTs, and expose decompression error and enable-status bits.
- DMIF, MCIF, DCI, DVMM, and DCHUB fields control request throttling, VMID assignment, buffer allocation, outstanding request counters, memory power states, address apertures, page-table request generation, fault status, and hub credit errors. Incorrect programming can affect display fetch, writeback, and memory translation across multiple pipes.
- Writeback/capture uses update-lock style fields (`CNV_UPDATE_PENDING`, `CNV_UPDATE_TAKEN`, `CNV_UPDATE_LOCK`), window/source geometry, CSC coefficient registers, scaler coefficient RAM selection/tap data, and CRC/overflow/host-conflict interrupt fields. These are stateful programming surfaces where geometry, filter coefficients, and enable bits should be latched coherently.
- DMCU control includes microcontroller reset/enable, IRQ/XIRQ routing, register-read timeout, firmware address/checksum fields, ERAM/IRAM host access with auto-increment and select bits, event trigger fields, and interrupt occurrence/clear/enable masks. Host code must treat RAM access and interrupt clear bits as register protocol operations, not ordinary RAM variables.

Persistence is hardware-register persistence only. The macros allocate no memory and maintain no software state; after consumers write MMIO registers, the state lives in the display engine until later register writes, resets, power transitions, or firmware actions change it.

## Dependencies and Integration Points

The chunk depends on generated-name compatibility with the rest of `dce_12_0_sh_mask.h` and companion DCE 12.0 register address/offset headers under the AMD ASIC register tree. Numeric values are coupled to AMD DCE 12.0 hardware documentation and to existing AMDGPU/DC register helper conventions that expect `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names.

Primary integration points:

- AMDGPU display clock and link programming uses the DCCG, DENTIST, DTO, pixel-rate, PHYPLL, symbol-clock, DAC/DVO/MIPI, and AV sync fields during mode set, link bring-up, and display clock changes.
- Power-management paths use SMU, DMCU-SMU, display memory global power request, DCPG interrupt, pipe/DSI/DCFEV power-gate, DCI clock-gate, memory power, and soft-reset fields.
- Plane fetch and memory arbitration use DMIF/MCIF/DCI/DVMM/DCHUB fields for VMID, address aperture, tiling, request bursts, urgent levels, outstanding counters, low-power tiling, page-table requests, memory power state, and fault diagnostics.
- FBC code uses the FBC control/status/misc/LUT/region/alpha fields to enable compression, tune compressor behavior, handle invalidation or decompression faults, and validate enable/compression status.
- Writeback and capture paths use WB/CNV/WBSCL controls for capture enable, crop/window/source geometry, stereo/interlace capture metadata, CSC, scaling coefficients, CRC testing, backpressure counters, and writeback RAM power controls.
- DMCU firmware loading and event handling code uses DMCU reset/enable/status, PC/firmware/checksum registers, IRAM/ERAM host-access fields, event triggers, and interrupt routing/clear masks for microcontroller-managed display features such as ABM/static-screen handling and power-event notification.

## Risks and Edge Cases

- The constants are a hardware ABI. A one-bit shift or mask change can silently corrupt unrelated fields in a shared 32-bit MMIO register.
- Many registers use negative polarity or control-by-disable naming, such as `*_GATE_DISABLE`, `*_MEM_PWR_DIS`, `*_DS_DISABLE`, `DISABLE_IRQ_TO_UC`, and `PSTATE_URGENT_DISABLE`. Call sites must not infer polarity from a generic enable/disable helper without checking field meaning.
- Clear and occurrence bits often share the same bit position and mask, especially in `DMCU_INTERRUPT_STATUS`, `DMCU_UC_INTERNAL_INT_STATUS`, and static-screen interrupt status. Read/modify/write helpers must avoid preserving stale write-one-to-clear bits.
- Interrupt mask fields have repeated names ending in `_MASK_MASK`, for example `DCPG_INTERRUPT_CONTROL__DCFE0_POWER_UP_INT_MASK_MASK` and `DMCU_INTERRUPT_TO_HOST_EN_MASK__..._MASK_MASK`. This is generated but visually error-prone when grepping or wrapping macros.
- Several repeated per-pipe families are not perfectly symmetric across all display blocks. The chunk covers pipes 0-5 for power gating and DMIF buffer controls, pipes 0-7 for some arbitration/max-request/DVMM PTE state fields, and DCFEV/DSI special cases. Generic loops in consumers need validated register lists, not just a pipe count assumption.
- `DCCG_AUDIO_DTO0_MODULE` and `DCCG_AUDIO_DTO1_MODULE` use `MODULE` rather than the more common `MODULO`; this generated spelling must be preserved for source compatibility.
- This range starts after the first `DCE_VERSION__MAJOR_VERSION__SHIFT` line and ends before the full `DMCU_INTERRUPT_TO_UC_EN_MASK` register definition completes. The final merged per-file research should join adjacent chunks before making claims about complete DCE version or DMCU interrupt-to-UC coverage.
- DCHUB aperture, DVMM fault, VMID, and memory-power fields influence memory access behavior. Misprogramming can produce display underflow, stale translations, invalid requests, or faults that look unrelated to the original register write.

## Test Signals

Useful validation is mostly compile-time plus hardware/display behavior:

- Kernel or targeted AMDGPU header builds should catch missing macro names, syntax errors, duplicate definitions, and generated-name drift.
- Static checks can verify that representative shifts/masks match expected bit positions for DCCG clock controls, `CRTCn_PIXEL_RATE_CNTL`, `DCPG_INTERRUPT_CONTROL`, `DMIF_CONTROL`, `DCI_MEM_PWR_CNTL*`, `DVMM_CNTL`, `CNV_UPDATE`, `WBSCL_OVERFLOW_STATUS`, and `DMCU_INTERRUPT_STATUS`.
- Mode-set tests should exercise display clock changes, DP DTO programming, PHYPLL source selection, pixel add/drop correction, and DISP output FIFO error reporting across multiple CRTCs.
- Power-management tests should cover pipe/DSI/DCFEV power gating, DCPG interrupt clear/mask paths, SMU/DMCU static-screen events, clock gating, DCI memory power transitions, and soft resets.
- Memory-fetch and writeback tests should check DMIF buffer allocation/completion, arbitration/urgent settings, VMID/aperture setup, DVMM PTE and fault reporting, DCHUB credit error handling, FBC enable/invalidate/error paths, and MCIF/writeback backpressure counters.
- Capture/scaler validation should cover CNV window/source sizing, CSC coefficients and clamps, update lock/taken/pending sequencing, WBSCL coefficient RAM programming, overflow/host-conflict interrupts, CRC outputs, and scaled writeback image correctness.
- DMCU tests should verify firmware start/checksum programming, ERAM/IRAM host access auto-increment behavior, event trigger delivery, interrupt-to-host and interrupt-to-UC masks, write-one-to-clear interrupt behavior, and register-read timeout reporting.
