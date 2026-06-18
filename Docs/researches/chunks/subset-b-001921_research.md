# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 59329-61649

## Scope

This chunk is a generated AMD DCN 3.1.6 register shift/mask header slice for Azalia/HDA audio endpoint and input-endpoint indirect registers. It contains no executable code, functions, structs, or runtime allocation logic. Its public surface is a large set of preprocessor constants named as:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The slice starts inside `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_SINK_INFO4`, completes the tail of output endpoint 5, covers complete output endpoint 6 and output endpoint 7 Azalia register families, then covers input endpoint 0, input endpoint 1, input endpoint 2, and most of input endpoint 3. The next chunk begins at `azf0inputendpoint4_inputendpointind`.

## Purpose

The header maps hardware register bit layouts into C preprocessor constants used by DCN 3.1.6 display/audio code. Consumers pair these field masks and shifts with matching offset/index definitions from `dcn_3_1_6_offset.h` and the display driver's register helper macros. The intended use is field extraction and field construction for memory-mapped or indirect Azalia codec endpoint registers.

The endpoint blocks describe HDMI/DisplayPort audio codec state exposed through GPU display hardware:

- Output endpoints `AZF0ENDPOINT5`, `AZF0ENDPOINT6`, and `AZF0ENDPOINT7` model digital audio converter/pin widgets, sink metadata, ELD-like descriptor fields, stream/channel routing, IEC 60958 channel-status overrides, hot-plug/audio enable state, and interrupt/status bits.
- Input endpoints `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT3` model input converter and input pin widgets, including stream format, channel/stream ID, input pin sense, multichannel enables, HBR support, input activity, LPIB snapshots, and audio infoframe fields.

## Important Definitions

The main macro families in this chunk are:

- `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_*`: tail of endpoint 5 pin-control metadata and status. The chunk includes sink description bytes 4-17, hot-plug control, forced unsolicited response payload, default pin configuration, multichannel enable mode, IEC 60958 channel-status override registers 0-8, association info, output-active status, LPIB snapshot registers, coding type, format-change status, wireless display ID, remote keepalive, and audio enable/disable/format interrupt status.
- `AZF0ENDPOINT6_AZALIA_F0_CODEC_CONVERTER_*` and `AZF0ENDPOINT7_AZALIA_F0_CODEC_CONVERTER_*`: output converter fields for audio widget capabilities, converter format, channel/stream ID, digital converter flags, supported stream formats/rates, stripe control, ramp rate, GTC presentation-time embedding, and GTC delta diagnostics.
- `AZF0ENDPOINT6_AZALIA_F0_CODEC_PIN_*` and `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_*`: output pin fields for widget capabilities, pin capabilities, unsolicited response, pin sense, output widget enable, channel/speaker allocation, ACP packet data, audio descriptors 0-13, multichannel controls, lipsync, HBR, sink information, hot-plug control, configuration default, channel-status overrides, output status, LPIB, coding type, format change, wireless display, remote keepalive, and audio enable/disable/format interrupt state.
- `AZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_*` through `AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_*`: input converter and input pin fields for input debug, widget capabilities, converter format, channel/stream ID, digital converter flags, supported formats/rates, input pin capabilities, unsolicited response, input pin sense with presence detect, input widget enable, multichannel controls 0-7, HBR, channel allocation, hot-plug/audio-enabled state, forced unsolicited response, default config, LPIB snapshots, input activity/status-control, and audio infoframe fields.

Repeated field patterns are important because most endpoints share identical bit positions:

- Audio widget capability bits use low single-bit flags (`INPUT_AMPLIFIER_PRESENT`, `OUTPUT_AMPLIFIER_PRESENT`, `FORMAT_OVERRIDE`, `DIGITAL`, `POWER_CONTROL`, `LR_SWAP`) plus delay and type fields in the upper halfword.
- Converter format uses `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, sample base divisor/multiple/rate, and stream type packed in the low 16 bits.
- Digital converter control uses IEC 60958-style flags: `DIGEN`, validity, `VCFG`, pre-emphasis, copyright, non-audio, professional, level, category code, and keepalive.
- Pin speaker/channel allocation uses speaker allocation, channel allocation, HDMI/DP connection bits, extra connection info, LFE playback level, level shift, and down-mix inhibit.
- Multichannel controls pack enable, mute, and channel ID fields into repeated 8-bit lanes.
- Status/interrupt registers expose flag, mask, and type bits for audio enabled, disabled, and format changed events.

## Control Flow

There is no local control flow in this header chunk. Runtime behavior is indirect:

1. DCN 3.1.6 display code includes `dcn_3_1_6_offset.h` and this `dcn_3_1_6_sh_mask.h`.
2. Register helper macros such as `FD_MASK`, `FD_SHIFT`, `SF`, `HWS_SF`, and related resource-table initializers expand these constants into per-block register/mask/shift tables.
3. Higher-level audio, DIO, AFMT, APG, VPG, and DMUB paths use those tables to read, mask, shift, and write hardware fields.

`dcn316_resource.c` includes this header and uses Azalia endpoint index/data fields in audio register lists. `dmub_dcn316.c` also includes the same offset and mask headers to populate DMUB service register tables through mask/shift expansion.

## State And Persistence

The macros themselves are compile-time constants and persist only in the built kernel object code as immediate values or initializer data. They do not store software state.

The hardware fields they describe are stateful device registers. Relevant state categories in this slice include:

- Link/sink capability state: sink manufacturer/product IDs, sink description bytes, audio descriptors, speaker/channel allocation, HBR capability, DP/HDMI connection indicators, supported rates/formats, and widget capabilities.
- Stream programming state: converter format, stream ID, channel ID, digital converter flags, multichannel enable/mute/channel routing, channel-status overrides, coding type, and keepalive.
- Event/status state: hot-plug audio enable, output active, input activity, presence detect, format changed, forced unsolicited responses, and enable/disable/format interrupt flags/masks/types.
- Timing/debug state: LPIB snapshots, cyclic buffer wrap count, LPIB timer snapshot, GTC embedding controls, and GTC counter delta/min/max diagnostics.

Persistence across suspend/resume, hotplug, modeset, or audio stream teardown depends on the surrounding AMDGPU display/audio code reprogramming the corresponding hardware registers. This header only defines bit positions; it does not preserve or restore register contents.

## Dependencies

This chunk depends on generated register naming consistency across AMD's ASIC register headers:

- Matching register offsets and indirect indices in `dcn_3_1_6_offset.h`.
- Register helper macros in AMD display code that expect the `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming scheme.
- DCN 3.1.6 resource and DMUB code that include these generated headers.
- The Azalia/HDA hardware programming model, where endpoint index/data registers select codec node registers and fields are packed into 32-bit register values.

The source tree also contains analogous definitions for other DCN/DCE generations. Those parallel headers are useful for diff-based validation, but this chunk is authoritative for DCN 3.1.6.

## Integration Points

Key integration points are:

- `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`: includes this header and uses its masks/shifts in DCN 3.1.6 resource construction and hardware sequencer field tables. Audio-related register lists reference Azalia endpoint index/data registers and global Azalia clock/audio DTO fields.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`: includes this header to build DMUB service mask/shift tables through `FD_MASK` and `FD_SHIFT`.
- DCE/DCN audio support such as `dce_audio`, AFMT, APG, VPG, DIO stream encoders, and HPO stream paths: these components consume the generated field tables rather than directly depending on individual macros from this chunk in most cases.
- Hardware validation and generated-header maintenance: ASIC register database updates must keep `_SHIFT`, `_MASK`, offset, and indexed address-block definitions synchronized.

## Risks

- Generated-header drift: a wrong mask or shift compiles cleanly but can program the wrong hardware bits, leading to broken HDMI/DP audio, bad channel routing, missing HBR, incorrect ELD/sink data, or missed unsolicited responses.
- Boundary risk: this chunk begins mid-register for endpoint 5 and ends before input endpoint 4. Merge/reconciliation must combine adjacent chunks to avoid treating endpoint 5 or input endpoint 3/4 coverage as complete per-file analysis.
- Repetition risk: endpoint 6 and endpoint 7 are near-identical. Copy-generation mistakes can leave one endpoint with mismatched field names, missing masks, or a stale bit position while neighboring endpoints look correct.
- Interrupt/status risk: flag/mask/type fields for audio enabled/disabled/format changed use compact bit positions. Incorrect masks can invert interrupt enable behavior or hide format-change notifications.
- Indexed-register risk: Azalia endpoint blocks are accessed through endpoint index/data registers. A correct field mask is still unsafe if paired with the wrong `ix...` indirect index or endpoint instance.
- Capability reporting risk: sink info, audio descriptors, HBR capability, speaker allocation, and input infoframe fields may be surfaced up-stack. Bad field extraction can cause userspace-visible audio capability errors even when the link itself is otherwise functional.

## Test Signals

Useful validation signals for changes touching this header or its generator include:

- Build coverage for AMDGPU DCN 3.1.6 display code with warnings enabled, confirming all generated macro names referenced by resource/DMUB tables still resolve.
- Diff checks against the paired `dcn_3_1_6_offset.h` to ensure every `AZF0ENDPOINT6`, `AZF0ENDPOINT7`, and `AZF0INPUTENDPOINT0-3` register field has a matching register/index definition where applicable.
- Cross-generation diffing against nearby DCN headers for repeated Azalia endpoint layouts, while accounting for ASIC-specific differences.
- HDMI/DP audio smoke tests on DCN 3.1.6 hardware: hotplug audio detection, audio enable/disable transitions, PCM playback, multichannel routing, HBR/encoded playback if supported, suspend/resume with audio, and format changes during active playback.
- Register readback tests for representative fields: converter format packing, channel/stream ID, multichannel enables, audio descriptors, sink info bytes, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, `AUDIO_FORMAT_CHANGED_INT_STATUS`, input activity/status-control, and LPIB snapshots.
- DMUB initialization tests verifying mask/shift tables derived from `FD_MASK`/`FD_SHIFT` match expected DCN 3.1.6 register metadata.
