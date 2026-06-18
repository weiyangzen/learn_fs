# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 22626-25141

## Scope

This chunk covers lines 22626-25141 of the generated AMD DCN 3.1.5 shift/mask header. It is entirely preprocessor register metadata: 2,104 `#define` entries across 2,516 source lines, with 1,053 `__SHIFT` constants and 1,058 `_MASK` constants plus generated register and `addressBlock` comments. There are no functions, structs, enums, variables, includes, allocation paths, locks, or executable statements in this range.

The range starts in the middle of `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_4_5` with its final masks, then covers the tail of MPCC OGAM instance 2, the complete visible MPCC OGAM instance 3 block, MPC output mux/output CSC/denorm masks, MPC RMU global and RMU instance 0/1 shaper and 3DLUT masks, ABM0 backlight and adaptive backlight statistics masks, and the beginning of ABM1. It ends mid-register at `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS`; the masks and clear fields for that register continue in the next chunk.

## Purpose

The purpose of this header slice is to publish exact bit positions and masks for DCN 3.1.5 display hardware registers. AMDGPU display code combines these constants with the matching `dcn_3_1_5_offset.h` addresses and register helper macros to pack MMIO writes, perform read-modify-write updates, and decode status fields without embedding raw bit positions in driver logic.

This is a generated hardware contract. Runtime behavior is implemented by consumers such as DCN315 resource construction, MPC color-management code, ABM/backlight code, DMUB, IRQ, and GPIO setup paths. This file only supplies the field layout that those consumers paste into `REG_*`, `FD_SHIFT`, and `FD_MASK` style helpers.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within a 32-bit register value.
- `//<REGISTER>` comments group fields for one logical register.
- `// addressBlock: ...` comments group registers by decoded hardware block.

Major constant families in this chunk include:

- `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_6_7` through `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_32_33`, plus `MPCC_OGAM2_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM2_MPC_GAMUT_REMAP_*`, covering the tail of MPCC output-gamma RAMB region descriptors and MPCC gamut remap matrix programming for coefficient banks A and B.
- `MPCC_OGAM3_MPCC_OGAM_*`, covering output gamma control, LUT index/data/control, RAMA/RAMB start, slope, base, end, offset, region descriptor, and gamut remap fields for MPCC instance 3.
- `MPC_OUT0_*` through `MPC_OUT3_*`, covering MPC output mux selection, rate/flow-control fields, denorm mode and RGB/YCbCr clamp fields, output CSC coefficient format, CSC mode, and paired 16-bit CSC matrix coefficients for banks A and B.
- `MPC_RMU_CONTROL` and `MPC_RMU_MEM_PWR_CTRL`, covering RMU enable and memory-power controls.
- `MPC_RMU0_*` and `MPC_RMU1_*`, covering shaper control, per-channel offset/scale, shaper LUT index/data/write-enable, RAMA/RAMB region descriptors, 3DLUT mode/index/data/read-write controls, 30-bit data packing, output normalization, and output offset/scale fields.
- `ABM0_BL1_PWM_*` and `ABM1_BL1_PWM_*`, covering ambient/user/target/current/final/minimum PWM levels, ABM enable and auto-update controls, backlight-update sample rate, group register locking, and frame-start update selection.
- `ABM0_DC_ABM1_*` and the beginning of `ABM1_DC_ABM1_*`, covering ABM enable/bypass, IPS color-space coefficient select, ACE slope/offset and threshold programming, HGLS read-progress status, histogram/luma-stat sampling controls, luma-stat counters, histogram bin shift/index registers, histogram result registers, and backlight master lock.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN315 code includes `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Resource-table macros such as `SRII`, `SRII_MPC_RMU`, `MPC_REG_LIST_DCN3_0`, `MPC_OUT_MUX_REG_LIST_DCN3_0`, `MPC_RMU_REG_LIST_DCN3AG`, and ABM register-list macros resolve register addresses from the offset header.
3. Field-list macros paste register and field names into `__SHIFT` and `_MASK` symbols from this header to initialize per-block shift/mask tables.
4. Runtime code calls register helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_SET_3`, `REG_GET`, `REG_GET_2`, `REG_WAIT`, and direct `REG_WRITE`/`REG_READ`; those helpers use the populated masks and shifts to access hardware fields.

The declaration order mirrors hardware organization. MPCC OGAM and RMU blocks intentionally duplicate nearly identical field layouts per instance so instance-indexed resource tables can map each MPCC/RMU to the correct hardware symbols.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes bit locations for state in DCN 3.1.5 display registers.

Writable fields in this range can program MPCC output gamma and gamut remap state, MPC output routing and color conversion, RMU shaper and 3D LUT state, RMU memory power behavior, PWM backlight state, ABM enable/bypass, ACE curve parameters, histogram/luma-stat sampling cadence, and ABM lock/update behavior. These programmed values persist according to the underlying display block power and reset domains, and can be lost or reinitialized across modesets, display block reset, suspend/resume, GPU reset, or ASIC reset.

Hardware-updated fields expose current OGAM/gamut modes, MPC output status, RMU memory power state, ABM current/final levels, update-pending flags, read-progress flags, missed-frame flags, luma-stat observations, histogram results, and lock/update status. Access type, reset values, read-clear behavior, write-one-to-clear behavior, and required polling sequences are not encoded here.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.5 register offset header for MMIO addresses. The shift/mask header says how to pack fields; the offset header says where each register lives. Mixing this file with a different DCN generation is risky because many register and field names are structurally similar while addresses or bit layouts can diverge.

Primary integration points include:

- `display/dc/resource/dcn315/dcn315_resource.c`, which includes the DCN 3.1.5 offset and mask headers and constructs `mpc_regs`, `mpc_shift`, and `mpc_mask` using DCN3 MPC, output mux, and RMU register-list macros. The chunk's MPC/MPCC/RMU symbols feed `dcn30_mpc_construct()`.
- `display/dc/mpc/dcn30/dcn30_mpc.[ch]`, where MPCC OGAM fields are used to power OGAM LUT memory, select RAM A/B, load output gamma LUTs, read current OGAM state, and program gamut/output CSC state through register helpers.
- `display/dc/dce/dce_abm.[ch]` and `display/dc/dce/dmub_abm_lcd.c`, where ABM masks drive initialization of histogram/luma-stat sample rates, IPS coefficient selection, PWM levels, luma thresholds, missed-frame clear fields, and current/target backlight reads.
- DCN315 DMUB, IRQ, and GPIO code that includes the same generated header for their own generated register tables, even though most fields in this particular line range are consumed by MPC and ABM paths.
- Higher-level color-management and modeset paths that select MPCC OGAM, gamut remap, output CSC, shaper, and 3DLUT programming through the MPC abstraction rather than using these macros directly.

## Risks And Edge Cases

- The chunk starts mid-register. The shift definitions and earlier masks for `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_4_5` are in the previous chunk; this range only contains the last four masks for region 4/5.
- The chunk ends mid-register. `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS` has only six shift definitions here; its masks and any later clear/status fields continue in the next chunk.
- Several register families are copy-sensitive: MPCC OGAM2 versus OGAM3, MPC_OUT0-3, RMU0 versus RMU1, and ABM0 versus ABM1 have mostly repeated field layouts. A generator drift or copy error can compile while routing a field to the wrong hardware instance.
- Some runtime code uses only a subset of the generated region registers. For example, generic DCN3 MPC register lists name `MPCC_OGAM_RAMA_REGION_0_1` and `32_33` directly for PWL programming, while this chunk also exposes all intermediate region pairs. Whole-file analysis should avoid assuming every generated macro is actively used by the current driver.
- Control and status bits are often adjacent. Examples include OGAM current-mode fields near programmed-mode fields, RMU memory power control/status, ABM update-pending/readback/lock bits, and ABM missed-frame clear/status bits. Consumers must preserve unrelated bits and follow hardware sequencing that this header does not document.
- Full-width histogram and LUT data masks use `0xFFFFFFFFL`, while many packed coefficients use paired 16-bit fields. Incorrect signedness or width assumptions in consumers would not be caught by the header itself.
- ABM backlight fields are 17-bit PWM values, while some driver paths convert from or to user-facing brightness and BIOS scratch state. Mask errors here can produce visibly wrong brightness, stuck ramping, or stale current/target backlight reads.
- RMU shaper and 3DLUT programming is color-critical. Wrong offsets, segment counts, RAM bank selection, 30-bit packing, or output normalization fields can cause subtle color corruption that may only appear with nontrivial HDR/3D LUT workloads.

## Test Signals

Useful validation is mostly build-time consistency plus hardware integration:

- Build AMDGPU display code for a DCN315-enabled configuration to catch missing, renamed, or mismatched macros used by generated register-helper expansion.
- Mechanically verify that complete registers in this line range have matching `__SHIFT` and `_MASK` symbols for each field, while accounting for the partial first and last registers.
- Compare this slice against the authoritative DCN 3.1.5 register database and the matching offset header to ensure each `addressBlock`, register name, field name, shift, and mask aligns.
- Exercise MPCC output gamma and gamut remap programming across MPCC instances 2 and 3, including RAM A/B switching, bypass/current-mode reads, nontrivial PWL transfer functions, and gamut matrices in coefficient banks A and B.
- Exercise MPC output mux, denorm, and output CSC paths for all four MPC outputs, checking modeset, color conversion, and clamp behavior.
- Exercise RMU shaper and 3DLUT programming on RMU instances 0 and 1 with 1D shaper curves, 3D LUT writes/reads, 30-bit data mode, memory power transitions, and HDR/color-management workloads.
- Exercise ABM and backlight flows through both legacy DCE ABM and DMUB ABM paths: ABM initialization, PWM user/current/target/final levels, fractional PWM, sample-rate programming, luma thresholds, missed-frame clear, histogram/luma-stat reads, panel on/off, suspend/resume, and brightness ramping.
- Watch for stuck update-pending/read-progress bits, missed-frame flags, incorrect histogram bins, unexpected luma-stat values, RMU memory power wait failures, visible gamma/color artifacts, and backlight values outside the expected 17-bit hardware range.

## Open Cross-Chunk Notes

The merge lane should combine this chunk with the previous chunk to describe `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_4_5` completely. It should combine this chunk with the next chunk for the complete `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS` register and the remainder of ABM1. Whole-file analysis should reconcile this chunk with neighboring DCN 3.1.5 generated-header chunks before making final claims about the complete MPCC OGAM, MPC OCSC/RMU, and ABM register coverage of `dcn_3_1_5_sh_mask.h`.
