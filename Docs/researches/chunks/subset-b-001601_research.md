# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 49844-52212

## Scope And Purpose

This chunk is a generated AMD DCN 1.0 register field shift/mask table for Azalia/HD-audio codec endpoint registers. It contains no executable C logic. Its purpose is to provide compile-time bitfield metadata that the AMDGPU display audio code uses when it selects an Azalia endpoint index register, reads or writes endpoint data, and composes or decodes HD-audio codec response/control values.

The path is under a local `ceph-client` source mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

This range is the late output-endpoint area of `dcn_1_0_sh_mask.h`. It starts in the middle of `AZF0ENDPOINT3` and then covers complete or near-complete repeated endpoint blocks:

- Tail of `AZF0ENDPOINT3`: multichannel controls, lip-sync/HBR/sink info, hot-plug audio enable, configuration default, IEC 60958 channel-status override, LPIB snapshots, format-change and keepalive status, and audio enable/disable/format-change interrupt status.
- Complete `AZF0ENDPOINT4`, `AZF0ENDPOINT5`, and `AZF0ENDPOINT6` output endpoint indexed blocks: converter capabilities/control, pin capabilities/control, audio descriptors, multichannel routing, sink metadata, hot-plug/audio enable, IEC 60958 overrides, LPIB tracking, coding/format status, keepalive, and audio interrupt status.
- Most of `AZF0ENDPOINT7`: from converter capability/control through IEC 60958 channel-number override 7; the final endpoint 7 tail continues in the next chunk.

The chunk is highly repetitive by design. Each endpoint instance exposes the same HD-audio style register fields so display code can bind one logical audio object per hardware endpoint.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the generated preprocessor contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit endpoint-data value.
- The register names in this chunk are instance-qualified, such as `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL__AUDIO_ENABLED_MASK`.

Important macro families in this chunk:

- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: endpoint converter capability bits, including channel capability, amplifier/format override support, stripe/processing/unsolicited response capability, connection-list and digital/power-control flags, LR swap, delay, and widget type.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`: stream format fields for channel count, bits per sample, sample divisor/multiple/base rate, and PCM/non-PCM stream type.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: channel and stream IDs used to bind a codec converter to an HDA stream.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital converter enable and IEC-style status/control bits such as validity, pre-emphasis, copyright, non-audio, professional, level, category code, and keepalive.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `...SUPPORTED_SIZE_RATES`: capability bitmaps for supported stream formats, sample rates, and sample sizes.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_STRIPE_CONTROL`, `...RAMP_RATE`, `...GTC_EMBEDDING`, and `...GTC_COUNTER_DELTA*`: stripe, ramp, and global time counter synchronization/control fields.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_PARAMETER_*`: output pin widget capabilities and connector capabilities such as HDMI/DP, jack-detect, output/input capability, EAPD, VREF, and balanced I/O flags.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_CONTROL_*`: pin control fields for unsolicited response tags, pin sense, widget output enable, channel/speaker allocation, audio descriptors 0-13, multichannel enable/mute/channel IDs, lip-sync response, HBR capable/enable, sink info, hot-plug audio enable, forced unsolicited response payloads, configuration default, digital output status, LPIB snapshot/current/timer values, coding type, format-change response, wireless display identification, and remote keepalive.
- `AZF0ENDPOINTn_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`: IEC 60958 channel-status override fields for mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, sampling coefficient, MPEG surround, CGMS-A, and channel numbers for left/right plus channels 2-7.
- `AZF0ENDPOINTn_AZALIA_F0_AUDIO_ENABLE_STATUS`, `...AUDIO_ENABLED_INT_STATUS`, `...AUDIO_DISABLED_INT_STATUS`, and `...AUDIO_FORMAT_CHANGED_INT_STATUS`: endpoint audio state and interrupt flag/mask/type fields.

The unqualified `AZALIA_F0_*` field names used by common display audio code are mapped to the appropriate instance by register/field table macros. For DCN 1.0, `dcn10_resource.c` builds `audio_regs[]` with `AUD_COMMON_REG_LIST(id)` for endpoint instances 0-3 and uses `SF(AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX, AZALIA_ENDPOINT_REG_INDEX, ...)` and endpoint-data masks for the common indexed access path. Later endpoint instance macros remain part of the generated ASIC surface even when a resource table exposes fewer audio instances.

## Control Flow

This chunk has no runtime control flow. It is consumed by code that performs indexed Azalia endpoint MMIO:

1. Select the desired endpoint-local register through `AZALIA_F0_CODEC_ENDPOINT_INDEX`.
2. Read or write the endpoint payload through `AZALIA_F0_CODEC_ENDPOINT_DATA`.
3. Use the generated shift/mask macros to update individual fields in that payload.

The relevant display-core integration is in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` and `dce_audio.c`:

- `AUD_COMMON_REG_LIST(id)` maps `AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_ENDPOINT_DATA` to `AZF0ENDPOINT{id}` instances.
- `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` carry register addresses plus endpoint index/data field masks into common audio code.
- `dce_aud_az_enable()` and `dce_aud_az_disable()` read `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, toggle `CLOCK_GATING_DISABLE`, then set or clear `AUDIO_ENABLED`.
- `dce_aud_az_configure()` programs speaker/channel allocation, endpoint audio descriptors, sink/product strings, HBR state, and lip-sync/audio latency data from DRM/display audio metadata.
- `dce_aud_endpoint_valid()` reads `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT` and checks the port-connectivity field to decide whether the endpoint is usable.

Legacy DCE paths (`amdgpu/dce_v6_0.c`, `dce_v8_0.c`, and `dce_v10_0.c`) show the same HDA endpoint programming pattern using `RREG32_AUDIO_ENDPT` and `WREG32_AUDIO_ENDPT` against `ixAZALIA_F0_CODEC_PIN_CONTROL_*` indexed registers. They are not DCN 1.0 consumers of these exact instance-qualified macros, but they document the same hardware contract: configure audio descriptors, lip-sync, speaker allocation, and hot-plug audio enable via Azalia endpoint index/data registers.

Because the header is declarative, it does not enforce sequencing. Consumers must order clock-gating disable/enable, endpoint index selection, endpoint-data writes, HDA stream setup, modeset/link bring-up, and interrupt/status handling.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. The macros describe hardware endpoint MMIO state.

The represented hardware state includes:

- Converter state: stream format, channel/stream IDs, digital converter control, supported format/rate bitmaps, striping, ramp rate, GTC embedding, and GTC counter-delta tracking.
- Pin capability and control state: pin/widget capabilities, unsolicited response configuration, pin sense, output enable, speaker/channel allocation, EDID-derived audio descriptor fields, multichannel enable/mute/channel IDs, HBR capability/enable, and HDMI/DP sink metadata.
- Hot-plug/audio state: clock gating disable, clock-on status, `AUDIO_ENABLED`, forced unsolicited response payloads, configuration-default reporting, digital output active status, wireless display identification, and remote keepalive enable/capability.
- IEC 60958 channel status override state: mode/source, clock accuracy, word length, sampling-frequency fields, sampling-frequency coefficient, MPEG surround/CGMS-A fields, and per-channel number fields.
- Position and timing state: LPIB snapshot lock, cyclic buffer wrap count, current LPIB, and LPIB timer snapshot.
- Event and interrupt state: coding type, format-change reason/response, audio enable status, audio-enabled/audio-disabled/audio-format-changed flags, masks, and type fields.

Persistence is field-specific and not encoded here. Some fields are programming knobs that persist until rewritten, reset, modeset, suspend/resume, power-gating transition, or GPU reset. Other fields are status, capability, interrupt, sticky, self-clearing, or latched snapshot values. Names such as `*_STATUS`, `*_FLAG`, `*_MASK`, `*_TYPE`, `*_ENABLE`, `*_CAPABILITY`, `*_SNAPSHOT_LOCK`, `*_ACK_UR_ENABLE`, and `*_RESPONSE` hint at semantics, but this generated header does not declare access type, reset value, side effects, or write-one-to-clear behavior.

## Dependencies And Integration Points

This chunk depends on the generated DCN 1.0 ASIC register-header ecosystem:

- `dcn_1_0_d.h` for the matching register/index address constants, including endpoint index/data and indexed `ixAZALIA_F0_CODEC_*` names.
- `dcn_1_0_enum.h` and related enum/value headers for symbolic field values used with these masks.
- Display-core helper macros such as `REG_SET`, `REG_SET_FIELD`, `get_reg_field_value`, `set_reg_field_value`, `SRI`, `SF`, `AZ_REG_READ`, and `AZ_REG_WRITE`.
- Runtime register access through the AMDGPU/DC context, which turns resource-table addresses plus masks/shifts into MMIO reads/writes.

Direct integration points visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`: declares the common DCE/DCN audio register, mask, and shift tables and maps `AZF0ENDPOINT{id}` indexed registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`: implements endpoint validation, Azalia enable/disable, HBR control, lip-sync latency, speaker/channel allocation, audio descriptor programming, and DTO setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`: instantiates DCN 1.0 audio register arrays and binds the endpoint index/data masks/shifts used by `dce_audio.c`.
- Later DCN resource files use the same common audio model for newer generated endpoint headers, so consistency in this generated naming contract matters across display generations.

Functional integration surfaces are HDMI/DisplayPort audio bring-up, EDID/ELD-derived audio capability propagation, sink description/manufacturer/product metadata reporting, HDA stream/channel binding, HBR audio enabling, audio clock/DTO setup, hot-plug audio enable/disable, audio format-change handling, and HDA/DRM audio debug.

## Risks And Edge Cases

- Masks and shifts are hardware ABI. A one-bit error can compile cleanly but program the wrong HDA field, corrupt adjacent endpoint state, leave audio disabled, misreport sink capabilities, or break HDMI/DP audio.
- The range is generated and very repetitive. Manual edits to `AZF0ENDPOINT3` through `AZF0ENDPOINT7` instance families are easy to skew; regeneration from the authoritative register database is safer than hand edits.
- This chunk starts and ends at chunk boundaries, not semantic boundaries. It begins after earlier `AZF0ENDPOINT3` pin/audio-descriptor fields and ends before the final `AZF0ENDPOINT7` pin/status tail in the next chunk.
- Endpoint count is generation/resource dependent. DCN 1.0 resource code exposes endpoint instances through `audio_regs[]`; generated macros for later endpoint numbers do not imply every board or ASIC path creates that many active audio objects.
- Indexed endpoint access is sequencing-sensitive. Selecting the wrong endpoint index/data pair or racing another indexed access can read/write the wrong endpoint-local register.
- `HOT_PLUG_CONTROL` combines clock-gating and `AUDIO_ENABLED`. Consumers must follow the established sequence of temporarily disabling clock gating before changing audio enable state.
- Audio descriptors encode EDID-derived capabilities. Bad `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, or descriptor-byte fields can cause userspace/HD-audio layers to expose invalid formats or hide valid sink formats.
- IEC 60958 override fields are audio-format sensitive. Incorrect sampling frequency, word length, channel numbers, CGMS-A, or non-audio/professional bits can cause sink rejection, silence, wrong channel layout, or bad compressed-audio behavior.
- Interrupt/status fields mix flag, mask, and type naming. Misinterpreting them can lose enable/disable/format-change notifications or generate repeated unsolicited responses.
- LPIB and timer snapshot fields are likely latched/snapshot-style hardware state. Incorrect snapshot-lock handling can produce inconsistent position reporting.

## Test Signals

Useful validation is mainly build-time plus hardware/display-audio behavior:

- Build AMDGPU display-core DCN 1.0 code with this header included; generated macro drift should fail in `dcn10_resource.c`, `dce_audio.h`, or shared register-field helper users.
- Compare this chunk against adjacent chunks of `dcn_1_0_sh_mask.h`, the matching `dcn_1_0_d.h` indexed register names, and newer DCN headers to catch instance-index or field-name drift.
- Exercise HDMI and DisplayPort audio on DCN 1.0 hardware: hotplug, modeset, stream start/stop, suspend/resume, multi-monitor endpoint selection, and audio enable/disable transitions.
- Validate EDID/ELD-derived audio capabilities: stereo fallback, multichannel speaker allocation, compressed formats, HBR-capable formats, sample-rate/word-length exposure, and sink manufacturer/product/description metadata where visible.
- Test format changes while audio is active and watch for correct reprogramming of descriptor, converter format, channel-stream ID, IEC 60958 status, and audio format-change interrupt/status behavior.
- Check negative signals in kernel logs and user-visible behavior: missing HDMI/DP audio device, silent playback, wrong channel layout, invalid sample-rate exposure, HBR formats unavailable, repeated audio enable/disable interrupts, hotplug audio regressions, LPIB position anomalies, or resume leaving `AUDIO_ENABLED` cleared.
