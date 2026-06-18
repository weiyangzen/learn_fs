# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 47395-49843

## Purpose

This chunk is part of AMDGPU's generated DCN 1.0 register field mask/shift header. It contains no executable C logic; it publishes compile-time bit layout constants for Azalia/HD-audio registers in the display audio block.

Each register field is represented by paired macros:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

Driver code combines these definitions with matching register address macros from `dcn_1_0_offset.h` and with AMD display register helper macros such as `SF(...)`, `REG_SET`, `REG_UPDATE`, and lower-level MMIO read/write helpers. Correctness is therefore a hardware-layout contract: a wrong bit position can compile cleanly while programming the wrong audio endpoint, stream, or status bit.

The range is centered on the DCN 1.0 display audio/Azalia namespace:

- Tail fields for the function-2 input pin, including HBR capability/enable masks, multichannel controls, LPIB snapshot registers, input activity/status, infoframe/channel status, and pin capabilities.
- The `azroot_f2codecind` root/function codec block, including vendor/device and revision parameters, subordinate node counts, power state, subsystem ID response bytes, converter synchronization, codec reset, supported sample rates/formats, and power-state capabilities.
- Sixteen repeated `azf0stream<N>_streamind` stream blocks, each exposing FIFO size and latency counter fields for stream indices 0-15.
- Four repeated `azf0endpoint<N>_endpointind` endpoint blocks, for endpoint indices 0-3. Endpoints 0-2 are fully represented in this chunk; endpoint 3 is present through its audio descriptor fields and then the chunk ends at the next multichannel-control comment.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU display-driver hardware metadata. It has no Ceph filesystem protocol behavior, no distributed filesystem state, and no filesystem persistence semantics.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime APIs in this chunk. The macro namespace is the API surface.

The first section completes function-2 input-pin fields:

- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR__HBR_CAPABLE_MASK` and `...__HBR_ENABLE_MASK` expose HBR audio capability and enable bits.
- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL1_ENABLE`, `MULTICHANNEL3_ENABLE`, `MULTICHANNEL5_ENABLE`, and `MULTICHANNEL7_ENABLE` each provide enable, mute, and channel-ID fields for odd-numbered multichannel pairs.
- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT` expose a snapshot lock, cyclic buffer wrap count, current link position in buffer, and timer snapshot.
- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL` exposes input activity, channel layout, unsolicited-response enablement for activity, and unsolicited-response enablement for channel-layout/channel-status/infoframe changes.
- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_INFOFRAME`, `CHANNEL_STATUS_L`, and `CHANNEL_STATUS_H` expose audio infoframe channel count/allocation/validity and IEC channel-status payload words.
- `AZALIA_F2_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `..._CAPABILITIES` describe pin widget capabilities such as digital/power-control/LR-swap support, widget type, jack detection, input/output capability, HDMI/DP capability, VREF control, and EAPD capability.

The `azroot_f2codecind` group describes codec root and function-level Azalia metadata:

- `AZALIA_F2_CODEC_ROOT_PARAMETER_VENDOR_AND_DEVICE_ID`, `REVISION_ID`, and `SUBORDINATE_NODE_COUNT` expose full-width root parameter values.
- `AZALIA_F2_CODEC_FUNCTION_CONTROL_POWER_STATE` exposes requested and actual power state plus `CLKSTOPOK` and settings reset.
- `AZALIA_F2_CODEC_FUNCTION_CONTROL_RESPONSE_SUBSYSTEM_ID` and byte-specific variants expose subsystem ID bytes.
- `AZALIA_F2_CODEC_FUNCTION_CONTROL_CONVERTER_SYNCHRONIZATION` and `..._RESET` expose converter synchronization and codec reset controls.
- `AZALIA_F2_CODEC_FUNCTION_PARAMETER_SUPPORTED_SIZE_RATES`, `STREAM_FORMATS`, and `POWER_STATES` expose audio rate/bit capabilities, stream format capabilities, and function power capabilities including `CLKSTOP` and `EPSS`.

The `AZF0STREAM0` through `AZF0STREAM15` groups are mechanically repeated. For each stream, the macros define:

- `AZALIA_FIFO_SIZE_CONTROL` fields for minimum FIFO size, maximum FIFO size, and maximum latency support.
- `AZALIA_LATENCY_COUNTER_CONTROL__AZALIA_LATENCY_COUNTER_RESET`.
- Full-width worst-case latency count, cumulative latency count, and cumulative request count fields.

The `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, `AZF0ENDPOINT2`, and partial `AZF0ENDPOINT3` groups describe function-0 codec converter and pin controls:

- Converter widget capabilities: audio channel capability, amplifier presence, format override, striping, processing widget, unsolicited response capability, connection list, digital/power-control/LR-swap support, delay, and widget type.
- Converter format and stream routing: number of channels, bits per sample, sample base divisor/multiple/rate, stream type, channel ID, and stream ID.
- Digital converter status/control: `DIGEN`, validity, validity configuration, pre/copy/non-audio/professional/channel-status bits, channel count, and keepalive.
- Supported formats and rates: full-width stream-format capability plus rate and bit-depth capability fields.
- Striping, ramp rate, GTC embedding, and GTC counter delta/min/max fields.
- Pin widget capabilities and pin capabilities, including digital, HDMI, DP, power, jack-detect, VREF, EAPD, and input/output support bits.
- Pin controls for unsolicited responses, pin sense, widget output enable, channel/speaker allocation, HDMI/DP connection bits, extra connection information, LFE level, level shift, and down-mix inhibit.
- Audio descriptor 0-13 fields for EDID-like short audio descriptor contents: max channels, supported frequencies, descriptor byte 2, and for descriptor 0 an extra stereo-frequency field.
- Endpoint 0-2 additional controls after the descriptor list: multichannel enable groups, lipsync/HBR response fields, sink-info words, hot-plug and unsolicited-response force controls, configuration default, multichannel mode, IEC 60958 channel-status override registers, association and digital-output status, LPIB snapshots, coding type, format-change status/ack/reason/response, wireless display identification, remote keepalive, audio-enable status, and audio enabled/disabled/format-changed interrupt status fields.

The endpoint pattern is copy-generated. Endpoint 0 spans `AZF0ENDPOINT0_AZALIA_F0_*`, endpoint 1 spans `AZF0ENDPOINT1_AZALIA_F0_*`, endpoint 2 spans `AZF0ENDPOINT2_AZALIA_F0_*`, and endpoint 3 begins the same pattern through `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR13`.

## Control Flow

This header chunk has no runtime control flow. It is preprocessor data.

Runtime control appears in consumers that follow a generated-register pattern:

1. DCN 1.0 resource code includes `dcn/dcn_1_0_offset.h` and `dcn/dcn_1_0_sh_mask.h`.
2. Resource tables bind address macros and field masks/shifts into hardware object register descriptors. In `dcn10_resource.c`, the audio table uses `AUD_COMMON_REG_LIST(id)` for four audio instances and builds `dce_audio_shift` and `dce_audio_mask` from `DCE120_AUD_COMMON_MASK_SH_LIST(...)`.
3. The generic DCE/DCN audio implementation selects an audio endpoint instance, writes endpoint index/data windows when needed, and programs converter/pin fields for the active stream.
4. Mode-set, audio setup, hotplug, DP/HDMI infoframe, and enable/disable flows read or write the resulting MMIO fields through the DC register helper layer.

Control-sensitive hardware actions represented by this chunk include codec reset and power-state changes, digital converter enable, stream/channel ID routing, audio format programming, pin output enable, HBR enablement, multichannel mute/enable/channel ID programming, channel-status override, sink audio descriptor publication, LPIB snapshot locking, format-change acknowledgement, remote keepalive, and audio interrupt mask/status handling. The macros themselves do not enforce legal sequencing, valid enum values, write-one-to-clear behavior, or endpoint ownership.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in Azalia/HD-audio hardware registers.

The represented state includes:

- Codec identity and topology state: vendor/device ID, revision ID, subordinate node counts, group type, stream formats, supported rates, bit depths, and power states.
- Function-level control state: requested/actual power state, clock-stop capability, reset, subsystem ID response bytes, and converter synchronization.
- Stream performance state: FIFO size limits, latency counter reset control, worst-case latency, cumulative latency, and cumulative request counters for stream indices 0-15.
- Converter state: sample format, stream/channel routing, digital converter enable/status bits, validity and channel-status bits, keepalive, striping, ramp rate, and GTC presentation-time embedding/counter deltas.
- Pin/endpoint state: output enable, pin sense, speaker/channel allocation, HDMI/DP connection flags, audio descriptors, sink info, HBR and lipsync responses, configuration default, multichannel controls, codec channel-status overrides, LPIB snapshots, coding type, format-change status, wireless display identification, remote keepalive, audio enable state, and audio interrupt status/mask/type fields.

Persistence depends on hardware semantics outside this generated header. Some fields are read-only capability or status values, some are latched control bits that persist until another driver/firmware write, some are counters or snapshots, some are sticky interrupt/status bits requiring acknowledgement, and some may be reset by audio disable, hotplug handling, power gating, suspend/resume, codec reset, or ASIC reset. The header does not distinguish read-only, writable, volatile, self-clearing, or write-one-to-clear fields.

## Dependencies And Integration Points

This chunk depends on the generated DCN 1.0 address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`

Direct include points for `dcn_1_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.c`

The most direct integration point for this specific chunk is the DC audio resource setup in `dcn10_resource.c`. It constructs four `dce_audio_registers` entries, one per audio instance, then fills `dce_audio_shift` and `dce_audio_mask`. The field list includes endpoint index/data window fields and the common audio mask/shift list used by the DCE audio implementation. Other DC core code assigns and releases audio objects from the resource pool, copies EDID-derived `audio_info` into streams, and calls audio object functions during stream enable/disable paths.

Related generated enum metadata appears in broader AMD include headers, such as `soc24_enum.h`, where Azalia converter format and pin/audio descriptor values are named. Those enum names are not defined in this chunk, but they document legal values for fields whose bit positions are exposed here.

## Risks And Edge Cases

The primary risk is silent audio hardware misprogramming. A wrong mask or shift can compile successfully while updating the wrong endpoint, routing audio to the wrong stream/channel, losing a status bit, or corrupting adjacent fields during read-modify-write updates.

High-risk fields include converter format and stream routing. Bad `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, sample base rate/divisor/multiple, `STREAM_ID`, or `CHANNEL_ID` constants can produce missing audio, distorted audio, wrong sample rate, incorrect channel mapping, or failures in DP/HDMI audio compliance tests.

HBR and multichannel fields are sensitive for high-bandwidth and surround audio. Incorrect `HBR_ENABLE`, `MULTICHANNEL*_ENABLE`, `MULTICHANNEL*_MUTE`, or `MULTICHANNEL*_CHANNEL_ID` masks can break compressed/HBR formats, mute only part of a multichannel stream, or route channels inconsistently.

Pin and descriptor fields affect sink-visible capability reporting. Bad audio descriptor masks, speaker/channel allocation fields, HDMI/DP connection bits, lipsync values, sink-info fields, or configuration-default fields can make the display audio codec report capabilities that disagree with EDID or link state. Symptoms include the OS selecting unsupported modes, missing formats, channel layout errors, or receiver compatibility failures.

Power, reset, keepalive, and status fields affect sequencing. Incorrect codec reset, function power-state, `CLKSTOPOK`, digital converter enable, remote keepalive, output enable, or audio enable/disable interrupt masks can cause audio not to start, not to stop cleanly, or to leave stale interrupt/status state across hotplug, DPMS, suspend/resume, or modeset.

The repeated stream and endpoint patterns create copy-generation risk. Stream blocks 0-15 are nearly identical, and endpoints 0-3 repeat long converter/pin sequences. A mismatched endpoint suffix, missing field, or copied mask from a neighboring instance might only fail for one connector/audio engine and could be missed by build tests.

The line range boundaries are artificial. This chunk starts with the `HBR` masks after the corresponding HBR shift definitions from the prior chunk, and it ends on the `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` comment before that register's fields. The final per-file merge should treat these as chunk boundaries, not source omissions.

## Test Signals

Useful validation signals are mostly compile-time plus hardware behavior:

- Kernel or module build coverage for DCN 1.0 display paths that include `dcn_1_0_sh_mask.h`.
- Generated-header consistency checks comparing every `*_MASK` and `*__SHIFT` pair in this range against AMD's register database and the matching addresses in `dcn_1_0_offset.h`.
- Static checks that every `SF(...)` field used by DCN 1.0 audio resource tables has matching mask and shift macros.
- HDMI and DisplayPort audio playback tests across all exposed audio instances, including stereo PCM, multichannel LPCM, compressed formats, and HBR-capable formats where hardware/sink support exists.
- EDID/audio capability tests verifying that short audio descriptors, speaker allocation, channel allocation, sample rates, sample sizes, lipsync, and sink-info fields match the connected sink.
- Hotplug, DPMS, modeset, and suspend/resume stress tests checking that audio endpoints are acquired/released correctly, audio enable/disable status changes are observed, and stale format-change or interrupt bits do not persist.
- LPIB and latency-counter diagnostics, when available, should show monotonic/current position behavior, correct snapshot locking, and sane worst-case/cumulative latency counts.
- Compliance or lab tests for IEC 60958 channel-status override fields, HBR audio, keepalive/silent-stream behavior, and DP/HDMI audio infoframe behavior.

Regression symptoms from bad constants include no HDMI/DP audio, audio on the wrong display, wrong channel count, bad sample rate or bit depth, muted channels, intermittent audio after hotplug or resume, HBR-only failures, incorrect sink capabilities exposed to the OS, interrupt storms or missing audio interrupts, LPIB position mismatches, and audio format-change handshakes that never clear.

## Cross-Chunk Notes

Earlier chunks of `dcn_1_0_sh_mask.h` define the preceding Azalia controller, codec, converter, and function-2 input-pin fields, including the beginning of the HBR register whose masks appear at the top of this chunk. Later chunks continue endpoint 3 from `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and then proceed through the remaining DCN 1.0 register mask namespace. The final per-file research document should treat the full header as one generated DCN 1.0 hardware register-layout contract rather than as independent algorithmic code.
