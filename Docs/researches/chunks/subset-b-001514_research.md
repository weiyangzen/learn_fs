# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_sh_mask.h lines 4132-7720

## Scope

This chunk covers lines 4132-7720 of the AMD DCE 11.0 register mask header. It is a generated/declarative C preprocessor header region, not executable code: the content is a dense catalog of `#define` constants for register field masks and their corresponding shift counts. The chunk contains 3,589 macro definitions. Each field generally appears as a pair:

- `<REGISTER>__<FIELD>_MASK`
- `<REGISTER>__<FIELD>__SHIFT`

The constants are consumed by the AMDGPU display stack when composing read-modify-write values for DCE 11.0 display controller registers, decoding status registers, clearing interrupt bits, programming color pipelines, managing graphics plane addresses, configuring display encoders, and routing DMCU microcontroller interrupts.

## Purpose

The purpose of this chunk is to expose bit layout metadata for several DCE 11.0 hardware blocks:

- GPIO, AUX, DDC, DVO, DAC, UNIPHY, DCRX PHY, and DPHY pad/macro control fields.
- The graphics plane (`GRPH_*`) fetch, format, tiling, flip, address, compression, DFQ, interrupt, underflow, stereo, and counter fields.
- Color-management fields for prescale, input CSC, output CSC, common matrices, denorm, clamp, keying, degamma, gamut remap, dither, LUT, and regamma programming.
- DIG, HDMI, AFMT, and TMDS front-end/back-end encoder and packet/audio fields.
- DMCU control, firmware address, internal memory access, event trigger, interrupt, static-screen, power-gating, vblank, and performance-monitor interrupt fields.

The header lets C code avoid hard-coded bit numbers while still using raw MMIO register programming. For example, a driver can mask/shift `GRPH_CONTROL__GRPH_FORMAT`, `DIG_BE_CNTL__DIG_MODE`, `HDMI_CONTROL__HDMI_DEEP_COLOR_DEPTH`, or `DMCU_INTERRUPT_STATUS__VBLANK1_INT_CLEAR` with symbol names tied to the hardware register manual.

## Important APIs, Types, and Functions

This chunk defines no C functions, structs, enums, or storage objects. Its public API is the macro namespace itself. Important macro families include:

- `DC_GPIO_PWRSEQ_Y`, `DC_GPIO_PAD_STRENGTH_1`, `DC_GPIO_PAD_STRENGTH_2`, `PHY_AUX_CNTL`, `DC_GPIO_I2CPAD_*`: GPIO, power-sequencing, HPD/sync, AUX, DDC, I2C pad enable, receive, pull-down, and drive strength fields.
- `DVO_VREF_CONTROL`, `DVO_SKEW_ADJUST`: digital video output reference voltage and skew tuning fields.
- `DAC_MACRO_CNTL_RESERVED*`, `UNIPHY_MACRO_CNTL_RESERVED*`, `DCRX_PHY_MACRO_CNTL_RESERVED*`, `DPHY_MACRO_CNTL_RESERVED*`: full-register reserved windows. Each reserved macro has a full `0xffffffff` mask and shift `0`, preserving access to reserved macro-control register slots when a caller or table needs symbolic coverage.
- `GRPH_ENABLE`, `GRPH_CONTROL`, `GRPH_SWAP_CNTL`, `GRPH_PRIMARY_SURFACE_ADDRESS`, `GRPH_SECONDARY_SURFACE_ADDRESS`, `GRPH_PITCH`, `GRPH_UPDATE`, `GRPH_FLIP_CONTROL`, `GRPH_DFQ_*`, `GRPH_INTERRUPT_*`, `GRPH_COMPRESS_*`, `GRPH_XDMA_*`, `GRPH_STEREOSYNC_FLIP`, `HW_ROTATION`: primary graphics plane format, tiling, memory address, flip, compression, synchronization, and fault/underflow controls.
- `PRESCALE_*`, `INPUT_CSC_*`, `OUTPUT_CSC_*`, `COMM_MATRIX*`, `DENORM_CONTROL`, `OUT_*`, `KEY_*`, `DEGAMMA_CONTROL`, `GAMUT_REMAP_*`, `DCP_SPATIAL_DITHER_CNTL`, `DC_LUT_*`, `REGAMMA_*`, `ALPHA_CONTROL`: color-processing and blending register fields.
- `DCP_CRC_*`, `DIG_OUTPUT_CRC_*`, `AFMT_AUDIO_CRC_*`: CRC control/result fields used as display and audio test or validation hooks.
- `DIG_FE_CNTL`, `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, `DIG_FIFO_STATUS`, `DIG_DISPCLK_SWITCH_*`, `DIG_LANE_ENABLE`, `DIG_TEST_PATTERN`, `DIG_RANDOM_PATTERN_SEED`: digital encoder front-end/back-end selection, test-pattern, FIFO, lane, and clock-switch metadata.
- `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_AUDIO_PACKET_CONTROL`, `HDMI_ACR_*`, `HDMI_*_PACKET_CONTROL*`, `HDMI_INFOFRAME_CONTROL*`, `HDMI_GC`: HDMI data scrambling, deep color, AVMUTE, ACR, VBI, generic packet, and infoframe control bits.
- `AFMT_*`: audio formatter packet control, IEC 60958 channel status fields, generic and AVI/MPEG/audio infoframe payload fields, ISRC payload bytes, audio source selection, DTO debug, ramp/test, status, and CRC fields.
- `TMDS_*`: TMDS control character generation, feedback, debug, DC balancer, CTL bit generation, stereo sync, and sync pattern fields.
- `DMCU_*`: display microcontroller reset/enable/status, firmware and PC addresses, IRAM/ERAM access, software/internal events, interrupt status/clear, interrupt masks to host/uC, XIRQ selection, static-screen events, and perfmon interrupt routing.

Consumers normally combine these with register offset headers, ASIC-specific register accessor macros, and AMDGPU display helper macros such as field update/read helpers in the surrounding driver tree.

## Control Flow

There is no local runtime control flow. The practical control flow is imposed by callers:

1. Driver code chooses a DCE 11.0 register offset from a companion register header.
2. It composes a value by shifting a field value by `<FIELD>__SHIFT` and constraining it with `<FIELD>_MASK`.
3. It writes the register, or reads a register and extracts a field by applying the same mask/shift pair.
4. For status/interrupt registers, code may write a matching `*_CLEAR` or `*_ACK` field back to clear a latched condition.

The chunk itself therefore behaves as a hardware contract. Bugs are not branch bugs in this file; they are bitfield mapping bugs that propagate into all display initialization, modeset, flip, audio, interrupt, or power-management paths using these symbols.

## State and Persistence Behavior

The macros do not allocate or persist software state. They describe persistent or latched state inside DCE hardware registers:

- `GRPH_PRIMARY_SURFACE_ADDRESS`, `GRPH_SECONDARY_SURFACE_ADDRESS`, high address, pitch, tiling, compression, and update-lock fields persist graphics plane programming until the next modeset or flip sequence changes them.
- `GRPH_UPDATE`, `GRPH_FLIP_CONTROL`, `GRPH_INTERRUPT_STATUS`, `GRPH_XDMA_CACHE_UNDERFLOW_DET_STATUS`, `DCP_CRC_*`, `DIG_FIFO_STATUS`, `HDMI_STATUS`, `AFMT_STATUS`, and many `DMCU_INTERRUPT_STATUS*` fields represent transient, pending, latched, or ack/clear state.
- `DC_LUT_*`, `REGAMMA_*`, CSC, gamut, degamma, denorm, clamp, key, alpha, dither, and prescale fields represent programmed color pipeline state.
- `DMCU_ERAM_*`, `DMCU_IRAM_*`, firmware checksum/address, event, and interrupt-mask fields control the display microcontroller and its memory access windows.
- Full-register reserved macros expose opaque hardware state. Drivers should treat them carefully because reserved fields can have undocumented side effects across ASIC revisions.

## Dependencies

The direct dependency is the C preprocessor. There are no includes visible in this chunk, but the macros depend on the rest of the AMD ASIC register infrastructure for meaning:

- Companion offset headers for DCE 11.0 register addresses.
- AMDGPU display MMIO helpers that use mask/shift constants to read and write bitfields.
- Hardware programming tables and block-specific code for DCP, DIG, HDMI, AFMT, DMCU, DCRX, DPHY, and UNIPHY.
- DCE 11.0 hardware documentation or generated register database that must match these constants.

The macro names encode dependencies on display block naming conventions: `DCP` for display controller pipe, `DIG` for digital encoder, `AFMT` for audio formatter, `DMCU` for display microcontroller, and `GRPH` for graphics plane registers.

## Integration Points

Likely integration points in the broader driver are:

- Plane programming and page-flip code uses `GRPH_*` address, tiling, format, pitch, flip, update, interrupt, DFQ, XDMA, and stereosync fields.
- Color-management code uses `INPUT_CSC_*`, `OUTPUT_CSC_*`, `GAMUT_REMAP_*`, `REGAMMA_*`, `DC_LUT_*`, `DEGAMMA_CONTROL`, `PRESCALE_*`, and clamp/denorm/dither fields.
- Display CRC and validation paths use `DCP_CRC_*`, `DIG_OUTPUT_CRC_*`, and `AFMT_AUDIO_CRC_*`.
- HDMI and DVI/TMDS encoder setup uses `DIG_*`, `HDMI_*`, and `TMDS_*` fields for link mode, packet generation, deep color, scrambling, infoframes, test patterns, and lane enables.
- Audio-over-HDMI/DP setup uses `AFMT_*`, `HDMI_AUDIO_PACKET_CONTROL`, `HDMI_ACR_*`, and IEC 60958 channel status fields.
- Power, backlight, static-screen, vblank, and microcontroller integration uses `DMCU_*` control, event, memory, interrupt, and perfmon routing fields.
- Board/connector bring-up paths use GPIO, HPD, AUX, DDC/I2C pad, DVO, DAC, UNIPHY, DCRX PHY, and DPHY macro fields.

## Risks

- Incorrect mask or shift values can silently corrupt adjacent fields during read-modify-write operations. High-risk examples include `GRPH_CONTROL` tiling/format bits, `DIG_BE_CNTL` encoder routing, `HDMI_CONTROL` deep-color/scrambling bits, and DMCU interrupt masks.
- Many interrupt status fields define both `*_OCCURRED` and `*_CLEAR` with the same mask. Callers must know whether a field is read-only status, write-one-to-clear, or an enable mask; the macro names alone do not enforce safe access.
- `*_MASK_MASK` names, such as interrupt mask fields, can be visually confusing because the first `MASK` is part of the hardware field name and the second is the generated suffix. This increases review risk in manual updates.
- The long `DCRX_PHY_MACRO_CNTL_RESERVED0` through `DCRX_PHY_MACRO_CNTL_RESERVED379` range and similar reserved windows have full-register masks. Accidental writes through these definitions can touch undocumented register space.
- Address fields such as `GRPH_PRIMARY_SURFACE_ADDRESS`, `GRPH_COMPRESS_SURFACE_ADDRESS`, and XDMA recovery addresses mask off low bits and split high bits. Callers must preserve alignment and high-address programming for large GPU addresses.
- Color pipeline fields pack signed, fixed-point, segmented LUT, and matrix coefficients into 16- or 18-bit ranges. Incorrect signedness or scaling in caller code will not be caught by these macros.
- This header is generated-style hardware metadata. Manual edits are risky unless they are synchronized with register offset headers and the authoritative ASIC register database.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Compile coverage: all macros referenced by DCE 11.0 display code resolve with no duplicate/conflicting definitions.
- Static checks: every used field has a matching `_MASK` and `__SHIFT`; each mask aligns with its shift; full-register masks use shift `0`; no field pairs overlap unexpectedly within a register unless they intentionally alias status/clear semantics.
- Display bring-up: modeset tests across HDMI/DVI/DP paths, including deep color, scrambling, audio, and infoframe programming.
- Plane tests: page flips, primary/secondary surface selection, pitch/tiling modes, compression, rotation, stereo sync, and XDMA underflow recovery.
- Color tests: LUT/regamma/degamma, CSC, gamut remap, dithering, clamping, keying, and alpha blending checks.
- Interrupt tests: vblank, page flip, DMCU, static-screen, perfmon, HDMI/AFMT status, FIFO error, and underflow interrupt acknowledge paths.
- CRC tests: DCP output CRC, DIG output CRC, and AFMT audio CRC paths can detect incorrect field extraction or programming.

## Chunk Notes for Merge

This chunk starts mid-header at `DC_GPIO_PWRSEQ_Y` fields and ends within the DMCU perfmon interrupt-to-uC mask definitions. Cross-chunk reconciliation should merge this with earlier/later DCE 11.0 register definitions to produce a whole-file view. The final per-file report should not treat this chunk as owning register offsets or executable behavior; it supplies mask/shift metadata for the code that includes this header.
