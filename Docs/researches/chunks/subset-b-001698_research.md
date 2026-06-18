# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 27352-29904

## Scope

This chunk is a generated AMDGPU DCN 3.0.0 register shift/mask header slice. It contains preprocessor constants only: no functions, structs, enums, global storage, or executable code. The exported surface is the usual generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macro pairs consumed by AMD display register helpers.

The range covers 2,553 source lines and 2,137 `#define` entries: 1,061 shift constants and 1,076 mask constants. The imbalance is caused by artificial chunk boundaries. The first line starts inside `CM5_CM_SHAPER_RAMA_START_CNTL_R`, after its first shift macro appeared in the previous chunk, and the last line starts `ODM5_OPTC_BYTES_PER_PIXEL`, whose mask and following ODM5 fields continue in the next chunk.

The covered hardware areas are late DPP5 color-management registers, DPP5 and OPP display performance monitors, six repeated OPP/FMT/DPG/OPPBUF/CRC instances, OPP top-level clock and ABM controls, six DSC-remapper forwarding blocks, and the beginning of six ODM/OPTC input blocks.

## Purpose

The file maps DCN 3.0.0 hardware bitfields to C macros so higher-level display code can program MMIO registers by field name instead of hard-coding bit numbers. This chunk supplies field layouts for:

- `CM5` color-management shaper RAM A/B region programming, shaper and 3D LUT memory power controls/status, 3D LUT indexed data access, output normalization/offset/scale, and test-debug index/data access.
- `DC_PERFMON17` under `dce_dc_dpp5_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`, exposing DPP5 display performance counter setup, state, run control, interrupt status/ack, and counter value readback.
- `FMT0` through `FMT5`, covering output formatter clamp ranges, dynamic expansion, pixel encoding, subsampling, truncation, spatial/temporal dithering, random seeds, 4:2:0 memory power, and 4:2:2 edge handling.
- `DPG0` through `DPG5`, the display pattern generator blocks for test pattern enablement, mode, dynamic range, bit depth, resolution fields, ramp controls, colors, offsets, segment width, and double-buffer pending status.
- `OPPBUF0` through `OPPBUF5`, output pixel-processor buffer width/segmentation/repetition/3D-parameter/padding fields.
- `OPP_PIPE0` through `OPP_PIPE5`, pipe clock and digital bypass controls.
- `OPP_PIPE_CRC0` through `OPP_PIPE_CRC5`, CRC enable/mode/source/mask/result fields for output validation.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`, top-level OPP clock gating/test-clock/ABM clock-on fields and ABM backlight PWM selection.
- `DSCRM0` through `DSCRM5`, DSC forwarding enable/source/status and double-buffer pending fields.
- `DC_PERFMON18` under `dce_dc_opp_opp_dcperfmon_dc_perfmon_dispdec`, exposing the OPP-level performance counter block.
- `ODM0` through the start of `ODM5`, describing OPTC input global reset/underflow/double-buffer fields, data source segment selection, DSC data format, bytes-per-pixel, width, input-clock, memory-select, and spare-register fields. `ODM5` is partial in this chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this source is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed-storage, or network behavior.

## Important APIs, Types, And Macros

There are no callable APIs or C types here. The API-like contract is the macro namespace:

- `*_SHIFT` gives the low bit position for a register field.
- `*_MASK` gives the already-shifted register mask for that field.
- Register-heading comments group the generated fields for one MMIO register.
- `addressBlock` comments identify generated hardware register blocks, not C scopes.

Important macro families in this chunk include:

- `CM5_CM_SHAPER_RAMA_*` and `CM5_CM_SHAPER_RAMB_*`: start/end controls per RGB channel and 34 exponential-region descriptors packed as region pairs. Region descriptors use LUT offset fields and segment-count fields, while start/end controls expose 18-bit or 16-bit range fields plus base/segment selectors.
- `CM5_CM_MEM_PWR_CTRL2` and `CM5_CM_MEM_PWR_STATUS2`: power force/disable and state fields for shaper and HDR 3D LUT memories.
- `CM5_CM_3DLUT_*`: mode/size/current-mode fields, 11-bit index, packed 16-bit data lanes, 30-bit data access, write-enable mask, RAM/read selectors, output normalization, and per-channel output offset/scale.
- `CM5_CM_TEST_DEBUG_INDEX` and `CM5_CM_TEST_DEBUG_DATA`: an indexed debug access pair with an 8-bit index, write-enable bit, and 32-bit data value.
- `DC_PERFMON17_*` and `DC_PERFMON18_*`: performance counter control fields such as event select, counted value select/type, increment mode, run-enable mode, hardware stop/start selectors, active state, counter state selectors, report count, counter-off interrupt status/ack, eight per-counter interrupt status/ack bits, and low/high value readback.
- `FMTn_FMT_*`: six repeated formatter instances. `FMT_BIT_DEPTH_CONTROL` is the densest formatter register, packing truncation, spatial dithering, temporal dithering, randomization, FRC selection, and reset fields. `FMT_CONTROL` carries stereo override, dither frame counter fields, pixel encoding, subsampling mode/order, CbCr bit-reduction bypass, and double-buffer pending status.
- `DPGn_DPG_*`: repeated pattern generator fields for enable, mode, dynamic range, bit depth, horizontal/vertical resolution encoding, field polarity, ramp offset/increment, active dimensions, two colors per component, X offset, segment width, and double-buffer pending.
- `OPPBUFn_OPPBUF_*` and `OPP_PIPEn_OPP_PIPE_CONTROL`: active width, display segmentation, overlap pixels, pixel repetition, pending status, 3D vactive space sizes, dummy RGB data, segment padding, pipe clock enable/on state, and digital bypass.
- `OPP_PIPE_CRCn_*`: per-pipe CRC enable, continuous mode, stereo/interlace modes, pixel/source select, one-shot pending, mask, and A/R/G/B/C result fields.
- `DSCRMn_DSCRM_DSC_FORWARD_CONFIG`: `DSCRM_DSC_FORWARD_EN`, `DSCRM_DSC_OPP_PIPE_SOURCE`, `DSCRM_DSC_DOUBLE_BUFFER_REG_UPDATE_PENDING`, and `DSCRM_DSC_FORWARD_EN_STATUS`.
- `ODMn_OPTC_*`: input soft reset, underflow interrupt enable/type/status/clear/current, double-buffer pending, input/output segment counts, segment source selectors, data format, DSC mode, DSC bytes per pixel, segment/slice widths, input clock gate/enable/on state, memory select, and spare register data.

## Control Flow

This chunk has no local control flow. Runtime behavior is supplied by consumers that include `dcn_3_0_0_offset.h` and this shift/mask header, build generation-specific register tables, and then access MMIO through AMD display helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_WAIT`, and `REG_READ`.

A typical path is:

1. DCN30/DCN302 display code includes the offset and shift/mask headers.
2. Register-list macros paste instance names such as `FMT0_FMT_CONTROL`, `DPG0_DPG_CONTROL`, `DSCRM0_DSCRM_DSC_FORWARD_CONFIG`, or `ODM0_OPTC_INPUT_GLOBAL_CONTROL` into address, shift, and mask initializers.
3. OPP, DPP, DSC, ODM/OPTC, IRQ, clock, GPIO, or DMUB runtime code issues field-level register reads and writes during resource construction, modeset, pipe programming, color pipeline setup, DSC routing, diagnostics, interrupt handling, or power transitions.
4. The generated masks and shifts isolate the requested bitfields while preserving unrelated bits in the same register.

The control-sensitive flows represented by this chunk include shaper/3D LUT programming, DPP/OPP performance counter start/stop/interrupt handling, output formatting and dithering, display pattern generation, output CRC collection, OPP pipe clocking, DSC forwarding to an OPP pipe, and ODM input segment routing. The header does not encode sequencing rules, write-one-to-clear behavior, self-clearing bits, read-only status fields, clock-domain requirements, or double-buffer commit timing.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It describes hardware register state in the DCN 3.0 display pipeline. That state lives in display-controller registers and persists according to hardware reset, display pipe reprogramming, power gating, suspend/resume, modeset, and driver reinitialization behavior.

State represented here includes:

- Color pipeline state for DPP5 shaper RAM region topology, shaper/HDR LUT memory power mode, 3D LUT mode/size/index/data, output normalization, and RGB output offset/scale.
- Diagnostic state for CM5 indexed test-debug access and DPP/OPP performance monitors, including active counter selection, run state, counter states, interrupt enable/status/ack, and value readback.
- OPP formatter state for clamp ranges, dynamic expansion, truncation and dithering configuration, random seeds, pixel encoding, subsampling, stereo override, 4:2:0 memory power, 4:2:2 extra pixel handling, and double-buffer pending flags.
- Pattern generator state for generated output test patterns, dimensions, colors, ramp parameters, segment placement, field polarity, and pending updates.
- Output buffer and pipe state for active width, segmentation, overlap, pixel repetition, 3D padding/dummy data, pipe clock enables, clock-on readback, and digital bypass.
- CRC capture state for per-pipe output CRC source/mode/mask/result and one-shot pending status.
- DSC forwarding state for each `DSCRM` instance, including enable, selected OPP pipe source, enable status, and double-buffer pending.
- ODM/OPTC input state for soft reset, underflow interrupt tracking, segment source mapping, data/DSC format, width fields, input clock gating/enablement, memory selection, and spare register contents.

Many fields are configuration latches, while others are live status or interrupt/status-ack fields. Misprogrammed configuration can persist until the next modeset, stream revalidation, color-management update, CRC/debug teardown, DSC reprogramming, power transition, or GPU reset.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which supplies the matching MMIO addresses and base indices. Examples from that companion include `mmCM5_CM_SHAPER_RAMA_START_CNTL_R`, `mmCM5_CM_3DLUT_MODE`, `mmDC_PERFMON17_PERFCOUNTER_CNTL`, `mmFMT0_FMT_CONTROL`, `mmDPG0_DPG_CONTROL`, `mmOPPBUF0_OPPBUF_CONTROL`, `mmOPP_PIPE_CRC0_OPP_PIPE_CRC_CONTROL`, `mmDSCRM0_DSCRM_DSC_FORWARD_CONFIG`, `mmDC_PERFMON18_PERFCOUNTER_CNTL`, and `mmODM0_OPTC_INPUT_GLOBAL_CONTROL`.

Visible include sites for the DCN 3.0.0 offset and shift/mask headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Important consuming abstractions are the common DPP, OPP, DSC, ODM/OPTC, IRQ, clock-manager, GPIO, and DMUB register-table patterns. For example, OPP code uses `OPP_SF(...)`, `REG_UPDATE(FMT_CONTROL, ...)`, `REG_UPDATE(DPG_CONTROL, ...)`, and `REG_READ(OPP_PIPE_CRC_CONTROL)` style helpers; DSC code uses `DSCRM_DSC_FORWARD_CONFIG` fields to route DSC forwarding to OPP pipes; color-management paths use DPP shaper and 3D LUT fields through DPP register tables.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. These macros compile as constants; an incorrect shift or mask can write a neighboring field, truncate a value, fail to clear stale bits, misread status, or make a wait loop observe the wrong condition.

Chunk boundaries are not hardware boundaries. The first three lines finish `CM5_CM_SHAPER_RAMA_START_CNTL_R` after the previous chunk supplied `CM_SHAPER_RAMA_EXP_REGION_START_R__SHIFT`. The final line supplies only `ODM5_OPTC_BYTES_PER_PIXEL__OPTC_DSC_BYTES_PER_PIXEL__SHIFT`; its mask and the remaining `ODM5` width, clock, memory, and spare-register fields continue in the next chunk. Reconciliation must merge adjacent chunks before declaring complete coverage for those registers.

The repeated instance blocks create copy-generation hazards. `FMT0` through `FMT5`, `DPG0` through `DPG5`, `OPPBUF0` through `OPPBUF5`, `OPP_PIPE_CRC0` through `OPP_PIPE_CRC5`, `DSCRM0` through `DSCRM5`, and `ODM0` through `ODM5` should be structurally aligned except where the range is partial. A single wrong instance prefix or drifted field width could make only one pipe fail.

Color and formatter fields are user-visible. Bad shaper, 3D LUT, clamp, dynamic expansion, bit-depth, dither, pixel encoding, or subsampling constants can produce wrong colors, banding, crushed ranges, invalid YCbCr output, stereo formatting problems, or failures that appear only with HDR, LUT updates, or non-RGB formats.

Double-buffer and pending bits need correct masks. `FMT_DOUBLE_BUFFER_REG_UPDATE_PENDING`, `DPG_DOUBLE_BUFFER_PENDING`, `OPPBUF_DOUBLE_BUFFER_PENDING`, `DSCRM_DSC_DOUBLE_BUFFER_REG_UPDATE_PENDING`, and `OPTC_DOUBLE_BUFFER_PENDING` are synchronization/status fields. Incorrect definitions can cause premature programming, missed waits, or hangs in register wait paths.

Performance monitor and CRC fields mix control, status, interrupt, and readback semantics. Wrong interrupt status/ack masks can leave perf counter interrupts stuck or lost. Wrong CRC source/mode/result masks can make debugfs or validation CRCs look mismatched even when the pixel stream is correct.

Clock and power fields can affect availability of downstream state. Misusing `OPP_PIPE_CLOCK_EN`, `OPP_PIPE_CLOCK_ON`, `OPP_DISPCLK_*_GATE_DIS`, `FMT_MAP420MEM_PWR_*`, `SHAPER_MEM_PWR_*`, or `HDR3DLUT_MEM_PWR_*` can lead to reads from gated blocks, failed LUT access, or intermittent programming failures across power transitions.

ODM and DSC fields are display-topology sensitive. Bad `OPTC_SEGn_SRC_SEL`, segment-count fields, DSC mode, bytes-per-pixel, slice width, or DSC forwarding source can route pixels from the wrong segment or pipe, break DSC pass-through, or cause underflow conditions on multi-pipe or compressed-display configurations.

## Test Signals

Useful validation signals include:

- Build coverage for DCN30/DCN302 resource, IRQ, GPIO, clock-manager, DMUB, OPP, DPP, DSC, and ODM/OPTC paths that include `dcn_3_0_0_sh_mask.h`.
- Generated-header checks that every field has a shift/mask pair where the complete register is in the chunk, masks align with shifts, and every register has a matching address in `dcn_3_0_0_offset.h`.
- Cross-generation diffs against adjacent DCN headers such as `dcn_2_1_0_sh_mask.h`, `dcn_3_0_1_sh_mask.h`, and later DCN 3.x headers, with expected ASIC differences reviewed against the register database.
- Pipe-by-pipe structural checks across `FMTn`, `DPGn`, `OPPBUFn`, `OPP_PIPE_CRCn`, `DSCRMn`, and `ODMn` instances to catch accidental instance-specific drift.
- Color-management tests for shaper LUT and 3D LUT programming, HDR modes, LUT bypass/enable transitions, suspend/resume, and memory power state transitions.
- Display format tests covering RGB and YCbCr, 4:2:0, 4:2:2, dithering/truncation paths, bit-depth changes, stereo override, and clamp/dynamic-expansion behavior.
- Pattern generator tests for solid color, ramp, dimensions, segment offsets, dynamic range, and bit-depth settings on all six pipes.
- CRC validation through output CRC/debugfs or internal test hooks, checking continuous and one-shot captures, stereo/interlace modes, source select, masks, and result registers.
- DSC/ODM topology tests for single-pipe, multi-pipe, DSC-enabled, ODM-combine/split, and underflow recovery paths.
- Performance monitor tests that start/stop counters, select events, read low/high values, trigger and acknowledge counter interrupts, and verify no stuck interrupt status remains.

Regression symptoms from bad constants include wrong color output, banding, failed HDR LUT programming, display underflow, incorrect DSC routing, blank or partially routed displays in ODM modes, stuck double-buffer waits, missing or false CRC mismatches, invalid performance counter values, stuck perfmon interrupts, and pipe-specific failures that reproduce only on one generated instance.

## Cross-Chunk Notes

This chunk is one slice of the large generated `dcn_3_0_0_sh_mask.h` file. The previous chunk owns the beginning of `CM5_CM_SHAPER_RAMA_START_CNTL_R`; this chunk owns the rest of CM5 shaper/3D LUT material and the majority of OPP/ODM material described above; the next chunk continues `ODM5_OPTC_BYTES_PER_PIXEL` and the remaining ODM5 fields. The final per-file research document should treat this as part of the DCN 3.0.0 generated register-layout contract rather than a standalone module.
