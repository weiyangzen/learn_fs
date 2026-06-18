# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 49631-52079

## Scope

This chunk is a generated AMD DCN 3.2.1 shift/mask header slice. It contains preprocessor constants only: register grouping comments, `_SHIFT` macros for field bit positions, and `_MASK` macros for register-positioned field masks. There are no C functions, structs, enums, branches, loops, allocations, locks, or direct file-backed persistence in this range.

The requested range covers 2,449 source lines, 2,033 `#define` lines, and 374 register or address-block comments. It starts in the middle of the `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL4_ENABLE` family, covers the remaining F2 input-pin audio fields, the F2 codec root/function parameter block, all 16 Azalia stream indirect latency/FIFO blocks, complete endpoint 0 through endpoint 2 codec converter/pin blocks, and the beginning of endpoint 3 through `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR11`. The chunk ends before the rest of endpoint 3's pin-control register family, so adjacent chunks are required for a whole-file view.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU Display Core hardware metadata for DCN 3.2.1 Azalia/HD Audio programming, not Ceph filesystem code.

## Purpose

The purpose of this range is to describe bit layouts for DCN 3.2.1 Azalia audio codec, stream, and endpoint indirect registers. The matching offset header supplies MMIO and indirect-index addresses; this header supplies the field positions and masks used by generated register tables and helper macros to pack writes, decode reads, and preserve unrelated bits during read/modify/write sequences.

The hardware surfaces represented here are:

- F2 codec input-pin control and parameter fields for multichannel enable/mute/channel-id controls, HBR capability/enable, LPIB snapshots, input activity, audio infoframe content, channel status, widget capabilities, and pin capabilities.
- F2 codec root and function parameters for vendor/device ID, revision, subordinate node counts, power state, subsystem ID response bytes, converter synchronization, reset, supported sample rates/bit depths, stream formats, and supported power states.
- `AZF0STREAM0` through `AZF0STREAM15` stream-indirect latency/FIFO telemetry, each with FIFO size limits, latency-counter reset, worst-case latency, cumulative latency, and cumulative request counters.
- `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, and `AZF0ENDPOINT2` endpoint-indirect codec converter and pin-control definitions, including audio widget capability, converter format, channel/stream ID, digital converter channel-status bits, supported formats/rates, stripe/ramp/GTC timing controls, pin descriptors, speaker/channel allocation, sink information, hotplug/audio enable controls, IEC 60958 channel-status overrides, LPIB snapshots, format-change reporting, remote keepalive, and audio interrupt status.
- The start of `AZF0ENDPOINT3`, covering the same converter block and early pin block through audio descriptor 11.

These constants are generated data rather than executable logic, but they form an ABI between AMDGPU display/audio code, generated register access tables, firmware-facing display code, and the GPU's HD Audio/Azalia hardware. A wrong shift or mask can compile cleanly while causing HDMI/DisplayPort audio setup, channel mapping, timing readback, hotplug reporting, or interrupt handling to touch the wrong hardware bits.

## Important APIs, Types, And Macros

This chunk exports the standard AMD generated register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register-positioned form.
- `//<REGISTER>` comments group the following definitions by hardware register.
- `// addressBlock: ...` comments mark indirect register windows such as codec root, stream, and endpoint blocks.

There are no callable APIs or C data types in this chunk. Runtime code consumes these symbols through AMD display register-list and mask/shift-list infrastructure, normally paired with addresses from `dcn_3_2_1_offset.h`.

Important macro families in this range include:

- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_*` and `AZALIA_F2_CODEC_INPUT_PIN_PARAMETER_*`.
- `AZALIA_F2_CODEC_ROOT_PARAMETER_*` and `AZALIA_F2_CODEC_FUNCTION_*`.
- `AZF0STREAM[0-15]_AZALIA_FIFO_SIZE_CONTROL`, `AZALIA_LATENCY_COUNTER_CONTROL`, `AZALIA_WORSTCASE_LATENCY_COUNT`, `AZALIA_CUMULATIVE_LATENCY_COUNT`, and `AZALIA_CUMULATIVE_REQUEST_COUNT`.
- `AZF0ENDPOINT[0-3]_AZALIA_F0_CODEC_CONVERTER_*` for converter format, channel stream ID, digital converter status, supported stream/rate information, stripe control, ramp rate, GTC embedding, and GTC counter deltas.
- `AZF0ENDPOINT[0-3]_AZALIA_F0_CODEC_PIN_PARAMETER_*` and `AZF0ENDPOINT[0-3]_AZALIA_F0_CODEC_PIN_CONTROL_*` for pin capabilities, unsolicited responses, pin sense, widget output enable, speaker/channel allocation, audio descriptors, HBR/lipsync/sink info, hotplug state, multichannel state, LPIB state, format-change reporting, and remote keepalive.
- `AZF0ENDPOINT[0-2]_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_*` for IEC 60958 channel-status override controls.
- `AZF0ENDPOINT[0-2]_AZALIA_F0_AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`.

## F2 Input Pin And Codec Root Fields

The chunk begins with the tail of the F2 input-pin multichannel controls. The visible multichannel families expose a repeated layout: an enable bit at bit 0, mute at bit 1, and a 4-bit channel ID at bits 4 through 7. The range includes odd/even multichannel registers across channels 1, 3, 5, 7 and the tail of channel 4 plus channel 6, while earlier channel definitions live in the preceding chunk.

`AZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR` exposes high-bit-rate audio capability and enable bits. The LPIB families define a snapshot lock, an 8-bit cyclic-buffer wrap count, the 32-bit link position in buffer, and a 32-bit timer snapshot. `INPUT_STATUS_CONTROL` exposes input activity, channel-layout state, and unsolicited-response enables for activity or channel-layout/channel-status infoframe changes. `INFOFRAME` exposes channel count, channel allocation, byte 5, and validity. `CHANNEL_STATUS_L` and `_H` expose full 32-bit low/high channel-status payloads.

The F2 input pin parameter families describe HD Audio widget/pin capabilities. `AUDIO_WIDGET_CAPABILITIES` includes flags for channel capability, input/output amplifier presence, amplifier parameter override, stripe, processing widget, unsolicited response support, connection list, digital output, power control, left/right swap, widget delay, and type. `PARAMETER_CAPABILITIES` includes impedance sense, trigger required, jack detection, headphone drive, output/input capability, balanced I/O, HDMI, VREF control, EAPD, and DP capability bits.

The `azroot_f2codecind` address block then defines root and function-level codec fields. Root parameters provide vendor/device ID, revision ID, and subordinate node count. Function-control registers expose power-state set/actual values, clock-stop OK, settings reset, subsystem ID response bytes, converter synchronization, and codec reset. Function parameter registers expose subordinate node count, group type, supported sample rates/bit depths, supported stream formats, and power-state capability flags such as clock-stop and EPSS.

## Stream Indirect Blocks

The `azf0stream0_streamind` through `azf0stream15_streamind` blocks are structurally identical. Each stream exposes:

- `AZALIA_FIFO_SIZE_CONTROL`, with 7-bit minimum FIFO size, 7-bit maximum FIFO size, and an 8-bit maximum latency support field.
- `AZALIA_LATENCY_COUNTER_CONTROL`, with a latency-counter reset bit.
- `AZALIA_WORSTCASE_LATENCY_COUNT`, a full 32-bit worst-case latency counter.
- `AZALIA_CUMULATIVE_LATENCY_COUNT`, a full 32-bit cumulative latency counter.
- `AZALIA_CUMULATIVE_REQUEST_COUNT`, a full 32-bit cumulative request counter.

These definitions are used by runtime display/audio code or diagnostics to configure or inspect stream buffering and latency behavior. The macros do not identify which stream is active for a given audio path; that mapping is supplied by higher-level resource allocation and hardware programming code. The counters should be treated as hardware telemetry, not persistent software accounting.

## Endpoint Converter Blocks

Endpoint 0 through endpoint 2 are complete in this chunk, and endpoint 3 begins with the same converter structure. The converter parameter and control registers define the digital audio converter attached to each endpoint:

- `CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` describes converter widget flags such as channel capability, amplifier presence, format override, stripe support, processing widget, unsolicited-response support, digital/power-control behavior, LR swap, delay, and widget type.
- `CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` packs number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- `CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID` maps converter channel ID and stream ID.
- `CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER` exposes digital converter enable and IEC-style channel-status bits such as validity, validity-config, pre-emphasis, copy, non-audio, professional mode, level, category code, and keepalive.
- `CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `SUPPORTED_SIZE_RATES` expose supported stream formats, audio rate capabilities, and audio bit-depth capabilities.
- `CODEC_CONVERTER_STRIPE_CONTROL` exposes stripe-control and stripe-capability fields.
- `CODEC_CONVERTER_CONTROL_RAMP_RATE` defines an 8-bit ramp-rate control.
- `CODEC_CONVERTER_CONTROL_GTC_EMBEDDING` controls presentation-time embedding, offset-changed signaling, GTC min/max delta clearing, and presentation-time embedding group selection.
- `CODEC_CONVERTER_GTC_COUNTER_DELTA`, `_MIN`, and `_MAX` expose 32-bit GTC delta readbacks.

The converter blocks are central to HDMI/DP audio stream setup. Format, channel count, stream ID, channel ID, sample-rate fields, and digital converter status must remain synchronized with the display audio stream and with the sink's ELD/EDID-derived capabilities.

## Endpoint Pin Blocks

Endpoint pin parameter and control registers describe the external audio pin side of each endpoint. Complete endpoint 0 through 2 blocks include pin widget capabilities, pin capabilities, unsolicited-response controls, pin-sense readback, widget output enable, speaker/channel allocation, audio descriptors, multichannel controls, sink information, hotplug/audio enable state, channel-status overrides, LPIB snapshots, format-change state, remote keepalive, and interrupt status. Endpoint 3 is included through audio descriptor 11 in this chunk.

Key pin-control families include:

- `CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `CODEC_PIN_PARAMETER_CAPABILITIES`, which mirror the HD Audio widget/pin capability surfaces for each endpoint.
- `CODEC_PIN_CONTROL_UNSOLICITED_RESPONSE`, with a 6-bit tag and enable bit.
- `CODEC_PIN_CONTROL_RESPONSE_PIN_SENSE`, exposing a 31-bit impedance-sense field in the visible endpoint blocks.
- `CODEC_PIN_CONTROL_WIDGET_CONTROL`, exposing output enable.
- `CODEC_PIN_CONTROL_CHANNEL_SPEAKER`, with speaker allocation, channel allocation, HDMI/DP connection flags, extra connection info, LFE playback level, level shift, and down-mix inhibit.
- `CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `13` on complete endpoints, each exposing maximum channels, supported frequencies, descriptor byte 2, and for descriptor 0 an additional stereo-frequency byte.
- `CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`, which pack enable, mute, and channel ID fields for multichannel pairs or individual odd channels.
- `CODEC_PIN_CONTROL_RESPONSE_LIPSYNC` and `RESPONSE_HBR`, used for sink timing and high-bit-rate audio capability/enable reporting.
- `CODEC_PIN_CONTROL_SINK_INFO0` through `8`, which expose sink manufacturer/product IDs and packed 8-bit description bytes.
- `CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, with clock gating disable, clock-on state, and an audio-enabled bit.
- `CODEC_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE`, with a payload and force bit for synthetic unsolicited responses.
- `CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`, describing sequence, default association, misc, color, connection type, default device, location, and port connectivity.
- `CODEC_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT`, which expose per-pin link-position and timer snapshots.
- `CODEC_PIN_CONTROL_CODING_TYPE`, `FORMAT_CHANGED`, `WIRELESS_DISPLAY_IDENTIFICATION`, and `REMOTE_KEEPALIVE`.

For endpoint 3, the chunk stops in the middle of the audio descriptor list. The final merged file-level report should combine this range with the next chunk to cover endpoint 3's remaining descriptors, multichannel fields, sink info, hotplug controls, and interrupt/status fields.

## Channel Status Overrides And Interrupt Status

Endpoint 0 through endpoint 2 include `AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`. These fields map to IEC 60958 channel-status override knobs:

- Mode and source number.
- Clock accuracy, word length, and corresponding override-enable bits.
- Sampling frequency, original sampling frequency, and corresponding override-enable bits.
- Sampling-frequency coefficient, MPEG surround info, CGMS-A, and CGMS-A validity.
- Channel numbers for left/right and channels 2 through 7.

These override fields can alter the channel-status information presented to an audio sink. They are value/override style controls in practice: programming an override value without enabling the relevant override bit may have no effect, while leaving an override enabled can make the sink receive stale or policy-inconsistent audio metadata.

Endpoint 0 through endpoint 2 also include audio state and interrupt status surfaces. `AUDIO_ENABLE_STATUS` reports current audio-enable state. `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS` each expose a flag bit, a mask bit, and a type bit. These definitions support interrupt handling around audio enable/disable and audio format changes. The macros do not state whether flags are write-one-to-clear, read-clear, level, or edge-triggered; the driver code and hardware documentation must supply that behavior.

## Control Flow

There is no executable control flow in this header. Runtime flow is supplied by AMDGPU display code that includes this generated mask file, includes the matching generated offset file, and expands generated register access macros or register tables.

Typical runtime usage is:

1. DCN 3.2.1 resource, link-encoder, audio, DMUB, clock, IRQ, or diagnostic code selects an Azalia root, stream, or endpoint indirect register.
2. Generated offset symbols from `dcn_3_2_1_offset.h` identify the MMIO register or indirect index/data pair.
3. Generated register helpers bind those offsets to one or more `_SHIFT` and `_MASK` symbols from this file.
4. Runtime code packs writes, performs read/modify/write updates, reads status fields, polls counters or flags, or decodes register dumps using these masks and shifts.
5. Hardware latches stream/converter/pin configuration, reports sink/audio status, updates latency and LPIB counters, generates audio-related unsolicited responses or interrupts, or exposes channel-status and infoframe data.

This file does not encode reset values, valid enumerations, indirect-index access ordering, volatile semantics, write-one-to-clear behavior, required delays, interrupt acknowledgement rules, or policy for HDMI versus DisplayPort audio.

## State And Persistence Behavior

No software state is stored by this file. It describes MMIO-backed and indirect-register-backed hardware state whose lifetime is governed by GPU reset, display hotplug, modeset, audio stream allocation, link training, sink capability discovery, runtime power management, suspend/resume, interrupt handling, and diagnostic tooling.

Persistent or latched hardware configuration fields in this chunk include codec/function power state, converter synchronization/reset controls, converter format, channel and stream IDs, digital converter enable/channel-status bits, stripe/ramp controls, GTC embedding controls, pin output enable, channel/speaker allocation, multichannel enable/mute/channel IDs, hotplug clock/audio enable controls, configuration default fields, channel-status overrides, coding type, format-change response controls, wireless-display identification, remote keepalive, interrupt masks, and latency-counter reset controls.

Volatile or readback-oriented fields include vendor/device/revision parameters, subordinate node counts, supported formats/rates/power states, HBR capability, LPIB values, timer snapshots, cyclic buffer wrap count, input activity, infoframe validity/content, channel status, stream worst-case and cumulative latency counters, cumulative request counters, GTC delta/min/max readbacks, pin sense, sink info, audio enable status, interrupt flags, output-active state, and format-changed state.

Side-effecting or sequencing-sensitive fields include codec reset, power-state transitions, converter synchronization, HBR enable, digital converter enable, hotplug audio enable, unsolicited-response force, interrupt masks/flags, LPIB snapshot lock, latency-counter reset, GTC min/max clear, channel-status override enables, and format-change acknowledgement controls. Treating these as ordinary static fields can leave audio disabled, generate spurious unsolicited responses, hide real format changes, or report inaccurate timing/counter data.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.2.1 offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`

The offset and mask headers must be generated from the same hardware register database. The matching offset file contains the Azalia index/data MMIO registers such as `regAZF0STREAM0_AZALIA_STREAM_INDEX`, `regAZF0STREAM0_AZALIA_STREAM_DATA`, `regAZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX`, and `regAZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_DATA`, plus indirect offsets such as `ixAZALIA_F2_CODEC_ROOT_PARAMETER_VENDOR_AND_DEVICE_ID`, `ixAZF0STREAM0_AZALIA_FIFO_SIZE_CONTROL`, and `ixAZF0ENDPOINT0_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`.

Local DCN 3.2.1 integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes `dcn/dcn_3_2_1_offset.h` and `dcn/dcn_3_2_1_sh_mask.h`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn321/dcn321_dio_link_encoder.c` and `.h`, which provide DCN 3.2.1 link-encoder construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, which has DCN321-specific register/mask wiring for clock management.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c` and `dmub_srv.h`, which identify `DMUB_ASIC_DCN321`.
- Higher-level display/audio paths under AMDGPU DM and Display Core that use the DCN321 resource pool, link encoders, hotplug handling, audio endpoint setup, and DMUB firmware interactions.

Practical integration surfaces are HDMI/DP audio enumeration, audio stream format programming, channel allocation, HBR audio, sink description reporting, LPIB/timing readback, GTC presentation-time embedding, audio hotplug, unsolicited HD Audio responses, and audio enable/disable/format-change interrupts.

## Risks And Edge Cases

- The chunk starts and ends inside register families. `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL4_ENABLE` is partial at the start, and endpoint 3's pin descriptor family is partial at the end.
- Generated-header drift from the authoritative DCN 3.2.1 register database is the primary risk. Wrong numeric shifts or masks usually compile but produce runtime audio failures.
- The stream blocks are highly repetitive across 16 streams. Copying a symbol with the wrong `AZF0STREAMN` prefix can silently read or reset the wrong stream's latency counters.
- Endpoint blocks are highly repetitive across endpoints 0 through 3. A wrong endpoint prefix can program channel allocation, sink info, converter format, or interrupts for the wrong audio endpoint.
- Many fields are packed byte or nibble fields. Incorrect masks for channel IDs, descriptor bytes, source/channel numbers, sample frequency, or word length can corrupt only part of a metadata word and be difficult to spot in register dumps.
- HBR, channel allocation, speaker allocation, and audio descriptor fields must match sink capabilities. This header provides bit placement only, not validation.
- LPIB snapshot lock, timer snapshots, stream latency counters, and GTC deltas are timing-sensitive readback surfaces. Incorrect access ordering or stale snapshots can produce misleading audio/video synchronization diagnostics.
- Interrupt status fields expose flag, mask, and type bits but not acknowledgement semantics. Treating an interrupt flag as ordinary read-only state can lose or repeat audio enable/disable/format-change events.
- Channel-status override fields can make the sink receive metadata that differs from the active stream format if override-enable bits remain asserted after modesets or stream changes.
- Unsolicited-response force controls are diagnostic-like surfaces. Accidental writes can synthesize HD Audio events and confuse hotplug/audio state machines.
- This mask header cannot protect callers from invalid values, wrong indirect-register selection, wrong write order, missing locking around shared Azalia index/data windows, or writes to status/readback-only fields.

## Test Signals

Useful validation signals for this chunk include:

- Compile coverage for DCN321 display objects that include `dcn_3_2_1_sh_mask.h`, especially `dcn321_resource.c` and any generated register-list users. Missing or renamed macros surface at build time.
- Consistency checks against `dcn_3_2_1_offset.h`: every register family used from this chunk should have a matching direct or indirect offset/index definition.
- Register-database or generated-header diff checks against adjacent ASIC generations to catch unintended DCN 3.2.1 changes in Azalia field placement.
- HDMI and DisplayPort audio smoke tests across stereo, multichannel PCM, and HBR-capable paths, verifying stream format, channel allocation, sink descriptor, and audio enable state.
- Hotplug and modeset tests that confirm unsolicited responses, audio enable/disable interrupts, and format-change interrupts fire and clear correctly.
- Suspend/resume and runtime power-management tests that verify codec/function power state, converter format, channel-status overrides, and audio enable state are restored or reprogrammed correctly.
- Audio/video synchronization diagnostics that compare LPIB snapshots, timer snapshots, GTC delta/min/max, and latency counters against expected stream behavior.
- Register dump decoding for endpoints 0 through 3 and streams 0 through 15, checking that decoded fields align with the active display/audio topology.
- Negative or recovery tests that switch between HDMI and DP sinks, change channel counts and sample rates, enable/disable HBR audio, and verify stale channel-status overrides or multichannel mutes do not persist.

## Chunk Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002047_research.md`. Whole-file research for `dcn_3_2_1_sh_mask.h` must merge adjacent chunks to complete the preceding F2 input-pin multichannel block and the following endpoint 3 Azalia pin-control block.
