# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 44292-46764

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.0.2 register shift/mask header. It contains preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for memory-mapped display hardware registers. The companion `dcn_3_0_2_offset.h` header supplies register addresses; this file supplies the field layout used by the AMD display register helper macros.

The requested range begins inside the DSC encoder 1 DSCC interrupt-control/status register, then completes DSC encoder 1's PPS, memory-power, error, and buffer-fullness fields. It then covers complete generated field layouts for DSC encoder instances 2, 3, and 4, including their DSC top, DSCCIF, DSCC, and associated DSC perfmon blocks. The range also covers the WB0 DWB top block, WB0 perfmon block, and the beginning of the WB0 DWB color-processing block through the start of `DWB_OGAM_RAMA_REGION_6_7`.

There are no functions, structs, branches, loops, or direct runtime side effects in this chunk. The exported surface is macro metadata for generated register tables. Runtime behavior occurs when DCN 3.0.2 resource construction binds these masks and shifts into hardware block objects and later display code uses `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers to program registers.

The chunk has partial-block boundaries. It starts after the first half of `DSCC1_DSCC_INTERRUPT_CONTROL_STATUS`; the instance 1 top, DSCCIF, config, status, and early interrupt definitions live in the previous chunk. It ends in the middle of the DWB output-gamma RAM A region table; `DWB_OGAM_RAMA_REGION_6_7` is completed and the remaining RAM A regions plus RAM B fields continue in the next chunk.

## Register Blocks Covered

The DSC encoder 1 tail covers `DSCC1_DSCC_INTERRUPT_CONTROL_STATUS` masks for rate-buffer underflow, rate-control model overflow, and interrupt-enable bits, followed by `DSCC1_DSCC_PPS_CONFIG0` through `DSCC1_DSCC_PPS_CONFIG22`. These PPS fields encode Display Stream Compression parameters such as DSC version, bits per component, bits per pixel, picture and slice dimensions, chunk size, initial transmit/decode delays, scale increments/decrements, BPG offsets, initial/final offsets, flatness QP bounds, RC model size, RC quantization limits, RC buffer thresholds, and range QP/BPG offsets 0 through 14. The instance 1 tail also includes DSCC memory-power controls, squared-error and maximum-absolute-error counters, and rate-buffer/rate-control-buffer maximum-fullness readback fields.

DSC encoder instances 2, 3, and 4 are covered as repeated full blocks. Each instance has:

- `DSC_TOPx_DSC_TOP_CONTROL` and `DSC_TOPx_DSC_DEBUG_CONTROL` fields for DSC clock enable/gating and debug clock selection.
- `DSCCIFx_DSCCIF_CONFIG0` and `DSCCIFx_DSCCIF_CONFIG1` fields for input-interface underflow recovery/status/interrupt, input pixel format, bits per component, slice width, and picture dimensions.
- `DSCCx_DSCC_CONFIG0`, `DSCCx_DSCC_CONFIG1`, `DSCCx_DSCC_STATUS`, and `DSCCx_DSCC_INTERRUPT_CONTROL_STATUS` fields for slice topology, ICH behavior, rate-control buffer model sizing, double-buffer update pending, rate-buffer overflow/underflow events, rate-control model overflow events, and interrupt enables.
- `DSCCx_DSCC_PPS_CONFIG0` through `DSCCx_DSCC_PPS_CONFIG22` fields for the packed DSC PPS programming described above.
- `DSCCx_DSCC_MEM_POWER_CONTROL`, channel squared-error counters, maximum absolute-error counters, and rate-buffer/rate-control-buffer maximum-fullness counters.

The DSC performance monitor blocks `DC_PERFMON20` through `DC_PERFMON23` follow DSC instances 1 through 4. Each perfmon block includes `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`. These fields cover performance counter enable/clear/mode, counter event selection, counter status readback, perfmon enable/clear modes, threshold and interrupt controls, trigger/window selection, and high/low counter-value readback.

The WB0 top block begins at `dce_dc_wb0_dispdec_dwb_top_dispdec`. It includes `DWB_ENABLE_CLK_CTRL`, `DWB_MEM_PWR_CTRL`, frame-capture controls (`FC_MODE_CTRL`, `FC_FLOW_CTRL`, `FC_WINDOW_START`, `FC_WINDOW_SIZE`, `FC_SOURCE_SIZE`), update locking/pending (`DWB_UPDATE_CTRL`), DWB CRC controls/masks/results, output format/range controls (`DWB_OUT_CTRL`), MMHUBBUB backpressure counters, host-read rate control, overflow status/counter, and soft reset.

`DC_PERFMON24` is the WB0 performance monitor with the same perfmon shape as the DSC perfmon instances. It is associated with the writeback path rather than a DSC encoder.

The WB0 DWB color-processing block begins at `dce_dc_wb0_dispdec_dwbcp_dispdec`. This chunk covers `DWB_HDR_MULT_COEF`, gamut-remap mode and coefficient format, both A and B gamut-remap coefficient matrices, output gamma (`DWB_OGAM`) mode/index/data/control registers, RAM A start/base/slope/end/offset fields for B/G/R channels, and RAM A region descriptors through regions 6 and 7.

## Important APIs, Types, And Macros

The important interface is the generated macro naming contract:

- `<register>__<field>__SHIFT` gives the bit offset for a field inside a 32-bit register.
- `<register>__<field>_MASK` gives the mask for that field.
- Comments such as `//DSCC2_DSCC_PPS_CONFIG0` and `// addressBlock: ...` delimit generated register groups but are not compiled APIs.
- Instance prefixes in this chunk include `DSC_TOP2` through `DSC_TOP4`, `DSCCIF2` through `DSCCIF4`, `DSCC1` through `DSCC4`, `DC_PERFMON20` through `DC_PERFMON24`, and unindexed WB0 names such as `DWB_ENABLE_CLK_CTRL`, `FC_MODE_CTRL`, `DWB_GAMUT_REMAP_MODE`, and `DWB_OGAM_CONTROL`.

The macros are consumed indirectly through AMD display register-list helpers. `display/dc/resource/dcn302/dcn302_resource.c` includes `dcn/dcn_3_0_2_offset.h` and this `dcn/dcn_3_0_2_sh_mask.h` header, builds DSC register arrays with `DSC_REG_LIST_DCN20(id)`, and initializes `dsc_shift`/`dsc_mask` with `DSC_REG_LIST_SH_MASK_DCN20(__SHIFT/_MASK)`. It creates DSC objects with `dsc2_construct(dsc, ctx, inst, &dsc_regs[inst], &dsc_shift, &dsc_mask)`.

The DSC field list is defined in `display/dc/dsc/dcn20/dcn20_dsc.h`. That header maps canonical field names such as `DSCC_PPS_CONFIG1.BITS_PER_PIXEL`, `DSCC_PPS_CONFIG3.SLICE_WIDTH`, `DSCC_CONFIG0.NUMBER_OF_SLICES_PER_LINE`, and `DSCC_MEM_POWER_CONTROL.DSCC_MEM_PWR_STATE` to the instance-0 generated macro names. The DCN register helper layer then pairs those generic shifts/masks with per-instance register addresses, allowing a single DSC implementation to program instances 0 through 4.

The DWB writeback macros are consumed through `display/dc/dwb/dcn30/dcn30_dwb.h`, where `DWBC_COMMON_REG_LIST_DCN30` names the top and color-processing registers and `DWBC_COMMON_MASK_SH_LIST_DCN30(__SHIFT/_MASK)` maps fields such as `FC_FRAME_CAPTURE_EN`, `DWB_CRC_EN`, `DWB_GAMUT_REMAPA_C11`, `DWB_OGAM_MODE`, and `DWB_OGAM_RAMA_EXP_REGION0_LUT_OFFSET`. In `dcn302_resource.c`, `dcn302_dwbc_create()` constructs one DCN30 DWBC instance from these register, shift, and mask tables.

The DWB color-management fields are used by `display/dc/dwb/dcn30/dcn30_dwb_cm.c`. That code programs `DWB_HDR_MULT_COEF`, alternates between gamut-remap A/B coefficient banks, reads `DWB_GAMUT_REMAP_MODE_CURRENT`, configures output-gamma RAM A/B selection through `DWB_OGAM_CONTROL`, writes `DWB_OGAM_LUT_INDEX` and `DWB_OGAM_LUT_DATA`, and programs PWL region descriptors with the `DWB_OGAM_RAMA_*` and `DWB_OGAM_RAMB_*` masks.

## Functional Field Groups

The DSCC PPS fields encode the Display Stream Compression picture parameter set into hardware registers. The chunk covers the dense packing of DSC wire-format parameters into 32-bit registers: version and component precision, bits per pixel, VBR, RGB conversion, native 4:2:0/4:2:2 flags, picture and slice geometry, chunk size, delay values, BPG offsets, RC model sizing, flatness and quantization constraints, RC target offsets, fourteen RC buffer thresholds, and fifteen range parameter triples. This is the core hardware programming surface for compressed display streams.

DSCC configuration and status fields describe how each encoder instance consumes slices and handles initial-code-history behavior. `NUMBER_OF_SLICES_PER_LINE`, `NUMBER_OF_SLICES_IN_VERTICAL_DIRECTION`, `ICH_RESET_AT_END_OF_LINE`, `ALTERNATE_ICH_ENCODING_EN`, and `DSCC_DISABLE_ICH` must match the DSC mode selected by link and timing code. `DSCC_DOUBLE_BUFFER_REG_UPDATE_PENDING` is the status bit that tells callers whether deferred updates are still waiting to take effect.

DSCC interrupt and telemetry fields expose underflow, overflow, and rate-control error conditions. The rate-buffer overflow/underflow bits and rate-control-buffer-model overflow bits are paired with interrupt-enable fields. Squared-error and max-absolute-error fields give diagnostic quality/error measurements for R/Y, G/Cb, and B/Cr channels. Maximum-fullness registers expose peak fullness for rate buffers and rate-control buffer models 0 through 3.

DSCC memory-power fields expose low-power controls and status for DSC memories, including default low-power state, force mode, disable bits, current memory state, and native 4:2:2 memory power controls. These fields tie DSC functionality to DCN power-management sequencing.

The `DC_PERFMON20` through `DC_PERFMON24` fields describe hardware performance counter configuration and readback. Counter-control fields select enable, clear, counter mode, clock enable, event selection, and threshold behavior. State fields expose status, error, current selected counters, and latched values. Perfmon control fields select trace/window behavior and trigger source, while low/high readback registers expose counter values.

The DWB top fields describe the writeback capture pipeline. Clock and memory-power fields control DWBC enable/gating and OGAM LUT memory power. Frame-capture fields select enable, capture rate, crop enable, stereo eye, stereo polarity, new-content flag, current capture state, window start/size, source size, and first-pixel delay. Update-control fields provide lock and pending status for double-buffered programming.

DWB CRC, overflow, backpressure, host-read, and output fields are validation and flow-control surfaces. CRC fields select one-shot/continuous mode and CRC source, then pack masks and signatures for red/green/blue/alpha. Output fields select output format, denormalization, and min/max clamp/range behavior. Overflow status fields report and acknowledge data overflow conditions, and the overflow counter/backpressure counter fields expose pressure in the writeback path.

DWB color-processing fields provide writeback-specific color correction. `DWB_HDR_MULT_COEF` applies HDR multiplier state. `DWB_GAMUT_REMAP_MODE`, `DWB_GAMUT_REMAP_COEF_FORMAT`, and A/B coefficient matrices provide banked color-space conversion. `DWB_OGAM_CONTROL`, LUT index/data/control, and RAM A region descriptors expose an output-gamma PWL LUT. The RAM A region table is only partially present in this chunk; it continues after `DWB_OGAM_RAMA_REGION_6_7`.

## Control Flow And State Behavior

This header has no direct control flow. Runtime behavior is created by macro expansion in resource initialization and register helper calls. DCN 3.0.2 resource setup binds addresses from `dcn_3_0_2_offset.h` and masks/shifts from this header into `dcn20_dsc` and `dcn30_dwbc` objects. Later DSC and DWB code uses those structures to read, write, or update memory-mapped hardware registers.

The hardware state described here persists in display-controller registers until changed by driver programming, firmware, reset logic, power-management transitions, or hardware status events. PPS registers, slice topology, memory-power control, frame-capture parameters, DWB output format, gamut coefficients, HDR multiplier, and OGAM LUT descriptors are configuration state. Overflow/underflow flags, max-fullness counters, perfmon counters, CRC result registers, current-mode bits, update-pending bits, and current memory-power state are live status or telemetry.

Several groups are timing-sensitive. DSCC and DWB update-pending fields indicate double-buffered updates that may not be active immediately after a register write. DSC PPS and slice fields must be programmed coherently before enabling compressed output. DWB frame capture and output-gamma programming similarly use stateful index/data windows and bank selection, so write ordering matters.

The DWB color path uses banked state. `dcn30_dwb_cm.c` reads current gamut-remap and OGAM mode state, programs the inactive A/B bank, then switches selection. For OGAM, LUT programming depends on `DWB_OGAM_LUT_HOST_SEL`, `DWB_OGAM_LUT_WRITE_COLOR_MASK`, `DWB_OGAM_LUT_INDEX`, and sequential writes to `DWB_OGAM_LUT_DATA`. A valid mask with the wrong bank or stale index still writes hardware, but to the wrong state.

Perfmon and CRC fields are stateful diagnostic windows. Clear/enable ordering, threshold/trigger selection, continuous versus one-shot mode, and read selection determine whether values represent the intended interval. Stale counters or pending one-shot state can make diagnostics misleading even when the field masks are correct.

## Dependencies And Integration Points

This file must stay synchronized with `dcn_3_0_2_offset.h`. The offset header provides `reg...` symbols for the same register names, while this header provides the field layout. A renamed or mismatched macro on either side can break compilation in generated register-list initializers or, worse, compile while programming the wrong hardware bits if the generated specification is inconsistent.

The main DCN 3.0.2 include site is `display/dc/resource/dcn302/dcn302_resource.c`. That file includes this header, creates five DSC objects, creates one DWBC object, and initializes their shared mask/shift tables with `DSC_REG_LIST_SH_MASK_DCN20` and `DWBC_COMMON_MASK_SH_LIST_DCN30`.

The DSC fields integrate with the DCN20 DSC implementation through `display/dc/dsc/dcn20/dcn20_dsc.h` and the `dsc2_construct()` path. Higher-level display code computes DSC mode feasibility and required DSCCLK in DML/resource code, then hardware sequencing programs DSC instances through these generated register fields. The chunk's PPS, slice, interrupt, memory-power, and telemetry fields are the low-level endpoint for that programming.

The DWB top and color-processing fields integrate with `display/dc/dwb/dcn30/dcn30_dwb.c`, `display/dc/dwb/dcn30/dcn30_dwb_cm.c`, and `display/dc/inc/hw/dwb.h`. Runtime paths update capture windows, enable/disable frame capture, set stereo parameters, program output format, enable DWB CRC, configure gamut remap, program output gamma, and apply HDR multiplier through these masks.

The writeback instance is also integrated through hardware sequencing in DCN30-family code. `dcn30_hwseq.c` connects writeback to the MPC DWB mux, updates DWBC parameters, enables DWBC, warms up MMHUBBUB/MCIF writeback state, and disables the DWB path when capture stops. The register fields in this chunk are the DWBC-side control/status surface for those operations.

The perfmon fields are generated metadata for diagnostic or profiling access. The visible resource constructors bind the masks, but this tree has fewer high-level named consumers for `DC_PERFMON20` through `DC_PERFMON24` than for the DSC and DWBC functional blocks. Likely users include register dumps, debug tooling, firmware-assisted diagnostics, or future instrumentation using the standard register helper layer.

## Risks And Edge Cases

The primary risk is generated-header drift from the hardware register specification or from the matching offset header. An incorrect shift or mask can corrupt DSC PPS programming, slice layout, memory power state, writeback capture parameters, CRC masks/results, gamut-remap coefficients, or output-gamma LUT region descriptors. These failures often appear as display corruption, failed compressed link training, bad writeback output, unreliable CRCs, or silent diagnostic errors rather than simple crashes.

The chunk starts and ends in partial logical regions. Instance 1 DSCC interrupt definitions are split with the previous chunk, and DWB OGAM RAM A definitions are split with the next chunk. Per-file reconciliation must merge adjacent chunk reports before claiming complete coverage of DSCC1 or DWB OGAM.

DSC PPS programming is packed and truncation-sensitive. Many fields are narrow bit ranges in shared 32-bit registers, and range parameters pack QP and BPG offsets tightly. Callers must clamp values to the protocol/hardware limits and use mask/shift helpers, especially for bits-per-pixel fixed-point values, picture/slice dimensions, delay intervals, BPG offsets, RC buffer thresholds, and range offsets.

DSC topology fields must match the stream, link, and clock plan. Wrong slice counts, picture dimensions, chunk size, or DSCCLK assumptions can create underflow/overflow events, stuck update-pending state, or an apparently valid mode that fails only under bandwidth pressure.

Interrupt/status fields combine event bits and enable bits in a single register for the older DSCC layout. Code that treats status bits as pure configuration, or that writes a full register value without preserving unrelated fields, can lose latched errors or accidentally enable/disable interrupt sources.

DWB color programming is banked and ordered. Gamut remap alternates A/B coefficient banks based on current mode, and OGAM alternates RAM A/B LUTs. Selecting a bank before all coefficient or LUT data is programmed can produce transient color errors in writeback. Programming the LUT data window with a stale index or wrong color mask writes valid values to the wrong component or entry.

DWB frame capture and CRC diagnostics are stateful. `FC_FRAME_CAPTURE_EN_CURRENT`, `DWB_UPDATE_PENDING`, overflow flags, CRC continuous/one-shot mode, CRC source selection, and CRC masks all affect how tests should interpret readback. Missing reset/clear sequencing can make captures or CRC comparisons look wrong even with correct register definitions.

Memory-power controls for DSCC and DWB OGAM LUT memory are sensitive to mode changes and suspend/resume. Forcing low-power or disabling memory while DSC or writeback color processing is active can cause failures that only reproduce around blanking, stream reconfiguration, hotplug, or power-management transitions.

## Test Signals

Build-time coverage should catch missing or renamed generated macros in `dcn302_resource.c`, `dcn20_dsc.h`, and `dcn30_dwb.h`. High-signal compile failures include missing `DSCC0_*`, `DSCCIF0_*`, `DWB_*`, `FC_*`, or `DWB_OGAM_*` field names referenced through `DSC_REG_LIST_SH_MASK_DCN20` or `DWBC_COMMON_MASK_SH_LIST_DCN30`.

DSC runtime validation should exercise compressed display modes on DCN 3.0.2 across DSC instances 1 through 4 where hardware routing permits. Useful signals include successful modesets with DSC enabled, correct PPS values in register dumps, no stuck `DSCC_DOUBLE_BUFFER_REG_UPDATE_PENDING`, no unexpected rate-buffer overflow/underflow interrupts, stable DSCCLK programming, and sane max-fullness/error counters under bandwidth-heavy modes.

Writeback validation should exercise frame-capture enable/disable, crop windows, source/window size programming, stereo fields where supported, output format/range controls, update locking, overflow status handling, and MMHUBBUB backpressure counters. Expected signals are correct captured dimensions and format, no unexpected overflow, and update-pending bits clearing after the intended update point.

Color/writeback validation should cover HDR multiplier programming, gamut-remap bypass and A/B bank switching, coefficient-format selection, output-gamma bypass and RAM LUT modes, LUT index/data writes, and current-mode readback. CRC-based comparisons of writeback output are useful because many color-path errors do not crash the driver.

Perfmon and CRC diagnostic tests should validate clear/enable/readback sequencing for `DC_PERFMON20` through `DC_PERFMON24`, low/high counter reads, trigger/window selection, DWB CRC masks, one-shot versus continuous CRC mode, and CRC source selection. Hardware register-spec cross-checks remain the strongest regression signal because this file is generated metadata.
