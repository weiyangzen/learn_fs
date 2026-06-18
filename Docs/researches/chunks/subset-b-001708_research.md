# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 51608-54079

## Scope

This chunk is a partial slice of the generated DCN 3.0.0 register shift/mask header. It contains only preprocessor constants and address-block/register comments; there are no C functions, structs, enums, or executable statements. The exported contract is the generated `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` namespace consumed by AMD display register helper macros.

The range starts mid-register at the final `DSCC2_DSCC_PPS_CONFIG15__RANGE_BPG_OFFSET0_MASK` definition, continues through the tail of DSC compressor instance 2, covers DSC compressor instances 3 and 4, starts DSC compressor instance 5, covers the first display writeback top/perfmon/control-processing blocks, and ends mid-register at `DWB_OGAM_RAMB_START_BASE_CNTL_G__SHIFT`. The next chunk must supply the matching `DWB_OGAM_RAMB_START_BASE_CNTL_G_MASK` and the rest of the DWB RAMB output-gamma fields.

## Purpose

The purpose of this header chunk is to describe bit layouts for DCN 3.0 display stream compression and display writeback hardware registers. Driver code combines these masks and shifts with register offsets from `dcn_3_0_0_offset.h` so higher-level DSC/DWB code can program MMIO fields through macros such as `REG_SET`, `REG_SET_N`, `REG_UPDATE`, `REG_GET`, `DSC_SF`, `FD_MASK`, and `FD_SHIFT` without hard-coding numeric bit positions.

The main hardware areas visible in this chunk are:

- DSC instance 2 tail fields: remaining PPS range QP/BPG-offset fields, DSCC memory power control, encoder error/statistic readbacks, and rate-buffer fullness readbacks.
- DSC instance 2 perfmon block: `DC_PERFMON23_*` counter configuration, state, interrupt/status/ack, and readback fields.
- Full DSC instances 3 and 4: `DSC_TOP3/4`, `DSCCIF3/4`, `DSCC3/4`, and `DC_PERFMON24/25` field definitions.
- Start of DSC instance 5: `DSC_TOP5`, `DSCCIF5`, `DSCC5`, and `DC_PERFMON26` definitions through the common DSC control, PPS, status, and perfmon patterns.
- Display writeback instance 0: `DWB_ENABLE_CLK_CTRL`, memory power control, frame-composer controls, CRC fields, output control, MMHUBBUB backpressure counters, host-read control, overflow status/counter, soft reset, `DC_PERFMON27`, gamut-remap matrices, HDR multiplier, output-gamma LUT control, RAMA region tables, and the start of RAMB start-control fields.

## Important APIs, Types, And Constants

There are no callable APIs or data types. The important interface is the macro set:

- `DSC_TOPn_DSC_TOP_CONTROL` and `DSC_TOPn_DSC_DEBUG_CONTROL` fields control per-instance DSC clock enable, clock-gating disable bits, and debug enable.
- `DSCCIFn_DSCCIF_CONFIG0/1` fields describe input-interface recovery/underflow status, input pixel format, bits per component, double-buffer update pending state, and picture dimensions.
- `DSCCn_DSCC_CONFIG0/1` fields describe ICH reset behavior, slice counts, alternate ICH encoding, vertical slice count, rate-control buffer model size, and ICH disable.
- `DSCCn_DSCC_INTERRUPT_CONTROL_STATUS` packs rate-buffer overflow/underflow status bits, rate-control model overflow status bits, and the matching interrupt-enable bits.
- `DSCCn_DSCC_PPS_CONFIG0` through `DSCCn_DSCC_PPS_CONFIG22` encode the DSC picture parameter set: DSC version, PPS identifier, line-buffer depth, bits per component, bits per pixel, native/simple 4:2:2 or 4:2:0 flags, chunk size, picture/slice dimensions, initial delays, scale intervals, first/second-line offsets, BPG offsets, RC model size, flatness QP bounds, quantization increment limits, target offsets, rate-control buffer thresholds, and range min/max QP plus range BPG offsets.
- `DSCCn_DSCC_MEM_POWER_CONTROL` controls default low-power state, forced memory power state, memory power disable, current memory power state, and native 4:2:2 memory power fields.
- `DSCCn_DSCC_*_SQUARED_ERROR_*`, `DSCCn_DSCC_MAX_ABS_ERROR*`, `DSCCn_DSCC_RATE_BUFFER*_MAX_FULLNESS_LEVEL`, and `DSCCn_DSCC_RATE_CONTROL_BUFFER*_MAX_FULLNESS_LEVEL` expose diagnostic/statistical readback fields.
- `DC_PERFMON23` through `DC_PERFMON27` repeat the standard perfmon layout: event selection, counted value selection, increment mode, hardware stop selectors, counter state selectors, perfmon state, report count, counter-off interrupt control/status/ack, per-counter interrupt status/ack bits, and low/high counter readback.
- `DWB_*` fields describe writeback clock/memory power, frame-composer mode and window/source geometry, update/CRC/output controls, MMHUBBUB backpressure and overflow reporting, soft reset, HDR multiplier, gamut-remap mode and 3x4 matrix coefficient registers for two matrices, output-gamma mode/LUT access, and RAMA/RAMB piecewise-linear region geometry.

The DSC register families are instance-suffixed in the generated header (`DSCC3_...`, `DSCC4_...`, etc.) but are normally consumed through per-instance register tables. For example, `drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h` uses `SRI(DSCC_PPS_CONFIG16, DSCC, id)` for offsets and `DSC_SF(DSCC0_DSCC_PPS_CONFIG16, RANGE_MIN_QP1, mask_sh)` style macros for shifts/masks, allowing runtime DSC code to use unsuffixed logical register names such as `DSCC_PPS_CONFIG16`.

## Control Flow

This chunk has no runtime control flow. Its compile-time flow is:

1. DCN 3.0 consumers include `sienna_cichlid_ip_offset.h`, `dcn_3_0_0_offset.h`, and this shift/mask header.
2. Register-list macros concatenate generated register and field names to populate register-address and field-mask tables.
3. Runtime DSC and DWB functions call generic register helpers against those tables.
4. The helpers use the generated shift/mask constants here to preserve unrelated bits while programming individual hardware fields.

The ordering is still important for maintenance because the file is organized by address block and register. Each register generally lists all field shifts first, then masks. Because this is generated hardware metadata, reordering or partial hand edits can make diffs harder to audit and can hide mismatches against the paired offset header.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It defines how driver writes reach persistent hardware register state until the driver overwrites it, the display block resets, or the GPU resets.

Important state described by this chunk includes:

- DSC enablement and clock/debug state in `DSC_TOPn`.
- DSC input-interface underflow recovery, underflow status, pixel format, component depth, picture dimensions, and double-buffer update pending state in `DSCCIFn`.
- DSC encoder configuration and PPS state in `DSCCn`, including slice topology, rate-control model size, PPS programming, RC thresholds, QP ranges, and native 4:2:2/4:2:0 flags.
- Error and fullness counters for DSC quality/debug visibility. Many of these are readback-style 16-, 18-, or 32-bit fields.
- Perfmon event selection, run/stop control, interrupt enable/status/ack, and counter readback state for the DSC and DWB-related performance monitor blocks.
- DWB clock/memory-power, frame-composer geometry, output mode, CRC mask/value, backpressure/overflow counters, color-processing matrices, output-gamma LUT mode/index/data, and output-gamma RAM region geometry.

Some registers contain status and acknowledgement fields in the same word, especially perfmon interrupt/status/ack fields. Consumers must rely on the hardware programming model to distinguish read-only status, write-one-to-clear acknowledgement, and normal control fields; the generated mask names alone do not encode access semantics.

## Dependencies And Integration Points

This chunk depends on strict generated-name compatibility with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which supplies the matching register offsets.
- ASIC base-offset headers such as `sienna_cichlid_ip_offset.h`.
- AMD display register helper macros in the DC codebase, including `SRI`, `SR`, `REG_SET`, `REG_SET_N`, `REG_UPDATE`, `REG_GET`, `DSC_SF`, `FD_MASK`, and `FD_SHIFT`.

Observed direct include sites for the whole `dcn_3_0_0_sh_mask.h` header include DCN 3.0 and DCN 3.0.2 DMUB, IRQ, GPIO, resource, and clock-manager code:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`

The DSC-specific field families integrate with `drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h` and related DSC implementations. Those files define register lists and field-list macros for programming DSC PPS registers and reading DSC status. The DWB fields integrate with writeback/resource paths that configure display capture/output formatting, color processing, CRC, and output-gamma state.

## Risks And Edge Cases

- This is generated numeric hardware metadata. A wrong mask or shift can compile cleanly while silently programming the wrong MMIO bits.
- The range starts and ends in the middle of registers. Whole-file merge must reconcile `DSCC2_DSCC_PPS_CONFIG15` with the previous chunk and `DWB_OGAM_RAMB_START_BASE_CNTL_G` with the next chunk before drawing final completeness conclusions.
- DSC instances 3, 4, and 5 repeat nearly identical layouts. Copy/generator drift in only one instance can create instance-specific failures that normal compile tests will not catch.
- Offset/header mismatch is high risk: the logical DSC register tables combine offsets from `dcn_3_0_0_offset.h` with masks from this file. If either side gains, loses, or renames an instance register independently, field accesses can target the wrong address or fail to compile.
- Several fields use full-register masks such as `0xFFFFFFFFL` for counter/error readbacks. Callers must preserve unsigned width expectations and avoid sign-extension assumptions.
- Perfmon status/ack fields are adjacent to control bits. Read/modify/write code that writes back stale status or ack bits can inadvertently clear interrupts or change counter behavior.
- DSC PPS fields directly affect compressed stream syntax and rate-control behavior. Bad values can produce link failures, corrupted compressed output, underflow/overflow interrupts, or display blanking.
- DWB output-gamma and gamut-remap fields are stateful color-processing controls. Incorrect masks can cause visible color errors in writeback/capture paths without necessarily breaking modeset.
- Memory-power and clock-enable fields can cause hangs or lost state if consumers disable memory or clocks while a block is active.

## Test Signals

Useful validation for this chunk is mostly compile-time plus DCN hardware integration:

- Build DCN 3.0/3.0.2 display paths that include `dcn_3_0_0_sh_mask.h`, with attention to DSC, DWB, DMUB, IRQ, GPIO, resource, and clock-manager translation units.
- Compile-check representative `DSC_SF`, `FD_MASK`, `FD_SHIFT`, `REG_SET_N`, `REG_UPDATE`, and `REG_GET` expansions for `DSCC_PPS_CONFIG0-22`, `DSCCIF_CONFIG0/1`, `DSC_TOP_CONTROL`, and DWB color/output registers.
- Exercise DSC enable/disable, PPS programming, multiple slice layouts, native 4:2:2/4:2:0 flags, bits-per-pixel/component settings, and DSC underrun/overflow interrupt paths on DCN 3.0 hardware.
- Read DSC diagnostic counters and max/squared error registers after DSC traffic to confirm masks select the expected low/high fields.
- Program and read back `DC_PERFMON23` through `DC_PERFMON27` counters, including interrupt status and ack behavior.
- Exercise DWB capture/writeback with frame-composer windows, CRC enable/masks, MMHUBBUB backpressure counters, overflow handling, gamut remap, HDR multiplier, and OGAM LUT/RAMA/RAMB programming.
- Compare generated masks in this range against the paired DCN 3.0.0 offset header and adjacent DCN family headers where the DSC/DWB layouts are expected to remain stable.

## Open Cross-Chunk Questions

- The previous chunk should confirm the first four fields and masks of `DSCC2_DSCC_PPS_CONFIG15`; this chunk only contains its final mask.
- The next chunk should confirm the missing mask for `DWB_OGAM_RAMB_START_BASE_CNTL_G` and the remaining RAMB/OGAM region table definitions.
- Whole-file reconciliation should verify that every `DSC_TOPn`, `DSCCIFn`, `DSCCn`, `DC_PERFMON2x`, and DWB register offset has matching field definitions and that instance numbering stays aligned across offset and mask headers.
