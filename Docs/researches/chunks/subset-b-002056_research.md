# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 1-2227

## Purpose

This chunk is the opening slice of AMD's generated DCN 3.5.0 shift/mask register-field header. It has no executable C logic; it publishes preprocessor constants that encode bit positions and masks for DCN 3.5.0 MMIO register fields. Driver code pairs this header with the companion `dcn_3_5_0_offset.h` register-offset header so macro-generated register tables can update or extract individual fields through AMDGPU display register helpers.

The requested range covers the license, header guard opening, and the first 2,202 `#define` entries in a 53,484-line file. Within those defines there are 1,101 `__SHIFT` macros and 1,100 `_MASK` macros. The one unpaired field in this exact slice is `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_2__IEC_60958_CS_SAMPLING_FREQUENCY_OVRRD_EN`: its shift appears at line 2,226, while its mask is just outside this chunk at line 2,228.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset used when packing, unpacking, or updating a field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or preserve the field during read-modify-write operations.

The main macro families in this range are:

- `AZCONTROLLER0_*`: HDA/Azalia controller command and response ring fields, including CORB write/read pointers, CORB control/status/size, RIRB base addresses/write pointer/control/status/size, response interrupt count, immediate command/response interfaces, immediate command busy/result-valid status, and DMA position buffer base-address fields.
- `AZALIA_F2_CODEC_PIN_CONTROL_*` and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`: function-2 sink metadata fields for manufacturer ID, product ID, sink description length, port IDs, and per-byte sink description payload.
- `AZALIA_INPUT_CRC[0-1]_CHANNEL[0-7]` and `AZALIA_CRC[0-1]_CHANNEL[0-7]`: 32-bit channel CRC capture fields for audio validation or diagnostics.
- `AZF0STREAM0` through `AZF0STREAM15`: repeated Azalia stream FIFO and latency counter fields. Each stream has FIFO min/max/latency-support fields plus reset, worst-case latency, cumulative latency, and cumulative request counters.
- `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, and `AZF0ENDPOINT2`: complete repeated endpoint field groups in this chunk, covering converter widget capabilities, supported size/rate and stream-format bitmaps, converter format, channel/stream ID, digital converter controls, GTC embedding, ramp-rate and GTC delta counters, stripe control, pin widget capabilities, pin capabilities, unsolicited response control, pin sense, widget output enable, channel/speaker allocation, HDMI/DP connection bits, audio descriptors 0-13, multichannel enable/mute/channel-ID maps, lipsync, HBR capability/enable, sink info, hot-plug control, forced unsolicited responses, configuration default, multichannel mode, IEC 60958 channel-status overrides, association info, output-active status, LPIB snapshot/LPIB/timer fields, coding type, format-change state, wireless display identification, remote keepalive, audio enable status, and audio enabled/disabled/format-changed interrupt status.
- `AZF0ENDPOINT3`: the beginning of the same endpoint pattern for endpoint 3. This chunk includes endpoint 3 converter fields, pin fields, descriptors, sink/hotplug/configuration/multichannel fields, and stops midway through IEC 60958 channel-status override 2.

Several repeated field layouts are visible. Endpoint instances 0-2 mostly carry identical shift/mask geometry, while endpoint 3 is only partially present because of the artificial line boundary. Stream instances 0-15 are also mechanically repeated, with the same FIFO and latency-counter field shapes per stream.

## Control Flow

This header has no runtime control flow. The runtime path is supplied by AMDGPU display code:

1. DCN 3.5 code includes `dcn_3_5_0_offset.h` and this shift/mask header.
2. Register-list macros token-paste symbolic register and field names into offset, shift, and mask table initializers.
3. Hardware block constructors store those tables in DCN 3.5 display objects, including DMUB service, DIO/audio-related blocks, stream encoders, resource-pool components, and other register-helper users.
4. Runtime paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers use the numeric shift/mask constants to touch only the intended MMIO bits.

The macros do not encode sequencing rules. Consumers must still order HDA ring setup, DMA buffer base programming, immediate command submission, audio endpoint configuration, hotplug handling, stream format changes, interrupt acknowledgement, suspend/resume restore, and power/clock transitions correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware state in DCN 3.5.0 Azalia/audio registers:

- Command ring and response ring state for CORB/RIRB pointers, base addresses, DMA enable bits, ring-size selection, and memory/error/overrun interrupt controls.
- Immediate command state for codec-address, verb/payload, data/index, busy status, and result-valid status.
- DMA position buffer state and alignment-constrained base-address fields.
- Sink identity and description state derived from connected HDMI/DP audio sinks.
- Audio CRC and input CRC capture state for per-channel diagnostics.
- Per-stream FIFO sizing and latency counters for stream instances 0-15.
- Endpoint codec/converter state for advertised widget capabilities, supported rates/formats, converter format, stream/channel binding, digital-converter options, and GTC timing fields.
- Endpoint pin-control state for pin capabilities, output enable, HDMI/DP connection metadata, channel/speaker allocation, EDID-like audio descriptors, HBR, lipsync, multichannel mapping, sink info, hotplug/audio-enabled state, unsolicited responses, IEC 60958 channel-status override fields, LPIB snapshots, format-change signaling, remote keepalive, and endpoint interrupt status bits.

Persistence is hardware-defined. Configuration fields generally survive until modeset reprogramming, audio stream teardown, power-gating, suspend/resume, driver reset, or ASIC reset. Status and interrupt fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while related display/audio clocks and power domains are active. This generated header does not indicate access semantics; consuming code and the hardware register specification must supply that knowledge.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which provides the matching MMIO offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which directly includes `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h` when initializing DCN 3.5 DMUB register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.h`, whose `DMUB_DCN35_REGS()` and `DMUB_DCN35_FIELDS()` macros define register, shift, and mask table shapes for DCN 3.5 DMUB access.
- DCN 3.5 resource, DIO, stream-encoder, IRQ, and audio paths that consume generated register constants indirectly through AMD display register-list macros.

The most direct behavioral integration from this specific chunk is HDMI/DP audio support: HDA command/response plumbing, sink identity and audio capability reporting, per-stream latency/FIFO diagnostics, endpoint format programming, HBR and multichannel audio setup, hotplug/audio enablement, and endpoint audio interrupt status.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong mask or shift can compile cleanly while writing the wrong MMIO bit, corrupting an adjacent field, failing to enable audio, or missing an interrupt.
- The file is generated metadata. Manual edits can diverge from the authoritative AMD register database, the matching offset header, firmware expectations, and silicon documentation.
- The endpoint and stream families are highly repetitive. Copy/paste or generator errors can affect only one instance, so endpoint 0 working does not prove endpoint 1-3 or stream 0-15 are correct.
- The chunk boundary is artificial. Endpoint 3's `IEC_60958_CS_SAMPLING_FREQUENCY_OVRRD_EN` mask is outside this range, and the rest of endpoint 3 plus later endpoint/register families continue in later chunks.
- Ring and DMA address fields include unimplemented/alignment bits. Incorrect masks around low address bits can program invalid CORB/RIRB/DMA position buffer addresses or fail on systems with stricter address alignment.
- Interrupt/status fields are side-effect-sensitive. Confusing flag, mask, type, ack, or response fields can cause stuck audio hotplug state, missed format-change notifications, interrupt storms, or stale audio-enable state.
- Audio format and channel-status fields are interoperability-sensitive. Wrong converter format, IEC 60958 override, HBR, multichannel, speaker allocation, or descriptor masks can produce silent HDMI/DP audio, channel swaps, incorrect sample-rate reporting, or receiver-specific failures.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support with DCN 3.5 enabled. Missing or renamed macros should fail in DCN35 DMUB register initialization and any DCN35 display/audio register-table construction that references these fields.
- Mechanically verify that every field in lines 1-2227 has a matching `__SHIFT` and `_MASK` pair where expected, while allowing the known artificial boundary exception for `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_2__IEC_60958_CS_SAMPLING_FREQUENCY_OVRRD_EN`.
- Diff this range against AMD's authoritative DCN 3.5.0 register database and nearby generated headers such as `dcn_3_5_1_sh_mask.h` or earlier DCN 3.x variants where Azalia register layouts are expected to be compatible.
- Exercise HDMI and DisplayPort audio on DCN 3.5 hardware across plug/unplug, modeset, suspend/resume, stream enable/disable, format changes, multichannel LPCM, HBR/compressed formats, and audio sink changes.
- Validate CORB/RIRB and immediate command paths by checking codec verb responses, busy/result-valid behavior, response-overrun handling, and ring pointer reset behavior.
- Watch kernel logs and display/audio diagnostics for missed audio enabled/disabled interrupts, format-change interrupt storms, HDA command timeouts, stale LPIB snapshots, CRC mismatches, bad sink descriptor parsing, wrong channel allocation, silent audio after hotplug, and resume-only HDMI/DP audio failures.

## Cross-Chunk Notes

This is the first chunk of `dcn_3_5_0_sh_mask.h`. Later chunks continue endpoint 3 from the IEC 60958 channel-status override fields and then cover the rest of the DCN 3.5.0 display, link, audio, hub, timing, compression, and DMUB register-field namespace. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.5.0 registers or all Azalia endpoint instances.
