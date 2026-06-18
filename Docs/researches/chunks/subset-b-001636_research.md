# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 64602-66921

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains no executable C logic; its interface is a large set of `#define` constants that map Azalia/HD-audio codec endpoint register fields to bit shifts and masks.

The path sits inside a local `ceph-client` source mirror, but the content belongs to the Linux AMDGPU display stack. In this line range it describes HDMI/DisplayPort audio codec endpoint state, not Ceph filesystem behavior.

The range starts in the middle of output endpoint 5 audio descriptor coverage, then covers the tail of output endpoint 5, all of output endpoints 6 and 7, and the beginning of input endpoints 0 through 3. The chunk ends inside `AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE2`, so full endpoint 3 input-pin coverage continues in the next chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this chunk. The public API is the generated preprocessor naming scheme:

- `<register>__<field>__SHIFT` gives the bit position for a field.
- `<register>__<field>_MASK` gives the field mask used by `REG_SET_FIELD`, `REG_GET_FIELD`, `AZ_REG_READ`, `AZ_REG_WRITE`, and related AMD display register helpers.
- Prefixes such as `AZF0ENDPOINT6_...` and `AZF0INPUTENDPOINT1_...` distinguish repeated Azalia codec endpoint instances that otherwise expose nearly identical field layouts.

Important macro families in this range:

- `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_*`: tail of an output pin endpoint, including audio descriptors 12 and 13, multi-channel channel-pair enable/mute/channel-id fields, lipsync, high-bit-rate audio capability/enable, sink manufacturer/product/port/description fields, hotplug/audio enable, forced unsolicited response payload, default pin configuration, IEC 60958 channel-status override bytes 0 through 8, association info, digital output activity, LPIB snapshot/timer fields, coding type, format-change state, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status fields.
- `AZF0ENDPOINT6_AZALIA_F0_CODEC_CONVERTER_*`: complete output converter fields for endpoint 6, including widget capabilities, converter format, stream/channel identifiers, digital converter bits (`DIGEN`, validity, pre-emphasis, copy, non-audio, professional, level, category code, keepalive), supported stream/size/rate capabilities, stripe control, ramp rate, global-time-counter embedding, and GTC delta/min/max measurements.
- `AZF0ENDPOINT6_AZALIA_F0_CODEC_PIN_*`: complete output pin fields for endpoint 6, mirroring output endpoint 5 pin functionality: pin widget and pin capabilities, unsolicited response control, pin sense, output widget control, channel/speaker allocation, audio descriptors 0 through 13, multi-channel enable banks, lipsync, HBR, sink info, hotplug, forced unsolicited responses, default configuration, IEC 60958 channel status override, LPIB, coding/format-change, keepalive, and audio interrupt status.
- `AZF0ENDPOINT7_AZALIA_F0_CODEC_CONVERTER_*` and `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_*`: complete output endpoint 7 converter and pin field masks/shifts with the same structure as endpoint 6.
- `AZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_CONVERTER_*`: first input endpoint converter capabilities and controls, including audio widget capabilities, converter format, channel/stream IDs, digital converter status bits, supported formats, and supported sample sizes/rates.
- `AZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_PIN_*`: first input endpoint pin fields: input pin widget and pin capabilities, unsolicited response, input pin sense, input-enable widget control, multi-channel enable banks for channels 0-7, HBR response, channel allocation, hotplug/audio enable, forced unsolicited response payload, default configuration, LPIB snapshot/timer, input activity/status control, and audio infoframe fields.
- `AZF0INPUTENDPOINT1_*`, `AZF0INPUTENDPOINT2_*`, and the visible start of `AZF0INPUTENDPOINT3_*`: repeated input converter and pin field masks for additional input endpoints. Endpoint 3 reaches converter format, stream ID, digital converter, stream/rate capabilities, input pin capabilities, unsolicited response, input pin sense, widget input enable, multi-channel enable, and the start of multi-channel enable2 in this chunk.

## Control Flow

This header has no runtime control flow. It is declarative hardware metadata. Runtime behavior emerges when display/audio code combines these masks with the matching offset/index headers and register access helpers.

Representative flows in local consumers:

- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` writes Azalia endpoint index/data registers, then uses field masks from this header to program HBR enablement, lipsync values, hotplug/audio enable, channel speaker allocation, audio descriptors from EDID SAD data, and sink identity/description fields.
- Older DCE paths such as `drivers/gpu/drm/amd/amdgpu/dce_v8_0.c` and `drivers/gpu/drm/amd/amdgpu/dce_v10_0.c` use the same indexed endpoint model with `RREG32_AUDIO_ENDPT` and `WREG32_AUDIO_ENDPT`, plus `REG_SET_FIELD`, to configure audio pin defaults, lipsync, speaker allocation, audio descriptors, and hotplug/audio-enable state.
- DCN20 integration files (`display/dc/resource/dcn20/dcn20_resource.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`, `display/dmub/src/dmub_dcn20.c`, and `amdgpu/gmc_v10_0.c`) include `dcn_2_0_0_sh_mask.h` with the matching offset header so generated register tables and service code can compile against the DCN20 register contract.

Because this file only provides constants, it does not enforce endpoint sequencing. Consumers must select the right endpoint index/data window, program fields in the order required by the Azalia codec interface, and preserve reserved bits when updating packed registers.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The masks describe fields in MMIO-backed or indexed hardware registers whose values are owned by the DCN/Azalia hardware.

The represented state includes:

- Output endpoint audio capabilities and current programming: converter format, stream/channel IDs, supported formats/rates, digital converter channel status, HBR capability and enablement, multi-channel mute/enable/channel ID maps, speaker/channel allocation, audio coding descriptors, and IEC 60958 channel-status override fields.
- Output pin and sink metadata: manufacturer/product ID, port ID, sink description bytes, default pin configuration, DP/HDMI pin capabilities, hotplug/audio-enable state, pin sense, unsolicited-response configuration, and remote keepalive.
- Timing and synchronization aids: lipsync fields, GTC embedding enable/group, presentation time offset change, GTC delta/min/max fields, and LPIB/timer snapshot fields.
- Interrupt and event status: audio enabled/disabled/format-changed flags, masks, and types; input activity and channel-layout status; unsolicited response tags/enables; forced unsolicited response payloads.
- Input endpoint state: input converter format/stream/digital controls, input pin presence/impedance sensing, input widget enable, HBR/channel allocation, input activity state, and infoframe channel-count/allocation/valid bits.

Hardware persistence is not encoded here. Some fields are durable configuration until a modeset, audio stream reconfiguration, power transition, or codec reset. Other fields are status, interrupt, latch, snapshot, or force/ack controls with side effects. Names such as `*_INT_STATUS`, `*_FORMAT_CHANGED`, `*_LPIB_SNAPSHOT_LOCK`, `*_UNSOLICITED_RESPONSE_FORCE`, `*_CLEAR_GTC_COUNTER_MIN_MAX_DELTA`, and `*_PRESENCE_DETECT` signal behavior that must be confirmed against the hardware specification and surrounding driver logic before changing access patterns.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract:

- `dcn_2_0_0_offset.h` supplies the MMIO offsets and indexed-register addresses.
- `dcn_2_0_0_sh_mask.h` supplies these field masks and shifts.
- AMD display register helpers consume the macros through `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_UPDATE`, `REG_READ`, `REG_WRITE`, `AZ_REG_READ`, `AZ_REG_WRITE`, and endpoint-specific indexed access wrappers.

Integration points include:

- DC display audio programming in `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`.
- Legacy AMDGPU display/audio programming in `drivers/gpu/drm/amd/amdgpu/dce_v8_0.c` and `drivers/gpu/drm/amd/amdgpu/dce_v10_0.c`.
- DCN20 register-table and service construction in `display/dc/resource/dcn20`, `display/dc/irq/dcn20`, `display/dc/gpio/dcn20`, `display/dc/clk_mgr/dcn20`, and `display/dmub/src`.
- Higher-level DRM/Display Core flows that derive audio state from connector EDID, ELD/SAD audio descriptors, link type, stream timing, hotplug state, suspend/resume, and modeset/audio-enable transitions.

## Risks And Edge Cases

- The macros are a hardware ABI. Incorrect mask or shift values can compile cleanly while programming the wrong bitfield, causing silent HDMI/DP audio failures, bad channel maps, invalid sample-rate/bit-depth advertisement, lost HBR audio, or broken sink detection.
- Endpoint families are highly repetitive. Manual edits can easily drift one instance (`ENDPOINT6` versus `ENDPOINT7`, or `INPUTENDPOINT1` versus `INPUTENDPOINT2`) while leaving adjacent instances correct, producing connector- or stream-count-specific failures.
- The chunk boundary is not semantic. It starts after earlier endpoint 5 descriptor fields and ends mid-way through input endpoint 3 multi-channel enable2, so whole-file analysis must merge adjacent chunks before drawing complete endpoint coverage conclusions.
- Packed bitfields require read-modify-write discipline. Fields such as channel status override, default configuration, multi-channel enable/mute/channel IDs, interrupt mask/type/flag bits, and input status controls share registers; writing a full literal without preserving unrelated bits can corrupt neighboring state.
- Interrupt and event fields can have side effects. Audio enabled/disabled/format-change status, unsolicited response force, snapshot lock, and GTC min/max clear fields may be sticky, self-clearing, write-one-to-clear, or latch-triggering depending on hardware semantics outside this generated header.
- Output and input endpoint naming is similar but not interchangeable. Using output pin masks on input endpoint registers, or vice versa, can produce plausible-looking code that targets the wrong indexed register layout.
- Sink information fields pack EDID-derived identity and descriptions into byte lanes. Bad masks or lengths can expose wrong ELD/sink metadata to userspace or audio clients.
- HBR, IEC 60958, channel allocation, and audio descriptor fields affect standards-visible audio behavior. Regressions may appear only with specific receivers, formats, channel counts, compressed streams, or DisplayPort/HDMI link modes.

## Test Signals

Useful validation is mostly compile-time plus hardware behavior:

- Build AMDGPU/DC with DCN20 support; missing or renamed macros should fail in DCN20 resource/service code and audio paths that include the generated headers.
- Diff this generated mask chunk against adjacent ASIC families or regenerated headers to catch unintended endpoint-instance drift, especially for repeated endpoint 6/7 and input endpoint 0-3 families.
- Exercise HDMI and DisplayPort audio on DCN20 hardware across multiple connectors and streams: enable/disable audio, hotplug displays, modeset with audio active, suspend/resume, and switch between HDMI and DP sinks.
- Validate EDID/SAD-derived programming by checking supported audio formats, sample rates, bit depths, speaker allocation, channel count, and sink identity as observed by ALSA/ELD userspace.
- Test HBR and compressed/high-channel-count formats where available, plus basic PCM stereo and multi-channel PCM.
- Watch for kernel log errors, missing audio devices, wrong ELD contents, EDID/audio descriptor parsing anomalies, hotplug flapping, lost audio after modeset, stale audio after unplug, format-change interrupt storms, and failures limited to high endpoint counts.
- For input endpoint coverage, validate input activity/status, infoframe validity, channel allocation, and multichannel mapping on hardware or test paths that expose Azalia input endpoints.
