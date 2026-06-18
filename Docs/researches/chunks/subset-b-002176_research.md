# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 62307-64577

## Purpose

This chunk is generated AMD DCN 4.1.0 register-field metadata. It contains no executable C logic; it exports preprocessor constants that describe bit positions and masks for Azalia/HD-audio codec endpoint and input-endpoint indexed registers. AMDGPU display code pairs these field constants with the matching DCN 4.1.0 offset definitions and generic register helpers to pack, extract, and update individual MMIO or indexed-register fields.

The requested range contains 2,026 `#define` lines: 1,013 `__SHIFT` macros and 1,013 `_MASK` macros. It starts inside `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER`: the `SPEAKER_ALLOCATION__SHIFT` is on line 62306, just before this chunk, while the remaining shifts and all masks for that register are in this chunk. It ends inside `AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`: only `STREAM_FORMATS__SHIFT` is included at line 64577, while its mask and the rest of input endpoint 7 continue after this chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or callbacks in this range. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, preserving, or clearing that field.

Major register groups in this chunk:

- `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_*` and related endpoint 7 macros. This covers output pin channel/speaker allocation, ACP packet data, HDMI/DP audio descriptors 0-13, multichannel enable/mute/channel-id packing, lipsync and HBR capability/enables, sink manufacturer/product/port/description fields, hot-plug audio enable/clock-gating control, unsolicited response forcing, default pin configuration, multichannel mode, channel-status override bytes, association information, digital output status, LPIB snapshot/readback/timer fields, coding type, format-change flags, wireless-display identification, remote keepalive, audio enable/disable/format interrupt status, and endpoint fine-grain clock-gating reporting disable.
- `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT6`. Each complete input endpoint instance repeats the same input-converter and input-pin register layout: audio widget capabilities, converter format, channel/stream ID, digital converter status/control bits, supported stream formats, supported sample rates and bit depths, pin widget capabilities, pin capability flags, unsolicited-response control, input pin sense, widget control, multichannel enables 0-7, HBR capability/enable, channel allocation, hot-plug/audio-enable control, unsolicited-response force payload, default configuration, LPIB snapshot/data/timer, input activity/status controls, and audio infoframe fields.
- Beginning of `AZF0INPUTENDPOINT7`. The range includes its input-converter audio-widget capabilities, converter format, channel/stream ID, digital converter bits, and only the first `STREAM_FORMATS__SHIFT` line. The rest of endpoint 7 belongs to the following chunk.

Important field themes are HD-audio codec capability advertisement, stream format programming, HDMI/DP audio channel mapping, IEC/channel-status reporting and override, hotplug and unsolicited-response signaling, link-position-in-buffer snapshots, input activity reporting, and per-endpoint audio clock/power status.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display and audio integration code:

1. DCN 4.1.0 code includes this shift/mask header along with `dcn_4_1_0_offset.h`.
2. Resource and hardware-block tables token-paste symbolic register and field names into structures used by display register helpers.
3. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and indexed-register variants to access endpoint index/data registers.
4. The numeric shift/mask values from this chunk control which bits are read or modified when the driver advertises audio capabilities, programs stream/channel format, handles hotplug/unsolicited responses, snapshots LPIB state, and services audio-status interrupts.

The macros themselves do not encode ordering rules. Consumers must still sequence codec endpoint index selection, data reads/writes, stream disable/enable, hotplug transitions, HBR setup, multichannel routing, infoframe validity, and interrupt/status acknowledgement according to the hardware programming model.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware-backed Azalia state:

- Output endpoint 7 pin state, including speaker/channel allocation, HDMI/DP connection indication, ACP packet controls, audio descriptor capabilities, multichannel enable/mute/channel-id fields, lipsync, HBR, sink identity/description, hotplug audio enable, unsolicited responses, pin default configuration, channel-status override bytes, digital output status, LPIB snapshots, coding type, format-change state, wireless-display identification, keepalive, and audio interrupt status.
- Input endpoints 0-6 state, including converter capabilities, converter stream format, stream/channel IDs, digital converter control/status bits, rate/size capabilities, input pin capabilities, unsolicited response configuration, pin sense, widget control, multichannel routing, HBR, hotplug/audio enable, LPIB snapshots, input activity flags, channel layout, activity/infoframe-change unsolicited-response enables, and input infoframe contents.
- Partial input endpoint 7 converter state through the `STREAM_FORMATS__SHIFT` field.

Persistence is hardware-defined. Configuration fields generally survive until modeset, audio stream reprogramming, hotplug, display/audio block power gating, suspend/resume, GPU reset, or driver reinitialization. Status, interrupt, format-change, unsolicited-response, LPIB snapshot, keepalive, audio-enabled, clock-state, and activity fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only when the relevant endpoint clocks and power domains are active. This generated header does not express those access semantics; the consuming driver code and hardware specification must provide them.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 4.1.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`, which provides the matching register offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c`, and other DCN 4.0.1/DCN 4.1.0 display files that include `dcn_4_1_0_sh_mask.h`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`, which defines Azalia endpoint register-list patterns using `AZF0ENDPOINT` instance names.
- Generic AMD display register-helper infrastructure that combines offsets, masks, shifts, and base indexes for MMIO and indexed endpoint register access.
- HD-audio/DisplayPort/HDMI audio behavior in the display stack, including ELD/sink capability advertisement, infoframe and channel-status programming, HBR audio, hotplug handling, and stream position reporting.

The most direct integration points are display audio enumeration, HDMI/DP audio stream setup, high-numbered output endpoint 7 handling, capture/input-audio endpoint handling for endpoints 0-7, hotplug/unsolicited-response delivery, audio interrupt handling, and diagnostics that read LPIB or input activity state.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while reading or writing the wrong hardware bits.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the matching offset header, firmware expectations, and silicon documentation.
- The chunk boundaries cut two register groups. Complete reasoning about `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER` requires the previous line for `SPEAKER_ALLOCATION__SHIFT`; complete reasoning about input endpoint 7 requires the following chunk.
- Repeated input endpoint instances are copy-sensitive. An error in one `AZF0INPUTENDPOINT<n>` namespace can affect only a specific endpoint and may be missed by testing that exercises only endpoint 0.
- Indexed endpoint access is sequencing-sensitive. Using a field macro with the wrong endpoint index/data register can return plausible but unrelated data or modify another endpoint's state.
- Audio capability and descriptor fields are user-visible through sink and codec enumeration. Bad masks can advertise invalid channel counts, rates, bit depths, speaker allocations, HBR support, or HDMI/DP connection state.
- Hotplug, unsolicited-response, interrupt-status, audio-enabled, and format-change fields can be sticky or self-clearing. Wrong masks can drop events, repeatedly signal stale events, or acknowledge unrelated status.
- LPIB and timer snapshot fields are timing-sensitive. Incorrect lock or readback masks can produce inconsistent stream-position reporting, which can appear as audio drift, latency jumps, or underrun diagnostics.
- Clock-gating, audio enable, keepalive, and endpoint status fields may be invalid while the display/audio block is power-gated or reset.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.1.0 audio behavior:

- Build AMDGPU display support with DCN 4.1.0 enabled. Missing or renamed macros should fail in DCN 4.0.1/DCN 4.1.0 resource, DMUB, IRQ, GPIO, clock-manager, or audio register-table construction.
- Mechanically verify every included field has exactly one shift and one mask, while allowing the two boundary exceptions: `SPEAKER_ALLOCATION__SHIFT` is immediately before this range, and `AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS__STREAM_FORMATS_MASK` is immediately after it.
- Diff this slice against AMD's authoritative DCN 4.1.0 register database and adjacent generated ASIC headers where layout compatibility is expected.
- Exercise HDMI and DisplayPort audio on output endpoint 7 where hardware routing can expose it: hotplug, modeset, stream enable/disable, HBR formats, channel-count changes, speaker allocation, IEC channel status, ELD/sink descriptor reporting, and suspend/resume.
- Exercise input endpoints 0-7 where supported: converter format changes, channel/stream ID programming, digital converter flags, rate/size capability reads, multichannel enable/mute/channel IDs, input activity transitions, infoframe validity, and unsolicited-response events.
- Read LPIB and timer snapshots during active streams and across pause/resume to catch stale locks, wrap-count errors, or inconsistent position reporting.
- Monitor kernel logs, audio userspace enumeration, hotplug events, audio interrupt counters, sink capability dumps, and hardware traces for invalid descriptors, stuck status bits, missed unsolicited responses, audio dropouts, incorrect channel mapping, or resume-only failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of output endpoint 7 pin-control metadata, including the `SPEAKER_ALLOCATION__SHIFT` line for `CHANNEL_SPEAKER`. This chunk owns the rest of output endpoint 7, complete input endpoints 0-6, and the opening converter fields for input endpoint 7. The next chunk owns the `STREAM_FORMATS` mask and the remaining input endpoint 7 input-pin/control/status fields, plus whatever generated register families follow. The final per-file research document should reconcile those adjacent chunks before making complete claims about all Azalia endpoint and input-endpoint fields in `dcn_4_1_0_sh_mask.h`.
