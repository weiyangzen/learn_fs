# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 15459-17678

## Scope And Purpose

This chunk is a generated AMD DCN 3.5.1 display register shift/mask header segment. It does not define executable code; it defines C preprocessor constants used to extract, insert, and document bitfields in memory-mapped display hardware registers. The source file has an MIT SPDX header and a normal include guard at the top of the full header. This chunk starts in the `CURSOR0_3_DMDATA` register group and runs through the beginning of `DC_PERFMON11_PERFMON_CNTL`.

The dominant purpose of this range is to provide field layout for display pipe instances 0 and 1 in DCN351-era hardware:

- Cursor metadata transfer fields for cursor instance 3.
- Display core performance monitor blocks `DC_PERFMON9`, `DC_PERFMON10`, and the start of `DC_PERFMON11`.
- DPP top-level control, soft reset, CRC, and host-read throttling for DPP instances 0 and 1.
- CNVC format conversion, color keying, alpha LUT, pre-dealpha, pre-CSC, pre-degamma, and pre-realpha fields for CNVC instances 0 and 1.
- Cursor composition fields for `CNVC_CUR0` and `CNVC_CUR1`.
- DSCL/scaler fields for coefficient RAM access, tap selection, scaler mode, filter ratio/init values, overscan, recout/MPC sizing, line-buffer controls, and DSCL/OBUF memory power controls for DSCL instances 0 and 1.
- CM color-management fields for post-CSC, gamut remap, bias, gamma correction LUT programming, RAM A/RAM B piecewise regions, HDR multiplier, memory power, dealpha, coefficient format, and a CM0 debug index.

As a chunk report, this document covers only lines 15459-17678. The final per-file report should merge this with adjacent chunks to describe the entire `dcn_3_5_1_sh_mask.h` header.

## Important APIs, Types, And Macros

The only exported surface in this chunk is `#define` constants. Each hardware field normally has two constants:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset of the field within the register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field.

Consumers use these constants through AMD display register helper macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `TF_SF(...)`, and related register-list expansion macros. In `dmub_dcn351.c`, for example, `DMUB_SF(reg, field)` writes `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` into DMUB register metadata. In `dcn351_resource.c`, the header is included with `dcn_3_5_1_offset.h` so resource construction code can pair register offsets with these masks and shifts. DPP-specific headers such as `dcn35_dpp.h` reference fields like `DPP_TOP0_DPP_CONTROL` through `TF_SF`.

No C types, functions, structs, or inline helpers are declared in this range. The effective ABI is the macro naming scheme and exact numeric values.

## Register Areas Covered

### Cursor DMDATA Tail

The opening lines finish `CURSOR0_3_DMDATA` definitions:

- `DMDATA_CNTL` includes `DMDATA_SIZE` at bits 16-27, continuing from prior lines in the file.
- `DMDATA_QOS_CNTL` defines mode, QoS level, and deadline delta fields.
- `DMDATA_STATUS` exposes `DMDATA_DONE`, `DMDATA_UNDERFLOW`, and `DMDATA_UNDERFLOW_CLEAR`.
- `DMDATA_SW_CNTL` and `DMDATA_SW_DATA` define software-updated metadata payload control and 32-bit data access.

These fields affect cursor/display metadata programming and underflow reporting. The chunk begins mid-register group, so the paired address-high/low and earlier `DMDATA_CNTL` fields belong to the previous chunk.

### DC Performance Monitors

`DC_PERFMON9`, `DC_PERFMON10`, and the start of `DC_PERFMON11` share a repeated layout:

- `PERFCOUNTER_CNTL` selects the counted event, counted value source, increment mode, hardware control, run-enable mode, count-off start behavior, restart behavior, interrupt enable, masking, active state, and counter select.
- `PERFCOUNTER_CNTL2` selects counted value type, hardware stop inputs, count-off select, and control-bank select.
- `PERFCOUNTER_STATE` packs state and selector fields for counters 0 through 7.
- `PERFMON_CNTL` controls perfmon state, report count, count-off interrupt logic, interrupt enable/status/ack.
- `PERFMON_CNTL2` appears for perfmon 9 and 10 in this chunk and defines count-off interrupt type, clock enable, and run-enable start/stop selectors.
- `PERFMON_CVALUE_INT_MISC`, value low/high, and read select fields appear for perfmon 9 and 10. The chunk ends before the corresponding value fields for perfmon 11.

These masks are used by debug, diagnostics, tracing, and internal display performance instrumentation paths. Incorrect masks would misprogram event selection or fail to acknowledge performance counter interrupts.

### DPP Top Control For Instances 0 And 1

`DPP_TOP0_*` and `DPP_TOP1_*` define DPP-level controls:

- `DPP_CONTROL`: DPP clock enable, DPP/disp clock gating disable controls, dynamic/DSCL clock gate controls, and test clock select.
- `DPP_SOFT_RESET`: soft reset bits for CNVC, DSCL, CM, and OBUF subblocks.
- `DPP_CRC_VAL_R_G`, `DPP_CRC_VAL_B_A`, and `DPP_CRC_CTRL`: CRC result fields and CRC enable, continuous/one-shot modes, 4:2:0 component select, source select, stereo/interlace/pixel/cursor format selection, and CRC mask.
- `HOST_READ_CONTROL`: host read rate control.

These definitions support DPP construction, clock/power sequencing, CRC capture for validation, and register debug access. The DCN35 DPP code adds or overrides a small set of fields elsewhere in the header, but this chunk provides the core `DPP_TOP0` and `DPP_TOP1` bit layouts.

### CNVC And Cursor Composition For Instances 0 And 1

`CNVC_CFG0_*` and `CNVC_CFG1_*` define input format conversion and pre-color-processing controls:

- Surface pixel format and alpha-plane enable.
- Format expansion, 16-bit conversion, alpha enable, bypass, MSB alignment, positive clamp controls, update-pending status, and RGB crossbar selection.
- Floating-point bias and scale for R/G/B.
- Color-key enable, mode, and per-channel low/high ranges for alpha, red, green, and blue.
- 2-bit alpha LUT entries.
- Pre-dealpha, pre-CSC mode and 3x4 coefficient matrices, alternate B coefficient banks, coefficient format, pre-degamma, and pre-realpha.

`CNVC_CUR0_*` and `CNVC_CUR1_*` define cursor-composition control, two cursor colors, and cursor floating-point scale/bias. The control fields include expansion mode, alpha enable, mode, format, degamma, 2-bit alpha, pre-multiply alpha, and cursor truncation or bit-depth related controls visible in the masks.

Together these fields are the fixed hardware contract for programming pixel format conversion, alpha handling, color keying, pre-CSC matrices, and cursor blending in the first two DPP/CNVC instances.

### DSCL/Scaler For Instances 0 And 1

`DSCL0_*` and `DSCL1_*` provide the scaler and line-buffer fields for each pipe:

- Coefficient RAM tap select/data fields for loading scaler coefficients.
- Scaler mode, coefficient RAM selection, chroma coefficient mode, and current-selection status.
- Tap-control fields for horizontal/vertical and chroma luma taps.
- DSCL control, 2-tap control, manual replicate control.
- Horizontal and vertical scale ratios and initial phases, including chroma and bottom-field variants.
- Black color, update pending, and autocal pipe coordination fields.
- Extended overscan, OTG blanking, recout start/size, MPC size.
- Line-buffer data format, memory partitioning, vertical counters.
- DSCL LUT/LB memory power force/disable/status fields across LB groups G1-G6.
- OBUF bypass/full-buffer/half-width/out-hold controls and OBUF memory power controls/status.

These constants are central to timing-sensitive scaling, viewport setup, output-size programming, and low-power memory gating for the first two display pipes.

### CM Color Management For Instances 0 And 1

`CM0_*` and `CM1_*` define color-management fields after CNVC/DSCL:

- CM bypass and update-pending fields.
- Post-CSC mode/current state and two coefficient banks for 3x4 matrix coefficients.
- Gamut-remap mode/current state and two coefficient banks.
- Bias fields for Cr/R and Y/G/Cb/B.
- Gamma-correction control, LUT index/data/control, and host selection.
- Gamma correction RAM A and RAM B start, slope, base, end, offset, and 34-region definitions. Each region pair packs LUT offset and segment-count values for two adjacent expansion regions.
- HDR multiplier coefficient.
- Gamma correction memory power force/disable/status.
- CM dealpha enable and blend mode.
- Coefficient format selectors for bias, post-CSC, and gamut-remap fields.

For CM0 only, this chunk also includes `CM0_CM_TEST_DEBUG_INDEX`, with a debug index field and debug write-enable bit. CM1's corresponding region in this chunk ends at coefficient format, then transitions to `DC_PERFMON11`.

## Control Flow

There is no runtime control flow in this chunk. The constants are compiled into driver code and used when register helper macros generate read/modify/write masks, field shifts, and register metadata tables. Runtime control flow lives in consumers such as DC resource construction, DPP programming, DSCL/scaler programming, color-management programming, IRQ service setup, and DMUB register initialization.

The implicit "flow" is data-driven:

1. Register offset headers provide absolute or base-relative register addresses.
2. This `*_sh_mask.h` header provides per-field shifts and masks.
3. Hardware block register-list macros expand field names into per-block `shift` and `mask` structs.
4. Runtime code writes or reads fields with helper macros, relying on these exact constants for bit placement.

## State And Persistence Behavior

The header itself has no mutable state and no persistence. The state it describes is hardware state:

- DPP clock/reset/CRC state persists in hardware registers until reprogrammed or reset.
- CNVC, DSCL, and CM settings represent active display pipeline configuration, often latched or double-buffered by update-pending/current fields.
- Gamma LUT and piecewise region fields persist in CM hardware RAM/registers and are selected through A/B banks.
- Memory power control/status fields reflect display block SRAM power-gating policy and state.
- Perfmon fields configure counters and interrupts whose values/status persist until stopped, acknowledged, or reset.

Because many fields are double-buffered, banked, or status/ack sensitive, a wrong mask can cause persistent display misconfiguration rather than a simple compile-time failure.

## Dependencies And Integration Points

Direct includes of `dcn_3_5_1_sh_mask.h` in this source tree include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, paired with `dcn_3_5_1_offset.h` during DCN351 resource construction.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, where `FD_MASK` and `FD_SHIFT` populate DMUB-visible register mask/shift metadata.
- `drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`, which includes the same generated offset and mask headers for DCN351 IRQ service definitions.

The fields in this chunk are also tied to shared display component headers:

- DPP register-field lists in `dcn10_dpp.h`, `dcn30_dpp.h`, and `dcn35_dpp.h` reference DPP, CNVC, DSCL, and CM field names that resolve through this generated header on DCN351.
- Register helper macros in AMD display code assume the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming convention.
- Offset headers such as `dcn_3_5_1_offset.h` supply matching register addresses; masks without matching offsets are incomplete.

The numerical values are generated from ASIC register specifications. They should not be hand-edited except as part of a deliberate hardware-header update.

## Risks And Edge Cases

- The chunk begins and ends mid-logical areas: it starts after earlier `CURSOR0_3_DMDATA_CNTL` fields and ends before the rest of `DC_PERFMON11`. Merge-time research must not treat this chunk as a complete file-level map.
- Field names are contract-sensitive. Renaming a macro breaks downstream `TF_SF`, `DMUB_SF`, or `FD_MASK` expansions even when the numeric value is unchanged.
- Numeric drift is high impact: a one-bit shift/mask error can write unrelated hardware fields, causing display corruption, scaler programming errors, bad color transforms, lost CRC/debug signals, bad power-gating behavior, or stuck perfmon interrupts.
- The pipe-instance repetition is easy to desynchronize. Instance 0 and 1 definitions mostly mirror each other; accidental divergence may only affect multi-display or multi-plane configurations.
- Current/update-pending fields must remain aligned with programming sequences. Incorrect masks can make driver code believe a programming update completed when it did not.
- Power-control fields combine force, disable, mode, and status bits. Wrong values can keep SRAM powered unnecessarily or power down active pipeline resources.
- Perfmon status/ack bits are interrupt-sensitive. Bad masks can leave interrupts unacknowledged or acknowledge the wrong counter.
- Because this is a generated header, normal unit tests may not catch hardware semantic errors unless register tables are compared against authoritative specs or exercised on matching hardware.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, table-generation, and hardware-integration oriented:

- Build AMDGPU display code for DCN351 targets and confirm all `FD_MASK`, `FD_SHIFT`, `TF_SF`, and register-list expansions compile.
- Compare generated `dcn_3_5_1_sh_mask.h` values against AMD's authoritative ASIC register source for DCN 3.5.1.
- Boot or initialize DCN351 hardware and verify DPP construction, DMUB register initialization, and IRQ service setup do not hit missing-field or bad-register assertions.
- Exercise display modes that use scaling, color conversion, cursor blending, color keying, HDR/gamma LUT programming, and multi-pipe operation.
- Run CRC and perfmon/debug paths where available to confirm status, ack, and readback fields behave as expected.
- Check power-management/display-idle scenarios that touch DSCL, OBUF, cursor, and CM memory power controls.

Static review should focus on repeated block consistency between `0` and `1` instances, consistency with adjacent DCN 3.5.0/3.5.1/4.x generated headers where hardware specs indicate reuse, and exact pairing with matching offsets in `dcn_3_5_1_offset.h`.
