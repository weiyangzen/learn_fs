# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 24607-27132

## Purpose

This chunk is generated AMD DCN 3.0.3 register field metadata. It contains no executable C logic; it publishes `#define` constants for register-field bit shifts and masks used by AMDGPU Display Core to pack and unpack MMIO register values.

The selected range starts in the middle of the `MPCC_OGAM0` output-gamma block, covers the full `MPCC_OGAM1` output-gamma block, then continues through MPC global configuration, output CSC/denorm programming, RMU shaper and 3D LUT registers, display performance monitor blocks, HPO top clocking, two ABM/backlight blocks, and the start of the HDA Azalia CORB/RIRB controller block. Although the file lives under a local `ceph-client` source mirror, this content is AMD GPU display-controller hardware metadata, not Ceph or distributed-filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, classes, enums, variables, callbacks, allocation sites, or locks in this line range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: field bit position within the register value.
- `<REGISTER>__<FIELD>_MASK`: field bit mask, normally with an `L` suffix.

Major macro families in this chunk:

- `MPCC_OGAM0_*`: tail of output gamma RAM B metadata for MPCC instance 0, including RGB offsets, 34 segmented-region descriptors, gamut-remap format/mode status, and coefficient banks A/B.
- `MPCC_OGAM1_*`: complete output gamma metadata for MPCC instance 1. It includes `MPCC_OGAM_CONTROL`, LUT index/data/control, RAM A and RAM B start/end/base/slope/offset fields for B/G/R, region pairs `0_1` through `32_33`, gamut-remap coefficient format/mode fields, and gamut-remap matrix coefficients `C11` through `C34` for banks A and B.
- `MPC_*` configuration: `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, CRC controls and results, performance event enable, bypass background color, host-read throttling, DPP/OPP/MPCC/DWB pending-status fields, vupdate lock sets for two pipes, and `MPC_DWB0_MUX`.
- `MPC_OUT0_*` and `MPC_OUT1_*`: output mux selection, rate/flow-control fields, denorm clamp min/max values, output CSC coefficient format, CSC mode/current status, and banks A/B of output CSC matrix coefficients.
- `MPC_RMU*`: RMU mux and memory power controls, shaper LUT control/data/write-enable, shaper offsets/scales, RAM A/B segmented-region descriptors, 3D LUT mode/index/data/read-write control, output normalization factor, and output offsets.
- `DC_PERFMON15_*` and `DC_PERFMON16_*`: display performance-counter selector, threshold, state, interrupt/status/ack, current value, and high/low result fields for MPC and HPO perfmon blocks.
- `HPO_TOP_CLOCK_CONTROL`: HPO display clock gate/test-clock fields.
- `ABM0_*` and `ABM1_*`: backlight/PWM levels, ABM enable and sample-rate controls, register locks, ACE offset/slope and thresholds, histogram/luma statistics controls and readback fields, sample-rate counters, histogram bin shift/index fields, histogram result registers 1 through 24, and master-lock fields.
- `CORB_*` and the first `RIRB_LOWER_BASE_ADDRESS` marker: HDA command output ring buffer write/read pointer, reset, control, memory-error status, and size/capability fields.

Consumers normally do not reference every generated name manually. They use token-pasting helpers such as `SF(register, field, __SHIFT)`, `SF(register, field, _MASK)`, `SR(register)`, and `SRII(register, block, instance)` to initialize per-block register, shift, and mask tables.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMD Display Core:

1. DCN 3.0.3 resource and hardware-block code include the matching offset and shift/mask headers.
2. Register-list macros paste register names into MMIO offset symbols, while field-list macros paste register and field names into this header's `__SHIFT` and `_MASK` symbols.
3. Constructors for MPC, ABM, audio, and related display blocks receive static register/shift/mask tables.
4. Modeset, color-management, backlight, perfmon, and display-audio paths call helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, or indexed register accessors.
5. Those helpers use the masks and shifts in this chunk to read/modify/write only the intended hardware bits.

The macro values do not encode ordering. Consumers still must handle sequencing around clocks, power, soft reset, double-buffer/update locks, LUT bank selection, frame-start updates, histogram readback, interrupt clear/ack, and HDA DMA ring setup.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It describes hardware state in DCN 3.0.3 display registers.

Important state represented here includes:

- Color pipeline configuration: MPCC output gamma modes, LUT bank selection, RAM A/B segmented PWL regions, gamut remap matrices, output CSC matrices, denorm clamps, RMU shaper LUTs, and RMU 3D LUT contents.
- Composition and routing state: MPC output muxes, DWB muxing, DPP/OPP/MPCC/DWB pending status, rate/flow-control state, vupdate locks, and soft-reset bits.
- Power and clock state: MPC display-clock gates, RMU memory power controls, and HPO clock-control fields.
- Diagnostics: MPC CRC enable/source/result fields and perfmon counter configuration, states, current values, interrupts, and high/low readback values.
- Backlight and adaptive brightness state: PWM user/ambient/target/current/final/min duty values, ABM enable/bypass controls, ACE curves, luma statistics, histogram bins/results, sample-rate frame counters, missed-frame flags, and lock/update-pending flags.
- Audio controller state: HDA CORB pointers, reset/control bits, memory-error status, and CORB sizing/capability information.

Persistence is hardware-defined. Configuration fields generally remain until overwritten, reset, power-gated, or restored after suspend/resume. Status, pending, current-mode, current-mux, CRC, perfmon, histogram, missed-frame, memory-error, and interrupt-like fields may be read-only, sticky, write-one-to-clear, self-clearing, or latch-on-read depending on the register. This generated header only supplies bit positions; it does not express access type or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h`, which supplies matching register offsets and base-index constants.
- AMD's generated DCN 3.0.3 register database.
- Display Core register-helper macros that consume these generated names through token pasting.

Relevant integration points in the inspected tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h`, where `MPC_REG_LIST_DCN3_0`, `MPC_OUT_MUX_REG_LIST_DCN3_0`, `MPC_RMU_GLOBAL_REG_LIST_DCN3AG`, and `MPC_RMU_REG_LIST_DCN3AG` enumerate many `MPCC_OGAM`, `MPC_OUT`, and `MPC_RMU` registers covered by this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h`, where `MPC_COMMON_MASK_SH_LIST_DCN32` and related field-list macros use `SF(...)` against several field names present here, including output CSC, denorm, MPCC output gamma, DWB mux, and flow-control fields.
- ABM/backlight hardware code and resource tables that use the `ABM0_*` and `ABM1_*` field masks for PWM, ACE, histogram, luma-stat, and lock/update programming.
- Display audio/HDA code that uses the Azalia CORB/RIRB masks together with the matching offsets to manage command and response DMA rings.

The generated constants are compile-time data for hardware access. They are not a standalone abstraction and are meaningful only with the matching register offsets, register-block tables, and access helpers.

## Risks And Edge Cases

- Mask/shift drift is the main risk. A wrong generated value can compile cleanly while writing or reading the wrong hardware bits.
- This chunk is artificially bounded. It starts after the beginning of `MPCC_OGAM0` and ends at the start of the `RIRB_LOWER_BASE_ADDRESS` block, so adjacent chunks are needed for complete file-level reasoning.
- The repeated RAM A/RAM B and RGB region tables are copy-sensitive. Prefix, instance, channel, bank, or region-number mistakes can affect only one color channel, one LUT bank, or one MPCC instance.
- Double-buffered and current-status fields are easy to misuse. `*_CURRENT`, update-pending, frame-start, lock, and ignore-master-lock fields require correct sequencing around vblank/frame-start updates.
- Color LUT and matrix fields are user-visible. Bad masks can produce wrong gamma, gamut remap, CSC, denorm clamp, HDR/SDR conversion, or 3D LUT behavior without causing an obvious kernel failure.
- Soft reset, clock gating, and memory-power fields can disrupt active display hardware if written outside the intended power-sequencing path.
- CRC and perfmon fields mix configuration, status, thresholds, interrupt status, and acknowledgement bits. Treating ack or sticky status masks as ordinary configuration can lose diagnostics or leave interrupts asserted.
- ABM histogram/luma fields include readback-in-progress, missed-frame, clear, and lock bits. Incorrect access ordering can sample inconsistent brightness statistics or miss frame-boundary updates.
- HDA CORB fields manage DMA ring state. Incorrect pointer, reset, enable, or memory-error handling can break display-audio command transport.

## Test Signals

Useful validation signals for changes touching this generated data include:

- AMDGPU/DC display build coverage for the DCN 3.0.3 target; token-pasting users catch missing or renamed generated macros at compile time.
- Modeset and color-management tests on matching hardware: output gamma, gamut remap, output CSC, denorm clamp, RMU shaper LUT, and 3D LUT programming should produce expected visual output.
- CRC/perfmon diagnostics: enabling MPC/HPO counters or CRC capture should yield stable, expected register readback and interrupt/ack behavior.
- Backlight and ABM tests: brightness changes, ambient/ABM level updates, ACE behavior, luma statistics, histogram bins, missed-frame flags, and lock/update-pending bits should behave across frame boundaries.
- Suspend/resume and runtime power-management tests covering LUTs, backlight state, RMU memory power, HPO/MPC clocking, and audio ring state restoration.
- Display-audio smoke tests on HDMI/DP sinks to verify HDA command transport still works when CORB/RIRB registers are initialized and reset.
