# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 20170-22676

## Scope

This chunk is a generated AMD DCN 3.2.1 register field mask segment. It covers 2,507 source lines with 2,093 `#define` entries: 1,045 `__SHIFT` constants, 1,048 `_MASK` constants, and 399 register-group comment markers. The source is not executable C; it is a compile-time bitfield schema consumed by AMD display register helper code.

The chunk starts in the middle of `MPCC_MCM2` 1D LUT region definitions, then covers complete or near-complete blocks for:

- `dce_dc_mpc_mpcc_mcm3_dispdec`: `MPCC_MCM3` shaper LUT, 3D LUT, 1D LUT, and LUT memory power-control fields.
- `dce_dc_mpc_mpc_ocsc_dispdec`: `MPC_OUT0` through `MPC_OUT3` mux, denormalization, clamp, and output CSC fields.
- `dce_dc_opp_abm0_dispdec`, `dce_dc_opp_abm1_dispdec`, and the beginning of `dce_dc_opp_abm2_dispdec`: backlight PWM and Adaptive Backlight Management fields.

The file-level include guard and license live outside this span. The corresponding address macros are in `dcn_3_2_1_offset.h`; this chunk only supplies shifts and masks.

## Purpose

The purpose of the chunk is to let DCN 3.2.1 driver code program hardware register fields by name instead of hard-coding bit positions. Each field uses the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index.
- `<REGISTER>__<FIELD>_MASK` gives the full register mask for the field.

The MPCC/MCM portions describe color-management storage and control in an MPC compositor path. They define shaper RAM A/B region layouts, 3D LUT indexing/data/control fields, 1D LUT RAM A/B segment definitions, output offsets, write enables, current mode readbacks, and memory power state controls. These fields are the low-level contract behind high-level color features such as shaper curves, 3D LUTs, gamut remap, 1D transfer functions, and memory power gating for those tables.

The MPC OCSC portion describes post-composition output routing and color conversion. It covers four MPC outputs, each with mux selection, rate/flow control flags, denormalization clamp ranges for R/Cr, G/Y, and B/Cb, CSC mode/current-mode fields, and two coefficient banks (`A` and `B`) for 3x4 output color-space conversion coefficients.

The ABM portions describe backlight and image-statistics state for up to three ABM instances. ABM fields cover PWM levels, automatic ambient/backlight update control, frame-sampled update cadence, grouped register locks, ACE thresholds and slope/offset curves, histogram and luma-statistic controls, histogram result readbacks, and master locks.

## Important APIs, Types, and Data Shapes

There are no functions, structs, enums, or inline helpers in this chunk. The exposed API is the macro namespace used by the AMD display register helper layer. DCN code commonly feeds these macros through register-list and mask/shift-list generators such as `SRII`, `SRI_ARR`, and `SF`, then stores the resulting values in hardware block register tables.

Important data shapes in this span include:

- `MPCC_MCM*_MPCC_MCM_SHAPER_*`: shaper mode/current-mode, per-channel offsets and scales, 8-bit LUT index, 24-bit LUT data, write-mask/write-select fields, and RAM A/B piecewise-region metadata.
- `MPCC_MCM*_MPCC_MCM_3DLUT_*`: 3D LUT mode, 12-bit index, 30-bit data path, read/write done and select flags, output normalization, and signed-looking output offsets packed as 19-bit fields.
- `MPCC_MCM*_MPCC_MCM_1DLUT_*`: 1D LUT mode/current-mode, selection, read/write control, direct LUT index/data access, RAM A/B start/end/base/slope/offset values, and paired region entries.
- LUT region packing: most `*_REGION_N_M` registers pack two regions. Each region usually has a 9-bit LUT offset and a 3-bit segment count at shifts `0x0`/`0xc` for the first region and `0x10`/`0x1c` for the second.
- `MPCC_MCM*_MPCC_MCM_MEM_PWR_CTRL`: force/disable/low-power controls and readback state for shaper, 3D LUT, and 1D LUT memories.
- `MPC_OUT*_MUX`: output selection, overflow error, error acknowledgment, rate-control disable/control, flow-control mode, and an 11-bit flow-control count.
- `MPC_OUT*_DENORM_*`: 12-bit min/max clamp fields and a 3-bit denorm mode.
- `MPC_OUT*_CSC_*`: output CSC mode/current mode plus packed 16-bit coefficient pairs for banks `A` and `B`.
- `ABM*_BL1_PWM_*`: 17-bit ambient/user/target/current/final/minimum duty-level fields, ABM enable bits, ambient-level enable, auto-update controls, and 16-bit step size.
- `ABM*_DC_ABM1_*`: ABM enable/bypass, input CSC coefficient selection, ACE slope/offset and threshold registers, histogram/luma statistic controls, sample-rate controls, shift flags and indexes, 24 histogram result words, and lock/readback/update-pending fields.

The `L` suffix on masks makes these long integer constants. Consumers should still use the driver’s unsigned register helpers rather than ad hoc signed arithmetic.

## Control Flow and Behavior

This header has no runtime control flow. Runtime behavior is created when DCN 3.2.1 resource construction includes `dcn/dcn_3_2_1_sh_mask.h` and combines these field definitions with address registers from `dcn_3_2_1_offset.h`. In this tree, `dcn321_resource.c` includes both headers and `dcn32_resource.h` defines broad register-list macros for the MCM, MPC OCSC, and ABM families represented here.

The implied hardware flows are:

- MCM color programming: higher-level color code selects shaper, 3D LUT, and 1D LUT modes, writes LUT entries through index/data registers, configures RAM A/B regions and start/end slopes, then relies on mode-current/read-write status fields to confirm the active programming path.
- MCM memory power management: power-control fields can force, disable, or place shaper/3D LUT/1D LUT memories into low-power modes, with corresponding state bits for readback.
- MPC output routing: mux fields select the composed stream feeding each MPC output. Rate and flow-control fields expose pacing or overflow/error recovery behavior for those output paths.
- Output color conversion: OCSC mode and coefficient-bank fields define post-composition color-space conversion. Banked coefficients allow programming one bank while another may be active, depending on the surrounding hardware sequence.
- Denormalization and clamping: denorm mode plus per-channel min/max clamps constrain output component ranges before the data leaves the MPC output path.
- ABM/backlight update: PWM level fields represent ambient input, user level, target/current ABM level, final duty cycle, and minimum duty cycle. Control bits decide whether ABM and ambient level are used and whether current level/final duty are automatically updated.
- ABM statistics and ACE processing: luma-sum/min/max/pixel-count registers and histogram bins feed adaptive contrast/backlight decisions. ACE slope/offset/threshold fields configure the image-dependent transform.
- Frame-synchronized updates: ABM grouped locks, HGLS locks, update-at-frame-start, frame-start display select, readback-double-buffer enable, and update-pending bits describe synchronization around frame boundaries.

Because this chunk only declares field positions, it does not enforce ordering. Correct sequencing, polling, locks, timeouts, and value ranges are responsibilities of the display block implementations and hardware programming guide.

## State and Persistence

No software state is allocated or persisted by this file. The persistent state represented by the macros lives in GPU display hardware registers after driver writes.

State classes represented in the chunk include:

- Latched color configuration: shaper/3D LUT/1D LUT modes, LUT entries, region segment metadata, offsets, scales, output normalization, OCSC modes, CSC coefficients, denorm modes, and clamp bounds.
- Double-buffered or frame-synchronized state: MCM mode-current fields, ABM grouped lock fields, readback double-buffer enables, update-at-frame-start selectors, and update-pending bits.
- Hardware memory power state: shaper/3D LUT/1D LUT memory force, disable, low-power mode, and state readbacks.
- Backlight control state: user, ambient, target, current, minimum, and final PWM duty values plus ABM enable and auto-update controls.
- Image statistics readback state: luma sums, min/max luma, filtered min/max luma, pixel counts, min/max pixel-value counters, histogram bin shifts/indexes, and 24 histogram result registers per complete ABM instance in this span.
- Error/status/clear state: MPC rate-control overflow and acknowledgement fields, ABM missed-frame flags and clear bits, HGLS read-in-progress and missed-frame clear bits.

Some fields likely have read-only or write-one-to-clear semantics despite appearing as plain masks. Examples include `*_CURRENT`, `*_DONE`, `*_UPDATE_PENDING`, `*_MISSED_FRAME_CLEAR`, read-in-progress, and lock-related fields. The header itself does not encode access permissions.

## Dependencies and Integration Points

This chunk depends on the generated AMD register header set:

- `dcn_3_2_1_offset.h` supplies register addresses and base indices.
- `dcn_3_2_1_sh_mask.h` supplies shifts and masks.
- `reg_helper.h` and display block register-list macros combine address, shift, and mask data into typed register tables used by DCN hardware blocks.

Key integration points in this tree include:

- `display/dc/resource/dcn321/dcn321_resource.c`, which includes this exact DCN 3.2.1 shift/mask header during DCN321 resource construction.
- `display/dc/resource/dcn32/dcn32_resource.h`, whose MCM register-list macros enumerate the `MPCC_MCM_SHAPER`, `MPCC_MCM_3DLUT`, `MPCC_MCM_1DLUT`, and `MPCC_MCM_MEM_PWR_CTRL` register families covered here.
- MPC block code and headers such as `display/dc/mpc/dcn32/dcn32_mpc.h`, which expose `MPC_OUT0_MUX` field definitions for output mux/rate/flow control.
- Color-management paths in `display/dc/core/dc.c`, `display/dc/core/dc_hw_sequencer.c`, and `display/amdgpu_dm/amdgpu_dm_color.c`, which refer to shaper, 3D LUT, 1D LUT, OCSC, and CTM placement at a higher abstraction level.
- DMUB ABM code such as `display/dc/dce/dmub_abm_lcd.c`, which programs ABM sample-rate and backlight-related registers through the shared register helper mechanism.

The chunk is source-tree-aligned with a DCN321 generated header, but many register families are shared with DCN32/DCN35-style blocks. Adjacent chunks are needed to complete `MPCC_MCM2` before line 20170 and `ABM2` after line 22676.

## Risks

- Generated-header drift: if a mask or shift disagrees with the silicon register specification, callers will compile cleanly while programming the wrong bits.
- Chunk-boundary incompleteness: this span starts mid-register for `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_6_7` and ends at `ABM2_DC_ABM1_LS_SUM_OF_LUMA`. Per-file synthesis must merge adjacent chunks before making claims about whole families.
- Bank and instance confusion: MCM RAM A/B, CSC banks A/B, MPC output indices 0-3, MPCC MCM instances 2/3, and ABM instances 0-2 are all encoded textually. Copy/paste mistakes can program the wrong instance or inactive bank.
- LUT write sequencing hazards: index/data/write-enable/read-write-control fields usually require precise write order and completion polling. A bad sequence can leave partially loaded shaper, 3D LUT, or 1D LUT tables.
- Region packing hazards: paired region registers share one 32-bit value. Updating one region without preserving the other can corrupt neighboring segment metadata.
- Power-control hazards: MCM memory power force/disable/low-power fields can make LUT memories unavailable. These fields should not be toggled blindly while color programming is active.
- Frame-synchronization hazards: ABM locks, update-pending bits, update-at-frame-start, and missed-frame clears imply timing-sensitive access. Ignoring these fields can produce stale readbacks, missed updates, or visible brightness jumps.
- Read/write semantic ambiguity: the generated masks do not identify read-only, write-one-to-clear, self-clearing, or reserved behavior. Callers must rely on block-specific programming code and hardware documentation.
- Width and signedness issues: many color coefficients and offsets use 16-bit, 18/19-bit, 24-bit, 30-bit, or full 32-bit masks. Manual shifts can mishandle sign extension or truncation; central field macros should be preferred.
- ABM user-visible impact: incorrect PWM minimum/final/target/current duty fields can produce brightness flicker, backlight clipping, slow convergence, or inaccessible panel brightness behavior.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Build coverage for DCN321 display resources and any DCN32 block code that uses the shared MCM, MPC, and ABM register-list macros.
- Static consistency checks that every field has a non-overlapping mask/shift pair and that paired region fields preserve the expected `0x0`, `0xc`, `0x10`, and `0x1c` packing.
- Color pipeline tests that load shaper curves, 3D LUTs, 1D LUTs, and OCSC matrices, then verify mode-current/readback fields and visual output.
- HDR, CTM, gamma, degamma, color-space conversion, and gamut-remap tests that exercise the shaper/3D LUT/1D LUT/OCSC programming path.
- Register readback after MCM memory power transitions to confirm LUT memories are available before writes and return expected power-state values afterward.
- Multi-output display tests that exercise `MPC_OUT0` through `MPC_OUT3` mux and flow-control fields under clone, extended desktop, and hotplug scenarios.
- ABM/backlight tests covering user brightness changes, ambient-light input, automatic duty-cycle calculation, suspend/resume, panel power sequencing, and rapid frame updates.
- Histogram/luma-statistics diagnostics checking nonzero luma sum, plausible min/max values, pixel counts, histogram bins, missed-frame flags, and update-pending behavior.
- Stress tests around frame-boundary updates to catch stuck locks, missed-frame flags, or incomplete double-buffer updates.

## Research Notes

This is chunk-level research only. The final per-file document should reconcile this with neighboring chunks because the MPCC MCM2 1D LUT family begins before this span and the ABM2 family continues after it. Direct source searches show this exact header included by DCN321 resource construction, while many individual field names are consumed through macro-generation patterns rather than direct hand-written references.
