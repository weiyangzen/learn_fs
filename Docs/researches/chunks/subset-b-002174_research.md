# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 57439-59938

## Purpose

This chunk is a generated AMD DCN 4.1.0 shift/mask header slice for Azalia/HDA display-audio register fields. It contains C preprocessor constants only: no functions, structs, enums, storage, includes, locking, allocation, or executable algorithms. Its API surface is the generated bitfield naming contract where `REGISTER__FIELD__SHIFT` gives a field bit offset and `REGISTER__FIELD_MASK` gives the already-shifted mask used by AMD display register helpers.

The requested range contains 2,035 `#define` entries: 1,016 shift macros, 1,019 mask macros, and 411 generated comment lines. The chunk starts at an artificial boundary inside `AUDIO_DESCRIPTOR8` and ends at another artificial boundary after `AZF0ENDPOINT2_AZALIA_F0_CODEC_PIN_CONTROL_LPIB`; adjacent chunks are needed for complete per-register claims around those edges. Although the path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

## Hardware Surface

The chunk covers these Azalia/display-audio register groups:

- Generic audio descriptor tail fields for `AUDIO_DESCRIPTOR8` through `AUDIO_DESCRIPTOR13`, including maximum channels, supported frequency bitmaps, descriptor byte 2, and stereo-frequency support.
- Sink information fields in `azendpoint_sinkinfoind`: manufacturer ID, product ID, sink description length, two 32-bit port IDs, and 18 one-byte sink-description characters.
- Input and output CRC result blocks: `AZALIA_INPUT_CRC0/1_CHANNEL0-7` and `AZALIA_CRC0/1_CHANNEL0-7`, each exposing 32-bit per-channel CRC values.
- F2 input codec fields in `azinputendpoint_f2codecind`: converter format, channel/stream ID, digital converter flags, widget capabilities, supported rates/formats, pin control, pin sense, unsolicited responses, configuration defaults, multichannel enable banks, HBR, LPIB snapshots, input status, infoframe, and channel-status registers.
- F2 root/function codec fields in `azroot_f2codecind`: vendor/device/revision IDs, subordinate node counts, power state, subsystem ID bytes, converter synchronization, reset, group type, supported rates/formats, and power-state capability bits.
- Indexed stream latency/FIFO blocks `AZF0STREAM0` through `AZF0STREAM15`: FIFO size/configuration, latency counter reset, worst-case latency, cumulative latency, and cumulative request count.
- Indexed output endpoint blocks `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, and most of `AZF0ENDPOINT2`: converter capability/control, pin capability/control, audio descriptor arrays, multichannel routing, HBR/lipsync, sink info, hot-plug audio control, forced unsolicited response, default configuration, IEC-60958 channel-status overrides, output status, and LPIB state.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this range. The important exported interface is the generated macro pattern:

- `<REGISTER>__<FIELD>__SHIFT` for field least-significant bit positions.
- `<REGISTER>__<FIELD>_MASK` for masks used during read/modify/write or readback extraction.

Representative high-value field families include:

- Audio format capability fields such as `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, `DESCRIPTOR_BYTE_2`, `FORMATS`, `RATES`, `BITS_32`, `BITS_24`, `BITS_20`, `PCM`, `HDMI`, `DP`, and `HBR`.
- Stream format/programming fields such as `CHANNEL_COUNT`, `BITS_PER_SAMPLE`, `NUMBER_OF_CHANNELS`, `BASE_RATE`, `MULTIPLY`, `DIVIDE`, `STREAM_ID`, `CHANNEL_ID`, and `STRIPE_CONTROL`.
- Digital converter control fields such as `DIGEN`, `V`, `VCFG`, `PRE`, `COPY`, `NON_AUDIO`, `PRO`, `L`, `CC`, and `KEEPALIVE`.
- Pin and hot-plug fields such as `UNSOLICITED_RESPONSE_TAG`, `UNSOLICITED_RESPONSE_ENABLE`, `PRESENCE_DETECT`, `OUT_ENABLE`/`IN_ENABLE`, `CLOCK_GATING_DISABLE`, `CLOCK_ON_STATE`, and `AUDIO_ENABLED`.
- Speaker/channel fields such as `SPEAKER_ALLOCATION`, `HDMI_CONNECTION`, `DP_CONNECTION`, `EXTRA_CONNECTION_INFO`, multichannel enable/mute/channel-ID fields for channels 0-7, and `MULTICHANNEL_MODE`.
- Sink and EDID-derived identity fields such as `MANUFACTURER_ID`, `PRODUCT_ID`, `SINK_DESCRIPTION_LEN`, `PORT_ID0`, `PORT_ID1`, and packed `DESCRIPTION0-17`.
- IEC-60958 override fields for clock accuracy, word length, sampling frequency, original sampling frequency, CGMS-A, MPEG surround, and channel numbers.
- Status/diagnostic fields such as CRC values, LPIB snapshot locks, cyclic buffer wrap counts, LPIB/timer snapshot values, input activity, channel layout, infoframe validity, format change reason/response, audio enable/disable/format-changed interrupt flags, and endpoint fine-grain clock-gating response disable.

The matching `dcn_4_1_0_offset.h` supplies the indirect register indices for these names, for example `ixAZALIA_INPUT_CRC0_CHANNEL0`, `ixAZALIA_F2_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`, `ixAZF0STREAM0_AZALIA_FIFO_SIZE_CONTROL`, and `ixAZF0ENDPOINT0_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`. Endpoint index/data access ports such as `regAZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `regAZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_DATA` are also defined there.

## Control Flow

This header has no runtime control flow. Its compile-time flow is:

1. DCN401 source includes `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`.
2. Register-list macros token-paste generated offset, shift, and mask names into per-block register structures.
3. Runtime code uses generic AMD display helpers such as `REG_UPDATE`, `REG_READ`, `REG_WRITE`, `get_reg_field_value`, `set_reg_field_value`, and Azalia indexed-register helpers to read or update hardware fields.
4. For indexed Azalia endpoint or stream registers, software selects an indirect register index through an index port, then reads/writes the data port while applying the masks and shifts defined here.

The header does not encode HDA sequencing rules. Consumers still need to order converter format changes, stream/channel ID programming, multichannel routing, hot-plug audio enables, unsolicited response handling, HBR setup, LPIB snapshot locking, and status sampling according to hardware rules.

## State And Persistence Behavior

The file itself stores no state and persists nothing. It describes hardware-resident MMIO or indexed-register state whose lifetime is controlled by modesets, audio reconfiguration, hotplug, suspend/resume, GPU reset, clock gating, and ASIC reset.

The represented state includes audio capability advertisement, sink identity, stream format and stream ID, digital converter flags, channel allocation, multichannel routing, HBR/lipsync controls, hot-plug audio enable state, unsolicited response configuration, IEC-60958 channel-status overrides, LPIB/timer snapshots, CRC diagnostics, latency counters, and audio enable/format-change interrupt status.

Persistence and side effects are hardware-defined. Capability registers are often read-only descriptions; programming registers generally persist until rewritten or reset; status and interrupt fields may be read-only, sticky, self-clearing, write-one-to-clear, sampled only while clocks are ungated, or valid only while the endpoint is active. These generated masks do not communicate access type, side effects, reset values, or legal update ordering.

## Dependencies And Integration Points

- The direct dependency is the matching `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`; offset/index names and bit layouts must come from the same generated DCN 4.1.0 register database.
- `display/dc/resource/dcn401/dcn401_resource.c` includes both generated headers, defines `audio_regs_init(id)` through `AUD_COMMON_REG_LIST_RI(id)`, allocates `audio_regs[5]`, reports `num_audio = 4`, initializes audio register entries 0-4 in `dcn401_create_audio()`, and calls `dce_audio_create()`.
- The same DCN401 resource file builds `audio_shift` and `audio_mask` with `SF(AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX, AZALIA_ENDPOINT_REG_INDEX, ...)`, `SF(AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_DATA, AZALIA_ENDPOINT_REG_DATA, ...)`, and shared `AUD_COMMON_MASK_SH_LIST_BASE(...)` fields. That directly consumes some endpoint/function bitfields from this generated header; many endpoint-specific fields in this chunk are available for lower-level indexed access and diagnostics even when not all are copied into `struct dce_audio_shift/mask`.
- Shared DCE audio code in `display/dc/dce/dce_audio.c` programs Azalia hardware through `dce_aud_hw_init()`, `dce_aud_az_enable()`, `dce_aud_az_disable()`, `dce_aud_az_configure()`, and `dce_aud_wall_dto_setup()`. It relies on generated register, shift, and mask tables to set audio DTOs, function power/rate capability bits, endpoint hot-plug audio control, speaker/channel allocation, HDMI/DP connection bits, and default configuration fields.
- `display/dmub/src/dmub_dcn401.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/gpio/dcn401/hw_translate_dcn401.c`, `display/dc/gpio/dcn401/hw_factory_dcn401.c`, and `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c` include the same generated header pair, so generated-symbol consistency affects firmware mailbox support, IRQ metadata, GPIO/DDC/HPD translation, and clock setup as well as display audio.
- Enum metadata for several Azalia concepts appears in ASIC enum headers such as `soc24_enum.h`, but this shift/mask header itself only exposes numeric bit geometry, not semantic enum types.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting an adjacent hardware bit, truncating a field, decoding status incorrectly, or leaving stale bits during read/modify/write.
- The chunk boundaries are partial. Lines 57439-57443 contain only the tail of `AUDIO_DESCRIPTOR8`, whose first shift fields are in the previous chunk; lines 59937-59938 end before `AZF0ENDPOINT2_AZALIA_F0_CODEC_PIN_CONTROL_LPIB_TIMER_SNAPSHOT` and later endpoint-2 fields in the next chunk.
- Repeated instance blocks are easy to misread. `AZF0STREAM0-15` are mechanically similar, and `AZF0ENDPOINT0-2` repeat large layouts. Instance aliasing or copy/paste drift can affect only one stream or endpoint while adjacent instances still pass simple tests.
- Indexed-register access is pairing-sensitive. The correct endpoint/stream index and data ports must be used with matching `ix*` register numbers; otherwise masks from this header decode or program a different indirect register than intended.
- Status versus control fields are mixed in the same generated namespace. Fields named `*_STATUS`, `*_FLAG`, `*_MASK`, `*_RESPONSE`, `*_FORCE`, `*_ACK`, `*_VALID`, `*_LOCK`, and CRC/LPIB readbacks may have different access semantics that are not visible from the macro alone.
- Audio format and channel fields are interoperability-sensitive. Bad descriptor, supported-rate, stream-format, channel allocation, multichannel, HBR, or IEC-60958 masks can produce silent audio, wrong channel mapping, invalid sink capability advertisement, bad HBR behavior, or malformed HDMI/DP audio packets.
- Hot-plug and unsolicited response fields can affect notification behavior. Confusing enable, force, tag, payload, interrupt flag, and mask bits can cause missed audio events, repeated notifications, stale format-change status, or audio enable/disable interrupts that never clear.
- LPIB and latency fields can be timing-sensitive. Reading LPIB/timer snapshots without honoring snapshot locks and wrap counts can yield inconsistent audio position data; resetting latency counters at the wrong time can hide performance diagnostics.
- Clock-gating and power fields require sequencing. `CLOCK_GATING_DISABLE`, `CLOCK_ON_STATE`, power-state capability bits, and endpoint FGCG response controls interact with hardware availability; touching endpoint registers while clocks are gated can produce stale reads or dropped writes.

## Test Signals

Useful validation combines generated-header consistency, build coverage, and hardware audio behavior:

- Build AMDGPU display with DCN401 enabled. Missing or renamed generated macros should fail in DCN401 resource construction, shared DCE audio table setup, DMUB, IRQ, GPIO, or clock-manager compilation.
- Mechanically verify each complete register group has coherent `__SHIFT` and `_MASK` pairs, while treating `AUDIO_DESCRIPTOR8` and the endpoint-2 LPIB boundary as cross-chunk partials.
- Compare this slice with the authoritative DCN 4.1.0 register database and its paired `dcn_4_1_0_offset.h`, especially for indirect indices such as `AZF0STREAM*` and `AZF0ENDPOINT*`.
- Exercise HDMI and DP audio enumeration on DCN401 hardware across hotplug, modeset, suspend/resume, and GPU reset. Expected signals are stable audio device enumeration, correct endpoint validity, and no stale hot-plug audio state.
- Validate PCM and HBR negotiation across sample rates, bit depths, channel counts, channel allocation maps, speaker allocation, IEC-60958 channel status, and HDMI versus DP connection selection.
- Monitor unsolicited responses, audio-enabled/disabled interrupts, format-changed interrupts, input activity, and infoframe-change fields for missed, repeated, or uncleared events.
- Read back CRC, LPIB, LPIB timer snapshot, cyclic wrap count, stream FIFO/latency counters, and sink info while audio is active to catch stale reads, wrong masks, or endpoint/stream aliasing.
- Test all exposed audio endpoint instances used by DCN401 resource construction; `audio_regs[5]` is initialized while `num_audio = 4`, so diagnostics should distinguish generated register availability from the number of runtime audio objects exposed by the resource caps.

## Cross-Chunk Notes

This is one generated slice inside `dcn_4_1_0_sh_mask.h`. The previous chunk owns the beginning of `AUDIO_DESCRIPTOR8`; this chunk owns the descriptor tail, sink info, CRC/result blocks, F2 input/root codec fields, stream 0-15 latency/FIFO fields, endpoint 0 and endpoint 1, and most of endpoint 2 through LPIB. The following chunk continues endpoint 2 with LPIB timer snapshot, coding type, format change, remote keepalive, audio interrupt/status fields, endpoint FGCG, and later endpoint instances. The merge/reconciliation lane should combine adjacent chunks before making whole-file completeness claims.
