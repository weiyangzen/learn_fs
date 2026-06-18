# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 19847-22341

## Scope And Purpose

This chunk is a generated AMD DCE 12.0 register shift/mask header section. It contains C preprocessor constants only: no functions, structs, enums, mutable storage, allocation, or executable control flow. Each register field is represented by paired macros named `...__SHIFT` and `..._MASK`, giving the bit offset and bit mask used by display-driver code when composing or decoding MMIO register values.

The range starts at the tail of pipe 2 DCP regamma LUT definitions, covers most of the pipe 2 front-end/display pipe register blocks, and ends in the early pipe 3 DCP cursor update definitions. The covered hardware domains are `DCP2`, `LB2`, `DCFE2`, `DC_PERFMON5`, `DMIF_PG2`, `SCL2`, `BLND2`, `CRTC2`, `FMT2`, and the first part of `DCP3`.

The purpose is to preserve the DCE 12.0 hardware ABI in source form. Consumers include this header together with the matching DCE 12.0 address/offset headers and use these constants through register-helper macros to program graphics planes, gamma/color processing, line buffers, display front-end clocks and memory power, performance counters, memory-interface watermarks, scalers, blenders, timing generators, formatters, CRC/readback blocks, interrupts, and cursor state.

## Important APIs, Types, And Macro Families

The public API surface is the macro namespace. The file does not define callable APIs or C types, but these macros are part of the low-level interface consumed by AMDGPU/DC display code.

Important macro groups in this chunk:

- `DCP2_REGAMMA_*`: pipe 2 output regamma LUT programming fields, including LUT write-enable mask and paired A/B piecewise region programming (`START_CNTL`, `SLOPE_CNTL`, `END_CNTL*`, and region `0_1` through `14_15`). These fields describe LUT offsets, segment counts, start/end values, slopes, and bases for color transfer programming.
- `DCP2_ALPHA_CONTROL` and `DCP2_GRPH_XDMA_*`: pipe 2 alpha rounding/cursor alpha blend fields and XDMA recovery/cache-underflow detection/status fields for display-plane recovery behavior.
- `LB2_*`: line-buffer format and memory controls, desktop height, vline/vline2/vblank counters and interrupt status, sync reset selection, black/keyer colors, buffer fill/urgency/empty/full status, no-outstanding-request status, and MVP AFR flip/swap-lock helper fields.
- `DCFE2_*`: pipe 2 display front-end clock gating, soft reset, memory power control/status for DCP LUT/regamma/cursor, scaler coefficient, line-buffer, and blender memories, plus misc and flush status fields.
- `DC_PERFMON5_*`: performance-counter control/state, low/high counter values, counter-off and interrupt controls, and cvalue interrupt/status fields for display performance monitoring.
- `DMIF_PG2_DPG_*`: pipe 2 display memory-interface arbitration, watermark masks, urgency levels, stutter/self-refresh behavior, low-power/P-state controls, repeater programming, pre-processing buffer checks, and DVMM forced-flip status/clear fields.
- `SCL2_*`: scaler coefficient RAM select/data, mode, taps, bypass/replication/auto-ratio controls, horizontal and vertical ratios and initial phases, rounding offsets, update-lock/update-taken state, sharpness, ALU disable, coefficient RAM conflict interrupt/status, viewport and overscan geometry, and scaler mode-change detection/masking.
- `BLND2_*`: blender global gain/alpha/mode/stereo/feedthrough controls, super-AA and PTI fields, blender update locks, underflow interrupt status/ack/mask, vertical-update lock fanout for DCP/SCL/BLND blocks, and register-update pending status.
- `CRTC2_*`: timing-generator fields for horizontal and vertical totals, blanking, sync A/B windows, polarity, triggers, force-count-now, flow control, stereo/interlace, master enable, blanking, readback/status counters, snapshots, interrupts, double buffering, test patterns, master update locks/modes, MVP in-band controls, overscan colors, CRC windows/data, external timing sync, static-screen detection, 3D structure, GSL, range timing update, and DRR control.
- `FMT2_*`: formatter clamp component limits, dynamic expansion, pixel encoding/subsampling, spatial/temporal dithering, random seeds, clamp control, formatter CRC setup/signatures, side-by-side stereo width, and 4:2:0 hblank early start fields.
- `DCP3_*` opening block: pipe 3 graphics enable/control, surface addressing, viewport, desktop/windowing, flip/update/interrupt fields, prescale/CSC/color matrices, denorm/round/clamp/keying, degamma/gamut remap, DCP spatial dither, random seeds, converted-field readout, and cursor control/surface/size/position/hotspot/color/update fields through `DCP3_CUR_UPDATE__CURSOR_UPDATE_TAKEN_MASK`.

## Control Flow And Data Flow

There is no runtime control flow in this header. Data flow is compile-time substitution: a caller includes `dce_12_0_sh_mask.h`, picks a field macro, shifts a value by `...__SHIFT`, masks it with `..._MASK`, and writes the resulting bits through an AMDGPU/DC MMIO helper to the address from a matching `dce_12_0_*` register-address header.

The implied hardware flows are stateful:

- Plane programming uses DCP fields to set graphics surface format, tiling/swizzle metadata, addresses, viewport, flip behavior, color transforms, gamma/gamut controls, dither, keying, and cursor registers. Update and lock fields determine when programmed state becomes active.
- Timing programming uses CRTC fields to stage totals, blank/sync windows, interlace/stereo, master-enable, update locks, snapshots, interrupts, CRC windows, DRR, GSL, and external timing sync.
- Memory and bandwidth programming uses LB and DMIF fields to set line-buffer formats, buffer levels, urgency thresholds, watermarks, stutter/self-refresh, P-state allowance, and underrun/underflow acknowledgement.
- Scaling and blending use SCL and BLND fields to load coefficient RAM, choose filter modes and ratios, define viewports/overscan, latch updates, blend planes/cursors, and surface underflow events.
- Formatter and CRC paths use FMT and CRTC CRC fields to clamp, dither, encode pixels, control 4:2:0/subsampling behavior, seed random dithering, and capture output signatures for validation.
- DCFE and PERFMON fields participate in clock/memory power sequencing, soft resets, flush detection, and performance counter collection.

Ordering is not encoded here, but consumers must respect hardware sequencing. Examples include locking updates before multi-register changes, waiting for `*_UPDATE_TAKEN` or pending bits to clear, acknowledging interrupt/status bits with the correct clear field, programming coefficient/LUT RAM through index/data windows without conflicts, and avoiding clock or memory power gating while dependent blocks are active.

## State And Persistence Behavior

The header itself has no persistence. The state represented by these constants lives in DCE 12.0 hardware registers after the driver writes them and persists until overwritten, reset, power-gated, or reinitialized during modeset, suspend/resume, GPU reset, or display pipeline teardown.

State categories represented here include:

- Color and pixel-processing state: regamma regions/LUT enables, prescale, input/output CSC matrices, degamma/gamut remap, denorm, rounding, clamping, dithering, formatter dynamic expansion, and CRC capture controls.
- Plane and cursor state: graphics enable, surface addresses, tiling/swizzle metadata, pitch, viewport, flip/pending status, cursor enable/mode/address/size/position/hotspot/colors, alpha blend, and update locks.
- Timing-generator state: active/blank/sync geometry, interlace/stereo, master enable, blanking, frame/line counters, snapshots, forced sync/count operations, DRR, GSL, static-screen detection, test patterns, and external timing sync.
- Bandwidth and memory-interface state: line-buffer configuration, buffer levels, urgency marks, DMIF arbitration weights, watermarks, stutter/self-refresh, P-state change controls, and flush/no-outstanding-request status.
- Power and reset state: DCFE clock gating, soft reset, memory power force/disable/mode/status fields for pipe-local memories.
- Interrupt and diagnostic state: vblank/vline status, underflow/cache-underflow, CRTC events, external sync loss, scaler coefficient conflicts, performance counter interrupts, CRC signatures, and readback registers.

Many fields are acknowledgement, clear, status, pending, or mask bits. These should be treated as hardware side effects, not ordinary software state. Writing the wrong bit can clear evidence, leave interrupts asserted, unmask an interrupt unexpectedly, or latch partially programmed display state.

## Dependencies And Integration Points

This generated header depends on consistency with the DCE 12.0 register database and sibling generated headers that provide register offsets and enumerated values. The masks and shifts are useful only when paired with the correct register address for the same ASIC generation and display pipe.

Primary integration points:

- AMDGPU/DC register access helpers that use generated shift/mask fields to implement `REG_SET`, `REG_UPDATE`, bitfield read/modify/write, and traceable MMIO programming.
- DCE 12.0 resource construction and hardware sequencing code that maps logical pipes to `DCP`, `SCL`, `BLND`, `CRTC`, `FMT`, `LB`, `DMIF`, and `DCFE` register blocks.
- Atomic modeset, page-flip, cursor, color-management, scaling, and blending paths that program the DCP/SCL/BLND/CRTC/FMT fields.
- Interrupt handling for vblank/vupdate, vline, underflow, scaler conflicts, CRTC events, external timing sync, static-screen, and performance-monitor events.
- Power-management and bandwidth code that adjusts DMIF watermarks, stutter/P-state behavior, DCFE memory power, clock gating, and flush/no-outstanding-request status.
- Diagnostics and validation paths that use CRTC/FMT CRC registers, pixel readback, counters, and performance monitor fields.

The chunk is also structurally tied to repeated pipe instances. Pipe 2 register blocks dominate the range, and the final section begins pipe 3 DCP definitions. Generated maintenance must preserve the pipe index in macro names and the corresponding address block selected by caller code.

## Risks And Edge Cases

The major risk is generated-header drift. These constants are hardware ABI: a one-bit shift or mask error compiles cleanly but programs the wrong register field.

Specific risks:

- Chunk boundaries are partial. The range starts after the beginning of the `DCP2_REGAMMA_LUT_WRITE_EN_MASK` block and ends in the middle of `DCP3_CUR_UPDATE`; adjacent chunks are needed for complete per-file synthesis.
- Repeated pipe and register families make copy/generation errors hard to spot. `DCP2`, `LB2`, `SCL2`, `BLND2`, `CRTC2`, `FMT2`, and `DCP3` names are similar but must match the correct pipe address block.
- Many fields have write-one-to-clear or acknowledgement semantics (`*_ACK`, `*_CLEAR`, `*_CLR`, `*_RESET`, `*_UPDATE_TAKEN`, interrupt occurred bits). Treating them as normal read/write values can lose events or wedge status bits.
- Mask polarity is not uniform. Fields named `*_MASK`, `*_INT_MSK`, `*_DIS`, `*_DISABLE`, `*_GATE_DISABLE`, or `*_FORCE_*` require hardware-specific interpretation.
- LUT and coefficient RAM fields are index/data style and may conflict with hardware readers. Misordered access can corrupt gamma or scaler coefficients, producing color or scaling artifacts.
- Timing and update-lock fields can cause visible glitches if related CRTC/SCL/BLND/DCP fields are not latched atomically at the intended vertical update.
- Bandwidth, urgency, stutter, P-state, and memory-power fields can cause underflow, flicker, self-refresh failures, or power regressions even when the display still lights up.
- Formatter pixel encoding, 4:2:0, dithering, clamp, and CRC fields interact with connector/output format expectations; wrong masks can produce subtle color-depth or validation failures.

## Test Signals

There are no standalone unit tests for this macro section. Useful validation signals are build coverage, generated-header comparison, and hardware behavior:

- Build AMDGPU/DC configurations that include `dce_12_0_sh_mask.h`; this catches syntax errors, missing macros, and duplicate definitions.
- Compare this range against the authoritative DCE 12.0 register database or a known-good upstream generated header, especially repeated pipe 2 blocks and the transition into pipe 3.
- Exercise modeset, page flip, cursor movement, color-management gamma/degamma/gamut, scaling, blending, overscan, stereo/interlace, DRR, and 4:2:0 output paths on DCE 12.0 hardware.
- Validate vblank/vline/vupdate, CRTC trigger, underflow, scaler conflict, external timing sync, static-screen, and performance-monitor interrupts for correct mask/ack behavior.
- Run CRC and pixel-readback validation through CRTC/FMT CRC windows and compare signatures across known test patterns.
- Stress suspend/resume, GPU reset, clock gating, memory power, stutter/self-refresh, and P-state transitions to catch DCFE/DMIF/LB sequencing mistakes.
- Inspect MMIO traces for representative register writes to ensure field values are shifted and masked into the expected bit positions.
