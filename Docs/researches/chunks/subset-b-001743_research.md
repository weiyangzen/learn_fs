# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 51892-53361

## Purpose

This chunk is generated AMD DCN 3.0.1 register field metadata for Azalia HD-audio input endpoints. It contains no executable C logic; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bitmasks (`_MASK`) for indirect Azalia codec input-converter and input-pin registers.

The requested range covers the tail of `AZF0INPUTENDPOINT2` and complete repeated layouts for `AZF0INPUTENDPOINT3` through `AZF0INPUTENDPOINT7`. These are per-endpoint input-side HDA codec register definitions under generated address blocks such as `azf0inputendpoint3_inputendpointind`. The chunk ends the header with `#endif`, so later content does not continue after this range. Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display/audio hardware metadata, not Ceph filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocation paths, or include directives in this range. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position for a field in a 32-bit register value.
- `<REGISTER>__<FIELD>_MASK`: field mask for extracting or updating that field.
- `//AZF0INPUTENDPOINT*_...` comments: generated register grouping markers.
- `// addressBlock: azf0inputendpoint*_inputendpointind`: generated indirect-register block markers.

The range contains 1,321 `#define` lines: 161 for the end of `AZF0INPUTENDPOINT2`, then 232 each for endpoints 3, 4, 5, 6, and 7. Endpoint 2 starts mid-register in this chunk: its `INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES__AUDIO_CHANNEL_CAPABILITIES__SHIFT` and earlier input-converter definitions are owned by the previous chunk, while this range includes the rest of that pin block and all following endpoint-2 pin-control registers.

Major register groups:

- `*_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: input converter widget capability fields such as channel capability, amplifier presence, format override, stripe, processing-widget, unsolicited-response capability, digital flag, power control, LR swap, delay, and widget type.
- `*_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`: stream format fields for channel count, bits per sample, sample-base divisor/multiple/rate, and stream type.
- `*_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: channel and stream-id assignment fields.
- `*_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital converter control/status bits such as `DIGEN`, validity/config/pre-emphasis/copy/non-audio/professional/level flags, channel-status category code, and keepalive.
- `*_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS` and `*_SUPPORTED_SIZE_RATES`: advertised stream-format, sample-rate, and bit-depth capability masks.
- `*_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `*_PARAMETER_CAPABILITIES`: input pin widget and pin capability fields, including impedance sense, trigger requirement, jack-detection capability, output/input capability, HDMI/DP indicators, VREF control, EAPD capability, and related widget flags.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`: unsolicited-response tag and enable fields.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`: impedance-sense value and presence-detect bit.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`: input-enable control.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `*_MULTICHANNEL_ENABLE2`: per-channel enable, mute, and channel-id fields for multichannel slots 0-7.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`: high-bit-rate capable/enable flags.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`: HDMI/DP channel allocation byte.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`: clock-gating disable, clock-on state, and audio-enabled fields.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE`: forced unsolicited-response payload and trigger bit.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`: HDA default-configuration fields such as sequence, association, misc, color, connection type, default device, location, and port connectivity.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB*`: link-position-in-buffer snapshot lock, wrap count, LPIB value, and timer snapshot.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL`: input activity, channel layout, and unsolicited-response enables for activity and channel-layout/channel-status infoframe changes.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`: audio infoframe channel count, channel allocation, infoframe byte 5, and valid bit.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by the AMD display/audio driver:

1. DCN301 resource and DMUB code include `dcn_3_0_1_offset.h` and this matching `dcn_3_0_1_sh_mask.h`.
2. `dcn301_resource.c` builds Azalia audio objects with `audio_regs(0..6)`, `DCE120_AUD_COMMON_MASK_SH_LIST(__SHIFT)`, and `DCE120_AUD_COMMON_MASK_SH_LIST(_MASK)`.
3. `dce_audio.c` programs Azalia endpoint registers indirectly: it writes an index into `AZALIA_F0_CODEC_ENDPOINT_INDEX` and reads/writes payload through `AZALIA_F0_CODEC_ENDPOINT_DATA`.
4. Generic audio setup code configures supported formats, rates, DTO clocks, packetization, and AFMT/stream-encoder state around those endpoint accessors.

The input-endpoint-specific symbols in this chunk are generated metadata for indirect endpoint register payload layouts. In this tree, direct display audio code primarily uses the generic endpoint index/data masks and output/audio-function fields; `rg` did not find direct references to `AZF0INPUTENDPOINT[2-7]_AZALIA_F0_CODEC_INPUT_*` outside generated register headers. That means this chunk is an ABI-style hardware description that can be used by future diagnostics, firmware-facing code, or HDA input-endpoint paths even when not actively consumed by the current DCN301 display path.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes hardware-visible fields for Azalia input endpoint state:

- Converter format state: channel count, sample size, sample-rate base/divider/multiple, stream type, stream ID, and channel ID.
- Digital converter state: enablement, channel status attributes, non-audio/professional/copy flags, category code, validity, and keepalive behavior.
- Advertised capability state: supported stream formats, sample rates, bit depths, widget capabilities, pin capabilities, HDMI/DP identity, jack-detection/presence capability, VREF and EAPD support.
- Pin-control state: input enable, multichannel enable/mute/channel mapping, HBR enable, channel allocation, hot-plug audio enablement, unsolicited-response enable/force, default configuration, LPIB snapshots, input activity, channel layout, and infoframe validity.

Persistence and side effects are hardware-defined. Configuration fields typically remain until driver reprogramming, codec reset, power transition, suspend/resume, or ASIC reset. Status-like fields such as presence detect, LPIB snapshots, activity, infoframe validity, and hot-plug/audio state can change asynchronously with hardware events. Force/clear/update-style fields may be self-clearing or side-effectful even though the header only exposes masks.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which supplies the matching `mmAZF0INPUTENDPOINT*_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX/DATA` MMIO offsets and `ixAZF0INPUTENDPOINT*_...` indirect register indexes.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`, which includes this generated header and constructs DCN301 audio register, shift, and mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`, which includes the same generated offset/mask pair for DMUB register definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` and `dce_audio.c`, which define the generic Azalia endpoint access model and audio-object interface.
- HDA/Azalia and HDMI/DP audio concepts represented elsewhere in the driver: EDID SAD parsing, audio component ELD delivery, AFMT packet programming, stream-encoder audio setup, and DTO clock programming.

The key integration contract is indirect register addressing. Endpoint-specific `ixAZF0INPUTENDPOINT*` indexes select logical HDA codec registers, while the generated `__SHIFT`/`_MASK` constants describe the fields inside the value transferred through endpoint data registers. Any consumer must pair the correct endpoint instance, indirect index, and field layout.

## Risks And Edge Cases

- Mask/shift drift is the central risk. These constants are untyped macros; a wrong mask can compile cleanly and corrupt the wrong bit in an audio endpoint register.
- The repeated endpoint layouts invite copy/paste or generator errors. Endpoints 3-7 should have identical field layouts, while endpoint 2 is split across chunk boundaries. A mismatch may affect only one audio input endpoint and escape ordinary display-output tests.
- Indirect register access requires correct endpoint selection and serialized index/data operations. Mixing endpoint index registers or racing index/data writes can read or update the wrong logical register.
- Input endpoint support may be dormant in this tree. Because the DCN301 display path does not directly reference these `INPUTENDPOINT` macros, compile coverage alone may not detect stale or incorrect generated definitions.
- HDA semantic fields have side effects. Unsolicited-response force/enable, hot-plug audio enable, HBR enable, LPIB snapshot lock, activity UR enables, and infoframe-valid fields can create interrupt noise, stale status, missed presence changes, or broken audio capture/loopback behavior if programmed incorrectly.
- Format and channel mapping fields are user-visible. Bad sample-size/rate/channel fields, channel allocation, multichannel mutes, or channel IDs can cause silent channels, swapped channels, unsupported-format advertisement, or HBR playback/capture failures.
- Capability fields influence policy decisions. Incorrect HDMI/DP, input/output capable, jack-detection, VREF, EAPD, supported-size/rate, or widget-type masks could cause the driver or firmware to expose nonexistent functionality or hide supported functionality.

## Test Signals

Useful validation is a mix of generated-header consistency and hardware/audio behavior:

- Build AMDGPU/DC with DCN301 support enabled; generated include drift should surface in resource construction, DMUB register compilation, and shared audio definitions that consume this header.
- Mechanically verify every field in this range has the expected `__SHIFT` and `_MASK` pair, and that each mask aligns with its shift and width.
- Compare endpoint 3, 4, 5, 6, and 7 field layouts for exact consistency, then compare endpoint 2 against adjacent chunks to ensure the split register is complete after merge.
- Cross-check `dcn_3_0_1_sh_mask.h` against `dcn_3_0_1_offset.h`: every `AZF0INPUTENDPOINT*_...` field group should have a matching `ixAZF0INPUTENDPOINT*_...` indirect index where the generated register database expects one.
- Diff these definitions against nearby AMD generated headers such as other `dcn_3_*_sh_mask.h` files when the Azalia input endpoint layout is expected to match.
- On hardware or emulator paths that exercise input endpoints, test converter format programming, stream/channel IDs, digital converter enable/keepalive, supported-rate reporting, HBR enablement, multichannel enable/mute/channel IDs, channel allocation, LPIB snapshot reads, and input infoframe validity.
- Exercise hotplug, suspend/resume, codec reset, runtime power transitions, and repeated unsolicited-response paths while monitoring kernel logs for HDA/Azalia errors, missed presence changes, stuck activity/status bits, or interrupt storms.
- For user-visible audio validation, check channel mapping, sample rates and bit depths, HDMI/DP HBR behavior, ELD/EDID-derived mode exposure, and audio continuity across modesets and fast updates.

## Cross-Chunk Notes

The previous chunk owns the beginning of `AZF0INPUTENDPOINT2`, including its input-converter blocks and the first field of `INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`. This chunk completes endpoint 2's pin-side definitions, contains complete endpoint 3-7 input converter and input pin layouts, and closes `dcn_3_0_1_sh_mask.h`. The final per-file research document should merge this with adjacent chunks before making complete claims about all Azalia function, output endpoint, or input endpoint definitions in the generated DCN 3.0.1 mask header.
