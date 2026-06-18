# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 17310-19827

## Scope

This chunk is a large middle slice of AMDGPU's generated DCN 3.0.0 shift/mask header. It contains preprocessor constants only: no functions, structs, enums, storage objects, or local executable control flow. The exported contract is a dense set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that describe the bit positions and already-shifted masks for DCN 3.0.0 display hardware registers.

The range starts in the tail of the DPP1 DSCL line-buffer memory-control group, covers the rest of DPP1 DSCL memory/power and output-buffer fields, then covers almost the full DPP1 color-management block, DPP1 display-performance monitor block, and the beginning of DPP2. The DPP2 material includes top-level DPP control, CNVC format/cursor conversion, DSCL scaler fields, and the beginning of the DPP2 color-management block through `CM2_CM_GAMCOR_RAMA_OFFSET_R`. The chunk ends before the remaining `CM2_CM_GAMCOR_RAMA_REGION_*` fields, so whole-file reconciliation must merge this slice with adjacent chunks.

## Purpose

The purpose of this header region is to provide ASIC-specific field metadata for DCN 3.0 display pipe programming. Runtime DC code can refer to logical field names while the generated header supplies the exact bit layout for the DCN 3.0.0 register database.

The covered hardware areas are:

- DPP1 DSCL tail fields: line-buffer partitioning, luma/chroma vertical counters, DSCL LUT/line-buffer memory power control and status, output-buffer bypass/full-buffer/hold control, and output-buffer memory power state.
- DPP1 CM fields: post color-space conversion matrices, gamut remap matrices, bias registers, gamma-correction LUT programming, blending gamma LUT programming, HDR multiplier coefficient, CM memory-power controls/status, dealpha/coefficient-format controls, shaper LUT programming, 3D LUT programming, and CM test/debug index/data registers.
- DPP1 DC perfmon 13 fields: performance-counter event selection, counter control, counter state, perfmon control, current-value comparison, and high/low counter readback.
- DPP2 DPP top fields: DPP clock enable/gating, soft reset, CRC values/control, and host-read control.
- DPP2 CNVC fields: surface pixel format, format expansion/conversion/alpha/crossbar controls, floating-point bias/scale, color keying, alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, pre-realpha, and cursor color/scale/bias fields.
- DPP2 DSCL fields: scaler coefficient RAM access, scaler mode/tap controls, two-tap sharpening, manual replication, scale ratios, initial phases, black color, update/autocal controls, overscan, OTG blanking windows, recout/MPC sizes, line-buffer format/memory fields, and DSCL/OBUF memory power.
- DPP2 CM start fields: post CSC, gamut remap, bias, and the beginning of gamma-correction RAM A setup.

Although this repository path sits under `sources/distributed-fs/ceph-client`, this file is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, or network protocol behavior.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro naming scheme:

- `*_SHIFT` gives the field's low bit position.
- `*_MASK` gives the field mask already shifted into the register position.
- Register-heading comments group macros by hardware register.
- `addressBlock` comments identify generated register blocks such as `dce_dc_dpp1_dispdec_cm_dispdec`, `dce_dc_dpp1_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`, `dce_dc_dpp2_dispdec_dpp_top_dispdec`, `dce_dc_dpp2_dispdec_cnvc_cfg_dispdec`, `dce_dc_dpp2_dispdec_cnvc_cur_dispdec`, `dce_dc_dpp2_dispdec_dscl_dispdec`, and `dce_dc_dpp2_dispdec_cm_dispdec`.

The DSCL memory and output-buffer groups use compact masks for power and buffering state. `DSCL1_DSCL_MEM_PWR_CTRL` and `DSCL2_DSCL_MEM_PWR_CTRL` define force/disable fields for LUT memory and line-buffer groups `LB_G1` through `LB_G6`, plus `LB_MEM_PWR_MODE`. Their matching `*_STATUS` registers expose each memory group's state. `DSCL*_OBUF_CONTROL` covers bypass, full-buffer use, half recout width, and output hold count; `DSCL*_OBUF_MEM_PWR_CTRL` combines force, disable, mode, and state bits for the output buffer memory.

The CM1 and CM2 matrix groups follow a consistent 16-bit-pair layout. Post-CSC and gamut-remap coefficient registers pack pairs such as `C11/C12`, `C13/C14`, `C21/C22`, `C23/C24`, `C31/C32`, and `C33/C34` into low and high 16-bit halves. The `_B_` variants provide the alternate bank of coefficients. Control registers such as `CM*_CM_POST_CSC_CONTROL` and `CM*_CM_GAMUT_REMAP_CONTROL` expose mode and current-mode fields, while `CM*_CM_CONTROL` provides bypass and update-pending status.

The CM1 gamma-correction, blending-gamma, and shaper blocks expose indexed LUT programming surfaces. `CM1_CM_GAMCOR_LUT_INDEX`, `CM1_CM_GAMCOR_LUT_DATA`, and `CM1_CM_GAMCOR_LUT_CONTROL` define index, data, write-color mask, read-color select, debug read, host select, and config mode. `CM1_CM_BLNDGAM_*` mirrors the gamma-correction pattern for blend gamma. `CM1_CM_SHAPER_*` defines shaper control, RGB offsets, scale fields, LUT index/data, write-enable masks, and RAM A/B region descriptors.

The LUT region descriptors are repeated and mechanically generated. For gamma-correction and blend-gamma RAM A/B, each color channel has start, start slope, start base, end base, end/slope, and offset registers. Region-pair registers such as `CM1_CM_GAMCOR_RAMA_REGION_0_1` through `REGION_32_33` pack one 9-bit LUT offset and one segment-count field per region into the low and high halves. Shaper RAM A/B uses the same region-pair idea for its piecewise approximation tables, while CM2 starts the same `GAMCOR_RAMA` sequence before the chunk ends.

The 3D LUT group is specific to CM1 in this range. `CM1_CM_3DLUT_MODE` carries enable/interpolation/size/readback configuration fields. `CM1_CM_3DLUT_INDEX`, `CM1_CM_3DLUT_DATA`, and `CM1_CM_3DLUT_DATA_30BIT` provide indexed data access. `CM1_CM_3DLUT_READ_WRITE_CONTROL` exposes write-enable, readback, config status, bit-depth, and mode-change/update fields. Output normalization and RGB output offsets are described by `CM1_CM_3DLUT_OUT_NORM_FACTOR` and `CM1_CM_3DLUT_OUT_OFFSET_*`.

The DPP1 perfmon block defines the `DC_PERFMON13_*` field contract. `DC_PERFMON13_PERFCOUNTER_CNTL` selects events, counted current-value source, increment mode, run-enable mode, restart/int enable, active/off-mask bits, and counter select. `DC_PERFMON13_PERFCOUNTER_CNTL2` adds counted-value type and hardware stop controls. `DC_PERFMON13_PERFCOUNTER_STATE` exposes current state, restart pending, stop pending, clear state bits, current value, and carry/overflow style status. The `PERFMON_CNTL*`, `PERFMON_CVALUE_*`, `PERFMON_HI`, and `PERFMON_LOW` groups define counter-window, comparison, and readback fields.

The DPP2 top and CNVC groups describe the start of a second display pipe. `DPP_TOP2_DPP_CONTROL` includes DPP clock enable and several DPP/DISPCLK gate-disable controls plus a test clock selector. `DPP_TOP2_DPP_SOFT_RESET` exposes reset and reset-status bits for top, DSCL, CM, CNVC, and cursor subblocks. `DPP_TOP2_DPP_CRC_CTRL` selects CRC components, region source, mode, window inclusion/exclusion, and enablement. `CNVC_CFG2_FORMAT_CONTROL` defines format expansion, 16-bit conversion, alpha enable, bypass/MSB alignment, positive clamps, update pending, and RGB crossbar selection.

The DPP2 DSCL groups are the scaler programming surface. The key fields include coefficient RAM tap pair/phase/filter type and even/odd coefficient values, scaler mode and RAM selection, luma/chroma/alpha coefficient modes, vertical/horizontal tap counts for luma and chroma, two-tap hardcoded coefficient and sharpening controls, horizontal/vertical scale ratios, initial phases for top/bottom and chroma, black color values, update pending, autocal pipe fields, overscan rectangles, OTG blanking start/end, recout and MPC dimensions, line-buffer format/memory partitioning, vertical counters, and DSCL/OBUF memory power.

## Control Flow

This header region has no local control flow. Runtime behavior is created by consumers that include `dcn_3_0_0_offset.h` and this shift/mask header, then use AMD display register helpers and generated register tables.

A typical path is:

1. DCN 3.0/3.0.2 code includes the DCN 3.0.0 offset and shift/mask headers.
2. Register-table macros paste instance-neutral names such as `DPP_CONTROL`, `FORMAT_CONTROL`, `SCL_MODE`, `CM_GAMCOR_CONTROL`, or `CM_3DLUT_MODE` onto instance-specific generated names such as `DPP_TOP2_DPP_CONTROL__DPP_CLOCK_ENABLE_MASK`.
3. Helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_SET_N`, `REG_UPDATE_N`, `REG_WAIT`, and the `SRI`/`TF_SF` table-building macros use the `*_SHIFT` and `*_MASK` constants to isolate fields during MMIO read/modify/write operations.
4. Display code sequences the hardware operations around power, blanking, update-lock, plane programming, or LUT programming requirements.

Examples visible in the display tree include DPP clock control through `DPP_CONTROL`, format programming through `FORMAT_CONTROL`, DSCL programming through `SCL_MODE`, `SCL_TAP_CONTROL`, scale-ratio, init, recout, and memory-power fields, and color-state readback/programming through CM shaper, blend gamma, gamma correction, and 3D LUT registers. The header does not encode the ordering rules for those operations; it only defines the bit layout needed by the sequenced code.

## State And Persistence Behavior

The file itself stores no state and persists nothing. It describes hardware register state in DPP/DSCL/CNVC/CM/perfmon blocks whose lifetime is controlled by display pipe power, modeset programming, plane updates, resets, suspend/resume, and GPU reset.

State represented by this chunk includes:

- DSCL scaler configuration: filter taps, coefficient RAM selection and values, scale ratios, initial phases, overscan, output dimensions, line-buffer partitioning, and update-pending state.
- DSCL and OBUF memory power state: force/disable/mode controls and readback status for LUT, line-buffer, and output-buffer memories.
- CM color pipeline state: CSC/gamut matrices, biases, coefficient formats, HDR multiplier, dealpha, shaper, gamma-correction, blend-gamma, and 3D LUT configuration and data.
- CNVC state: surface format, conversion behavior, alpha and color-key controls, pre-CSC/pre-degamma/pre-realpha, floating-point bias/scale, and cursor color controls.
- DPP top state: clock gating, soft-reset state, CRC capture state, and host-read routing.
- Perfmon state: event selection, counter enable/restart/interrupt controls, counter state, current-value comparison, and high/low counter values.
- Test/debug state: CM test debug index/data controls.

Some fields are configuration latches, some are live status readbacks, some are indexed data ports, and some are power/reset controls. A bad write can persist until the affected display pipe is reprogrammed, power-cycled, reset, or the GPU is reset. Indexed LUT/data registers are especially stateful: writes through an index/data pair alter table entries, not just a scalar register, and the selected index may affect subsequent reads or writes.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which provides the matching register addresses and base indices. Representative anchors in that file include:

- `mmDSCL1_LB_V_COUNTER` at `0x0e81` and `mmDSCL1_DSCL_MEM_PWR_CTRL` at `0x0e82`.
- `mmCM1_CM_CONTROL` at `0x0e8b`, `mmCM1_CM_GAMCOR_CONTROL` at `0x0ea8`, `mmCM1_CM_BLNDGAM_CONTROL` at `0x0ef2`, `mmCM1_CM_SHAPER_CONTROL` at `0x0f42`, and `mmCM1_CM_3DLUT_MODE` at `0x0f7b`.
- `mmDC_PERFMON13_PERFCOUNTER_CNTL` at `0x0f8f`.
- `mmDPP_TOP2_DPP_CONTROL` at `0x0f9b`.
- `mmCNVC_CFG2_FORMAT_CONTROL` at `0x0fa6` and `mmCNVC_CUR2_CURSOR0_CONTROL` at `0x0fc7`.
- `mmDSCL2_SCL_COEF_RAM_TAP_SELECT` at `0x0fcf`, `mmDSCL2_SCL_MODE` at `0x0fd1`, and `mmDSCL2_DSCL_MEM_PWR_CTRL` at `0x0fed`.
- `mmCM2_CM_CONTROL` at `0x0ff6`, `mmCM2_CM_GAMCOR_CONTROL` at `0x1013`, and `mmCM2_CM_GAMCOR_RAMA_OFFSET_R` at `0x1028`.

Visible include sites for `dcn_3_0_0_sh_mask.h` in this tree are:

- `display/dc/resource/dcn30/dcn30_resource.c`, which builds DCN 3.0 display resources and register tables.
- `display/dc/irq/dcn30/irq_service_dcn30.c` and `display/dc/irq/dcn302/irq_service_dcn302.c`, which use generated register metadata for interrupt tables.
- `display/dc/gpio/dcn30/hw_factory_dcn30.c` and `display/dc/gpio/dcn30/hw_translate_dcn30.c`, which consume the same generated namespace for GPIO support.
- `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`, which includes the DCN 3.0 register headers for clock-management programming.
- `display/dmub/src/dmub_dcn30.c` and `display/dmub/src/dmub_dcn302.c`, which include these headers for DMUB-facing display microcontroller support.

The most important functional consumers are the DPP/DSCL/CM helpers under `display/dc/dpp/`. Common register lists in `dcn10_dpp.h` map logical registers such as `SCL_MODE`, `FORMAT_CONTROL`, `DPP_CONTROL`, `DSCL_MEM_PWR_CTRL`, and `CM_*` tables to instance-specific generated names. Runtime code in `dcn10_dpp.c`, `dcn10_dpp_dscl.c`, `dcn10_dpp_cm.c`, and later DCN DPP implementations then uses those register tables through generic helper macros.

Cross-generation integration is also relevant. Headers such as `dcn_3_0_1_sh_mask.h`, `dcn_3_5_1_sh_mask.h`, and `dcn_3_6_0_offset.h` contain similar DPP/CM/DSCL/CNVC/perfmon names, but offsets and field availability can differ. Consumers must bind the correct offset and mask header pair for the target ASIC.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. Shift and mask constants compile cleanly even when wrong, but a bad value can update the wrong field, leave stale bits behind, truncate a coefficient, corrupt a neighboring field, or decode live status incorrectly.

Chunk-boundary risk is high in this work item. The first lines are only the tail of `DSCL1_LB_MEMORY_CTRL` masks without the full preceding register context, and the final lines stop at `CM2_CM_GAMCOR_RAMA_OFFSET_R` before the remaining CM2 RAM A region descriptors. The final per-file report should not infer complete DPP1 DSCL or CM2 gamma coverage from this chunk alone.

Color-management fields are precision-sensitive. The CSC/gamut matrices use packed 16-bit coefficients, gamma/blend/shaper data fields use 18-bit-style data masks, and 3D LUT data has both standard and 30-bit paths. Incorrect masks or shifts can cause visible color errors, banding, wrong gamut remap, bad HDR/shaper behavior, or LUT programming that appears successful but produces wrong output.

Indexed LUT programming is ordering-sensitive. LUT index, data, write color mask, host select, config mode, and read/debug selectors must be sequenced by the caller. This header does not say which updates require blanking, update locks, pipe disable, or current-mode polling. Those rules must come from the DC code and hardware programming guide.

DSCL fields affect geometry and sampling. Wrong scale ratios, phase init fields, tap counts, coefficient RAM selectors, recout/MPC sizes, overscan, or line-buffer partitioning can produce distorted images, chroma misalignment, underflow, clipped output, or hangs that occur only for certain formats, rotations, scaling ratios, or multi-pipe layouts.

Power and reset fields can be hazardous. `DSCL*_DSCL_MEM_PWR_CTRL`, `DSCL*_OBUF_MEM_PWR_CTRL`, `CM1_CM_MEM_PWR_CTRL*`, `DPP_TOP2_DPP_SOFT_RESET`, and clock-gate-disable fields interact with block availability. Incorrect use can force memories off while active, fail to restore state after power transitions, or leave update/status bits stuck.

Perfmon fields can be misleading if masks are wrong. Event selection, counter select, compare value, restart, interrupt, and state fields may still return plausible values while counting the wrong event or clearing the wrong status. This is a diagnostic risk rather than a direct display-output risk, but it can hide real performance regressions.

The generated namespace is highly repetitive across DPP instances. A field that is correct for DPP1 may look identical for DPP2 while binding to a different register address through the offset header. Mixing DCN generations or pairing `dcn_3_0_0_sh_mask.h` with the wrong offset header would be a systemic failure mode.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Compile coverage for all DCN 3.0/3.0.2 include sites: resource construction, IRQ service, GPIO factory/translate, clock manager, and DMUB support.
- Generated-register consistency checks that every `*_MASK` has a matching `*_SHIFT`, expected width, and matching register offset in `dcn_3_0_0_offset.h`.
- Cross-generation diffs against `dcn_3_0_1_sh_mask.h` and later DCN headers, with expected differences reviewed against the ASIC register database.
- DPP/DSCL display tests for bypass, upscaling/downscaling, chroma 4:2:0 paths, non-integer ratios, overscan, multi-plane composition, and recout/MPC size changes.
- Color-management tests for post-CSC, gamut remap, gamma correction, blend gamma, shaper LUT, 3D LUT, HDR multiplier, coefficient format, and suspend/resume restoration.
- CNVC tests for surface pixel formats, alpha enable, format conversion, crossbar mapping, color keying, pre-CSC/pre-degamma/pre-realpha, and cursor color/FP scale-bias behavior.
- Power-management tests that exercise DSCL/OBUF/CM memory power, DPP clock gating, soft reset, display idle, modeset, hotplug, runtime PM, and system suspend/resume.
- CRC tests using `DPP_TOP2_DPP_CRC_*` to verify region/component selection and output stability for known frames.
- Perfmon tests that select known events, start/restart counters, validate high/low readback, compare-value behavior, and interrupt/state handling.

Regression symptoms from bad constants include blank or distorted display output, incorrect scaling or chroma alignment, color shifts, LUT banding, HDR errors, alpha/cursor artifacts, stale update-pending bits, failed memory-power transitions, broken CRC capture, misleading perf counters, or failures that appear only on DCN 3.0/3.0.2 ASICs.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dcn_3_0_0_sh_mask.h`. The preceding chunk owns the start of the DPP1 DSCL scaler and line-buffer groups, and the following chunk owns the rest of CM2 gamma-correction RAM region descriptors and subsequent DPP2 material. The merge/reconciliation lane should treat this document as the DPP1 CM/perfmon and early DPP2 middle portion of the full DCN 3.0.0 shift/mask contract.
