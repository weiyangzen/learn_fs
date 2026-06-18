# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 29961-32471

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains no executable C code; its interface is a set of preprocessor constants that name bit shifts and bit masks for memory-mapped display hardware registers.

The source path is under a local `ceph-client` mirror, but this file is Linux AMDGPU display-driver ASIC metadata. It does not implement Ceph filesystem behavior.

The range covers the tail of the output pixel processor instance 5 mask list and the beginning of the OPTC timing-generator mask list:

- `FMT5_*` formatter fields for blue-channel clamp, dynamic expansion, format control, bit-depth/truncation/dither, random dither seeds, clamp enable/color format, side-by-side stereo, 4:2:0 memory power, and 4:2:2 left-edge chroma handling.
- `DPG5_*` display pattern generator fields for enable/mode, dynamic range, bit depth, resolution, ramp control, active dimensions, two pattern colors in RGB/YUV component registers, segment offset/width, and double-buffer pending status.
- `OPPBUF5_*`, `OPP_PIPE5_*`, and `OPP_PIPE_CRC5_*` fields for OPP buffer segmentation/3D dummy data, OPP pipe clock/bypass control, and output-pipe CRC enable/modes/masks/results.
- `OPP_TOP_CLK_CONTROL` and `DSCRM[0-5]_DSCRM_DSC_FORWARD_CONFIG` fields for OPP-level clock gating and DSC forwarding control per output.
- `DC_PERFMON18_*` fields for the OPP display performance monitor control, counter state, current values, interrupt status/acknowledge bits, and high/low readback.
- `ODM[0-5]_OPTC_*` fields for OPTC input routing, data format/DSC mode, bytes per pixel, segment/slice width, input clock state, memory selection, underflow status/clear, and spare registers.
- Full `OTG0_*` and `OTG1_*` timing-generator field definitions, spanning horizontal/vertical timings, VRR/DRR totals, trigger controls, flow control, stereo/interlace state, timing status/readback, update locks, master enable, blank/black colors, vertical interrupts, CRC windows/results, static-screen controls, 3D structure, global sync lock, vstartup/vupdate/vready events, DSC start position, and pipe-update status.
- The beginning of `OTG2_*`, from horizontal total through `OTG2_OTG_V_TOTAL_CONTROL`, before the OTG2 interrupt/status section continues in the next chunk.

Each field appears as a pair of generated constants:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position used to pack or unpack a field.
- `<REGISTER>__<FIELD>_MASK`: the field mask within the 32-bit register value.

These constants are paired with register offsets from `dcn_2_0_0_offset.h` and consumed through AMD display register-access helpers. They are hardware ABI data: correctness depends on matching the DCN 2.0 register specification.

## Important APIs, Types, And Macros

There are no functions, structs, enums, typedefs, variables, or storage objects in this range. The important API is the generated macro namespace used by register table initializers and access helpers.

Important macro families in this chunk:

- `FMT5_FMT_CONTROL__*` describes output format controls such as stereo sync override, PTI field polarity, spatial dither frame counter settings, pixel encoding, subsampling mode/order, CbCr bit-reduction bypass, double-buffer pending status, and PTI enable. These fields inform formatter programming for the sixth OPP instance.
- `FMT5_FMT_BIT_DEPTH_CONTROL__*` describes truncation, spatial dithering, temporal dithering, randomization, temporal reset, and FRC selection fields. Consumers use these masks when configuring panel/output bit depth and dithering behavior.
- `FMT5_FMT_DITHER_RAND_{R,G,B}_SEED__*`, `FMT5_FMT_CLAMP_*`, `FMT5_FMT_MAP420_MEMORY_CONTROL__*`, and `FMT5_FMT_422_CONTROL__*` define seed, offset, clamp, 4:2:0 memory-power, and 4:2:2 extra-left-pixel controls.
- `DPG5_DPG_CONTROL__*`, `DPG5_DPG_RAMP_CONTROL__*`, `DPG5_DPG_DIMENSIONS__*`, and `DPG5_DPG_COLOUR_*__*` define pattern-generator configuration used for test output and diagnostics.
- `OPPBUF5_OPPBUF_CONTROL__*`, `OPPBUF5_OPPBUF_3D_PARAMETERS_*__*`, and `OPPBUF5_OPPBUF_CONTROL1__*` define active width, display segmentation, overlap, pixel repetition, 3D vactive spacing, dummy RGB data, and segment padding.
- `OPP_PIPE5_OPP_PIPE_CONTROL__*` describes OPP pipe clock enable/on status and digital bypass.
- `OPP_PIPE_CRC5_OPP_PIPE_CRC_*__*` describes CRC enable, continuous/one-shot mode, stereo/interlace mode, pixel/source select, mask, and A/R/G/B/C result fields for output validation.
- `OPP_TOP_CLK_CONTROL__OPP_TOP_CLOCK_ENABLE` and `OPP_TOP_CLK_CONTROL__OPP_TOP_CLOCK_ON` expose top-level OPP clock state.
- `DSCRM[0-5]_DSCRM_DSC_FORWARD_CONFIG__DSCRM_DSC_FORWARD_EN` and `DSCRM_DSC_OPP_SOURCE_SELECT` expose DSC forwarding and source selection for each descrambler instance.
- `DC_PERFMON18_PERFCOUNTER_*` and `DC_PERFMON18_PERFMON_*` describe event selection, current-value selection, increment mode, hardware start/stop/counter-off controls, active state, interrupt enable/status/ack bits, report count, clock enable, current-value high/low, and readback selector fields.
- `ODM[0-5]_OPTC_INPUT_GLOBAL_CONTROL__*` exposes input soft reset, underflow interrupt enable/type/status, underflow clear/current status, and double-buffer pending bits for each OPTC input.
- `ODM[0-5]_OPTC_DATA_SOURCE_SELECT__*`, `OPTC_DATA_FORMAT_CONTROL__*`, `OPTC_BYTES_PER_PIXEL__*`, and `OPTC_WIDTH_CONTROL__*` describe ODM segmentation, source selection, DSC mode, compressed bytes per pixel, segment width, and DSC slice width.
- `OTG[0-2]_OTG_H_TOTAL__OTG_H_TOTAL`, `OTG_H_BLANK_START_END__*`, `OTG_H_SYNC_A__*`, `OTG_V_TOTAL__*`, `OTG_V_BLANK_START_END__*`, and `OTG_V_SYNC_A__*` are the core timing fields for horizontal/vertical totals, blanking windows, and sync windows.
- `OTG[0-2]_OTG_V_TOTAL_CONTROL__*` describes variable-refresh and dynamic refresh behavior: min/max total selection, mid-total substitution, lock-on-event, DRR active period, set-min mask enable/value, and mid-frame count.
- `OTG0_*` and `OTG1_*` include additional timing-generator fields for interrupts, triggers, flow control, stereo, interlace, status, snapshots, update locks, double buffering, CRC, static-screen detection, global sync lock, master update lock, manual flow control, range timing update, DRR readback, DSC start position, and pipe update status.

The local consumers do not generally reference instance 5 names directly. Instead, common field tables use instance 0 field names and indexed register-offset macros to describe all instances. For example, `display/dc/opp/dcn20/dcn20_opp.h` builds `struct dcn20_opp_shift` and `struct dcn20_opp_mask` through `OPP_MASK_SH_LIST_DCN20(__SHIFT)` and `OPP_MASK_SH_LIST_DCN20(_MASK)`, while `display/dc/optc/dcn10/dcn10_optc.h` builds timing-generator mask/shift tables through `TG_COMMON_MASK_SH_LIST_DCN(...)`. The repeated instance 5 and OTG1/OTG2 field definitions must remain numerically consistent with instance 0 for indexed helpers to be valid.

## Control Flow

This chunk has no runtime control flow. It is declarative mask/shift data.

Runtime control flow appears in consumers that include `dcn_2_0_0_sh_mask.h` and use these fields through generated tables:

- `display/dc/resource/dcn20/dcn20_resource.c` includes this header and initializes DCN20 block register, shift, and mask tables. For OPP, it populates `opp_shift` and `opp_mask` with `OPP_MASK_SH_LIST_DCN20`; for OPTC it uses timing-generator masks through DCN10/DCN20 OPTC structures.
- `display/dc/opp/dcn20/dcn20_opp.c` updates formatter 4:2:2 behavior with `REG_UPDATE(FMT_422_CONTROL, FMT_LEFT_EDGE_EXTRA_PIXEL_COUNT, count)` and reads OPP state with `REG_READ(DPG_CONTROL)`, `REG_READ(FMT_CONTROL)`, `REG_READ(OPP_PIPE_CONTROL)`, `REG_READ(OPP_PIPE_CRC_CONTROL)`, `REG_READ(OPPBUF_CONTROL)`, and `REG_READ(DSCRM_DSC_FORWARD_CONFIG)`.
- `display/dc/optc/dcn10/dcn10_optc.c` writes horizontal timing via `REG_SET(OTG_H_TOTAL, OTG_H_TOTAL, patched_crtc_timing.h_total - 1)`, writes sync fields with `REG_UPDATE_2`, programs variable refresh behavior through `REG_UPDATE_5(OTG_V_TOTAL_CONTROL, ...)`, reads hardware timing and underflow status with `REG_GET`, clears underflow with `REG_UPDATE(OPTC_INPUT_GLOBAL_CONTROL, OPTC_UNDERFLOW_CLEAR, 1)`, and derives `max_h_total`/`max_v_total` from the mask values.
- `display/dc/irq/dcn20/irq_service_dcn20.c` maps vupdate and vblank IRQ entries through `OTG_GLOBAL_SYNC_STATUS` fields such as `VUPDATE_NO_LOCK_INT_EN`, `VUPDATE_NO_LOCK_EVENT_CLEAR`, `VSTARTUP_INT_EN`, and `VSTARTUP_EVENT_CLEAR`.
- `display/dmub/src/dmub_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, and `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c` include the same generated mask header for DCN20 service and hardware-resource integration.

The generated constants do not enforce sequencing. Correct sequencing is in the block drivers: modeset code must program timings and source routing in the right order, use update locks and double-buffer controls around latched registers, handle underflow clear bits as side-effecting operations, and avoid reading CRC/perfmon/status fields before hardware has produced stable values.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. It defines how software encodes and decodes hardware register state.

The represented hardware state includes:

- Persistent display programming state, such as formatter clamp/dither/bit-depth controls, OPP buffer segmentation, ODM source routing, DSC mode, segment width, OTG timing totals, blank/sync windows, master enable, black/blank colors, stereo/interlace controls, and DSC start position.
- Double-buffered state, indicated by fields such as `FMT_DOUBLE_BUFFER_REG_UPDATE_PENDING`, `DPG_DOUBLE_BUFFER_PENDING`, `OPPBUF_DOUBLE_BUFFER_PENDING`, `OPTC_DOUBLE_BUFFER_PENDING`, `OTG_UPDATE_PENDING`, `OTG_MASTER_UPDATE_LOCK`, and `UPDATE_LOCK_STATUS`. These values may be staged and latched at vertical update boundaries rather than taking effect immediately.
- Status and counter state, such as OPP pipe CRC result registers, OTG pixel/status/readback counters, frame counts, snapshot status, perfmon current values, perfmon counter state, and `OTG_PIPE_UPDATE_STATUS` flip/DC/cursor update bits.
- Interrupt and sticky event state, such as underflow interrupt/status/clear, `OTG_V_TOTAL_INT_STATUS`, `OTG_GLOBAL_SYNC_STATUS`, vertical interrupt controls, range timing update status, and perfmon interrupt status/ack fields.
- Power and clock state, such as `FMT_MAP420MEM_PWR_*`, `OPP_PIPE_CLOCK_EN/ON`, `OPP_TOP_CLOCK_ENABLE/ON`, and `OPTC_INPUT_CLK_EN/ON/GATE_DIS`.

Persistence is hardware-defined. Some fields remain programmed until modeset, suspend/resume, reset, power gating, or explicit rewrite. Other fields are read-only status, sticky status cleared by writing a clear/ack bit, self-clearing trigger bits, or current counter snapshots. The macro names reveal likely behavior but not access permissions, reset values, write-one-to-clear semantics, or clock-domain timing requirements.

## Dependencies And Integration Points

This chunk depends on the AMD generated ASIC register-header contract:

- `dcn_2_0_0_offset.h` supplies the matching MMIO register offsets and base indices.
- This `dcn_2_0_0_sh_mask.h` range supplies the bit packing contract for the same registers.
- AMD display register helpers such as `REG_READ`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `SRI`, `OPP_SF`, and indexed register-list macros consume the generated constants.
- DCN20 resource construction wires offsets, shifts, and masks into block-specific structs such as OPP and timing-generator register tables.

Important local integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`

Functional integration points are display modeset programming, page-flip/vblank timing, variable refresh and DRR, ODM combine/split routing, DSC output positioning, formatter color/depth/chroma programming, output diagnostics through pattern generation and CRC, OPP/OPTC performance monitoring, underflow detection/clear, global-sync lock behavior, and IRQ routing for vblank/vupdate/vline-style events.

## Risks And Edge Cases

- Generated mask/shift values are hardware ABI. A wrong mask or shift can compile cleanly and still program the wrong bits, causing black screens, flicker, timing instability, bad color, invalid CRCs, stuck interrupts, or hangs.
- The chunk boundary is not semantic. It starts after earlier `FMT5` fields already appeared in the previous chunk and ends in the middle of the `OTG2` register bank. Per-file synthesis must merge adjacent chunk results before making complete claims about FMT5 or OTG2 coverage.
- Repeated per-instance banks are vulnerable to instance drift. `FMT5`, `DPG5`, `OPPBUF5`, `OPP_PIPE5`, `OPP_PIPE_CRC5`, `DSCRM[0-5]`, `ODM[0-5]`, `OTG0`, `OTG1`, and `OTG2` fields must remain aligned with their offset-header instance mappings and with the field tables that often use instance 0 as the canonical mask source.
- OTG fields are timing critical. Incorrect horizontal/vertical totals, blanking, sync polarity, vtotal min/max/mid, update-lock, trigger, global-sync, or DSC start-position masks can produce modeset failures, missed vblank, bad VRR/DRR pacing, multi-display sync failures, or invalid DSC output.
- Underflow fields have side effects. `OPTC_UNDERFLOW_CLEAR` and related interrupt bits must be handled as hardware status/clear controls; using a regular read-modify-write without understanding semantics can lose diagnostic state or fail to clear sticky status.
- CRC and perfmon fields mix control, status, and acknowledge semantics. Bad masks can leave CRC one-shot pending, sample the wrong channel/window, acknowledge the wrong counter interrupt, or report misleading diagnostic data.
- Formatter and dither fields directly affect visible output. Wrong bit-depth, truncation, temporal/spatial dithering, random seed, clamp, 4:2:0 memory, or 4:2:2 left-edge masks can cause banding, chroma artifacts, incorrect color range, or power-state bugs that only appear on particular output formats.
- Clock and power bits can be asynchronous or status-only. `*_CLOCK_EN`, `*_CLOCK_ON`, memory power state, and clock-gate-disable fields should be treated according to block driver sequencing rather than inferred solely from names.
- The header has no type checking. Masks are `L` integer constants and shifts are untyped preprocessor values, so invalid cross-register use may not be caught by the compiler if names happen to fit helper macros.

## Test Signals

Useful validation signals are mostly compile-time and hardware/display behavioral checks:

- Build AMDGPU/DC with DCN20 enabled. Missing or renamed macros should fail in DCN20 resource, OPP, OPTC, IRQ, DMUB, GPIO, and clock-manager code paths.
- Diff this generated chunk against the matching `dcn_2_0_0_offset.h` register names and adjacent DCN family mask headers to catch accidental register-bank omissions, instance drift, or unexpected field-width changes.
- Exercise DCN20 modesets on hardware across single-display, multi-display, ODM/split, DSC, stereo/interlace where supported, suspend/resume, and hotplug paths.
- Validate OTG behavior: vblank delivery, page-flip completion, vline interrupts, frame counters, horizontal/vertical active size readback, update-lock behavior, global-sync/vupdate/vstartup/vready events, VRR/DRR min/max/mid changes, and DSC start position.
- Validate OPP/formatter behavior: output bit depth, truncation/dither modes, random seed effects, clamp configuration, RGB/YUV pixel encodings, 4:2:0/4:2:2 output formats, and absence of visible banding or chroma-edge artifacts.
- Validate diagnostics: DPG pattern output on pipe 5, OPP pipe CRC one-shot and continuous modes, OTG CRC windows/results, perfmon counter start/stop/interrupt/ack behavior, and debug state readbacks.
- Watch kernel logs and display symptoms for negative signals: underflow reports, missed vblank/page-flip timeouts, stuck update pending bits, black screens, flicker, bad colors, CRC mismatches, HPD or resume regressions caused by broader DCN20 integration, and clock/power transition warnings.
