# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 42079-44295

## Purpose

This chunk is a generated AMD DCN 3.5.1 register shift/mask header segment. It contains 2,217 preprocessor definitions and no executable code. The macros describe bit positions and masks for fields in DisplayPort HPO symbol encoder instance 3 (`DP_SYM32_ENC3`), MPC plane-composition instances (`MPCC0`-`MPCC3`), and per-MPCC output-gamma/gamut-remap blocks (`MPCC_OGAM0`-`MPCC_OGAM3`).

Consumers pair these field constants with register offsets from the matching `dcn_3_5_1_offset.h` header and AMD display register helpers. The constants are part of the ABI between driver source, generated register tables, and DCN 3.5.1 display hardware: a wrong mask or shift silently changes which hardware bits are read or written.

## Important API surface

There are no functions or types in this chunk. The important API is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the starting bit number for a field.
- `REGISTER__FIELD_MASK` gives the packed field mask.
- Register access code uses these with helpers such as `FD_SHIFT`, `FD_MASK`, `SF`, `SE_SF`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and block-specific register tables.

The major field groups are:

- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL7` through `...GSP_CONTROL14`: Generic Secondary-data Packet controls for DP symbol encoder 3. The common fields cover video/idle continuous transmission enables, one-shot trigger, one-shot position, double buffering, payload size, SOF reference, deadline-missed and pending status, double-buffer pending status, and a 16-bit transmission line number. The chunk starts mid-`GSP_CONTROL7`: masks for all fields are present, but the first two shift definitions for `GSP_VIDEO_CONTINUOUS_TRANSMISSION_ENABLE` and `GSP_IDLE_CONTINUOUS_TRANSMISSION_ENABLE` are immediately before the requested line range.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_METADATA_PACKET_CONTROL`: metadata packet enable, double-buffer enable, pending status, and line-number/trigger fields used for DP metadata sideband timing.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_AUDIO_CONTROL0`: audio secondary packet controls, including audio mute and ASP/ATP/AIP/ACM packet enables plus audio packet timing/status fields.
- `DP_SYM32_ENC3_DP_SYM32_ENC_VID_CRC_CONTROL`, `...VID_CRC_STATUS`, `...VID_CRC_RESULT0` through `...RESULT3`, and `...SPARE`: video CRC control, one-shot/continuous status, and four CRC result registers for stream validation/debug.
- `DP_SYM32_ENC3_DP_SYM32_ENC_MEM_POWER_CONTROL`: memory power force/disable/low-power/state fields for the symbol encoder block.
- `MPCC0` through `MPCC3` base composition fields: top/bottom source selection, OPP routing, composition mode, alpha blend mode, premultiplied-alpha mode, active-overlap-only blend, background bits-per-component, bottom gain mode, global alpha/gain, stereo-mixer controls, update-lock selection/status, top and bottom gains, background color components, OGAM memory power controls, and idle/busy/disabled status bits.
- `MPCC_OGAM0` through `MPCC_OGAM3` output gamma fields: OGAM mode/select/current status, LUT index/data, LUT write/read/host/config controls, RAM A and RAM B piecewise-linear region programming, per-channel start/end/base/slope/offset fields, and packed region descriptors for pairs of regions.
- `MPCC_OGAM0` through `MPCC_OGAM2`, plus the beginning of `MPCC_OGAM3`, gamut-remap fields: coefficient format, mode/current status, and A/B coefficient-bank pairs such as `C11_C12`, `C13_C14`, `C21_C22`, `C23_C24`, `C31_C32`, and `C33_C34`. The requested range ends before the full later `MPCC_OGAM3` continuation.

## Control flow and data flow

This header has no runtime control flow. Its data flow is compile-time expansion into register tables and MMIO accessors:

1. ASIC-specific DCN 3.5.1 initialization includes `dcn_3_5_1_sh_mask.h` and the matching offset header.
2. Register-list macros select per-block offsets and field masks/shifts for a concrete hardware instance.
3. Display code encodes desired field values by shifting and masking, then writes the packed value through AMDGPU/DC MMIO helpers.
4. Status paths read MMIO registers, mask/shift fields, and use the decoded values for polling, validation, or diagnostics.

For DP symbol encoder fields, the runtime paths live in HPO DP stream encoder code. That code programs stream enablement, secondary data packets, metadata/audio packet emission, VBID/MSA state, and CRC diagnostics through generated `DP_SYM32_ENC*` register tables.

For MPCC and OGAM fields, the runtime paths live in MPC/color-management code. Plane composition and blending decisions select MPCC top/bottom inputs and alpha/gain modes, while color-management programming writes OGAM LUT indices/data, PWL region descriptors, and gamut-remap coefficients. The repeated MPCC instance layout lets the same code operate on MPCC0-3 by selecting the instance-specific register table.

## State and persistence

The macros hold no runtime state. The state they describe is hardware-resident:

- DP GSP, metadata, and audio packet registers determine how secondary data packets are emitted on a stream. Continuous/one-shot enable bits and line-number fields persist until overwritten, display reset, power-gate, modeset reinitialization, or firmware/hardware reset.
- DP CRC control/status/result fields expose stream validation state. One-shot pending/status bits are timing-sensitive and may change as frames pass.
- MPCC selection, OPP routing, alpha/gain, background color, stereo-mixer, and update-lock fields define active composition state for display pipes.
- OGAM LUT RAM A/B, LUT index/data, region descriptors, offsets, bases, starts, ends, and slopes define output transfer-function state. These are persistent hardware tables and packed control registers, so stale or partial programming can affect visible color until the block is reprogrammed or reset.
- Memory-power fields such as `MPCC_OGAM_MEM_PWR_FORCE`, `MPCC_OGAM_MEM_PWR_DIS`, `MPCC_OGAM_MEM_LOW_PWR_MODE`, and state bits affect low-power behavior and may interact with display power management.

## Dependencies and integration points

- The matching generated offset header is required; these field macros only identify bit layout, not register addresses.
- `dmub/src/dmub_dcn351.c` includes `dcn_3_5_1_sh_mask.h` for DCN 3.5.1 ASIC register initialization, though this specific chunk's DP/MPCC fields are mainly consumed by display pipeline code rather than DMUB mailbox-only paths.
- HPO DP stream encoder code uses `DP_SYM32_ENC*` register/mask tables for stream setup, secondary packet programming, audio packet controls, and CRC diagnostics.
- MPC/MPCC code uses the `MPCC*` and `MPCC_OGAM*` fields for plane composition, blend/gain/background setup, update-lock handling, output gamma LUT programming, and gamut-remap programming.
- The generated naming convention is an integration point: register-table macros assume exact spelling of register and field names, so renames or missing companion offsets break builds, while wrong numeric values can pass builds and fail only at runtime.

## Risks and edge cases

- The chunk begins mid-register and ends mid-family. `GSP_CONTROL7` is missing two shift definitions from this range, and `MPCC_OGAM3` RAMB/gamut continuation is outside this range. The final per-file merge must reconcile adjacent chunks before treating either family as complete.
- Copy/paste or generator drift across repeated instances is high risk. `MPCC0`-`MPCC3` and `MPCC_OGAM0`-`MPCC_OGAM3` should stay structurally identical except for instance number and intentional boundary placement.
- Packed LUT and region fields are especially sensitive: LUT offsets are 9-bit fields, region segment counts occupy the high nibble positions in packed region pairs, start/end/base/slope values use 16- or 18-bit masks depending on register, and coefficient pairs are two 16-bit fields. A single shift error corrupts color tables.
- Full-register writes must preserve reserved or unrelated bits. Many registers combine control, status, pending, and line-number fields.
- Packet-timing fields can cause sink-specific failures. Incorrect GSP/audio/metadata line numbers, double-buffering, or one-shot triggers may only fail with HDR metadata, audio packet changes, replay/panel features, or particular DP sinks.
- Power controls can hide defects: forcing/disabling OGAM memory power may mask sequencing bugs or increase display power.
- Status fields such as pending, current mode, idle/busy/disabled, memory power state, and CRC one-shot pending should not be treated as writable configuration fields unless the hardware spec says so.

## Test signals

- Build coverage with DCN 3.5.1 enabled should catch missing macro names when register-list macros instantiate DP, MPCC, OGAM, and DMUB register tables.
- Static consistency checks should verify that each `__SHIFT` has a matching `_MASK`, and that each mask width matches the expected field width after shifting.
- Cross-version comparison against neighboring DCN 3.5.0/DCN 3.x headers should show expected structural alignment for repeated DP symbol encoder, MPCC, OGAM, and gamut-remap fields.
- Runtime DP tests should exercise HDR/metadata packet programming, audio packet enable/mute transitions, stream enable/disable, CRC one-shot and continuous modes, and modeset/suspend/resume reinitialization.
- Runtime MPC tests should cover multi-plane composition, alpha blending, global alpha/gain, background color fill, update locks, MPCC busy/idle polling, and OPP routing changes.
- Color-management tests should exercise gamma/degamma or output gamma LUT updates, PWL region programming, gamut-remap coefficient banks A/B, HDR color paths, and repeated updates across MPCC instances 0-3.
- Power-management tests should observe display stability and power after OGAM memory low-power/force/disable paths, including reset and resume cycles.
