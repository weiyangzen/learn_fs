# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 52080-54448

## Scope

This chunk is a generated AMD DCN 3.2.1 register shift/mask header slice for Azalia F0 audio endpoint indirect registers. It contains preprocessor constants only: register-group comments, `_SHIFT` macros for bit positions, and `_MASK` macros for register-positioned masks. There are no C functions, structs, enums, branches, allocations, locking paths, or software persistence mechanisms in this range.

The requested range covers 2,369 source lines, 2,049 `#define` lines, and 312 register/address-block comments. It starts inside endpoint 3 pin-control audio descriptor data, then covers the tail of `AZF0ENDPOINT3_AZALIA_F0_*`, complete repeated register layouts for `azf0endpoint4_endpointind`, `azf0endpoint5_endpointind`, and `azf0endpoint6_endpointind`, plus most of `azf0endpoint7_endpointind`. It ends inside `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4`; two masks for that register continue immediately after the chunk.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU Display Core hardware metadata. The slice is about HDMI/DisplayPort audio codec endpoint programming, not Ceph filesystem behavior.

## Purpose

The purpose of this header range is to provide named bit layouts for DCN 3.2.1 Azalia F0 endpoint codec registers. AMD display audio code pairs these masks with offsets from `dcn_3_2_1_offset.h` and with the generic DCE audio register helpers so it can program HDMI/DP audio format, channel mapping, sink metadata, HBR capability, lipsync values, hotplug audio enable state, IEC 60958 channel-status overrides, and endpoint interrupt/status fields without hard-coding raw bit positions.

The main hardware surfaces represented here are:

- Converter widget capabilities and converter controls for endpoints 4 through 7, including stream format, channel/stream ID, digital-converter channel-status bits, supported stream formats/rates, stripe control, ramp rate, and GTC embedding/counter delta fields.
- Pin widget capabilities and pin controls, including unsolicited response, pin sense, widget output enable, speaker/channel allocation, HDMI vs DP connection flags, LFE level, downmix inhibit, and extra connection info.
- Fourteen audio descriptor registers per endpoint, exposing max channels, supported frequencies, descriptor byte 2, and for descriptor 0 an extra stereo-frequency byte.
- Multichannel enable/mute/channel-ID packing for both channel pairs (`01/23/45/67`) and odd individual channels (`1/3/5/7`), plus multichannel mode.
- Sink information registers carrying manufacturer/product IDs, sink display-name length, port IDs, and up to 18 bytes of monitor description text.
- Hot-plug/audio enable control, lipsync response, HBR response, forced unsolicited response payloads, configuration default response, digital output status, LPIB snapshot/data, coding type, format-change response fields, remote keepalive, audio enable status, and endpoint audio interrupt status.
- IEC 60958 channel-status override registers for mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, sampling-frequency coefficient, MPEG surround info, CGMS-A, CGMS-A valid, and per-channel numbers.

These constants form a generated hardware ABI between the display driver and DCN 3.2.1 audio hardware. A wrong shift or mask can compile cleanly while causing HDMI/DP audio to expose incorrect EDID-derived capabilities, route channels incorrectly, leave HBR disabled, report stale sink identity, or fail to acknowledge endpoint audio events.

## Important APIs, Types, And Macros

There are no callable APIs or C data types in this chunk. Its exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the register-positioned bit mask.
- `//<REGISTER>` comments group the subsequent field definitions by endpoint-indirect register.
- `// addressBlock: azf0endpointN_endpointind` comments mark repeated endpoint register blocks.

Important macro families include:

- Endpoint converter capabilities and controls: `AZF0ENDPOINT[4-7]_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `...CONTROL_CONVERTER_FORMAT`, `...CONTROL_CHANNEL_STREAM_ID`, `...CONTROL_DIGITAL_CONVERTER`, `...PARAMETER_STREAM_FORMATS`, `...PARAMETER_SUPPORTED_SIZE_RATES`, `...STRIPE_CONTROL`, `...CONTROL_RAMP_RATE`, `...CONTROL_GTC_EMBEDDING`, and `...GTC_COUNTER_DELTA*`.
- Pin capabilities and controls: `AZF0ENDPOINT[4-7]_AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `...PIN_PARAMETER_CAPABILITIES`, `...PIN_CONTROL_UNSOLICITED_RESPONSE`, `...RESPONSE_PIN_SENSE`, `...WIDGET_CONTROL`, and `...CHANNEL_SPEAKER`.
- Audio descriptor tables: `AZF0ENDPOINT[3-7]_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`.
- Multichannel controls: `...PIN_CONTROL_MULTICHANNEL_ENABLE`, `...MULTICHANNEL_ENABLE2`, and `...MULTICHANNEL_MODE`.
- Sink metadata and hotplug/audio response controls: `...RESPONSE_LIPSYNC`, `...RESPONSE_HBR`, `...SINK_INFO0` through `SINK_INFO8`, `...HOT_PLUG_CONTROL`, `...UNSOLICITED_RESPONSE_FORCE`, and `...RESPONSE_CONFIGURATION_DEFAULT`.
- IEC 60958 channel-status overrides: `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`.
- Endpoint status/interrupt registers: `...AUDIO_ENABLE_STATUS`, `...AUDIO_ENABLED_INT_STATUS`, `...AUDIO_DISABLED_INT_STATUS`, and `...AUDIO_FORMAT_CHANGED_INT_STATUS`.

The chunk also indirectly supports generic non-endpoint-specific audio code. In `drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`, the audio object is built around `AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_ENDPOINT_DATA`; endpoint-indirect register names such as `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR` are selected through the endpoint index/data path rather than by open-coding each endpoint's concrete `AZF0ENDPOINTN_...` symbol at every call site.

## Endpoint Coverage And Register Layout

Endpoint 3 is only partially represented. The chunk begins with the last mask for `AUDIO_DESCRIPTOR11`, then includes descriptor 12 and 13, multichannel controls, lipsync/HBR responses, sink-info registers, hot-plug/audio-enable control, unsolicited-response forcing, configuration default, IEC 60958 override registers, association/status/LPIB/coding/format-change/keepalive controls, and the endpoint audio enable/disable/format-change interrupt status registers.

Endpoints 4, 5, and 6 are complete within this chunk. Each block starts at an `addressBlock` marker and repeats the same converter, pin, descriptor, multichannel, sink-info, hotplug, channel-status override, LPIB, format-change, keepalive, audio-enable status, and audio interrupt register families. This repetition is intentional: each audio endpoint has the same endpoint-indirect register shape but a distinct endpoint instance and macro prefix.

Endpoint 7 starts at line 53990 and is mostly covered through the early IEC 60958 override registers. The visible range includes converter and pin capability/control registers, all fourteen audio descriptors, multichannel controls, sink-info registers, hotplug/audio enable, unsolicited/configuration response, and override registers 0 through the first two masks of override register 4. The remaining masks for `CGMS_A` and `CGMS_A_VALID` are in the next chunk.

## Runtime Control Flow

This header has no executable control flow. Runtime flow is supplied by AMDGPU display audio code:

1. DCN 3.2.1 resource construction wires audio register offsets and field masks into `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask`. In this tree, `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c` defines `audio_regs[5]` and binds common Azalia endpoint index/data fields via `DCE120_AUD_COMMON_MASK_SH_LIST`.
2. `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` selects an endpoint instance and uses `AZ_REG_READ`, `AZ_REG_WRITE`, `set_reg_field_value`, and `get_reg_field_value` around the generic endpoint-indirect register names.
3. The helper layer writes the endpoint index register, reads or writes endpoint data, and uses this generated shift/mask data to pack or extract individual fields.
4. Hardware then latches converter/pin/audio metadata, reports audio enable/disable/format-change state, and exposes endpoint status to the display interrupt and audio paths.

Representative consumers visible in `dce_audio.c` include:

- `set_high_bit_rate_capable()` reads and writes `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR` using `HBR_CAPABLE`.
- `set_video_latency()` and `set_audio_latency()` update `VIDEO_LIPSYNC` and `AUDIO_LIPSYNC`.
- `dce_aud_az_enable()` and `dce_aud_az_disable()` toggle `CLOCK_GATING_DISABLE` and `AUDIO_ENABLED` in `HOT_PLUG_CONTROL`.
- `dce_aud_az_configure()` programs `CHANNEL_SPEAKER`, `AUDIO_DESCRIPTOR0 + format_index`, `SINK_INFO0` through `SINK_INFO8`, HBR capability, and lipsync fields from the detected HDMI/DP audio information.

The IRQ source IDs for endpoint audio enabled, disabled, and format-changed events are declared in `drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`; the status/mask/type register fields in this chunk are the endpoint-local hardware status surface that corresponds to those classes of events.

## State And Persistence Behavior

The macros themselves store no software state. They describe MMIO-backed endpoint-indirect hardware registers whose lifetime is governed by GPU reset, display core initialization, endpoint selection, hotplug handling, modeset/audio configuration, suspend/resume, runtime power management, and HDMI/DP audio driver interactions.

Persistent or latched hardware configuration fields in this range include converter stream format, channel/stream ID, digital converter channel-status bits, stripe control, ramp-rate mode, GTC embedding parameters, pin widget output enable, speaker allocation, HDMI/DP connection flags, audio descriptors, multichannel enable/mute/channel IDs, sink manufacturer/product/port/display-name metadata, HBR capability/enable, lipsync values, configuration default response, IEC 60958 channel-status override values, remote keepalive, and hotplug audio-enable state.

Volatile or event/status-oriented fields include pin sense, digital output active, LPIB and LPIB timer snapshots, cyclic-buffer wrap count, format-changed status/reason/response, wireless display identification, audio enable status, and audio enabled/disabled/format-changed interrupt flag/mask/type fields.

Several fields are sequencing-sensitive. `HOT_PLUG_CONTROL` includes `CLOCK_GATING_DISABLE`, `CLOCK_ON_STATE`, and `AUDIO_ENABLED`; `dce_audio.c` explicitly disables clock gating before changing audio enable state and then re-enables gating. `LPIB_SNAPSHOT_LOCK` is a lock/snapshot control, not ordinary metadata. The interrupt status registers have flag/mask/type triplets, so acknowledgement and masking policy must preserve the intended flag semantics. The forced unsolicited-response register has a payload plus force bit, so stale payload data can be emitted if the force bit is misused.

## Dependencies And Integration Points

The direct generated-header pair for this chunk is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`

The offsets identify endpoint index/data and endpoint-indirect register addresses; this chunk provides the field packing metadata. These files must be generated from the same DCN 3.2.1 register database.

Important local integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`: declares the common audio register, shift, and mask structures and the `AUD_COMMON_*` register-list macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`: programs HBR, lipsync, hotplug audio enable, channel/speaker allocation, ACP data, audio descriptor tables, sink info, and audio clock DTO state.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`: constructs DCN 3.2.1 audio register arrays and binds the common Azalia endpoint index/data masks into audio objects.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`: declares endpoint audio enabled, disabled, and format-changed interrupt source/context IDs.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h`: contains related Azalia enum values for converter format fields, digital converter bits, audio descriptor format codes, and multichannel mute semantics on newer/generated register descriptions.

Practical runtime integration points are HDMI audio, DP audio, DP MST audio endpoints, EDID/audio-info propagation, sink display-name and port-ID reporting, HBR exposure for high-bit-rate compressed formats, lipsync reporting, hotplug audio enable/disable sequencing, endpoint interrupt handling, and audio debug/register-dump decoding.

## Risks And Edge Cases

- The chunk starts and ends inside register definitions. Endpoint 3 `AUDIO_DESCRIPTOR11` is partial at the beginning, and endpoint 7 `CODEC_CS_OVERRIDE_4` is partial at the end. Adjacent chunks are required for complete per-register coverage at the boundaries.
- The endpoint blocks are highly repetitive. Copying a symbol with the wrong `AZF0ENDPOINTN` prefix can target the wrong audio endpoint while keeping the field layout valid enough to compile.
- Endpoint count must match resource construction. This chunk exposes endpoints 3 through 7, while `dcn321_resource.c` declares five audio objects; instance-to-endpoint mapping must remain consistent with the offset header and hardware topology.
- Audio descriptors are programmed by index arithmetic in `dce_audio.c` (`AUDIO_DESCRIPTOR0 + format_index`). The descriptor registers must remain contiguous and consistently shaped for that code to be correct.
- `AUDIO_DESCRIPTOR0` has the extra `SUPPORTED_FREQUENCIES_STEREO` field, while descriptors 1 through 13 do not. Generic descriptor-writing code must only use that field for descriptor 0.
- `CHANNEL_SPEAKER` contains both HDMI and DP connection bits. Incorrect setting can advertise the wrong transport to the audio driver or sink.
- `HOT_PLUG_CONTROL` is power/clock sensitive. Updating `AUDIO_ENABLED` without the expected clock-gating sequence can race hardware state or fail to latch the change.
- `RESPONSE_HBR` separates capability and enable bits. Advertising unsupported HBR or failing to set capability when bandwidth allows can break high-bit-rate audio formats.
- Sink info registers pack bytes of display name and port IDs. Off-by-one string length, nonzero stale bytes, or wrong byte order can expose incorrect monitor identity through the audio codec interface.
- IEC 60958 override fields are standards-visible channel-status metadata. Bad sampling-frequency, word-length, clock-accuracy, CGMS-A, or channel-number values can create audio-driver or receiver interoperability problems.
- Interrupt status registers expose flag/mask/type fields with repeated names such as `AUDIO_ENABLED_MASK_MASK`. Automated name processing must preserve the generated spelling.
- This header does not encode reset values, access permissions, write-one-to-clear behavior, volatile semantics, value enumerations, required delays, or endpoint selection rules. Callers must rely on the hardware specification and existing helper code for those semantics.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for DCN 3.2.1 display audio consumers, especially `dcn321_resource.c` and `dce_audio.c`, so missing or renamed masks fail at compile time.
- Generated-header consistency checks that each visible field has a matching shift and mask, masks do not overlap within a register unless documented, and endpoint 4/5/6 repeated layouts remain identical except for the endpoint prefix.
- Static validation that `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` remain contiguous in the matching offset header, because runtime descriptor programming uses indexed writes.
- HDMI and DP audio smoke tests across hotplug, modeset, suspend/resume, and audio enable/disable transitions.
- EDID/audio-info propagation tests that verify speaker allocation, audio descriptor formats, supported sample rates, HBR capability, lipsync values, sink manufacturer/product IDs, port IDs, and display-name bytes are visible through the audio codec interface.
- DP MST tests with multiple active audio endpoints, to catch wrong endpoint-prefix or instance mapping mistakes.
- Interrupt tests or trace validation for endpoint audio enabled, disabled, and format-changed events, including flag/mask/type handling.
- Register dump comparison against the DCN 3.2.1 hardware register database for endpoint 3 through endpoint 7 Azalia blocks.

## Summary

This chunk is a dense generated bitfield map for DCN 3.2.1 Azalia F0 HDMI/DP audio endpoint registers. Its practical value is naming the fields that AMD display audio code uses to expose sink capabilities, program audio format and channel metadata, toggle endpoint audio, report lipsync/HBR state, manage sink identity strings, and observe endpoint audio events. The main engineering risks are stale generated data, wrong endpoint instance selection, descriptor-table assumptions, standards-visible IEC 60958 metadata mistakes, and power/event sequencing bugs around hotplug audio enable and interrupt status.
