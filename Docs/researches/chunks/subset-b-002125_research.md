# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 17537-20052

## Purpose

This chunk is a generated AMD DCN 3.6.0 register shift/mask header segment. It contains 2,099 preprocessor definitions and no executable C code. The macros describe bit positions and masks for fields in display color-management, DPP instance 3, DC performance monitor blocks, MPC/MPCC composition blocks, and MPCC output-gamma/gamut-remap blocks.

Consumers combine these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants with register offsets from the matching `dcn_3_6_0_offset.h` header and AMD display register helpers. The values are hardware ABI data: build-time names may compile successfully while an incorrect bit number or mask silently programs the wrong MMIO field at runtime.

## Important API surface

There are no functions or types in this range. The public surface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit for a hardware field.
- `REGISTER__FIELD_MASK` gives the packed field mask in the 32-bit register value.
- Driver-side register table macros and access helpers use these names through `FD_SHIFT`, `FD_MASK`, `SF`, `SE_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and related AMD DC MMIO helper patterns.

The major field groups are:

- `CM3_CM_GAMCOR_RAMB_REGION_16_17` through `CM3_CM_GAMCOR_RAMB_REGION_32_33`, followed by `CM3_CM_HDR_MULT_COEF`, `CM3_CM_MEM_PWR_CTRL`, `CM3_CM_MEM_PWR_STATUS`, `CM3_CM_DEALPHA`, `CM3_CM_COEF_FORMAT`, `CM3_CM_TEST_DEBUG_INDEX`, `CM3_CM_TEST_DEBUG_DATA`, and `CM3_DPP_CRC_VAL_*`. These cover the tail of DPP3 color-management gamma-correction RAM B region descriptors, HDR multiplier, gamma-correction memory power control/status, dealpha controls, coefficient-format selection, CM test/debug index/data, and DPP CRC result channels.
- `DPP_TOP3_DPP_CONTROL`, `DPP_TOP3_DPP_SOFT_RESET`, `DPP_TOP3_DPP_CRC_CTRL`, and `DPP_TOP3_HOST_READ_CONTROL` in address block `dce_dc_dpp3_dispdec_dpp_top_dispdec`. These expose DPP3 clock-enable/gating/test-clock fields, per-subblock soft reset for CNVC/DSCL/CM/OBUF, DPP CRC source/format/mask/stereo/interlace/one-shot controls, and host-read throttling.
- `DC_PERFMON14_*` for DPP3 perfmon. The fields describe performance-counter event selection, counted-value selection, increment and run-enable modes, counter restart/interrupt/off-mask/active status, counter state for eight counters, perfmon run state/report count, counter-off interrupt control/status/ack, run-enable start/stop sources, current-value high/low fragments, and read selectors.
- `MPCC0` through `MPCC3` base composition fields in address blocks `dce_dc_mpc_mpcc[0-3]_dispdec`. Each instance has top/bottom input selection, OPP routing, blend mode, alpha mode, premultiplied-alpha mode, active-overlap-only blend, background bits-per-component, bottom gain mode, global alpha/gain, stereo-mixer control/status, update-lock selection/status, top and bottom gains, movable color-management location, background RGB/YCbCr components, OGAM memory power control/state, and idle/busy/disabled status.
- MPC-wide fields in `dce_dc_mpc_mpc_cfg_dispdec`: `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, `MPC_CRC_CTRL`, `MPC_CRC_SEL_CONTROL`, `MPC_PERFMON_EVENT_CTRL`, bypass background color registers, host-read control, DPP and OPP/MPCC/DWB pending-status registers, four vertical-update lock-set register families, MPC CRC result channels, and `MPC_DWB0_MUX`.
- `DC_PERFMON15_*` for MPC perfmon, structurally matching the DPP perfmon fields but attached to the MPC block.
- `MPCC_OGAM0` and `MPCC_OGAM1` full output-gamma/gamut-remap groups, plus `MPCC_OGAM2` from control through RAMB region `26_27`. These include OGAM mode/select/current status, PWL disable, LUT index/data/control, RAM A and RAM B PWL start/end/base/slope/offset fields per RGB channel, packed region descriptors for region pairs 0-33, coefficient format, gamut-remap mode/current status, and A/B coefficient-bank pairs such as `C11_C12`, `C13_C14`, `C21_C22`, `C23_C24`, `C31_C32`, and `C33_C34`.

## Control flow and data flow

This header has no runtime control flow. Its data flow is compile-time expansion into ASIC-specific register tables and MMIO read/modify/write operations:

1. DCN 3.6 display code includes `dcn_3_6_0_offset.h` and this `dcn_3_6_0_sh_mask.h` file.
2. Resource, DMUB, IRQ, DPP, MPC, MPCC, color-management, CRC, and perfmon register-list macros select register offsets and the corresponding field shifts/masks for the DCN 3.6 ASIC.
3. Runtime paths pack desired field values by shifting them into the masked bit positions, then write the resulting 32-bit values through AMDGPU/DC register helpers.
4. Status and diagnostic paths read MMIO registers, mask and shift fields back to logical values, and use them for polling, debug output, CRC validation, performance monitoring, update synchronization, and display pipeline decisions.

For DPP3 and CM fields, the runtime programming is driven by color-management and DPP setup paths. Gamma-correction RAM region descriptors, coefficient formats, dealpha controls, and HDR multiplier values define how pixels are transformed before they leave DPP3. DPP CRC fields are used by validation and debug flows that select a source/format and then read per-channel CRC result registers.

For MPC/MPCC fields, plane composition code configures which DPP feeds each MPCC top/bottom input, which OPP receives the composed result, how alpha and global gain are applied, and when update locks allow register changes to take effect. MPC pending-status fields provide synchronization signals around DPP surface/config/cursor updates, OPP updates, MPCC updates, and DWB updates.

For MPCC OGAM and gamut-remap fields, color-management paths program the output transfer function through LUT index/data/control registers, RAM A/B region descriptors, and per-channel PWL boundary/slope/offset registers. Gamut-remap code programs matrix coefficients in A/B banks and selects the active mode/bank through the control fields.

## State and persistence

The macros themselves have no state. They describe hardware-resident state that persists until overwritten, reset, power-gated, or reinitialized by modeset/resume/firmware flows:

- DPP3 clock, gate-disable, test-clock, soft-reset, host-read, and CRC-control fields affect the operating state and diagnostics of DPP instance 3.
- CM3 gamma-correction and coefficient fields define color pipeline state. RAM region descriptors and LUT-related state can produce visible color shifts if programmed partially or with stale values.
- Memory power fields such as `GAMCOR_MEM_PWR_FORCE`, `GAMCOR_MEM_PWR_DIS`, `GAMCOR_MEM_PWR_STATE`, `MPCC_OGAM_MEM_PWR_FORCE`, `MPCC_OGAM_MEM_PWR_DIS`, `MPCC_OGAM_MEM_LOW_PWR_MODE`, and `MPCC_OGAM_MEM_PWR_STATE` reflect or control local RAM power behavior.
- MPCC selection, OPP ID, blend mode, alpha/gain, background color, stereo-mixer, and movable color-management location fields define active plane-composition state.
- Update-lock and pending-status fields are synchronization state. They gate or report when register writes are latched relative to vertical update windows and pipeline update sequencing.
- Perfmon control, state, current-value, interrupt status, and ack fields are diagnostic state. Counter values and interrupt bits change as hardware events occur.
- CRC result registers expose frame-dependent diagnostic data and are timing-sensitive when one-shot or continuous modes are toggled.

## Dependencies and integration points

- This header must be paired with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`; the masks/shifts alone do not identify MMIO addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` include the DCN 3.6 offset and shift/mask headers for ASIC-specific resource, DMUB, and IRQ setup.
- DPP and color-management implementations rely on the `CM3_*` and `DPP_TOP3_*` fields for DPP instance 3 color transforms, memory power behavior, reset, clock control, and CRC diagnostics.
- MPC/MPCC implementations rely on `MPCC[0-3]_*`, `MPC_*`, and `MPCC_OGAM[0-2]_*` fields for plane blending, routing to OPPs, update locking, CRC capture, writeback muxing, output gamma, and gamut remap.
- Perfmon consumers rely on `DC_PERFMON14_*` and `DC_PERFMON15_*` for event selection, counter control, current-value reads, interrupt status/ack, and run-enable trigger selection.
- Generated spelling is an integration point. Register table macros assume exact register and field names; missing or renamed macros fail builds, while numeric drift can survive compilation and surface as display corruption, failed synchronization, invalid CRCs, or broken performance diagnostics.

## Risks and edge cases

- The requested range starts in the middle of the `CM3_CM_GAMCOR_RAMB_REGION_14_15` group and ends in the middle of the `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_26_27` group. Adjacent chunks are required before the final per-file report can treat those families as complete.
- Repeated instance blocks are copy/generator sensitive. `MPCC0` through `MPCC3`, `DC_PERFMON14` versus `DC_PERFMON15`, and `MPCC_OGAM0` through `MPCC_OGAM2` should remain structurally consistent except for intentional instance numbering and chunk boundaries.
- Packed PWL region fields are high risk: LUT offsets use 9-bit masks, segment counts sit at bits 12-14 and 28-30 in packed region-pair registers, start segment fields use high bits around bit 20, start/base/slope/offset fields use 18- or 19-bit masks, and end/slope pairs split 16-bit halves. A single shift or width error corrupts gamma/output transfer programming.
- Some registers mix control, status, pending, interrupt, and ack fields. Read/modify/write paths must avoid clearing status or acking interrupts unintentionally.
- Soft-reset and clock-gating fields can destabilize active display pipes if written outside the expected sequencing windows.
- CRC one-shot pending and update-lock/pending-status bits are timing-sensitive. Tests that only read idle-state registers may miss races during modeset, page flip, cursor update, writeback, or stereo/interlace changes.
- Perfmon interrupt status/ack and current-value high/low reads can race with counter updates unless read sequences follow the hardware programming model.
- Cross-generation similarity is risky. Nearby DCN 3.x and DCN 4.x headers have similarly named MPCC, MPC, DPP, CM, OGAM, and perfmon fields, but masks and field availability can differ; consumers must not mix offset/mask headers across ASIC versions.

## Test signals

- Build coverage with DCN 3.6 enabled should catch missing macro names when resource, DMUB, IRQ, DPP, MPC, MPCC, OGAM, and perfmon register tables instantiate these fields.
- Static generated-header checks should verify that every field has a matching shift and mask, masks have the expected width after shifting, repeated instance blocks are structurally aligned, and chunk-boundary registers reconcile with adjacent ranges.
- Cross-version diffing against AMD's authoritative register database and nearby generated headers should show intentional DCN 3.6 changes, especially for `DPP_FGCG_REP_DIS`, MPCC/OGAM memory power fields, perfmon fields, and packed PWL region layouts.
- Runtime DPP/color tests should exercise DPP3 gamma/output color changes, HDR multiplier and coefficient-format selection, dealpha behavior, gamma-correction memory power sequencing, reset/resume, and per-channel DPP CRC capture.
- Runtime MPC/MPCC tests should cover multi-plane composition, top/bottom source changes, OPP routing, alpha blending, global alpha/gain, background color, movable color-management location, update locks, pending-status polling, DWB0 mux selection, and MPC CRC one-shot/continuous modes.
- Runtime color-management tests should update MPCC OGAM LUTs and PWL region descriptors across MPCC OGAM instances 0-2, switch A/B gamut-remap coefficient banks, and verify visible output or CRC signatures across modeset and suspend/resume.
- Perfmon tests should configure DPP3 and MPC perfmon events, verify counter increments/current-value reads, exercise run-enable start/stop selection, and validate interrupt status/ack handling without disrupting display.
