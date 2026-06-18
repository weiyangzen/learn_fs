# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 9904-12415

## Scope

This chunk is a generated AMD DCN 3.0.3 ASIC register bitfield header segment. It contains preprocessor constants only: hardware register fields are represented by a `__SHIFT` macro for the bit offset and a `_MASK` macro for the field mask. The assigned range spans 2,512 source lines, with 2,113 `#define` entries, 1,055 shift definitions, 1,066 mask definitions, and 385 register/comment anchors.

The range starts in the middle of `CM0_CM_GAMCOR_RAMA_REGION_14_15` and ends on the `CM1_CM_GAMCOR_RAMB_REGION_32_33` comment before that register's fields. The merge lane must stitch adjacent chunks before treating either boundary group as complete.

## Purpose

The purpose of this header segment is to expose symbolic bit positions for DCN 3.0.3 display pipeline programming in the AMDGPU display driver. It is included with the matching DCN 3.0.3 offset header so register helper macros can construct MMIO read-modify-write operations without embedding raw bit constants in driver logic.

The covered register surface is concentrated on DPP pipe 0 color management, DPP0 performance monitoring, and the beginning of DPP pipe 1:

- tail of `CM0` gamma-correction RAM-A region programming.
- `CM0` gamma-correction RAM-B, blend-gamma RAM-A/RAM-B, shaper RAM-A/RAM-B, CM memory power, dealpha, coefficient format, 3D LUT, and debug fields.
- `DC_PERFMON7` DPP0 performance counter control, state, interrupt, and value readback fields.
- `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, and a large prefix of `CM1` display-pipe fields for DPP1.

This source is data-like rather than executable. Runtime behavior is indirect: the constants must match AMD's hardware register specification and the companion `dcn_3_0_3_offset.h` address definitions.

## Address Blocks And Register Surface

Visible address blocks and implied surfaces:

- The opening lines continue the `dce_dc_dpp0_dispdec_cm_dispdec` color-management block from the previous chunk. This range covers `CM0_CM_GAMCOR_*`, `CM0_CM_BLNDGAM_*`, `CM0_CM_HDR_MULT_COEF`, `CM0_CM_MEM_PWR_*`, `CM0_CM_DEALPHA`, `CM0_CM_COEF_FORMAT`, `CM0_CM_SHAPER_*`, `CM0_CM_3DLUT_*`, and CM test-debug fields.
- `dce_dc_dpp0_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON7` performance counter selection, state, perfmon control, interrupt/status, and counter value low/high registers for DPP0.
- `dce_dc_dpp1_dispdec_dpp_top_dispdec`: `DPP_TOP1` clock, gating, reset, CRC, and host-read control fields.
- `dce_dc_dpp1_dispdec_cnvc_cfg_dispdec`: `CNVC_CFG1` source pixel format, format conversion, floating-point scale/bias, color keying, alpha, pre-dealpha, pre-CSC, coefficient format, pre-degamma, and pre-realpha fields.
- `dce_dc_dpp1_dispdec_cnvc_cur_dispdec`: `CNVC_CUR1` cursor enable/mode/color/floating-point scale-bias fields.
- `dce_dc_dpp1_dispdec_dscl_dispdec`: `DSCL1` scaler coefficient RAM, scaler mode/taps/ratios/inits, black color, update/autocal, overscan, blanking, recout/MPC dimensions, line-buffer memory, DSCL memory power, OBUF control, and OBUF memory power fields.
- `dce_dc_dpp1_dispdec_cm_dispdec`: starts `CM1` color-management controls and proceeds through post-CSC, gamut remap, bias, gamma-correction controls, gamma RAM-A/RAM-B region programming, and the start of the next blend-gamma section outside this chunk.

## Important Macros And Register Families

`CM0_CM_GAMCOR_RAMA_*` and `CM0_CM_GAMCOR_RAMB_*` define DPP0 gamma-correction piecewise-linear RAM programming. The range starts with the tail of RAM-A `REGION_14_15`, then continues RAM-A region descriptors through `REGION_32_33`. RAM-B includes per-channel start controls, start slope/base controls, end controls, offsets, and paired region descriptors from `REGION_0_1` through `REGION_32_33`. The repeated region registers pack two PWL regions per 32-bit register: LUT offsets use masks such as `0x000001FFL` and `0x01FF0000L`; segment counts use `0x00007000L` and `0x70000000L`.

`CM0_CM_BLNDGAM_*` mirrors the gamma-correction shape for blend gamma. It includes mode/select/current-state bits, LUT index/data/control, RAM-A and RAM-B start/end/offset/region descriptors, and the same two-regions-per-register encoding used by gamma correction. `CM_BLNDGAM_PWL_DISABLE`, color write masks, read color selection, host selection, and config mode are the key control fields.

`CM0_CM_SHAPER_*` defines DPP0 shaper LUT control and region programming. The shaper block includes offset/scale fields for R/G/B, indexed LUT access, a write-enable mask register, RAM-A/RAM-B start and end controls, and paired RAM region descriptors. Unlike the gamma/blend RAM-B end controls, shaper RAM-B end controls pack end and end-base fields rather than the end-slope split used by the other PWL blocks.

`CM0_CM_MEM_PWR_CTRL`, `CM0_CM_MEM_PWR_STATUS`, `CM0_CM_MEM_PWR_CTRL2`, and `CM0_CM_MEM_PWR_STATUS2` expose memory power control and state for gamma/blend, shaper, and HDR 3D LUT memories. These fields are force/disable/state bits, not standalone policy.

`CM0_CM_3DLUT_*` exposes DPP0 3D LUT programming: mode, size, current mode, index, 16-bit paired data, 30-bit data access, RAM selection, write-enable mask, read selection, output normalization, and RGB output offset/scale. `CM0_CM_TEST_DEBUG_INDEX` and `CM0_CM_TEST_DEBUG_DATA` provide indexed debug access.

`DC_PERFMON7_*` defines DPP0 performance-monitor controls. `PERFCOUNTER_CNTL` selects event, counted value, increment mode, hardware control source, run-enable mode, restart, interrupt, off-mask behavior, active state, and counter selector. `PERFCOUNTER_CNTL2` selects counted value type, hardware stop inputs, counter-off source, and counter-control selector. `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` cover per-counter state, report count, counter-off interrupt status/ack, clock enable, run start/stop source selection, and value readback.

`DPP_TOP1_*` defines top-level DPP1 controls: DPP clock enable, static/dynamic clock-gate disables, DSCL gate disable, DISPCLK/DPPCLK gating, test clock selection, soft-reset bits for CNVC/DSCL/CM/OBUF, CRC value registers, CRC enable/one-shot/status/source/pixel-format/cursor-format/mask fields, and host-read rate control.

`CNVC_CFG1_*` defines the DPP1 converter configuration path before scaling and color management. It covers surface pixel format, alpha-plane enable, expansion mode, 16-bit conversion, CNVC bypass/MSB alignment, positive clamps, update-pending status, RGB crossbar selection, floating-point bias/scale, color-keyer enable/alpha and RGB low/high thresholds, four-entry 2-bit alpha LUT, pre-dealpha, pre-CSC mode/current mode, primary and alternate pre-CSC matrices, coefficient format, pre-degamma mode/select, and pre-realpha.

`CNVC_CUR1_*` is the DPP1 cursor subset: cursor0 enable, expansion mode, pixel inversion, ROM enable, cursor mode, pixel-alpha modulation, update-pending status, two 24-bit cursor colors, and floating-point scale/bias.

`DSCL1_*` defines DPP1 scaler and line-buffer programming. Coefficient RAM fields select tap pair, phase, filter type, and even/odd tap data with enable bits. The scaler mode/tap/ratio/init fields configure luma/chroma scale ratios and initial phases, coefficient RAM bank/current/readback selection, chroma/alpha coefficient modes, two-tap sharp/hardcoded behavior, manual replicate factors, black color, update state, autocal pipe selection, overscan, OTG blanking, recout/MPC dimensions, line-buffer interleave/alpha, line-buffer partition counts, vertical counters, DSCL memory power, OBUF behavior, and OBUF memory power.

`CM1_CM_*` begins the DPP1 color-management block. This range includes global bypass/update-pending, post-CSC mode/current state and A/B 3x4 matrix fields, gamut-remap mode/current state and A/B 3x4 matrices, bias fields, gamma-correction mode/LUT/control, and most gamma RAM-A/RAM-B PWL region programming. The chunk ends before `CM1_CM_GAMCOR_RAMB_REGION_32_33` fields are listed, so the following chunk is needed for the complete RAM-B region table and subsequent blend/shaper/3D LUT CM1 fields.

## Control Flow And Runtime Behavior

There is no C control flow in this chunk. Runtime control flow is represented by hardware programming sequences that consume these bit masks through AMDGPU register helper macros.

The likely hardware flows represented here are:

- DPP0 color-management programming: driver code loads gamma correction, blend gamma, shaper, and 3D LUT state by programming mode/select fields, indexed LUT data registers, PWL region descriptors, and output normalization/offset registers.
- DPP0 performance monitoring: diagnostic or profiling code selects events and counter modes through `DC_PERFMON7_*`, enables clock/run conditions, handles counter-off/per-counter interrupts, and reads high/low counter values.
- DPP1 pipe bring-up and reset: `DPP_TOP1_DPP_CONTROL` and `DPP_TOP1_DPP_SOFT_RESET` enable the DPP clock, manage gating, and reset CNVC, DSCL, CM, and OBUF subblocks.
- DPP1 conversion and cursor setup: `CNVC_CFG1_*` and `CNVC_CUR1_*` select surface format, alpha/keying behavior, pre-CSC/pre-degamma transforms, cursor mode, and cursor colors.
- DPP1 scaling and viewport setup: `DSCL1_*` programs coefficient RAM, scale ratios, filter inits, taps, output sizes, overscan, line-buffer partitions, memory power, and output-buffer state.
- DPP1 color-management setup: `CM1_CM_*` fields in this chunk establish post-CSC, gamut remap, bias, gamma-correction control, and a partial gamma PWL RAM table.

## State And Persistence

The macros themselves hold no mutable state and allocate no storage. They describe fields in hardware MMIO registers. Writes through these fields persist in the display hardware until another write, block reset, GPU reset, suspend/resume restore, or mode-set reprogramming occurs.

Important state classes represented by this chunk:

- Double-buffer/current-state fields: `*_UPDATE_PENDING`, `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `SCL_COEF_RAM_SELECT_CURRENT`, and `SCL_COEF_RAM_SELECT_RD` expose the difference between requested and currently latched hardware state.
- Indexed RAM state: `CM*_GAMCOR_LUT_INDEX`, `CM*_GAMCOR_LUT_DATA`, `CM*_BLNDGAM_LUT_INDEX`, `CM*_BLNDGAM_LUT_DATA`, `CM0_CM_SHAPER_LUT_*`, `CM0_CM_3DLUT_*`, and `DSCL1_SCL_COEF_RAM_*` are address/data style interfaces. The selected index, RAM bank, host/config mode, color write mask, and read selector are stateful context for subsequent accesses.
- Piecewise-linear curve descriptors: gamma, blend-gamma, and shaper RAM-A/RAM-B region registers persist LUT offsets and segment counts. These descriptors must match the indexed LUT data layout loaded elsewhere.
- Matrix and bias state: CNVC pre-CSC, CM post-CSC, CM gamut-remap, and bias fields persist color transform state and can affect every pixel through the pipe.
- Power state: CM, DSCL, line-buffer, and OBUF memory power fields can force, disable, or report subblock memory state. These interact with active scanout and power management rather than behaving as ordinary display parameters.
- Interrupt and diagnostic state: perfmon interrupt status/ack fields, CRC status/value fields, line-buffer counters, and CM debug registers expose hardware state that may be latched or write-one-to-clear depending on the underlying register semantics. The header does not encode those semantics.

## Dependencies And Integration Points

This chunk depends on companion generated DCN 3.0.3 headers for register addresses and base indices, especially `dcn_3_0_3_offset.h`. Consumers combine register names and field names through macros such as `FD_MASK`, `FD_SHIFT`, `REG_OFFSET`, `SF`, and `TF_SF` to populate per-block register tables and issue MMIO operations.

Concrete include points for `dcn_3_0_3_sh_mask.h` include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`, where the DCN 3.0.3 resource layer includes the offset and mask headers while constructing display resources.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c`, where DMUB register tables use `FD_MASK` and `FD_SHIFT` arrays derived from this header.
- `drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c`, where interrupt service code includes the same register definitions.

Functional integration points include:

- DPP resource construction and DPP helper tables that bind generic DPP0/DPP1 field names to instance-specific register offsets and masks.
- Color-management code that programs transfer functions, gamma/blend-gamma PWL curves, shaper curves, post-CSC/gamut matrices, bias, HDR multiplier, and 3D LUT contents.
- Scaler code that programs DSCL coefficient RAM, taps, ratios, initial phases, recout/MPC dimensions, line-buffer partitioning, OBUF behavior, and overscan.
- Cursor and conversion paths that program CNVC format, alpha/keying, pre-dealpha/pre-realpha, pre-CSC, pre-degamma, and cursor registers.
- Diagnostics and profiling paths that use DPP CRC, DC perfmon, DSCL counters, and CM test-debug interfaces.
- Power-management and suspend/resume paths that restore DPP subblock memory power state and indexed LUT contents.

Because this is a generated public include within the AMDGPU display tree, compile-time consumers are sensitive to exact macro spelling. A missing or renamed macro can break builds, and an incorrect mask or shift can silently program the wrong hardware bits.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask can corrupt neighboring fields in a 32-bit MMIO register, causing display blanking, bad color transforms, scaling artifacts, cursor defects, incorrect perfmon data, or power-management regressions.
- The range starts and ends mid-register-family. `CM0_CM_GAMCOR_RAMA_REGION_14_15` starts before line 9904, and `CM1_CM_GAMCOR_RAMB_REGION_32_33` fields are outside the range. File-level conclusions must merge adjacent chunks.
- Repeated PWL RAM region tables are easy to misgenerate. Gamma, blend-gamma, and shaper RAM A/B blocks use many near-identical `REGION_N_N+1` macros, so an off-by-two region, channel swap, RAM A/B swap, or missing final region would be hard to detect by inspection.
- Several field names include the word `MASK`, producing generated names such as `CM0_CM_SHAPER_LUT_WRITE_EN_MASK__CM_SHAPER_LUT_WRITE_EN_MASK_MASK` and `PERFCOUNTER_OFF_MASK_MASK`. Parsers that split naively on `_MASK` can misclassify these fields.
- Indexed RAM programming is order-sensitive. Losing the intended index, RAM select, 30-bit mode, read selector, color write mask, or host/config mode can corrupt LUT contents even if each bitfield constant is individually correct.
- Status, current-mode, update-pending, interrupt-status, and ack fields have hardware-specific semantics not represented by the macros. Callers must rely on the block programming sequence and hardware documentation, not just the mask constants.
- Memory-power fields can interact with active scanout. Forcing or disabling CM, DSCL, line-buffer, OBUF, shaper, gamma/blend, or HDR3DLUT memories at the wrong time can produce visual corruption, stale LUT data, underflow, or hangs.
- The constants are DCN 3.0.3-specific. Reusing them for nearby DCN revisions because names appear similar risks subtle register layout mismatches.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware/display regression signals:

- AMDGPU DCN 3.0.3 compile coverage catches missing or renamed macros used by resource tables, DMUB register tables, IRQ code, DPP/DSCL/CM helpers, and perfmon helpers.
- Generated-header checks should verify that every complete field has both `__SHIFT` and `_MASK`, masks fit within 32 bits, repeated RAM-region families retain expected offsets and segment-count positions, and chunk boundaries are reconciled by adjacent chunks.
- Display mode-set tests should exercise DPP1 clock/reset, CNVC pixel formats, alpha/keying, cursor modes, DSCL scaling ratios/taps/coefficient RAM, recout/MPC sizing, line-buffer partitioning, and OBUF behavior.
- Color-management tests should cover DPP0 and DPP1 gamma correction, DPP0 blend gamma, DPP0 shaper LUTs, DPP0 3D LUT mode/data paths, post-CSC, gamut remap, bias, bypass/current-mode readbacks, and update-pending handshakes.
- Power tests should cover suspend/resume and runtime power transitions for CM gamma/blend/shaper/HDR3DLUT memories, DSCL LUT/LB banks, and OBUF memory.
- Diagnostic tests should compare DPP CRC output, `DC_PERFMON7` counter programming/readback, perfmon interrupt acknowledgement, DSCL vertical counters, and CM debug-index/data behavior against expected hardware results.

## Open Questions For Merge Lane

- Confirm the previous chunk contains the beginning of `CM0_CM_GAMCOR_RAMA_REGION_14_15` and the earlier `CM0` gamma-control fields needed to describe the complete gamma-correction block.
- Confirm the next chunk contains `CM1_CM_GAMCOR_RAMB_REGION_32_33` fields and the remainder of the `CM1` blend-gamma, shaper, memory-power, 3D LUT, and debug surface.
- Identify the exact DCN 3.0.3 DPP/DSCL/CM register table macros that consume the `CM0`, `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, `CM1`, and `DC_PERFMON7` fields before the final per-file report names call sites.
