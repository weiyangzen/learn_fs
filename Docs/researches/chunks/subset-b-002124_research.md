# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 14997-17536

## Scope

This chunk covers a generated AMD DCN 3.6 register shift/mask header slice. It contains 2,114 `#define` entries over 2,540 lines, split almost evenly between `__SHIFT` constants and `_MASK` constants. The covered region starts in the tail of DPP instance 1 color-management gamma-correction RAM-B fields, then covers DPP instance 2 configuration, scaler, color-management, top, CRC, and perfmon fields, and ends partway through DPP instance 3 color-management gamma-correction RAM-B region definitions.

The file is data-only: it declares preprocessor constants for hardware register bitfields and contains no C functions, structs, storage allocation, or executable control flow.

## Purpose

The constants describe bit positions and bit masks for DCN 3.6 display pipe processor (DPP) register fields. They are consumed by the AMD display driver register-helper layer to populate shift and mask tables used by `REG_SET`, `REG_UPDATE`, `REG_GET`, and wait/poll helpers. Correctness is hardware-contract correctness: each constant must match the corresponding ASIC register definition in `dcn_3_6_0_offset.h` and the DCN 3.x DPP programming code.

Major hardware areas in this chunk:

- `CM1`, `CM2`, and `CM3`: color management, including post-CSC, gamut remap, bias, gamma-correction LUT host access, gamma-correction piecewise-linear region descriptors, HDR multiplier, dealpha, coefficient format, memory power control/status, debug, and DPP CRC result fields.
- `CNVC_CFG2` and `CNVC_CFG3`: converter surface format, format control, fixed-point bias/scale, color keying, alpha LUT, pre-dealpha, pre-CSC matrix programming, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR2` and `CNVC_CUR3`: cursor enable/mode, color registers, and cursor floating-point scale/bias.
- `DSCL2` and `DSCL3`: display scaler coefficient RAM access, scaler mode, taps, 2-tap sharpness control, manual replication, scale ratios, initial phases, black color, update/autocal, overscan, OTG blanking geometry, recout/MPC size, line-buffer format and memory control, memory power state, and output-buffer power/control.
- `DPP_TOP1` and `DPP_TOP2`: DPP clock gates, dynamic gate disables, fine-grain clock-gating repeat disable, soft reset bits for CNVC/DSCL/CM/OBUF, DPP CRC control, and host-read throttling.
- `DC_PERFMON12` and `DC_PERFMON13`: DPP-local display performance monitor counter selection, state, control, counter-value readback, interrupt status/ack, high/low value registers, and read selectors.

## Important Definitions

This chunk follows the standard register-field naming pattern:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned field mask.
- Instance prefixes such as `CM2_`, `CNVC_CFG3_`, `DSCL2_`, and `DPP_TOP2_` bind otherwise repeated register layouts to a hardware DPP instance.

Notable field groups:

- Gamma correction RAM descriptors use `RAMA` and `RAMB` banks with mirrored field shapes: start control, start slope/base, end base/slope, offsets, and paired `REGION_N_N+1` descriptors. Region pairs pack two LUT offsets and segment counts into one register: low region offset at bits 0-8, low region segment count at bits 12-14, high region offset at bits 16-24, high region segment count at bits 28-30.
- CSC and gamut-remap matrix registers pack two 16-bit coefficients per register, with first coefficient in bits 0-15 and second in bits 16-31. The `_B_` suffixed copies provide alternate/banked coefficient sets.
- Format and color-conversion controls expose enable/bypass/state bits (`CNVC_BYPASS`, `ALPHA_EN`, `CNVC_UPDATE_PENDING`, `PRE_CSC_MODE_CURRENT`, `PRE_DEGAM_MODE`, `PRE_REALPHA_EN`) that higher-level plane programming uses to synchronize pixel format and color pipeline changes.
- DSCL geometry fields use packed X/Y or width/height values, generally low component in bits 0-12 or 0-13 and high component in bits 16-28 or 16-29.
- Memory-power controls expose force/disable fields and status/state fields for gamma correction memory, scaler LUT/line-buffer groups, and OBUF memory. These are used by power sequencing paths that may poll state after changing force bits.
- CRC controls define one-shot/continuous operation, source select, stereo/interlace/pixel/cursor format selection, and a 16-bit CRC mask. CRC value registers expose full 32-bit R/G/B/A channel results.
- Perfmon definitions include eight per-counter interrupt status/ack bits, counter run/stop selection, counted-value type, active state, high/low counter value readback, and threshold/interrupt control fields.

## Control Flow

There is no runtime control flow in this header. Its effective control flow is through compile-time macro expansion in DCN resource setup:

- `dcn36_resource.c` includes both `dcn_3_6_0_offset.h` and this `dcn_3_6_0_sh_mask.h`.
- `dcn36_resource.c` constructs `tf_shift` with `DPP_REG_LIST_SH_MASK_DCN35(__SHIFT)` and `tf_mask` with `DPP_REG_LIST_SH_MASK_DCN35(_MASK)`.
- `DPP_REG_LIST_SH_MASK_DCN35` extends the DCN 3.0 common DPP field list and uses `TF_SF(...)` entries to refer to symbols from this header, such as `CM0_CM_GAMCOR_CONTROL__CM_GAMCOR_MODE__SHIFT` or `DSCL0_SCL_MODE__DSCL_MODE_MASK`. For instances 2 and 3, equivalent generated definitions in this chunk must remain layout-compatible with the common instance-0 macro pattern because the register table initialization substitutes instance-specific register addresses while sharing the same field layouts.
- Runtime DPP code under `display/dc/dpp/` uses the populated shift/mask tables through register-helper macros, so a bad bit definition here turns into incorrect read-modify-write behavior rather than an obvious local compile-time control-flow error.

## State and Persistence

The header itself persists no state. It describes hardware state in MMIO registers. State affected by these fields lives in display hardware until overwritten, reset, power-gated, or reprogrammed during modeset/plane-update paths.

Important state classes:

- Color-pipeline programming state: CNVC format controls, pre-CSC/pre-degamma/pre-realpha, CM post-CSC, gamut-remap, bias, HDR multiplier, dealpha, and gamma-correction LUT regions.
- Double-buffer/current-state indicators: fields such as `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `CNVC_UPDATE_PENDING`, `CUR0_UPDATE_PENDING`, `SCL_UPDATE_PENDING`, and `CM_UPDATE_PENDING` expose or coordinate pending hardware updates.
- Memory power state: `GAMCOR_MEM_PWR_STATE`, `LUT_MEM_PWR_STATE`, `LB_G*_MEM_PWR_STATE`, and `OBUF_MEM_PWR_STATE` reflect power-management state machines.
- Diagnostic state: CRC values and perfmon counters are readback state used for validation, telemetry, and debugging.

Because this is an ASIC register contract, persistence risks come from stale or mismatched constants: an incorrect mask may silently preserve stale bits, clear unrelated hardware state, or poll the wrong state field.

## Dependencies and Integration Points

Primary dependencies:

- `dcn_3_6_0_offset.h` provides register addresses and base-index macros; this file provides field layout for those addresses.
- `display/dc/resource/dcn36/dcn36_resource.c` includes this header and instantiates DPP shift/mask tables.
- `display/dc/dpp/dcn35/dcn35_dpp.h` defines the DPP mask/shift list shape used by DCN36 resource setup.
- `display/dc/dpp/dcn30/dcn30_dpp.h`, `dcn20_dpp.h`, and `dcn10_dpp.h` define common DPP field lists and the register helper field expectations that many entries in this chunk satisfy.
- `reg_helper.h` and the register access macros consume the populated shift/mask structs for MMIO read/write operations.

Integration expectations:

- Instance-specific symbols must exist for every DPP instance present in the offset table. This chunk contributes instance 2 and 3 symbols and the tail of instance 1 symbols.
- Register field names must match the names used in common DPP macro lists. Renaming a generated define without updating macro lists causes build failures; changing a numeric value without a name change causes runtime hardware misprogramming.
- The generated `L`-suffixed constants are intended as 32-bit masks despite C's platform-dependent `long` width; consumers store them in `uint32_t` mask fields.

## Risks

- Hardware layout drift: DCN 3.6 may differ subtly from DCN 3.5/3.2 even when the common DPP field-list macros are reused. Missing or stale generated masks can produce incorrect color conversion, scaling, cursor, CRC, or power behavior.
- Banked gamma LUT programming is dense and repetitive. Region pairs, RAMA/RAMB bank selection, and RGB channel suffixes are easy to misalign in generated output. A single region mask error can corrupt transfer-function programming for only part of the curve.
- Power-management fields are high impact. Incorrect `*_MEM_PWR_FORCE`, `*_MEM_PWR_DIS`, or status masks can leave memories powered down during programming or cause waits to poll unrelated bits.
- Update-pending/current fields are synchronization-sensitive. Bad masks for `CNVC_UPDATE_PENDING`, `SCL_UPDATE_PENDING`, `CM_UPDATE_PENDING`, or `*_CURRENT` fields can cause code to assume a programming update has landed when hardware has not latched it.
- Perfmon and CRC fields are often test/debug only, so regressions may escape normal functional display tests unless CRC/perf telemetry paths are exercised.
- This generated header has duplicate-looking layouts across DPP instances. Manual edits are risky because local consistency does not prove ASIC correctness; generated-source provenance should be preserved.

## Test Signals

Useful validation signals for changes touching this chunk:

- Build the AMDGPU display driver with DCN36 enabled; missing symbols from this header should fail at compile time in `dcn36_resource.c` or DPP shift/mask struct initialization.
- Exercise modesets and plane updates across DPP instances 1, 2, and 3, especially configurations that use scaling, cursor, alpha, FP16/format conversion, pre-CSC, post-CSC, gamut remap, and gamma correction.
- Validate color correctness with gamma/gamut/HDR paths enabled, including bank switching for GAMCOR RAMA/RAMB and LUT region programming.
- Check DSCL behavior for 4:4:4 and 4:2:0 content, horizontal/vertical scaling, chroma scaling, overscan, recout sizing, and line-buffer partition programming.
- Run display CRC capture or IGT/KMS CRC-style checks where available; mismatches can indicate DPP CRC source/format/mask or color-pipeline field errors.
- Exercise DC perfmon setup/readback if supported by local diagnostics, including interrupt ack/status paths and high/low counter reads.
- Test runtime power-management transitions or display idle/resume paths that force or disable GAMCOR, DSCL LUT/LB groups, or OBUF memories, watching for timeout waits on `*_MEM_PWR_STATUS`.
