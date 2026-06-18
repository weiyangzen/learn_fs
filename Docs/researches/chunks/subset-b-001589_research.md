# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 20047-22602

## Purpose

This chunk is part of the generated AMD DCN 1.0 register shift/mask header. It contains C preprocessor constants only; there are no functions, structs, storage objects, branches, or executable algorithms in this source slice. Each register field is exposed as a bit-position macro ending in `__SHIFT` and a positioned bit mask ending in `_MASK`.

The covered hardware area is the late display pipeline and timing generator side of DCN 1.0:

- The chunk begins in the tail of the ABM1 ambient/backlight-management histogram block, with histogram bin shift-index registers, histogram result registers, and the ABM backlight master lock.
- It defines output pixel processor formatter (`FMT0` through `FMT5`) fields for clamp ranges, dynamic expansion, pixel encoding, 4:2:0/subsampling behavior, bit-depth reduction, dithering, random seeds, stereo active width, and 4:2:0 memory power control.
- It defines output pixel processor buffer (`OPPBUF0` through `OPPBUF5`) fields for active width, segmentation, overlap, pixel repetition, double-buffer pending status, and 3D timing/dummy-data parameters.
- It defines OPP pipe control and OPP pipe CRC registers for six OPP instances.
- It includes OPP top clock control and display performance monitor instance 17.
- It defines ODM/OPTC input blocks (`ODM0` through `ODM5`) for underflow status/clear, double-buffer pending, input source selection, input clock control, and spare registers.
- It defines a complete OTG0 timing-generator block and begins OTG1, ending at `OTG1_OTG_COUNT_RESET`.

The header is hardware ABI metadata for AMDGPU Display Core. Driver code combines these constants with register-address macros from `dcn_1_0_offset.h`, then uses register helpers such as `REG_UPDATE`, `REG_SET`, `REG_READ`, or lower-level MMIO helpers to program DCN display hardware.

Although the file path is under a `ceph-client` source mirror, this chunk is AMD GPU display register metadata. It does not implement Ceph filesystem behavior, distributed storage state, network protocol handling, or filesystem persistence.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The public interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit number for a field.
- `<REGISTER>__<FIELD>_MASK`: already-positioned mask for the same field.

Important macro families are:

- `ABM1_DC_ABM1_HG_BIN_*`, `ABM1_DC_ABM1_HG_RESULT_*`, and `ABM1_DC_ABM1_BL_MASTER_LOCK`: ABM1 histogram and luma-statistics readback/control fields. The chunk starts after the earlier ABM sample-rate and luma-stat blocks, so the final per-file merge needs adjacent chunk context for the full ABM1 story.
- `FMTn_FMT_CLAMP_COMPONENT_[RGB]`: per-channel lower/upper clamp values. Each register carries two 16-bit fields.
- `FMTn_FMT_DYNAMIC_EXP_CNTL`: dynamic expansion enable and mode, used when expanding lower color depths toward a wider output pipeline representation.
- `FMTn_FMT_CONTROL`: stereo override, spatial dither frame-counter behavior, pixel encoding, subsampling mode/order, Cb/Cr bit-reduction bypass, and double-buffer update-pending state.
- `FMTn_FMT_BIT_DEPTH_CONTROL`: truncation, truncation depth/mode, spatial dithering, randomization controls, temporal dithering, temporal offsets, temporal level, reset, and FRC selection fields.
- `FMTn_FMT_DITHER_RAND_[RGB]_SEED`: per-channel random seed and output offset fields for dither behavior.
- `FMTn_FMT_CLAMP_CNTL`: clamp enable and clamp color-format selection.
- `FMTn_FMT_SIDE_BY_SIDE_STEREO_CONTROL`: active width for side-by-side stereo.
- `FMTn_FMT_MAP420_MEMORY_CONTROL`: 4:2:0 mapping memory power force/disable/status fields.
- `OPPBUFn_OPPBUF_CONTROL`: active width, display segmentation, overlap pixels, pixel repetition, and double-buffer pending state.
- `OPPBUFn_OPPBUF_3D_PARAMETERS_0/1`: vertical active-space sizes plus dummy RGB data used by 3D/stereo output-buffer behavior.
- `OPP_PIPEn_OPP_PIPE_CONTROL`: OPP pipe clock enable.
- `OPP_PIPE_CRCn_OPP_PIPE_CRC_*`: CRC enable/continuous mode, stereo/interlace modes, pixel/source select, one-shot pending status, CRC mask, and result registers for A/R/G/B channels.
- `OPP_TOP_CLK_CONTROL`: OPP top-level clock force/allow/state fields.
- `DC_PERFMON17_*`: display performance monitor instance 17 fields for counter control, current-value selection, counter state, performance-monitor state, interrupt threshold/status/ack, and high/low value readback.
- `ODMn_OPTC_*`: output data merger/input-to-timing-generator fields for underflow state, source selection, input clock enable/on/gate-disable, and spare register content.
- `OTG0_OTG_*`: timing generator 0 fields for horizontal/vertical totals, blanking, sync, dynamic refresh/vertical-total controls, trigger A/B controls, force-count-now, flow control, stereo/AV sync, master enable, blanking, pipe abort, interlace, field indication, pixel readback, scanout status/counters, interrupts, double buffering, test patterns, colors, CRC windows/results, static-screen detection, 3D structure, global sync lock, global update control, dynamic refresh rate, request control, and spare register state.
- `OTG1_OTG_*`: the beginning of timing generator 1 with the same shape as OTG0 through count reset. The chunk ends before the remaining OTG1 stereo, interrupt, CRC, global sync, DRR, request, and spare fields.

Several generated macro names contain repeated words, such as `OPP_PIPE_CRC_MASK__OPP_PIPE_CRC_MASK_MASK`. That is expected: the first `MASK` is part of the hardware field name and the final `_MASK` suffix identifies the generated mask constant.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is created by caller code that uses these macros to encode and decode DCN 1.0 registers.

A typical use pattern is:

1. DCN10 resource setup includes `dcn/dcn_1_0_offset.h` and `dcn/dcn_1_0_sh_mask.h`.
2. Register-list macros in modules such as `dcn10_opp.h` and `dcn10_optc.h` select the `FMT0`, `OPPBUF0`, `OPP_PIPE0`, `OTG0`, and `ODM0` field names and instantiate per-block shift/mask tables.
3. Object constructors bind instance-specific register addresses and the shared shift/mask tables into objects such as `struct dcn10_opp` and timing generator/OPTC objects.
4. Higher-level Display Core code computes DRM modeset, stream, color, plane, vblank, CRC, stereo, and timing state.
5. Hardware-specific code writes or reads fields through helpers such as `REG_UPDATE`, `REG_UPDATE_2`, and `REG_READ`, which use the stored shift and mask values generated from this header.

Concrete local consumers illustrate this flow:

- `dcn10_opp.h` uses `OPP_SF(FMT0_FMT_BIT_DEPTH_CONTROL, ...)`, `OPP_SF(FMT0_FMT_CONTROL, ...)`, `OPP_SF(FMT0_FMT_DYNAMIC_EXP_CNTL, ...)`, `OPP_SF(FMT0_FMT_MAP420_MEMORY_CONTROL, ...)`, `OPP_SF(OPPBUF0_OPPBUF_CONTROL, ...)`, and `OPP_SF(OPP_PIPE0_OPP_PIPE_CONTROL, ...)` to build OPP shift/mask structures.
- `dcn10_opp.c` programs dynamic expansion through `FMT_DYNAMIC_EXP_CNTL`, 4:2:0 memory behavior through `FMT_MAP420_MEMORY_CONTROL`, bit-depth reduction and clamp/pixel-encoding state through FMT registers, stereo active widths through `OPPBUF_CONTROL` and `OPPBUF_3D_PARAMETERS_0`, and OPP clock enable through `OPP_PIPE_CONTROL`.
- `dcn10_optc.h` maps many `OTG0` and `ODM0` fields into timing-generator structures, including master update lock, blank control, timing totals, syncs, interlace, stereo, dynamic vertical total, triggers, scanout status, clocks, vertical interrupts, ODM underflow, global sync lock, CRC, and global update control fields.

The hardware sequencing implied by the register names is important even though it is not encoded in this file:

- Double-buffer and update-lock fields (`FMT_DOUBLE_BUFFER_REG_UPDATE_PENDING`, `OPPBUF_DOUBLE_BUFFER_PENDING`, `OTG_UPDATE_PENDING`, `OTG_MASTER_UPDATE_LOCK`, `UPDATE_LOCK_STATUS`, `OPTC_DOUBLE_BUFFER_PENDING`) imply staged state changes that latch on specific display timing boundaries.
- Clear and ack fields (`*_CLEAR`, `*_ACK`, `*_INT_CLEAR`, `OTG_PIPE_ABORT_DONE`, `OTG_TRIGA_CLEAR`, `OTG_TRIGB_CLEAR`) imply write-sensitive status handling.
- CRC fields require configuration, enable/one-shot or continuous operation, then result readback.
- Dynamic vertical total, global sync lock, force-count-now, and trigger fields require coordination with active scanout and vblank timing.

## State And Persistence Behavior

The header itself stores no state and persists nothing. The state represented by these macros lives in GPU display registers and in caller-maintained Display Core objects.

Hardware state represented in this chunk includes:

- ABM1 histogram/readback state: histogram bin shift flags/indexes, histogram results, and backlight master lock state.
- Formatter state for six OPPs: clamp lower/upper values, clamp enable/color format, pixel encoding, subsampling, Cb/Cr reduction bypass, dynamic expansion mode, truncation mode/depth, spatial/temporal dithering, random seeds, temporal FRC selection, stereo active width, and 4:2:0 memory power state.
- OPP buffer state: active width, display segmentation, overlap pixels, pixel repetition, double-buffer pending state, and 3D active-space/dummy-data parameters.
- OPP pipe state: pipe clock enable and CRC configuration/results.
- OPP top and performance monitor state: clock-force/allow/status and DC performance counter programming, thresholding, status, ack, and readback values.
- ODM/OPTC input state: selected input source, input clock state, underflow status/clear, double-buffer pending status, and spare register state.
- OTG timing state: horizontal/vertical totals, blank start/end, sync start/end, sync polarity, interlace control/status, field output, blank data color, black color, test-pattern state, scanout counters, frame counters, CRC windows/data, vertical interrupts, global sync lock, trigger configuration, dynamic vertical total limits, DRR/request behavior, and global update controls.

Persistence is hardware-specific:

- Programmed mode, color, dither, stereo, timing, CRC window, test-pattern, and global sync fields persist until rewritten, reset, or lost through display block power/reset.
- Pending and lock status fields are transient and reflect whether hardware has accepted or is waiting to latch a staged update.
- Counter, status-position, frame-count, vblank/hblank, and pixel-readback fields are live readback of current scanout state.
- Interrupt, underflow, trigger, force-count, snapshot, CRC, and performance-monitor status fields may be sticky until cleared or acknowledged.
- Memory power status for `FMT_MAP420_MEMORY_CONTROL` is a live hardware power-state readback rather than durable driver state.

Callers must distinguish ordinary configuration fields from status/clear fields. This header gives bit positions and masks, not access type, reset value, latch timing, or write-one-to-clear semantics.

## Dependencies And Integration Points

This chunk depends on the generated DCN 1.0 register contract. Its constants are meaningful only with sibling generated headers and Display Core helpers, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`, which provides matching `mm*` register addresses and base-index macros.
- Other DCN/DCE display headers that define register-list macros, field-list macros, object layouts, enum values, and helper wrappers.
- `reg_helper.h` and Display Core register access helpers that combine register addresses, masks, and shifts.
- Earlier and later sections of `dcn_1_0_sh_mask.h`, because this chunk starts in the middle of ABM1 and ends in the middle of OTG1.

Observed local include points for `dcn_1_0_sh_mask.h` include:

- `display/dc/resource/dcn10/dcn10_resource.c`, which creates DCN10 hardware object resources and includes the DCN 1.0 offset and shift/mask headers.
- `display/dc/irq/dcn10/irq_service_dcn10.c`, which needs register field metadata for DCN10 interrupt setup and handling.
- `display/dc/gpio/dcn10/hw_factory_dcn10.c` and `display/dc/gpio/dcn10/hw_translate_dcn10.c`, plus the DCN20 GPIO translator, which use shared DCN 1.0 register metadata for GPIO-related display hardware.

Primary runtime integration points are:

- OPP formatter programming: color depth reduction, dynamic expansion, 4:2:0 formatting, dithering, clamp and pixel-encoding setup, and stereo output-buffer setup.
- OPP clock and CRC programming: enabling/disabling OPP pipe clocks, selecting CRC sources, capturing CRC results, and logging/readback of OPP register state.
- Timing generator programming: DRM modeset timing totals, blanking, sync polarity, enable/disable sequencing, vblank/vertical interrupts, scanout position queries, blank data colors, test patterns, dynamic refresh, global sync lock, and master update lock.
- ODM/OPTC routing and underflow handling: selecting input sources to timing generators, controlling input clocks, observing/clearing underflow, and tracking double-buffer update state.
- Performance diagnostics: DC performance monitor 17 and OTG/OPP CRC fields for validation and debug.
- Power management and reset paths: 4:2:0 memory power controls, OPP/OTG clock controls, and state reprogramming after display reset or runtime power transitions.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are raw preprocessor constants; a wrong shift, wrong mask, stale generated value, or mismatched offset can compile successfully while programming the wrong display bit.

Important risk areas in this chunk are:

- Repeated instance layouts. `FMT0` through `FMT5`, `OPPBUF0` through `OPPBUF5`, `OPP_PIPE_CRC0` through `OPP_PIPE_CRC5`, `ODM0` through `ODM5`, and `OTG0`/`OTG1` repeat nearly identical field names. A prefix or instance mismatch can steer writes to the wrong pipe without a type-system failure.
- Chunk boundaries. The chunk begins after the start of ABM1 histogram configuration and ends before the rest of OTG1. Whole-file conclusions must be merged with adjacent chunks to avoid missing setup or clear/readback fields.
- Update-lock and double-buffer ordering. FMT, OPPBUF, ODM/OPTC, and OTG pending/lock fields indicate timing-sensitive staged updates. Incorrect sequencing can expose partially updated timing, color, dither, stereo, segmentation, or CRC state during active scanout.
- Status/clear aliases. Fields named `CLEAR`, `ACK`, `INT_CLEAR`, or underflow/trigger clears can be write-one-to-clear or otherwise edge-sensitive. Generic read-modify-write code can accidentally clear interrupts, trigger status, underflow state, or performance monitor status if it writes back stale set bits.
- Timing-generator programming. OTG horizontal/vertical totals, sync windows, blanking windows, interlace, field polarity, disable/start points, and dynamic vertical-total min/max fields are mode-critical. Bad values can cause blank screens, unstable vblank accounting, modeset failures, or monitor link issues.
- Dynamic refresh and global sync. `OTG_V_TOTAL_CONTROL`, `OTG_DRR_CONTROL`, `OTG_GSL_*`, force-count-now, trigger, and global-control fields are synchronized with frame timing. Misconfiguration can break variable refresh, genlock/global sync, multi-display synchronization, or update lock behavior.
- Color and format precision. FMT clamp, truncation, dither, temporal FRC, dynamic expansion, pixel encoding, and 4:2:0/subsampling fields affect visible output. Off-by-one clamp ranges, wrong dither depth, wrong pixel encoding, or wrong 4:2:0 memory power/control can produce banding, color shifts, chroma artifacts, or underrun.
- Clock and power fields. OPP pipe clock, OPP top clock, OTG clock, input clock, and 4:2:0 memory power controls interact with active scanout and block availability. Disabling or forcing clocks at the wrong time can hang updates, produce underflow, or make status polling unreliable.
- CRC and debug side effects. OPP and OTG CRC, test patterns, pixel readback, DTM/test, performance monitor, and static-screen fields are useful for validation but can affect or confuse normal display output if left enabled or if windows/selectors are wrong.
- Full-width masks. Several readback/result/spare fields use `0xFFFFFFFFL`. Consumers should use existing 32-bit register helpers to avoid signedness or width surprises.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build coverage for DCN10 display code that includes `dcn_1_0_sh_mask.h` and instantiates OPP, OPTC, IRQ, GPIO, and resource objects.
- Static generated-header checks that every `__SHIFT` has a matching `_MASK`, masks align to their shifts, and repeated instance families are consistent across `FMT0-5`, `OPPBUF0-5`, `OPP_PIPE_CRC0-5`, `ODM0-5`, and `OTG0/OTG1`.
- Diff checks against the authoritative DCN 1.0 register database and `dcn_1_0_offset.h`, especially around the ABM1 and OTG1 chunk boundaries.
- Modeset tests across common timings, blanking/sync polarities, interlaced and progressive modes, high-refresh modes, and multi-display configurations that exercise OTG totals, syncs, blanking, enable/disable, and update locks.
- Plane/stream update tests that verify pending bits drain and no partial frame is visible while changing formatter, OPP buffer, ODM, or OTG state.
- Format/color tests for RGB, YCbCr, 4:2:0, 8/10/12-bit depths, clamp ranges, dynamic expansion, truncation, spatial/temporal dithering, and FRC behavior.
- Stereo/3D tests that exercise FMT stereo override, side-by-side active width, OPPBUF 3D parameters, OTG stereo status/control, and 3D structure control.
- Vblank, vline, vertical-total, trigger, force-count-now, underflow, and performance-monitor interrupt tests that confirm status, mask, ack, and clear semantics.
- CRC validation using OPP pipe CRC and OTG CRC windows/results against known framebuffers and timing configurations.
- Power-management tests around OPP/OTG/input clocks, 4:2:0 memory power control, suspend/resume, runtime power transitions, and display block reset to ensure state is restored and polling does not hang.
- Debug/readback tests for scanout position, frame count, HV/VF counters, pixel readback, static-screen status, global sync status, and performance monitor high/low value reads.

## Cross-Chunk Notes

This source slice starts at `ABM1_DC_ABM1_HG_BIN_9_16_SHIFT_INDEX` follow-on definitions and then continues through ABM1 histogram result fields; earlier ABM1 control, sample-rate, luma-statistics, and threshold fields are outside this chunk. It ends immediately after `OTG1_OTG_COUNT_RESET`, before the rest of the OTG1 timing-generator fields. The final per-file report should reconcile this chunk with neighboring chunks before describing the complete ABM1 and OTG1 register families.
