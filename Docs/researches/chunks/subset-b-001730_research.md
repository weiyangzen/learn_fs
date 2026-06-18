# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 19931-22460

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.1 register shift/mask table. It contains C preprocessor constants that describe bit positions (`__SHIFT`) and masks (`_MASK`) for memory-mapped display hardware registers. The companion offset header supplies register addresses; this header supplies field layout metadata consumed by AMD display register helpers.

The requested range starts inside the `dce_dc_dpp3_dispdec_cm_dispdec` color-management address block, beginning after the first `CM3_CM_POST_CSC_B_C11_C12` line and continuing through the rest of the DPP3 color pipeline registers. It then covers the `DC_PERFMON13` performance-monitor address block and the OPP formatter, display-pattern-generator, output buffer, output-pipe, and output-pipe CRC blocks for OPP instances 0, 1, and 2. The range ends inside instance 3 after `DPG3_DPG_COLOUR_G_Y`, so the later DPG3, OPPBUF3, OPP_PIPE3, and CRC3 fields continue in the next chunk.

There are no executable functions, structs, or runtime branches in this chunk. The exported surface is a dense set of 2,115 macro definitions. The highest-density region is `CM3`, which contributes most of the macros because programmable piecewise-linear LUT RAM A/B region tables are expanded into per-field definitions.

## Register Blocks Covered

The first portion completes DPP3 color-management (`CM3`) fields. It covers post-CSC bank B coefficients, gamut-remap control and coefficients for primary and bank B coefficient sets, bias registers, gamma-correction control and LUT access, gamma-correction RAM A/B region descriptors, blend-gamma control and LUT access, blend-gamma RAM A/B region descriptors, HDR multiplier, CM memory power control and status, dealpha control, coefficient format selection, shaper LUT control and RAM A/B region descriptors, additional CM memory power controls, 3D LUT mode/index/data/read-write/output normalization fields, and CM test/debug index/data registers.

The `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` block covers `DC_PERFMON13`. It provides field layouts for performance-counter control, counter-window and event selection, trigger selection and trigger masks, performance-monitor enable and clear state, counter-state readback, thresholding, and low/high counter-value readback registers.

The `FMT0` through `FMT3` blocks cover OPP formatter fields. Each formatter instance includes RGB component clamps, dynamic expansion enable/mode, pixel encoding, subsampling mode and order, CbCr bit-reduction bypass, double-buffer update-pending status, bit-depth truncation, spatial dithering, temporal dithering, random seed registers, clamp enable/color format, side-by-side stereo active width, 4:2:0 formatter memory power controls, and 4:2:2 left-edge extra-pixel count.

The `DPG0` through partial `DPG3` blocks cover display pattern generators. Instances 0, 1, and 2 are complete in this slice and include enable/mode/dynamic-range/bit-depth/resolution controls, ramp controls, active dimensions, two packed colors per RGB/YCbCr component register, offset/segment width, and double-buffer pending status. Instance 3 begins at line 22426 and is covered only through `DPG3_DPG_COLOUR_G_Y`; `DPG3_DPG_COLOUR_B_CB`, offset/segment, and status fields continue after the requested range.

The `OPPBUF0` through `OPPBUF2` blocks cover output-buffer fields. They define active width, display segmentation, overlap pixels, pixel repetition, double-buffer pending status, 3D vertical-active space sizes, dummy RGB data, and padded-pixel count.

The `OPP_PIPE0` through `OPP_PIPE2` blocks define output-pipe clock and bypass fields: clock enable, clock-on status, and digital bypass enable.

The `OPP_PIPE_CRC0` through `OPP_PIPE_CRC2` blocks define output-pipe CRC capture controls, mask, and result registers. They include CRC enable, continuous mode, stereo and interlace modes, pixel/source selection, one-shot pending status, a 16-bit mask, and packed A/R/G/B/C result fields.

## Important APIs, Types, And Macros

The important API is the generated macro naming contract:

- `<register>__<field>__SHIFT` gives the bit offset for packing or extracting a hardware field.
- `<register>__<field>_MASK` gives the field mask in the 32-bit register value.
- Register comments such as `//CM3_CM_GAMCOR_CONTROL` and address-block comments such as `// addressBlock: dce_dc_opp_fmt0_dispdec` delimit generated register groups but are not themselves C APIs.
- Instance prefixes in this chunk include `CM3`, `DC_PERFMON13`, `FMT0` through `FMT3`, `DPG0` through `DPG3`, `OPPBUF0` through `OPPBUF2`, `OPP_PIPE0` through `OPP_PIPE2`, and `OPP_PIPE_CRC0` through `OPP_PIPE_CRC2`.

These macros are consumed indirectly through AMD display register-list helpers such as `SF`, `SRI`, `TF_SF`, `OPP_SF`, `REG_READ`, `REG_GET`, `REG_SET`, and `REG_UPDATE`. For DCN 3.0.1, `display/dc/resource/dcn301/dcn301_resource.c` includes this header, builds `dpp_regs[]` with `DPP_REG_LIST_DCN30(id)`, initializes `tf_shift` and `tf_mask` with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT/_MASK)`, builds `opp_regs[]` with `OPP_REG_LIST_DCN30(id)`, and initializes `opp_shift` and `opp_mask` with `OPP_MASK_SH_LIST_DCN20(__SHIFT/_MASK)`.

The DPP color fields are used by DCN DPP code paths such as `dcn10_dpp_cm.c`, `dcn20_dpp.c`, and `dcn30_dpp.c`. Those modules program or read gamut remap, post-CSC, gamma correction, blend gamma, shaper LUT, and 3D LUT state through the generic register tables whose field layouts come from this header. The OPP formatter and pattern-generator fields are wired through `dcn10_opp.h` and `dcn20_opp.h`, where `OPP_MASK_SH_LIST_DCN20` references `FMT0_*`, `DPG0_*`, and `OPPBUF0_*` field names as the canonical mask/shift source for every OPP instance.

## Functional Field Groups

Post-CSC and gamut-remap fields provide matrix-style color transforms. The chunk includes the tail of `CM3_CM_POST_CSC_B_*` and full `CM3_CM_GAMUT_REMAP_*` and `CM3_CM_GAMUT_REMAP_B_*` coefficient sets. Coefficients are packed as 16-bit halves in paired registers such as C11/C12 and C33/C34, while control registers expose selected and current modes. The banked forms allow drivers to program an alternate coefficient set and switch modes around frame-synchronized update points.

Gamma-correction and blend-gamma fields expose programmable PWL LUTs. `CM3_CM_GAMCOR_*` and `CM3_CM_BLNDGAM_*` include mode/select/current bits, LUT index/data/control registers, per-channel start/end slope/base/offset fields, and RAM A/B region tables from region 0 through 33. The region table fields pair LUT offsets with segment counts, while separate endpoint fields describe start and end behavior per color channel. Blend gamma mirrors this structure for the later blend/output gamma stage.

The shaper and 3D LUT fields support the DCN color pipeline used for HDR and wide-gamut workflows. The shaper block includes per-channel offsets/scales, LUT access fields, write-enable and RAM-select controls, and RAM A/B region tables. The 3D LUT block includes mode/current status, index, data, 30-bit data path fields, read/write control, output normalization factor, and per-channel output offsets. These fields integrate with the color capability flags in the DCN 3.0.1 resource setup, where post-CSC, gamma correction, hardware 3D LUT, and output gamma RAM are advertised.

Memory-power and debug fields include `CM3_CM_MEM_PWR_CTRL`, `CM3_CM_MEM_PWR_STATUS`, `CM3_CM_MEM_PWR_CTRL2`, `CM3_CM_MEM_PWR_STATUS2`, `CM3_CM_TEST_DEBUG_INDEX`, and `CM3_CM_TEST_DEBUG_DATA`. They describe force/disable/mode/state fields for CM memories and indexed debug read/write access.

`DC_PERFMON13` fields describe hardware performance counter configuration. Control fields select counter enables, clear actions, counter modes, clock enable, event selection, threshold enable, windowing, and trigger selection. State and value registers expose current counter status and low/high counter values. These registers are diagnostic and profiling surfaces rather than display-mode programming knobs.

Formatter (`FMTx`) fields control final stream formatting before link/pipe output. They include clamp bounds, dynamic expansion, pixel encoding, 4:2:0/4:2:2 controls, truncation and dither mode/depth/seed fields, temporal dither reset/offset/FRC selectors, memory power state for 4:2:0 mapping memory, and double-buffer update-pending status. These fields are used when programming output bit depth, YCbCr packing, dithering, and clamp behavior.

Display pattern generator (`DPGx`) fields generate test patterns in the OPP path. Control fields select enable, pattern mode, dynamic range, bit depth, horizontal/vertical resolution, and field polarity. Dimensions, color, ramp, and segment fields describe the generated pattern geometry and colors. Status exposes double-buffer pending state.

OPP buffer and pipe fields describe output buffering and clock/bypass state. `OPPBUFx` active width, segmentation, overlap, pixel repetition, 3D parameters, dummy data, and padded-pixel count support segmented output and stereo/3D formatting. `OPP_PIPEx` clock enable/on and digital bypass bits control the pipe-level output path.

OPP pipe CRC fields support validation and diagnostics. CRC controls enable one-shot or continuous capture, select stereo/interlace behavior, choose pixel/source selection, and report one-shot pending state. Result registers return packed 16-bit component CRC values.

## Control Flow And State Behavior

This file has no direct control flow. Runtime behavior is created by macro expansion in display-core register helpers. DCN 3.0.1 resource initialization binds register addresses from the offset header and field masks/shifts from this header into per-block register, shift, and mask structs. Later DPP and OPP code calls generic helpers such as `REG_SET`, `REG_UPDATE`, and `REG_GET`; those helpers use the bound shift/mask fields to modify memory-mapped registers.

The hardware state described here persists in display-controller registers until driver code, firmware, reset logic, power-management logic, or hardware event logic changes it. Matrix coefficient registers, LUT region descriptors, formatter settings, pattern generator parameters, OPP buffer settings, and pipe clock controls are configuration state. Current-mode fields, memory-power state fields, double-buffer pending bits, clock-on bits, CRC pending bits, performance counter state, and counter readback fields are live hardware status.

Several field groups are explicitly banked or double-buffered. CM gamma, blend-gamma, and shaper RAM A/B fields allow programming one RAM bank while another is active. Mode/current fields indicate requested versus active color-pipeline state. FMT, DPG, and OPPBUF pending bits indicate delayed register updates. Programming code must account for frame-synchronized updates, RAM bank ownership, and pending-state completion rather than assuming an immediate visible change.

LUT access registers are stateful index/data windows. `*_LUT_INDEX`, `*_LUT_DATA`, `*_LUT_CONTROL`, `*_3DLUT_INDEX`, and `*_3DLUT_DATA*` operations depend on the current index and selected channel/RAM bank. Incorrect ordering can write valid values to the wrong component, bank, or LUT entry.

## Dependencies And Integration Points

This header must stay aligned with `dcn_3_0_1_offset.h`, which provides the addresses for the same generated register names. A mask/shift macro without the matching address macro, or vice versa, breaks the generated resource tables or silently misprograms hardware if names are mismatched.

The direct DCN 3.0.1 include sites found for this header are `display/dc/resource/dcn301/dcn301_resource.c` and `display/dmub/src/dmub_dcn301.c`. The resource file is the key integration point for this chunk because it instantiates DPP and OPP register tables for four pipes and binds the field metadata through `tf_shift`, `tf_mask`, `opp_shift`, and `opp_mask`.

The DPP fields integrate with `display/dc/dpp/dcn30/dcn30_dpp.c`, `display/dc/dpp/dcn20/dcn20_dpp.c`, and older shared DPP color-management helpers. Examples include state reads for `CM_GAMCOR_CONTROL`, `CM_SHAPER_CONTROL`, `CM_3DLUT_MODE`, and `CM_BLNDGAM_CONTROL`; post-CSC programming through `CM_POST_CSC_CONTROL` and coefficient registers; blend-gamma LUT programming through `CM_BLNDGAM_LUT_*`; and region descriptor programming through `CM_BLNDGAM_RAMA_*` masks.

The OPP fields integrate with shared OPP definitions in `display/dc/opp/dcn10/dcn10_opp.h` and `display/dc/opp/dcn20/dcn20_opp.h`. Those headers define the canonical OPP field lists for formatter dithering, clamp, dynamic expansion, 4:2:0 memory power, OPP buffer segmentation, pattern-generator setup, and output-pipe clock state. DCN 3.0.1 uses the DCN 3.0 OPP register list while still relying on the DCN 2.0-era mask list for the common fields present in this chunk.

The performance-monitor fields are generated register metadata for the DPP3 performance monitor. This tree has fewer visible high-level consumers for `DC_PERFMON13` than for DPP and OPP color/output fields, so the likely users are diagnostic/debug paths, register dumps, firmware interactions, or future perf-counter instrumentation that accesses the generated register names through the same register-helper layer.

## Risks And Edge Cases

The primary risk is drift between the generated header, the offset header, and the hardware register specification. A single bad mask or shift can target the wrong bits in a memory-mapped register, causing wrong colors, broken HDR/3D LUT behavior, incorrect dithering, missing pattern-generator output, bad CRC results, stuck power states, or unreliable diagnostics.

The chunk begins and ends at partial block boundaries. It starts after the first fields for `CM3_CM_POST_CSC_B_C11_C12`, and it ends before the DPG3 block is complete. Merge/reconciliation must combine adjacent chunks before drawing per-file conclusions about complete DPP3 or OPP3 coverage.

Banked color LUT programming is sensitive to RAM selection and current-mode state. Confusing RAM A and RAM B fields, or switching mode before a bank is fully programmed, can create transient or persistent color corruption. The same caution applies to `*_CURRENT` fields: they are readback/status indicators, not always the same as the requested mode fields.

Packed coefficient and color fields are truncation-sensitive. Many matrix and color registers pack two 16-bit fields into one 32-bit register, while LUT and offset fields use 18- or 19-bit masks. Callers must clamp and pack values through the generated masks rather than assuming natural C integer widths map directly to hardware fields.

Formatter and output-buffer updates are timing-sensitive. Dither, truncation, pixel encoding, subsampling, segmentation, overlap, and active-width settings must match stream timing and link encoding. Incorrect values can manifest as color banding, chroma ordering errors, edge artifacts, or update-pending bits that do not clear as expected.

CRC and perfmon fields are diagnostic but still stateful. CRC one-shot pending, continuous capture, source selection, and mask fields can produce misleading test results if not reset between captures. Performance-counter clear/enable/window/trigger fields can similarly produce stale or partial values if programmed out of order.

Memory power fields need care around low-power transitions. Forcing, disabling, or changing default low-power modes for CM or FMT memories while the corresponding LUT or formatter path is active can cause subtle failures that only appear during blanking, resume, mode changes, or multi-pipe configurations.

## Test Signals

Build-time tests should catch missing or renamed macros through failures in `dcn301_resource.c`, DPP mask/shift initialization, and OPP mask/shift initialization. High-signal errors include missing `CM3_*`, `FMT0_*`, `DPG0_*`, `OPPBUF0_*`, or `OPP_PIPE0_*` identifiers referenced through `SF`, `TF_SF`, `OPP_SF`, `DPP_REG_LIST_SH_MASK_DCN30`, or `OPP_MASK_SH_LIST_DCN20`.

Runtime display validation should exercise DCN 3.0.1 hardware across all four DPP/OPP instances. Useful signals include successful modesets, stable scanout, correct color output with post-CSC and gamut-remap changes, correct gamma/blend-gamma/shaper/3D-LUT behavior, and no stuck double-buffer pending or memory-power state during mode changes and suspend/resume.

Color-management tests should cover RAM A/B LUT programming, current-mode readback, HDR multiplier behavior, 3D LUT 30-bit paths, and state dumps from `dcn30_dpp.c` paths. Visual or CRC-based comparisons are useful because many failures are silent register misprogramming rather than crashes.

OPP tests should cover truncation, spatial and temporal dithering, RGB and YCbCr pixel encodings, 4:2:0 and 4:2:2 formatting, clamp ranges, active width and segmentation, pixel repetition, and side-by-side stereo parameters where supported.

Diagnostic tests should validate DPG-generated patterns, OPP pipe CRC capture in one-shot and continuous modes, and performance-counter clear/enable/readback sequencing. Because the file is generated metadata, the strongest regression signal is a combination of hardware-register database cross-checks, compile coverage of every generated field list, and hardware smoke tests that touch each display pipe instance represented by the chunk.
