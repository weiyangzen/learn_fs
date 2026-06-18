# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 22677-25260

## Scope

This chunk is a generated AMD DCN 3.2.1 register shift/mask header segment. It contains C preprocessor constants only: `__SHIFT` macros give field low-bit positions and `_MASK` macros give positioned masks for hardware register fields. There are no C functions, structs, enums, branches, loops, allocations, locks, or direct MMIO operations in this range.

The slice covers 2,584 source lines with 2,114 `#define` entries, including 1,061 shift definitions and 1,070 mask definitions, grouped by 374 register comments. It starts inside the `ABM2_DC_ABM1_LS_SUM_OF_LUMA` register group: the register comment is at line 22676, just before this chunk. It ends inside `OTG1_OTG_V_TOTAL_CONTROL`: the shift definitions are in this chunk, while that register's masks begin at line 25261 and continue after the chunk. Merge-time reconciliation should treat both boundary register groups as partial.

## Purpose

This header is part of the generated register ABI for the AMDGPU Display Core. Matching offset headers define register addresses; this `*_sh_mask.h` file defines the bit layout used by register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and related DC register table initialization code. Runtime display code includes the header through the DCN 3.2.1 resource path, notably `display/dc/resource/dcn321/dcn321_resource.c`, which includes both `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`.

The hardware surface in this chunk spans the output/display-tail side of DCN:

- The tail of `dce_dc_opp_abm2_dispdec` and the full `dce_dc_opp_abm3_dispdec` block for ambient backlight management, luma statistics, histogram results, adaptive contrast enhancement, PWM level calculation, and ABM register locks.
- Repeated OPP pipe instances 0-3 for display pattern generation (`DPG`), output formatter (`FMT`), output processor buffer (`OPPBUF`), pipe clock/bypass control, and OPP pipe CRC.
- DSC remap (`DSCRM0..3`) forwarding configuration and OPP top-level clock/ABM selection.
- ODM/OPTC input blocks 0-3 for output data merger input reset, underflow status/interrupts, segment source selection, DSC format/bytes-per-pixel, segment widths, input clocks, and memory selection.
- The complete `OTG0` timing generator field set in this slice and the start of `OTG1`, covering mode timing, triggers, status, interrupts, CRC, static-screen detection, global sync lock, double-buffer/update locking, dynamic refresh rate, DSC start position, and pipe update status.

## Important APIs And Data Shapes

The only API exposed here is the macro namespace. Each complete field normally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit index for the field.
- `<REGISTER>__<FIELD>_MASK`, the field mask in register position.

The comments are generated structure:

- `// addressBlock: ...` marks hardware address-block transitions such as `dce_dc_opp_fmt0_dispdec`, `dce_dc_optc_odm0_dispdec`, and `dce_dc_optc_otg0_dispdec`.
- `//<REGISTER>` introduces the following field definitions until the next register comment.

Important definition families in this range include:

- ABM2/ABM3 luma and histogram state: `*_LS_SUM_OF_LUMA`, `*_LS_MIN_MAX_LUMA`, `*_LS_FILTERED_MIN_MAX_LUMA`, `*_LS_PIXEL_COUNT`, min/max pixel threshold/count registers, `*_HG_SAMPLE_RATE`, `*_LS_SAMPLE_RATE`, histogram bin shift/index registers, and `*_HG_RESULT_1..24`.
- ABM/PWM and ACE controls: `ABM3_BL1_PWM_*` ambient/user/target/current/final/minimum duty-cycle fields, `ABM3_BL1_PWM_ABM_CNTL`, sample-rate and group-2 lock fields, `ABM3_DC_ABM1_CNTL`, IPCSC coefficient selection, ACE offset/slope and threshold fields, ACE missed-frame status, HGLS read-progress status, HGLS locks, and `ABM*_BL_MASTER_LOCK`.
- DPG 0-3: `DPG_CONTROL`, ramp control, active dimensions, two-color RGB/YCbCr values, offset segment, and double-buffer-pending status for test-pattern or generated-display output.
- FMT 0-3: component clamp lower/upper bounds, dynamic expansion, pixel encoding and subsampling fields, truncation/spatial/temporal dithering controls, random seed and offset values, clamp format, side-by-side stereo active width, 4:2:0 memory power controls, and 4:2:2 edge handling.
- OPPBUF and OPP pipe 0-3: active width, display segmentation, overlap pixels, pixel repetition, 3D spacing/dummy data, padded segment pixels, pipe clock enable/on status, and digital bypass.
- OPP pipe CRC 0-3: CRC enable/continuous/one-shot controls, stereo and interlace selection, pixel/source selection, CRC masks, and A/R/G/B/C result fields.
- DSCRM/OPP top: DSC forward-map controls per instance, OPP display-clock gate/test-clock/ABM-clock status, and backlight PWM selection.
- ODM 0-3: soft reset, underflow interrupt/status/clear/current flags, double-buffer pending, number of input/output segments, segment source selectors, data format, DSC mode, DSC bytes per pixel, segment and DSC slice width, input clock gating/enabled/on status, memory selection/status, and spare registers.
- OTG0: horizontal/vertical totals and blank/sync windows, variable vertical-total controls and status, nominal vsync status, trigger A/B controls, force-count-now, flow control, stereo/interlace controls and status, pixel/status readback, counters, snapshot controls, interrupt controls, update locks, double-buffer controls, master enable, vertical interrupts 0-2, CRC windows/results/masks, static-screen detection, 3D structure, GSL timing, master-update mode/locks, vstartup/vupdate/vready timing, global sync status, GSL windows, global control, DRR interrupt/range/change/window/control fields, M-constant DTO, DSC start position, and pipe-update status.
- OTG1 beginning: H total, H blank/sync, H sync control, H timing divider, V total/min/max/mid, and the shift side of V total control.

## Control Flow And State Behavior

This header has no executable control flow. Runtime behavior is implied by callers that combine these masks with register offsets and perform MMIO reads/writes.

Typical display flows represented by the fields are:

1. Panel/backlight code programs ABM and PWM fields, then reads luma statistics, histogram bins, min/max counts, filtered values, update-pending bits, missed-frame status, and lock status.
2. OPP construction and stream enablement code configures generated patterns, formatter clamp/dither/subsampling, OPP buffer segmentation, pipe clock/bypass state, and pipe CRC capture.
3. DSC/ODM setup code routes compressed or uncompressed data through DSCRM and ODM/OPTC input blocks, selecting segments, slice widths, bytes per pixel, memory configuration, and input clocks while checking underflow and double-buffer status.
4. OTG code programs timing totals, sync/blank ranges, master enable, interlace/stereo behavior, trigger and flow-control sources, vstartup/vupdate/vready windows, update locks, vertical interrupts, DRR windows, GSL, CRC windows, and DSC start position.
5. Diagnostics and validation paths read OTG counters/status, snapshot registers, CRC results, static-screen events, underflow state, ABM statistics, OPP pipe CRC values, and pipe update pending flags.

The state represented here is hardware register state:

- Persistent programmed state includes PWM and ABM control values, ACE threshold and slope values, DPG pattern parameters, FMT clamp/dither/pixel-format controls, OPP buffer segmentation, pipe clock/bypass bits, ODM source/format/width/memory settings, OTG timing, update-lock windows, interrupt masks/types, CRC windows, DRR settings, GSL parameters, and DSC start positions.
- Volatile readback includes luma/histogram statistics, filtered min/max luma, ABM/HGLS read/update/missed-frame bits, DPG/OPP/FMT/ODM double-buffer pending flags, OPP pipe CRC results, underflow status/current bits, clock-on status, OTG current master-enable state, interlace/stereo status, HV/frame/VF counters, snapshot data, interrupt occurrence/status bits, CRC data, static-screen state, global sync status, DRR events, and pipe update pending bits.
- Sequencing-sensitive fields include register-lock/master-lock bits, readback-double-buffer selects, update-at-frame-start controls, underflow clear bits, OTG master/update locks, double-buffer enable/update-pending controls, interrupt clear/ack fields, one-shot CRC and trigger clear bits, DRR timing updates, GSL/master-update locking, and soft reset/clock-enable fields.

## Dependencies And Integration Points

The definitions depend on exact agreement with the DCN 3.2.1 register specification and with `dcn_3_2_1_offset.h`. A missing macro usually fails the build; an incorrect shift or mask can compile cleanly while causing wrong hardware programming.

Primary integration points are:

- `display/dc/resource/dcn321/dcn321_resource.c`, which includes this header and builds DCN 3.2.1 resource objects from register-offset and shift/mask tables.
- ABM and panel-control paths, including DMUB ABM integration, that consume ABM/PWM/luma/statistics fields for backlight and adaptive brightness behavior.
- OPP and formatter code that uses DPG, FMT, OPPBUF, OPP pipe, and OPP pipe CRC field tables when creating output pixel processor instances and validating output color/CRC behavior.
- OPTC/OTG timing-generator code, especially DCN 3.2 OPTC definitions that use `OTG0_*` masks for timing programming, update locks, vstartup/vupdate/vready, global controls, DRR, and CRC.
- ODM and DSC routing code that uses OPTC input and DSCRM fields for multi-segment output, DSC mode, bytes-per-pixel, slice width, underflow handling, and input clock/memory selection.
- IRQ services and diagnostics that depend on OTG vertical interrupt fields, OTG status/clear bits, ODM underflow interrupts, OPP pipe CRC results, and static-screen or DRR event bits.

## Risks And Maintenance Notes

- This is generated hardware ABI. Manual edits to shifts or masks are high risk because register helper code will still compile while targeting the wrong bits.
- Repeated instance families are copy/paste-sensitive: ABM2/ABM3, DPG/FMT/OPPBUF/OPP pipe/CRC instances 0-3, DSCRM0-3, ODM0-3, and OTG0/OTG1 must stay aligned with the register generator and address headers.
- Many fields are packed into adjacent bit ranges. A one-bit mask error can corrupt neighboring controls such as interrupt clear/mask bits, update locks, pixel-format selection, dithering controls, DRR state, or underflow handling.
- Clear/ack/reset fields are side-effect-prone. Misusing underflow clear, interrupt ack/clear, trigger clear, force-count clear, CRC one-shot pending, soft reset, or update-lock fields can produce intermittent display glitches or stuck status.
- Timing fields are user-visible. Bad OTG total/blank/sync, vstartup/vupdate/vready, DRR, GSL, or DSC start-position masks can surface as black screens, flicker, missed vblank, tearing, bad variable-refresh behavior, or DSC timing faults.
- Color-path fields are visually sensitive. Incorrect FMT clamp, pixel encoding, subsampling, dithering, truncation, or dynamic-expansion masks may cause color shifts, banding, chroma ordering errors, or CRC mismatches.
- Boundary completeness matters. This chunk starts after the `ABM2_DC_ABM1_LS_SUM_OF_LUMA` comment and ends before the `OTG1_OTG_V_TOTAL_CONTROL` masks, so final file-level documentation should merge adjacent chunks before claiming complete register-group coverage.

## Test Signals

Useful validation signals include:

- Build AMDGPU Display Core with DCN 3.2.1 enabled and confirm DCN321 resource, OPP, OPTC, ODM, ABM, IRQ, and DSC paths compile with this generated header and the matching offset header.
- Run generated-register consistency checks: each complete register group should have paired shifts and masks, masks should not overlap unexpectedly, repeated instance families should be numerically consistent, and boundary partial groups should reconcile with neighboring chunks.
- Compare all ABM, DPG/FMT/OPP, DSCRM, ODM, and OTG field values against the authoritative DCN 3.2.1 register source, prioritizing lock/update-pending bits, clear/ack bits, timing fields, CRC fields, underflow state, and packed pixel-format/dither fields.
- Exercise display modes across common and edge timings, including interlace where supported, stereo/3D paths where available, DSC, ODM/multi-segment output, 4:2:0/4:2:2 formats, high bit depth, and variable refresh/DRR.
- Validate panel brightness and ABM behavior by sampling luma statistics, histogram results, PWM target/current/final duty-cycle fields, HGLS read progress, missed-frame flags, and lock/update-pending behavior.
- Capture OPP and OTG CRCs before and after enabling formatter dither/truncation, chroma subsampling, generated patterns, DSC, and stereo/interlace modes; unexpected CRC drift points to format or timing mask issues.
- Monitor ODM underflow status/interrupts, OTG vertical interrupts, vblank timing, pipe update pending, global sync status, and DRR events during mode set, page flip, cursor update, suspend/resume, hotplug, and VRR transitions.
- Use register dumps around mode programming and updates to confirm that read-modify-write helpers affect only intended fields, especially locks, interrupt clears, update windows, timing totals, and clock/power gate controls.

## Chunk-Specific Summary

Lines 22677-25260 define generated bitfield masks and shifts for the tail of ABM2, the full ABM3 block, repeated OPP output pipe and formatter blocks 0-3, DSC remap and OPP top controls, ODM/OPTC input blocks 0-3, the complete OTG0 timing/control/status surface in this slice, and the beginning of OTG1 timing fields. The content is data-only register ABI. Correctness depends on exact generated values, repeated-instance consistency, careful handling of partial boundary registers, and hardware validation through ABM, formatting, CRC, ODM/DSC, timing, interrupt, DRR, and update-lock flows.
