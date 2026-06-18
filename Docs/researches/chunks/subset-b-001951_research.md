# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 54468-56733

## Purpose

This chunk is generated AMD DCN 3.2.0 register bitfield metadata. It defines C preprocessor constants for hardware register fields using the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming contract. There is no executable logic in this range; the values are compile-time inputs for AMDGPU display/audio/PHY register helpers that pack, extract, and preserve individual fields during MMIO or indirect-register accesses.

The assigned range contains 2,027 `#define` entries: 1,016 shift macros and 1,011 mask macros. It begins in the tail of the `AZF0ENDPOINT7` Azalia output endpoint pin-control block, covers all eight repeated `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` input endpoint blocks, and ends at the start of the `c20_phy_cr0_rdpcspipecrind` address block. Although this file is under a mirrored `ceph-client` tree, the content is AMDGPU DCN ASIC register metadata, not Ceph filesystem code.

## Major Register Areas

The first portion completes fields for `AZF0ENDPOINT7` output audio endpoint pin control. It covers IEC 60958 channel-status override words 2-8 for sampling frequency, original sampling frequency, sampling-frequency coefficient, MPEG surround information, CGMS-A, and channel-number fields. It then defines output endpoint association/status/snapshot/control fields: association info, digital output active status, LPIB snapshot lock and wrap count, current LPIB value, LPIB timer snapshot, coding type, format-changed flag/ack/reason/response, wireless-display identification, remote keepalive enable/capability, audio enable status, and audio enabled/disabled/format-changed interrupt status fields.

The central portion repeats the same `azf0inputendpointN_inputendpointind` field layout for input endpoints 0 through 7. Each input endpoint block defines:

- Input converter capability fields: channel capability, amplifier presence, amplifier/format override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, widget delay, and widget type.
- Input converter programming fields: converter format number of channels, bits per sample, sample base divisor/multiple/rate, stream type, channel ID, stream ID, digital converter flags, channel status category code, and keepalive.
- Input converter parameter fields: supported stream formats, audio rate capabilities, and audio bit capabilities.
- Input pin capability fields: widget capabilities, impedance sense, trigger required, jack detection, headphone drive, output/input capability, balanced I/O, HDMI, VREF control, EAPD capability, and DP capability.
- Input pin runtime control/status fields: unsolicited response tag/enable, input pin sense, input enable, multichannel enable/mute/channel ID for channels 0-7, HBR capability/enable, channel allocation, hot-plug clock-gating/control/audio-enabled status, forced unsolicited response payload, configuration default decoding, LPIB snapshot/value/timer snapshot, input activity/channel layout UR enables, and HDMI/DP audio infoframe fields.

The final portion starts the `C20_PHY_CR0` PHY control register block. In this chunk it defines ID code low/high fields, reference-clock override fields, MPLLA/MPLLB divider-clock override fields, HDMI override fields, and the beginning of `MPLLA_OVRD_IN_0`. These are 16-bit PHY-side masks rather than the 32-bit Azalia endpoint masks used earlier in the range.

## APIs, Types, And Macros

This chunk defines no functions, structs, enums, variables, locks, allocation paths, or exported C symbols. Its public contract is the macro namespace:

- `__SHIFT` constants name the least-significant bit position for a field.
- `_MASK` constants name the field mask in its final register position.
- Full-register fields such as `LPIB`, `LPIB_TIMER_SNAPSHOT`, `ASSOCIATION_INFO`, and `STREAM_FORMATS` use `0xFFFFFFFFL` masks.
- Input endpoint names encode both the logical instance and register family, for example `AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME__INFOFRAME_VALID_MASK`.
- C20 PHY names encode the PHY instance and sub-block, for example `C20_PHY_CR0_SUP_DIG_REFCLK_OVRD_IN_0__REF_CLK_RANGE_MASK`.

Consumers normally include this header together with the matching DCN 3.2.0 offset/index header. Token-paste register helpers use matching `ixAZF0*` and `ixC20_PHY*` index macros for address selection, then use these shift/mask macros to update individual fields through read-modify-write helpers.

## Control Flow

There is no runtime control flow in the header. Runtime sequencing is provided by AMD display, audio, and PHY code that includes these generated constants.

For audio input endpoints, driver code typically selects an input endpoint indirect register index, reads or writes the endpoint data window, and uses these masks to decode capabilities or program stream format, channel/stream ID, digital converter flags, multichannel routing, HBR, channel allocation, hot-plug clocking, LPIB snapshots, and unsolicited response behavior. Status fields such as input activity, infoframe validity, presence detect, and LPIB snapshot values are consumed by higher-level audio/display logic.

For the output endpoint tail, runtime code uses the channel-status override masks to program or decode IEC 60958 metadata and uses the format-change, keepalive, and audio enable/disable interrupt status fields to report or acknowledge state transitions.

For the C20 PHY block, display link bring-up and PHY programming sequences use the reference-clock, MPLL divider, HDMI, and MPLLA override fields while configuring links. Correct ordering, polling, and reset sequencing are not described here; this header only supplies bit positions.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. It describes hardware-backed state:

- Azalia/HDA codec endpoint capabilities and controls for audio input and output paths.
- Stream format and channel mapping state that connects HDA streams to HDMI/DP audio paths.
- Multichannel, HBR, channel allocation, audio infoframe, and IEC 60958 channel-status metadata.
- Hot-plug, unsolicited response, format-change, audio enable/disable, input activity, and LPIB snapshot status.
- PHY reference-clock, bandgap, MPLL divider, HDMI mode, and MPLLA override state.

Persistence is defined by hardware. Programmed control fields generally retain values until the driver, firmware, reset, power-gating transition, or suspend/resume restore path changes them. Status and interrupt fields may be read-only, latched, sticky, self-clearing, write-one-to-clear, or side-effect-sensitive depending on the hardware register specification; the generated shift/mask header does not encode those access policies.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor naming contract shared with `dcn_3_2_0_offset.h`, where matching `ixAZF0ENDPOINT7_*`, `ixAZF0INPUTENDPOINT[0-7]_*`, and `ixC20_PHY_CR0_*` indexes are defined. These shift/mask constants also depend on DCN register helper macros that combine masks and shifts safely for read-modify-write access.

Direct include sites in this source tree include DCN 3.2 display and platform paths such as:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`

Functional integration points include HDMI/DP audio enumeration, HDA codec verb emulation, audio format programming, channel allocation and infoframe handling, LPIB position reporting, hot-plug/unsolicited-response paths, audio enable/disable/format-change interrupt handling, and DCN PHY/link programming for C20 PHY CR0 reference clock/MPLL/HDMI state.

## Risks And Edge Cases

The main risk is silent hardware misprogramming from generated mask/shift drift. A wrong mask can preserve or overwrite the wrong bits during read-modify-write; a wrong shift can encode valid-looking values into the wrong field. In audio paths this can show up as missing HDMI/DP audio, wrong sample rate or bit depth, incorrect channel mapping, stale LPIB position, bad infoframe/channel allocation, lost hot-plug or unsolicited responses, or broken format-change acknowledgements.

The eight `AZF0INPUTENDPOINT` blocks are highly repetitive. That repetition makes generator or caller mix-ups hard to detect by inspection: endpoint 0 through endpoint 7 share the same local layout but refer to different endpoint index/data windows. A token-paste mistake may only break one display/audio route or one connector configuration.

Several fields represent side-effect-sensitive hardware state. Interrupt status, format-change, audio enable/disable flags, LPIB snapshot lock, input activity, forced unsolicited responses, and hot-plug control fields require the correct access policy from the register specification and surrounding driver code. The presence of a mask here does not mean arbitrary writes are safe.

The C20 PHY portion changes width and domain from 32-bit Azalia endpoint registers to 16-bit PHY control fields. Consumers must not assume the same access path, register width, or side-effect model across the chunk boundary. PHY override fields are especially risky because reference-clock, bandgap, MPLL, and HDMI mode programming can destabilize active links if changed out of sequence.

The chunk boundaries are partial. The range begins after `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0/1` started in the previous chunk and ends before the rest of the `C20_PHY_CR0` MPLLA and subsequent PHY fields. The final per-file research should reconcile adjacent chunks before making complete claims about endpoint 7 output audio or the full C20 PHY CR0 block.

## Test Signals

Useful validation for code that consumes these macros includes:

- Build AMDGPU/DCN 3.2 configurations so token-pasted shift/mask names resolve for display, DMUB, GPIO, IRQ, clock-manager, GMC, and audio paths.
- Compare these generated masks and shifts against AMD's authoritative DCN 3.2.0 register database or a known-good generated header, especially for repeated `AZF0INPUTENDPOINT0-7` layouts.
- Exercise HDMI and DisplayPort audio on every exposed endpoint: stream format changes, sample-rate/bit-depth changes, channel/stream ID assignment, stereo and multichannel playback, HBR paths, channel allocation, and IEC 60958 channel-status metadata.
- Test hotplug, unplug, suspend/resume, display modeset, audio enable/disable, and audio format-change interrupt flows to catch wrong status or acknowledgement fields.
- Validate LPIB and LPIB timer snapshot behavior under active audio playback, including snapshot lock and cyclic-buffer wrap-count handling.
- Exercise unsolicited response and input activity/infoframe change paths where hardware or emulation can generate them.
- Run DP/HDMI link bring-up, retraining, and resume tests on hardware using C20 PHY CR0 to catch bad reference-clock, MPLL divider, HDMI override, or PHY access-width assumptions.

## Cross-Chunk Notes

Earlier chunks in `dcn_3_2_0_sh_mask.h` contain the beginning of `AZF0ENDPOINT7` output endpoint fields, including the first channel-status override registers. Later chunks continue the C20 PHY CR0 definitions after the partial `MPLLA_OVRD_IN_0` group that starts here. The merge/reconciliation lane should combine those ranges before producing final file-level conclusions about the complete DCN 3.2.0 audio endpoint and C20 PHY register map.
