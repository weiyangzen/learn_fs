# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 22376-24894

## Scope

This chunk is a generated AMD DCN 3.0.2 ASIC register bitfield header segment. It contains preprocessor constants only: each hardware field is represented by a `__SHIFT` macro and a `_MASK` macro used by AMDGPU display code to compose and extract MMIO register fields. The chunk spans 2,519 source lines and includes 2,115 `#define` entries.

The range starts in the tail of `DC_PERFMON14_PERFCOUNTER_STATE`, covers the full DPP4 display pipe register surface for converter, scaler, color-management, cursor, and performance-monitor blocks, then covers the beginning of OPP0 output formatting and pipe CRC state. It ends on the `OPP_PIPE_CRC0_OPP_PIPE_CRC_RESULT2` register comment; the result2 field definitions are outside this exact chunk and must be reconciled by the adjacent chunk.

## Purpose

The purpose of this header segment is to expose symbolic bit positions for DCN 3.0.2 display hardware registers. Driver code includes `dcn_3_0_2_sh_mask.h` together with the matching offset header and uses these constants to build typed register tables for register helper read-modify-write operations.

The covered hardware area is display data processing and output processing:

- `DPP4` pipeline control, clock gating, soft reset, host read throttling, CRC, surface conversion, cursor, scaler, line-buffer, output buffer, and color-management fields.
- `CM4` color pipeline programming for pre/post CSC, gamut remap, gamma correction, blend gamma, shaper LUT, HDR multiplier, 3D LUT, memory power, and debug access.
- `DC_PERFMON14` and `DC_PERFMON15` performance monitor controls around DPP4.
- `FMT0`, `DPG0`, `OPPBUF0`, `OPP_PIPE0`, and most of `OPP_PIPE_CRC0`, which belong to output pixel processing for pipe 0.

The chunk is data-like source rather than executable logic. Its correctness depends on exact agreement with the AMD DCN 3.0.2 register specification and with `dcn_3_0_2_offset.h`.

## Address Blocks And Register Surface

Visible address blocks:

- Tail of `dce_dc_dpp4_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: final `DC_PERFMON14_PERFCOUNTER_STATE` masks plus `DC_PERFMON14_PERFMON_*` control, count value, interrupt, high, and low value fields.
- `dce_dc_dpp4_dispdec_dpp_top_dispdec`: `DPP_TOP4_DPP_CONTROL`, soft reset, DPP CRC value/control, and host read control.
- `dce_dc_dpp4_dispdec_cnvc_cfg_dispdec`: converter configuration, surface pixel format, format control, FP bias/scale, color keyer, 2-bit alpha LUT, pre-dealpha, pre-CSC matrix registers, pre-degamma, and pre-realpha fields.
- `dce_dc_dpp4_dispdec_cnvc_cur_dispdec`: cursor0 control, palette colors, and cursor floating-point scale/bias.
- `dce_dc_dpp4_dispdec_dscl_dispdec`: scaler coefficient RAM, scaling mode/taps, 2-tap sharpening, manual replication, horizontal/vertical ratios and init values, black color, update/autocal, overscan, timing blank references, recout, MPC size, line-buffer format/memory, DSCL memory power, and OBUF power/control.
- `dce_dc_dpp4_dispdec_cm_dispdec`: color-management control, post-CSC, gamut remap, gamma/blend-gamma LUT and piecewise-linear regions, HDR multiplier, memory power/status, dealpha, coefficient format, shaper LUT, 3D LUT, and test-debug fields.
- `dce_dc_dpp4_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: complete `DC_PERFMON15_*` counter and monitor controls for another perfmon selector in the DPP4 block.
- `dce_dc_opp_fmt0_dispdec`: FMT0 clamp, dynamic expansion, pixel encoding/subsampling, truncation, spatial/temporal dithering, random seeds, 4:2:0 memory power, and 4:2:2 edge control.
- `dce_dc_opp_dpg0_dispdec`: display pattern generator mode, dimensions, ramp, colors, segment offset, and double-buffer status.
- `dce_dc_opp_oppbuf0_dispdec`: active width, segmentation, overlap, repetition, 3D parameters, dummy data, and padded-pixel control.
- `dce_dc_opp_opp_pipe0_dispdec`: OPP pipe clock enable/status and digital bypass.
- `dce_dc_opp_opp_pipe_crc0_dispdec`: CRC control, CRC mask, result0, result1, and the opening comment for result2.

## Important Macros And Register Families

`DPP_TOP4_*` fields control the DPP4 block boundary: clock enable, multiple gate-disable knobs, test clock selection, soft reset for CNVC/DSCL/CM/OBUF subblocks, and DPP CRC one-shot/continuous mode, source, stereo/interlace/pixel-format selection, and component results.

`CNVC_CFG4_*` and `CNVC_CUR4_*` fields describe input conversion. They cover surface pixel format, alpha-plane enable, bypass/MSB alignment, 16-bit conversion, positive clamp modes, channel crossbar selection, color key ranges, alpha LUT entries, FP bias/scale, pre-dealpha/re-alpha, pre-degamma mode/select, pre-CSC coefficient format, and cursor mode/enable/ROM/pixel-inversion/alpha modulation.

`DSCL4_*` fields describe scaling and line-buffer behavior. The register families include coefficient RAM tap selection/data, scale modes, tap counts, 2-tap sharpening, chroma/luma ratios and initial phases, black fill color, recout and MPC dimensions, autocalibration, overscan, OTG blank windows, line-buffer interleave/alpha/memory partitioning, live line-buffer counters, and memory-power controls/status for LUT, data, and coefficient memories.

`CM4_*` is the largest family in this chunk. It provides post-CSC and gamut-remap matrix fields, bias, gamma-correction and blend-gamma LUT controls, RAM A/B region descriptors from regions 0-33, start/end/slope/base/offset values per RGB component, shaper LUT controls and regions, HDR multiplier, dealpha, coefficient format, 3D LUT mode/index/data/read-write/out normalization/out offsets, memory power controls/status for gamma/blend/shaper/3D LUT memories, and indexed debug access.

`DC_PERFMON14_*` and `DC_PERFMON15_*` define display performance counter control surfaces. They include event select, counted value type, increment/run-enable mode, hardware stop controls, count-off selection, interrupt enable/status/ack, active state, report count, read selector, and split high/low count values.

`FMT0_*` fields describe the output formatter: component clamp bounds, dynamic expansion, pixel encoding, subsampling mode/order, CbCr bit-reduction bypass, double-buffer update pending, truncation, spatial/temporal dithering, random seed and per-channel offsets, clamp enable/color format, side-by-side stereo width, 4:2:0 memory power state, and 4:2:2 left-edge extra pixel count.

`DPG0_*`, `OPPBUF0_*`, `OPP_PIPE0_*`, and `OPP_PIPE_CRC0_*` describe output-pipe support. DPG fields configure internal test pattern generation and expose double-buffer pending state. OPPBUF fields control active width, segmentation, overlap, pixel repetition, 3D vertical-active spacing, dummy RGB data, and padded segment pixels. OPP pipe fields gate the pipe clock and enable digital bypass. CRC fields enable one-shot or continuous CRC collection and expose stereo/interlace/source/pixel-select controls plus component result registers.

## Control Flow And Runtime Behavior

There is no C control flow in this chunk. Runtime behavior is indirect: `dcn302_resource.c` includes `dcn/dcn_3_0_2_sh_mask.h`, creates DPP and OPP register shift/mask tables, and passes those tables into hardware block constructors.

For DPP, `dcn302_resource.c` defines `tf_shift` and `tf_mask` from `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`, then passes them to `dpp3_construct()` for instances 0-4. The `DPP_REG_LIST_SH_MASK_DCN30` macro in `dcn30_dpp.h` expands through `TF_SF(...)`/`TF2_SF(...)` entries for the same logical fields represented here, using instance-0 names such as `CM0_*`, `CNVC_CFG0_*`, and `DSCL0_*`. The generated DCN header supplies equivalent instance-specific macros; this chunk is the instance-4 register-data source used when the generated field names are expanded for DPP4.

For OPP, `dcn302_resource.c` defines `opp_shift` and `opp_mask` from `OPP_MASK_SH_LIST_DCN20(__SHIFT)` and `OPP_MASK_SH_LIST_DCN20(_MASK)`, then passes them to `dcn20_opp_construct()` for instances 0-4. The OPP mask lists in `dcn10_opp.h` and `dcn20_opp.h` consume fields such as `FMT0_FMT_BIT_DEPTH_CONTROL`, `FMT0_FMT_CONTROL`, `FMT0_FMT_MAP420_MEMORY_CONTROL`, `DPG0_*`, `OPPBUF0_*`, and `OPP_PIPE0_*`, all present in this chunk.

Hardware-oriented flows represented by the fields include:

- DPP block enable/reset and CRC capture through `DPP_TOP4_*`.
- Surface format conversion, alpha handling, cursor composition, and pre-CSC/pre-degamma setup through `CNVC_CFG4_*` and `CNVC_CUR4_*`.
- Scaling setup through coefficient RAM programming, tap selection, scale ratios, recout/MPC dimensions, autocalibration, and DSCL update bits.
- Color processing through pre/post CSC, gamut remap, gamma/blend/shaper LUT programming, HDR multiplier, and 3D LUT read/write controls.
- Formatter and output-pipe setup through FMT0 bit-depth/dither/subsampling/clamp controls, DPG pattern generation, OPP buffer segmentation, and OPP pipe clocking.
- Performance and validation flows through perfmon counters, DPP CRC, OPP pipe CRC, memory power status, double-buffer pending fields, and indexed debug data.

## State And Persistence

The macros themselves hold no mutable state and introduce no storage. They describe persistent hardware state in memory-mapped display registers. Writes through these fields can affect device state until overwritten, reset, power-gated, or restored during display reinitialization.

Several field groups represent latched or handshake state:

- Double-buffer and update state: `CNVC_UPDATE_PENDING`, `DSCL_UPDATE`, `FMT_DOUBLE_BUFFER_REG_UPDATE_PENDING`, `DPG_DOUBLE_BUFFER_PENDING`, `OPPBUF_DOUBLE_BUFFER_PENDING`, and CRC one-shot pending fields expose hardware update synchronization and must be polled or cleared according to register-specific semantics.
- Memory power state: `DSCL4_DSCL_MEM_PWR_CTRL/STATUS`, `DSCL4_OBUF_MEM_PWR_CTRL`, `CM4_CM_MEM_PWR_CTRL/STATUS`, `CM4_CM_MEM_PWR_CTRL2/STATUS2`, and `FMT0_FMT_MAP420_MEMORY_CONTROL` contain force/disable/default-low-power/state fields. Incorrect programming can leave memories powered unnecessarily or unavailable while LUT/scaler data is being used.
- Indexed/table state: gamma, blend-gamma, shaper, and 3D LUT index/data/control registers represent internal RAM programming windows. Host code must coordinate index selection, read/write control, host select, and color write masks.
- Status and ack state: perfmon count-off and per-counter interrupt status/ack fields, CRC status/result registers, and DPG/OPPBUF pending bits are hardware-observed state. Masks do not document whether a bit is write-one-to-clear, read-only, sticky, or self-clearing.

## Dependencies And Integration Points

This chunk depends on companion generated headers for the same IP version:

- `dcn_3_0_2_offset.h` supplies register addresses and base indices.
- `dcn_3_0_2_sh_mask.h` supplies the shift/mask values in this chunk.
- Resource construction code in `display/dc/resource/dcn302/dcn302_resource.c` selects these generated headers for the DCN 3.0.2 ASIC path.
- DPP integration comes through `display/dc/dpp/dcn30/dcn30_dpp.h` register and mask-list macros and through `dpp3_construct()`.
- OPP integration comes through `display/dc/opp/dcn10/dcn10_opp.h`, `display/dc/opp/dcn20/dcn20_opp.h`, and `dcn20_opp_construct()`.
- Runtime register access uses AMD display helper macros that combine a register address table with the generated mask/shift tables to write packed bitfields without open-coded bit positions.

The chunk also intersects display validation and debug paths: CRC collection, DPG test patterns, perfmon counters, memory power reporting, and test-debug index/data registers are all observable signals used when bring-up or diagnosing display failures.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask can overwrite adjacent bits in a 32-bit MMIO register, causing blank displays, incorrect color conversion, scaler failures, cursor corruption, bad dithering, CRC mismatches, or power-management regressions.
- The range begins after the start of `DC_PERFMON14_PERFCOUNTER_STATE` and ends before the `OPP_PIPE_CRC0_OPP_PIPE_CRC_RESULT2` field definitions. The final file report must merge adjacent chunks before treating either register family as complete.
- Field names ending in `_MASK_MASK` are legitimate generated names when the logical field is named `..._MASK`. Parsers or scripts that strip `_MASK` naively can mis-handle fields such as DPP/OPP CRC mask registers and other bitmask-valued fields.
- DPP4 is an instance of a repeated pipe family. Code often defines tables from instance-0 macro names and generates per-instance register addresses separately; reviewers should avoid assuming that all visible `*4` macros are directly referenced by name in hand-written C even though they are part of the generated register namespace.
- Table programming registers are sequencing-sensitive. Gamma, blend, shaper, and 3D LUT data paths require correct index/control/host-select ordering; the masks alone do not encode required delays, locks, or double-buffer handshakes.
- Power-control fields combine force, disable, default-low-power, and state fields in adjacent bit ranges. A mask typo or wrong write value can silently change power behavior for LUT, scaler, OBUF, or formatter memories.
- Perfmon and CRC status/ack bits can be sticky or self-clearing depending on hardware semantics. Consumers must not infer safe acknowledge behavior from the masks alone.

## Test Signals

Useful validation signals for this chunk include:

- Compile coverage for the DCN 3.0.2 resource path, especially `dcn302_resource.c`, `dcn30_dpp.h`, `dcn10_opp.h`, and `dcn20_opp.h`, to catch missing or renamed generated macros.
- Generated-header consistency checks that verify every full field has a matching `__SHIFT` and `_MASK`, masks fit within 32 bits, masks align with shifts, and repeated pipe instances are consistent where the hardware spec requires parity.
- Display mode-set tests that exercise DPP4 enable/reset, scaling, cursor, pre/post CSC, gamut remap, gamma/blend/shaper LUTs, 3D LUT programming, HDR multiplier, and output formatter dithering/clamping/subsampling.
- Hardware validation using DPP CRC, OPP pipe CRC, DPG test patterns, DSCL line-buffer counters, perfmon counts, and debug index/data registers.
- Suspend/resume and power-gating tests that verify DSCL, OBUF, CM, shaper, 3D LUT, and FMT 4:2:0 memory power controls are restored correctly and do not leave pending double-buffer updates.
- Negative/regression checks for common symptoms: black screen after mode set, wrong cursor colors or alpha, scaler artifacts, incorrect HDR/gamut output, unexpected dither/truncation, stale LUT contents, CRC mismatch, perfmon interrupt storms, or memory power state stuck in forced-on/forced-off.

## Open Questions For Merge Lane

- Confirm the adjacent previous chunk supplies the full opening context for `DC_PERFMON14_PERFCOUNTER_STATE`.
- Confirm the adjacent next chunk supplies the `OPP_PIPE_CRC0_OPP_PIPE_CRC_RESULT2` shift/mask definitions and then continues into `FMT1`.
- Compare the DPP4 instance fields in this chunk against DPP0-DPP3 chunks for intentional instance differences versus generation defects.
- Map which of the many visible `CM4_*` LUT and 3D LUT fields are actually reachable through current DCN 3.0.2 color-management code and which are reserved for debug or future feature paths.
