# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 59939-62306

## Purpose

This chunk is a generated AMD DCN 4.1.0 shift/mask register-field slice for Azalia F0 display-audio endpoint-indirect registers. It contains no executable C logic; its exported surface is the C preprocessor contract of `#define ...__SHIFT` and `#define ..._MASK` constants used by AMDGPU display register helpers to pack, update, and decode MMIO bitfields.

The requested range contains 2,053 `#define` entries over 300 register names and 365 distinct field names. The chunk starts in the tail of `AZF0ENDPOINT2` pin-control fields, fully covers `AZF0ENDPOINT3` through `AZF0ENDPOINT6`, and ends early in the `AZF0ENDPOINT7` block at `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER__SPEAKER_ALLOCATION__SHIFT`. The line boundaries are therefore chunking artifacts, not hardware-block boundaries.

Although this path lives under a local `ceph-client` source tree, the content is AMDGPU DCN display/audio hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct I/O operations in this range. The public API is the generated bitfield macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a field inside the register value.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field inside the register value.

The visible register families describe repeated HD Audio/Azalia endpoint capabilities and controls:

- Endpoint 2 tail: `LPIB_TIMER_SNAPSHOT`, `CODING_TYPE`, `FORMAT_CHANGED`, `WIRELESS_DISPLAY_IDENTIFICATION`, `REMOTE_KEEPALIVE`, `AUDIO_ENABLE_STATUS`, audio enabled/disabled/format-changed interrupt status, and endpoint fine-grain clock-gating report disable.
- Endpoints 3 through 6 complete repeated blocks: converter widget capability, converter format, channel/stream ID, digital converter control, supported stream formats and size/rates, stripe and ramp controls, pin widget/capability parameters, unsolicited response, pin sense, widget output enable, channel/speaker allocation, ACP data, audio descriptors 0 through 13, multichannel enable/mode, lipsync, HBR, sink info 0 through 8, hot-plug control, forced unsolicited response, configuration default, IEC 60958 channel-status override registers 0 through 8, association info, digital output status, LPIB snapshot/LPIB/timer, coding type, format-change state, wireless display ID, remote keepalive, audio enable status, audio interrupt status, and endpoint clock-gating report disable.
- Endpoint 7 beginning: converter parameter/control fields through the start of pin-channel speaker allocation. Later endpoint 7 fields are outside this line range.

Representative fields include audio stream attributes (`NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, `SAMPLE_BASE_RATE`, `STREAM_ID`, `CHANNEL_ID`), digital-output flags (`DIGEN`, `V`, `VCFG`, `PRE`, `COPY`, `NON_AUDIO`, `PRO`, `L`, `CC`, `KEEPALIVE`), pin and sink capability fields (`HDMI`, `DP`, `EAPD_CAPABLE`, `POWER_CONTROL`, `UNSOLICITED_RESPONSE_CAPABILITY`), ELD/sink data fields (`MANUFACTURER_ID`, `PRODUCT_ID`, `SINK_DESCRIPTION`, `PORT_ID`, `SINK_INFO_VERSION`), audio descriptor fields (`MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, `SUPPORTED_BIT_RATES`, `SUPPORTED_BITS`, `AUDIO_FORMAT_CODE`), multichannel and HBR toggles, hotplug/unsolicited-response control bits, `LPIB` snapshot fields, and interrupt status fields with flag/mask/type subfields.

The masks are 32-bit register masks with an `L` suffix, such as `0x00000001L`, `0x000000F0L`, `0x00FF0000L`, or `0xFFFFFFFFL`. Consumers normally combine these masks with shifts through AMD display macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and generated register-field list initializers.

## Control Flow

This header has no runtime control flow. Its role is compile-time macro expansion:

1. DCN401 display code includes `dcn_4_1_0_sh_mask.h` with the matching `dcn_4_1_0_offset.h`.
2. Register-list and field-list macros token-paste symbolic register and field names into per-block register tables.
3. Runtime display/audio paths call AMD display register helpers. Those helpers read or write MMIO offsets from the offset header and use these shift/mask constants to isolate or program the relevant fields.
4. Hardware and consumer code provide ordering semantics for enabling audio, changing stream format, handling hotplug/unsolicited responses, reading status, and acknowledging interrupts; this generated header only names the bit positions.

The repeated endpoint naming is part of the compile-time control path. A consumer targeting endpoint 4 must expand `AZF0ENDPOINT4_*` field symbols, while endpoint 5 and endpoint 6 use separate but mostly isomorphic symbols. Accidentally token-pasting the wrong endpoint instance can still compile if the target register family exists.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It defines field encodings for hardware-visible Azalia endpoint state:

- Converter format and stream routing state: channel count, sample size/rate, stream type, stream ID, channel ID, stripe control, ramp rate, and supported format/rate capabilities.
- Digital audio output state: digital converter enable, validity/configuration/preemphasis/copyright/non-audio/professional flags, channel-status category/code fields, keepalive, and IEC 60958 channel-status override nibbles.
- Pin and sink state: HDMI/DP capability flags, pin sense, unsolicited response enable/tag, output enable, speaker/channel allocation, ELD-like sink information, audio descriptors, lipsync, HBR, ACP, hotplug control, wireless display identification, and remote keepalive capability/enable.
- Runtime status and interrupt state: audio enable status, audio enabled/disabled/format-changed flags, interrupt masks/types, format-change reason/response, LPIB snapshots, digital output active status, and endpoint clock-gating report disable.

Persistence is hardware-defined. Control fields generally remain until reprogrammed by modeset, audio stream setup/teardown, hotplug handling, suspend/resume, power gating, GPU reset, or ASIC reset. Status, interrupt, snapshot, and acknowledgement-related fields may be sticky, read-only, write-one-to-clear, self-clearing, or valid only while the Azalia/audio endpoint block is powered and clocked. This header does not encode those access rules.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus AMD's generated register-header convention. This file must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`, which supplies the matching Azalia endpoint register offsets and `_BASE_IDX` values.
- AMD's generated DCN 4.1.0 register database, because these masks and shifts are silicon ABI metadata.
- DCN401 display code that includes the generated offset and shift/mask headers for register table construction.

Important integration points are display audio and connector handling in the AMDGPU DCN401 stack. Resource construction and encoder setup code use generated register tables to expose Azalia/AFMT/audio register fields to shared display code. Runtime paths that configure HDMI/DP audio, ELD/sink information, HBR, multichannel audio, channel-status overrides, stream IDs, and hotplug or unsolicited-response behavior depend on the correctness of these field names and masks.

These definitions also integrate with interrupt/status handling. The `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS` fields provide the flag/mask/type layout that consumers use to identify and control audio-state events. The `FORMAT_CHANGED` fields provide both event state and acknowledgement/response-related fields, so their masks must agree with the hardware side effects expected by the driver.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting unrelated bits in an MMIO register or decoding the wrong status.
- The file is generated. Manual edits risk divergence from the authoritative register database, the paired offset header, firmware assumptions, and the silicon documentation.
- The chunk boundaries are not semantic. Endpoint 2 begins before this range, endpoint 7 continues after it, and only endpoints 3 through 6 are complete within this chunk.
- Repeated endpoint layouts make instance drift hard to spot. `AZF0ENDPOINT3` through `AZF0ENDPOINT6` are mostly isomorphic, so a single wrong endpoint prefix or copied mask may only fail on a specific connector or audio engine.
- Several fields represent status, mask, acknowledgement, or interrupt-control bits. Misprogramming them can leave audio enable/disable/format-change events stuck, masked unintentionally, or acknowledged incorrectly.
- Format and stream-routing fields are protocol-visible. Bad masks for channel count, sample width/rate, stream ID, HBR, multichannel mode, or IEC 60958 channel status can produce silent audio, distorted audio, incorrect sink-reported capabilities, or invalid HDMI/DP audio packets.
- Sink-info and audio-descriptor fields are wide byte/nibble packed layouts. Off-by-one shifts can produce plausible-looking but wrong ELD/audio capability data, which may only surface with particular monitors, receivers, or multichannel formats.
- Power/clock-gating and snapshot fields can be timing-sensitive. Reads or writes while the endpoint is clock-gated, during hotplug churn, or around stream reconfiguration may return stale status or drop updates depending on hardware sequencing.

## Test Signals

Useful validation signals are a mix of generated-header consistency checks, build coverage, and display-audio runtime behavior:

- Build DCN401 AMDGPU display code with `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h` together. Missing or renamed field macros should fail in generated register-table initialization and register-helper use sites.
- Mechanically compare this range against AMD's authoritative DCN 4.1.0 register source. Treat the first and last registers as partial chunk boundaries.
- Run static checks that every `__SHIFT` field has a matching `_MASK`, that repeated endpoint 3 through 6 groups have the same field sets, and that masks align with shifts for representative packed fields such as `CHANNEL_STREAM_ID`, `CONVERTER_FORMAT`, `CHANNEL_SPEAKER`, `AUDIO_DESCRIPTOR*`, `SINK_INFO*`, and `FORMAT_CHANGED`.
- Exercise HDMI and DisplayPort audio on connectors backed by endpoints 3 through 6, including stream enable/disable, sample-rate changes, bit-depth changes, stereo and multichannel playback, HBR formats where supported, and rapid modesets.
- Verify ELD/sink info and audio descriptor reporting with multiple displays or AV receivers. Expected signals are correct supported format/rate/channel data and stable user-space audio device capabilities after hotplug.
- Exercise hotplug, unplug, suspend/resume, and GPU reset paths while audio is active. Watch for missed or stuck audio enabled/disabled/format-changed interrupts, stale LPIB snapshots, lost unsolicited responses, or incorrect digital-output-active status.
- Check HDMI/DP protocol behavior with audio analyzers or kernel/display diagnostics where available: valid IEC 60958 channel status, correct speaker/channel allocation, no malformed audio infoframes, and no cross-endpoint aliasing.

## Cross-Chunk Notes

The previous chunk contains the earlier `AZF0ENDPOINT2` definitions, including fields needed to understand endpoint 2 as a complete block. The next chunk continues `AZF0ENDPOINT7` after the early `CODEC_PIN_CONTROL_CHANNEL_SPEAKER` fields. The final per-file research document should merge adjacent chunks before making whole-file claims about all Azalia endpoints or all DCN 4.1.0 shift/mask definitions.
