# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 17692-19909

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.5.0 register shift/mask header. It contains preprocessor constants for hardware register bitfields, not executable driver logic. Consumers combine these `__SHIFT` and `_MASK` constants with the matching `dcn_3_5_0_offset.h` register offsets and AMD display register helpers to read or write memory-mapped DCN display hardware.

The requested range contains 2,218 `#define` lines: 1,113 shift macros and 1,105 mask macros. The imbalance is caused by chunk boundaries. The range starts inside the tail of `DC_PERFMON11_PERFMON_CNTL`, after earlier `PERFMON_STATE`, `PERFMON_RPT_COUNT`, `PERFMON_CNTOFF_AND_OR`, and `PERFMON_CNTOFF_INT_EN` shift lines, and ends inside `FMT0_FMT_BIT_DEPTH_CONTROL` before the remaining shifts and all masks for that register. There are no source comments in this range.

The substantive hardware covered here is the DCN 3.5 DPP pipe 2 and pipe 3 programming surface, plus adjacent performance monitor instances and the beginning of output formatter instance 0. Major areas are:

- `DC_PERFMON11`, `DC_PERFMON12`, and `DC_PERFMON13` control, counter state, interrupt, and value readback fields.
- `DPP_TOP2` and `DPP_TOP3` DPP clock, reset, CRC, and host-read control fields.
- `CNVC_CFG2`/`CNVC_CUR2` and `CNVC_CFG3`/`CNVC_CUR3` input conversion, surface format, pre-CSC, pre-degamma, color keyer, alpha, cursor, and floating-point bias/scale fields.
- `DSCL2` and `DSCL3` scaler, line buffer, coefficient RAM, recout, overscan, autocalibration, and scaler/OBUF memory power fields.
- `CM2` and `CM3` color-management controls: post-CSC, gamut remap, bias, gamma correction LUT RAM A/B programming, HDR multiplier, dealpha, coefficient format, and CM memory power state.
- The first `FMT0` output formatter fields for clamp ranges, dynamic expansion, pixel encoding/subsampling control, and the initial part of bit-depth/truncation/dither control.

## Important Constants And Register Areas

The `DC_PERFMON11` tail defines perfmon count-off interrupt status and acknowledgement bits, perfmon clock enable, run-enable start/stop selectors, counter interrupt status/ack bits for counters 0 through 7, high/low counter value readback, and read-select fields. `DC_PERFMON12` and `DC_PERFMON13` are more complete in this chunk and add counter event selection, counted-value selection, increment mode, hardware stop selectors, count-off selector, active state, and per-counter state selectors. These are diagnostic/performance measurement registers for display hardware events.

`DPP_TOP2` and `DPP_TOP3` expose the per-DPP top-level control surface. The fields cover `DPP_CLOCK_ENABLE`, DPPCLK and DISPCLK gate-disable bits, dynamic gate disables, test-clock select, soft resets for CNVC/DSCL/CM/OBUF subblocks, CRC values and control, and host read rate control. The same layout is repeated for DPP instances 2 and 3.

`CNVC_CFG2` and `CNVC_CFG3` describe the converter/cursor input side of each DPP. They include surface pixel format and alpha-plane enable, format expansion and 16-bit conversion, alpha enable, bypass and MSB alignment, positive clamp controls, update-pending readback, RGB crossbar selection, floating-point conversion bias and scale per channel, color keyer control and low/high component ranges, a 2-bit alpha LUT, pre-dealpha and pre-realpha controls, pre-CSC mode/current-mode and coefficient matrix banks A/B, pre-degamma mode/select, cursor mode/enable/expansion/inversion/ROM fields, cursor colors, and cursor floating-point scale/bias.

`DSCL2` and `DSCL3` contain the scaler path. Fields cover coefficient RAM tap select/data, scaler mode and current coefficient RAM select, vertical/horizontal and chroma tap counts, 2-tap hardcoded/sharpen controls, manual replication, horizontal/vertical scale ratios and initial phases for luma/chroma/bottom fields, black color, update state, autocalibration mode/pipe id/pipe count, extended overscan, OTG blank timing, recout start/size, MPC size, line-buffer data format and memory configuration, vertical counter, DSCL LUT/ALU/line-buffer/alpha memory power force/disables, corresponding memory power status fields, OBUF mode, and OBUF memory power force.

`CM2` and `CM3` are complete repeated color-management instances for pipes 2 and 3. They include CM bypass/current-mode, post-CSC control and matrix banks A/B, gamut-remap control and matrix banks A/B, bias fields, gamma-correction control, LUT index/data/control, RAM A and RAM B start/end/slope/base/offset fields for B/G/R channels, 34 gamma region descriptors per bank, HDR multiplier, shared/gamma memory power control and status, dealpha controls, and coefficient format. Region descriptor registers pack two regions per 32-bit register, using low/high LUT offsets and segment-count fields.

The `FMT0` tail begins output formatter instance 0. It includes per-channel clamp lower/upper bounds, dynamic expansion enable/mode, formatter control fields for stereosync override, spatial-dither frame counter, pixel encoding, subsampling mode/order, CbCr bit-reduction bypass, and double-buffer update pending. The chunk ends after the early `FMT_BIT_DEPTH_CONTROL` shifts for truncate, spatial dither, randomization, and temporal dither fields; later shifts and masks continue after line 19909.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this source range. The public interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the bit position for packing or extracting a register field.
- `REGISTER__FIELD_MASK` gives the already-positioned field mask.
- Register names encode the hardware block and instance, such as `CNVC_CFG2_*`, `DSCL3_*`, or `CM2_*`.

The macros are consumed indirectly by register-list and field-list structures in the AMD display stack. For DCN 3.5, `dc/resource/dcn35/dcn35_resource.c` includes both `dcn_3_5_0_offset.h` and this shift/mask header, then builds register address and `tf_shift`/`tf_mask` tables for DPP construction. `dc/dpp/dcn35/dcn35_dpp.c` stores those tables in DPP objects and accesses fields through `REG_SET`, `REG_UPDATE`, and related helpers. The output formatter side is similarly represented through OPP structures, and IRQ/DMUB code also includes this generated header for DCN 3.5 register access.

Semantic values are not defined here. Valid enum-like settings for pixel formats, scaler modes, LUT modes, memory power states, dither modes, and performance counter event selectors must come from hardware documentation, generated enum headers, or higher-level DCN code.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior happens when the display driver uses these masks and shifts to program DCN registers during modeset, plane update, color-management update, cursor update, diagnostics, power-management, or debug readback paths.

The implied DPP programming flow starts with top-level DPP clock gating and optional subblock reset, then converter setup for surface format, alpha, bypass, channel swizzle, color keying, pre-CSC/pre-degamma, and cursor state. Scaler setup programs coefficient RAM selection/data, tap counts, scale ratios, initial phases, viewport/recout dimensions, line-buffer format, and autocalibration fields. Color-management programming writes post-CSC and gamut-remap matrices, gamma-correction LUT index/data/control, RAM A/B piecewise region tables, HDR/dealpha controls, and memory power settings. Output formatter programming, beginning at the end of this chunk, handles clamp and dithering/truncation state after DPP processing.

The performance monitor flow is separate: callers select display events, count modes, hardware start/stop/count-off conditions, interrupt behavior, and readback selectors, then observe active state, interrupt status, and counter values. Count-off interrupt acknowledgement fields are side-effecting by nature and should be handled by the established interrupt/debug path rather than casual read-modify-write code.

Repeated instance layout is important control-flow context. The chunk contains the pipe-2 block sequence from `DPP_TOP2` through `CM2`, then repeats the same sequence for pipe 3 from `DPP_TOP3` through `CM3`. Callers rely on instance-indexed register tables so the same DPP/scaler/color code can operate on different hardware pipes by changing the register base and mask/shift table.

## State And Persistence

The file itself stores no mutable state. It defines how software reaches persistent hardware state in DCN registers and internal SRAM/LUT memories.

Hardware state represented here includes DPP clock/reset/gating controls, CRC configuration and values, surface format and converter controls, color key ranges, cursor mode/colors/FP scale and bias, scaler coefficient RAM and filter geometry, line-buffer configuration, scaler and OBUF memory power state, CM post-CSC/gamut-remap matrices, gamma LUT RAM A/B contents and region tables, HDR multiplier, dealpha mode, and FMT clamp/dither/truncation state.

Several fields expose double-buffered or current-state behavior. `*_CURRENT` fields, update-pending fields, coefficient-RAM current selection, CM current mode, pre-CSC current mode, and formatter double-buffer update pending should be treated as hardware readback/state synchronization points. The macros do not document when those values change; timing comes from the higher-level DCN programming sequence and display blanking/update rules.

Memory power fields are persistent and side-effect-prone. `DSCL*_DSCL_MEM_PWR_CTRL`, `DSCL*_OBUF_MEM_PWR_CTRL`, and `CM*_CM_MEM_PWR_CTRL` can force, disable, or observe memories used for scaler LUTs, line buffers, alpha storage, OBUF, and gamma correction. Powering or depowering these memories out of sequence can affect retained table data and active scanout.

## Dependencies And Integration Points

This generated header depends on the matching DCN 3.5.0 address header. The numeric masks are only meaningful with the same register database and ASIC generation; similar-looking DCN 3.2, 3.5.1, or 4.x headers must not be substituted without validation.

Primary integration points are:

- `dc/resource/dcn35/dcn35_resource.c`, which includes the generated offset and shift/mask headers and expands register-list macros for DCN 3.5 hardware objects.
- `dc/dpp/dcn35/dcn35_dpp.c` and inherited DCN 3.0/3.2 DPP code, which program CNVC, DSCL, CM, and DPP top fields through `tf_shift` and `tf_mask` structures.
- `dc/dpp/dcn30/dcn30_dpp.h`, which defines many common DPP register and field list macros used by later DPP versions for CNVC, DSCL, cursor, color, and memory-power programming.
- `dc/opp/dcn35` and inherited OPP code, which consume the `FMT0_*` family for output pixel processing, clamp, bit-depth reduction, and dithering.
- `dc/irq/dcn35/irq_service_dcn35.c` and `display/dmub/src/dmub_dcn35.c`, which include the same generated header for DCN 3.5 interrupt and DMUB-side register access.

The register helper layer is the main API boundary. Direct open-coded bit twiddling against these masks would bypass instance tables, base-index selection, and existing sequencing assumptions.

## Risks And Edge Cases

Generated-header drift is the central risk. A wrong mask or shift generally compiles successfully but writes the wrong hardware bits, causing subtle failures such as incorrect plane format conversion, broken cursor alpha, bad scaler coefficients, incorrect color matrices, gamma LUT corruption, invalid memory power transitions, or broken performance counter readback.

Chunk boundaries are incomplete. The range begins after part of `DC_PERFMON11_PERFMON_CNTL` and ends before `FMT0_FMT_BIT_DEPTH_CONTROL` is complete. Whole-register validation for those two registers requires neighboring chunks.

Repeated instance consistency is a strong maintenance signal. Pipe 2 and pipe 3 blocks should be structurally parallel, and `DC_PERFMON12`/`DC_PERFMON13` should match except for instance numbering. A one-instance generator error may only appear on a specific DPP pipe or diagnostic counter.

Sequencing-sensitive fields need care. LUT RAM index/data/control fields, coefficient RAM selectors, write-enable masks, current-mode readbacks, update-pending bits, and memory power controls have side effects or hardware timing dependencies. Reordering writes or using the wrong RAM bank can produce visible artifacts or stale state.

The `L` suffix on masks such as `0xFFFF0000L`, `0x80000000L`, and `0xC0000000L` means consumers should keep using the driver register helper types rather than signed arithmetic on raw constants.

## Test And Validation Signals

Compile coverage should include DCN 3.5 display objects that include `dcn_3_5_0_sh_mask.h`, especially resource construction, DPP, OPP, IRQ, and DMUB code. Missing or renamed macros usually fail at compile time; incorrect numeric values require generated-data comparison or hardware validation.

Useful static checks include comparing this range against the authoritative DCN 3.5.0 register database, verifying that complete registers have non-overlapping masks and shifts that match their masks, diffing pipe 2 and pipe 3 repeated blocks, and cross-checking the neighboring chunks for the incomplete `DC_PERFMON11_PERFMON_CNTL` and `FMT0_FMT_BIT_DEPTH_CONTROL` boundaries.

Runtime signals include successful modesets on DCN 3.5 hardware, correct scanout across multiple DPP pipes, cursor enable/format/alpha behavior, scaler quality for luma/chroma and 4:2:0 paths, correct color output with pre-CSC, post-CSC, gamut remap, gamma correction, HDR multiplier, and dealpha enabled, stable suspend/resume and runtime power-management transitions, valid DPP CRC readback, working output dithering/truncation through OPP/FMT, and reliable performance monitor counter/interrupt behavior.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002064_research.md`. Whole-file research for `dcn_3_5_0_sh_mask.h` must merge adjacent chunks to complete the leading `DC_PERFMON11_PERFMON_CNTL` register and the trailing `FMT0_FMT_BIT_DEPTH_CONTROL` register.
