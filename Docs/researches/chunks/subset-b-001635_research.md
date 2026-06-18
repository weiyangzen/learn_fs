# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 62233-64601

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata for Azalia/HD-audio output endpoint registers. It contains only C preprocessor constants; there are no functions, structs, enums, variables, or executable control paths. Its purpose is to publish compile-time `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants used by AMDGPU display audio code when it composes or decodes 32-bit payloads accessed through Azalia endpoint index/data registers.

The path is under a local `ceph-client` source mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior, distributed filesystem state, or storage persistence.

The assigned range covers 2,048 `#define` lines across repeated output endpoint blocks:

- Tail of `AZF0ENDPOINT1`, beginning at `AZALIA_F0_CODEC_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES` and continuing through audio enable, audio enabled/disabled, and audio format-changed interrupt status.
- Complete `AZF0ENDPOINT2`, `AZF0ENDPOINT3`, and `AZF0ENDPOINT4` output endpoint field layouts.
- Beginning of `AZF0ENDPOINT5`, from converter audio-widget capability through the first mask of `AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR11`.

The chunk is repetitive by design. Each endpoint instance exposes the same HD-audio style converter and pin-widget fields so display code can bind logical display-audio objects to per-link hardware endpoints. The chunk boundaries are artificial: earlier lines contain the start of endpoint 1, and later lines complete endpoint 5.

## Important APIs, Types, And Macros

The macro namespace is the API surface:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned 32-bit field mask.
- Register names are endpoint-qualified, for example `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL__AUDIO_ENABLED_MASK`.

Important register/field families in this chunk:

- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: converter widget capability bits such as channel count capability, input/output amplifier presence, format override, stripe, processing widget, unsolicited response support, connection-list support, digital/power-control flags, LR swap, delay, and widget type. This family is complete for endpoints 2-5 and starts before the chunk for endpoint 1.
- `...CONVERTER_CONTROL_CONVERTER_FORMAT`: HDA stream format fields for number of channels, bits per sample, sample base divisor/multiple/rate, and stream type.
- `...CONVERTER_CONTROL_CHANNEL_STREAM_ID`: channel ID and stream ID fields used to bind the endpoint converter to an HDA stream.
- `...CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital converter enable and IEC-style status/control bits including validity, validity configuration, pre-emphasis, copyright, non-audio, professional, level, category code, and keepalive.
- `...CONVERTER_PARAMETER_STREAM_FORMATS` and `...CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`: capability bitmaps for supported stream formats, sample rates, and bit depths. Endpoint 1 coverage begins at supported size/rates.
- `...CONVERTER_STRIPE_CONTROL`, `...CONTROL_RAMP_RATE`, `...CONTROL_GTC_EMBEDDING`, and `...GTC_COUNTER_DELTA*`: stripe capability/control, ramp rate, presentation-time/GTC embedding, clear-min/max-delta, group selection, and GTC counter delta/min/max fields.
- `...CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `...CODEC_PIN_PARAMETER_CAPABILITIES`: output pin widget and connector capability fields including jack detection, output/input capability, balanced I/O, HDMI, DP, VREF, and EAPD capability.
- `...CODEC_PIN_CONTROL_UNSOLICITED_RESPONSE`, `...RESPONSE_PIN_SENSE`, and `...WIDGET_CONTROL`: unsolicited response tag/enable, impedance-sense response, and output-enable control.
- `...CODEC_PIN_CONTROL_CHANNEL_SPEAKER`: speaker allocation, channel allocation, HDMI/DP connection flags, extra connection info, LFE playback level, level shift, and downmix inhibit.
- `...CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `...AUDIO_DESCRIPTOR13`: EDID/SAD-derived audio descriptor fields. Descriptor 0 has stereo frequency support in the high byte; descriptors 1-13 carry max channels, supported frequencies, and descriptor byte 2. Endpoint 5 is cut off at descriptor 11.
- `...CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and `...MULTICHANNEL_ENABLE2`: enable/mute/channel ID fields for channel pairs 01, 23, 45, 67 and additional multichannel extension fields.
- `...CODEC_PIN_CONTROL_RESPONSE_LIPSYNC` and `...RESPONSE_HBR`: video/audio lip-sync latency bytes and high-bit-rate audio capable/enable fields.
- `...CODEC_PIN_CONTROL_SINK_INFO0` through `...SINK_INFO8`: manufacturer ID, product ID, sink description length, two port-ID words, and packed sink description bytes.
- `...CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`: `CLOCK_GATING_DISABLE`, `CLOCK_ON_STATE`, and `AUDIO_ENABLED`. This field set is directly used by the common display audio enable/disable path.
- `...CODEC_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE` and `...RESPONSE_CONFIGURATION_DEFAULT`: forced unsolicited response payloads, port connectivity, location, default device, connection type, color, miscellaneous, default association, and sequence.
- `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`: IEC 60958 channel-status override fields for mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, sampling-frequency coefficient, MPEG surround, CGMS-A, and channel numbers for left/right plus channels 2-7.
- `...CODEC_PIN_ASSOCIATION_INFO`, `...DIGITAL_OUTPUT_STATUS`, `...LPIB_SNAPSHOT_CONTROL`, `...LPIB`, `...LPIB_TIMER_SNAPSHOT`, `...CODING_TYPE`, `...FORMAT_CHANGED`, `...WIRELESS_DISPLAY_IDENTIFICATION`, and `...REMOTE_KEEPALIVE`: association, output-active status, position/timer snapshots, coding type, format-change acknowledgement/reason/response, wireless-display ID, and remote keepalive fields.
- `AZF0ENDPOINTn_AZALIA_F0_AUDIO_ENABLE_STATUS`, `...AUDIO_ENABLED_INT_STATUS`, `...AUDIO_DISABLED_INT_STATUS`, and `...AUDIO_FORMAT_CHANGED_INT_STATUS`: endpoint enable state plus flag/mask/type fields for enable, disable, and format-change interrupts.

## Control Flow

This header chunk has no runtime control flow. It is preprocessor data consumed by DCN 2.0 display code through generated register descriptor tables and shared register helpers.

The runtime pattern for these fields is indexed Azalia endpoint access:

1. Select an endpoint-local indexed register through `AZALIA_F0_CODEC_ENDPOINT_INDEX`.
2. Read or write the endpoint-local 32-bit payload through `AZALIA_F0_CODEC_ENDPOINT_DATA`.
3. Use this header's shifts and masks to update or decode individual fields in that payload.

Local integration points show this pattern clearly. `display/dc/dce/dce_audio.h` defines `AUD_COMMON_REG_LIST(id)` with `SRI(AZALIA_F0_CODEC_ENDPOINT_INDEX, AZF0ENDPOINT, id)` and `SRI(AZALIA_F0_CODEC_ENDPOINT_DATA, AZF0ENDPOINT, id)`. `display/dc/resource/dcn20/dcn20_resource.c` instantiates `audio_regs[]` for endpoint instances 0 through 6 and builds common `dce_audio_shift`/`dce_audio_mask` structures using endpoint-data fields from this mask header. `display/dc/dce/dce_audio.c` then uses helpers such as `AZ_REG_READ`, `AZ_REG_WRITE`, and `set_reg_field_value` to validate endpoints, enable/disable Azalia audio, program EDID-derived audio descriptors, set speaker/channel allocation, configure HBR, fill sink metadata, and manage format-change and hotplug-related state.

Because this header is declarative, it does not enforce sequencing. Callers must order endpoint index selection, endpoint-data read-modify-write, clock-gating disable/restore, `AUDIO_ENABLED` updates, stream/channel binding, link/modeset bring-up, and interrupt/status handling.

## State And Persistence Behavior

The header itself stores no software state and has no persistence mechanism. It describes state held in DCN 2.0 display audio hardware.

The represented hardware state includes:

- Converter state: stream format, stream/channel IDs, digital converter control, supported format/rate/bit-depth capabilities, striping, ramp rate, GTC embedding, and GTC counter delta/min/max tracking.
- Pin capability and control state: widget and connector capabilities, unsolicited response configuration, pin sense, output enable, speaker/channel allocation, audio descriptors, multichannel channel-pair controls, lip-sync latency, HBR capability/enable, and HDMI/DP sink metadata.
- Hotplug/audio enable state: clock gating disable, clock-on state, `AUDIO_ENABLED`, forced unsolicited response data, configuration-default reporting, digital output active status, wireless display identification, and remote keepalive.
- IEC 60958 channel-status override state: sampling frequency, original sampling frequency, word length, clock accuracy, source and channel numbers, CGMS-A, MPEG surround, and override-enable bits.
- Position/timing state: LPIB snapshot lock, cyclic buffer wrap count, current LPIB, and LPIB timer snapshot.
- Event state: coding type, format-change flag/ack/reason/response, audio enable status, and audio-enabled/audio-disabled/audio-format-changed interrupt flag/mask/type bits.

Persistence is hardware-defined and not encoded in this generated file. Some fields are stable programming knobs until rewritten, modeset, reset, suspend/resume, power-gating transition, or GPU reset. Other fields are read-only capabilities/status, latched snapshots, sticky interrupt flags, self-clearing control bits, or write-sensitive acknowledgement fields. Names such as `*_STATUS`, `*_FLAG`, `*_MASK`, `*_TYPE`, `*_ENABLE`, `*_CAPABILITY`, `*_SNAPSHOT_LOCK`, `*_ACK_UR_ENABLE`, and `*_RESPONSE` indicate likely semantics, but access type, reset value, and side effects require the hardware register specification and surrounding driver usage.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 ASIC register header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` supplies the matching endpoint index/data register addresses and indexed endpoint register IDs.
- This file supplies only field layouts for packed endpoint payloads.
- AMD display register helpers (`SRI`, `SF`, `AZ_REG_READ`, `AZ_REG_WRITE`, `set_reg_field_value`, `get_reg_field_value`, and related macros) combine offset and mask/shift metadata into MMIO operations.
- Shared display-audio types in `display/include/audio_types.h`, `display/dc/dc_types.h`, and EDID/ELD handling feed the descriptor, speaker-allocation, latency, and HBR fields represented here.

Direct integration points visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`: includes the DCN 2.0 offset and mask headers, creates `audio_regs[]` for endpoint instances, and passes `audio_shift`/`audio_mask` into `dce_audio_create()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`: declares the common audio register, shift, and mask structures and maps endpoint index/data registers by instance.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`: programs the hardware endpoint fields represented here during audio validation, enable/disable, descriptor setup, channel allocation, HBR setup, sink-info programming, DTO setup, and format-change handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_helpers.c` and DRM EDID paths: populate display audio capability data that is later reflected into the endpoint audio descriptor and speaker/channel fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c`: exposes HDMI/DP audio ELD integration to the DRM audio component, which depends on the display audio endpoint programming being correct.

Functional integration surfaces are HDMI/DisplayPort audio bring-up, EDID/ELD-derived capability propagation, sink manufacturer/product/description reporting, HDA stream binding, multichannel speaker allocation, HBR audio, audio position reporting, audio format-change notification, hotplug audio enable/disable, and display-audio debug.

## Risks And Edge Cases

- Masks and shifts are hardware ABI. A one-bit error can compile successfully while programming the wrong HDA field, corrupting adjacent endpoint state, leaving audio disabled, misreporting sink capabilities, or breaking HDMI/DP audio.
- The range is generated and highly repetitive. Endpoint 2, 3, and 4 should be structurally identical, endpoint 1 is only a tail in this chunk, and endpoint 5 is only a prefix. Manual edits can easily introduce instance skew.
- The chunk boundaries are not semantic. Final per-file reconciliation must merge the preceding endpoint 1 converter prefix and the following endpoint 5 descriptor/status tail before drawing whole-file conclusions.
- DCN20 resource code exposes a finite set of audio endpoint instances through `audio_regs[]`; the presence of generated macros does not by itself prove every endpoint is active on every ASIC, board, link, or display topology.
- Indexed endpoint access is sequencing-sensitive. Selecting the wrong endpoint index/data pair, sharing the indexed window incorrectly, or racing another indexed access can read or write the wrong endpoint-local register.
- `HOT_PLUG_CONTROL` mixes clock-gating and audio-enable fields. Existing code disables clock gating around `AUDIO_ENABLED` changes; bypassing that pattern risks writes being dropped or audio state becoming inconsistent.
- Audio descriptors and speaker/channel allocation are EDID-derived. Bad masks for `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, descriptor byte 2, speaker allocation, or channel allocation can expose invalid formats, hide valid formats, produce silence, or create wrong channel layouts.
- IEC 60958 override fields are format-sensitive. Incorrect sample frequency, original sample frequency, word length, channel number, CGMS-A, professional/non-audio, or validity settings can cause sink rejection, compressed-audio failures, or incorrect receiver metadata.
- Interrupt/status fields mix flag, mask, and type terminology. Misinterpreting them can lose audio enable/disable/format-change notifications, cause repeated unsolicited responses, or hide format-change events.
- LPIB and timer snapshot fields are likely latch-style state. Incorrect snapshot-lock handling can produce inconsistent audio position reporting.

## Test Signals

Useful validation is mainly build-time plus hardware display-audio behavior:

- Build AMDGPU/DC with DCN 2.0 support. Macro drift should fail in `dcn20_resource.c`, `dce_audio.h`, or shared audio helper code that consumes the generated shift/mask names.
- Cross-check the generated `*_SHIFT` and `*_MASK` pairs against the matching endpoint indexed register names in `dcn_2_0_0_offset.h` and against adjacent DCN/DCE generated headers where the Azalia endpoint layout is expected to be compatible.
- Exercise HDMI and DisplayPort audio on DCN 2.0 hardware across hotplug, modeset, stream start/stop, suspend/resume, multi-monitor endpoint selection, and audio enable/disable transitions.
- Validate EDID/ELD-derived audio capabilities: stereo fallback, multichannel layouts, compressed formats, HBR-capable formats, sample-rate and word-length exposure, speaker allocation, and sink manufacturer/product/description metadata.
- Test active format changes and verify descriptor, converter format, channel/stream ID, IEC 60958 status, HBR, and audio format-changed status/interrupt behavior update coherently.
- Check LPIB/position behavior during playback, especially around snapshot locking, cyclic buffer wrap count, resume, and stream restarts.
- Watch negative signals in kernel logs and user-visible behavior: missing HDMI/DP audio devices, silent playback, wrong channel layout, invalid sample-rate exposure, HBR formats unavailable, hotplug audio regressions, repeated audio enable/disable interrupts, audio format-change storms, LPIB position anomalies, or resume leaving `AUDIO_ENABLED` cleared.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_0_sh_mask.h` contain the beginning of the Azalia endpoint region, including endpoint 0 and the start of endpoint 1 converter fields. Later chunks complete endpoint 5 and continue with later endpoint/input-endpoint definitions. The final per-file research document should treat this header as a generated DCN 2.0 hardware field-layout contract rather than algorithmic driver code, and should preserve the distinction between endpoint index/data addresses from the offset header and packed field definitions from this mask header.
