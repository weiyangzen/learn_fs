# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 12636-15195

## Purpose

This chunk is generated DCN 3.2 register field metadata for AMD display hardware. It provides `_SHIFT` and `_MASK` constants for packed bitfields inside DPP and MPC registers. The constants are consumed by AMDGPU Display Core register helper macros to populate shift/mask tables, allowing higher-level display code to update individual hardware fields through `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers without hard-coding bit positions.

The covered range starts in the tail of DPP1 color-management gamma-correction RAM B region descriptors, then defines the complete DPP2 and DPP3 converter/scaler/color-management/top masks, and ends in the beginning of MPC MPCC0/MPCC1 composition masks.

## Important Definitions

- `CM1_CM_GAMCOR_RAMB_REGION_28_29` through `CM1_CM_GAMCOR_RAMB_REGION_32_33` encode final DPP1 gamma-correction RAM B region descriptors. Each paired region register uses low and high half-word layouts: LUT offset fields at bits `0` and `16`, and segment-count fields at bits `12` and `28`.
- `CM1_CM_HDR_MULT_COEF`, `CM1_CM_MEM_PWR_CTRL`, `CM1_CM_MEM_PWR_STATUS`, `CM1_CM_DEALPHA`, `CM1_CM_COEF_FORMAT`, and `CM1_CM_TEST_DEBUG_*` expose DPP1 post-color-management controls for HDR multiplication, gamma RAM power, alpha handling, coefficient format, and indexed debug access.
- `DPP_TOP1_DPP_*`, `DPP_TOP2_DPP_*`, and `DPP_TOP3_DPP_*` expose per-DPP top-level clock gating, soft reset, CRC value, CRC control, and host-read-rate fields. The CRC control fields include enable, continuous/one-shot behavior, source selection, stereo/interlace/pixel/cursor format selection, and a 16-bit CRC mask.
- `CNVC_CFG2_*` and `CNVC_CFG3_*` define input converter configuration for DPP2/DPP3: surface pixel format, alpha-plane enable, format conversion and bypass, positive clamping, channel crossbar routing, floating-point bias/scale, color-key ranges, 2-bit alpha LUT entries, pre-dealpha, pre-CSC mode/coefficient matrices, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR2_*` and `CNVC_CUR3_*` define cursor composition fields: cursor mode, expansion, enable, pixel-invert mode, pixel alpha modulation, ROM enable, two cursor colors, and cursor floating-point scale/bias.
- `DSCL2_*` and `DSCL3_*` define DPP2/DPP3 scaler fields: coefficient RAM tap select/data, scaler mode, tap counts, two-tap sharpness controls, manual replication, horizontal/vertical luma and chroma scale ratios and initial phases, black color, update/autocal fields, overscan, OTG blanking windows, recout and MPC sizes, line-buffer format/memory controls, v-counter, scaler LUT memory power, output-buffer control, and output-buffer memory power.
- `CM2_*` and `CM3_*` define color-management fields for DPP2/DPP3: CM bypass/current status, post-CSC and gamut remap mode plus A/B coefficient matrices, bias, gamma-correction LUT index/data/control, RAM A/B start/end/slope/base/offset fields, 34 region split descriptors per RAM, HDR multiplier, CM memory power, dealpha, coefficient format, and test debug index/data.
- `MPCC0_*` and the beginning of `MPCC1_*` define MPC composition fields: top/bottom pipe selection, OPP target ID, blending mode, alpha mode, premultiplied-alpha mode, overlap-only blending, background bits-per-component, bottom-gain mode, global alpha/gain, stereo-mode controls, update-lock selection and status, top/bottom gains, movable CM location, background color, output-gamma memory power, and MPCC idle/busy/disabled status.

There are no C functions or runtime types in this chunk. Its public API is the generated preprocessor namespace itself: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants.

## Control Flow

The file does not execute control flow. Its effect occurs at compile time:

1. DCN 3.2 source files include `dcn/dcn_3_2_0_sh_mask.h` together with matching offset headers.
2. Component headers such as `dc/dpp/dcn30/dcn30_dpp.h` and `dc/mpc/dcn32/dcn32_mpc.h` use field-list macros (`TF_SF(...)`, `SF(...)`) to reference the generated `_SHIFT` and `_MASK` symbols.
3. Resource setup code instantiates `struct dpp_shift`, `struct dpp_mask`, `struct mpc_shift`, `struct mpc_mask`, and related register tables from those macro lists.
4. Runtime display code uses the populated tables when programming planes, cursors, scalers, color transforms, gamma LUTs, CRC capture, memory-power controls, and MPCC blending.

The repeated instance prefixes (`CNVC_CFG2`, `DSCL2`, `CM2`, `DPP_TOP2`; then `...3`) represent separate hardware pipes. Higher-level code usually writes through instance-aware register lists, so the bit layouts must remain consistent across instances even when register addresses differ in the offset header.

## State And Persistence

These macros describe MMIO register state, not kernel-owned persistent storage. The state persists in display hardware registers until reprogrammed, reset, power-gated, or lost across suspend/resume and GPU reset flows. Several fields explicitly interact with hardware state transitions:

- `*_MEM_PWR_CTRL` and `*_MEM_PWR_STATUS` fields control or report low-power behavior for gamma LUT RAMs, scaler LUT memory, OBUF memory, and MPCC output-gamma memory.
- `*_UPDATE_PENDING`, `*_MODE_CURRENT`, `SCL_COEF_RAM_SELECT_CURRENT`, and `MPCC_UPDATE_LOCKED_STATUS` fields expose double-buffered or latched hardware state that may differ from the requested value until an update point.
- Gamma LUT and scaler coefficient programming is indirect for several blocks: index/control/data fields select RAM banks, write masks, host access, color lanes, and coefficient taps before payload data is written.
- CRC value registers are observation state generated by hardware from selected DPP sources.

Because this header only supplies bit positions, persistence correctness depends on the call sites sequencing register writes, update locks, memory power requests, and reads of current/status fields correctly.

## Dependencies And Integration Points

- Depends on matching generated DCN 3.2 offset definitions, especially `dcn_3_2_0_offset.h`, for the register addresses corresponding to these field layouts.
- Included by DCN 3.2 display components such as `dc/resource/dcn32/dcn32_resource.c`, IRQ, GPIO, clock manager, and DMUB code.
- DPP field masks integrate mainly through DPP macro lists in `dc/dpp/dcn10/dcn10_dpp.h` and descendants such as `dc/dpp/dcn30/dcn30_dpp.h`. Those lists use the instance-0 names as canonical field layouts, while resource register lists map concrete per-instance addresses.
- MPCC masks integrate through `dc/mpc/dcn10/dcn10_mpc.h`, `dc/mpc/dcn30/dcn30_mpc.h`, and `dc/mpc/dcn32/dcn32_mpc.h`, where `MPC_COMMON_MASK_SH_LIST_DCN32` pulls MPCC blending, movable CM, status, and memory-power fields into typed mask/shift tables.
- DPP top CRC registers also integrate with hardware-sequencer diagnostics and CRC capture paths; DCN resource code registers DPP CRC control/value registers for debug and validation.

## Risks

- Any incorrect shift or mask silently writes the wrong bits in MMIO registers, which can cause display corruption, wrong color conversion, scaler artifacts, cursor failures, broken CRC validation, or power-management instability.
- These generated constants are tightly coupled to silicon register specs. Manual edits are risky unless mirrored in the matching offset and field-list consumers.
- Instance-copy errors are high impact. DPP2 and DPP3 blocks are structurally repetitive, so a single stale field layout in one instance can break only specific pipes or monitor configurations.
- LUT and coefficient fields are especially sensitive: wrong region offsets, segment counts, host-select bits, or write masks can corrupt gamma curves and color output while leaving the driver apparently functional.
- Memory-power force/disable/state masks can race with programming if call sites do not wait for power state before writing RAM-backed LUT/coefficient blocks.
- Status/current fields should not be treated as writable requests. Confusing requested and current fields can make update-lock or double-buffer sequencing unreliable.

## Test Signals

- Build-level: compile AMDGPU display code for DCN 3.2 targets with `dcn_3_2_0_sh_mask.h` included; unresolved macro names or struct initializer failures catch missing/renamed fields.
- Static consistency: compare DPP2/DPP3 field layouts against DPP0/DPP1 and against generated DCN offset headers for the same ASIC generation; repeated blocks should have identical field masks where hardware instances are identical.
- Display validation: exercise multiple DPP pipes with scaling, cursor enable/disable, alpha formats, color keying, pre/post CSC, gamut remap, HDR multiplier, and gamma LUT updates.
- CRC/debug: enable DPP CRC one-shot and continuous modes and confirm stable expected CRC values across source selections and pixel formats.
- Power-management: run suspend/resume, display idle, memory power-gating, and GPU reset tests while programming CM, DSCL, OBUF, and MPCC RAM-backed blocks.
- Multi-plane composition: validate MPCC top/bottom selection, global alpha/gain, stereo-mode controls, background color, update-lock behavior, and idle/busy/disabled status with several overlay and pipe-split configurations.
