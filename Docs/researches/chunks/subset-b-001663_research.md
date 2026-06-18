# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 17357-19859

## Scope

This chunk is a generated AMD DCN 2.1.0 register shift/mask header slice. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. Its exported contract is the paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that AMD display register helpers use to pack and unpack fields in memory-mapped DCN registers.

The range has 2,503 source lines, including 2,119 `#define` entries, 1,060 shift constants, 1,059 mask constants, 372 register/address comments, and 6 address-block markers. The chunk begins inside the DPP2 color-management block at the tail of `CM2_CM_BLNDGAM_RAMA_REGION_6_7`, then covers the rest of DPP2 blend gamma, shaper, 3D LUT, CM memory-power, and CM debug masks. It then enters DPP3 register blocks for DPP top, CNVC converter/cursor, DSCL scaler, DC perfmon instance 13, and a large part of DPP3 color management ending inside `CM3_CM_SHAPER_RAMB_REGION_10_11`.

## Purpose

The chunk provides exact bit positions and already-shifted masks for DCN 2.1 display pipe/plane processing hardware. Higher-level display code names logical fields through register helper macros; this generated header supplies the ASIC-specific bit layout for Renoir/DCN 2.1.

Major hardware areas covered here are:

- `CM2_CM_BLNDGAM_*`: DPP2 blend/output gamma RAM A/B controls, per-channel start/end/slope values, LUT region descriptors for regions 0-33, LUT index/data/write-enable fields, and current/config status bits.
- `CM2_CM_SHAPER_*`: DPP2 shaper LUT controls, offsets, scales, LUT access, write masks, RAM A/B start/end controls, and 34-region piecewise-linear segment descriptors.
- `CM2_CM_3DLUT_*`: DPP2 3D LUT mode, index, 12-bit/30-bit data path, read/write control, output normalization, and RGB output offsets.
- `CM2_CM_MEM_PWR_*`, `CM2_CM_HDR_MULT_COEF`, `CM2_CM_DEALPHA`, `CM2_CM_COEF_FORMAT`, and `CM2_CM_TEST_DEBUG_*`: color-management memory power, HDR multiplier, de-alpha, coefficient format, and indexed debug/status access.
- `DC_PERFMON13_*`: perf counter and perfmon control/state/value masks for the DPP2 perfmon address block.
- `DPP_TOP3_*`: DPP3 top-level enable/reset/CRC/host-read controls.
- `CNVC_CFG3_*` and `CNVC_CUR3_*`: DPP3 converter pixel format, format expansion/bypass/alpha controls, floating-point bias/scale, color keyer ranges, 2-bit alpha LUT, cursor mode/colors, and cursor FP scale/bias.
- `DSCL3_*`: DPP3 scaler coefficient RAM, tap counts, scaler mode, scale ratios, filter init, recout/MPC sizes, line-buffer format/memory, autocal, overscan/blanking geometry, memory power, and output-buffer controls.
- `CM3_CM_*`: DPP3 color-management control, ICSC and gamut-remap A/B coefficient banks, bias, degamma, blend gamma, HDR multiplier, shaper, dealpha, coefficient format, and CM memory-power masks. This chunk includes complete DPP3 degamma and blend gamma region blocks and a partial DPP3 shaper block.

## Important APIs, Types, And Macros

There are no callable APIs in this range. The important interface is the generated macro naming scheme:

- `*_SHIFT` constants hold a field's low bit position.
- `*_MASK` constants hold the field mask already shifted into register position.
- Register comments such as `//CM2_CM_SHAPER_RAMA_REGION_0_1` group the following field macros by hardware register.
- Address-block comments such as `// addressBlock: dce_dc_dpp3_dispdec_dscl_dispdec` mark generated hardware register windows.

The constants are consumed through AMD display register helper conventions rather than direct hand-written bit operations. DCN21 resource setup includes `dcn_2_1_0_offset.h` and this file, then expands macros such as `SRI`, `SR`, `TF_SF`, `FD_MASK`, and `FD_SHIFT` into register, shift, and mask tables. Runtime code then uses helpers such as `REG_SET`, `REG_SET_2`, `REG_SET_4`, `REG_UPDATE`, `REG_GET`, and `IX_REG_GET`.

Representative DPP2 color-management fields in this chunk include `CM2_CM_BLNDGAM_RAMB_REGION_0_1__CM_BLNDGAM_RAMB_EXP_REGION0_LUT_OFFSET_MASK`, `CM2_CM_BLNDGAM_LUT_WRITE_EN_MASK__CM_BLNDGAM_LUT_WRITE_SEL_MASK`, `CM2_CM_SHAPER_CONTROL__CM_SHAPER_LUT_MODE_MASK`, `CM2_CM_SHAPER_RAMA_END_CNTL_B__CM_SHAPER_RAMA_EXP_REGION_END_BASE_B_MASK`, `CM2_CM_3DLUT_READ_WRITE_CONTROL__CM_3DLUT_CONFIG_STATUS_MASK`, and `CM2_CM_TEST_DEBUG_DATA__CM_TEST_DEBUG_DATA_MASK`.

Representative DPP3 converter/scaler/top fields include `DPP_TOP3_DPP_CONTROL__DPP_CLOCK_ENABLE_MASK`, `CNVC_CFG3_FORMAT_CONTROL__CNVC_BYPASS_MASK`, `CNVC_CFG3_CNVC_SURFACE_PIXEL_FORMAT__CNVC_SURFACE_PIXEL_FORMAT_MASK`, `CNVC_CUR3_CURSOR0_CONTROL__CUR0_ENABLE_MASK`, `DSCL3_SCL_MODE__DSCL_MODE_MASK`, `DSCL3_SCL_TAP_CONTROL__SCL_H_NUM_TAPS_MASK`, `DSCL3_SCL_COEF_RAM_TAP_DATA__SCL_COEF_RAM_EVEN_TAP_COEF_MASK`, `DSCL3_LB_MEMORY_CTRL__LB_MEMORY_CONFIG_MASK`, and `DSCL3_DSCL_MEM_PWR_CTRL__LUT_MEM_PWR_FORCE_MASK`.

Representative DPP3 color fields include `CM3_CM_CONTROL__CM_BYPASS_MASK`, `CM3_CM_ICSC_CONTROL__CM_ICSC_MODE_MASK`, `CM3_CM_GAMUT_REMAP_CONTROL__CM_GAMUT_REMAP_MODE_MASK`, `CM3_CM_DGAM_CONTROL__CM_DGAM_LUT_MODE_MASK`, `CM3_CM_BLNDGAM_LUT_WRITE_EN_MASK__CM_BLNDGAM_CONFIG_STATUS_MASK`, `CM3_CM_SHAPER_CONTROL__CM_SHAPER_LUT_MODE_MASK`, and the many `CM3_CM_*_REGION_*__*_LUT_OFFSET/NUM_SEGMENTS` masks that describe piecewise-linear LUT programming.

## Control Flow

This header has no local control flow. Runtime behavior is created by the consumers that combine these shift/mask macros with the matching addresses from `dcn_2_1_0_offset.h`.

A typical DPP path is:

1. `display/dc/resource/dcn21/dcn21_resource.c` includes `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`.
2. Register-list macros instantiate per-DPP address, shift, and mask tables. `dcn21_dpp_create()` constructs `struct dcn20_dpp` objects with `dpp2_construct()`, passing `tf_regs`, `tf_shift`, and `tf_mask`.
3. Generic DCN2 DPP code in `display/dc/dpp/dcn20/` uses those tables for converter setup, cursor setup, scaler setup, color-management programming, LUT access, gamut remap, degamma, blend gamma, shaper, 3D LUT, memory power, and state reads.
4. `REG_*` and `IX_REG_*` helpers combine a register address with the field's shift and mask from this generated header to perform MMIO reads/writes or indexed debug-register reads.

Control-sensitive flows represented by this chunk include pixel-format selection, alpha enable, input color-space conversion, color keying, cursor attribute programming, scaler coefficient/tap/ratio programming, line-buffer setup, DPP clock/soft-reset/CRC handling, color-management bypass, double-buffered ICSC/gamut-remap coefficient selection, degamma/shaper/blend LUT RAM A/B selection, 3D LUT data access, and DPP/DSCL/CM memory power transitions.

The macros do not encode sequencing, access type, volatility, field value limits beyond bit width, frame-boundary latch timing, or write-one-to-clear behavior. Callers must still know when a field is read-only status, live hardware state, sticky debug/status, double-buffered RAM selection, or safe to modify only during a blanking/update sequence.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. It describes hardware register state that persists according to DCN register semantics until changed by software, hardware sequencing, power management, reset, or firmware activity.

State represented in this range includes:

- DPP2/DPP3 color-management pipeline state: CM bypass, ICSC and gamut-remap coefficient bank selection, coefficient format, RGB bias, de-alpha, HDR multiplier, degamma/blend/shaper LUT modes, LUT RAM selection, LUT data/index state, LUT region metadata, 3D LUT mode/size/bit depth/data, output normalization, and RGB offsets.
- DPP3 converter/cursor state: pixel format, format expansion, alpha enable, clamp/crossbar controls, FP bias/scale values, color-key ranges, alpha 2-bit LUT values, cursor mode/enable/expansion/ROM/pixel-alpha controls, cursor colors, and cursor FP bias/scale.
- DPP3 scaler state: coefficient RAM selector and coefficient data, tap counts, scaler and chroma coefficient modes, horizontal/vertical scale ratios and initial phases for luma/chroma, output geometry, MPC size, line-buffer format/memory configuration, autocal controls, overscan/OTG blanking, black offsets, DSCL update controls, and DSCL/OBUF memory power state.
- Top/debug/perf state: DPP clock enable, soft reset, CRC values/control, host-read control, perf counter control/state/value registers, and CM indexed debug status/data.

Many fields are configuration latches, some are live readbacks, and some are selected through indexed debug paths. Incorrect values can persist until the affected pipe is reprogrammed by a modeset, plane update, color update, scaler update, suspend/resume, DPP power transition, or full GPU reset.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies matching MMIO offsets and base-index macros. This chunk supplies bit layout inside those registers.

Visible include sites for the full generated header in this tree are:

- `display/dc/resource/dcn21/dcn21_resource.c`, which builds Renoir/DCN21 resources and instantiates DPP, IPP, AUX/I2C, IRQ, link, audio, clock, hub, MPC, OPP, DSC, and other display blocks.
- `display/dc/irq/dcn21/irq_service_dcn21.c`, which uses the generated namespace for interrupt-source tables.
- `display/dc/gpio/dcn21/hw_factory_dcn21.c` and `display/dc/gpio/dcn21/hw_translate_dcn21.c`, which use DCN21 generated masks for GPIO/HPD translation.
- `display/dmub/src/dmub_dcn21.c`, which expands `FD_MASK` and `FD_SHIFT` values for DMUB service register tables.

For this chunk specifically, the strongest functional integration is with `display/dc/dpp/dcn20/dcn20_dpp.h`, `dcn20_dpp.c`, and `dcn20_dpp_cm.c`. Those files define the DCN2 DPP register lists and the runtime operations that use the CM, CNVC, DSCL, DPP_TOP, and memory-power fields represented here. `display/dc/inc/hw/dpp.h` documents the DPP pipeline as CNVC, DSCL, CM, OBUF, and DPB, matching the hardware blocks in this chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed storage, network protocol, or persistence-layer behavior.

## Risks And Edge Cases

The dominant risk is silent hardware misprogramming. A wrong shift or mask compiles cleanly but can write the wrong bits, truncate a field, read stale status, choose the wrong RAM bank, or corrupt unrelated control fields.

Color-management fields are especially sensitive because they are often double-buffered or RAM-backed. Bad masks in blend gamma, shaper, degamma, ICSC, gamut-remap, or 3D LUT registers can produce wrong colors, banding, HDR errors, broken color-space conversion, incorrect gamma/transfer curves, or updates that tear because software wrote the active bank instead of the inactive bank.

Scaler and converter fields affect plane correctness. Incorrect `CNVC_*` masks can select the wrong pixel format, alpha behavior, cursor mode, color key range, or channel mapping. Incorrect `DSCL3_*` masks can produce bad scaling ratios, wrong tap counts, coefficient RAM corruption, line-buffer underuse/overflow, chroma misalignment, clipped recout geometry, or failures that appear only for video formats, 4:2:0 planes, high bit depth, cursors, or scaling cases.

Power-management fields must match hardware semantics. Bad `CM_MEM_PWR_*`, `DSCL_MEM_PWR_*`, or `OBUF_MEM_PWR_*` masks can leave memories powered down while being accessed, prevent low-power entry, or cause intermittent failures around plane enable/disable, idle, suspend/resume, or clock gating.

Repeated generated layouts create copy hazards. DPP2 and DPP3 register families are structurally similar but not always identical; apparent one-off differences must be checked against the ASIC register database and matching offset header before being treated as bugs. The chunk boundary also matters: it begins with mask definitions from a register whose earlier shift definitions are in the previous chunk, and it ends inside the DPP3 shaper RAMB region sequence. Whole-file conclusions need adjacent chunks.

## Test Signals

Useful validation signals are a mix of generated-header consistency checks and display behavior:

- Build coverage for DCN21 resource, DPP, IRQ, GPIO, DMUB, and common register-helper users that include `dcn_2_1_0_sh_mask.h`.
- Generated-register validation that every field used by DCN21 register-list macros has a matching shift and mask, a matching address in `dcn_2_1_0_offset.h`, and a mask consistent with its shift and expected width.
- Structural comparison across repeated DPP instances and RAM A/B blocks: `CM2` vs `CM3`, `RAMA` vs `RAMB`, and region pairs `0_1` through `32_33`.
- Plane-format tests for ARGB/ABGR/RGB565/RGB111110/FP formats, alpha enable/disable, 2-bit alpha LUT paths, color keying, cursor modes, and cursor disable cases for selected video formats.
- Scaling tests covering bypass, up/downscale, luma/chroma scaling, 4:2:0 content, tap count variations, coefficient RAM updates, recout/MPC geometry, overscan, and line-buffer partition changes.
- Color tests for degamma, gamut remap, ICSC, blend gamma, shaper, HDR multiplier, 3D LUT programming, and double-buffered RAM bank switching across frame updates.
- Power-management tests around plane enable/disable, display idle, memory power-gating, suspend/resume, and modeset transitions while using CM/DSCL/OBUF memories.
- CRC/perf/debug sanity checks that DPP CRC registers, DC perfmon instance 13, and CM test-debug indexed reads return plausible values and do not break normal pipe programming.

Regression symptoms from bad constants include black or corrupted planes, wrong colors or gamma, broken HDR/color-management paths, bad scaling or chroma placement, cursor corruption, alpha/color-key errors, flicker during LUT updates, memory-power transition hangs, invalid CRC reads, and failures limited to DPP instance 2 or 3 because this chunk mostly covers `CM2` and `*3` blocks.

## Cross-Chunk Notes

This is a generated constants-only chunk, not a standalone module. The previous chunk owns the beginning of the DPP2 blend-gamma RAMA register sequence, including some shifts for fields whose masks appear at this chunk's start. Later chunks own the remainder of the DPP3 shaper RAMB sequence and subsequent DCN 2.1 register blocks. The final per-file document should merge adjacent chunks to describe the complete `dcn_2_1_0_sh_mask.h` register-layout contract.
