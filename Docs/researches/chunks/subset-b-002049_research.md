# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 54449-56598

## Scope

- Chunk id: `subset-b-002049`
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`
- Source lines: 54449-56598
- Observed content: 2,150 generated header lines containing 1,922 `#define` entries, split into 960 `__SHIFT` macros and 962 `_MASK` macros.

This chunk is the final generated shift/mask slice of the AMD DCN 3.2.1 register-field header. It has no executable C logic. It starts in the middle of the `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4` field group, completes the remaining output endpoint 7 Azalia/HDA audio pin-control and audio interrupt fields, then covers all eight `azf0inputendpointN_inputendpointind` indexed input endpoint address blocks. The range ends with the file's closing `#endif`.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display/audio hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The chunk provides compile-time bit positions and masks for DCN321 Azalia function 0 endpoint registers. These constants are paired with register offsets and indexed-register IDs from `dcn_3_2_1_offset.h` so AMD display code can program or inspect HDA/HDMI/DP audio codec endpoint state through register helper macros.

The covered hardware surface is audio-specific:

- The tail of `AZF0ENDPOINT7` output endpoint fields for IEC 60958 channel-status overrides, channel numbers, association info, digital-output status, LPIB snapshots, coding type, audio format-change reporting, wireless-display identification, remote keepalive, audio enable state, and enable/disable/format-change interrupt status.
- `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` input endpoint fields for converter capabilities, stream format, channel/stream IDs, digital converter control, supported size/rate reports, pin capabilities, unsolicited response setup, input pin sense, widget control, multichannel enable maps, HBR capability/enable, channel allocation, hot-plug/audio-enable state, forced unsolicited responses, configuration defaults, LPIB snapshots, input activity/status controls, and received infoframe metadata.

The `AZF0INPUTENDPOINT*` groups are highly regular repeated instances. Each endpoint has the same generated field layout, with the endpoint number encoded in the macro prefix.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, includes, locks, or runtime APIs in this chunk. The public interface is the generated preprocessor namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: 32-bit mask for isolating or updating that field.
- `// addressBlock: azf0inputendpointN_inputendpointind`: generated block markers for indexed input endpoint register groups.

Important field families in this range include:

- IEC/channel-status override fields: `IEC_60958_CS_CHANNEL_NUMBER_*`, `IEC_60958_CS_CGMS_A`, and validity bits in the output endpoint 7 `CODEC_CS_OVERRIDE_*` registers.
- Output endpoint 7 status and event fields: `OUTPUT_ACTIVE`, `FORMAT_CHANGED`, `FORMAT_CHANGED_ACK_UR_ENABLE`, `FORMAT_CHANGE_REASON`, `FORMAT_CHANGE_RESPONSE`, `REMOTE_KEEP_ALIVE_ENABLE`, `REMOTE_KEEP_ALIVE_CAPABILITY`, `AUDIO_ENABLE_STATUS`, and audio enabled/disabled/format-changed flag/mask/type triples.
- Input converter capability fields: `AUDIO_CHANNEL_CAPABILITIES`, amplifier-present bits, `FORMAT_OVERRIDE`, `DIGITAL`, `POWER_CONTROL`, `LR_SWAP`, widget delay, and widget `TYPE`.
- Input converter format fields: `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, `SAMPLE_BASE_DIVISOR`, `SAMPLE_BASE_MULTIPLE`, `SAMPLE_BASE_RATE`, and `STREAM_TYPE`.
- Input digital converter fields: `DIGEN`, validity/config/preemphasis/copy/non-audio/professional bits, category code `CC`, and `KEEPALIVE`.
- Input pin capability and sense fields: impedance sense, trigger/jack detection, output/input capability, HDMI/DP capability bits, VREF control, EAPD capability, `IMPEDANCE_SENSE`, and `PRESENCE_DETECT`.
- Input pin routing and multichannel fields: `CHANNEL_ID`, `STREAM_ID`, `IN_ENABLE`, multichannel 0-7 enable/mute/channel-id bitfields split across `MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`, `CHANNEL_ALLOCATION`, and HBR capability/enable.
- Input status/metadata fields: `AUDIO_ENABLED`, `INPUT_ACTIVITY`, `CHANNEL_LAYOUT`, unsolicited-response enable bits, `CHANNEL_COUNT`, `CHANNEL_ALLOCATION`, `INFOFRAME_BYTE_5`, and `INFOFRAME_VALID`.

The companion offset header exposes both MMIO selector/data registers, such as `regAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` and `regAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA`, and indexed IDs such as `ixAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`. This chunk supplies the field layout for those indexed register payloads.

## Control Flow

This header chunk has no local control flow. Runtime behavior is supplied by AMDGPU Display Core:

1. DCN321 resource construction includes `dcn_3_2_1_offset.h` and this shift/mask header.
2. Register-list and field-list macros paste generated names into register, shift, and mask tables.
3. Audio helper code selects an Azalia endpoint indexed register through endpoint index/data registers or direct register tables.
4. Helper macros such as `REG_SET`, `REG_UPDATE`, `REG_READ`, and audio-specific indexed helpers pack or extract field values using these masks and shifts.
5. Hardware implements the actual behavior: codec capability reporting, stream-format programming, channel allocation, HBR enablement, LPIB snapshotting, unsolicited responses, hotplug/audio-enable indication, and input infoframe/status capture.

The chunk does not encode ordering rules. Consumers still need to sequence endpoint index selection, register data reads/writes, audio stream enable/disable, infoframe updates, hotplug handling, interrupt masking/acknowledgement, and audio format-change response according to the HDA/Azalia and DCN programming model.

## State And Persistence Behavior

The macros are stateless constants. State exists only in the underlying hardware registers:

- Capability and descriptor-style fields report stable hardware or firmware-populated codec properties, such as widget capabilities, supported stream formats, supported sample rates/bit depths, pin capabilities, HDMI/DP capability bits, and default configuration values.
- Programmed configuration state includes converter format, channel/stream IDs, digital converter controls, unsolicited-response enable/tag values, input widget enablement, multichannel enable/mute/channel mapping, HBR enablement, hot-plug clock gating controls, forced unsolicited-response payloads, and UR-enable bits for input activity or infoframe changes.
- Live or latched status includes output active, input activity, audio-enabled status, presence detect, LPIB position, LPIB timer snapshots, cyclic-buffer wrap count, infoframe validity and contents, format-change reason/response, audio enabled/disabled/format-changed flags, and HBR capability/status.

Persistence is hardware-defined. Some fields are read-only capability/status, some are writable configuration, and some status or interrupt bits may be sticky, write-one-to-clear, self-clearing, or valid only while the associated display/audio clock and endpoint are powered. The generated shift/mask header does not identify access semantics; consumers must preserve reserved or unrelated bits through read-modify-write paths where required.

## Dependencies And Integration Points

Direct dependencies and consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`, which supplies the matching MMIO offsets and indexed register IDs for the Azalia endpoint blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes this header and builds DCN321 register/shift/mask tables. The `DCE120_AUD_COMMON_MASK_SH_LIST` macro references the `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_DATA` fields, while common audio masks cover function-level audio fields outside this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` and `dce_audio.h`, which implement shared display audio operations around Azalia endpoint index/data access, stream format support, HBR response, hotplug control, speaker/channel mapping, sink info, audio descriptors, and configuration-default fields.
- DCN resource and stream/link paths that create audio objects for display connectors. On DCN321, the declared audio register array has five entries, while the generated register database includes more endpoint and input endpoint definitions. That mismatch is normal for generated ASIC metadata but means not every generated endpoint is necessarily instantiated by the driver.
- HDA/Azalia, HDMI, and DisplayPort audio flows visible to users as monitor audio device enumeration, format negotiation, hotplug audio enable/disable, high-bit-rate audio, channel allocation, and infoframe handling.

The input endpoint blocks are generated and paired with index/data register accessors in the offset header, but local display code primarily exercises output audio endpoint paths. Input endpoint definitions still matter for ASIC register database completeness, future consumers, diagnostics, and cross-generation table consistency.

## Risks And Edge Cases

- Numeric drift is the main risk. A wrong mask or shift can compile cleanly but update the wrong HDA codec field, causing silent audio format negotiation failures, bad channel mapping, missed hotplug/audio enable state, incorrect LPIB reporting, or broken unsolicited responses.
- The range starts mid-register at the tail of `CODEC_CS_OVERRIDE_4`. Final per-file synthesis must combine the previous chunk before making complete claims about output endpoint 7 IEC channel-status override coverage.
- Repeated endpoint names are easy to misuse. `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` share nearly identical field layouts, but the endpoint number is part of the selected indexed register namespace.
- Output endpoint and input endpoint fields are similar but not interchangeable. For example, output pin-sense and input pin-sense fields use different generated register names, and output endpoint audio controls may have additional sink-info/audio-descriptor/lipsync fields outside this chunk.
- Indexed endpoint access requires correct selector/data sequencing. Using the right field mask with the wrong indexed register ID or stale endpoint index can read or write unrelated codec state.
- Multichannel enable fields pack enable, mute, and channel-id values for eight logical channels across two registers. Off-by-one channel mapping mistakes can produce valid-looking register values with wrong speaker layout.
- Format and stream fields are compact bitfields. Incorrect values for sample base, divisor, multiplier, bits per sample, stream type, or channel count can break only specific audio modes.
- Status, flag, mask, and type fields often have side effects. Incorrect handling of audio enabled/disabled/format-changed flags or unsolicited-response force bits can cause missed events or interrupt storms.
- `PRESENCE_DETECT`, `INFOFRAME_VALID`, `INPUT_ACTIVITY`, and LPIB snapshots are live or latched observations. Tests must account for timing, power state, and stream activity rather than assuming static readback.

## Test Signals

Useful validation signals for this chunk are build-time consistency checks plus DCN321 hardware audio behavior:

- Build AMDGPU Display Core with DCN321 enabled and ensure `dcn321_resource.c`, audio register tables, and `dce_audio` consumers resolve all referenced Azalia endpoint shift/mask names.
- Generated-header consistency checks: every expected field should have a matched `__SHIFT` and `_MASK`, masks should fit within 32 bits, repeated `AZF0INPUTENDPOINT0-7` field layouts should be identical where the hardware database intends them to be, and indexed register IDs in `dcn_3_2_1_offset.h` should have matching field names in this header.
- HDMI/DP audio smoke tests on DCN321 hardware: monitor audio device enumeration, hotplug/unplug, modeset with audio enabled, suspend/resume, stream disable/enable, and format renegotiation.
- Audio format coverage: 2-channel and multichannel LPCM, different sample rates and sample widths, HBR audio when supported, non-audio/professional/copy bits, and IEC channel-status override behavior.
- Channel mapping validation with layouts that exercise `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, `CHANNEL_ALLOCATION`, `CHANNEL_ID`, and `STREAM_ID`.
- Event-path validation for audio enabled/disabled/format-changed interrupts, unsolicited responses, hot-plug control, format-change response, and remote keepalive behavior.
- Diagnostics using LPIB/LPIB timer snapshots, cyclic-buffer wrap counts, digital-output active state, input activity, presence detect, infoframe validity, and HBR capability/enable readback.

## Chunk Boundary Notes

Line 54449 begins after the comment and first fields for `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4`; adjacent prior chunk coverage is needed for the complete register group. Lines 54534-56597 cover all eight generated input endpoint blocks, and line 56598 closes the header guard. The merge/reconciliation lane should combine this report with adjacent `dcn_3_2_1_sh_mask.h` chunks before producing the final per-file research document.
