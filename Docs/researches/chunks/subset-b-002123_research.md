# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 12459-14996

## Purpose

This chunk is a generated AMD DCN 3.6.0 register shift/mask slice. It contains no executable logic; it exports C preprocessor constants that describe bit positions and bit masks for memory-mapped display-controller registers. Driver code combines these constants with the matching `dcn_3_6_0_offset.h` register offsets so AMDGPU display helpers can pack, unpack, and update individual fields without hard-coding numeric bit layouts at call sites.

The requested range contains 2,113 `#define` entries, split into 1,052 `__SHIFT` macros and 1,061 `_MASK` macros, plus 389 register-name comments and 12 address-block comments. The chunk starts in the middle of the `HUBPRET3_HUBPRET_INTERRUPT` definition group and ends in the middle of `CM1_CM_GAMCOR_RAMB_REGION_18_19`, so both boundaries are artificial line-split boundaries rather than semantic hardware boundaries.

Although this file lives under a local `ceph-client` source mirror, this chunk is AMDGPU DCN display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct I/O operations in this range. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or preserving that field during read/modify/write operations.

The main register families covered here are:

- `HUBPRET3_*`: tail of HUBP request/read-line status support for pipe vblank and read-line interrupts, current read line, snapshot read line, and inside/outside read-line status.
- `CURSOR0_3_*`: HUBP instance 3 cursor control, surface address, size, position, hot spot, stereo offsets, destination offset, cursor memory power state, dynamic metadata address/control/QoS/status/software-data fields.
- `DC_PERFMON10_*`: HUBP-side performance monitor and counter controls, counter state selection, count-off interrupt configuration, per-counter interrupt status/acknowledge bits, and low/high counter value fields.
- `CNVC_CFG0_*`: DPP0 converter/configuration fields for surface pixel format, format control, floating-point bias/scale, color keying, alpha LUT, pre-dealpha, pre-CSC matrices for main and B paths, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0_*`: DPP0 converter cursor overlay fields for cursor enable/mode/color and floating-point cursor scale/bias.
- `DSCL0_*`: DPP0 scaler fields for coefficient RAM access, scaler mode and tap control, 2-tap controls, manual replication, horizontal/vertical scaling ratios and initial phases for luma/chroma/bottom fields, black color, update/autocal, overscan, OTG blanking, recout/MPC size, line-buffer format/memory/counter, DSCL memory power, and output-buffer controls.
- `CM0_*`: DPP0 color-management fields for post-CSC, gamut remap, bias, gamma-correction control, LUT index/data/control, gamma-correction RAM A/B start/end/slope/base/offset/region programming, HDR multiplier coefficients, memory power status, dealpha, coefficient format, debug access, and DPP CRC values.
- `DPP_TOP0_*`: top-level DPP0 control, soft reset, CRC control, and host-read controls.
- `DC_PERFMON11_*`: DPP-side performance monitor/counter fields mirroring the `DC_PERFMON10_*` shape for another performance-monitor instance.
- `CNVC_CFG1_*`, `CNVC_CUR1_*`, and `DSCL1_*`: beginning of the same converter, cursor, and scaler register layout for DPP1.
- `CM1_*`: beginning of DPP1 color-management register layout, continuing through post-CSC, gamut remap, bias, gamma-correction control, LUT access, and most of the gamma-correction RAM A/B region programming included before the chunk boundary.

Many groups are mechanically repeated per hardware instance. DPP0 and DPP1 use the same field names with different numeric instance prefixes, and `DC_PERFMON10` and `DC_PERFMON11` share the same performance-counter register shape.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this generated header:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` and this shift/mask header.
2. Register-list macros token-paste register and field names into per-block register, shift, and mask tables.
3. DCN 3.6 constructors wire those tables into resource-pool objects, IRQ service structures, DMUB service register tables, DPP/DSCL/HUBP blocks, and hardware-sequencer helpers.
4. Runtime display paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; the helpers use these masks and shifts to touch only the intended MMIO bits.

The macros do not encode sequencing rules. Consumers still need to program cursor memory before enabling the cursor, update scaler ratios and taps in the right update window, load gamma/CSC LUTs in hardware-defined order, acknowledge perfmon interrupts correctly, and coordinate DPP/HUBP state with pipe lock, vblank, power, and clock transitions.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It describes hardware-visible state in DCN 3.6 registers:

- HUBP vblank/read-line interrupt mask/type/clear/status bits and sampled read-line state.
- Cursor state for enablement, mode, memory address, dimensions, on-screen position, hot spot, stereo layout, trusted-memory-zone marking, request behavior, memory power, and dynamic metadata transport.
- Performance-monitor state for event selection, counting mode, hardware start/stop/count-off selection, active state, counter values, and interrupt status/acknowledge bits.
- Converter and cursor-overlay state for DPP pixel format conversion, alpha handling, floating-point scale/bias, color keying, pre-CSC/pre-degamma, and cursor colors.
- Scaler state for filter coefficients, tap counts, scaling ratios, phase initialization, recout dimensions, overscan, line-buffer memory layout, and DSCL/OBUF memory power.
- Color-management state for post-CSC, gamut remap, gamma-correction LUT programming, RAM A/B region metadata, HDR coefficients, memory power, debug index/data, and CRC capture.
- DPP top-level state for reset, CRC, and host-read behavior.

Persistence is hardware-defined. Configuration fields generally remain until a modeset, plane update, pipe reprogramming, power-gating event, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, snapshot, debug, CRC, and counter fields may be read-only, sticky, write-one-to-clear, self-clearing, clock-gated, or valid only while the associated pipe and block are powered. This generated header does not identify those access semantics; consumers must rely on the register specification and block-specific driver code.

## Dependencies And Integration Points

This file must remain synchronized with AMD's generated DCN 3.6.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` supplies the matching MMIO addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes both DCN 3.6 generated headers while initializing DMUB register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes the same headers for DCN 3.6 IRQ source setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes them for DCN 3.6 resource construction and hardware-sequencer register tables.
- Shared display block headers such as DPP, DSCL, HUBP, timing-generator, IRQ, and register-helper code consume these generated constants through macro tables rather than including this chunk's field names one by one at most call sites.

The most direct behavioral integration from this range is plane composition and scanout: cursor programming, DPP format conversion, scaler configuration, color management, per-pipe CRC/debug support, HUBP timing interrupts, and DC performance monitoring.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while touching the wrong MMIO bit, corrupting adjacent fields, or silently disabling a feature.
- The file is generated. Manual edits risk diverging from the authoritative register database, the matching offset header, firmware assumptions, and silicon documentation.
- The chunk boundaries are not semantic. The first `HUBPRET3_HUBPRET_INTERRUPT` fields started before line 12459, and the `CM1_CM_GAMCOR_RAMB_REGION_18_19` mask set continues after line 14996.
- Repeated DPP0/DPP1 and perfmon layouts make copy/generator drift hard to see. DPP0 working does not prove DPP1 fields are correct, and one perfmon instance can fail independently from another.
- Cursor address, size, position, pitch, stereo, and hot-spot masks are user-visible. Off-by-one or width errors can cause missing cursors, clipped cursors, wrong stereo cursor placement, invalid memory reads, or TMZ/security mismatches.
- Scaler ratio, phase, tap, and coefficient fields are precision-sensitive. Incorrect masks can cause image blur, ringing, chroma misalignment, crop errors, blank output, or filter RAM programming failures.
- Color-management fields are interoperability- and color-accuracy-sensitive. Wrong CSC, gamut-remap, gamma-region, LUT, bias, coefficient-format, or HDR multiplier masks can produce subtle color regressions that are not caught by simple modeset smoke tests.
- Interrupt/status/ack fields are side-effect-sensitive. Confusing status with clear/ack or enable bits can cause missed vblank/read-line events, stuck perfmon interrupts, or interrupt storms.
- Power-state fields for cursor, DSCL, OBUF, and CM memory can interact with clock gating and power gating; writing them at the wrong time can produce intermittent resume, modeset, or underflow failures.

## Test Signals

Useful validation combines generated-header checks with DCN 3.6 hardware behavior:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed constants should fail in DCN36 DMUB, IRQ, resource, DPP, DSCL, HUBP, or hardware-sequencer register-table construction.
- Mechanically compare this range against AMD's authoritative DCN 3.6.0 register source and the adjacent `dcn_3_6_0_offset.h` names. Allow for the known artificial boundary at the start and end of the requested line slice.
- Run static consistency checks that expected register fields have both `__SHIFT` and `_MASK` definitions when the complete register group is considered across adjacent chunks.
- Exercise cursor enable/disable, movement, hotspot changes, size changes, 2x magnification, stereo cursor paths, TMZ cursor surfaces, suspend/resume, and rapid modesets.
- Exercise DPP scaler paths across identity scale, up/downscale, chroma formats, fractional ratios, recout changes, overscan, line-buffer pressure, and filter coefficient reloads.
- Validate color paths with CRC or visual/color tests for pre-CSC, post-CSC, gamut remap, gamma correction RAM A/B, HDR multipliers, alpha/dealpha/realpha, color keying, and pixel-format conversion.
- Exercise perfmon setup and interrupts for `DC_PERFMON10` and `DC_PERFMON11`, checking counter start/stop, count-off behavior, status/ack handling, and counter high/low reads.
- Watch kernel logs and display diagnostics for vblank/read-line interrupt loss, cursor corruption, scaler underflow, CRC mismatches, color-management regressions, stuck perfmon interrupt status, memory-power transition failures, and resume-only display artifacts.

## Cross-Chunk Notes

The previous chunk contains the beginning of the `HUBPRET3_HUBPRET_INTERRUPT` group. The next chunk continues `CM1_CM_GAMCOR_RAMB_REGION_18_19` and the remaining DCN 3.6 register-field namespace. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.6 shift/mask definitions or all DPP/HUBP instances.
