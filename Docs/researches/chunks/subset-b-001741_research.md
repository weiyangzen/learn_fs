# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 47181-49549

## Scope

This chunk is a generated AMD DCN 3.0.1 register shift/mask header slice for Azalia HD-audio endpoint indirect registers. It contains preprocessor constants only; there are no functions, structs, enums, variables, allocation paths, locks, or executable branches.

The requested range starts in the tail of `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR7`, covers the rest of endpoint 0 pin-control/audio-status fields, covers complete endpoint 1 through endpoint 3 converter and pin-control field blocks, and enters endpoint 4 through `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_MODE` before stopping at the comment for `AZF0ENDPOINT4_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0`. The visible address-block markers are `azf0endpoint1_endpointind`, `azf0endpoint2_endpointind`, `azf0endpoint3_endpointind`, and `azf0endpoint4_endpointind`.

The slice has 2,049 `#define` lines: 1,023 `__SHIFT` constants and 1,038 `_MASK` constants. The imbalance is caused by chunk boundaries and field-family details: the first lines are only the mask tail for endpoint 0 audio descriptor 7, and some descriptors include additional fields such as the stereo-frequency bitfield.

Although this source path is under a `ceph-client` mirror, the content is AMDGPU display-driver hardware metadata. It does not implement distributed filesystem behavior.

## Purpose

The purpose of this chunk is to map symbolic DCN 3.0.1 Azalia endpoint register fields to exact bit positions and bit masks. AMD display code uses these constants with generated register helper macros to program HDMI/DisplayPort audio codec state without hard-coding bit arithmetic.

Major hardware surfaces represented here are:

- Per-endpoint converter capabilities and controls: audio-widget capabilities, converter format, channel/stream ID, digital converter state, stream formats, supported size/rates, stripe control, ramp rate, GTC embedding, and GTC counter delta/min/max fields.
- Per-endpoint pin capabilities and controls: pin widget capabilities, pin capabilities, unsolicited response setup, pin sense, widget control, channel speaker allocation, audio descriptors 0 through 13, multichannel enables, lipsync response, HBR response, sink information, hot-plug/audio enable control, unsolicited response force, default pin configuration, codec channel-status overrides, association info, digital output status, LPIB snapshot/timer fields, coding type, format-changed status, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status.
- Endpoint repetition for `AZF0ENDPOINT1`, `AZF0ENDPOINT2`, and `AZF0ENDPOINT3`, plus a partial `AZF0ENDPOINT4` block. Endpoint 0 is partial in this range because earlier endpoint 0 converter and early pin-control descriptors live in the previous chunk.

## Important APIs, Types, And Macros

The exported API is the generated field macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

There are no C-callable APIs or types. The important field groups are the register families exposed through those macro names:

- `AZALIA_F0_CODEC_CONVERTER_*` fields provide converter-side audio format, stream/channel binding, digital converter enables, supported stream format/rate descriptors, stripe control, ramp rate, and GTC timestamp/counter programming.
- `AZALIA_F0_CODEC_PIN_PARAMETER_*` and `AZALIA_F0_CODEC_PIN_CONTROL_*` fields provide pin widget/pin capabilities, pin sense, unsolicited response control, widget enable/control bits, speaker allocation, and per-format audio descriptor fields.
- `AUDIO_DESCRIPTOR*` fields pack `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, optional `SUPPORTED_FREQUENCIES_STEREO`, and `DESCRIPTOR_BYTE_2`. Runtime audio code writes these from EDID/audio mode data for HDMI and DP sinks.
- `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, and `MULTICHANNEL_MODE` expose enable, mute, and channel-ID routing for paired and odd multichannel lanes.
- `RESPONSE_LIPSYNC` exposes `VIDEO_LIPSYNC` and `AUDIO_LIPSYNC`; `RESPONSE_HBR` exposes `HBR_CAPABLE` and `HBR_ENABLE`.
- `SINK_INFO0` through `SINK_INFO8` encode manufacturer/product IDs, sink-description length, port IDs, and up to 18 display-name bytes.
- `HOT_PLUG_CONTROL` contains `CLOCK_GATING_DISABLE`, `CLOCK_ON_STATE`, and `AUDIO_ENABLED`, which are used around audio endpoint enable/disable and configuration writes.
- `UNSOLICITED_RESPONSE_FORCE`, `RESPONSE_CONFIGURATION_DEFAULT`, `PIN_CONTROL_CODEC_CS_OVERRIDE_*`, `DIGITAL_OUTPUT_STATUS`, `LPIB*`, `CODING_TYPE`, `FORMAT_CHANGED`, `WIRELESS_DISPLAY_IDENTIFICATION`, `REMOTE_KEEPALIVE`, and `AUDIO_*_INT_STATUS` provide status, override, timer, stream-position, and interrupt/status field metadata.

These constants are normally consumed indirectly through helpers such as `set_reg_field_value`, `get_reg_field_value`, `AZ_REG_READ`, `AZ_REG_WRITE`, `REG_SET`, `REG_UPDATE`, and register-list macros that token-paste register and field names into the generated `__SHIFT`/`_MASK` symbols.

## Control Flow

This header has no local runtime control flow. Runtime sequencing is supplied by AMDGPU display audio code:

1. DCN 3.0.1 resource and DMUB code include `dcn_3_0_1_offset.h` together with `dcn_3_0_1_sh_mask.h`.
2. Audio register tables bind endpoint register offsets with these field shifts/masks.
3. Audio setup code selects an Azalia endpoint, reads or writes endpoint data through the generated access macros, and uses `set_reg_field_value`/`get_reg_field_value` to pack or extract individual fields.
4. HDMI/DP audio configuration writes speaker allocation, ACP AI support, audio descriptor entries, HBR capability, lipsync values, sink manufacturer/product IDs, sink port IDs, display-name bytes, hot-plug/audio-enable state, and status/interrupt fields in the order required by the audio block and display link state.

The macros do not encode sequencing rules. Callers must still gate clocks correctly, select the intended endpoint, apply signal-specific HDMI versus DP behavior, respect sink capabilities, and handle sticky status/interrupt bits according to the hardware specification.

## State And Persistence Behavior

The chunk stores no software state. It describes MMIO-backed hardware state in Azalia endpoint registers:

- Converter state persists the active stream format, stream/channel ID, digital converter configuration, stripe/ramp settings, and GTC timing/counter fields.
- Pin state persists reported sink capabilities, pin sense, widget control, channel/speaker allocation, audio format descriptors, HBR and lipsync response values, sink identity strings, multichannel routing, and default configuration response data.
- Hot-plug/audio enable fields control whether the audio endpoint is exposed and whether clock gating is temporarily disabled during programming.
- LPIB and timer snapshot fields expose stream-position/timing state; audio enable/disable/format-change fields expose status and interrupt state.

Persistence is hardware-defined. Configuration fields generally remain until audio reconfiguration, modeset, endpoint reset, power gating, suspend/resume, or GPU reset. Status, interrupt, snapshot, force, and keepalive fields may be read-only, sticky, write-one-to-clear, self-clearing, or side-effect-sensitive; this generated header only supplies bit positions and masks, not access semantics.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.0.1 register offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`

Direct DCN 3.0.1 include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`

The audio behavior represented by these field names is implemented in the shared DCE/DC audio path, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`. That code reads and writes many fields present in this chunk, including `RESPONSE_HBR`, `RESPONSE_LIPSYNC`, `HOT_PLUG_CONTROL`, `CHANNEL_SPEAKER`, `AUDIO_DESCRIPTOR*`, and `SINK_INFO*`. It programs these values from `struct audio_info`, `struct audio_crtc_info`, DP link information, sink EDID data, and the active signal type.

Integration is also cross-generation. Azalia audio field names are repeated across DCE/DCN generated headers, so generic audio code can target multiple ASIC generations through per-generation register tables. The offset header and shift/mask header must be paired for the same ASIC; a DCN 3.0.1 mask used with a different offset table can compile while programming incorrect bits.

## Risks And Edge Cases

- Incorrect shifts or masks silently corrupt MMIO bitfields. High-risk fields include `HOT_PLUG_CONTROL`, audio descriptor packing, HBR capability/enable, lipsync values, sink info strings, multichannel routing, LPIB snapshot controls, and interrupt status/clear fields.
- Endpoint repetition is copy-sensitive. `AZF0ENDPOINT1`, `AZF0ENDPOINT2`, `AZF0ENDPOINT3`, and partial `AZF0ENDPOINT4` are structurally similar; an instance-specific mismatch may affect only one physical audio endpoint or one connector topology.
- The chunk boundaries are artificial. Endpoint 0 begins before this range, and endpoint 4 continues after it. The final per-file report must merge adjacent chunks before making complete claims about all Azalia endpoints.
- Audio descriptors are packed and indexed by format. A bad `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, `SUPPORTED_FREQUENCIES_STEREO`, or `DESCRIPTOR_BYTE_2` mask can make a sink expose the wrong LPCM or compressed-audio modes to the OS audio stack.
- Hot-plug and clock-gating fields are sequencing-sensitive. Runtime code temporarily disables clock gating while programming endpoint data; wrong masks can cause writes to be ignored, audio to remain disabled, or low-power state transitions to become unreliable.
- Sink-info string fields are byte-packed across several registers. Wrong masks or shifts can corrupt monitor-name reporting or overwrite adjacent bytes.
- Interrupt/status fields can be sticky or write-one-to-clear. Generic read-modify-write helpers must use exact masks or they can lose audio enable/disable/format-change events.

## Test Signals

Useful validation signals for this chunk are:

- Build AMDGPU display code with DCN 3.0.1 enabled, especially `dcn301_resource.c`, `dmub_dcn301.c`, and shared DCE audio code, to catch missing or renamed generated field macros.
- Static consistency checks that every full register family in this range has expected `__SHIFT` and `_MASK` pairs and that repeated endpoint 1 through endpoint 3 families remain structurally consistent where the hardware specification expects repetition.
- Diff against AMD's authoritative DCN 3.0.1 register database and neighboring generated headers such as DCN 3.0.0 or later DCN 3.x variants, reviewing intentional ASIC differences.
- HDMI and DisplayPort audio runtime tests across multiple connectors/endpoints: audio enable/disable, hotplug, EDID-driven sink capability programming, LPCM and compressed formats, 192 kHz/8-channel HBR checks, channel-count changes, and DP MST audio paths.
- Validate sink metadata exposed to the OS: manufacturer/product IDs, port IDs, display-name length, and all 18 display-name bytes from `SINK_INFO4` through `SINK_INFO8`.
- Exercise suspend/resume, display modesets, connector unplug/replug, clock/power gating, and audio format changes while watching for missing audio devices, stale capabilities, audio dropouts, stuck interrupts, bad lipsync/HBR state, and kernel display/audio logs.

## Cross-Chunk Notes

Previous chunks own the beginning of the endpoint 0 Azalia block, including converter fields and early pin-control fields before the descriptor 7 tail visible here. Later chunks own the remainder of endpoint 4 after `AZF0ENDPOINT4_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` and any subsequent Azalia/register families. The merge lane should combine adjacent chunks before presenting complete endpoint coverage for `dcn_3_0_1_sh_mask.h`.
