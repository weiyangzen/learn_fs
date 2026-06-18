# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 5219-7834

## Scope

This chunk covers 2,616 lines from the generated AMD DCN 3.0.2 register-offset header. It contains only C preprocessor constants and generated register block comments; there are no functions, structs, enums, storage objects, or executable statements in this slice.

The slice exports 2,402 `#define` entries: 1,201 MMIO register offset macros and 1,201 matching `_BASE_IDX` macros. Each register offset is paired with a base-segment selector used by AMD display register-table macros to form a full SOC15/DCN MMIO address.

The range starts in the middle of the DPP2 CNVC configuration block, covers most of DPP instances 2-4, covers OPP instances 0-4, then reaches the beginning of the OPTC OTG0 block. The final `dce_dc_optc_otg0_dispdec` address-block comment is a boundary marker only in this chunk; its register definitions begin after line 7834.

## Purpose

This header region maps symbolic DCN 3.0.2 display-pipeline register names to ASIC-specific register offsets. Runtime display code does not use these values directly as standalone physical addresses; it combines `mm<REGISTER>` with `DCN_BASE__INST0_SEG<BASE_IDX>` through macros such as `BASE(mm..._BASE_IDX) + mm...`.

The covered hardware areas are:

- Display Pipe Processor instances 2, 3, and 4: DPP top control/CRC, CNVC format and cursor controls, DSCL scaler/line-buffer controls, CM color-management controls, and per-DPP performance counters.
- Output Pixel Processor instances 0 through 4: FMT output formatting/dither/clamp registers, DPG display pattern generator registers, OPP buffer controls, OPP pipe control, OPP pipe CRC controls/results, and shared OPP top/ABM controls.
- DSC remap controls for OPP to DSC forwarding, one register each for DSCRM0 through DSCRM4.
- OPP-side DC perfmon block 16.
- OPTC ODM input controls for ODM0 through ODM4, including data source selection, format, bytes-per-pixel, width, input clock, memory configuration, and spare registers.

This is a hardware contract file. Its value is precise generated naming and offset data for the DCN 3.0.2 display stack, not algorithmic behavior.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the macro naming convention:

- `mm<REGISTER>` expands to the register offset within the selected DCN base segment.
- `mm<REGISTER>_BASE_IDX` expands to the segment index used by the generated `DCN_BASE__INST0_SEG*` constants.
- Instance-numbered families such as `mmDSCL2_*`, `mmCM3_*`, `mmFMT4_*`, `mmODM1_*`, and `mmOPP_PIPE_CRC0_*` describe repeated hardware instances.

The main register families are:

- `CNVC_CFG2_*`, `CNVC_CFG3_*`, and `CNVC_CFG4_*` for input pixel format conversion, floating-point bias/scale, color keying, alpha handling, pre-CSC coefficient banks, coefficient format, pre-degamma, and pre-realpha. The chunk starts with the last 25 register offsets of `CNVC_CFG2`; the complete `CNVC_CFG3` and `CNVC_CFG4` blocks each contain 31 register offsets.
- `CNVC_CUR2_*`, `CNVC_CUR3_*`, and `CNVC_CUR4_*` for cursor control, cursor colors, and cursor FP scale/bias.
- `DSCL2_*`, `DSCL3_*`, and `DSCL4_*` for scaler coefficient RAM access, scaler modes/taps, horizontal and vertical scale ratios/initial phases for luma/chroma, black color, update/autocal control, overscan, OTG blanking, recout/MPC sizing, line-buffer format and memory controls, memory power controls/status, and output buffer controls.
- `CM2_*`, `CM3_*`, and `CM4_*` for color-management state. Each complete CM block in this range has 250 register offsets covering post-CSC, gamut remap, bias, gamma correction LUTs, region programming, output CSC, degamma/regamma LUTs, 3D LUT controls/data, shaper controls/data, memory controls, debug, and related color-pipeline registers.
- `DC_PERFMON12_*`, `DC_PERFMON13_*`, `DC_PERFMON14_*`, and `DC_PERFMON16_*` for perf counter control, state, current value, high/low counter values, and perfmon control registers.
- `DPP_TOP3_*` and `DPP_TOP4_*` for DPP control, soft reset, CRC values/control, and host read control. DPP2 top appears in the previous chunk; this range resumes after it.
- `FMT0_*` through `FMT4_*` for output formatter clamp component limits, dynamic expansion, format control, bit depth, dither random seeds, clamp control, side-by-side stereo, 4:2:0 memory control, and 4:2:2 control.
- `DPG0_*` through `DPG4_*` for display pattern generator control, ramp, dimensions, RGB/YCbCr color components, offset segment, and status.
- `OPPBUF0_*` through `OPPBUF4_*`, `OPP_PIPE0_*` through `OPP_PIPE4_*`, and `OPP_PIPE_CRC0_*` through `OPP_PIPE_CRC4_*` for OPP buffering, 3D parameters, pipe control, CRC masks, and CRC result registers.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL` for shared OPP top clock and adaptive backlight management control.
- `DSCRM<n>_DSCRM_DSC_FORWARD_CONFIG` for DSC forwarding remap per OPP/DSC instance.
- `ODM0_*` through `ODM4_*` for OPTC input composition and DSC input-segment controls.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro expansion:

1. `dcn302_resource.c` includes `dcn/dcn_3_0_2_offset.h` together with the matching `dcn_3_0_2_sh_mask.h`.
2. Register list macros from hardware blocks such as DPP, OPP, OPTC, IRQ, GPIO, and perfmon expand register tokens into address-table initializers.
3. The local `SR`, `SRI`, `SRII`, and related macros in `dcn302_resource.c` form final offsets as `BASE(mm..._BASE_IDX) + mm...`.
4. Runtime code accesses those table entries through helpers such as `dm_read_reg_func`, `dm_write_reg_func`, `generic_reg_update_ex`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Ordering is still meaningful. Blocks are emitted in instance order: DPP2 partials, DPP3, DPP4, OPP0-4, DSCRM0-4, OPP perfmon, ODM0-4, then the OTG0 boundary marker. Repeated offsets and base indices must stay synchronized with the generated shift/mask header and with resource-table macros that assume these symbolic names exist.

## State And Persistence Behavior

The header itself stores no state and performs no persistence. It describes hardware state that lives in GPU display MMIO registers.

The registers named here control persistent hardware programming until a later driver write, display block reset, power-gate transition, suspend/resume restore, or ASIC reset changes them. Examples include scaler ratios/taps, line-buffer memory controls, color-management LUT configuration, post-CSC/gamut matrices, output format/dither/clamp configuration, OPP pipe routing, ODM segment format/width/source selection, and DSC forwarding selection.

Some registers expose transient or readback state rather than durable configuration, including CRC values/results, perf counter current/high/low values, perf counter state, DSCL memory power status, OPP pipe CRC results, line-buffer counters, DPG status, OPTC underflow/double-buffer status bits through matching field definitions, and clock/status fields. This offset header does not encode access direction; callers must rely on the hardware programming model and the matching shift/mask definitions.

## Dependencies And Integration Points

The primary integration point is the AMD display DCN 3.0.2 resource construction path in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`, which includes this offset header and builds hardware register tables using `BASE(mm..._BASE_IDX) + mm...`.

Important dependencies are:

- `dcn_3_0_2_sh_mask.h`, which supplies the field masks and shifts for the register names mapped here.
- `dimgrey_cavefish_ip_offset.h`, which supplies the `DCN_BASE__INST0_SEG*` constants used by the `_BASE_IDX` selectors for this ASIC.
- DC hardware block headers and register list macros such as `dcn30_dpp.h`, `dcn30_opp.h`, and `dcn30_optc.h`, which concatenate instance numbers with symbolic register names.
- Generic display MMIO helpers in `dm_services.h` and register helper layers that use the resolved addresses for reads, writes, polling, and read-modify-write operations.
- Kernel DRM/AMDGPU display flows for plane scaling, cursor setup, color management, output formatting, pipe CRC, perf monitoring, ODM/DSC routing, and display bring-up on DCN 3.0.2 hardware.

The chunk also relies on cross-generation naming stability. Many names match other DCN generations, but the numeric offsets and sometimes base indices vary by ASIC, so consumers must include the DCN 3.0.2 header for DCN 3.0.2 hardware rather than borrowing a nearby generation's constants.

## Risks And Edge Cases

- The slice begins mid-`CNVC_CFG2` and ends before any OTG0 register definitions. Whole-file reporting must merge adjacent chunks before making complete-block claims for those boundary areas.
- Wrong `_BASE_IDX` values are as dangerous as wrong offsets. The address can compile and still target the wrong MMIO segment.
- Repeated DPP/OPP/ODM instance blocks are mechanically similar. A generator error in one instance can be hard to spot in code review because only the instance number and offset sequence change.
- CM blocks are large and stateful. Bad offsets in gamma, degamma, regamma, shaper, or 3D LUT registers can cause visible color corruption without a simple compile-time signal.
- DSCL programming mixes ratios, init phases, coefficient RAM, line-buffer sizing, and memory power state. Offset drift can present as scaler artifacts, underflow, hangs, or memory-power sequencing failures.
- OPP FMT registers affect output bit depth, dithering, chroma subsampling, clamping, and 4:2:0/4:2:2 behavior. Incorrect addresses may only appear under specific pixel encodings or monitor modes.
- Pipe CRC and DPP CRC registers are often used for validation/debug. Wrong offsets can produce misleading test failures rather than obvious runtime breakage.
- Perfmon registers are counter/control pairs. Misaddressed control or value registers can silently corrupt performance telemetry.
- ODM and DSCRM mappings affect multi-segment output and DSC routing. Mistakes can surface only in multi-display, high-bandwidth, DSC, or ODM split configurations.

## Test Signals

Useful validation is mostly build-time plus hardware/display integration:

- Build the DCN 3.0.2 AMD display path to catch missing macro names in resource-table, IRQ, GPIO, DPP, OPP, and OPTC expansions.
- Preprocess `dcn302_resource.c` and representative register-list macros to confirm `mm...` and `_BASE_IDX` names resolve to the expected `BASE(...) + mm...` expressions.
- Compare this offset chunk with the generated DCN 3.0.2 register database and the matching `dcn_3_0_2_sh_mask.h` to ensure every referenced register has matching field definitions.
- Boot DCN 3.0.2 hardware and exercise display modes across DPP instances 2-4 and OPP/ODM instances 0-4.
- Validate scaler paths with upscaling, downscaling, chroma formats, overscan, line-buffer pressure, and suspend/resume to cover DSCL and CNVC programming.
- Exercise color-management paths: post-CSC, gamut remap, degamma/regamma LUTs, 3D LUT, shaper LUT, HDR/SDR transitions, and LUT memory programming.
- Run pipe CRC and DPP CRC tests and compare stable-frame CRCs across modes to catch wrong CRC result/control offsets.
- Test output formatter modes including RGB, YCbCr, 4:2:0, 4:2:2, dithering/truncation, dynamic expansion, and clamp behavior.
- Exercise DSC and ODM split configurations to validate `DSCRM*` and `ODM*` offsets, especially high-resolution or high-refresh modes that require segmentation.
- Check perfmon readouts for DPP2-4 and OPP perfmon controls to ensure counters start, stop, and report plausible values.

## Open Cross-Chunk Questions

- The later merge lane should combine this with the preceding chunk to describe the complete DPP2 top and CNVC_CFG2 blocks.
- The later merge lane should combine this with the following chunk to describe the full OTG0 timing-generator register block.
- Whole-file reconciliation should verify that the expected five-pipe DCN 3.0.2 topology is complete across DPP, OPP, DSCRM, ODM, OPTC, DIO, and perfmon sections.
