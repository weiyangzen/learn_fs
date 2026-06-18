# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002087`: lines 1-2215, `Docs/researches/chunks/subset-b-002087_research.md`
- `subset-b-002088`: lines 2216-4415, `Docs/researches/chunks/subset-b-002088_research.md`
- `subset-b-002089`: lines 4416-6585, `Docs/researches/chunks/subset-b-002089_research.md`
- `subset-b-002090`: lines 6586-8803, `Docs/researches/chunks/subset-b-002090_research.md`
- `subset-b-002091`: lines 8804-11021, `Docs/researches/chunks/subset-b-002091_research.md`
- `subset-b-002092`: lines 11022-13240, `Docs/researches/chunks/subset-b-002092_research.md`
- `subset-b-002093`: lines 13241-15458, `Docs/researches/chunks/subset-b-002093_research.md`
- `subset-b-002094`: lines 15459-17678, `Docs/researches/chunks/subset-b-002094_research.md`
- `subset-b-002095`: lines 17679-19896, `Docs/researches/chunks/subset-b-002095_research.md`
- `subset-b-002096`: lines 19897-22113, `Docs/researches/chunks/subset-b-002096_research.md`
- `subset-b-002097`: lines 22114-24331, `Docs/researches/chunks/subset-b-002097_research.md`
- `subset-b-002098`: lines 24332-26548, `Docs/researches/chunks/subset-b-002098_research.md`
- `subset-b-002099`: lines 26549-28768, `Docs/researches/chunks/subset-b-002099_research.md`
- `subset-b-002100`: lines 28769-30986, `Docs/researches/chunks/subset-b-002100_research.md`
- `subset-b-002101`: lines 30987-33204, `Docs/researches/chunks/subset-b-002101_research.md`
- `subset-b-002102`: lines 33205-35422, `Docs/researches/chunks/subset-b-002102_research.md`
- `subset-b-002103`: lines 35423-37642, `Docs/researches/chunks/subset-b-002103_research.md`
- `subset-b-002104`: lines 37643-39861, `Docs/researches/chunks/subset-b-002104_research.md`
- `subset-b-002105`: lines 39862-42078, `Docs/researches/chunks/subset-b-002105_research.md`
- `subset-b-002106`: lines 42079-44295, `Docs/researches/chunks/subset-b-002106_research.md`
- `subset-b-002107`: lines 44296-46513, `Docs/researches/chunks/subset-b-002107_research.md`
- `subset-b-002108`: lines 46514-48830, `Docs/researches/chunks/subset-b-002108_research.md`
- `subset-b-002109`: lines 48831-51051, `Docs/researches/chunks/subset-b-002109_research.md`
- `subset-b-002110`: lines 51052-53401, `Docs/researches/chunks/subset-b-002110_research.md`
- `subset-b-002111`: lines 53402-53464, `Docs/researches/chunks/subset-b-002111_research.md`

## Chunk Research

### subset-b-002087: lines 1-2215

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 1-2215

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata. It contains no executable driver logic; it exposes C preprocessor constants that describe bit shifts and masks for hardware register fields. Consumers combine these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with matching register offsets from `dcn_3_5_1_offset.h` and AMD display register helpers to read, write, update, and preserve fields in DCN 3.5.1 MMIO registers.

The requested range covers the beginning of `dcn_3_5_1_sh_mask.h`: license/header guard, Azalia controller command/response DMA ring fields, immediate command/response fields, DMA position buffer fields, top-level sink identity/description fields, Azalia input/output CRC fields, Azalia stream latency/FIFO counters for streams 0-15, complete Azalia F0 endpoint field layouts for endpoints 0-2, and the start of endpoint 3 through `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4`.

Although this source tree is under a local `ceph-client` mirror, this file is AMD GPU display/audio hardware metadata. It has no Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, callbacks, locks, allocation paths, or direct I/O operations in this chunk. Its only exported interface is a generated macro namespace:

- `REGISTER__FIELD__SHIFT`: bit offset of `FIELD` inside `REGISTER`.
- `REGISTER__FIELD_MASK`: bit mask for the same field.

Major macro families in lines 1-2215:

- `AZCONTROLLER0_*`: HDA/Azalia controller CORB and RIRB queue fields, response interrupt count/control/status fields, immediate command output/input/status fields, and DMA position buffer base-address fields.
- `AZALIA_F2_CODEC_PIN_CONTROL_*` and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`: sink manufacturer/product IDs, sink description length, two 32-bit port IDs, and byte-sized sink description storage.
- `AZALIA_INPUT_CRC*` and `AZALIA_CRC*`: full 32-bit CRC fields for channels 0-7 across CRC groups 0 and 1.
- `AZF0STREAM0` through `AZF0STREAM15`: per-stream FIFO sizing fields (`MIN_FIFO_SIZE`, `MAX_FIFO_SIZE`, `MAX_LATENCY_SUPPORT`) and latency instrumentation (`AZALIA_LATENCY_COUNTER_RESET`, worst-case latency, cumulative latency, cumulative request count).
- `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, and `AZF0ENDPOINT2`: repeated endpoint converter and pin-control field layouts, including widget capabilities, converter format, channel/stream ID, digital converter control, supported formats/rates, stripe/ramp/GTC embedding controls, pin capabilities, unsolicited response controls, speaker/channel allocation, audio descriptors 0-13, multichannel enables, lipsync/HBR responses, sink info registers, hot-plug/audio enable control, configuration default response, IEC 60958 channel-status overrides, LPIB snapshots, coding type, format-change status, remote keepalive, and audio enabled/disabled/format-changed interrupt status.
- `AZF0ENDPOINT3`: same repeated endpoint layout begins at line 1814 but this chunk ends in the middle of the channel-status override group, at `CODEC_CS_OVERRIDE_4`.

The macro names are intentionally long because they encode the hardware block, instance, register, field, and generated constant kind. They are usually consumed through token-pasting helpers rather than typed directly in ordinary C code.

## Control Flow

This header has no runtime control flow. The operational flow is supplied by the AMD display and audio code that includes this generated metadata:

1. A DCN 3.5.1 source file includes `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`.
2. Register-list macros token-paste register and field names into offset, shift, and mask tables. For example, DCN 3.5.1 DMUB initialization uses `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` after including this header.
3. Runtime paths call helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_READ`, `AZ_REG_READ`, and `AZ_REG_WRITE`. Those helpers use the generated shift/mask constants to isolate a field and preserve unrelated bits.
4. Sequencing rules are entirely in the consumers. This chunk only defines where a field lives; it does not encode whether a field is read-only, write-one-to-clear, self-clearing, sticky, interrupt-status, or safe to touch while the audio/display block is clock-gated.

For Azalia endpoint access specifically, the audio code writes an endpoint register index and then reads or writes the indexed endpoint data register. The endpoint fields in this chunk define the bit layouts of the indexed endpoint data values.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes MMIO-backed GPU display/audio state.

Represented hardware state includes HDA CORB/RIRB queue pointers and enables, immediate codec command status, DMA position-buffer addresses, monitor/sink identity bytes, audio CRC observations, stream latency counters, converter sample/channel configuration, digital audio status bits, HDMI/DP speaker allocation, supported audio descriptors, hot-plug/audio enable state, lipsync/HBR response state, IEC 60958 channel-status overrides, LPIB snapshots, format-change status, and endpoint audio interrupt flags.

Persistence is hardware-defined. Configuration fields generally last until driver reprogramming, display/audio disable, block reset, power gating, suspend/resume, or ASIC reset. Counter/status fields may be read-only, clear-on-write, sticky, or self-clearing depending on the underlying register. Since the generated macros are untyped constants, the consuming driver must know ordering constraints for enabling audio, updating sink info, programming descriptors, toggling hot-plug/audio enable, clearing interrupt flags, and reading latency/CRC diagnostics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must match `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides the corresponding register offsets and base-index selectors.

Representative integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which includes this header and builds DCN 3.5.1 shift/mask tables with `FD_MASK` and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which includes this header while constructing the DCN 3.5.1 resource pool and hardware block register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`, which includes this header for generated interrupt register metadata used by the DCN 3.5.1 IRQ service.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`, whose `AUD_COMMON_REG_LIST` uses `SRI(AZALIA_F0_CODEC_ENDPOINT_INDEX, AZF0ENDPOINT, id)` and `SRI(AZALIA_F0_CODEC_ENDPOINT_DATA, AZF0ENDPOINT, id)` to bind endpoint instances to audio objects.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`, which programs endpoint-indexed Azalia fields for HBR capability, lipsync, hot-plug/audio enable, speaker/channel allocation, audio descriptors, sink info, configuration defaults, and supported stream formats.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These macros are untyped constants, so a wrong bit position can compile cleanly while silently writing the wrong hardware field.
- The Azalia controller fields drive command and response DMA rings. Incorrect CORB/RIRB pointer, reset, DMA enable, size, or interrupt masks can break codec command submission, lose responses, or cause audio initialization timeouts.
- Immediate command fields have busy/result-valid semantics. Wrong masks can make polling loops believe a command is complete too early or never complete.
- Sink metadata and audio descriptor fields feed HDMI/DP audio capability exposure. Incorrect masks can advertise wrong manufacturer/product data, speaker layout, supported rates, channel counts, HBR capability, or ELD-like sink description data to the audio stack.
- Repeated endpoint blocks are copy-sensitive. Endpoints 0-3 have nearly identical field layouts; an instance-specific typo may only affect one display/audio output.
- Stream latency and CRC fields are diagnostic. Bad masks may not break basic audio playback but can hide FIFO sizing, latency, CRC, or underrun-style problems.
- Hot-plug, unsolicited response, audio enable, audio disable, and format-change interrupt/status fields are ordering-sensitive. Incorrect masks can cause missed audio events, stale status, interrupt storms, or lost format-change acknowledgements.
- The chunk boundary is artificial. It ends inside endpoint 3 channel-status override fields, so later chunk research is required before making complete file-level claims about all endpoint 3 fields or endpoints 4-7.

## Test Signals

Useful validation signals combine generated-header consistency checks with hardware/audio behavior:

- Build AMDGPU/DC with DCN 3.5.1 enabled; missing or renamed macros should fail in DCN 3.5.1 DMUB, IRQ, resource, and audio register-table construction.
- Mechanically verify that every field in lines 1-2215 has the expected `__SHIFT` and `_MASK` pair, and that each mask aligns with its shift and apparent field width.
- Diff this chunk against AMD's authoritative DCN 3.5.1 register database and neighboring generated headers where identical Azalia layouts are expected.
- Exercise HDMI and DisplayPort audio bring-up across multiple connectors/endpoints, including hotplug, modeset, audio enable/disable, suspend/resume, and display power-gating transitions.
- Validate codec command paths that use CORB/RIRB and immediate commands by checking for command timeouts, invalid responses, or stuck busy/result-valid bits.
- Test EDID/ELD-driven audio configuration: supported rates, bit depths, channel counts, speaker allocation, HBR exposure, sink description bytes, manufacturer/product IDs, and port IDs.
- Exercise format changes while audio is active and watch audio enabled/disabled/format-changed interrupt status, unsolicited response behavior, and kernel logs for missed or repeated events.
- Read diagnostics for CRC, latency counter reset, worst-case latency, cumulative latency, and cumulative request counts across multiple streams.
- Listen for user-visible failures: no HDMI/DP audio device, wrong channel mapping, missing multichannel formats, HBR failures, audio dropouts, lipsync anomalies, stuck hotplug/audio enable state, or regressions limited to a single endpoint.

## Cross-Chunk Notes

This is the first chunk of `dcn_3_5_1_sh_mask.h`. Later chunks continue endpoint 3 after `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4`, then cover the rest of the generated DCN 3.5.1 register field map. The final per-file document should merge adjacent chunks before making complete claims about all Azalia endpoints, all audio interrupt fields, or the full DCN 3.5.1 mask/shift surface.

### subset-b-002088: lines 2216-4415

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 2216-4415

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata. It contains no executable driver logic; it exports C preprocessor constants that describe bit shifts and masks for Azalia/HD Audio codec endpoint registers. The constants follow the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming pattern and are consumed with the matching DCN 3.5.1 offset header and AMD display register helper macros.

The requested range covers the tail of output endpoint 3, full output endpoints 4 through 7, full input endpoint 0, and the beginning of input endpoint 1. These endpoint blocks describe HDMI/DisplayPort audio converter and pin-widget capabilities, stream format fields, channel/stream ID assignment, IEC 60958 channel-status overrides, sink/audio descriptor data, HBR, unsolicited responses, LPIB snapshots, hot-plug/audio state, GTC timestamp embedding, multichannel routing, and input-infoframe/activity state.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or callbacks in this range. The exported interface is entirely generated macros:

- `AZF0ENDPOINT*_...__FIELD__SHIFT`: bit position for an Azalia output endpoint field.
- `AZF0ENDPOINT*_...__FIELD_MASK`: bit mask for the same output endpoint field.
- `AZF0INPUTENDPOINT*_...__FIELD__SHIFT`: bit position for an Azalia input endpoint field.
- `AZF0INPUTENDPOINT*_...__FIELD_MASK`: bit mask for the same input endpoint field.

Major macro families in this chunk:

- Endpoint 3 tail: `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4` mask tail, `CODEC_CS_OVERRIDE_5` through `8`, pin association, digital-output active status, LPIB snapshot registers, coding type, format-change state/ack, wireless display identification, remote keepalive, audio enable status, and audio enabled/disabled/format-changed interrupt status fields.
- Output endpoints 4-7: repeated full codec converter and pin-control field maps for each endpoint instance. The converter side includes audio-widget capabilities, converter format, channel/stream ID, digital converter flags, supported stream formats, supported size/rates, stripe control, ramp rate, GTC embedding controls, and GTC counter delta/min/max registers.
- Output endpoint pin widgets: repeated audio-widget and pin-capability fields, unsolicited response enable/tag and force payload, pin sense, output widget enable, speaker/channel allocation, SAD/audio descriptors 0-13, sink information 0-8, HBR, lipsync, hot-plug control, multichannel mode, multichannel enables for channels 0-7, response configuration defaults, IEC 60958 channel-status override words 0-8, LPIB snapshots, coding type, format-change control, wireless display identification, remote keepalive, and audio status/interrupt fields.
- Input endpoint 0: input converter capabilities and stream-format controls, input pin capabilities, unsolicited response controls, input pin sense with presence detect, input widget enable, multichannel input routing, HBR, channel allocation, hot-plug/audio-enable state, response configuration defaults, LPIB snapshots, input status/control, and input infoframe fields.
- Input endpoint 1 boundary: only the start of `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` is present; this chunk includes all fourteen shift definitions and only the first six mask definitions before the requested range ends.

The range is highly repetitive by endpoint instance. Output endpoints 4, 5, 6, and 7 each contribute the same endpoint-local register groups with instance-specific macro prefixes, while input endpoint 0 has a related but input-specific register layout.

## Control Flow

This header has no runtime control flow. It becomes part of runtime behavior only when included by AMD display code that constructs register metadata tables:

1. DCN 3.5.1 display modules include `dcn_3_5_1_sh_mask.h` together with the corresponding offset header.
2. Register-list macros token-paste register and field names into mask/shift tables.
3. Runtime code calls helper operations such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and related AMD display register macros. Those helpers use these constants to isolate a field, shift values into position, and preserve unrelated bits during read-modify-write operations.
4. Hardware sequencing, ownership, access ordering, and status interpretation live in the consuming driver and firmware paths. This generated header only states bit locations.

For this chunk, the implied runtime flows are audio endpoint discovery/configuration, HDMI/DP audio format programming, stream/channel mapping, speaker and SAD propagation, HBR enablement, audio hot-plug and enable/disable event handling, input-audio status reporting, GTC audio timestamp embedding, LPIB snapshot reading, and unsolicited response programming.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU display/audio state.

Represented hardware state includes per-endpoint converter format and stream IDs, digital converter flags such as `DIGEN`, validity/copy/non-audio/pro mode bits, endpoint capability fields, sink descriptor bytes, speaker allocation, IEC 60958 channel status, multichannel enable/mute/channel IDs, hot-plug clock/audio enable state, remote keepalive, LPIB position snapshots, audio enable and format-change status, GTC timing deltas, input activity/channel layout, and audio infoframe validity.

Persistence is determined by the Azalia/DCN hardware block. Capability fields are effectively hardware-described constants. Control fields usually persist until reprogrammed, modeset, suspend/resume, power gating, audio block reset, or ASIC reset. Status, interrupt, force, ack, and snapshot fields may be sticky, self-clearing, read-only, write-one-to-clear, or latched depending on the register semantics supplied by the hardware specification and consuming code.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides the corresponding MMIO offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h`, which contains symbolic enum values for many Azalia input endpoint fields such as audio-widget capabilities, pin capabilities, HBR capability, and pin/control options.
- AMD display register helper infrastructure that consumes generated shift/mask constants through `REG_*`, `SF`, `SRI`, and related table-building macros.

Representative integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which includes `dcn_3_5_1_sh_mask.h` as part of the DCN 3.5.1 register interface.
- AMD display audio paths that program Azalia codec converter and pin-widget state for HDMI/DP audio, including converter format, channel/stream IDs, digital converter state, channel allocation, speaker allocation, SAD data, HBR, and IEC 60958 channel status.
- Display hotplug and interrupt service paths that depend on audio enabled/disabled/format-changed status fields and unsolicited-response enable/force fields.
- Diagnostics or debug paths that read LPIB snapshots, GTC counter deltas, audio enable state, sink-info fields, input activity, and input infoframe fields.

The later merge lane should combine this with adjacent chunks for the complete Azalia endpoint map. This chunk starts in the middle of endpoint 3 and ends inside the input endpoint 1 audio-widget capability register.

## Risks And Edge Cases

- Shift/mask drift is the main risk. These are untyped constants, so an incorrect bit position can compile while silently targeting the wrong hardware bit.
- Repeated endpoint blocks are copy-sensitive. Output endpoints 4-7 are near-identical; a single instance-specific typo can affect only one display/audio endpoint and be missed by basic single-monitor testing.
- The chunk begins at masks for `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4` without the matching shifts in this range. Adjacent chunk data is needed to validate endpoint 3 completely.
- The chunk ends after only the first six masks for `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`. Adjacent chunk data is needed to validate input endpoint 1 completely.
- Audio format fields are compact and interdependent. Wrong masks for channel count, sample base divisor/multiple/rate, bits per sample, stream type, stream ID, or channel ID can produce silent audio, wrong channel mapping, or intermittent format negotiation failures.
- IEC 60958 channel-status override and SAD/sink-info fields affect what downstream receivers see. Bad masks can advertise incorrect sample rates, channel counts, coding types, speaker allocations, copyright/category bits, or validity flags.
- Interrupt and unsolicited-response bits are sensitive. Incorrect flag/mask/type, ack-enable, tag, enable, or force-payload metadata can cause missed audio events, stale format-change notifications, or unsolicited response storms.
- LPIB and timer snapshot fields are full-width or latch-sensitive. Consumers must apply hardware-specified locking/snapshot ordering; the macros do not encode ordering rules.
- Hot-plug and clock-gating fields can be unsafe or ineffective if accessed while the Azalia block is power-gated, reset, or not clocked.
- GTC embedding and counter-delta fields cross audio/video timing domains. Wrong field locations can break timestamp embedding or make synchronization diagnostics misleading.

## Test Signals

Useful validation signals are a combination of generated-header checks and hardware behavior:

- Build AMDGPU/DC with DCN 3.5.1 support enabled; missing, renamed, or malformed macros should fail in register table construction or direct register helper use.
- Mechanically verify that every complete register group in lines 2216-4415 has paired `__SHIFT` and `_MASK` definitions and that masks align with shifts and expected field widths. Exclude the known artificial boundaries at endpoint 3 `CODEC_CS_OVERRIDE_4` and input endpoint 1 audio-widget capabilities until adjacent chunks are merged.
- Diff this chunk against AMD's authoritative DCN 3.5.1 register source and nearby generated generations, especially `dcn_3_5_0_sh_mask.h`, where endpoint layouts are expected to remain compatible.
- Exercise HDMI and DisplayPort audio on endpoints corresponding to Azalia output endpoints 4-7: hotplug, audio enable/disable, stream start/stop, sample-rate changes, bit-depth changes, stereo and multichannel layouts, HBR formats, and suspend/resume.
- Verify receiver-visible data: EDID/SAD-derived audio descriptors, speaker/channel allocation, IEC 60958 channel-status fields, coding type, sink info, lipsync, and wireless display identification where applicable.
- Exercise unsolicited response handling and audio format-change paths, watching for missed events, repeated interrupts, stale status bits, and wrong reason/response fields.
- Read LPIB and LPIB timer snapshots during playback/capture and check for sane monotonic position reporting under wrap conditions.
- For input endpoint 0, test input activity detection, channel layout reporting, input infoframe validity, channel allocation, presence detect, HBR capability/enable, and multichannel input routing.
- Monitor kernel logs and display/audio diagnostics for audio dropouts, wrong channel mapping, hotplug regressions, DPCD/EDID audio inconsistencies, stuck audio interrupts, and suspend/resume audio failures.

## Cross-Chunk Notes

Previous chunks own the earlier Azalia endpoint 3 definitions, including the missing shifts for the `CODEC_CS_OVERRIDE_4` masks that open this range. Later chunks own the rest of input endpoint 1 and likely additional input endpoint/register definitions. The final per-file report should merge adjacent chunks before making complete claims about all DCN 3.5.1 Azalia endpoints or the full `dcn_3_5_1_sh_mask.h` register field map.

### subset-b-002089: lines 4416-6585

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 4416-6585

## Purpose

This chunk is generated AMD DCN 3.5.1 register-field metadata. It contains no executable driver logic; it exports preprocessor constants that describe bit positions and masks for MMIO register fields. Consumers combine these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with the matching `dcn_3_5_1_offset.h` register offsets to populate AMD display register tables.

The requested range starts in the middle of the `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` mask group, then covers the rest of Azalia input endpoints 1 through 7, audio descriptor capability registers 0 through 13, immediate-command index/data windows for Azalia endpoint 0 and input endpoint 0, and a set of DCCG clock-generation fields through the beginning of `OTG1_PIXEL_RATE_CNTL`. Although the path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or direct I/O operations in this chunk. The interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: bit offset of a hardware field.
- `REGISTER__FIELD_MASK`: bit mask for the same hardware field.

Major macro families in this chunk:

- `AZF0INPUTENDPOINT1` through `AZF0INPUTENDPOINT7`: HDA/Azalia HDMI/DP input endpoint converter and pin-control fields. Each endpoint repeats fields for audio-widget capabilities, converter format, channel/stream ID, digital converter control, supported stream formats and rates, pin capabilities, unsolicited responses, pin sense, widget enable, multichannel enable/mute/channel ID for channels 0-7, HBR capability/enable, channel allocation, hot-plug/audio enable, forced unsolicited response payloads, configuration defaults, LPIB snapshots, input activity/channel layout status, and infoframe contents.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`: audio SAD-style descriptor payload fields, with channel count, format code, sample-rate flags, byte 3 fields, and the descriptor update bit.
- `AZENDPOINT0_AZENDPOINT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_*` and `AZINPUTENDPOINT0_AZENDPOINT_IMMEDIATE_COMMAND_INPUT_INTERFACE_*`: immediate command output/input interface index and data fields, exposing the full 32-bit data/register-index windows.
- `PHYPLLA_PIXCLK_RESYNC_CNTL` through `PHYPLLE_PIXCLK_RESYNC_CNTL`: per-PHY pixel clock resynchronization enable, deep-color control, pixel-clock enable, and double-rate enable fields.
- `DP_DTO_DBUF_EN`, `DSCCLK*_DTO_PARAM`, `DPREFCLK_CGTT_BLK_CTRL_REG`, `REFCLK_CGTT_BLK_CTRL_REG`, `DISPCLK_CGTT_BLK_CTRL_REG`, `SOCCLK_CGTT_BLK_CTRL_REG`, and `SYMCLK_CGTT_BLK_CTRL_REG`: DTO enable/selection and clock-gating turn-on/turn-off delay fields.
- `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DCCG_GATE_DISABLE_CNTL4`, and `DCCG_GATE_DISABLE_CNTL5`: gate-disable fields for DISPCLK, SOCCLK, DPREFCLK, DPPCLK, DSCCLK, AOMCLK, DSI/BYTE/ESC clocks, SYMCLK front-end/full clocks, HDMI character clocks, DPIA symbol clocks, DTBCLK_P pipes, and DP stream clocks.
- `DPSTREAMCLK_CNTL`, `SYMCLK32_SE_CNTL`, `SYMCLK32_LE_CNTL`, `DTBCLK_P_CNTL`, `DCCG_DS_*`, `DPREFCLK_CNTL`, `DCCG_GTC_*`, `MILLISECOND_TIME_BASE_DIV`, `MICROSECOND_TIME_BASE_DIV`, and `DISPCLK_FREQ_CHANGE_CNTL`: display clock source selection, enable, fractional divider, global-timer, deep-sleep, and time-base fields.
- `DCCG_PERFMON_CNTL` and `DCCG_PERFMON_CNTL2`: display clock generator perfmon enable, mode, OTG selection, and pulse-divider fields.
- `OTG0_PIXEL_RATE_CNTL`, `DP_DTO0_PHASE`, `DP_DTO0_MODULO`, `OTG0_PHYPLL_PIXEL_RATE_CNTL`, and the start of `OTG1_PIXEL_RATE_CNTL`: timing-generator pixel-rate source, DTO enable/status, add/drop-pixel control, DTO source selection, DIO FIFO error reporting, and 32-bit DP DTO phase/modulo fields.

## Control Flow

This header has no runtime control flow. Runtime behavior appears only after the macros are token-pasted into register tables and used by display helper code:

1. DCN 3.5.1 modules include `dcn_3_5_1_sh_mask.h` with `dcn_3_5_1_offset.h`.
2. Resource and block-specific register-list macros instantiate shift/mask tables. For example, `dcn351_resource.c` builds `dce_hwseq_shift`/`dce_hwseq_mask` entries from `DCCG_GATE_DISABLE_CNTL2`, `DCCG_GATE_DISABLE_CNTL4`, and `DCCG_GATE_DISABLE_CNTL5` fields, while shared DCCG tables in `dcn32_dccg.h` consume `OTG*_PIXEL_RATE_CNTL`, `DPSTREAMCLK_CNTL`, `OTG_PIXEL_RATE_DIV`, `DTBCLK_P_CNTL`, and related DCCG fields.
3. Runtime display paths call helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_WRITE`, `REG_WAIT`, `REG_GET`, and `REG_SET`. These helpers use the generated shift/mask constants to read or modify individual hardware fields while preserving unrelated bits.
4. The DCCG path programs DTO phase/modulo values, enables `DTBCLK_DTO_ENABLE`, waits for `DTBCLKDTO_ENABLE_STATUS`, selects `PIPE_DTO_SRC_SEL`, and toggles `OTG_ADD_PIXEL`/`OTG_DROP_PIXEL`. This sequencing comes from `dcn32_dccg.c`; the header only provides field geometry.
5. Audio endpoint paths use Azalia endpoint index/data windows and audio register tables to discover capabilities, program converter format/channel mapping, publish audio descriptors, observe input activity, and manage hot-plug/audio enable state. The field macros do not encode HDA verb semantics by themselves.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in files or memory. It describes MMIO-backed GPU display state.

Represented hardware state includes per-endpoint audio capabilities and controls, audio infoframe/descriptor data, LPIB snapshot and timer values, input activity status, HBR enablement, endpoint hot-plug/audio enable state, DCCG clock-gating overrides, pixel-clock resync configuration, DP/DTB DTO phase and modulo values, pixel-rate source selection, add/drop-pixel one-shot controls, DIO FIFO error counters, display time-base dividers, and DCCG perfmon controls.

Persistence is hardware-defined. Configuration fields usually retain values until display modeset reprogramming, block reset, power gating, suspend/resume, or ASIC reset. Status, counter, update, hot-plug, forced-response, and error fields can be read-only, sticky, write-one-to-clear, self-clearing, or edge-triggered depending on the register. Because the header is untyped, consuming code must know the correct access ordering and whether a field is safe while the audio, DIO, PHY, OTG, or DCCG block is clock gated.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h` for the corresponding MMIO offsets and base indices.
- AMD display register helper infrastructure that consumes generated shift/mask tables through `REG_*`, `SF`, `SRI`, `SRII`, `DCCG_SF`, `DCCG_SFII`, `HWS_SF`, and related token-pasting macros.

Representative integration points in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c` includes this header and fills DCN 3.5.1 register, shift, and mask structures. The visible consumers in this range include DCCG gate-disable fields, `AZALIA_AUDIO_DTO`, and clock/power-management metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c` include the same DCN 3.5.1 header pair, so generated-field correctness is part of the wider ASIC support contract even where this chunk's fields are not their main focus.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn32/dcn32_dccg.h` maps `OTG*_PIXEL_RATE_CNTL`, `DPSTREAMCLK_CNTL`, `SYMCLK32_*`, `DTBCLK_P_CNTL`, and DTO fields into DCCG masks/shifts; `dcn32_dccg.c` then programs DTBCLK DTOs, DP stream clocks, and add/drop-pixel controls using those tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_clock_source.h` and `dce_clock_source.c` integrate `DP_DTO0_PHASE`, `DP_DTO0_MODULO`, `OTG0_PIXEL_RATE_CNTL`, and `OTG0_PHYPLL_PIXEL_RATE_CNTL` style fields into DP DTO and pixel-clock source programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines the shared Azalia audio register-table pattern for endpoint index/data access and codec capability fields. This chunk's input-endpoint and audio-descriptor definitions provide the lower-level field map for the hardware audio endpoint area.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc.h` has debug/trace storage for DTO enable/source/divider, add/drop-pixel, and DP DTO phase state, matching fields represented by this chunk.

## Risks And Edge Cases

- Shift/mask drift is the main risk. These are untyped constants, so an incorrect mask can compile cleanly while modifying the wrong hardware bits.
- The chunk starts and ends at artificial boundaries. It begins after the first endpoint-1 widget-capability shifts and ends before the rest of `OTG1_PIXEL_RATE_CNTL` and later OTG/DTO instances; adjacent chunks are needed for complete file-level conclusions.
- Azalia endpoint blocks are copy-sensitive. Endpoints 1-7 repeat near-identical converter and pin-control layouts; a single instance typo can affect only one display audio endpoint, making failures appear connector-specific.
- Audio-format fields directly affect HDMI/DP audio behavior. Bad converter format, channel/stream ID, digital converter, HBR, channel allocation, infoframe, or descriptor masks can cause missing audio, wrong channel mapping, HBR failures, malformed EDID/SAD reporting, or incorrect audio hot-plug behavior.
- LPIB and snapshot fields may be timing-sensitive. Incorrect lock, buffer-wrap, position, or timer-snapshot fields can produce incorrect audio position reporting without an obvious display failure.
- DCCG and pixel-rate fields are sequencing-sensitive. The shared code enables DTOs, waits for status, then selects the DTO source; wrong `DTBCLK_DTO_ENABLE`, `DTBCLKDTO_ENABLE_STATUS`, `PIPE_DTO_SRC_SEL`, `DP_DTO*_PHASE`, or `DP_DTO*_MODULO` masks can cause blank displays, unstable pixel valid generation, or incorrect DP/HDMI timing.
- Clock-gate override fields can hide power bugs or create access hazards. Wrong `DCCG_GATE_DISABLE_*` bits can leave clocks unnecessarily on, gate a block while it is in use, or break suspend/resume and low-power transitions.
- Error and perfmon fields are diagnostic-sensitive. Bad DIO FIFO error masks or DCCG perfmon controls can make validation misleading even when normal modesets appear to work.

## Test Signals

Useful validation signals are a mix of build-time generated-header checks and hardware behavior:

- Build AMDGPU/DC with DCN 3.5.1 support enabled. Missing or renamed macros should fail in `dcn351_resource.c`, `dmub_dcn351.c`, `irq_service_dcn351.c`, DCCG, clock-source, or audio register-table construction.
- Mechanically verify that each field in lines 4416-6585 has the expected shift/mask pair where the generated pattern requires both, and that masks align with shift values and field widths.
- Diff this range against AMD's authoritative DCN 3.5.1 register database and nearby generated DCN headers where register layouts are expected to match, especially the repeated endpoint and OTG/DCCG instance blocks.
- Exercise HDMI and DP audio on every available output: hot-plug, EDID/audio descriptor discovery, 2-channel and multichannel LPCM, HBR-capable formats where supported, sample-rate and bit-depth changes, mute/unmute, suspend/resume, and connector replug.
- Validate endpoint-specific behavior by cycling streams across multiple physical links and checking for endpoint-only failures in converter format, channel allocation, input activity, infoframe valid state, and LPIB position reporting.
- Exercise DCCG and clock-source paths with DP, HDMI, HPO/DP stream encoder, pixel-rate changes, link-rate changes, modesets, fast modesets, add/drop-pixel controls, and dynamic refresh scenarios. Watch for blank displays, timing instability, FIFO error counters, or `REG_WAIT` timeouts on DTO enable status.
- Test clock-gating and power-management paths through runtime PM, display off/on, suspend/resume, and multi-monitor attach/detach. Clock-gate mask errors often show up as hangs, missed status transitions, or unexpected power draw rather than direct compile failures.
- Use debug traces or register dumps for `OTG*_PIXEL_RATE_CNTL`, `DP_DTO*_PHASE`, `DP_DTO*_MODULO`, `DCCG_GATE_DISABLE_*`, and Azalia endpoint registers to confirm programmed values match expected masks and shifts.

## Cross-Chunk Notes

Earlier chunks own the start of `dcn_3_5_1_sh_mask.h` and the beginning of the Azalia endpoint area, including endpoint 0 and the missing first part of endpoint 1 widget-capability definitions. Later chunks continue the OTG1 pixel-rate group and the rest of the DCCG/OTG/DTO field map. The final per-file research document should merge adjacent chunks before making complete claims about all DCN 3.5.1 audio endpoints, all DCCG gate controls, or all OTG/DTO instances.

### subset-b-002090: lines 6586-8803

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 6586-8803

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and masks used by AMDGPU display code when packing, updating, and reading MMIO register fields. The companion DCN 3.5.1 offset header supplies register addresses, while this file supplies the layout of fields inside each register.

The assigned range starts in the DCCG/OTG clock-control area at `DP_DTO1_PHASE`, covers pixel-rate DTOs, DPP/DSC/DTBCLK/audio DTO controls, symbol and HDMI stream clocks, DCCG resets and vsync counter fields, then moves through Azalia HDMI/DP audio codec function, converter, pin, channel-status, and infoframe fields. The later part covers display performance monitor blocks 0 through 2, DCPG power-gating domains and interrupts, DMU/SMU/Z-state control, GPU timer readback/start-position selectors, and the first twenty display interrupt status chain registers through the beginning of `DISP_INTERRUPT_STATUS_CONTINUE19` masks.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It is unrelated to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation sites, or locks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- Numeric instance suffixes, such as `OTG2`, `DP_DTO3`, `DC_PERFMON1`, `DOMAIN18`, and `DISP_INTERRUPT_STATUS_CONTINUE16`, expose repeated hardware block instances.

Major macro families in this slice:

- Pixel-rate and display-clock generation: `DP_DTO1/2/3_PHASE`, `DP_DTO1/2/3_MODULO`, `OTG1/2/3_PHYPLL_PIXEL_RATE_CNTL`, `OTG2/3_PIXEL_RATE_CNTL`, `DPPCLK_CGTT_BLK_CTRL_REG`, `DPPCLK0..3_DTO_PARAM`, `DPPCLK_DTO_CTRL`, `DSCCLK_DTO_CTRL`, `DTBCLK_DTO0..3_PHASE`, `DTBCLK_DTO0..3_MODULO`, `DTBCLK_DTO_DBUF_EN`, `DENTIST_DISPCLK_CNTL`, and `HDMISTREAMCLK0_DTO_PARAM`.
- DCCG clock, reset, and measurement controls: `SYMCLKA..E_CLOCK_ENABLE`, `FORCE_SYMCLK_DISABLE`, `DCCG_GATE_DISABLE_CNTL3`, `DCCG_SOFT_RESET`, `DCCG_CAC_STATUS2`, `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO0/1_PHASE`, `DCCG_AUDIO_DTO0/1_MODULE`, `DCCG_AUDIO_DTBCLK_DTO_PHASE/MODULO`, `DCCG_VSYNC_CNT_CTRL`, `DCCG_VSYNC_CNT_INT_CTRL`, and `DCCG_VSYNC_OTG0..5_LATCH_VALUE`.
- HDMI character and stream clock selection: `HDMICHARCLK0_CLOCK_CNTL` and `HDMISTREAMCLK_CNTL`, plus gate-disable bits for six HDMI stream clocks and multiple `SYMCLK32` root/SE/LE gates.
- Azalia/HDA HDMI/DP audio codec metadata: `AZALIA_F2_CODEC_ROOT_PARAMETER_*`, function control/parameter registers, output converter controls, output pin controls, IEC 60958 channel-status override registers, LPIB snapshot and timer snapshot registers, audio descriptor and sink-info index/data registers, HBR, lipsync, multichannel enable/mute/channel-id registers, wireless-display identification, remote keepalive, and corresponding input converter/input pin control and capability registers.
- DC performance monitor blocks: `DC_PERFMON0_*`, `DC_PERFMON1_*`, and `DC_PERFMON2_*` cover per-counter event selection, counted-value selection, increment/run-enable mode, control select, state select for counters 0 through 7, perfmon state/report count, count-off interrupt control, clock enable, start/stop trigger selectors, counter interrupt status/ack bits, and low/high value readback fields.
- Display power, firmware, and low-power controls: `DOMAIN0..3_PG_CONFIG/STATUS`, `DOMAIN16..19_PG_CONFIG/STATUS`, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_1`, `DC_IP_REQUEST_CNTL`, `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `SMU_INTERRUPT_CONTROL`, `ZSC_CNTL`, `ZSC_CNTL2`, `DMU_MISC_ALLOW_DS_FORCE`, and `ZSC_STATUS`.
- GPU timer selectors: `DC_GPU_TIMER_START_POSITION_V_UPDATE`, `DC_GPU_TIMER_START_POSITION_VSTARTUP`, `DC_GPU_TIMER_READ`, and `DC_GPU_TIMER_READ_CNTL`.
- Display interrupt status chain: `DISP_INTERRUPT_STATUS` and `DISP_INTERRUPT_STATUS_CONTINUE` through `DISP_INTERRUPT_STATUS_CONTINUE19` define status bits for OPTC underflow, OTG IHC events, vertical interrupts, DIG fast-training/video-disable events, HPD and AUX completion, DIO/RBBMIF/I2C events, DWB/WBSCL and DMCUB events, DMU/SMU/FCH/DMUB events, DCCG/DSC/ABM/DPP/HUBP/OPP/OPTC/MMHUBBUB/AZ perfmon interrupts, HUBP vblank/vline/timeout/flip/flip-away events, DCIO DPCS errors, DCPG power-down interrupts, and Azalia endpoint audio format/enabled/disabled events.

Within lines 6586-8803 there are 198 distinct register names represented by paired or grouped shift/mask macros. The largest families are the display interrupt status chain, Azalia audio codec controls, DC performance monitor blocks, DCCG clock controls, and DCPG power/interrupt controls.

## Control Flow

This header has no runtime control flow. Runtime use is indirect:

1. DCN 3.5.1 display code includes generated offset and shift/mask headers for the ASIC.
2. Register-table macros such as `SR`, `SRI`, `SF`, and block-specific wrappers paste register and field tokens into names from this file.
3. Resource constructors and DMUB register-initialization code populate per-block register-offset, shift, and mask tables for clock generation, audio, perfmon, power-gating, low-power coordination, GPU timer, and interrupt handling.
4. Operational code later uses helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and polling/wait helpers. Those helpers use this chunk's shifts and masks to preserve unrelated hardware bits while programming DTO ratios, enabling clocks, changing power states, reading status bits, acknowledging interrupts, and selecting timer/perfmon readbacks.

The macros do not encode ordering. The caller remains responsible for hardware sequencing: waiting for DTO or clock status bits, respecting reset ordering, latching vsync counters before reading values, programming audio converter/pin registers consistently with HDA verbs and stream state, acknowledging interrupt bits with the correct write semantics, and synchronizing power-gating/low-power transitions with DMU/SMU firmware.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- DTO phase/modulo registers and clock-control fields hold display, DP, DPP, DSC, HDMI stream, DTBCLK, and audio clock ratios, enable bits, source selectors, and status/error counters.
- DCCG reset and gate-control fields affect display clock tree reset, symbol-clock availability, stream-clock gating, and audio DTO clock reset behavior.
- Vsync counter fields configure global vsync counting, OTG latch enables, trigger selection, interrupt status/clear bits, and latched OTG counter values.
- Azalia codec fields represent hardware-emulated HDA codec state for HDMI/DP audio: function power state, supported sample sizes/rates, stream/channel IDs, converter format, digital converter flags, pin widget control, unsolicited response settings, pin sense, default configuration, speaker/channel allocation, audio descriptors, sink info, lipsync, high-bit-rate capability, multichannel routing, LPIB snapshots, infoframes, channel status, and format-change notifications.
- Perfmon fields hold programmable event selection, counter mode, active/run status, interrupt enable/status/ack bits, count-off threshold behavior, clock enable, trigger selectors, and current counter values.
- DCPG domain fields expose force-on/power-gate requests and desired/current power-gating FSM state for several display domains; interrupt registers expose power-up/down and wakeup event status/masking for DCPG-controlled domains.
- DMU/SMU/ZSC fields expose display microcontroller clocks, DC-to-SMU interrupts, Z-state allowance, SoC access forcing, deep-sleep forcing, and fence/access status.
- GPU timer fields expose a 32-bit read register and select which timer/start-position value is sampled.
- Display interrupt status fields expose broad hardware event state across display pipes, link encoders, AUX/HPD, perfmon, HUBP/OPP/OPTC, power domains, DCIO, and Azalia endpoints.

Persistence is hardware-defined. Configuration fields usually remain until modeset reprogramming, suspend/resume, power-gating, firmware reset, or ASIC reset. Status, clear, ack, snapshot, latch, interrupt, sticky, and busy/done fields can be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated mask file does not identify access type, reset value, or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides matching register offsets and base indices.
- DCN 3.5.1 resource and register-table setup code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/`, which includes generated DCN headers and maps field names into resource structures.
- DCCG/display-clock code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/`, which consumes DTO, clock-source, clock-gating, reset, and vsync counter fields.
- Display audio code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/` and related audio/hwss paths, which consumes Azalia codec, converter, pin, infoframe, channel-status, HBR, LPIB, and format-change fields for HDMI/DP audio.
- Perfmon and diagnostic code that consumes `DC_PERFMON0..2_*` fields and display interrupt status bits for counter programming and event attribution.
- Power-management and firmware integration paths that use DCPG, DMU, SMU, ZSC, and `CC_DC_PIPE_DIS` fields to coordinate display-domain gating, low-power entry/exit, and DMCUB enablement.
- Interrupt service and DMUB-facing code that maps `DISP_INTERRUPT_STATUS*` fields to display IRQ sources such as HPD/AUX, OTG/OPTC, DIG, HUBP, DCIO, power-domain, and Azalia events.

The main integration pattern is token pasting, so macro spelling is effectively a source-level ABI between generated headers and shared driver tables. Missing or renamed fields tend to break compilation; incorrect numeric masks or shifts can compile successfully and fail only under hardware exercise.

## Risks And Edge Cases

- Generated masks are untyped constants. A wrong shift or mask can silently update neighboring hardware fields and appear as display clock instability, audio failure, missed interrupts, broken power gating, or misleading diagnostics.
- The chunk boundary is artificial. It begins after earlier `OTG1_PIXEL_RATE_CNTL` fields from the previous chunk and ends midway through `DISP_INTERRUPT_STATUS_CONTINUE19`, with only the first seven audio-format-changed masks present. Adjacent chunks are required for a complete file-level view.
- DTO and clock source fields are timing-sensitive. Bad phase/modulo, enable, source-select, or double-buffer-enable masks can produce link-clock mismatch, FIFO errors, unstable pixel rate, incorrect DPP/DSC clocks, or display blanking.
- DCCG reset and gate-disable fields can affect shared clock domains. Incorrect masks can leave symbol, stream, audio, DPP, DSC, or DTB clocks gated or reset while the pipe is active.
- Vsync counter interrupt and clear fields reuse bit positions for status and clear names. Callers must preserve hardware clear semantics; treating them as ordinary read/write bits can drop interrupts or leave stale latches.
- Azalia codec and pin-control fields are exposed through HDA/HDMI/DP audio behavior. Incorrect stream-format, channel-id, infoframe, speaker-allocation, HBR, LPIB snapshot, or format-change masks can cause no-audio, wrong channel mapping, bad sample-rate reporting, or audio/video sync issues.
- IEC 60958 channel-status override fields are small bitfields with explicit override-enable bits. Programming channel status without the matching override can make tests pass in software but not affect transmitted audio metadata.
- Perfmon control/status fields include active, restart, interrupt, count-off, read-select, and ack bits. Wrong masks can hide counter overflow, acknowledge the wrong counter, read a stale high/low value, or produce misleading telemetry.
- DCPG, DMU, SMU, and ZSC fields coordinate firmware-managed low power. Wrong force/gate/fence/status masks can create suspend/resume failures, failed Z-state entry, stuck power-domain transitions, or false wake/fence diagnostics.
- The interrupt status chain uses continuation bits at bit 31. Missing the continuation bit or using the wrong register in the chain can cause the driver to miss downstream events such as HUBP vblank/vline, DCIO errors, DCPG power-down, or Azalia endpoint events.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.5.1 support enabled. Token-pasting consumers in resource, DCCG, audio, perfmon, power-management, DMUB, and interrupt code should catch missing or renamed macros.
- Mechanically verify that every `__SHIFT` macro in this line range has the expected matching `_MASK` macro and that each mask aligns with its shift and expected field width. Pay special attention to status/clear pairs with identical shifts and to fields ending at the chunk boundary.
- Diff the chunk against AMD's authoritative DCN 3.5.1 register database and nearby generated headers, especially DCN 3.5.0, when compatibility or intentional deltas are expected.
- Exercise modesets across multiple OTG/DIG instances, including DP and HDMI paths, pixel-clock changes, DSC/DPP clock changes, suspend/resume, hotplug, link retraining, and repeated enable/disable cycles.
- Validate HDMI/DP audio: EDID audio capability parsing, stream format changes, channel allocation, multichannel enable/mute, HBR, lipsync, infoframe/channel-status data, LPIB snapshot readback, and endpoint enabled/disabled/format-change interrupts.
- Exercise DCCG and vsync counter behavior with vertical interrupt tests, latched OTG counter readback, dynamic refresh scenarios, and clock-gating transitions.
- Exercise perfmon programming for all three local DC perfmon blocks, including event selection, counter start/stop triggers, interrupt enable/ack, high/low readback, and overflow/count-off behavior.
- Exercise low-power and power-gating paths: display idle, Z-state entry/exit, DCPG domain power transitions, SMU interrupts, DMU deep-sleep forcing, and suspend/resume while watching for stuck fences or stale sticky status.
- Monitor kernel logs, DC traces, debugfs/register readback, display output, and audio playback for underflows, HPD/AUX interrupt loss, missed vblank/vline events, DCIO errors, DCPG interrupt storms, stuck DTO status, bad clock readback, no-audio, channel mismatch, or power-transition timeouts.

## Cross-Chunk Notes

Adjacent chunks are required for a complete file report. The previous chunk contains earlier DCCG/OTG pixel-rate fields including the start of the OTG1 pixel-rate control sequence. The next chunk continues `DISP_INTERRUPT_STATUS_CONTINUE19` masks, `DISP_INTERRUPT_STATUS_CONTINUE20`, additional interrupt control/status fields, and later generated register families. The merge lane should preserve that this is a chunk-level document for `dcn_3_5_1_sh_mask.h`, not a final per-file report.

### subset-b-002091: lines 8804-11021

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 8804-11021

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata. It contains no executable C logic; it publishes `#define` constants that describe bit shifts and bit masks for fields inside DCN 3.5.1 display registers. The companion `dcn_3_5_1_offset.h` file supplies register addresses and base indices, while this file supplies field layout for register read/modify/write helpers.

The assigned range covers a broad middle slice of display interrupt routing/status, DMUB/DMCUB control and mailbox registers, display writeback and MMHUBBUB controls, DC perfmon instance 3, Azalia audio stream windows, Azalia clock control, and the beginning of DC perfmon instance 4. Although the repository path is under a local `ceph-client` source mirror, this is AMDGPU display-driver hardware metadata and is unrelated to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, or locks in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- Repeated instance prefixes such as `OTG0_INTERRUPT_DEST`, `OTG1_INTERRUPT_DEST`, `AZF0STREAM0_AZALIA_STREAM_INDEX`, and `DMCUB_REGION3_CW0_TOP_ADDRESS` describe replicated hardware blocks.

Major macro families in this slice:

- `DISP_INTERRUPT_STATUS_CONTINUE19` through `DISP_INTERRUPT_STATUS_CONTINUE25`: status-chain fields for Azalia audio endpoint format/enabled/disabled events, OTG CPU static-screen/v-update/GSL/vstartup/vready events, I2C DDC hardware done/read request events, DP fast-training/stream-disable events, OTG no-lock vupdate and DRR total reach events, DMCUB mailbox/fault/GPINT/security events, DMU/DWB/DCHUBBUB/EXTERNAL_SW/MALL underflow events, and low-priority/high-priority DMCUB outbox readiness.
- `DC_GPU_TIMER_START_POSITION_VREADY`, `DC_GPU_TIMER_START_POSITION_FLIP`, `DC_GPU_TIMER_START_POSITION_V_UPDATE_NO_LOCK`, and `DC_GPU_TIMER_START_POSITION_FLIP_AWAY`: compact per-pipe 3-bit selectors for GPU timer start-position events across display pipes.
- Interrupt destination registers: `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, `DCPG_INTERRUPT_DEST`, `MMHUBBUB_INTERRUPT_DEST`, `WB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST`, `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, `DPP_PERFCOUNTER_INTERRUPT_DEST`, `MPC_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`, `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, `DSC_INTERRUPT_DEST`, and `HPO_INTERRUPT_DEST`. These route many display, link, audio, power, perfcounter, and debug interrupts to IH, GPIO, DMCUB, or other destinations depending on hardware programming.
- `DMCUB_RBBMIF_SEC_CNTL`, `RBBMIF_TIMEOUT`, `RBBMIF_STATUS`, `RBBMIF_INT_STATUS`, `RBBMIF_TIMEOUT_DIS`, `RBBMIF_TIMEOUT_DIS_2`, and `RBBMIF_STATUS_FLAG`: DMCUB register-bus interface security, timeout, interrupt, timeout-disable, and status-flag fields.
- DMCUB region/window fields: `DMCUB_REGION0_OFFSET` through `DMCUB_REGION7_OFFSET_HIGH`, top-address/enable fields for regions 0, 1, 2, 4, 5, 6, and 7, and code-window `DMCUB_REGION3_CW0` through `DMCUB_REGION3_CW7` base/top/offset fields.
- DMCUB interrupt and control fields: `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, `DMCUB_INTERRUPT_TYPE`, external interrupt status/context/ack, instruction-fetch/data-write/undefined-address fault addresses, `DMCUB_SEC_CNTL`, `DMCUB_MEM_CNTL`, inbox/outbox base/size/read/write pointers, timer trigger/window/current registers, scratch registers 0 through 15, `DMCUB_CNTL`, `DMCUB_CNTL2`, GPINT data-in/data-out registers, low-speed wake interrupt enable, memory power control, and processor ID.
- Display writeback and memory-client fields: `MCIF_WB_BUFMGR_SW_CONTROL`, `MCIF_WB_BUFMGR_STATUS`, buffer pitch/status/status2 for buffers 1 through 4, arbitration, SCLK change, Y/C buffer addresses and high address halves, VCE control, NB pstate control/latency watermark, clock gating, self-refresh, multi-level QoS, security level, luma/chroma sizes, buffer resolutions, VMID control, minimum TTO, and watermark fields.
- MMHUBBUB/WBIF/DMU fields: warmup config/status/address/VMID, minimum TTO, control, memory power status/control, clock control, soft reset, WBIF SMU watermark and outstanding counters, and `DMU_IF_ERR_STATUS`.
- `DC_PERFMON3_*`: performance counter control, counter control 2, counter state, perfmon control, perfmon control 2, counter-value interrupt/ack/high bits, counter value low, high, and low readout fields for DC perfmon block 3.
- `AZF0STREAM0_AZALIA_STREAM_INDEX/DATA` through `AZF0STREAM7_AZALIA_STREAM_INDEX/DATA` and `AZ_CLOCK_CNTL`: indexed Azalia stream register access windows and audio clock-gating/test-clock fields.
- `DC_PERFMON4_PERFCOUNTER_CNTL`: the first perfmon 4 counter-control field set; the rest of perfmon 4 continues after this chunk.

Within lines 8804-11021 there are more than 200 distinct register names represented by paired or grouped shift/mask macros. The range starts in the middle of `DISP_INTERRUPT_STATUS_CONTINUE19` masks and ends in the middle of `DC_PERFMON4_PERFCOUNTER_CNTL`, so adjacent chunks are required for complete file-level coverage.

## Control Flow

This header has no runtime control flow. Runtime use is through token-pasting register helper macros:

1. DCN 3.5.1-specific code includes `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`.
2. Macros such as `SR`, `SRI`, `SRI_DMUB`, `HWS_SF`, `FD_MASK`, and `FD_SHIFT` paste register and field tokens into the names defined here.
3. Resource construction, IRQ construction, DMUB register initialization, writeback/MMHUBBUB setup, and performance-monitor code populate offset, mask, and shift tables.
4. Operational code later calls register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and polling/wait helpers. Those helpers use this chunk's masks and shifts to preserve unrelated bits while programming or reading hardware state.

The macros do not encode ordering. Correct sequencing still lives in driver code: IRQ routes must be programmed before interrupts are enabled, DMCUB memory windows and mailboxes must be initialized around firmware reset/startup, writeback buffers must be configured before capture, and clock/power/status fields must be handled according to hardware access rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- Interrupt status and destination registers expose sticky, routed, or latched hardware interrupt state for OTG, DMCUB, DMU, DCHUB, DPP, MPC, OPP, OPTC, link, HPD, AUX, DSC, HPO, audio, writeback, and perfcounter sources.
- GPU timer start-position fields configure which display-pipe events can anchor GPU timer sampling for vready, flip, no-lock vupdate, and flip-away cases.
- DMCUB region, security, control, scratch, GPINT, timer, fault, inbox, and outbox registers describe the host-visible control surface for DMCUB firmware boot, memory aperture setup, command submission, notification delivery, and debug capture.
- RBBMIF fields track or mask timeout/security behavior for DMCUB register-bus accesses.
- MCIF_WB fields hold writeback buffer manager state, buffer addresses, formats/sizes/resolutions, arbitration, watermark, security, VMID, pstate, self-refresh, and clock-gating controls.
- MMHUBBUB and WBIF fields hold memory warmup, power, reset, watermark, and outstanding-counter state.
- DC perfmon 3 and the start of perfmon 4 hold programmable event selection, counting mode, state selection, counter-off interrupt/ack/status, current-value, threshold, and readout fields.
- Azalia stream and clock fields hold audio stream indexed-register access state and audio clock-gating/test-clock selection.

Persistence is hardware-defined. Configuration fields generally remain until modeset reprogramming, DMCUB reset, power gating, suspend/resume, or ASIC reset. Status, ack, fault, scratch, mailbox pointer, timeout, and interrupt fields may be sticky, write-one-to-clear, self-clearing, read-only, or timing-sensitive. This generated mask file does not identify field access types.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, where `dmub_srv_dcn351_regs_init()` includes this header and converts `FD_MASK`/`FD_SHIFT` expansions into the DMUB DCN35 register table.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which uses the DMCUB fields for firmware reset/startup, region setup, inbox/outbox rings, GPINT handling, scratch/debug capture, timer reads, and DMCUB interrupt ack/enable operations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`, which includes this header and uses generated masks/offsets to build HPD, pflip, vupdate-no-lock, vblank, vline0, and DMCUB outbox IRQ source tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which includes the DCN 3.5.1 generated headers during resource construction and wires DCN351 capabilities, IRQ service, DIO, HUBBUB, writeback, and power/clock-control resources.
- Shared DCN35/DCN32 helper headers and implementations for MCIF writeback, MMHUBBUB, DMCUB, IRQ, and perfmon behavior, which use token-pasted register names that must match these generated definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which maps interrupt source IDs and context IDs to the status/destination concepts represented here.

The main integration pattern is source-level token pasting. Missing or renamed macros usually fail compilation; incorrect numeric shifts or masks can compile successfully while corrupting hardware programming.

## Risks And Edge Cases

- Generated constants are untyped. A wrong mask or shift can silently alter adjacent fields in a read/modify/write sequence.
- The chunk boundary is artificial. `DISP_INTERRUPT_STATUS_CONTINUE19` begins before this range, and `DC_PERFMON4_PERFCOUNTER_CNTL` continues after it. Merge/reconciliation must use adjacent chunks for complete register-family analysis.
- Interrupt status/destination fields are high-risk because incorrect routes or masks can cause missed vblank/vline/hotplug/audio/AUX/DMCUB events, interrupt storms, or acknowledgements that fail to clear the intended source.
- DMCUB region and security fields are boot-critical. Incorrect base/top/offset/enable masks can prevent firmware fetches, map the wrong memory window, trip access faults, or break PSP/security expectations.
- DMCUB inbox/outbox and GPINT fields are synchronization-sensitive. Bad pointer, ready, ack, or enable masks can stall command submission, lose notifications, or leave host/firmware rings inconsistent.
- RBBMIF timeout-disable/status fields can hide or misreport register-bus access failures, complicating debug of firmware and display block hangs.
- MCIF_WB buffer address/size/resolution/security/VMID fields affect display writeback DMA. Incorrect masks can write to the wrong address, corrupt capture output, violate isolation, or trigger underflow/backpressure.
- MMHUBBUB memory power, warmup, and reset fields affect low-power transitions and memory-client readiness. Bad masks can cause resume failures, underflow, or clock/power gating regressions.
- Perfmon fields are diagnostic but side-effect-sensitive; wrong event, enable, clear, threshold, or ack masks can invalidate telemetry or leave counter interrupts asserted.
- Azalia indexed stream register fields require correct write-enable and index/data handling. Bad masks can corrupt HDMI/DP audio stream programming or clock-gating state.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN351 support enabled. Token-pasting consumers in DMUB, IRQ, resource, writeback, MMHUBBUB, and perfmon paths should catch missing or renamed macros.
- Mechanically verify that every `__SHIFT` macro in this line range has the expected matching `_MASK` macro and that masks align with field shifts and widths.
- Diff this generated slice against AMD's authoritative DCN 3.5.1 register database and against nearby generated headers where DCN 3.5.0 or DCN 3.6 compatibility is expected.
- Exercise interrupt behavior: hotplug/HPD RX, vblank/vline0, page flip, vupdate-no-lock, DMCUB outbox, AUX/I2C, audio endpoint changes, DSC/link events, and perfcounter interrupts. Watch for missed events, storms, or stuck ack bits.
- Exercise DMCUB firmware lifecycle: cold boot, reset, suspend/resume, secure-region setup, inbox/outbox command traffic, GPINT notifications, scratch/debug collection, and fault-address reporting.
- Exercise writeback paths using display writeback capture with multiple formats, buffer rotations, VMID/security settings, watermark pressure, and power-management transitions.
- Exercise memory and power transitions involving MMHUBBUB warmup, memory power status/control, soft reset, self-refresh, and clock gating.
- Use perfmon/debug validation where available: program DC perfmon 3 and perfmon 4 counters, trigger threshold/overflow cases, ack counter interrupts, and compare readback against expected event activity.
- Monitor kernel logs, DC traces, DMCUB traces, register readback, IRQ counters, writeback output, and display behavior for underflow, timeout, DMCUB fault, stuck mailbox pointer, missing hotplug/vblank, black screen, audio loss, or resume instability.

## Cross-Chunk Notes

The previous chunk is required for the beginning of `DISP_INTERRUPT_STATUS_CONTINUE19`. The following chunk is required for the rest of `DC_PERFMON4_PERFCOUNTER_CNTL` and subsequent perfmon 4 fields. The final per-file report should treat this as one generated DCN 3.5.1 hardware metadata slice, not as an independent software module.

### subset-b-002092: lines 11022-13240

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 11022-13240

## Scope

This chunk is a generated AMD DCN 3.5.1 register shift/mask slice. It contains preprocessor constants only: each register field has a `__SHIFT` definition and a matching `_MASK` definition used to pack, update, and extract MMIO bit fields. There are no C functions, structs, enums, loops, branches, or driver-owned storage objects in this range.

The requested range begins in the tail of the `DC_PERFMON4_PERFCOUNTER_CNTL` field set and ends mid-register at `HUBP1_DCSURF_TILING_CONFIG__META_LINEAR_MASK`. The major covered surfaces are:

- Display performance monitor blocks `DC_PERFMON4`, `DC_PERFMON5`, and `DC_PERFMON6`.
- Azalia/HDA display-audio endpoint, stream, codec, CRC, DMA, DTO, clock-gating, memory-power, and connectivity fields.
- DCHUBBUB SDPIF, VM aperture, local memory, memory-power, CRC, DCC stats, compbuf/DET allocation, arbitration, watermark, timer, clock, performance measurement, timeout, debug, and fault-monitor fields.
- DCN VM context 0-15 page-table control and address fields, default address fields, and fault control/status/address fields.
- HUBP/HUBPREQ/HUBPRET/CURSOR instance 0 field definitions for surface format, tiling, viewport, addresses, flip, QoS/timing, memory power, read-line, interrupts, cursor, and DMDATA.
- The start of HUBP instance 1 surface configuration, address configuration, and tiling fields.

## Purpose

The header supplies the bit-position half of the DCN 3.5.1 hardware ABI. Companion offset headers identify which register to access; this file identifies which bits inside that register belong to each named field. AMD display code consumes these constants through field helper macros such as `FD_MASK`, `FD_SHIFT`, `SF`, `HWS_SF`, and block-specific mask/shift list macros, which then feed `REG_GET`, `REG_SET`, `REG_UPDATE`, IRQ table construction, DMUB register initialization, and hardware block register tables.

Because this is generated register metadata, the most important property is exact numeric correspondence with AMD's DCN 3.5.1 register specification and with the matching `dcn_3_5_1_offset.h` names. The file itself does not enforce access order or hardware side effects; it only defines symbolic bit encodings.

## Important Definitions

The exported interface is the macro namespace:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the field mask already shifted into register position.
- Repeated block prefixes such as `HUBP0`, `HUBPREQ0`, `HUBPRET0`, `CURSOR0_0`, and `DC_PERFMON6` identify the hardware instance whose fields are being described.

Important macro families in this range:

- `DC_PERFMON4_*`, `DC_PERFMON5_*`, and `DC_PERFMON6_*`: performance counter event selection, current-value source selection, increment mode, hardware start/stop/count-off selection, restart, interrupt enable/status/ack, active state, per-counter state, perfmon run-start/run-stop selection, high/low counter values, and high-half read selection.
- `AZF0ENDPOINT[0-7]_AZALIA_F0_CODEC_ENDPOINT_INDEX/DATA`: indirect endpoint register index and data windows for display-audio codec endpoints.
- `AZALIA_*`: controller clock gating, audio DTO phase/module and force controls, SOCCLK deep-sleep exit, underflow filler sample, data/BDL/CORB/RIRB/DP DMA snoop/isochronous settings, output stream arbiter, input/output CRC engines, memory-power control/status, function/root codec identity, power/reset/channel/resync controls, subsystem ID response, converter synchronization, and port connectivity override fields.
- `AZF0STREAM[8-15]_AZALIA_STREAM_INDEX/DATA` and `AZF0INPUTENDPOINT[0-7]_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX/DATA`: indirect stream and input-endpoint index/data windows.
- `DCHUBBUB_*`: SDPIF configuration and error/status controls, forced-I/O status capture, framebuffer/AGP/local-HBM aperture fields, SDPIF and return-path memory power, hubbub CRC source/result fields, DCC statistics, compbuf/DET size and allocation status, memory-power modes/status, debug depths, outstanding-request and QoS controls, DRAM self-refresh/pstate/DCFCLK-deep-sleep controls, watermark sets A-D including Z8 variants, host-VM arbitration, watermark change requests, timeout controls/status/clear/mask, global timer, VTG controls, soft reset, clock controls, DCFCLK counter/readback, performance measurement, vline snapshot, control status, FMON controls, and test debug index/data.
- `DCN_VM_CONTEXT[0-15]_*`: page-table depth/block-size, page-directory base high/low, logical page start high/low, and logical page end high/low fields for 16 contexts.
- `DCN_VM_DEFAULT_ADDR_*` and `DCN_VM_FAULT_*`: default physical page number/VMID, fault replay/write/access/page-table-block/protection controls, fault status/clear/client/write/read/VMID fields, and fault address low/high fields.
- `HUBP0_*`: surface pixel format, rotation, mirror, alpha plane, address configuration, tiling configuration, primary/secondary viewport start/dimension for luma and chroma, request-size configuration, HUBP blank/reset/VTG/TTU/timeout/underflow controls, clock gates/status, VMPG size, and DCFCLK/DPPCLK measurement-window controls.
- `HUBPREQ0_*`: surface pitch, VMID, primary/secondary and luma/chroma surface addresses, meta-surface addresses, TMZ/DCC surface controls, flip controls and flip interrupts, in-use and earliest-in-use readbacks, expansion modes, TTU/QoS controls for surfaces and cursors, DMDATA VM fault/late/underflow status, system aperture and L1 TLB control, blank/destination/prefetch/vblank/flip/nominal/delivery timing parameters, cursor settings, reference-to-pixel clock conversion, DRQ limits, and HUBPREQ memory-power control/status.
- `HUBPRET0_*`: return-path control, memory-power control/status, read-line control/value/status fields, and return-path interrupt enable/status/clear/mask fields.
- `CURSOR0_0_*`: cursor enable/mode/format/2x magnify/pitch/lines-per-chunk fields, cursor image address, size, position, hot spot, stereo, destination offset, cursor memory power, DMDATA address/control/QoS/status/software controls.
- `HUBP1_DCSURF_SURFACE_CONFIG`, `HUBP1_DCSURF_ADDR_CONFIG`, and the start of `HUBP1_DCSURF_TILING_CONFIG`: partial pipe-1 surface format, address layout, and tiling metadata.

## Control Flow

There is no runtime control flow in the header. The effective flow is macro expansion in the consuming driver code:

1. DCN 3.5.1 display code includes `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`.
2. Resource code expands block register-list macros and block mask/shift-list macros into C structs, for example HUBP and HUBBUB tables in `dcn351_resource.c`.
3. DMUB setup includes this exact header in `dmub_dcn351.c`; `dmub_srv_dcn351_regs_init()` calls `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` while expanding `DMUB_DCN35_FIELDS()`.
4. Runtime code uses the populated offsets, masks, and shifts to perform MMIO read/modify/write operations or to build IRQ register entries.
5. Hardware interprets the fields as state-machine controls, status bits, counter values, addresses, or timing parameters.

The header cannot express synchronization rules. Callers still need to serialize indirect index/data accesses, stage flip updates at the right vblank/vupdate boundary, poll or clear status bits according to hardware semantics, and avoid programming powered-down blocks.

## State and Persistence Behavior

The macros are compile-time constants and persist no data. The hardware registers they describe hold several kinds of state:

- Persistent configuration state: audio DTO, DMA snoop/isochronous behavior, codec power/reset/channel settings, port connectivity overrides, VM page-table context ranges, framebuffer/AGP/HBM apertures, HUBP format/tiling/viewport/request sizing, surface and metadata addresses, TMZ/DCC enablement, prefetch/vblank/flip/nominal/delivery timing, cursor image and DMDATA settings, clock-gating controls, and memory-power modes.
- Latched or double-buffered state: HUBPREQ surface update locks, flip pending state, master update lock status, in-use and earliest-in-use surface addresses, and timing fields that are consumed around frame boundaries.
- Volatile status and diagnostic state: Azalia CRC completion/results, memory-power status, SDPIF forced-I/O status, DCHUBBUB CRC values, DCC stats, compbuf/DET current sizes, watermark-change status, timeout status, VM fault status and fault address, HUBP timeout/underflow status, DMDATA fault/underflow/late/done status, read-line values/status, cursor memory-power state, and perfmon counter states/current values.
- Side-effect-sensitive fields: interrupt ack/clear bits, fault clears, timeout clears, underflow clears, perfmon ack bits, memory-power force/disable controls, soft resets, indirect stream/endpoint indexes, and debug index/data windows.

The repeated instance naming is part of the state isolation contract. `HUBP0`, `HUBPREQ0`, `HUBPRET0`, and `CURSOR0_0` describe pipe 0 fields; the final lines start pipe 1 and must be reconciled with the next chunk before drawing conclusions about all pipe-1 fields.

## Dependencies and Integration Points

Direct dependencies are preprocessor-level: this header is guarded by `_dcn_3_5_1_SH_MASK_HEADER` and is paired with the generated offset header for the same ASIC generation.

Important source-tree integration points include:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which includes `dcn/dcn_3_5_1_sh_mask.h` and initializes DMUB DCN 3.5 register masks and shifts with `FD_MASK` and `FD_SHIFT`.
- `drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which builds HUBP/HUBBUB/HWSEQ and other block shift/mask tables with macros such as `HUBP_MASK_SH_LIST_DCN35`, `HUBBUB_MASK_SH_LIST_DCN35`, and `HWSEQ_DCN35_MASK_SH_LIST`.
- `drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`, where IRQ entries macro-paste names such as `HUBPREQn_DCSURF_SURFACE_FLIP_INTERRUPT__SURFACE_FLIP_INT_MASK_MASK` and `__SURFACE_FLIP_CLEAR_MASK` into enable and ack tables.
- HUBP implementation code under `drivers/gpu/drm/amd/display/dc/hubp/dcn35/`, which programs fields such as `DCSURF_SURFACE_CONFIG`, surface addresses, flip controls, viewport/timing fields, cursor settings, and status readbacks through register helpers.
- DCN DML and resource code that computes watermarks, DET/compbuf allocation, VM timing, prefetch, vblank, flip, and delivery values that eventually land in the DCHUBBUB/HUBPREQ fields defined here.
- Display audio paths that use Azalia endpoint/stream/function fields for DP/HDMI audio setup, audio DTO control, audio memory power, CRC diagnostics, and codec power/reset behavior.

## Risks and Edge Cases

- Numeric drift is high impact. A wrong `_SHIFT` or `_MASK` can corrupt unrelated bits while all C code still compiles.
- This chunk starts and ends mid-block. `DC_PERFMON4_PERFCOUNTER_CNTL` lacks its earlier fields here, and `HUBP1_DCSURF_TILING_CONFIG` is incomplete at the end. Adjacent chunks are required for complete block-level documentation.
- Repeated register families are copy-sensitive. Azalia endpoint/input-endpoint/stream instances, DCN VM contexts 0-15, watermark sets A-D, and HUBP/HUBPREQ/HUBPRET/CURSOR instances can compile with an instance prefix mistake but affect only one pipe, stream, endpoint, or VM context at runtime.
- Indirect index/data windows require serialization. Azalia endpoint, input-endpoint, stream, and DCHUBBUB debug index/data fields can read or write the wrong target if callers interleave index and data operations.
- Address fields are split across low/high, primary/secondary, luma/chroma, and meta-surface variants. Partial updates can cause display fetches from mismatched addresses, wrong VMIDs, or stale compression metadata.
- Flip and timing fields are frame-boundary-sensitive. Bad values for update locks, flip pending delay, prefetch, vblank, nominal, delivery, and TTU/QoS fields can manifest as stale frames, page-flip timeout, underflow, or intermittent corruption.
- Clear/ack/status fields have hardware side effects. Misusing `SURFACE_FLIP_CLEAR`, `DCHUBBUB_TIMEOUT_INT_CLEAR`, `DMDATA_VM_FAULT_STATUS_CLEAR`, `DMDATA_UNDERFLOW_CLEAR`, perfmon interrupt ack bits, or HUBP underflow/timeout clears can lose diagnostics or leave interrupts stuck.
- Memory-power controls appear in Azalia, DCHUBBUB, HUBPREQ, HUBPRET, and cursor blocks. Writes while memory is disabled or before status settles can be dropped or produce transient readbacks.
- VM context and fault fields are global enough to affect multiple display fetch clients. Wrong page-table depth/block size, base/start/end addresses, default address, or fault control can break several planes rather than one immediate caller.

## Test Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware/display behavior:

- Build AMDGPU/DC with DCN 3.5.1 support and DMUB enabled. Missing or renamed field macros should fail in `dmub_dcn351.c`, `dcn351_resource.c`, HUBP/HUBBUB/HWSEQ tables, IRQ service code, and shared register helpers.
- Run generated-header consistency checks that each covered `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, that masks align with shifts and field widths, and that repeated instances preserve intended layouts across endpoint, stream, VM context, perfmon, and pipe blocks.
- Diff this slice against AMD's authoritative DCN 3.5.1 register database and nearby DCN 3.5/3.6 generated headers where layouts are expected to match.
- Exercise DP/HDMI audio modes, including stream setup, endpoint/input-endpoint indirect access, audio DTO changes, codec power/reset, memory-power transitions, and Azalia CRC diagnostics.
- Run modeset and multi-plane tests through HUBP/HUBPREQ pipe 0 with varied pixel formats, alpha plane, rotation, mirror, tiling modes, DCC/TMZ, luma/chroma surfaces, primary/secondary surfaces, meta surfaces, and VMID-backed addresses.
- Stress page flips, triple buffering, GSL, flip interrupts, surface in-use/earliest-in-use readback, cursor movement, cursor image changes, stereo cursor behavior, and DMDATA delivery while checking for underflow, late/fault status, and missed flip completion.
- Validate DCHUBBUB arbitration and watermark behavior under high bandwidth, high resolution, multi-plane, compressed-surface, memory-pressure, self-refresh, pstate, Z8, and DCFCLK deep-sleep scenarios.
- Use perfmon and debug tooling to program and read `DC_PERFMON4`, `DC_PERFMON5`, `DC_PERFMON6`, DCHUBBUB performance measurement counters, FMON state, DCC stats, CRC results, and DCFCLK/DPPCLK measurement windows.
- Run suspend/resume, display hotplug, blank/unblank, audio suspend, and display power-gating tests to exercise memory-power state transitions and restore sequencing across Azalia, DCHUBBUB, HUBPREQ, HUBPRET, cursor, and perfmon blocks.
- Inject or observe VM/display-fetch faults where supported and verify `DCN_VM_FAULT_STATUS`, fault address fields, DMDATA VM fault fields, and valid page-table context programming.

## Chunk-Specific Summary

Lines 11022-13240 define DCN 3.5.1 bit-field metadata rather than executable code. The slice is centered on display audio, DCHUBBUB memory/VM/arbitration diagnostics, DCN VM context/fault registers, pipe-0 HUBP/HUBPREQ/HUBPRET/cursor programming, and perfmon diagnostics, with only the beginning of pipe-1 HUBP fields included. Correctness depends on exact generated masks/shifts, matching offset-header names, instance-correct macro use, serialized indirect access, and hardware validation across audio, VM, plane fetch, flip, cursor, memory-power, watermark, fault, interrupt, and perfmon paths.

### subset-b-002093: lines 13241-15458

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 13241-15458

## Purpose

This chunk is generated AMD DCN 3.5.1 shift/mask register-field metadata. It has no executable C logic; it publishes preprocessor constants that encode bit offsets and field masks for display hub pipe, request, return, cursor, display metadata, and display perfmon MMIO registers. Consumers pair this header with `dcn_3_5_1_offset.h` so AMDGPU display register-helper macros can update or extract individual hardware fields without hard-coding bit positions in driver code.

The requested range is a mid-file slice containing 2,218 `#define` entries: 1,109 `__SHIFT` macros and 1,109 `_MASK` macros. The range starts at the tail of `HUBP1_DCSURF_TILING_CONFIG` with `PIPE_ALIGNED_MASK`, whose matching shift is in the previous chunk, and stops inside `CURSOR0_3_DMDATA_CNTL` after `DMDATA_MODE_MASK`, before the `DMDATA_SIZE_MASK` line in the next chunk. The apparent `*_MASK_MASK` names in interrupt and perfmon groups are expected generated names for fields whose semantic field name itself ends in `MASK`.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset used to pack or unpack a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, preserve, or clear the field during MMIO read-modify-write operations.

Major macro families in this slice are:

- `HUBP1`, `HUBP2`, and `HUBP3`: surface format, address/tiling, viewport, request-size, control, clock, VMPG, and DCFCLK/DPPCLK measurement-window fields. These describe per-plane hub pipe behavior, including surface dimensions, swizzle mode, chunk sizes, blank/reset/status bits, timeout/underflow reporting, clock-gating state, and perf measurement windows.
- `HUBPREQ1`, `HUBPREQ2`, and `HUBPREQ3`: hub pipe request-side surface state. Each instance covers pitch, VMID, primary/secondary luma and chroma addresses, meta-surface addresses, surface control, flip control, flip interrupts, in-use and earliest-in-use addresses, expansion mode, TTU/QoS timing, VM aperture and L1 TLB controls, blank offsets, destination dimensions, prefetch, vblank/flip/nominal timing parameters, per-line delivery, cursor request settings, memory power control/status, and additional flip/vblank VM/PTE/meta timing fields.
- `HUBPRET1`, `HUBPRET2`, and `HUBPRET3`: hub pipe return-side control and status. These fields cover DET buffer base selection, 3-to-2 packing disablement, component crossbar source selection, return-side memory power, read-line window programming, vblank/read-line interrupt mask/type/clear/status bits, current read-line value snapshots, and read-line/vblank inside/outside status.
- `CURSOR0_1`, `CURSOR0_2`, and partial `CURSOR0_3`: hardware cursor and display metadata fields. Complete cursor instance 1 and 2 blocks include cursor enable, mode, pitch, size, position, hot spot, stereo offsets, destination X offset, cursor memory power, DMDATA GPU address, DMDATA control, QoS, status, software data control, and software data payload. Instance 3 begins the same pattern and ends mid-`DMDATA_CNTL` because of the artificial chunk boundary.
- `DC_PERFMON7` and `DC_PERFMON8`: display perfmon control, state, counter value, interrupt/status/ack, and high/low readout fields. These are used to select events, counter value sources, increment/run modes, hardware count-off behavior, restart/interrupt behavior, and per-counter state readback.

The chunk is heavily instance-repeated. `HUBPREQ1-3` and `HUBPRET1-3` carry nearly identical field layouts, while `HUBP1` begins in the previous chunk and `CURSOR0_3` continues in the next chunk.

## Control Flow

This header has no runtime control flow. Runtime sequencing comes from AMDGPU display code:

1. DCN 3.5.1 resource, IRQ, and DMUB code includes `dcn_3_5_1_offset.h` and this shift/mask header.
2. Register-list macros such as `SRI(...)`, `HUBP_REG_LIST_DCN30_RI(...)`, and `HUBP_MASK_SH_LIST_DCN35(...)` token-paste register and field names into per-block offset, shift, and mask tables.
3. DCN 3.5.1 resource construction initializes `hubp_regs`, `hubp_shift`, and `hubp_mask` arrays for the available HUBP instances.
4. Runtime HUBP, cursor, flip, VM, prefetch, TTU/QoS, and interrupt paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers use the numeric masks and shifts from this file to touch only the intended bits.

The macros do not encode ordering rules. Consumers must still sequence surface address programming, flip arming, VM aperture/TLB updates, prefetch and delivery timing, cursor metadata updates, memory power transitions, clock gating, interrupt clear/ack behavior, and suspend/resume restore correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed DCN 3.5.1 hardware state:

- Plane fetch configuration for pixel format, rotation, mirroring, tiling, viewport dimensions, pitch, luma/chroma addresses, meta addresses, DCC-related metadata, and stereo/primary/secondary surfaces.
- VM and memory request state for VMID selection, system aperture bounds, L1 TLB controls, request chunk sizing, PTE/meta/VM group timing, and VMPG page-size selection.
- Flip and vblank state for immediate/async flip modes, master update lock status, GSL/triple-buffer control, flip interrupt masking/clearing/status, in-use address reporting, earliest-in-use tracking, and flip/vblank timing parameters.
- QoS, TTU, prefetch, and delivery timing for surfaces, cursors, and DMDATA, including per-line delivery and destination-position dependent request timing.
- HUBP control/status for blanking, soft reset, outstanding requests, underflow and timeout status, clock enable/gating state, and perf measurement windows.
- Cursor state for enable/mode/pitch, dimensions, screen position, hot spot, stereo offsets, source address, cursor memory power, and destination offsets.
- DMDATA state for metadata memory address, TMZ bit, update/repeat/mode/size fields, QoS level and deadline delta, completion/underflow status, and software-injected metadata data.
- HUBPRET read-line/vblank state and interrupts, including line-window start/end, line snapshots, vblank status, read-line inside/outside flags, and memory power state.
- DC perfmon state for selected events, run/count modes, active status, state selectors, current counter values, high/low counter readback, and interrupt status/ack bits.

Persistence is hardware-defined. Configuration fields generally remain until the next modeset, page flip, cursor update, power-gating event, suspend/resume path, driver reset, or ASIC reset. Status, interrupt, clear, underflow, timeout, perfmon, and memory-power fields may be read-only, sticky, self-clearing, write-one-to-clear, clock-domain dependent, or valid only while the relevant display block is powered. This generated header does not distinguish those access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides the matching MMIO offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which includes both generated headers and initializes DCN 3.5.1 HUBP register, shift, and mask tables with `HUBP_REG_LIST_DCN30_RI` and `HUBP_MASK_SH_LIST_DCN35`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.h`, which defines the DCN 3.5 HUBP shift/mask list extension and `struct dcn35_hubp2_shift` / `struct dcn35_hubp2_mask`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn20/dcn20_hubp.h` and inherited DCN 3.x HUBP headers, which define the common HUBP/HUBPREQ/CURSOR/DMDATA register-list and field-list shapes consumed by DCN 3.5.1.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`, which maps HUBP flip interrupt source IDs for instances including HUBP1-3 to DAL page-flip IRQ sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which uses the same generated shift/mask style to populate DMUB-facing DCN 3.5 register field tables.

The primary integration point is token-pasted register-table construction. Hardware-specific register names such as `HUBPREQ2_DCSURF_FLIP_CONTROL`, `CURSOR0_1_DMDATA_CNTL`, or `HUBPRET3_HUBPRET_INTERRUPT` become fields in driver-owned tables; generic HUBP code then uses those tables without embedding DCN 3.5.1 numeric bit positions.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing the wrong MMIO bits, corrupting adjacent fields, missing an interrupt, or reading stale status.
- The generated header must match the companion offset header and silicon register database. Manual edits or partial regeneration can make a register address correct but its field layout wrong.
- The chunk boundary is artificial. `HUBP1_DCSURF_TILING_CONFIG__PIPE_ALIGNED_MASK` begins without its shift in this range, and `CURSOR0_3_DMDATA_CNTL__DMDATA_SIZE__SHIFT` ends without its mask until the next line/chunk.
- Repeated instances are easy to miscompare. A generator or copy error in only `HUBPREQ2`, `HUBPRET3`, or `CURSOR0_1` may only fail on a specific pipe, display, cursor plane, or multi-monitor topology.
- Fields with semantic names ending in `MASK` produce generated names such as `PERFCOUNTER_OFF_MASK_MASK` and `PIPE_VBLANK_INT_MASK_MASK`. Tooling that naively strips `_MASK` can report false mismatches.
- Flip, interrupt, underflow, timeout, and clear fields are side-effect-sensitive. Confusing status, mask, type, ack, or clear bits can cause missed page-flip completion, interrupt storms, stuck vblank/read-line reporting, or hidden underflow diagnostics.
- Surface address and VM fields are high risk because low/high halves, chroma variants, meta-surface addresses, VMID, aperture, and TLB settings must agree with memory manager, DCC, TMZ, and plane format state.
- Timing and QoS fields interact with bandwidth calculations outside this header. Bad prefetch, TTU, delivery, PTE/meta/VM group, or deadline masks can produce underruns that only appear at high resolution, high refresh, multi-plane, rotated, or compressed modes.
- Power and clock gating fields may be ignored or hazardous when programmed while the relevant HUBP, request, return, cursor, memory, or clock domain is gated or reset.

## Test Signals

Useful validation combines generated-header checks with DCN 3.5.1 hardware behavior:

- Build AMDGPU display support with DCN 3.5.1 enabled. Missing or renamed macros should fail in DCN 3.5.1 resource construction, HUBP register table initialization, IRQ service code, or DMUB register-field initialization.
- Mechanically verify that every expected field in lines 13241-15458 has the right `__SHIFT`/`_MASK` pairing while accounting for the known boundary exceptions and field names that naturally end in `MASK`.
- Diff this range against AMD's authoritative DCN 3.5.1 register database and nearby generated headers such as `dcn_3_5_0_sh_mask.h` or later DCN 3.x variants where HUBP/HUBPREQ/HUBPRET/CURSOR layouts are expected to match.
- Exercise enough active displays and planes to use HUBP/HUBPREQ/HUBPRET instances 1 through 3, including primary and secondary surfaces, luma/chroma planes, DCC/meta surfaces, cursor planes, and multi-display page flips.
- Validate page-flip behavior with immediate, async, GSL, triple-buffer, vblank, and high-refresh scenarios; watch for missed flip interrupts, stale in-use addresses, underflows, and frame pacing defects.
- Test cursor and DMDATA behavior through cursor enable/disable, movement, hot-spot changes, stereo offsets, large cursor sizes, TMZ metadata, software metadata updates, and suspend/resume.
- Exercise VM and memory paths with different VMIDs, large addresses, system aperture bounds, compressed surfaces, rotated/mirrored surfaces, and memory pressure.
- Check HUBPRET vblank/read-line interrupts and snapshots for correct line windows, status transitions, interrupt clearing, and behavior while the request path is disabled or blanked.
- Use perfmon/debug tooling where available to confirm `DC_PERFMON7` and `DC_PERFMON8` event selection, counter state, interrupt/ack behavior, and high/low readout consistency.
- Watch kernel logs, display diagnostics, and hardware counters for page-flip timeouts, HUBP underflow/timeout status, interrupt storms, cursor corruption, blank displays, wrong viewport placement, DCC/meta faults, VM faults, and resume-only regressions.

## Cross-Chunk Notes

The previous chunk owns the beginning of the `HUBP1` field set, including most of `HUBP1_DCSURF_TILING_CONFIG` and the `PIPE_ALIGNED` shift. This chunk then covers the rest of HUBP/HUBPREQ/HUBPRET/CURSOR/perfmon instance groups for pipes 1 and 2, most of pipe 3, and stops inside `CURSOR0_3_DMDATA_CNTL`. The next chunk continues with `CURSOR0_3_DMDATA_CNTL__DMDATA_SIZE_MASK`, the rest of `CURSOR0_3` DMDATA fields, and subsequent DCN 3.5.1 register-field families. The final per-file research document should merge adjacent chunks before making whole-file claims about all HUBP instances, all cursor instances, or complete shift/mask pairing across `dcn_3_5_1_sh_mask.h`.

### subset-b-002094: lines 15459-17678

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 15459-17678

## Scope And Purpose

This chunk is a generated AMD DCN 3.5.1 display register shift/mask header segment. It does not define executable code; it defines C preprocessor constants used to extract, insert, and document bitfields in memory-mapped display hardware registers. The source file has an MIT SPDX header and a normal include guard at the top of the full header. This chunk starts in the `CURSOR0_3_DMDATA` register group and runs through the beginning of `DC_PERFMON11_PERFMON_CNTL`.

The dominant purpose of this range is to provide field layout for display pipe instances 0 and 1 in DCN351-era hardware:

- Cursor metadata transfer fields for cursor instance 3.
- Display core performance monitor blocks `DC_PERFMON9`, `DC_PERFMON10`, and the start of `DC_PERFMON11`.
- DPP top-level control, soft reset, CRC, and host-read throttling for DPP instances 0 and 1.
- CNVC format conversion, color keying, alpha LUT, pre-dealpha, pre-CSC, pre-degamma, and pre-realpha fields for CNVC instances 0 and 1.
- Cursor composition fields for `CNVC_CUR0` and `CNVC_CUR1`.
- DSCL/scaler fields for coefficient RAM access, tap selection, scaler mode, filter ratio/init values, overscan, recout/MPC sizing, line-buffer controls, and DSCL/OBUF memory power controls for DSCL instances 0 and 1.
- CM color-management fields for post-CSC, gamut remap, bias, gamma correction LUT programming, RAM A/RAM B piecewise regions, HDR multiplier, memory power, dealpha, coefficient format, and a CM0 debug index.

As a chunk report, this document covers only lines 15459-17678. The final per-file report should merge this with adjacent chunks to describe the entire `dcn_3_5_1_sh_mask.h` header.

## Important APIs, Types, And Macros

The only exported surface in this chunk is `#define` constants. Each hardware field normally has two constants:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset of the field within the register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field.

Consumers use these constants through AMD display register helper macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `TF_SF(...)`, and related register-list expansion macros. In `dmub_dcn351.c`, for example, `DMUB_SF(reg, field)` writes `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` into DMUB register metadata. In `dcn351_resource.c`, the header is included with `dcn_3_5_1_offset.h` so resource construction code can pair register offsets with these masks and shifts. DPP-specific headers such as `dcn35_dpp.h` reference fields like `DPP_TOP0_DPP_CONTROL` through `TF_SF`.

No C types, functions, structs, or inline helpers are declared in this range. The effective ABI is the macro naming scheme and exact numeric values.

## Register Areas Covered

### Cursor DMDATA Tail

The opening lines finish `CURSOR0_3_DMDATA` definitions:

- `DMDATA_CNTL` includes `DMDATA_SIZE` at bits 16-27, continuing from prior lines in the file.
- `DMDATA_QOS_CNTL` defines mode, QoS level, and deadline delta fields.
- `DMDATA_STATUS` exposes `DMDATA_DONE`, `DMDATA_UNDERFLOW`, and `DMDATA_UNDERFLOW_CLEAR`.
- `DMDATA_SW_CNTL` and `DMDATA_SW_DATA` define software-updated metadata payload control and 32-bit data access.

These fields affect cursor/display metadata programming and underflow reporting. The chunk begins mid-register group, so the paired address-high/low and earlier `DMDATA_CNTL` fields belong to the previous chunk.

### DC Performance Monitors

`DC_PERFMON9`, `DC_PERFMON10`, and the start of `DC_PERFMON11` share a repeated layout:

- `PERFCOUNTER_CNTL` selects the counted event, counted value source, increment mode, hardware control, run-enable mode, count-off start behavior, restart behavior, interrupt enable, masking, active state, and counter select.
- `PERFCOUNTER_CNTL2` selects counted value type, hardware stop inputs, count-off select, and control-bank select.
- `PERFCOUNTER_STATE` packs state and selector fields for counters 0 through 7.
- `PERFMON_CNTL` controls perfmon state, report count, count-off interrupt logic, interrupt enable/status/ack.
- `PERFMON_CNTL2` appears for perfmon 9 and 10 in this chunk and defines count-off interrupt type, clock enable, and run-enable start/stop selectors.
- `PERFMON_CVALUE_INT_MISC`, value low/high, and read select fields appear for perfmon 9 and 10. The chunk ends before the corresponding value fields for perfmon 11.

These masks are used by debug, diagnostics, tracing, and internal display performance instrumentation paths. Incorrect masks would misprogram event selection or fail to acknowledge performance counter interrupts.

### DPP Top Control For Instances 0 And 1

`DPP_TOP0_*` and `DPP_TOP1_*` define DPP-level controls:

- `DPP_CONTROL`: DPP clock enable, DPP/disp clock gating disable controls, dynamic/DSCL clock gate controls, and test clock select.
- `DPP_SOFT_RESET`: soft reset bits for CNVC, DSCL, CM, and OBUF subblocks.
- `DPP_CRC_VAL_R_G`, `DPP_CRC_VAL_B_A`, and `DPP_CRC_CTRL`: CRC result fields and CRC enable, continuous/one-shot modes, 4:2:0 component select, source select, stereo/interlace/pixel/cursor format selection, and CRC mask.
- `HOST_READ_CONTROL`: host read rate control.

These definitions support DPP construction, clock/power sequencing, CRC capture for validation, and register debug access. The DCN35 DPP code adds or overrides a small set of fields elsewhere in the header, but this chunk provides the core `DPP_TOP0` and `DPP_TOP1` bit layouts.

### CNVC And Cursor Composition For Instances 0 And 1

`CNVC_CFG0_*` and `CNVC_CFG1_*` define input format conversion and pre-color-processing controls:

- Surface pixel format and alpha-plane enable.
- Format expansion, 16-bit conversion, alpha enable, bypass, MSB alignment, positive clamp controls, update-pending status, and RGB crossbar selection.
- Floating-point bias and scale for R/G/B.
- Color-key enable, mode, and per-channel low/high ranges for alpha, red, green, and blue.
- 2-bit alpha LUT entries.
- Pre-dealpha, pre-CSC mode and 3x4 coefficient matrices, alternate B coefficient banks, coefficient format, pre-degamma, and pre-realpha.

`CNVC_CUR0_*` and `CNVC_CUR1_*` define cursor-composition control, two cursor colors, and cursor floating-point scale/bias. The control fields include expansion mode, alpha enable, mode, format, degamma, 2-bit alpha, pre-multiply alpha, and cursor truncation or bit-depth related controls visible in the masks.

Together these fields are the fixed hardware contract for programming pixel format conversion, alpha handling, color keying, pre-CSC matrices, and cursor blending in the first two DPP/CNVC instances.

### DSCL/Scaler For Instances 0 And 1

`DSCL0_*` and `DSCL1_*` provide the scaler and line-buffer fields for each pipe:

- Coefficient RAM tap select/data fields for loading scaler coefficients.
- Scaler mode, coefficient RAM selection, chroma coefficient mode, and current-selection status.
- Tap-control fields for horizontal/vertical and chroma luma taps.
- DSCL control, 2-tap control, manual replicate control.
- Horizontal and vertical scale ratios and initial phases, including chroma and bottom-field variants.
- Black color, update pending, and autocal pipe coordination fields.
- Extended overscan, OTG blanking, recout start/size, MPC size.
- Line-buffer data format, memory partitioning, vertical counters.
- DSCL LUT/LB memory power force/disable/status fields across LB groups G1-G6.
- OBUF bypass/full-buffer/half-width/out-hold controls and OBUF memory power controls/status.

These constants are central to timing-sensitive scaling, viewport setup, output-size programming, and low-power memory gating for the first two display pipes.

### CM Color Management For Instances 0 And 1

`CM0_*` and `CM1_*` define color-management fields after CNVC/DSCL:

- CM bypass and update-pending fields.
- Post-CSC mode/current state and two coefficient banks for 3x4 matrix coefficients.
- Gamut-remap mode/current state and two coefficient banks.
- Bias fields for Cr/R and Y/G/Cb/B.
- Gamma-correction control, LUT index/data/control, and host selection.
- Gamma correction RAM A and RAM B start, slope, base, end, offset, and 34-region definitions. Each region pair packs LUT offset and segment-count values for two adjacent expansion regions.
- HDR multiplier coefficient.
- Gamma correction memory power force/disable/status.
- CM dealpha enable and blend mode.
- Coefficient format selectors for bias, post-CSC, and gamut-remap fields.

For CM0 only, this chunk also includes `CM0_CM_TEST_DEBUG_INDEX`, with a debug index field and debug write-enable bit. CM1's corresponding region in this chunk ends at coefficient format, then transitions to `DC_PERFMON11`.

## Control Flow

There is no runtime control flow in this chunk. The constants are compiled into driver code and used when register helper macros generate read/modify/write masks, field shifts, and register metadata tables. Runtime control flow lives in consumers such as DC resource construction, DPP programming, DSCL/scaler programming, color-management programming, IRQ service setup, and DMUB register initialization.

The implicit "flow" is data-driven:

1. Register offset headers provide absolute or base-relative register addresses.
2. This `*_sh_mask.h` header provides per-field shifts and masks.
3. Hardware block register-list macros expand field names into per-block `shift` and `mask` structs.
4. Runtime code writes or reads fields with helper macros, relying on these exact constants for bit placement.

## State And Persistence Behavior

The header itself has no mutable state and no persistence. The state it describes is hardware state:

- DPP clock/reset/CRC state persists in hardware registers until reprogrammed or reset.
- CNVC, DSCL, and CM settings represent active display pipeline configuration, often latched or double-buffered by update-pending/current fields.
- Gamma LUT and piecewise region fields persist in CM hardware RAM/registers and are selected through A/B banks.
- Memory power control/status fields reflect display block SRAM power-gating policy and state.
- Perfmon fields configure counters and interrupts whose values/status persist until stopped, acknowledged, or reset.

Because many fields are double-buffered, banked, or status/ack sensitive, a wrong mask can cause persistent display misconfiguration rather than a simple compile-time failure.

## Dependencies And Integration Points

Direct includes of `dcn_3_5_1_sh_mask.h` in this source tree include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, paired with `dcn_3_5_1_offset.h` during DCN351 resource construction.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, where `FD_MASK` and `FD_SHIFT` populate DMUB-visible register mask/shift metadata.
- `drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`, which includes the same generated offset and mask headers for DCN351 IRQ service definitions.

The fields in this chunk are also tied to shared display component headers:

- DPP register-field lists in `dcn10_dpp.h`, `dcn30_dpp.h`, and `dcn35_dpp.h` reference DPP, CNVC, DSCL, and CM field names that resolve through this generated header on DCN351.
- Register helper macros in AMD display code assume the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming convention.
- Offset headers such as `dcn_3_5_1_offset.h` supply matching register addresses; masks without matching offsets are incomplete.

The numerical values are generated from ASIC register specifications. They should not be hand-edited except as part of a deliberate hardware-header update.

## Risks And Edge Cases

- The chunk begins and ends mid-logical areas: it starts after earlier `CURSOR0_3_DMDATA_CNTL` fields and ends before the rest of `DC_PERFMON11`. Merge-time research must not treat this chunk as a complete file-level map.
- Field names are contract-sensitive. Renaming a macro breaks downstream `TF_SF`, `DMUB_SF`, or `FD_MASK` expansions even when the numeric value is unchanged.
- Numeric drift is high impact: a one-bit shift/mask error can write unrelated hardware fields, causing display corruption, scaler programming errors, bad color transforms, lost CRC/debug signals, bad power-gating behavior, or stuck perfmon interrupts.
- The pipe-instance repetition is easy to desynchronize. Instance 0 and 1 definitions mostly mirror each other; accidental divergence may only affect multi-display or multi-plane configurations.
- Current/update-pending fields must remain aligned with programming sequences. Incorrect masks can make driver code believe a programming update completed when it did not.
- Power-control fields combine force, disable, mode, and status bits. Wrong values can keep SRAM powered unnecessarily or power down active pipeline resources.
- Perfmon status/ack bits are interrupt-sensitive. Bad masks can leave interrupts unacknowledged or acknowledge the wrong counter.
- Because this is a generated header, normal unit tests may not catch hardware semantic errors unless register tables are compared against authoritative specs or exercised on matching hardware.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, table-generation, and hardware-integration oriented:

- Build AMDGPU display code for DCN351 targets and confirm all `FD_MASK`, `FD_SHIFT`, `TF_SF`, and register-list expansions compile.
- Compare generated `dcn_3_5_1_sh_mask.h` values against AMD's authoritative ASIC register source for DCN 3.5.1.
- Boot or initialize DCN351 hardware and verify DPP construction, DMUB register initialization, and IRQ service setup do not hit missing-field or bad-register assertions.
- Exercise display modes that use scaling, color conversion, cursor blending, color keying, HDR/gamma LUT programming, and multi-pipe operation.
- Run CRC and perfmon/debug paths where available to confirm status, ack, and readback fields behave as expected.
- Check power-management/display-idle scenarios that touch DSCL, OBUF, cursor, and CM memory power controls.

Static review should focus on repeated block consistency between `0` and `1` instances, consistency with adjacent DCN 3.5.0/3.5.1/4.x generated headers where hardware specs indicate reuse, and exact pairing with matching offsets in `dcn_3_5_1_offset.h`.

### subset-b-002095: lines 17679-19896

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 17679-19896

## Scope

This chunk is a middle slice of AMDGPU's generated DCN 3.5.1 shift/mask header. It contains preprocessor constants only: no callable functions, structs, enums, storage objects, or local executable control flow. Its exported contract is the usual generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace, where each field macro describes the bit position and already-shifted mask for one DCN 3.5.1 display hardware register field.

The range starts in the tail of the `DC_PERFMON11` monitor block, then covers the DPP2 display pipe from top-level DPP control through CNVC, DSCL, CM, and `DC_PERFMON12`. It then repeats the same kind of register-field surface for DPP3 through CNVC, DSCL, CM, and `DC_PERFMON13`. The chunk ends at the beginning of `FMT0` output formatter fields after clamp, dynamic expansion, formatter control, and the first few bit-depth-control masks. Adjacent chunks own the preceding `DC_PERFMON11` context and the rest of `FMT0`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, network, or persistent-disk behavior.

## Purpose

The purpose of this header range is to provide ASIC-specific field metadata for DCN 3.5.1 display pipe and formatter programming. Runtime display code can refer to logical fields through register-table macros while this generated header supplies exact bit geometry for the DCN 3.5.1 register database.

The covered hardware areas are:

- `DC_PERFMON11` tail fields: monitor counter-off interrupt type, perfmon clock enable, run-enable start/stop selectors, counter interrupt status/ack bits, high current-value bits, and high/low perfmon readback fields.
- `DPP_TOP2` and `DPP_TOP3`: per-pipe DPP clock enable/gate-disable fields, soft resets for CNVC/DSCL/CM/OBUF, DPP CRC capture values/control, and host-read rate control.
- `CNVC_CFG2` and `CNVC_CFG3`: surface pixel format, alpha plane enable, format conversion/bypass/crossbar, floating-point conversion bias/scale, color keyer ranges, alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha fields.
- `CNVC_CUR2` and `CNVC_CUR3`: cursor enable/mode/pixel-alpha/update status and fixed cursor colors plus floating-point cursor scale/bias.
- `DSCL2` and `DSCL3`: scaler coefficient RAM access, scaler mode, tap control, two-tap sharpening, manual replication, horizontal/vertical scale ratios and initial phases, chroma scale/init fields, black color, update/autocal, overscan, OTG blanking, recout/MPC dimensions, line-buffer format/memory partitioning, vertical counters, DSCL memory power/status, and OBUF control/power fields.
- `CM2` and `CM3`: DPP color-management bypass/update, post-CSC matrices, gamut-remap matrices, bias registers, gamma-correction controls and LUT ports, RAM A/B piecewise-region descriptors, HDR multiplier, CM memory power/status, dealpha, and coefficient-format fields.
- `DC_PERFMON12` and `DC_PERFMON13`: performance-counter event selection, counter control, state/readback, perfmon control, current-value comparison, interrupt status/ack, and low/high counter readback.
- `FMT0` beginning: output formatter component clamps, dynamic expansion controls, pixel encoding/subsampling/double-buffer status, and the start of truncation/spatial/temporal dither bit-depth controls.

## Important APIs, Types, And Macros

There are no C APIs or concrete types in this chunk. The important interface is the generated macro pattern:

- `*_SHIFT` gives a field's least-significant bit position.
- `*_MASK` gives the field mask in its final register position.
- Register names encode hardware block and instance, such as `DPP_TOP2_DPP_CONTROL`, `CNVC_CFG2_FORMAT_CONTROL`, `DSCL2_SCL_MODE`, `CM2_CM_GAMCOR_CONTROL`, `DPP_TOP3_DPP_CONTROL`, `CM3_CM_GAMCOR_RAMB_REGION_32_33`, `DC_PERFMON13_PERFCOUNTER_CNTL`, and `FMT0_FMT_CONTROL`.

The DPP top fields are the gate and reset boundary for the per-pipe blocks. `DPP_TOP*_DPP_CONTROL` exposes `DPP_CLOCK_ENABLE`, multiple `DPPCLK`/`DISPCLK` gate-disable fields, and `DPP_TEST_CLK_SEL`. `DPP_TOP*_DPP_SOFT_RESET` exposes reset bits for `CNVC`, `DSCL`, `CM`, and `OBUF`. The `DPP_TOP*_DPP_CRC_*` registers describe CRC result components and a control register with enable, continuous/one-shot, source, stereo, interlace, pixel format, cursor format, and mask fields.

The CNVC groups describe the input converter stage. `CNVC_CFG*_FORMAT_CONTROL` is the main control surface for format expansion, 16-bit conversion, alpha enable, converter bypass and MSB alignment, positive clamps, update-pending readback, and RGB channel crossbar selection. `FCNV_FP_BIAS_*` and `FCNV_FP_SCALE_*` provide 19-bit-style bias/scale fields used by DCN 3.5 DPP code for floating-point conversion. The color keyer registers pack low/high thresholds into 16-bit halves for alpha/red/green/blue, and `ALPHA_2BIT_LUT` packs four 8-bit alpha entries into one register.

The CNVC pre-processing fields include pre-dealpha/realpha enable controls, `PRE_CSC_MODE` current-mode readback, two banks of packed 16-bit pre-CSC matrix coefficients, coefficient-format selection, and pre-degamma mode/select fields. Cursor fields under `CNVC_CUR*` expose hardware cursor enable/mode/ROM/pixel-alpha/update status and 24-bit colors plus packed scale/bias.

The DSCL groups are the scaler programming surface. `SCL_COEF_RAM_TAP_SELECT` selects tap pair, phase, and filter type; `SCL_COEF_RAM_TAP_DATA` packs even/odd tap coefficients and coefficient enable bits. `SCL_MODE` carries DSCL mode, coefficient RAM selection/current readback, chroma/alpha coefficient modes, and read selector. `SCL_TAP_CONTROL` programs luma and chroma horizontal/vertical tap counts, while `DSCL_2TAP_CONTROL` programs two-tap hardcoded coefficient and sharpening controls. Scale ratio and init registers use wide fixed-point masks for luma/chroma horizontal/vertical paths, including bottom-field variants.

The DSCL geometry and buffering fields describe how the scaler presents data downstream. Overscan and blanking fields pack start/end or left/right/top/bottom values; `RECOUT_*` and `MPC_SIZE` describe output rectangles; `LB_DATA_FORMAT` and `LB_MEMORY_CTRL` describe line-buffer format and partitioning; `LB_V_COUNTER` exposes luma/chroma vertical counters. `DSCL_MEM_PWR_CTRL` and `DSCL_MEM_PWR_STATUS` enumerate force/disable/state fields for LUT memory and six line-buffer groups, plus `LB_MEM_PWR_MODE`. `OBUF_CONTROL` and `OBUF_MEM_PWR_CTRL` cover output-buffer bypass/full-buffer/hold-count and memory-power controls.

The CM groups describe the color-management block. Post-CSC and gamut-remap matrices pack pairs of 16-bit coefficients, including alternate `_B_` banks. `CM_CONTROL`, `CM_POST_CSC_CONTROL`, `CM_GAMUT_REMAP_CONTROL`, and `CM_GAMCOR_CONTROL` carry bypass, update-pending, mode, select, PWL-disable, and current-mode/current-select status fields. Bias registers provide packed Y/G and Cb/B values plus a separate Cr/R value. `CM_HDR_MULT_COEF` contains the HDR multiplier coefficient.

The gamma-correction interface is indexed and banked. `CM*_CM_GAMCOR_LUT_INDEX`, `CM*_CM_GAMCOR_LUT_DATA`, and `CM*_CM_GAMCOR_LUT_CONTROL` define LUT index, data, write-color mask, read-color selection, host selection, and config mode. RAM A and RAM B each have per-channel start, start slope, start base, end base, end/slope, and offset registers. Region-pair registers from `REGION_0_1` through `REGION_32_33` pack LUT offsets and segment counts for two PWL regions into one register.

The perfmon groups use a repeated field contract. `DC_PERFMON12_*` and `DC_PERFMON13_*` define event selection, counted current-value source, increment mode, hardware control, run-enable mode, restart, interrupt enable, off-mask, active status, and counter selector fields. They also expose counter state for counters 0-7, perfmon state/report-count/control bits, counter-off interrupt status/ack, current-value compare status/ack bits, and low/high readback fields.

The `FMT0` fields at the end are output-formatter metadata. Clamp component registers pack lower/upper limits for R/G/B. `FMT_DYNAMIC_EXP_CNTL` enables dynamic expansion and selects expansion mode. `FMT_CONTROL` defines stereo sync override, spatial-dither frame-counter behavior, pixel encoding, subsampling mode/order, CbCr bit-reduction bypass, and double-buffer update-pending status. `FMT_BIT_DEPTH_CONTROL` begins the truncation and dither field list but is not complete in this chunk.

## Control Flow

This header range has no local control flow. Runtime behavior is created by consumers that include `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`, build register tables, and use display register helpers for MMIO reads and writes.

A typical DCN 3.5.1 path is:

1. DCN351 resource, IRQ, DMUB, and related display code includes the DCN 3.5.1 offset and shift/mask headers.
2. Resource construction macros such as `SRI_ARR(reg_name, block, id)` paste logical register names onto generated instance names such as `regCNVC_CFG2_FORMAT_CONTROL`, `regDSCL3_SCL_MODE`, or `regFMT0_FMT_CONTROL`, while field macros such as `TF_SF(...)` paste logical field names onto `REGISTER__FIELD_MASK` or `REGISTER__FIELD__SHIFT`.
3. Runtime helpers such as `REG_READ`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, and related `reg_helper.h` operations use the table-built offsets, masks, and shifts to perform read/modify/write operations.
4. Higher-level DPP, DSCL, CM, OPP, IRQ, and DMUB code sequences those operations around pipe enable, update locks, blanking, power transitions, LUT programming, or status polling.

Visible examples in this tree include `dcn351_resource.c`, which includes the DCN 3.5.1 headers and defines base/offset/field expansion macros; `dcn35_dpp.c`, which programs DPP clock enable and `FCNV_FP_BIAS_*`/`FCNV_FP_SCALE_*` fields through DPP register helpers; and `dmub_dcn351.c`, where `dmub_srv_dcn351_regs_init()` expands DCN35 register and field lists using the DCN 3.5.1 offset and shift/mask headers. The header itself does not encode sequencing rules, waits, or policy decisions.

## State And Persistence Behavior

The file itself stores no runtime state and persists nothing. It describes hardware register state whose lifetime is controlled by display pipe programming, DPP/OPP power, modesets, plane updates, cursor updates, suspend/resume, and GPU reset.

State represented by this chunk includes:

- DPP clock, clock-gating, soft-reset, CRC, and host-read state for DPP2 and DPP3.
- CNVC conversion state: input pixel format, alpha plane, format expansion/conversion/bypass, channel crossbar, FP bias/scale, color keying, alpha LUT, pre-CSC/pre-degamma/pre-dealpha/pre-realpha, and cursor color/format state.
- DSCL scaler state: filter taps and coefficient RAM contents, scaler mode, scale ratios, initial phases, two-tap sharpening, overscan, output rectangles, line-buffer partitioning, update-pending/autocal state, and memory-power state.
- CM color state: post-CSC and gamut-remap matrices, gamma-correction LUT index/data/configuration, PWL RAM A/B region descriptors, biases, HDR multiplier, memory-power state, and dealpha/coefficient-format controls.
- Perfmon diagnostic state: selected events, run/stop selectors, active/restart/interrupt controls, compare-value interrupt status, counter states, and counter readback values.
- FMT0 formatter state for clamp, dynamic expansion, pixel encoding, subsampling, double-buffer status, and the start of truncation/dither controls.

Several fields are status-only or status-like readbacks, such as update-pending, current-mode/current-select, memory-power state, perfmon active/status bits, and double-buffer update-pending. Several others are write controls that affect live hardware immediately or at a later synchronized update point. Indexed LUT registers are especially stateful: writes through `CM_GAMCOR_LUT_INDEX` and `CM_GAMCOR_LUT_DATA` modify table entries and the current index influences following accesses.

Bad register values can persist until the affected pipe is reprogrammed, reset, power-cycled, or the GPU is reset. Some display programming is restored during modeset or suspend/resume paths, but this generated header has no restore logic; it only defines the bit layout that restore/programming code depends on.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides matching register offsets and base indices. These shift/mask macros are only correct when paired with the DCN 3.5.1 offset header and the DCN351 register-instance layout.

Important visible integration points include:

- `display/dc/resource/dcn351/dcn351_resource.c`, which includes `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`, then expands `SR`, `SRI`, `SRI_ARR`, and related macros to build register tables using `ctx->dcn_reg_offsets`.
- `display/dc/dpp/dcn35/dcn35_dpp.h` and `display/dc/dpp/dcn35/dcn35_dpp.c`, which inherit DCN3 DPP field lists and add DCN35-specific DPP control fields. Runtime code uses the generated field masks/shifts to program DPP clock control and CNVC FP bias/scale.
- `display/dc/resource/dcn32/dcn32_resource.h` and later resource list patterns, which show how logical DPP registers such as `CM_GAMCOR_*`, `DSCL_*`, `FORMAT_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, `DPP_CONTROL`, `FCNV_FP_*`, and `FMT_*` are table-driven by generated instance names.
- `display/dmub/src/dmub_dcn351.c`, where `dmub_srv_dcn351_regs_init()` fills DMUB register offsets, masks, and shifts by expanding register and field lists over this header.
- `display/dc/irq/dcn351/irq_service_dcn351.c`, which includes the same DCN 3.5.1 generated headers for IRQ source metadata.
- OPP/formatter code through common `FMT` register lists, because this chunk begins the `FMT0` field layout used for output formatting, dithering, and pixel-encoding programming.

The generated namespace is cross-generation but not interchangeable. Nearby headers such as `dcn_3_5_0_sh_mask.h`, `dcn_3_2_1_sh_mask.h`, `dcn_3_6_0_offset.h`, and later DCN 4.x headers carry many similar names, but field availability, offsets, and exact masks may differ. Consumers must bind the correct offset and mask header pair for the target ASIC.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Shift and mask constants compile cleanly even when wrong, but a bad constant can update the wrong field, leave stale bits behind, truncate coefficient data, corrupt a neighboring field, or decode status incorrectly.

Chunk-boundary risk is real here. The first lines are only the tail of the `DC_PERFMON11` block, and the final lines stop before the rest of `FMT0_FMT_BIT_DEPTH_CONTROL` and later formatter fields. The final per-file report must merge adjacent chunks before making whole-block claims about perfmon11 or FMT0.

Instance pairing is critical. Fields named with `2` must match `DPP_TOP2`, `CNVC_CFG2`, `DSCL2`, `CM2`, and the corresponding generated offsets; fields named with `3` must match the DPP3/CNVC3/DSCL3/CM3 offsets. Copying a mask from one generation or instance into another table can create display failures that look like runtime sequencing bugs.

Color-management fields are precision-sensitive. Matrix coefficient masks, gamma LUT data widths, RAM A/B region offsets, segment counts, HDR multiplier, and coefficient-format bits directly affect visible output. Incorrect masks can cause color shifts, gamut errors, banding, broken HDR behavior, or LUT programming that appears to succeed but produces the wrong transfer curve.

Scaler and geometry fields can fail only for specific modes. Bad scale ratios, initial phases, tap counts, coefficient RAM selectors, overscan, recout/MPC dimensions, line-buffer partitions, or chroma fields can cause distortion, chroma misalignment, clipping, underflow, or blanking that appears only with certain pixel formats, rotations, scaling ratios, or multi-plane layouts.

Power and reset fields can be hazardous. DPP clock enable/gating, DPP soft reset, DSCL memory power, OBUF memory power, and CM memory power controls interact with live hardware availability. Incorrect programming can force memories off while active, leave blocks in reset, or make status bits appear stuck.

Indexed LUT programming has sequencing risk. The header defines index/data/control field geometry but not the ordering requirements for host selection, color write masks, config modes, double buffering, update locks, or pipe blanking. Callers must follow DC and hardware programming rules.

Perfmon fields are diagnostic-sensitive. Event selection, counter select, counter-off comparison, interrupt enable/status/ack, and readback masks may return plausible values even when the wrong event or counter is selected. That can hide performance regressions or mislead debug work without directly breaking display output.

`FMT0` fields at the end are incomplete in this chunk. Truncation and dithering controls are packed near high bits and often interact with random seed and temporal pattern registers in later lines. Partial review of this chunk alone is not enough to validate all output formatter behavior.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Compile coverage for DCN351 resource construction, IRQ service, DMUB register initialization, DPP programming, and OPP/formatter users that include the generated DCN 3.5.1 headers.
- Generated-register consistency checks that every `*_MASK` has a matching `*_SHIFT`, every mask width matches the hardware register database, and every register referenced by resource lists exists in `dcn_3_5_1_offset.h`.
- Cross-generation diffs against AMD's authoritative DCN 3.5.1 register database and nearby DCN 3.5.0/3.6/4.x headers, with expected differences explicitly reviewed.
- DPP clock/reset tests that exercise DPP2/DPP3 enable, clock gating, soft reset, CRC capture, host reads, runtime PM, display idle, modeset, and suspend/resume.
- CNVC tests for pixel formats, alpha plane enable, format expansion/conversion, bypass, channel crossbar, color keying, FP bias/scale, pre-CSC, pre-degamma, pre-dealpha/realpha, and cursor color/alpha behavior.
- DSCL tests for bypass, upscaling/downscaling, non-integer ratios, 4:2:0 chroma paths, coefficient RAM programming, two-tap sharpening, overscan, recout/MPC changes, multi-pipe layouts, and line-buffer partitioning.
- CM tests for post-CSC, gamut remap, gamma correction RAM A/B programming, HDR multiplier, bias, dealpha, coefficient format, LUT readback, current-mode readback, and restore after suspend/resume.
- Memory-power tests for DSCL LUT/LB groups, OBUF, and CM/GAMCOR power force/disable/state fields under active display, idle, hotplug, and reset paths.
- Perfmon tests that select known events, start/stop/restart counters, validate low/high readback, compare-value interrupt behavior, status/ack bits, and counter-state fields.
- FMT0 tests for clamp, dynamic expansion, pixel encoding, subsampling, truncation, spatial/temporal dither, and double-buffer update-pending once the following chunk's formatter fields are included.

Regression symptoms from bad constants include blank display output, distorted or clipped scaling, chroma errors, cursor artifacts, alpha/color-key mistakes, visible color shifts or banding, HDR/gamut failures, stuck update-pending bits, failed memory-power transitions, broken CRC capture, incorrect dithering, misleading perf counters, or failures that appear only on DCN 3.5.1 ASICs.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dcn_3_5_1_sh_mask.h`. The preceding chunk owns the beginning of the `DC_PERFMON11` context before line 17679. The following chunk owns the rest of `FMT0_FMT_BIT_DEPTH_CONTROL` and subsequent formatter/register blocks after line 19896. The merge/reconciliation lane should treat this document as the DPP2/DPP3 CNVC/DSCL/CM/perfmon middle portion plus the start of FMT0 for the full DCN 3.5.1 shift/mask contract.

### subset-b-002096: lines 19897-22113

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 19897-22113

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata. It contains no executable C code; it publishes preprocessor constants that describe field bit positions and field masks inside DCN hardware registers. The matching offset header supplies register addresses, while this shift/mask header supplies the layout used by AMDGPU display code to pack and decode MMIO register values without clobbering unrelated bits.

The assigned range starts in the middle of `FMT0_FMT_BIT_DEPTH_CONTROL` masks, then covers output formatter, display pattern generator, OPP buffer, OPP pipe, OPP pipe CRC, DSCRM, DC perfmon, ODM/OPTC input, OTG0 timing-generator, and the first half of OTG1 timing-generator field definitions. It ends at `OTG1_OTG_CRC3_DATA_B__CRC3_B_CB_MASK`; the companion `CRC3_C` mask and later OTG1 CRC signature/static-screen/3D/global-sync/DRR fields continue in the next chunk.

Although this source lives under a local `ceph-client` mirror path, this file is AMDGPU display-driver hardware metadata and is not related to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, or locks in this chunk. The effective API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for a field in a hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.
- Instance prefixes such as `FMT0_`, `DPG2_`, `OPPBUF3_`, `ODM1_`, `OTG0_`, and `OTG1_` identify repeated display-pipe or timing-generator register instances.

The range contains 2,217 macro lines covering 337 distinct register names. Major families are:

- `FMT0_` through `FMT3_`: output formatter fields for clamp bounds, dynamic expansion, stereo sync override, pixel encoding, subsampling, CbCr bit-reduction bypass, double-buffer update-pending state, truncation, spatial/temporal dithering, FRC selectors, random seeds, clamp color format, side-by-side stereo active width, 4:2:0 memory power controls, and 4:2:2 left-edge behavior. `FMT0` is partial because the line range starts after its early bit-depth shift definitions.
- `DPG0_` through `DPG3_`: display pattern generator enable/mode, dynamic range, bit depth, horizontal and vertical resolution selectors, ramp offsets/increments, active dimensions, two-color RGB/YCbCr pattern values, segment offsets, and double-buffer-pending status.
- `OPPBUF0_` through `OPPBUF3_`: OPP buffer active width, display segmentation, overlap pixels, pixel repetition, double-buffer-pending state, 3D vertical active-space sizes, dummy data, and padded segment pixel count.
- `OPP_PIPE0_` through `OPP_PIPE3_`: OPP pipe clock enable/status and digital bypass fields.
- `OPP_PIPE_CRC0_` through `OPP_PIPE_CRC3_`: OPP pipe CRC enable, continuous mode, stereo/interlace mode, pixel/source select, one-shot pending, CRC masks, and ARGB/C result fields.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`: top-level OPP fine-grain clock-gating and ambient-backlight-management mux fields.
- `DSCRM0_` through `DSCRM3_`: DSC forwarding configuration, including forward enable, OPP pipe source, enable status, power-down force, and power-down state.
- `DC_PERFMON14_*`: DC performance monitor 14 fields for counter control, selection, enable/clear, counter state, threshold/current values, interrupt status/ack bits, and high/low counter readback.
- `ODM0_` through `ODM3_`: OPTC input soft reset, underflow interrupt/status/clear/current fields, data source segment count and source selection, DSC data format/mode, bytes-per-pixel, segment and slice width, input clock control, memory selection/status, spare register, and double-buffer-pending state.
- `OTG0_*`: a broad timing-generator surface for horizontal/vertical totals, blanking, syncs, triggers A/B, force-count-now, master enable, stereo/interlace, pixel readback, status/position/frame counters, snapshots, interrupt masks/types/status/clears, update locks, double-buffer state, vertical interrupt 0/1/2, CRC controls/windows/results/signature masks, static-screen detection, 3D structure, global sync lock, DRR timing/status, DTO constants, request controls, DSC start position, pipe update status, and spare registers.
- `OTG1_*`: the same timing-generator layout begins for instance 1 and runs through CRC data registers in this chunk.

## Control Flow

This header has no runtime control flow. Runtime use is indirect and macro-driven:

1. DCN 3.5.1 resource and DMUB code include `dcn_3_5_1_offset.h` and this `dcn_3_5_1_sh_mask.h` header.
2. Register-table macros such as `SR`, `SRI`, `SF`, and block-specific wrappers paste register and field tokens into names from this file.
3. Constructors populate per-block offset, shift, and mask tables for OPP, DSC/DSCRM, OPTC/ODM/timing-generator, IRQ, DMUB-accessible registers, and related display resources.
4. Operational code later uses helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_SET`, `REG_GET`, and `REG_WAIT`. Those helpers use the shifts and masks from this chunk to update hardware fields while preserving other register bits.

The macros do not encode programming order. Modeset and validation paths still need to apply hardware sequencing rules: lock and unlock updates, wait for double-buffer-pending bits to clear, program timing changes around blanking boundaries, clear sticky interrupt/status bits correctly, and sequence DSC/ODM/OPP/OTG changes with pipe ownership.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- FMT registers hold per-output-pipe color/output formatting state: clamp ranges, pixel encoding, subsampling, truncation, dither mode/depth, temporal dither state, random seeds, 4:2:0 memory power state, 4:2:2 edge handling, and update-pending readback.
- DPG registers hold diagnostic/test-pattern state used for validation, blank pattern generation, and controlled output during transitions.
- OPPBUF and OPP pipe registers hold active-width, segmentation, pixel repetition, 3D dummy-data, clock, and bypass state for the output pixel processor path.
- OPP pipe CRC and OTG CRC registers hold capture configuration, CRC windows, source selections, masks, one-shot pending bits, and captured result data used by debug and automated validation paths.
- DSCRM registers hold DSC-to-OPP forwarding state and status, including enable, source pipe, and power-down fields.
- ODM/OPTC input registers hold segment routing, input/output segment counts, DSC mode, bytes-per-pixel, segment/slice widths, input clock enable/status, underflow flags, memory selection, and double-buffer state.
- OTG registers hold timing-generator state: programmed timings, dynamic refresh totals, triggers, interrupts, status counters, update locks, vertical interrupt positions, stereo/interlace control, global sync, DRR windows, DTO programming, DSC start position, pipe update status, static-screen detection, and spare registers.
- DC perfmon 14 registers hold programmable performance counter selection, thresholds, current values, interrupt bits, enable/clear fields, and readback state.

Persistence is hardware-defined. Many configuration bits remain until modeset reprogramming, power gating, suspend/resume, or ASIC reset. Status, pending, interrupt, snapshot, one-shot, clear, and perf-counter fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated header only gives bit layout; it does not describe access type or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DCN 3.5.1 register database and with these local consumers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, the matching register offset/base-index header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which includes the DCN 3.5.1 offset and shift/mask headers and uses `FD_MASK`/`FD_SHIFT` through `DMUB_DCN35_FIELDS()` to initialize DMUB register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which includes this header when constructing DCN 3.5.1 display resources and expanding register/field tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h`, `dcn10_opp.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn35/dcn35_opp.c`, which consume FMT, OPPBUF, OPP pipe, OPP CRC, and DSCRM field names for color depth, dithering, CRC readback, and OPP register-state capture.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn35/dcn35_dsc.c` and `dcn35_dsc.h`, which use `DSCRM_DSC_FORWARD_CONFIG` fields to query and program DSC forwarding.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.c` and `dcn35_optc.h`, which consume ODM/OPTC and OTG masks for ODM segment source selection, CRC configuration, timing-generator status, and update sequencing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c` and the shared DCN35 IRQ support, which rely on OTG interrupt mask/status/clear/type field definitions.
- Shared hardware sequencing code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/` and `dc/hwss/dcn351/`, which coordinates the modeset, blanking, power, pipe, and update-lock paths that ultimately touch these registers.

The integration contract is token spelling plus numeric correctness. A missing or renamed macro usually fails compilation through token-pasted field tables. A stale or incorrect numeric shift/mask can compile cleanly but program the wrong hardware bits at runtime.

## Risks And Edge Cases

- The chunk boundary is artificial. It begins after the `FMT0_FMT_BIT_DEPTH_CONTROL` shift definitions and early masks, and ends one line before `OTG1_OTG_CRC3_DATA_B__CRC3_C_MASK`. File-level analysis must merge adjacent chunks to avoid treating split register definitions as absent.
- These are untyped integer constants. A wrong mask or shift can corrupt adjacent register fields with no compiler diagnostics.
- FMT bit-depth, dithering, clamp, pixel-encoding, subsampling, and 4:2:0/4:2:2 fields directly affect visible output. Errors can present as banding, wrong color format, corruption on subsampled modes, bad stereo formatting, or failed update-pending waits.
- DPG fields are often diagnostic or transition-path tools. Incorrect dimensions, segment offsets, colors, or pending-state masks can make pattern generation or blanking validation misleading.
- OPP clock/bypass and OPPBUF segmentation fields are clock/power and pipe-topology sensitive. Bad masks can leave the OPP path clock gated, report false clock state, bypass processing, or break multi-segment output.
- DSCRM forwarding and ODM/OPTC segment-selection fields are high-risk for DSC and ODM combine. Wrong source pipe, segment count, DSC mode, bytes-per-pixel, or slice/segment width can break high-bandwidth modes even when simple single-pipe modes still work.
- OTG timing, vertical interrupt, trigger, force-count, update-lock, and double-buffer fields are sequencing-sensitive. Incorrect fields can cause missed vblank/vupdate interrupts, stuck update-pending waits, bad dynamic-refresh behavior, global-sync failures, or display hangs during modeset.
- CRC fields are used as validation signals. Incorrect OTG/OPP CRC source, window, mask, or result fields can invalidate automated display tests and obscure real rendering regressions.
- Perfmon fields are diagnostic but side-effect-sensitive; wrong enable/clear/ack/threshold masks can hide overflows or produce misleading performance telemetry.

## Test Signals

Useful validation combines generated-header checks with hardware/display behavior:

- Build AMDGPU/DC with DCN 3.5.1 enabled. Token-pasted tables in resource, DMUB, OPP, DSC, OPTC, and IRQ code should catch missing or renamed macro definitions.
- Mechanically verify each `__SHIFT` in the range has the expected matching `_MASK`, and verify masks align with the shift and expected bit width. Split boundary definitions should be reconciled with neighboring chunks before flagging mismatches.
- Diff this range against AMD's authoritative DCN 3.5.1 register database and nearby generated headers when compatibility is expected.
- Exercise normal and repeated modesets on all available pipes: enable/disable, blank/unblank, suspend/resume, hotplug, resolution/refresh changes, and pipe reassignment.
- Exercise color-format coverage that depends on FMT fields: 6/8/10/12 bpc, truncation, spatial and temporal dithering, RGB/YCbCr, 4:2:0, 4:2:2, and stereo cases.
- Exercise DSC and ODM paths: DSC enable/disable, DSC forwarding to OPP, high-bandwidth modes, ODM combine/split, segment source changes, and DSC slice width or bytes-per-pixel changes.
- Exercise OPP and OTG CRC debug paths in one-shot and continuous modes, with windowed CRC, stereo/interlace modes, and expected frame signatures.
- Monitor kernel logs, DC traces, hardware readback, debugfs CRC output, and display output for underflow, stuck double-buffer/update-pending bits, missed interrupts, CRC mismatches, black screens, link fallback, corruption, or timing-generator wait timeouts.

## Cross-Chunk Notes

Adjacent chunks are required for a complete file-level report. The previous chunk contains the beginning of `FMT0_FMT_BIT_DEPTH_CONTROL` and earlier FMT0 fields. The next chunk continues `OTG1_OTG_CRC3_DATA_B` with `CRC3_C_MASK` and then covers OTG1 CRC signature masks, static-screen controls, 3D structure, global sync, DRR, DTO, request, DSC start, pipe update, and spare fields.

### subset-b-002097: lines 22114-24331

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 22114-24331

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and bit masks used by AMDGPU display code when programming DCN timing generators, shared OPTC controls, ODM memory power controls, display performance counters, and DC I2C/DDC hardware.

The requested slice begins at the tail of the `OTG1` CRC data masks and static-screen/timing-generator fields, covers a complete `OTG2` field family, covers most of the `OTG3` field family, then moves into shared `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_*`, `DC_PERFMON15_*`, and `DC_I2C_*` field definitions. The range ends inside `DC_I2C_READ_REQUEST_INTERRUPT`: it includes all read-request shift definitions and only the first mask line for DDC1. Adjacent chunks are required for the full register's mask set.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or direct includes in this chunk. Its public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the right-shift count used to extract or place a field in a 32-bit MMIO register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used by `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, and related AMD display register helpers.

Major macro families in this slice:

- `OTG1_OTG_*`: tail fields for CRC3, CRC signature masks, static-screen detection, 3D structure control, global sync, master update lock, GSL configuration, double-buffer lock windows, DRR timing/status, DSC start position, pipe update status, and OPTC request/spare fields.
- `OTG2_OTG_*`: a full timing-generator instance field set, including horizontal and vertical timing, triggers, force-count/force-vsync controls, master enable, interlace, pixel readback, status counters, stereo control/status, snapshots, interrupts, update lock, double-buffer status, vertical interrupt positions, CRC controls/windows/data, static screen, global sync/update locks, DRR, M/N DTO, DSC position, and pipe update status.
- `OTG3_OTG_*`: the same timing-generator field pattern for a third instance, starting with horizontal timing and running through DRR/DTO/DSC/update/spare fields before the shared blocks.
- `GSL_SOURCE_SELECT` and `OPTC_CLOCK_CONTROL`: global swap lock source selection and OPTC clock gating/test-clock fields.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS`: per-memory-slice power force/disable/status fields plus unassigned and vblank power modes.
- `DC_PERFMON15_*`: display performance monitor fields for counter control, counter state, perfmon state, interrupt/ack/status, high/low compare or read values, counted value type, hardware stop selection, run-enable selection, and counter value storage.
- `DC_I2C_*`: I2C control, arbitration, interrupt, software status, per-DDC hardware status, per-DDC speed/setup, transaction descriptors, data FIFO/index access, EDID detect controls, and read-request interrupt fields.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from generated-token consumers:

1. DCN 3.5.1 resource, IRQ, and DMUB code includes this file together with `dcn_3_5_1_offset.h`.
2. Register-list macros in `dcn351_resource.c` and related headers paste symbolic names into constants such as `OTG2_OTG_CONTROL__OTG_MASTER_EN_MASK` or `DC_I2C_CONTROL__DC_I2C_GO__SHIFT`.
3. Static shift/mask tables such as `optc_shift`, `optc_mask`, I2C shift/mask tables, HW sequencer masks, IRQ source descriptors, and DMUB register masks are initialized from these macros.
4. Runtime code then sequences the hardware through register helpers. Timing-generator code uses the OTG/OPTC masks for modeset, vblank/vupdate handling, CRC capture, dynamic refresh, stereo/interlace, and update locking. I2C/DDC code uses the I2C masks for EDID/DDC transactions. IRQ service code uses interrupt status/clear/enable masks for vblank, vline, vupdate, hotplug, and related display interrupts.

The masks do not encode ordering rules. Consumers must still sequence power, clock enablement, update locks, interrupt acknowledgment, double-buffer commits, timing changes, and I2C arbitration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes fields inside MMIO-backed display hardware registers. The represented state includes:

- Timing-generator state for OTG instances 1-3: master enable, horizontal/vertical totals, blanking/sync windows, counters, frame/vblank/vupdate/vready status, force triggers, stereo/interlace state, snapshots, CRC windows/data, DRR timing, DSC position, and update-pending state.
- Synchronization state: global swap lock source selection, per-OTG GSL enable/master/delay/window configuration, master update locks, and vupdate keepout windows.
- Interrupt state: vertical interrupt positions/status/clear/type fields, global sync status/clear fields, DRR timing interrupt fields, static-screen CPU interrupt fields, I2C hardware-done/read-request interrupt fields, and performance counter interrupt/status/ack fields.
- Power and clock state: OPTC clock gate/test-clock bits and ODM memory force/disable/status fields.
- I2C/DDC transaction state: software/hardware ownership arbitration, transaction descriptors, selected DDC channel, go/reset bits, prescale/threshold/timing, per-DDC enable/setup, EDID detect control/status, data FIFO/indexing, and software status outcomes such as done, timeout, abort, overflow, and stopped-on-NACK.

Register persistence is hardware-defined. Configuration fields generally remain until reprogrammed, power-gated, reset, or lost across suspend/resume. Status, interrupt, clear, ack, pending, busy, and data/FIFO fields may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive; this header only supplies bit positions and cannot distinguish those semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must match the sibling offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h` supplies the MMIO offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c` includes both generated headers and initializes DCN351 resource tables. Its `optc_shift` and `optc_mask` use `OPTC_COMMON_MASK_SH_LIST_DCN3_5(__SHIFT)` and `_MASK`, which expand into OTG/OPTC/GSL field definitions from this generated namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.h` defines the DCN3.5 OPTC mask-list macro and declares timing-generator operations such as CRC configuration, DRR programming, long-vtotal programming, FGCg control, and OTG disable waits.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.h` maps `DC_I2C_*` field definitions into `struct dce_i2c_shift` and `struct dce_i2c_mask`; `dce_i2c_hw.c` then uses them to program hardware I2C/DDC transactions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h` and `hw_ddc.c` use DDC setup and EDID-detect masks for connector detection flows.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c` includes this mask header for IRQ register descriptors and maps hardware source IDs to DAL IRQ sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c` initializes DMUB-visible field masks and shifts through `FD_MASK` and `FD_SHIFT`.

## Risks And Edge Cases

- Field drift is the central risk. These constants are untyped preprocessor values, so an incorrect shift or mask can compile cleanly while corrupting an unrelated register field at runtime.
- Repeated OTG instances are copy-sensitive. `OTG2` and `OTG3` should be structurally parallel, while this chunk only contains the tail of `OTG1`; an instance-specific typo may only appear with particular pipes, multi-display layouts, or timing-generator assignments.
- The chunk boundary is artificial. It starts after the first `OTG1_OTG_CRC3_DATA_B` shift/mask lines and ends before the rest of `DC_I2C_READ_REQUEST_INTERRUPT` masks, so file-level conclusions must be reconciled with adjacent chunks.
- Interrupt and clear/ack fields are side-effect-sensitive. Bad masks in vblank/vline/vupdate/DRR/static-screen/I2C/perfmon fields can cause missed interrupts, interrupt storms, stale pending bits, or lost acknowledgments.
- Update-lock, double-buffer, and keepout masks are timing-sensitive. A wrong field can cause updates to land outside vblank/vupdate windows, leading to tearing, underflow, cursor/plane update stalls, or modeset hangs.
- CRC, pixel readback, and perfmon fields affect diagnostics and validation. Errors may not break normal display output but can invalidate automated CRC tests, debug readbacks, performance telemetry, or interrupt-driven counter collection.
- I2C/DDC masks directly affect EDID and AUX-adjacent connector workflows. Incorrect transaction count, data index, arbitration, timeout, stop-on-NACK, prescale, or DDC setup fields can cause intermittent monitor detection failures that depend on cable, sink behavior, or bus speed.
- Power-management masks such as `OPTC_CLOCK_CONTROL` and `ODM_MEM_PWR_*` interact with clock gating and memory retention; wrong values can manifest only after idle, vblank power transitions, suspend/resume, or runtime power management.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build coverage for DCN351 display code with this header included by `dcn351_resource.c`, `irq_service_dcn351.c`, and `dmub_dcn351.c`; failures often show as missing token-pasted macro names or struct initializer mismatches.
- Display modeset tests across multiple pipes, especially configurations using OTG2 and OTG3, to exercise horizontal/vertical timing, master enable, vblank/vupdate/vready, double-buffer updates, and update-lock paths.
- CRC capture/readback tests, including windowed CRC and multiple CRC slots, to verify OTG CRC field masks.
- Vblank, vline, page-flip, vupdate, static-screen, and DRR interrupt tests to catch incorrect status, clear, mask, or type fields.
- Variable refresh rate / DRR and long-vtotal tests to exercise `OTG_DRR_*`, `OTG_V_TOTAL_*`, and trigger-window fields.
- Multi-display synchronized-update tests to exercise GSL source selection, GSL windows, master update lock, and vupdate keepout behavior.
- EDID/DDC tests over each exposed DDC engine, including NACK, timeout, repeated-start, and read-request cases, to validate `DC_I2C_*` control, transaction, status, setup, speed, and interrupt fields.
- Suspend/resume and runtime power-management tests to exercise OPTC clock gating and ODM memory power fields.
- Perf counter smoke tests, if available, to confirm `DC_PERFMON15_*` control/status/value/interrupt masks match the ASIC register layout.

### subset-b-002098: lines 24332-26548

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 24332-26548

## Purpose

This chunk is part of the generated DCN 3.5.1 shift/mask header for AMD display hardware. It does not implement functions or own runtime control flow; it defines compile-time bit positions and masks for MMIO register fields consumed by AMDGPU display code through generated register-access macros.

The covered range spans Display I/O, HPD, DC perfmon, DisplayPort AUX, and VPG generic packet fields. It starts in the middle of the `DC_I2C_READ_REQUEST_INTERRUPT` field group: the shift definitions and the first `DC_I2C_DDC1_READ_REQUEST_OCCURRED_MASK` line are immediately before this chunk, while lines 24332-24360 contain the rest of the masks. It also ends in the middle of `VPG0_VPG_MPEG_INFO0`, with only `VPG_MPEG_INFO_CHECKSUM` and `VPG_MPEG_INFO_MB0` shifts inside the chunk; the remaining shifts and masks continue after line 26548.

## Important macros and register fields

- `DC_I2C_READ_REQUEST_INTERRUPT__*` covers DDC1-DDC6 and DDCVGA read-request interrupt masks. Each DDC channel has `READ_REQUEST_OCCURRED`, `READ_REQUEST_INT`, `READ_REQUEST_ACK`, and `READ_REQUEST_MASK` fields packed in four-bit groups, plus global `DC_I2C_DDC_READ_REQUEST_ACK_ENABLE` and `DC_I2C_DDC_READ_REQUEST_INT_TYPE` bits. Because the chunk begins at line 24332, it omits the `DDC1_READ_REQUEST_OCCURRED_MASK` definition at line 24331 but includes the rest of the group.
- `DIO_SCRATCH0` through `DIO_SCRATCH7` expose full 32-bit scratch register payload masks. These are broad software/hardware mailbox-style registers rather than narrowly typed bitfields.
- `DIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS` provides per-DIG wake status bits for `DIGA` through `DIGG`, supporting DisplayPort ALPM wake detection.
- `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_CTRL2` define I2C and DP link memory light-sleep state, disable, and force bits for DPA-DPG. These fields are power-management controls/status for the Display I/O block.
- `DIO_POWER_MANAGEMENT_CNTL`, `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, and `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL` describe reset/busy controls, HDMI RX status timer behavior, and link-to-HPO encoder selection. Link control fields include `ENC_TYPE_SEL`, `HPO_HDMI_ENC_SEL`, and `HPO_DP_ENC_SEL`.
- `HPD0_DC_HPD_*` through `HPD4_DC_HPD_*` repeat hot-plug-detect status, toggle filter, fast-train, interrupt control, and control fields for five HPD instances in this chunk. They include sense/status bits, RX interrupt status, connection/disconnection filter timers, interrupt enables/acks, and polarity/routing controls.
- `DC_PERFMON16_*` defines one display performance monitor instance. It includes counter low/high reads, counter control, perfmon enable/state, counter-state windowing, counter profile/debug state, current-value latch controls, overflow/clear/status bits, and interrupt select/read-select fields.
- `DP_AUX0_*` through `DP_AUX4_*` repeat the AUX-channel field layout for five DP AUX instances. The blocks include AUX enable/reset/control, software transaction control/data/status, LTTPR link-service data/status, AUX register arbitration, interrupts, DPHY TX/RX timing controls and status, GTC sync control/error/status, and AUX PHY wake handshakes.
- `VPG0_VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG0_VPG_GENERIC_PACKET_DATA`, `VPG0_VPG_GSP_FRAME_UPDATE_CTRL`, `VPG0_VPG_GSP_IMMEDIATE_UPDATE_CTRL`, `VPG0_VPG_GENERIC_STATUS`, `VPG0_VPG_MEM_PWR`, and `VPG0_VPG_ISRC1_2_*` describe VPG0 generic packet RAM access, byte packing, frame/immediate update triggers for generic packet slots 0-14, update-pending status bits, conflict status/clear, VPG memory power, and ISRC data indexing/data bytes.

## Control flow and usage model

There is no direct control flow in this header. The runtime pattern is generated-register expansion:

1. DCN 3.5.1 code includes `dcn_3_5_1_offset.h` and this `dcn_3_5_1_sh_mask.h`.
2. Macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `SRI(...)`, and `SE_SF(...)` expand these constants into register tables or read/modify/write helpers.
3. Driver code writes packed register values or extracts status fields by combining the address from the offset header with the mask and shift from this header.

The strongest local examples are `display/dmub/src/dmub_dcn351.c`, which initializes DMUB DCN35 register masks/shifts from the generated macros, and `display/dc/irq/dcn351/irq_service_dcn351.c`, which uses DCN 3.5.1 HPD interrupt masks to fill `irq_source_info` entries. VPG field names from this chunk also align with `display/dc/dcn31/dcn31_vpg.h`, where `DCN31_VPG_MASK_SH_LIST` maps `VPG0_VPG_*` masks/shifts into `struct dcn31_vpg_shift` and `struct dcn31_vpg_mask`.

## State and persistence behavior

The macros are stateless constants. The state they describe lives in DCN hardware registers and is reset or reprogrammed by display IP initialization, GPU reset, suspend/resume, hotplug handling, link training, modeset, DMUB coordination, or VPG packet programming.

State categories in this chunk are hardware-visible:

- DDC/I2C read-request bits are interrupt/status/ack/mask state for connector-side DDC transactions.
- DIO scratch registers are 32-bit mutable storage and must be treated as shared hardware state.
- DIO memory power and ALPM wake fields reflect power-gated/light-sleep state and wake events across DisplayPort link blocks.
- HPD fields persist as interrupt routing, ack, filter timing, polarity, and live/delayed sense state for connectors.
- AUX control/status fields represent an active transaction engine. `AUX_SW_GO`, `AUX_SW_DONE`, `AUX_LS_UPDATED_ACK`, arbitration request/done bits, reset bits, and PHY wake bits are ordering-sensitive hardware handshakes.
- VPG generic packet fields persist packet data, update triggers, pending bits, and conflict state; stale VPG data or pending update bits can affect InfoFrame/metadata transmission until cleared or overwritten.

## Dependencies and integration points

- The companion `dcn_3_5_1_offset.h` supplies address macros for the register names in this chunk, for example `regDC_I2C_READ_REQUEST_INTERRUPT`, `regDIO_SCRATCH0`, `regDIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS`, `regDIO_MEM_PWR_STATUS`, `regDIO_LINKA_CNTL`, `regHPD0_DC_HPD_INT_STATUS`, `regDP_AUX0_AUX_CONTROL`, `regDP_AUX4_AUX_PHY_WAKE_CNTL`, `regVPG0_VPG_GENERIC_PACKET_ACCESS_CTRL`, and `regVPG0_VPG_MPEG_INFO0`, all on base index 2 in the checked offset header.
- `dmub_dcn351.c` depends on this header to populate DMUB-facing DCN35 register metadata for DCN 3.5.1 hardware.
- `irq_service_dcn351.c` depends on the HPD masks to build per-source interrupt enable/ack/status records used by the DC interrupt service layer.
- VPG consumers depend on the `VPG0_VPG_*` layout through the shared DCN31 VPG abstractions, because later DCN versions reuse those field names and structures.
- DP AUX fields integrate with the display link/DDC/AUX stack, DisplayPort link training, LTTPR access, HDCP/CPIRQ handling through AUX, and GTC synchronization support.
- DIO link selection fields integrate with DCN link encoder assignment, especially HPO HDMI/DP encoder routing.

## Risks and edge cases

- Chunk-boundary incompleteness: this range omits one mask at the beginning of `DC_I2C_READ_REQUEST_INTERRUPT` and most of `VPG0_VPG_MPEG_INFO0` at the end. Any per-register final report must reconcile adjacent chunks before treating those groups as complete.
- Generated header drift: a wrong mask/shift silently corrupts hardware programming. Repeated blocks such as `DP_AUX0` through `DP_AUX4` and `HPD0` through `HPD4` are vulnerable to instance-copy mistakes.
- Reserved-bit corruption: many registers contain sparse fields. Callers must use read/modify/write helpers or preserve unknown bits, especially for DIO power control, AUX control, HPD control, and perfmon state.
- Handshake ordering: AUX reset/done, AUX software-go/done, arbitration request/done, interrupt ack, and PHY wake go/pending/ack fields should be written in the expected hardware sequence. Setting or clearing a bit with the right mask at the wrong time can wedge transactions or lose interrupts.
- Status-versus-ack ambiguity: HPD, AUX, GTC sync, and perfmon groups contain status, mask, and ack/clear fields in nearby bits. Using an ack mask as a status test, or vice versa, can cause missed events.
- Width truncation: packed fields such as `AUX_HPD_SEL`, `AUX_SW_WR_BYTES`, timer intervals, reply byte counts, GTC thresholds, perfmon counter selects, and VPG data indexes have limited widths. Callers must validate values before shifting.
- Power impact: DIO and VPG memory light-sleep disable/force fields can affect idle power, wake latency, and resume behavior.
- Partial instance coverage: this chunk contains HPD0-HPD4 and DP_AUX0-DP_AUX4 but not necessarily every possible connector instance for the ASIC; consumer tables must match the actual hardware instance count.

## Test signals

- Build-test DCN 3.5.1 AMDGPU display with `dmub_dcn351.c` and `irq_service_dcn351.c` enabled. Missing or misspelled generated macros should fail compilation.
- Add or run generated-header consistency checks that compare `DP_AUX0`-`DP_AUX4` field layouts and `HPD0`-`HPD4` field layouts for identical shifts/masks where the hardware instances are expected to match.
- Validate offset/mask pairing by checking that every register family used by consumers has both `reg...` address macros in `dcn_3_5_1_offset.h` and matching `__SHIFT`/`_MASK` symbols in this header.
- Runtime HPD tests: plug/unplug and HPD RX interrupt scenarios should set status bits, honor masks, and clear through the documented ack bits without losing later events.
- Runtime AUX tests: EDID reads, DPCD reads/writes, link training, LTTPR access, CPIRQ handling, AUX timeout/error injection, and suspend/resume should exercise `AUX_SW_STATUS`, `AUX_LS_STATUS`, arbitration, interrupt, reset, DPHY, GTC sync, and PHY wake fields.
- Power-management tests: monitor DIO and VPG memory power state fields across idle, display on/off, ALPM wake, suspend/resume, and link reconfiguration.
- VPG packet tests: write generic packet and ISRC data through the VPG path, request frame/immediate updates, observe pending bits clear, and verify conflict status/clear behavior.
- Perfmon tests: configure `DC_PERFMON16` counters, latch current values, verify overflow/clear behavior, and confirm interrupt/mask fields do not interfere with normal display interrupts.

### subset-b-002099: lines 26549-28768

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 26549-28768

## Scope

This chunk is a generated AMD DCN 3.5.1 register shift/mask header slice. It contains C preprocessor constants only: every meaningful symbol maps a display hardware register field to a bit shift or bit mask. There are no functions, runtime branches, structs, or direct storage in this range. Its consumers are AMDGPU display code paths that build read-modify-write values for MMIO registers through the `REG_SET`, `REG_UPDATE`, `REG_GET`, and related DC register-access macros.

The slice starts in the tail of `VPG0` MPEG info packet fields, covers the full `AFMT0` audio formatter group and `DME0` metadata engine group, covers a large `DIG0` HDMI/TMDS/back-end and `DP0` DisplayPort transmitter block, then repeats the beginning of the same per-pipe packet/audio/metadata/DIG pattern for instance 1 (`VPG1`, `AFMT1`, `DME1`, and early `DIG1`). The chunk ends mid-register at `DIG1_HDMI_GENERIC_PACKET_CONTROL10__HDMI_GENERIC1_EN_DB_PENDING__SHIFT`, so the next chunk must complete the remaining `DIG1_HDMI_GENERIC_PACKET_CONTROL10` masks and later DIG1/DP1 fields.

## Purpose

These macros provide the authoritative bit layout for DCN 3.5.1 display output hardware. The declarations are split by hardware instance:

- `VPG0` and `VPG1` define Video Packet Generator fields for generic packets, ISRC/MPEG info payload bytes, generic packet frame/immediate update triggers, conflict status, and VPG SRAM power controls.
- `AFMT0` and `AFMT1` define audio formatter packet controls for HDMI/DP audio: channel layout, channel enable mask, DP audio stream ID, HBR override, IEC 60958 channel status fields, HDMI audio infoframe bytes, audio CRC, audio test ramp generation, status, ACK bits, source selection, and AFMT memory power state.
- `DME0` and `DME1` define the display metadata engine controls: HUBP requestor selection, metadata engine enable, stream type, double-buffer pending/taken status and clear bits, DB disable, missed-transmission status/clear, and metadata memory power controls.
- `DIG0` defines the digital encoder/back-end fields for HDMI/TMDS packet scheduling, ACR, VBI, metadata packet injection, generic info packet send/continuous/line-reference/immediate controls, HDMI general-control mute/packing phase, double-buffer handshakes, audio clock gate controls, DIG back-end clock/reset/source selection, TMDS pattern generation, output CRC, and front-end/FIFO/test-pattern knobs.
- `DP0` defines the DisplayPort side of instance 0: link and stream controls, DPHY lane/symbol/training/scrambler/CRC, fast training, secondary data packet stream enables, audio M/N, secondary packet framing, MST/MSE slot allocation tables and status, MSA timing payloads, MSO controls, DSC mode, GSP8-GSP11 packet controls, generic secondary packet DB status, metadata transmission, VBID/MSA fields, video interrupt controls, and ALPM/AUX-less ALPM state/interrupt controls.
- `DIG1` begins the instance-1 digital encoder fields: FE/FIFO/output CRC/test pattern, HDMI control/status/VBI/metadata/generic packet controls, immediate sends, and HDMI general control/line-number fields.

## Important APIs, Types, and Symbols

There are no C types or callable APIs in this range. The exported surface is the naming contract:

- `*_SHIFT` constants give the least-significant bit index used when placing a field value in a register word.
- `*_MASK` constants give the contiguous bit mask used to isolate or update a field.
- Macro names follow `INSTANCE_REGISTER__FIELD_{SHIFT,MASK}`, which lets AMD display register tables and generated accessor macros pair register addresses from companion headers with bitfield definitions from this file.

Key register families in this slice:

- `VPG0_VPG_MPEG_INFO0/1` and `VPG1_VPG_MPEG_INFO0/1` contain MPEG infoframe checksum/message bytes, MPEG frame flags, and update bits.
- `VPG1_VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG1_VPG_GENERIC_PACKET_DATA`, `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`, and `VPG1_VPG_GSP_IMMEDIATE_UPDATE_CTRL` cover indexed generic packet payload data and 15 generic packet update slots with pending feedback.
- `AFMT[0-1]_AFMT_AUDIO_PACKET_CONTROL*`, `AFMT_AUDIO_INFO*`, `AFMT_60958_*`, `AFMT_STATUS`, `AFMT_AUDIO_CRC_*`, `AFMT_RAMP_CONTROL*`, and `AFMT_MEM_PWR` are the audio formatter programming interface for audio infoframes, IEC 60958 status, sample transmission, FIFO/enable-change ACKs, test ramps, CRC readback, and memory-light-sleep policy.
- `DME[0-1]_DME_CONTROL` and `DME_MEMORY_CONTROL` provide metadata engine enable/DB/missed-transmission control and memory-power state fields.
- `DIG0_HDMI_*` covers HDMI audio/video transport, including `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_VBI_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL*`, `HDMI_METADATA_PACKET_CONTROL`, `HDMI_ACR_PACKET_CONTROL`, `HDMI_ACR_*`, `HDMI_DB_CONTROL`, `HDMI_GENERIC_PACKET_CONTROL0/1/2/3/4/5/6/7/8/9/10`, and `HDMI_GC`.
- `DIG0_DIG_BE_*`, `DIG0_DIG_FE_CNTL`, `DIG0_DIG_FIFO_CTRL*`, `DIG0_DIG_TEST_PATTERN`, `DIG0_DIG_OUTPUT_CRC_*`, and `DIG0_TMDS_*` cover back-end clock/reset/source selection, FIFO servicing, BIST/test patterns, CRC capture, TMDS sync/control/DC balance, and control-character generation.
- `DP0_DP_*` spans the DP encoder and secondary packet engine, especially `DP_LINK_*`, `DP_VID_*`, `DP_DPHY_*`, `DP_SEC_*`, `DP_MSE_*`, `DP_MSO_*`, `DP_MSA_*`, `DP_GSP8..11_CNTL`, `DP_SEC_METADATA_TRANSMISSION`, `DP_STEER_FIFO`, `DP_ALPM_CNTL`, and `DP_AUXLESS_ALPM_CNTL*`.

## Control Flow and Programming Model

Because the file is declarative, runtime control flow lives in the display driver callers. The implied programming model is:

1. Select a display output instance and register family from the active link/stream encoder.
2. Use companion address/register headers to identify the MMIO register.
3. Use the `*_SHIFT` and `*_MASK` macros here to compose, update, or decode fields.
4. For stateful hardware protocols, write a request bit and poll/read a pending, taken, done, status, or occurred bit from the matching field.

The most important hardware handshakes exposed by this range are:

- VPG generic packet update flow: driver writes packet payload through indexed access/data registers, triggers frame or immediate update bits, and observes `*_PENDING` or conflict status fields.
- AFMT audio flow: driver sets layout/channel/HBR/stream-id/infoframe/channel-status fields, enables sample sending, then monitors `AFMT_STATUS` for audio enable, HBR status, FIFO overflow, and audio-enable-change events. Overflow and enable-change are acknowledged through `AFMT_AUDIO_PACKET_CONTROL`.
- DME metadata flow: driver enables the metadata engine, waits on `METADATA_DB_PENDING` and `METADATA_DB_TAKEN`, clears taken/missed conditions, and can disable DB behavior when required.
- HDMI generic packet flow: `HDMI_GENERIC_PACKET_CONTROL0` and `CONTROL6` enable slots 0-14, select continuous send and line-reference behavior, `CONTROL1/2/3/4/7/8/9/10` set line numbers and DB pending status, and `CONTROL5` requests immediate send while exposing immediate pending bits.
- HDMI DB flow: `HDMI_DB_CONTROL` carries pending/taken/taken-clear/lock/disable plus vupdate DB pending/taken status; callers must use these bits to avoid racing infoframe or generic packet updates.
- DP secondary packet flow: `DP_SEC_CNTL*` enables stream/audio/timecode/info/GSP/MPEG/ISRC packets, schedules GSP line numbers, requests GSP sends, exposes send-pending and deadline-missed flags, and controls DB disable/pending status for GSP slots 0-11.
- DP link training and link-layer flow: DPHY control registers expose lane enable, training pattern selection, scrambler, PRBS, CRC, HBR2 pattern, and fast-training trigger/status bits. These fields participate in link training and diagnostics but this header does not enforce the ordering.
- DP MST/MSO flow: MSE rate, slot allocation tables, SAT update, status readback, link timing, and MSO stream enable fields describe how the encoder allocates payload slots across streams.
- ALPM flow: `DP_ALPM_CNTL` and `DP_AUXLESS_ALPM_CNTL*` define enable/status/state/frame/line/interrupt fields used for low-power panel behavior and wakeup signaling.

## State and Persistence Behavior

The macros have no software state and no persistence. They describe hardware state located in DCN display registers.

Important stateful hardware fields in the chunk include:

- Sticky or event-like bits: `*_OCCURRED`, `*_MISSED`, `*_DONE`, `*_SEND_DEADLINE_MISSED`, `*_WAKEUP_INTERRUPT_OCCURRED`, and FIFO overflow/change flags.
- Clear or ACK bits: `*_CLR`, `*_ACK`, `*_CLEAR`, `AFMT_AUDIO_FIFO_OVERFLOW_ACK`, `AFMT_AZ_AUDIO_ENABLE_CHG_ACK`, `HDMI_DB_TAKEN_CLR`, `VUPDATE_DB_TAKEN_CLR`, `METADATA_DB_TAKEN_CLR`, and `METADATA_TRANSMISSION_MISSED_CLR`.
- Pending/taken DB bits: VPG, DME, HDMI, and DP GSP engines all expose pending/taken/pending-status fields. These are volatile handshakes with hardware double-buffer logic.
- Readback/status registers: audio CRC result, HDMI ACR status, DIG output CRC result, DP DPHY/MSE readbacks, DP MSA timing payload fields, ALPM current state and enable status.
- Power policy fields: AFMT/VPG/DME memory power controls and clock enable/on fields can affect register accessibility and side effects if a caller programs packet engines while memory or clocks are gated.

Any suspend/resume, hotplug, modeset, or link-reset path that reinitializes DCN output hardware must reprogram these registers through higher-level driver code. The header itself does not retain values across resets, power-gating, or display pipe reallocation.

## Dependencies and Integration Points

This header is part of the AMDGPU DRM display register-description layer under `drivers/gpu/drm/amd/include/asic_reg/dcn/`. It depends on generated register address headers for actual offsets and on display-core accessor macros for correct MMIO reads/writes. It is typically integrated indirectly through DCN resource, link encoder, stream encoder, audio, HDMI, DP, packet, and metadata programming code.

Integration points to preserve:

- Field names must match generated `sh_mask` references expected by `dcn*` stream encoder, link encoder, audio, HDMI, DP, and packet-management code.
- Instance suffixes must align with register-address instance tables. `AFMT0` pairs with `DIG0`/`DP0`/`VPG0`/`DME0`, and the repeated `1` groups must pair with the second output instance.
- Register layout must remain synchronized with firmware/hardware specs. These constants are usually regenerated from ASIC register databases; hand edits create high risk unless validated against the source spec.
- HDMI and DP packet fields overlap conceptually with DRM infoframe, audio, HDR metadata, adaptive sync, DSC PPS, PSR/ALPM, MST, and modeset code paths; an incorrect mask can surface far from the immediate write site as a blank screen, missing audio, stale metadata, or link-training instability.

## Risks and Edge Cases

- The chunk begins and ends in the middle of logical generated sections. `VPG0_MPEG_INFO0` starts before this range, and `DIG1_HDMI_GENERIC_PACKET_CONTROL10` continues after it. Merge tooling must concatenate adjacent chunk research for full per-file coverage.
- Off-by-one bit shifts or masks in this file are severe: they can corrupt neighboring fields in the same 32-bit register. Multi-bit fields such as channel masks, M/N values, line numbers, slot counts, ACR CTS/N, MSA timing, and ALPM frame/line numbers are especially sensitive.
- Some fields have similar names but different semantics across packet engines. For example, VPG generic update pending, HDMI generic immediate pending, DME DB pending, and DP GSP DB pending are not interchangeable despite similar pending terminology.
- Write-one-to-clear or ACK fields must not be treated as ordinary persistent enable bits by callers. Clear/ACK fields in DME, HDMI DB, AFMT, DP secondary packets, and ALPM interrupt controls can drop real hardware events if written casually during broad register updates.
- Power and clock gating fields can interact with programming order. AFMT memory power, VPG memory power, DME memory power, AFMT audio clock, and DIG back-end clock/reset fields should be sequenced by existing driver helpers rather than updated independently.
- Instance-number mismatch is a realistic integration risk. Programming `AFMT1` with `DIG0` or `DP0` state can send correct-looking packet data to the wrong pipe or leave the active encoder stale.
- DP MST/MSO and secondary packet scheduling fields include line/frame timing and deadline-missed status; wrong timing can produce intermittent failures that only appear at certain refresh rates, link rates, or blanking intervals.
- DP ALPM/AUX-less ALPM fields include hardware-mode status and wakeup interrupt fields; incorrect masks can create low-power wake failures or persistent wake interrupts.

## Test Signals

Useful validation is mostly integration and hardware-facing:

- Build coverage: compile AMDGPU DC display code for the target ASIC family with `W=1` or equivalent to catch missing or renamed macros.
- Header consistency checks: generated-register validation should compare every `*_SHIFT` and `*_MASK` in this range against the DCN 3.5.1 register database, including field widths and instance repetition.
- HDMI functional tests: modeset to HDMI with audio enabled, verify audio infoframe/channel status/HBR paths, generic info packets, AVMUTE, ACR behavior, and absence of AFMT FIFO overflow.
- DP functional tests: link training at multiple link rates/lane counts, check fast-training completion, scrambler/training-pattern transitions, DPHY CRC diagnostics, and stable video after hotplug and modeset.
- Metadata/infoframe tests: HDR/AVI/vendor-specific/generic packet updates should change on frame or immediate update without stale pending bits, DB conflicts, or deadline-missed flags.
- MST/MSO tests: exercise multiple streams, slot allocation updates, MSE SAT status readback, and secondary data packet scheduling.
- Low-power tests: PSR/ALPM or panel low-power scenarios should enter and exit ALPM cleanly, with expected wakeup interrupt status/clear behavior.
- Suspend/resume and hotplug tests: verify that packet/audio/metadata/DIG/DP state is restored for both instance 0 and instance 1 without cross-instance leakage.

### subset-b-002100: lines 28769-30986

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 28769-30986

## Purpose

This chunk is a generated DCN 3.5.1 shift/mask header section for AMD display engine registers. It defines C preprocessor constants that describe bit positions and masks for the second display I/O slice and adjacent packet/audio/metadata blocks: the tail of `DIG1`, the full `DP1` secondary-data and link block, `VPG2`, `AFMT2`, `DME2`, `DIG2`, and the beginning of `DP2`. It is not executable code; its job is to give AMDGPU display code stable field descriptors for read/modify/write operations against ASIC-specific MMIO registers.

The range contains 2,218 `#define` lines and no non-define statements. It starts mid-register at `DIG1_HDMI_GENERIC_PACKET_CONTROL10__HDMI_GENERIC2_EN_DB_PENDING__SHIFT` and ends mid-register at `DP2_DP_MSA_TIMING_PARAM3__DP_MSA_HSYNCWIDTH_MASK`, so some companion shift or mask fields for those boundary registers live in neighboring chunks.

## Important macros and field groups

- `DIG1_HDMI_*`, `DIG1_AFMT_CNTL`, `DIG1_DIG_BE_CNTL`, and `DIG1_TMDS_*` complete the first digital backend's HDMI, audio formatter, backend routing, and TMDS fields. Important controls include HDMI generic packet double-buffer pending bits, HDMI DB lock/disable/taken bits, ACR CTS/N fields for 32/44/48 kHz families, AFMT audio clock enable/status, backend source/HPD selection, and TMDS control-character, feedback, DC-balancer, sync, and generated control pattern fields.
- `DP1_DP_*` describes the first DisplayPort encoder slice. The fields cover link control, pixel format, MSA colorimetry/misc/timing, video stream enable/timing, DPHY training/scrambling/CRC/fast training, secondary-data packet controls, DP audio `N`/`M` values and readbacks, MSE rate and slot allocation tables, MSO stream enables, DSC mode, generic secondary packets `GSP0` through `GSP11`, DP double-buffer control, VBID overrides, metadata packet transmission, ALPM low-power signaling, and AUX-less ALPM timing/status fields.
- `VPG2_VPG_*` provides generic packet RAM access and status fields for the second video packet generator instance. It includes packet access control, packet payload data, frame-update and immediate-update controls for generic secondary packets, ISRC packet data, MPEG infoframe payload fields, status bits, and VPG memory power controls.
- `AFMT2_AFMT_*` describes the second audio formatter instance. It includes VBI/audio packet controls, audio infoframe fields, IEC 60958 channel status words, audio CRC controls/results, ramp generator controls, audio status, source selection, infoframe update controls, audio sample send/FIFO/channel-swap bits, and AFMT memory power fields.
- `DME2_DME_CONTROL` and `DME2_DME_MEMORY_CONTROL` define metadata engine 2 programming fields: HUBP requestor ID, engine enable, stream type, metadata double-buffer pending/taken/disable/clear bits, transmission-missed status/clear bits, and DME memory power controls.
- `DIG2_DIG_*`, `DIG2_HDMI_*`, `DIG2_AFMT_CNTL`, and `DIG2_TMDS_*` repeat the digital frontend/backend, HDMI, AFMT clock, and TMDS controls for the second digital encoder slice. This includes output CRC/test pattern/FIFO controls, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic packet control fields, HDMI GC and DB control, and TMDS generator fields.
- The `DP2_DP_*` portion begins the second DisplayPort encoder slice and runs through MSA timing parameter 3. It mirrors the early `DP1` groups for link/video/DPHY/secondary-data/audio/MSE status and MSA timing, but this chunk stops before `DP2_DP_MSA_TIMING_PARAM3__DP_MSA_HSYNCPOLARITY_MASK` and later DP2 groups.

There are no C functions, structs, or exported APIs here. The public surface is the generated macro naming contract: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, paired with `regREGISTER` and `regREGISTER_BASE_IDX` macros in `dcn_3_5_1_offset.h`.

## Control flow and usage model

The header has no runtime control flow. Runtime flow is in AMDGPU/DC code that includes this file with `dcn_3_5_1_offset.h`, selects the register address, applies the generated field mask/shift, and issues an MMIO read/modify/write through DC register helper macros.

A typical consumer path is:

1. DCN 3.5.1 resource, IRQ, or DMUB code includes the offset and shift/mask headers.
2. Resource-construction macros collect related field lists for blocks such as VPG and AFMT.
3. Encoder, packet, audio, metadata, or power-management code chooses a `reg...` address, for example `regDIG2_HDMI_CONTROL`, `regDP1_DP_SEC_CNTL2`, `regAFMT2_AFMT_AUDIO_PACKET_CONTROL`, `regDME2_DME_CONTROL`, or `regDP2_DP_MSA_TIMING_PARAM3`.
4. The caller encodes or extracts a field using the matching `_MASK` and `__SHIFT` value and writes the updated 32-bit register value.
5. Hardware double-buffer and status fields such as `*_DB_PENDING`, `*_DB_TAKEN`, `*_SEND_PENDING`, `*_SEND_ACTIVE`, and `*_DEADLINE_MISSED` report whether the hardware accepted or missed the programmed update.

The companion offset header maps the covered groups into base index 2 register addresses, including `regDIG1_HDMI_DB_CONTROL` at `0x21d5`, `regDP1_DP_SEC_CNTL2` at `0x228d`, `regAFMT2_AFMT_AUDIO_PACKET_CONTROL` at `0x22ca`, `regDME2_DME_CONTROL` at `0x22d9`, `regDIG2_HDMI_CONTROL` at `0x22e6`, and `regDP2_DP_MSA_TIMING_PARAM3` at `0x23ac`.

## State and persistence behavior

The macros are compile-time constants and hold no software state. The state they describe lives in GPU display hardware registers and can persist until changed by modeset programming, audio/packet reconfiguration, link retraining, display power transitions, suspend/resume restore paths, or GPU/display IP reset.

Several fields describe hardware-latched or double-buffered state. HDMI and DP DB controls track pending/taken/lock/disable states for synchronized updates. DP secondary-data and HDMI generic packet fields hold packet send/continuous/immediate-send state and expose pending, active, deadline-missed, and line-number status. AFMT and DP audio `N`/`M` fields affect audio clock recovery and packet generation, while MSE/SAT fields hold Multi-Stream Transport slot allocation state. Memory-power fields in VPG, AFMT, and DME affect block-local low-power state and must match the block's active use.

## Dependencies and integration points

- Depends on `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h` for register addresses and base-index information.
- Included directly by `display/dc/resource/dcn351/dcn351_resource.c`, `display/dc/irq/dcn351/irq_service_dcn351.c`, and `display/dmub/src/dmub_dcn351.c`.
- Integrates with DC register helper/list macros that consume generated `*_MASK` and `*__SHIFT` symbols for block-specific register tables.
- Binds display encoder programming to HDMI, DisplayPort, TMDS, VPG, AFMT, DME, MST/MSO, DSC, ALPM, and metadata packet behavior in the AMDGPU DRM display stack.
- Shares repeated field layouts across instances: `DIG1`/`DIG2`, `DP1`/`DP2`, and second-instance `VPG2`/`AFMT2`/`DME2` all depend on consistent generated instance numbering.

## Risks and edge cases

- Boundary incompleteness: this chunk begins and ends in the middle of register definitions, so users must include the whole generated header rather than treating this range as an independent register catalog.
- Mask/offset mismatch: a field macro is only useful when paired with the correct `reg...` address and base index. Mixing `DP1` masks with `DP2` offsets, or `DIG1` masks with `DIG2` offsets, would silently program the wrong hardware instance.
- Reserved-bit corruption: callers should update fields with mask-preserving read/modify/write helpers. Full-register writes can disturb reserved or status/clear bits adjacent to the named fields.
- Write-one-to-clear and status fields: bits such as `*_TAKEN_CLR`, `*_ACK`, `*_MISSED_CLR`, FIFO overflow acknowledge, and collision acknowledge must not be handled like ordinary sticky configuration bits.
- Timing-sensitive packet updates: generic secondary packets, HDMI infoframes, DP metadata, and MSE/SAT updates have line references, immediate-send controls, pending bits, and deadline-missed status. Incorrect sequencing can show up only on particular sinks, MST topologies, refresh rates, or HDR/metadata modes.
- Audio regressions: AFMT and HDMI/DP ACR fields control sample transport, channel layout, IEC 60958 status, audio clock recovery, and FIFO behavior; wrong widths or stale double-buffer state can cause dropouts, bad channel maps, or sink enumeration issues.
- Power-management regressions: VPG/AFMT/DME memory-power and ALPM/AUX-less ALPM fields can reduce power, but bad enable/disable ordering can block packet/audio/metadata transmission or leave hardware in a higher-power state.

## Test signals

- Build coverage for DCN 3.5.1 with AMDGPU/DC enabled; missing or renamed generated macros should fail compilation in resource, IRQ, DMUB, encoder, packet, or audio code.
- Header consistency checks comparing repeated instance layouts: `DIG1` versus `DIG2`, early `DP1` versus `DP2`, and DCN 3.5.1 versus nearby generated DCN versions for expected field stability.
- Offset/mask reconciliation tests that verify covered `REGISTER__FIELD` macro groups have matching `regREGISTER` and `regREGISTER_BASE_IDX` entries in `dcn_3_5_1_offset.h`.
- Runtime modeset and link-training tests on DCN 3.5.1 hardware covering HDMI, DP SST, DP MST/MSO, DSC, HDR/metadata packets, and ALPM transitions.
- Audio tests for HDMI and DP endpoints, including 32/44.1/48 kHz families, channel layout changes, IEC 60958 updates, FIFO overflow handling, suspend/resume, and hotplug.
- Packet-status diagnostics: confirm `*_SEND_PENDING`, `*_SEND_ACTIVE`, `*_DEADLINE_MISSED`, DB pending/taken, metadata missed, and collision status bits behave as expected under frame-update, immediate-update, and line-referenced packet sends.

### subset-b-002101: lines 30987-33204

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 30987-33204

## Purpose

This chunk is a generated DCN 3.5.1 register field shift/mask table for the AMD display core. It does not implement executable logic; it provides compile-time constants that let AMDGPU display code encode and decode hardware register fields for DisplayPort, HDMI/DIG, video packet generator, audio formatter, and Display Micro-Engine blocks.

The range begins in the middle of the `DP2` DisplayPort block, covers most of the `VPG3`, `AFMT3`, `DME3`, `DIG3`, and `DP3` stream-encoder/register block, and ends at the start of the `VPG4`/`AFMT4` block. The matching address definitions live in `dcn_3_5_1_offset.h` as `reg*` macros with `_BASE_IDX` companions; consumers include this header and use helper macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `REG_SET*`, and `REG_UPDATE*` to perform packed register operations.

## Important register groups

- `DP2_*`: tail fields for the second DisplayPort stream. The chunk completes MSA timing masks, then defines MSO, DSC enable, secondary-data packet controls, generic secondary packet line scheduling, doorbell status, MSA/VBID miscellaneous fields, metadata transmission, ALPM and AUX-less ALPM controls, and GSP8-GSP11 payload bytes. These fields control DP main-stream attributes, multi-stream output packet replication, DSC mode, secondary packet dispatch, and panel self-refresh/low-power transitions.
- `VPG3_*`: video packet generator 3 fields for indexed generic packet access/data, frame-update and immediate-update triggers for generic packets 0-14, status/conflict bits, memory power controls, ISRC packet data, and MPEG infoframe payload bytes. This block owns the packet memory and update handshakes for the third stream encoder's video/generic packet path.
- `AFMT3_*`: audio formatter 3 fields for VBI/HDMI packet controls, audio packet layout/channel/stream IDs, HDMI audio infoframe bytes, IEC 60958 channel status, audio CRC, ramp controls, formatter status, ACP/infoframe interrupt/control, audio source selection, and AFMT memory power. These are the field constants used when HDMI/DP audio metadata and audio packet generation are programmed for stream 3.
- `DME3_*`: Display Micro-Engine 3 control and memory-control fields. The control register includes clock enable, gating, halt, ready/active state, cache invalidate, stall controls, and memory unit reset. The memory-control register exposes address, data, write enable, and auto-increment fields for DME memory access.
- `DIG3_*`: DIG front-end/back-end/HDMI/TMDS fields for stream encoder 3. The chunk covers FE/BE enables and source selection, FIFO and output CRC controls, test and random patterns, AFMT binding, HDMI control/status, HDMI generic packet scheduling/data selection, metadata and infoframe controls, deep-color/guard-band bits, ACR packet controls and counters, HDMI/VBI audio packet controls, TMDS control symbols and DC-balancer patterns, and TMDS sync/stereo controls.
- `DP3_*`: the full third DisplayPort block in this chunk. It covers video stream format/timing, M/N values, MSA colorimetry and timing, link control/framing, DPHY training/scrambling/PRBS/CRC/fast-training fields, MST/MSE link timing and slot allocation table fields, DP secondary audio and generic-packet controls, metadata transmission, MSO packet enables, DSC mode, GSP8-GSP11 data registers, doorbell/status fields, ALPM/AUX-less ALPM controls, and final MSA/VBID fields.
- `VPG4_*` and `AFMT4_*`: the beginning of the fourth stream packet/audio block. The chunk includes VPG4 generic packet access/data, frame-update and immediate-update controls, status, memory power, ISRC and MPEG fields, then starts AFMT4 VBI/audio packet control and audio info fields before the line range stops.

## API and type surface

The only API surface is preprocessor constants named as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. Each pair describes a bitfield inside a 32-bit hardware register. Examples include `DP3_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE__SHIFT`, `DP3_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE_MASK`, `DIG3_HDMI_GENERIC_PACKET_CONTROL0__HDMI_GENERIC0_SEND_MASK`, and `VPG3_VPG_GSP_FRAME_UPDATE_CTRL__VPG_GENERIC0_FRAME_UPDATE_PENDING_MASK`.

The field constants are coupled to offset macros such as `regDP3_DP_SEC_CNTL`, `regDIG3_HDMI_GENERIC_PACKET_CONTROL0`, `regVPG3_VPG_GSP_FRAME_UPDATE_CTRL`, `regAFMT3_AFMT_AUDIO_PACKET_CONTROL2`, and `regDME3_DME_CONTROL` in `dcn_3_5_1_offset.h`. The DC and DMUB helper layers turn those generated names into register descriptors:

- `reg_helper.h` uses `FN`, `REG_SET*`, and `REG_UPDATE*` style macros to apply masks and shifts while preserving unrelated fields.
- `dmub_reg.h` defines `FD_SHIFT(reg_name, field)` and `FD_MASK(reg_name, field)` as direct token concatenations to these constants.
- `dcn351_resource.c`, `irq_service_dcn351.c`, and `dmub_dcn351.c` include both `dcn_3_5_1_offset.h` and this mask header, so this generated data feeds DC resource construction, IRQ register programming, and DMUB register initialization.

There are no C types, functions, structs, or inline helpers in this range.

## Control flow and programming model

There is no runtime control flow in the header itself. The practical flow is:

1. DCN 3.5.1 display code includes the offset and shift/mask headers for the ASIC.
2. Resource initialization computes absolute register addresses from `reg*_BASE_IDX` and `reg*`.
3. Stream encoder, packet generator, audio formatter, DMUB, or IRQ code chooses a register and field by symbolic name.
4. Register helpers combine a field value with the `*_MASK` and `*__SHIFT` constants.
5. The driver writes the packed value to MMIO, or reads a register and extracts fields for status/diagnostics.

Several groups imply hardware handshakes. `DP*_DP_SEC_CNTL2` and `DP*_DP_SEC_CNTL7` expose send, pending, deadline-missed, active, and idle-send bits for generic secondary packets. `VPG*_VPG_GSP_FRAME_UPDATE_CTRL` and `VPG*_VPG_GSP_IMMEDIATE_UPDATE_CTRL` expose trigger and pending bits for packet-memory updates. `DP*_DP_DB_CNTL` exposes doorbell pending/taken/ack state. DPHY, MSE/SAT, ALPM, and AUX-less ALPM fields represent state-machine configuration and status for link training, MST payload slot allocation, and low-power entry/exit.

## State and persistence behavior

The macros hold no state. State lives in the GPU display hardware registers they describe. Values written through these fields persist until changed by display modeset/reprogramming, stream disable, link retraining, power-gating/reset, suspend/resume restore, or GPU reset.

The state is stream-instance-specific. `DP2` and `DP3` use similar field layouts but target different stream/link register instances. `VPG3`, `AFMT3`, `DME3`, and `DIG3` are tied to the third stream encoder path; `VPG4` and `AFMT4` begin the corresponding fourth path. Any code using these constants must pair the field with the correct register instance and base index.

Some fields directly affect hardware-visible output:

- DP timing/MSA, colorimetry, VBID, M/N, stream format, and pixel-format fields define the main video stream interpretation by sinks.
- Secondary packet and VPG generic packet fields determine whether infoframes, metadata, ISRC, MPEG, audio, DSC PPS, and other sideband packets are emitted and at which lines.
- MST/MSE SAT fields assign stream sources and slot counts for multi-stream transport.
- DPHY and link-framing fields affect training patterns, scrambling, PRBS, HBR2 patterns, CRC capture, and lane/symbol behavior.
- AFMT and HDMI/TMDS fields affect HDMI audio packet generation, IEC 60958 channel status, HDMI deep color and guard bands, ACR timing, and TMDS control-symbol generation.
- ALPM and AUX-less ALPM fields affect low-power panel/link behavior and must remain consistent with sink/panel capabilities.

## Dependencies and integration points

- `dcn_3_5_1_offset.h`: provides the `reg*` address macros paired with these field constants. In this ASIC header, the relevant offsets use `reg` prefixes rather than older `mm` prefixes.
- `drivers/gpu/drm/amd/display/dc/inc/reg_helper.h`: token-pastes register/field names into mask and shift constants and performs masked read/modify/write operations.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h`: exports the same field constants into DMUB register tables through `FD_MASK` and `FD_SHIFT`.
- `drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`: includes the generated DCN 3.5.1 headers while building resource register lists for DCN351.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`: loads generated masks/shifts into DMUB-facing register metadata.
- `drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`: includes the same generated register pack for ASIC-specific interrupt handling.
- Higher-level DC stream encoder, VPG, AFMT, link-training, MST, HDMI, and DMUB code depends on these constants indirectly through register-list structs and helper macros, rather than by hand-coding numeric bit positions.

## Risks and edge cases

- Generated register drift: the shift/mask header and offset header must be generated from the same register database. A wrong shift, mask, or address silently programs the wrong hardware bits.
- Instance mismatch: `DP2` vs `DP3`, `VPG3` vs `VPG4`, and `AFMT3` vs `AFMT4` are easy to confuse because many fields repeat with identical layouts. Pairing a field group with the wrong register instance can corrupt another stream encoder path.
- Packed-register writes: most registers contain multiple independent fields. Callers must preserve unrelated bits using masked updates, especially for status/control registers that combine trigger, pending, clear, and enable bits.
- Width truncation: many fields are narrow nibbles or bytes (`GSP*_PB*`, channel enables, packet-line selectors, SAT slot counts, color/depth selectors). Values must be range-checked before shifting.
- Handshake ordering: trigger bits such as `SEND`, `FRAME_UPDATE`, `IMMEDIATE_UPDATE`, doorbell fields, and metadata transmission bits have pending/status companions. Writing new payload data without waiting for pending bits to clear can lose packets or report conflicts.
- Read/clear hazards: status bits such as conflict, deadline-missed, CRC result/status, doorbell taken/ack, and ALPM state bits may be write-one-to-clear or hardware-updated in surrounding documentation. Generic full-register writes risk clearing useful diagnostic state.
- Link-training and MST fragility: DPHY, MSE/SAT, MSA, and M/N fields are sink-visible and timing-sensitive. Invalid combinations can cause blank displays, failed link training, bad MST payload allocation, or incorrect DSC/secondary packet behavior.
- Power behavior: ALPM, AUX-less ALPM, memory power, clock-enable, and clock-gating fields can change idle power and wake behavior. They also interact with suspend/resume and panel self-refresh flows.

## Test signals

- Build signal: compile AMDGPU display code with DCN351 enabled. Missing or renamed mask/shift symbols should fail at compile time through `FD_MASK`, `FD_SHIFT`, `REG_SET*`, or register-list expansion.
- Generated-header consistency: compare each `REGISTER__FIELD__SHIFT` with its `_MASK` width and position, and verify every used field has a corresponding `regREGISTER` entry in `dcn_3_5_1_offset.h`.
- Cross-instance consistency: verify repeated `DP2`/`DP3`, `VPG3`/`VPG4`, and `AFMT3`/`AFMT4` field layouts where the hardware generation expects identical encodings.
- DisplayPort runtime tests: modeset DP streams, retrain links, exercise DSC, MST, MSA timing/colorimetry, secondary packets, and ALPM/AUX-less ALPM entry/exit while checking for link-training failures, blanking, and sink metadata correctness.
- HDMI/audio runtime tests: validate HDMI output, audio enumeration, channel layouts, IEC 60958 status, ACR stability, audio CRC paths, and deep-color/TMDS behavior through stream encoder 3 and the AFMT3 path.
- Packet-generator tests: update VPG generic packet payloads, ISRC, MPEG, metadata, and DSC PPS packets while polling pending/conflict bits; confirm packets appear on expected frame/line boundaries.
- Power-management tests: suspend/resume, display off/on, PSR/ALPM transitions, and memory/light-sleep paths should preserve or restore programmed register state without stale packet data.
- Debug/diagnostic tests: read DPHY CRC, output CRC, doorbell status, deadline-missed, conflict, and ALPM status fields under stress to catch ordering bugs in register programming.

### subset-b-002102: lines 33205-35422

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 33205-35422

## Purpose

This chunk is a generated DCN 3.5.1 shift/mask header segment for AMD display controller hardware. It contains C preprocessor constants only: every symbol describes a bit position (`__SHIFT`) or bit mask (`_MASK`) for a field in a 32-bit MMIO register. The companion address data lives in `dcn_3_5_1_offset.h`; consumers combine the address macros with these field macros through AMDGPU/DC register helper macros such as `FD`, `FN`, `REG_SET`, and related wrapper patterns.

The line range is centered on display link instance 4 and the shared DCIO/GPIO register block. It begins at the end of `AFMT4_AFMT_AUDIO_PACKET_CONTROL2`, covers the complete `AFMT4`, `DME4`, `DIG4`, and `DP4` field groups for audio, HDMI/TMDS, DisplayPort, metadata, and link training, then moves into UNIPHY lane mapping, DCIO reset/pattern/sync controls, generic/DDC/GENLK/HPD GPIO controls, power-sequencer backlight controls, pad strength, and the start of AUX analog control. It ends partway through `DC_GPIO_AUX_CTRL_1`; `DC_GPIO_AUX_CTRL_2` begins in the following chunk.

## Important macros and register fields

There are no functions, structs, or enums in this chunk. The important API surface is the macro naming contract:

- `REG__FIELD__SHIFT` gives the right shift needed to align a field to bit 0.
- `REG__FIELD_MASK` gives the field mask in register position.
- `regREG` and `regREG_BASE_IDX` are provided by the companion offset header, not by this file.

Major register families in this chunk:

- `AFMT4_*`: audio formatter fields for link/audio instance 4. This includes HDMI/DP audio infoframe payload fields (`AFMT_AUDIO_INFO0`, `AFMT_AUDIO_INFO1`), IEC 60958 channel status (`AFMT_60958_0`, `_1`, `_2`), audio CRC control/result, test ramp controls, audio status, audio packet control, audio infoframe source/update bits, audio source selection, and `AFMT_MEM_PWR` memory power controls.
- `DME4_*`: metadata engine controls for instance 4, including HUBP requestor selection, metadata engine enable, stream type, double-buffer pending/taken/clear/disable bits, missed-transmission status/clear, and DME memory power fields.
- `DIG4_*`: digital encoder instance 4 fields. Covered groups include front-end source/bypass routing, output CRC, test and random pattern generation, HDMI packet/control/status/ACR fields, HDMI generic packet controls for packets 0-14, HDMI double-buffer handshakes, AFMT clock gating status, back-end source/HPD selection, and TMDS control character, sync, DC-balance, and generated-control fields.
- `DP4_*`: DisplayPort instance 4 fields. This is the largest family in the chunk and includes DP link and video-stream control, DPHY training/scrambler/PRBS/CRC/8b10b controls, fast training status, HBR2 patterns, MSA timing/colorimetry/misc fields, secondary data packet enables and scheduling, DP audio M/N registers and readbacks, MST MSE rate/SAT/status fields, MSO controls, DSC enable mode, ALPM/AUX-less ALPM fields, and DPIA spare bits.
- `UNIPHYA_*`, `UNIPHYB_*`, `UNIPHYC_*`, `UNIPHYD_*`, `UNIPHYE_*`: physical transmitter lane controls. A/B/C expose lane invert and channel crossbar source fields; D/E expose channel crossbar source fields in this slice.
- `DCIO_*`, `DC_PINSTRAPS`, and `INTERCEPT_STATE`: shared DCIO controls for write-command delay, pinstrap audio/SMS/clock-bypass status, spare register bits, intercept state visibility, pattern generator enable/value, BL PWM frame-start display selection, GENLK/swaplock GSL pad controls, and soft resets for UNIPHY A-G, DSYNC A-G, and PWRSEQ0/1.
- `DC_GPIO_*`: shared GPIO register field definitions. This chunk covers generic GPIO mask/A/EN/Y, DDC1-DDC5 and DDCVGA mask/A/EN/Y controls, GENLK mask/A/EN/Y, HPD mask/A/EN/Y, PWRSEQ0/1 enable routing for backlight signals, pad strength registers, `PHY_AUX_CNTL`, `DC_GPIO_TX12_EN`, and the start of AUX/I2C analog tuning in `DC_GPIO_AUX_CTRL_0` and `DC_GPIO_AUX_CTRL_1`.

## Control flow and usage model

This header has no runtime control flow. Its control behavior comes from how callers use the generated constants:

1. DCN 3.5.1-specific source files include `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`.
2. Register abstraction macros expand a register/field pair into address, base-index, mask, and shift constants.
3. Callers encode values by masking and shifting field values into a 32-bit register value, often through `REG_SET`, `REG_UPDATE`, or lower-level `dm_read_reg`/`dm_write_reg` helpers.
4. Hardware samples the values through MMIO state, double-buffer handshakes, vertical update timing, HPD/DDC/AUX sideband logic, or link encoder control paths.

The instance suffixes are significant. `AFMT4`, `DME4`, `DIG4`, and `DP4` describe one link/encoder pipeline instance, so code that selects instance 4 must pair these masks with the matching `regAFMT4_*`, `regDME4_*`, `regDIG4_*`, and `regDP4_*` offsets. Using instance 4 masks with another instance's offset is usually layout-compatible for repeated blocks, but it breaks the generated symbol contract and risks subtle maintenance errors.

Several groups model explicit hardware sequencing:

- AFMT audio packet and 60958 updates require callers to program packed status/info fields and trigger update/ack bits at the right time.
- HDMI generic packet controls have send, continuous-send, line-reference, immediate-send, pending, line-number, and enable-double-buffer-pending fields. Callers must respect pending/taken/status fields before rewriting packet state.
- DP secondary packet controls similarly expose enable bits, line scheduling, send/pending/deadline-missed status, active/idle-send selection, and double-buffer disable fields.
- DME metadata and HDMI DB controls expose double-buffer pending/taken/clear/disable state; writes are meaningful only in relation to hardware's current update window.
- DCIO soft-reset and GPIO enable/mask fields directly gate physical or sideband blocks and should be ordered with link shutdown/startup paths rather than arbitrary display-state updates.

## State and persistence behavior

The macros do not store state. They describe persistent hardware state held in DCN 3.5.1 display registers after driver writes them.

The most externally visible state in this chunk includes:

- Audio state: channel status, audio infoframe fields, channel enable/layout selection, sample-send control, FIFO overflow status/ack, CRC test state, and AFMT memory power state.
- Metadata/packet state: DME and HDMI/DP double-buffer pending/taken flags, generic packet line scheduling, immediate-send pending bits, DP secondary data packet enables, and missed/deadline status bits.
- Link state: DP training pattern, scrambler, PRBS, CRC, M/N, MSA timing, MST slot allocation table, MSO stream enables, DSC mode, ALPM controls, and TMDS control/DC-balance settings.
- Physical routing state: DIG source selection, HPD selection, UNIPHY lane inversion/crossbar mapping, DCIO resets, DSYNC/UNIPHY reset bits, and AUX/DDC/HPD GPIO ownership and pad tuning.
- Panel/backlight related state: PWRSEQ0/1 backlight and variable-backlight OTG-vsync routing, plus BL PWM frame-start display selection.

Register contents are normally reset by GPU/display IP reset, runtime suspend/resume, ASIC reinitialization, modeset link reprogramming, or DMUB/DC resource rebuild. Some status fields, such as FIFO overflow, CRC done, DB taken, transmission missed, pending, and deadline-missed bits, are transient hardware observations. Some clear/ack fields are write-one style controls inferred from their names (`*_ACK`, `*_CLR`, `*_TAKEN_CLR`) and should not be treated as persistent configuration bits.

## Dependencies and integration points

- The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides the matching `reg...` address macros. Spot checks show matching offsets such as `regAFMT4_AFMT_AUDIO_PACKET_CONTROL2`, `regAFMT4_AFMT_AUDIO_PACKET_CONTROL`, `regDME4_DME_CONTROL`, `regDIG4_HDMI_CONTROL`, `regDP4_DP_SEC_CNTL`, `regDP4_DP_SEC_CNTL1` through `regDP4_DP_SEC_CNTL7`, `regDCIO_SOFT_RESET`, and `regDC_GPIO_DDC1_MASK`.
- DCN 3.5.1 users include `display/dmub/src/dmub_dcn351.c`, `display/dc/irq/dcn351/irq_service_dcn351.c`, and `display/dc/resource/dcn351/dcn351_resource.c`, which include the offset and shift/mask headers for register initialization and field extraction.
- The register helper API in the AMD display tree depends on exact generated names. Macros such as `FD(reg_field)`, `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `FN(reg, field)`, and resource/IRQ/DMUB tables all expect `REG__FIELD_MASK` and `REG__FIELD__SHIFT` spelling.
- HDMI, DP, AFMT, and DME fields integrate with the DC link encoder and stream encoder layers that program audio, infoframes, DSC/PPS packets, HDR/vendor metadata, MST stream allocation, link training, and sink timing.
- GPIO/DDC/AUX/HPD fields integrate with connector detection, AUX channel transactions, DDC I2C fallback, hotplug handling, panel power sequencing, and board-level pin routing.
- UNIPHY and DCIO soft reset fields sit below higher-level link-encoder resource selection; incorrect use can affect all connectors sharing that physical block, not just one stream.

## Risks and edge cases

- Generated-header drift: because these are generated constants, a single mask or shift typo will compile cleanly but corrupt hardware programming at runtime. Repeated instance blocks (`DP4`, `DIG4`, `AFMT4`) are especially vulnerable to copy/generation errors.
- Register/mask mismatch: instance 4 masks must be used with instance 4 offsets. Most repeated block layouts are likely identical, but relying on that manually can hide address-selection bugs.
- Packed-field overflow: many fields are narrow, for example 1-bit enables, 2-bit source selectors, 3-bit requestor/source IDs, 4-bit channel/status selectors, 6-bit DP SEC version or MST slot counts, 16-bit line/timing fields, 20-bit HDMI ACR CTS/N fields, and 24-bit audio M/N or CRC values. Callers must clamp or validate values before shifting.
- Reserved-bit writes: direct full-register writes can disturb undocumented bits. Read-modify-write or generated field update helpers are safer when the register contains status, reserved, or write-one-clear bits.
- Double-buffer sequencing: DME, HDMI, and DP packet controls expose pending/taken/clear/disable fields. Writing packet contents or enables without observing pending/taken state can produce stale metadata, missed packets, or packet updates on the wrong frame.
- Status/clear semantics: fields named `*_ACK`, `*_CLR`, `*_TAKEN_CLR`, `*_MISSED_CLR`, or `*_OVERFLOW_ACK` likely have write-one-to-clear behavior. Treating them as normal persistent bits can accidentally clear diagnostics or retrigger handshakes.
- Link-training sensitivity: DP DPHY training, scrambler, 8b10b, HBR2 pattern, PRBS, and symbol fields are timing-sensitive and can break link bring-up only on specific cables, retimers, docks, or sink revisions.
- Physical signal risk: GPIO, AUX, DDC, HPD, pad strength, slew, bias, resistor, and comparator selection fields affect electrical behavior. Incorrect values can cause intermittent hotplug, AUX/DDC failures, or board-specific regressions that are hard to reproduce in emulation.
- Power-management interactions: AFMT/DME memory power controls, ALPM/AUX-less ALPM controls, DCIO soft reset, and pad wake fields interact with suspend/resume and idle power. Bad sequencing can cause resume failures or excess power draw.

## Test signals

- Build coverage: compile AMDGPU/DC paths that include DCN 3.5.1 headers. Missing or misspelled generated symbols should fail at compile time when consumed by resource, IRQ, DMUB, link, audio, or GPIO code.
- Header consistency checks: compare `AFMT4`, `DME4`, `DIG4`, and `DP4` shift/mask values against neighboring instances in the same generated header and against the DCN 3.5.0/3.5.x headers where layouts are expected to match.
- Offset reconciliation: verify every field group used by code has a matching `reg...` and `reg..._BASE_IDX` in `dcn_3_5_1_offset.h`, especially packet-control, DP secondary-data, GPIO, and DCIO reset registers.
- Runtime register smoke tests on DCN 3.5.1 hardware: exercise modeset, hotplug, suspend/resume, and link retraining while tracing reads/writes for `DIG4`, `DP4`, `AFMT4`, `DME4`, DCIO, and GPIO registers.
- HDMI tests: validate audio playback, channel layout, IEC 60958 channel status, AVI/audio/infoframe updates, generic packet scheduling, ACR N/CTS behavior, AVMUTE, and TMDS output with HDMI sinks.
- DisplayPort tests: validate link training across rates/lanes, MST slot allocation, DSC/PPS secondary packets, audio M/N programming, MSA timing, ALPM entry/exit, CRC paths, and secondary packet send/deadline status.
- Connector-sideband tests: run HPD plug/unplug, AUX transactions, DDC EDID reads, DDCVGA paths if supported, and panel power sequencing across cold boot and resume.
- Negative diagnostics: intentionally monitor FIFO overflow, CRC done, DB pending/taken, metadata transmission missed, DP SEC deadline missed, and collision/audio-mute status to confirm ack/clear fields behave as expected.

### subset-b-002103: lines 35423-37642

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 35423-37642

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.5.1 register shift/mask header. It contains preprocessor constants for hardware register bitfields, not executable driver logic. Callers use these `__SHIFT` and `_MASK` definitions with the matching `dcn_3_5_1_offset.h` address header and AMD display register helpers to pack, update, and extract fields in memory-mapped DCN display registers.

The requested range contains 2,217 `#define` lines: 1,107 shift macros and 1,110 mask macros. The imbalance is caused by chunk boundaries. The range starts inside the mask tail of `DC_GPIO_AUX_CTRL_1`, after that register's shift lines and earlier masks, and ends inside `DC_PERFMON19_PERFCOUNTER_CNTL`, before its remaining masks and following perfmon registers. There are no source comments in this span.

The substantive hardware covered here is the DCN 3.5.1 display I/O, panel power sequencing, Display Stream Compression, and adjacent performance-monitor programming surface:

- GPIO/AUX/DDC/HPD electrical controls for AUX and hot-plug related pins.
- DC GPIO receive-enable and pull-up-enable fields for generic, sync, genlock, swaplock, and HPD pins.
- AUX/I2C pad power-good status.
- DCIO UNIPHY reserved macro-control words for UNIPHY instances 1 through 4.
- Two panel power sequencer instances, including panel GPIO ownership, panel timing, backlight PWM, reference dividers, and register locking.
- DSC top control, DSCC input interface, DSCC core configuration, PPS programming, memory power, error statistics, buffer fullness telemetry, and debug fields for DSC instances 0 through 2.
- DC performance monitor instances 17 and 18, plus the beginning of instance 19.

## Important Constants And Register Areas

The GPIO/AUX section finishes `DC_GPIO_AUX_CTRL_1` masks for I2C resistor bias, AUX comparator select, DDC/VGA spare and slew/rx select, per-AUX comparator select, and DDC/VGA comparator selection. `DC_GPIO_AUX_CTRL_2` defines HPD fall slew selection, spike filter enables/selectors, 0.9 V and 1.1 V HPD capacitor/resistor selections, HPD bias current enable, slew, resistor bias, and comparator select fields. `DC_GPIO_AUX_CTRL_3` covers AUX termination disable, DP/DN swap, and hysteresis tuning for AUX1 through AUX6. `DC_GPIO_AUX_CTRL_4` and `DC_GPIO_AUX_CTRL_5` expose per-AUX analog control nibbles and bias/impedance calibration controls.

`DC_GPIO_RXEN` and `DC_GPIO_PULLUPEN` expose one-bit receive-enable and pull-up-enable controls for generic GPIO A through G, HSYNC/VSYNC A, genlock clock/vsync, swaplock A/B, and HPD1 through HPD6. `AUXI2C_PAD_ALL_PWR_OK` provides per-AUX and DDC/VGA pad power-good status, which is useful as a precondition/readback signal for AUX/I2C access.

The `DCIO_UNIPHY{1,2,3,4}_UNIPHY_MACRO_CNTL_RESERVED{0..57}` definitions map each reserved macro-control register as a full 32-bit field. These are intentionally opaque in the generated header: they preserve addressable fields from the hardware register database without assigning semantic subfields in this chunk.

`PWRSEQ0_*` and `PWRSEQ1_*` repeat the same panel power sequencing register layout for two instances. They include GPIO enables for variable backlight, DIGON, and BLON; receive and pull-up enables; GPIO masks, pull-down disables, receiver selections, and A/Y state bits; panel target-state, sync, digital-on, and backlight-on controls with override and polarity bits; state readbacks; power-up and power-down delay registers; panel and PWM reference dividers; PWM active count, fractional enable, frame-start update recognition, enable state; post-frame-start update delays; PWM period and bit count; group-one register lock/update-pending/update-at-frame-start/readback controls; and spare full-width fields.

The DSC/DSCC region is repeated for instances 0, 1, and 2. `DSC_TOP*_DSC_TOP_CONTROL` exposes DSC clock enable and DISPCLK/DSCCLK gate-disable bits. `DSCCIF*_DSCCIF_CONFIG0/1` configures the input interface with underflow recovery/status/interrupt enable, input pixel format, bits per component, double-buffer update-pending readback, and picture width/height. `DSCC*_DSCC_CONFIG0/1` covers slice layout, alternate ICH encoding, vertical slice count, and rate-control buffer model size; DCN 3.5.1 resource code supplies local definitions for an `ICH_RESET_AT_END_OF_LINE` field around this register family.

`DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` packs rate-buffer overflow and underflow status bits for buffers 0 through 3, rate-control buffer model overflow status bits, and matching interrupt-enable bits. `DSCC*_DSCC_PPS_CONFIG0` through `DSCC*_DSCC_PPS_CONFIG22` carry the Display Stream Compression PPS fields: DSC version, PPS identifier, line-buffer depth, bits per component/pixel, VBR/simple-422/RGB/native-422/native-420/block-prediction modes, chunk size, picture and slice dimensions, initial transmit/decode delay, scale values and intervals, first/second-line BPG offsets, NFL/NSL/slice BPG offsets, initial/final offsets, flatness and RC model parameters, RC edge and quantization limits, target offsets, RC buffer thresholds 0 through 13, and range min/max QP plus range BPG offsets 0 through 14.

`DSCC*_DSCC_MEM_POWER_CONTROL` fields describe default low-power state, memory power force/disable/status, and native-422 memory power force/disable/status. The telemetry registers hold squared error lower/upper counters for R/Y, G/Cb, and B/Cr channels; max absolute error fields; max fullness levels for rate buffers 0 through 3; and max fullness levels for rate-control buffer models 0 through 3. Instance 0 additionally includes `DSCC0_DSCC_TEST_DEBUG_BUS_ROTATE`.

`DC_PERFMON17_*` and `DC_PERFMON18_*` are complete performance monitor instances in this chunk. They define counter event selection, counted-value selection, increment mode, hardware control selector, run-enable mode, count-off start disable, restart enable, interrupt enable, off mask, active status, counter select, count-off selection, counter state for counters 0 through 7, perfmon state/report count/count-off controls, perfmon count-off interrupt enable/status/ack, clock enable, run-enable start/stop selectors, per-counter interrupt status/ack, counter value high/low readback, and read selector fields. `DC_PERFMON19_PERFCOUNTER_CNTL` starts at the end of the chunk and is incomplete here.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this source range. The public interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the bit position for packing or extracting a register field.
- `REGISTER__FIELD_MASK` gives the already-positioned field mask.
- Register names encode hardware block and instance, such as `PWRSEQ1_BL_PWM_CNTL`, `DSCC2_DSCC_PPS_CONFIG16`, or `DC_PERFMON18_PERFCOUNTER_STATE`.

The macros are consumed through register-list and field-list structures in the AMD display stack. For DCN 3.5.1, `display/dc/resource/dcn351/dcn351_resource.c` includes `dcn_3_5_1_offset.h` and this shift/mask header, then builds resource, AUX, UNIPHY, DSC, and other register tables. `display/dc/irq/dcn351/irq_service_dcn351.c` and `display/dmub/src/dmub_dcn351.c` also include this header for ASIC-specific register access.

The DSC fields integrate with common DCN DSC code through `display/dc/dsc/dcn35/dcn35_dsc.c`, inherited DSC register list macros, and generic DSC calculations in `display/dc/dsc/dc_dsc.c`. Panel power and backlight fields correspond to panel-control code patterns in the DC display stack, especially the `dce_panel_cntl` and DCN panel-control abstractions. AUX and UNIPHY fields feed link encoder, DIO, AUX/I2C, and DMUB-side register setup rather than direct ad hoc bit twiddling.

Semantic enum values are not defined here. Valid values for pixel formats, bits-per-component encodings, DSC PPS fields, HPD/AUX analog tuning, power states, perfmon event selectors, and run-control selectors must come from hardware documentation, generated enum data, or higher-level DCN code.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs when the display driver programs the hardware registers described by these masks during probe/resource construction, link bring-up, AUX transactions, panel power transitions, backlight updates, DSC enable/disable/programming, interrupt handling, performance diagnostics, or debug readback.

The implied GPIO/AUX flow is: ensure relevant AUX/I2C pads are powered, configure AUX and HPD analog characteristics, enable receivers and pull-ups as required, and let the link/AUX layer drive transactions or HPD detection through the established register helper layer. Incorrect GPIO receive or pull-up programming can affect hotplug detection, DDC/AUX communication, genlock/swaplock signals, or panel control pins.

Panel sequencing flow is stateful and timing-sensitive. The driver programs reference dividers and delay registers, configures GPIO ownership and polarity, optionally locks or double-buffers PWM group registers, and drives `PANEL_PWRSEQ_TARGET_STATE` or override fields to transition the panel, DIGON, BLON, and sync outputs. Status and update-pending bits provide synchronization points; power and backlight code must respect them rather than treating the fields as ordinary memory.

The DSC programming flow uses the top clock-control fields, interface config, DSCC core config, PPS registers, interrupt controls, memory-power controls, and status fields together. Higher-level DSC code computes DSC PPS values from link timing and compression parameters, then writes `DSCC_PPS_CONFIG0..22`, configures slice layout and input format, enables clocks and memory, and monitors update-pending or error/overflow status. DSCCLK setup in the wider DCN sequencing is also relevant because DSCC register access can depend on clock availability.

Performance monitor flow is diagnostic: callers select events and counted values, choose increment and run-enable behavior, configure count-off and interrupt behavior, start or stop counters, then read high/low counter values through read selectors. Status and ACK fields in `PERFMON_CVALUE_INT_MISC` and `PERFMON_CNTL` are side-effect-prone and should be handled by the established perf/debug path.

Repeated instance layout is important control-flow context. The DSC/DSCC blocks are structurally parallel across instances 0, 1, and 2; `PWRSEQ0` and `PWRSEQ1` are structurally parallel; `DC_PERFMON17` and `DC_PERFMON18` are structurally parallel. The driver relies on instance-indexed register tables so common code can operate on the selected hardware instance by changing register addresses and using the same field names.

## State And Persistence

The file itself stores no mutable state. It defines how software reaches persistent hardware state in DCN registers and internal DSC/panel/link state machines.

Persistent hardware state represented here includes AUX/HPD electrical tuning, GPIO receiver and pull-up configuration, AUX/I2C pad power-good readback, UNIPHY reserved macro-control words, panel timing/divider/PWM/polarity/override state, DSC clocks and gate controls, DSCC input and PPS configuration, DSCC memory power state, DSCC error and buffer fullness telemetry, and perfmon configuration/counter state.

Several fields expose double-buffered or current-state behavior. `DOUBLE_BUFFER_REG_UPDATE_PENDING`, `BL_PWM_GRP1_REG_UPDATE_PENDING`, readback DB register enable fields, panel state readbacks, perfmon active/state fields, and DSCC error/fullness counters are synchronization or observation points. They should not be interpreted as independent software-owned state.

Memory power fields are persistent and sequencing-sensitive. `DSCC*_DSCC_MEM_POWER_CONTROL` can force or disable memories used by the DSC block and report their state. Powering these memories down at the wrong time can affect DSC programming retention, active compressed scanout, or safe register access.

## Dependencies And Integration Points

This generated header depends on the matching DCN 3.5.1 address header. The masks are meaningful only with the same register database and ASIC generation; similar DCN 3.5.0, DCN 3.6.0, or DCN 4.x headers must not be substituted without validation.

Primary integration points are:

- `display/dc/resource/dcn351/dcn351_resource.c`, which includes this generated header and builds DCN 3.5.1 resource, AUX, UNIPHY, DSC, and related register/mask tables.
- `display/dc/irq/dcn351/irq_service_dcn351.c`, which includes the same generated offset and shift/mask headers for DCN 3.5.1 interrupt source setup.
- `display/dmub/src/dmub_dcn351.c`, which initializes DMUB-facing DCN 3.5.1 register offsets and fields.
- `display/dc/dsc/dcn35/dcn35_dsc.c` and common DSC code, which consume DSC/DSCC field tables to enable clocks, configure memory power, program DSC PPS values, and read status.
- Panel-control code under `display/dc/dce` and `display/dc/dcn301`, which shows the higher-level patterns for PWRSEQ, PWM, target-state, and state-readback fields that these DCN 3.5.1 masks support.
- Link, DIO, AUX/I2C, and HPD handling paths, which rely on GPIO/AUX/UNIPHY field tables rather than direct register literals.

The register helper layer is the main API boundary. Direct open-coded bit manipulation against these constants would bypass instance tables, base-index selection, locking, double-buffering, and existing sequencing assumptions.

## Risks And Edge Cases

Generated-header drift is the central risk. A wrong mask or shift generally compiles successfully but writes the wrong hardware bits, which can cause failures in hotplug detection, AUX/DDC access, panel power sequencing, backlight PWM, DSC compression output, DSC interrupt status handling, or performance counter readback.

Chunk boundaries are incomplete. Whole-register validation for the first register requires the previous chunk's `DC_GPIO_AUX_CTRL_1` shift and early mask definitions. Whole-register validation for the last register requires the next chunk's remaining `DC_PERFMON19_PERFCOUNTER_CNTL` masks and related perfmon fields.

Reserved UNIPHY fields are opaque by design. Their full-width masks make it easy for generated tables to expose them, but they should not be written casually without hardware guidance. Treating reserved macro-control words as normal feature fields can destabilize PHY behavior.

Panel and backlight fields are sequencing-sensitive. Delay fields, target-state controls, override bits, polarity bits, register locks, frame-start update controls, and update-pending readbacks must be ordered with the panel power state machine. Mistakes can leave a panel dark, power a panel out of spec, or produce visible backlight jumps.

DSC PPS programming is highly coupled. PPS field mismatches between software calculation, DSCC registers, and sink expectations can produce link training success with corrupt compressed video. The `L` suffix on high-bit masks such as `0x80000000L`, `0xF0000000L`, and `0xFFFFFFFFL` also means consumers should keep using the driver's unsigned register helper types rather than signed arithmetic on raw constants.

Repeated instance consistency is a strong maintenance signal. `DSCC0`, `DSCC1`, and `DSCC2` should remain structurally parallel, as should `PWRSEQ0`/`PWRSEQ1` and `DC_PERFMON17`/`DC_PERFMON18`. A generator or merge error may only affect one DSC engine, one panel sequencer, or one perfmon instance.

## Test And Validation Signals

Compile coverage should include DCN 3.5.1 resource construction, IRQ service, DMUB register initialization, DSC code, AUX/DIO code, and panel-control users that include or indirectly consume `dcn_3_5_1_sh_mask.h`. Missing or renamed macros usually fail at compile time; incorrect numeric values require generated-data comparison or hardware validation.

Useful static checks include comparing this range against the authoritative DCN 3.5.1 register database, verifying complete registers have non-overlapping masks whose low set bit matches the shift value, diffing repeated `DSCC0/1/2`, `PWRSEQ0/1`, and `DC_PERFMON17/18` layouts, and checking neighboring chunks for the incomplete `DC_GPIO_AUX_CTRL_1` and `DC_PERFMON19_PERFCOUNTER_CNTL` boundaries.

Runtime signals include reliable HPD detection, stable AUX/DDC transactions, correct internal/eDP panel power-up and power-down timing, smooth and correctly synchronized backlight PWM updates, successful DSC modes on all exposed DSC engines, correct DSC PPS readback and compressed display output, absence of DSCC rate-buffer overflow/underflow interrupts during valid modes, stable suspend/resume and runtime power transitions, and working perfmon counter start/stop/readback/interrupt behavior.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002103_research.md`. Whole-file research for `dcn_3_5_1_sh_mask.h` must merge adjacent chunks to complete the leading `DC_GPIO_AUX_CTRL_1` register and trailing `DC_PERFMON19_PERFCOUNTER_CNTL` register context.

### subset-b-002104: lines 37643-39861

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 37643-39861

## Purpose

This chunk is a generated AMD DCN 3.5.1 shift/mask header segment. It has no executable code; it supplies compile-time bit positions and masks for display-core hardware registers consumed by AMDGPU/DC register access macros. The covered lines span several display output blocks: DC performance monitors 19-21, DSC compressor instance 3, DWB frame capture/writeback and output gamma, display host VM controls, HPO DisplayPort stream/link/PHY encoders, APG audio packet generator 0, DME metadata engine 5, and VPG generic/video packet generator 5.

The chunk begins in the middle of `DC_PERFMON19_PERFCOUNTER_CNTL`: only the tail masks for that register are present here, while its shifts and earlier masks are in the previous chunk. It ends in the middle of `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0`: the remaining CRC mask fields continue after this chunk.

## Important macros and register fields

- `DC_PERFMON19_*`, `DC_PERFMON20_*`, and `DC_PERFMON21_*` describe display-core performance monitor units. Each complete perfmon block has counter control selection, counted-value type and stop/source controls, eight packed counter-state fields, perfmon run/control interrupt fields, counter-value interrupt/status/ack fields, and low/high readback fields. These are the field surfaces used when selecting events, starting/stopping counters, reading counter values, and acknowledging perf counter interrupts.
- `DSC_TOP3_*`, `DSCCIF3_*`, and `DSCC3_*` define DSC compressor instance 3 control. The fields cover DSC clock enable/gating, input-interface underflow recovery/status, input pixel format and bits per component, picture dimensions, slice layout, rate-control buffer model size, double-buffer pending status, overflow/underflow interrupt enables, PPS payload registers 0-22, memory power control, squared/max error readbacks, and rate-buffer fullness watermarks.
- `DWB_*` and `FC_*` define the display writeback path. They cover DWB enable and clock gating, output FIFO and OGAM LUT memory power, frame-capture mode/rate/window/source geometry, update lock/pending state, CRC controls/results/masks, output formatting and denorm/min/max controls, MMHUBBUB backpressure counters, host read rate control, overflow status/counters, soft reset, gamut remap coefficients, and large output-gamma programming state for RAM A and RAM B.
- `DCHVM_*` describes display host VM integration: host VM init request, display/DCF clock gating controls, clock-request modes, fine-grain clock-gating repeat disable, GPUVM retention memory power controls, RIOMMU prefetch request/power status, RIOMMU active state, and prefetch-done status.
- `DP_STREAM_ENC0_*`, `DP_SYM32_ENC0_*`, `DP_LINK_ENC0_*`, and `DP_DPHY_SYM320_*` describe HPO DisplayPort stream/link/PHY encoder instance 0. The fields cover stream encoder clocks and input muxes, clock-ramp FIFO calibration/status, DP symbol encoder reset/enable, video FIFO, MSA double buffering and payload fields, pixel format, HBLANK control, SDP/GSP slots 0-14, audio SDP controls, metadata packet control, MSA/VBID/stream/panel replay controls, video CRC, symbol encoder memory power, link encoder clocking, DPHY enable/reset/precoder/mode/lane count, stream VC rates, slot-allocation-table controls/status, test pattern and PRBS/custom symbols, error status, symbol override, and the start of CRC config.
- `APG0_*` defines audio packet generator 0: reset/done, APG enable and DP audio stream ID, debug generator controls, ACP/audio-info source selection, audio CRC control/result, audio/HBR/FIFO status, output-active status, memory power state, and spare bits.
- `DME5_*` and `VPG5_*` define metadata and video packet generation for stream path 5. DME fields select the HUBP requestor and stream type, enable metadata, expose double-buffer pending/taken status, and clear missed/taken flags. VPG fields cover generic packet data access, generic packet frame/immediate update controls for many packet slots, generic status, memory power, ISRC data, and MPEG info-frame payload bytes.

## Control flow and usage model

There is no direct control flow in this header. Runtime code includes this ASIC-specific generated header together with the matching offset header, builds register field tables with macros such as `SE_SF`, `SF_DWB2`, or similar AMDGPU/DC helpers, and then uses `REG_UPDATE`, `REG_GET`, and related wrappers to encode or decode the bit fields.

The effective runtime pattern is:

1. DCN 3.5.1 resource initialization selects this shift/mask header and the corresponding register offsets for the active ASIC.
2. Block-specific code initializes structures for perfmon, DSC, DWB, HPO DP stream/link encoders, APG, DME, and VPG instances.
3. Driver code writes packed register values by shifting field values and applying the generated masks, normally preserving unrelated bits through read/modify/write helpers.
4. Hardware state is observed by reading status, pending, interrupt, CRC, overflow, FIFO, memory-power, or error fields through the same masks.

The key dynamic flows represented by this chunk are DSC programming before enabling compressed output; DWB capture setup, update locking, CRC collection, and overflow handling; HPO DP stream/link enablement with MSA/SDP/audio metadata programming; APG audio packet generation; VPG/DME metadata packet dispatch; and perfmon counter selection/readback around diagnostic or profiling paths.

## State and persistence behavior

The macros themselves hold no state. State lives in DCN hardware registers and follows display hardware lifetime rules: it may persist across normal modeset operations until explicitly reprogrammed, but can be reset by GPU reset, display IP reset, power-gating transitions, suspend/resume, or stream teardown/recreate paths.

Several fields represent latched or clear-on-write-style hardware state rather than durable configuration. Examples include perf counter interrupt status/ack bits, DSC overflow/underflow status bits, DWB overflow flags and counters, APG audio CRC done/clear and FIFO overflow clear bits, DME metadata-taken/missed clear bits, VPG update pending/taken status, DP symbol/DPHY error status, and CRC done/value fields. Memory-power state fields in `DSCC3`, `DWB`, `DCHVM`, `APG0`, `DME5`, and `DP_SYM32_ENC0` reflect power-management state machines and should not be treated as ordinary software-owned storage.

Double-buffered fields matter in DSC, DWB, DP symbol encoder MSA/pixel format, DME, and VPG paths. Programming order must account for update lock, update pending, and taken/pending flags so hardware observes a coherent packet, timing, or color-processing configuration.

## Dependencies and integration points

- Depends on the matching DCN 3.5.1 offset/register headers for addresses such as `regDWB_ENABLE_CLK_CTRL`, `regDSCC3_DSCC_PPS_CONFIG*`, `regDP_SYM32_ENC0_*`, and `regDP_DPHY_SYM320_*`. This file only supplies field encodings.
- Integrates with AMDGPU display register helper macros, especially the generated mask/shift table patterns used by DWB (`dcn30_dwb`/`dcn35_dwb`), HPO DP stream/link encoder code (`dcn31`/`dcn32` HPO headers), audio/APG, VPG/DME, DSC, and perfmon code.
- Sits under `drivers/gpu/drm/amd/include/asic_reg/dcn`, making it ASIC/IP-version-specific generated data. Neighboring DCN versions repeat many layouts, so cross-version comparisons are useful but must not replace the DCN 3.5.1 source of truth.
- Touches externally visible display behavior: DSC compression packets, DP stream timing/metadata/audio SDPs, writeback capture output, CRC diagnostics, and power/clock gating.

## Risks and edge cases

- Chunk-boundary incompleteness: `DC_PERFMON19_PERFCOUNTER_CNTL` and `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0` are split across adjacent chunks. Any generated-header audit must reconcile the neighboring lines before deciding a field set is missing.
- Packed-register corruption: most registers combine unrelated bit fields. Full-register writes or wrong masks can corrupt reserved bits, interrupt a double-buffered update, or change hardware-owned status bits.
- Width and encoding mistakes: PPS DSC fields, DP MSA/VC-rate/SAT fields, DWB geometry, OGAM region descriptors, APG/VPG payload bytes, and perfmon selectors have narrow bit widths. Callers must clamp or validate values before shifting.
- Ordering hazards: DSC, DP stream encoder, VPG, DME, and DWB update paths use pending/taken/status bits. Writing payload data without respecting update or reset sequencing can produce torn packets, stale metadata, bad compression state, or link training/display artifacts.
- Power-management interactions: memory power force/disable/status and clock-gating bits can hide bugs, increase power draw, or make reads unreliable if accessed while a block is gated or powered down.
- Diagnostic-only fields are hardware-sensitive: CRC, test pattern, PRBS, symbol override, perfmon, and DPHY error controls can disturb normal DP output if enabled unintentionally.

## Test signals

- Build coverage with DCN 3.5.1 enabled should catch missing or renamed field macros in consumers that instantiate register tables for DSC, DWB, HPO DP, APG, DME, VPG, and perfmon blocks.
- Header consistency checks should compare split boundary registers with adjacent chunks and compare repeated instances (`DC_PERFMON19/20/21`, DWB OGAM RAM A/B regions, VPG packet slot fields, DP SDP GSP controls 0-14) for expected identical layouts.
- Runtime display tests should exercise DP link bring-up, HPO stream enable/disable, modesets, panel replay paths, DSC on/off modes, audio over DP, metadata packet transmission, and writeback capture.
- Status-path tests should read and clear DWB overflow, APG FIFO overflow/audio CRC done, DME missed/taken, DP DPHY error, CRC done/value, and perfmon interrupt status fields to verify ack/clear semantics.
- Power tests should cover suspend/resume, display idle, clock-gating toggles, and memory power transitions while checking that DWB, APG, DME, DCHVM, DSCC, and DP symbol encoder status fields settle as expected.
- Visual and protocol validation should include DSC sink compatibility, DP MSA correctness, SDP/GSP/audio packet observation where tooling is available, and DWB CRC/readback comparison against known frames.

### subset-b-002105: lines 39862-42078

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 39862-42078

## Purpose

This chunk is a generated AMD DCN 3.5.1 register-field shift/mask slice. It has no executable C logic; it publishes preprocessor constants used by AMDGPU display code to pack, update, and extract MMIO bitfields. Runtime code pairs these `__SHIFT` and `_MASK` values with the matching register offsets in `dcn_3_5_1_offset.h` and with AMD display register helper macros such as `REG_SET`, `REG_UPDATE`, and `REG_GET`.

The range contains 2,217 `#define` entries: 1,108 shift macros and 1,109 mask macros. It begins inside the tail of `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0`, covers HPO DisplayPort stream encoder instances 1 and 2 plus the beginning of instance 3, includes link/DPHY instance 1 fields, and stops inside `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL7`. Boundary completeness therefore depends on adjacent chunks.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, allocations, locks, or direct control paths in this chunk. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for preserving, setting, or reading the field.

The main covered families are:

- `DP_DPHY_SYM320_*`: tail CRC configuration/status/count masks for the first HPO DP DPHY Symbol32 block.
- `DP_STREAM_ENC1`, `DP_STREAM_ENC2`, and `DP_STREAM_ENC3`: stream-encoder clock enable/status, pixel-stream source mux, audio-stream source mux, clock-ramp-adjuster FIFO reset/enable/read-level/status/error/calibration controls, and spare registers.
- `APG1`, `APG2`, and `APG3`: HPO DP audio packet generator reset/enable, DP audio stream ID, debug generator, packet source selection, audio CRC controls/results, audio/HBR/fifo-overflow status, output-active state, memory-power controls, and spare fields.
- `DME6`, `DME7`, and `DME8`: metadata engine controls for HUBP requestor selection, enable, stream type, double-buffer pending/taken/clear/disable, missed-transmission status/clear, and metadata memory-power fields.
- `VPG6`, `VPG7`, and `VPG8`: video packet generator access/data registers, generic packet frame-update and immediate-update controls for generic packet slots 0-14, pending bits, conflict status/clear, memory power, ISRC packet data, and MPEG info packet fields.
- `DP_SYM32_ENC1` and `DP_SYM32_ENC2`: complete Symbol32 stream encoder field sets for enable/reset, pixel-to-symbol FIFO, MSA and pixel-format double buffering, pixel format, MSA payload words, hblank minimum symbol width, generic SDP packet controls 0-14, SDP/audio/metadata controls, MSA/VBID/stream controls, panel replay controls, video CRC controls/results/status, memory-power controls, and spare fields.
- `DP_LINK_ENC1` and `DP_DPHY_SYM321`: HPO DP link encoder 1 clock/spare fields and DPHY instance 1 control, status, SAT update, symbol override, test pattern, frame, FEC, SR insert, register-insert, MST VC payload, timestamp, CRC, error, and clock-pattern fields.
- `DP_SYM32_ENC3`: beginning of Symbol32 stream encoder 3, from reset/FIFO/MSA/pixel format through GSP controls 0-6 and the first two shift definitions for GSP control 7.

The exact shift/mask pairing has five expected chunk-boundary exceptions: lines 39862-39864 contain masks whose shifts are in the previous chunk, and lines 42077-42078 contain shifts whose masks are in the next chunk.

## Control Flow

This header has no runtime control flow. The normal consumer flow is:

1. DCN 3.5.1-specific modules include `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`.
2. Resource initialization in `display/dc/resource/dcn351/dcn351_resource.c` token-pastes generated register and field names into register, shift, and mask tables. Relevant users include `DCN31_APG_MASK_SH_LIST`, `DCN3_VPG_MASK_SH_LIST`, and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST`.
3. HPO DP stream encoder code in `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.*` uses those tables to program clocks, stream input muxing, FIFO reset/enable sequencing, MSA/pixel format, sideband packets, audio mute/ASP enablement, CRC diagnostics, and stream enable/status.
4. APG and VPG helper code uses the APG/VPG field tables for audio packet generation and generic/info packet programming.
5. Runtime modeset, link training, audio setup, metadata, diagnostics, suspend/resume, and disable paths issue register reads/writes through AMDGPU's register helper layer.

The macros do not encode ordering rules. Consumers must still sequence clocks, resets, FIFO enablement, packet double-buffering, stream enablement, link/DPHY programming, and status polling correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes state held in DCN 3.5.1 display hardware registers:

- Stream encoder clock, source mux, audio mux, and clock-ramp FIFO state for HPO DP stream instances 1-3.
- APG audio packet generator reset/enable, debug generation, packet source, CRC, FIFO-overflow, output-active, and memory-power state.
- DME metadata double-buffer and missed-transmission state, including clear bits and memory-power controls.
- VPG generic packet payload bytes, packet update requests, update-pending readbacks, conflict status/clear bits, ISRC/MPEG packet payload, and low-power memory state.
- Symbol32 encoder reset/enable, video FIFO reset/overflow, MSA payload, pixel format, generic sideband packet scheduling, audio packet controls, metadata packet enablement, MSA/VBID timing, stream enable/status, panel replay tunnel optimization, video CRC capture, and memory power state.
- Link/DPHY enable/reset, lane/mode configuration, active/disabled/CRC/error status, test pattern generation, FEC, MST VC payload allocation, timestamp generation, and DPHY symbol override/debug state.

Persistence is hardware-defined. Configuration bits generally remain until driver reprogramming, stream teardown, power-gating, suspend/resume, GPU reset, or ASIC reset. Status bits can be read-only, sticky, write-one-to-clear, self-clearing, or meaningful only while the relevant display clocks and power domains are active. This generated header does not document those access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which supplies the matching DCN 3.5.1 MMIO register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which includes this header and initializes APG, HPO DP stream encoder, HPO DP link encoder, stream encoder, and related register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`, where `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST*` and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST` consume `DP_STREAM_ENC*` and `DP_SYM32_ENC*` fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h` and `dcn31_apg.c`, which consume APG reset/enable/audio-stream/debug/memory-power fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.h` and VPG users, which consume VPG generic packet data, update, pending, and conflict fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c` and `display/dc/irq/dcn351/irq_service_dcn351.c`, which include the same generated DCN351 register headers for firmware service and IRQ register access.

Instance mapping is an important contract. In this range, HPO stream encoder 1 uses `APG1`, `DME6`, `VPG6`, and `DP_SYM32_ENC1`; stream encoder 2 uses `APG2`, `DME7`, `VPG7`, and `DP_SYM32_ENC2`; stream encoder 3 begins with `APG3`, `DME8`, `VPG8`, and `DP_SYM32_ENC3`. The suffixes are not globally interchangeable across APG/DME/VPG/SYM32 families, so resource code must use the intended register tables rather than assuming a simple shared numeric namespace.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing the wrong MMIO bit, corrupting neighboring fields, failing stream enablement, losing audio packets, or breaking link/DPHY status handling.
- The file is generated metadata. Manual edits risk diverging from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- Chunk boundaries split real registers. The opening `DP_DPHY_SYM320...CRC_CONFIG0` masks lack their shifts in this artifact, and the closing `DP_SYM32_ENC3...GSP_CONTROL7` shifts lack their masks here.
- Repeated HPO instances are easy to confuse. `DP_STREAM_ENC1/2/3`, `APG1/2/3`, `DME6/7/8`, `VPG6/7/8`, `DP_SYM32_ENC1/2/3`, and `DP_DPHY_SYM320/321` have similar names but target distinct hardware.
- Reset/status and pending fields are sequencing-sensitive. Polling the wrong `RESET_DONE`, `FIFO_RESET_DONE`, `VID_STREAM_STATUS`, generic-packet pending bit, or CRC-valid bit can cause timeout, stale state, or premature stream activation.
- Sideband and audio packet programming is timing-sensitive. Incorrect GSP payload size, transmission line number, SOF reference, double-buffer enable, ASP/audio mute, metadata enable, or update trigger fields can produce missing HDR/metadata packets, broken audio, or packet conflicts visible only on certain modes.
- Power-state fields can mask bugs. For APG, DME, VPG, Symbol32, and DPHY memory/power controls, invalid masks may only fail after low-power transitions, suspend/resume, or clock-gating paths.
- Link/DPHY fields interact with link training and diagnostics. Mistakes in lane count, mode, FEC, MST VC payload allocation, clock pattern, PRBS/test pattern, symbol override, or CRC/error status can break DisplayPort bring-up or obscure validation failures.

## Test Signals

Useful validation combines generated-header checks and hardware behavior:

- Build AMDGPU display support with DCN351 enabled. Missing or renamed macros should fail in `dcn351_resource.c`, DMUB DCN351 register setup, IRQ service setup, APG/VPG/HPO DP stream encoder tables, or link encoder tables.
- Mechanically verify shift/mask pairs for lines 39862-42078, allowing only the known boundary exceptions: three opening `DP_DPHY_SYM320...CRC_CONFIG0` masks and two closing `DP_SYM32_ENC3...GSP_CONTROL7` shifts.
- Compare this slice against AMD's DCN 3.5.1 register database and nearby generated headers such as `dcn_3_5_0_sh_mask.h` where field layouts are expected to match.
- Exercise HPO DisplayPort streams backed by stream encoder instances 1, 2, and 3 across enable, blank, modeset, disable, suspend/resume, and hotplug. Watch `DP_STREAM_ENC_CLOCK_EN`, FIFO reset-done, FIFO error, `DP_SYM32_ENC_RESET_DONE`, pixel FIFO overflow, and `VID_STREAM_STATUS`.
- Validate audio packet paths using APG1-3: stereo, multichannel LPCM, HBR/compressed formats, mute/unmute, stream ID changes, and audio CRC diagnostics.
- Validate VPG/DME sideband behavior with HDR/static metadata, generic info packets, ISRC/MPEG packets, one-shot versus frame/immediate updates, pending-bit clearing, and conflict status handling.
- Run DisplayPort link and DPHY diagnostics on both HPO DPHY instances where possible, including link training, lane-count changes, MST payload updates, FEC, PRBS/test patterns, symbol overrides, CRC capture, and error status readback.
- Watch kernel logs, display debugfs output, and external sink behavior for HPO stream timeouts, silent audio, missing HDR metadata, packet conflicts, CRC mismatches, DP training failures, resume-only failures, and instance-specific regressions.

## Cross-Chunk Notes

This is a middle chunk of `dcn_3_5_1_sh_mask.h`. The previous chunk is needed for the full `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0` field set and earlier HPO stream/link definitions. The next chunk is needed to complete `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL7` and the rest of Symbol32 encoder 3. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.5.1 HPO DisplayPort, APG, VPG, DME, link, or DPHY fields.

### subset-b-002106: lines 42079-44295

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 42079-44295

## Purpose

This chunk is a generated AMD DCN 3.5.1 register shift/mask header segment. It contains 2,217 preprocessor definitions and no executable code. The macros describe bit positions and masks for fields in DisplayPort HPO symbol encoder instance 3 (`DP_SYM32_ENC3`), MPC plane-composition instances (`MPCC0`-`MPCC3`), and per-MPCC output-gamma/gamut-remap blocks (`MPCC_OGAM0`-`MPCC_OGAM3`).

Consumers pair these field constants with register offsets from the matching `dcn_3_5_1_offset.h` header and AMD display register helpers. The constants are part of the ABI between driver source, generated register tables, and DCN 3.5.1 display hardware: a wrong mask or shift silently changes which hardware bits are read or written.

## Important API surface

There are no functions or types in this chunk. The important API is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the starting bit number for a field.
- `REGISTER__FIELD_MASK` gives the packed field mask.
- Register access code uses these with helpers such as `FD_SHIFT`, `FD_MASK`, `SF`, `SE_SF`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and block-specific register tables.

The major field groups are:

- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL7` through `...GSP_CONTROL14`: Generic Secondary-data Packet controls for DP symbol encoder 3. The common fields cover video/idle continuous transmission enables, one-shot trigger, one-shot position, double buffering, payload size, SOF reference, deadline-missed and pending status, double-buffer pending status, and a 16-bit transmission line number. The chunk starts mid-`GSP_CONTROL7`: masks for all fields are present, but the first two shift definitions for `GSP_VIDEO_CONTINUOUS_TRANSMISSION_ENABLE` and `GSP_IDLE_CONTINUOUS_TRANSMISSION_ENABLE` are immediately before the requested line range.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_METADATA_PACKET_CONTROL`: metadata packet enable, double-buffer enable, pending status, and line-number/trigger fields used for DP metadata sideband timing.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_AUDIO_CONTROL0`: audio secondary packet controls, including audio mute and ASP/ATP/AIP/ACM packet enables plus audio packet timing/status fields.
- `DP_SYM32_ENC3_DP_SYM32_ENC_VID_CRC_CONTROL`, `...VID_CRC_STATUS`, `...VID_CRC_RESULT0` through `...RESULT3`, and `...SPARE`: video CRC control, one-shot/continuous status, and four CRC result registers for stream validation/debug.
- `DP_SYM32_ENC3_DP_SYM32_ENC_MEM_POWER_CONTROL`: memory power force/disable/low-power/state fields for the symbol encoder block.
- `MPCC0` through `MPCC3` base composition fields: top/bottom source selection, OPP routing, composition mode, alpha blend mode, premultiplied-alpha mode, active-overlap-only blend, background bits-per-component, bottom gain mode, global alpha/gain, stereo-mixer controls, update-lock selection/status, top and bottom gains, background color components, OGAM memory power controls, and idle/busy/disabled status bits.
- `MPCC_OGAM0` through `MPCC_OGAM3` output gamma fields: OGAM mode/select/current status, LUT index/data, LUT write/read/host/config controls, RAM A and RAM B piecewise-linear region programming, per-channel start/end/base/slope/offset fields, and packed region descriptors for pairs of regions.
- `MPCC_OGAM0` through `MPCC_OGAM2`, plus the beginning of `MPCC_OGAM3`, gamut-remap fields: coefficient format, mode/current status, and A/B coefficient-bank pairs such as `C11_C12`, `C13_C14`, `C21_C22`, `C23_C24`, `C31_C32`, and `C33_C34`. The requested range ends before the full later `MPCC_OGAM3` continuation.

## Control flow and data flow

This header has no runtime control flow. Its data flow is compile-time expansion into register tables and MMIO accessors:

1. ASIC-specific DCN 3.5.1 initialization includes `dcn_3_5_1_sh_mask.h` and the matching offset header.
2. Register-list macros select per-block offsets and field masks/shifts for a concrete hardware instance.
3. Display code encodes desired field values by shifting and masking, then writes the packed value through AMDGPU/DC MMIO helpers.
4. Status paths read MMIO registers, mask/shift fields, and use the decoded values for polling, validation, or diagnostics.

For DP symbol encoder fields, the runtime paths live in HPO DP stream encoder code. That code programs stream enablement, secondary data packets, metadata/audio packet emission, VBID/MSA state, and CRC diagnostics through generated `DP_SYM32_ENC*` register tables.

For MPCC and OGAM fields, the runtime paths live in MPC/color-management code. Plane composition and blending decisions select MPCC top/bottom inputs and alpha/gain modes, while color-management programming writes OGAM LUT indices/data, PWL region descriptors, and gamut-remap coefficients. The repeated MPCC instance layout lets the same code operate on MPCC0-3 by selecting the instance-specific register table.

## State and persistence

The macros hold no runtime state. The state they describe is hardware-resident:

- DP GSP, metadata, and audio packet registers determine how secondary data packets are emitted on a stream. Continuous/one-shot enable bits and line-number fields persist until overwritten, display reset, power-gate, modeset reinitialization, or firmware/hardware reset.
- DP CRC control/status/result fields expose stream validation state. One-shot pending/status bits are timing-sensitive and may change as frames pass.
- MPCC selection, OPP routing, alpha/gain, background color, stereo-mixer, and update-lock fields define active composition state for display pipes.
- OGAM LUT RAM A/B, LUT index/data, region descriptors, offsets, bases, starts, ends, and slopes define output transfer-function state. These are persistent hardware tables and packed control registers, so stale or partial programming can affect visible color until the block is reprogrammed or reset.
- Memory-power fields such as `MPCC_OGAM_MEM_PWR_FORCE`, `MPCC_OGAM_MEM_PWR_DIS`, `MPCC_OGAM_MEM_LOW_PWR_MODE`, and state bits affect low-power behavior and may interact with display power management.

## Dependencies and integration points

- The matching generated offset header is required; these field macros only identify bit layout, not register addresses.
- `dmub/src/dmub_dcn351.c` includes `dcn_3_5_1_sh_mask.h` for DCN 3.5.1 ASIC register initialization, though this specific chunk's DP/MPCC fields are mainly consumed by display pipeline code rather than DMUB mailbox-only paths.
- HPO DP stream encoder code uses `DP_SYM32_ENC*` register/mask tables for stream setup, secondary packet programming, audio packet controls, and CRC diagnostics.
- MPC/MPCC code uses the `MPCC*` and `MPCC_OGAM*` fields for plane composition, blend/gain/background setup, update-lock handling, output gamma LUT programming, and gamut-remap programming.
- The generated naming convention is an integration point: register-table macros assume exact spelling of register and field names, so renames or missing companion offsets break builds, while wrong numeric values can pass builds and fail only at runtime.

## Risks and edge cases

- The chunk begins mid-register and ends mid-family. `GSP_CONTROL7` is missing two shift definitions from this range, and `MPCC_OGAM3` RAMB/gamut continuation is outside this range. The final per-file merge must reconcile adjacent chunks before treating either family as complete.
- Copy/paste or generator drift across repeated instances is high risk. `MPCC0`-`MPCC3` and `MPCC_OGAM0`-`MPCC_OGAM3` should stay structurally identical except for instance number and intentional boundary placement.
- Packed LUT and region fields are especially sensitive: LUT offsets are 9-bit fields, region segment counts occupy the high nibble positions in packed region pairs, start/end/base/slope values use 16- or 18-bit masks depending on register, and coefficient pairs are two 16-bit fields. A single shift error corrupts color tables.
- Full-register writes must preserve reserved or unrelated bits. Many registers combine control, status, pending, and line-number fields.
- Packet-timing fields can cause sink-specific failures. Incorrect GSP/audio/metadata line numbers, double-buffering, or one-shot triggers may only fail with HDR metadata, audio packet changes, replay/panel features, or particular DP sinks.
- Power controls can hide defects: forcing/disabling OGAM memory power may mask sequencing bugs or increase display power.
- Status fields such as pending, current mode, idle/busy/disabled, memory power state, and CRC one-shot pending should not be treated as writable configuration fields unless the hardware spec says so.

## Test signals

- Build coverage with DCN 3.5.1 enabled should catch missing macro names when register-list macros instantiate DP, MPCC, OGAM, and DMUB register tables.
- Static consistency checks should verify that each `__SHIFT` has a matching `_MASK`, and that each mask width matches the expected field width after shifting.
- Cross-version comparison against neighboring DCN 3.5.0/DCN 3.x headers should show expected structural alignment for repeated DP symbol encoder, MPCC, OGAM, and gamut-remap fields.
- Runtime DP tests should exercise HDR/metadata packet programming, audio packet enable/mute transitions, stream enable/disable, CRC one-shot and continuous modes, and modeset/suspend/resume reinitialization.
- Runtime MPC tests should cover multi-plane composition, alpha blending, global alpha/gain, background color fill, update locks, MPCC busy/idle polling, and OPP routing changes.
- Color-management tests should exercise gamma/degamma or output gamma LUT updates, PWL region programming, gamut-remap coefficient banks A/B, HDR color paths, and repeated updates across MPCC instances 0-3.
- Power-management tests should observe display stability and power after OGAM memory low-power/force/disable paths, including reset and resume cycles.

### subset-b-002107: lines 44296-46513

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 44296-46513

## Purpose

This chunk is a generated DCN 3.5.1 register field shift/mask slice for AMD display hardware. It does not implement executable logic; it supplies preprocessor constants that higher-level AMDGPU display code uses to compose, update, poll, and decode memory-mapped display register fields without hard-coding bit positions.

The line range spans several related display blocks:

- The tail of `MPCC_OGAM3` output gamma and gamut-remap definitions, including RAM-B exponent region descriptors and A/B double-buffered gamut-remap coefficients.
- Core `MPC` definitions for clock/reset, CRC capture, pending-update status, DPP/OPP/DWB routing, denormalization clamps, and output color-space conversion for four outputs.
- Display perfmon blocks `DC_PERFMON22` and `DC_PERFMON23`.
- Link/output packet blocks `AFMT5`, `VPG9`, `DME9`, `HPO_TOP`, and `DP_STREAM_MAPPER_CONTROL0..3`.
- Four repeated ABM instances, `ABM0..ABM3`, covering backlight PWM levels, ambient backlight control, ACE curves, histogram/luma statistics, frame-synchronized update locks, and histogram result registers.
- The beginning of `DPIA_MU_RBBMIF` timeout/status fields. The requested line range ends at `DPIA_MU_RBBMIF_STATUS__RBBMIF_INVALID_ACCESS_ADDR__SHIFT`; later status masks and AZ controller definitions are outside this chunk.

## Important APIs, Types, and Register Families

The public surface here is macro-only. Each field is represented by two macro families:

- `REGISTER__FIELD__SHIFT` gives the bit offset used when packing/unpacking field values.
- `REGISTER__FIELD_MASK` gives the field mask used by `REG_SET`, `REG_UPDATE`, `REG_GET`, and similar AMD display register helper macros.

Important register families in this chunk:

- `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_26_27` through `_32_33` describe pairs of output-gamma RAM-B expansion regions. Each region has a 9-bit LUT offset and a 3-bit segment count. The chunk starts mid-register-family, so region 26's shift definitions are in the previous chunk while its masks appear here.
- `MPCC_OGAM3_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM3_MPC_GAMUT_REMAP_Cxx_Cyy_{A,B}` define the gamut-remap matrix path for MPCC OGAM instance 3. The `MODE_CURRENT` bitfield is readback/status; A/B coefficient banks indicate double-buffered hardware programming.
- `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, `MPC_CRC_*`, `MPC_DPP_PENDING_STATUS`, and `MPC_PENDING_STATUS_MISC` expose global MPC operation, diagnostics, and update synchronization. CRC selection can target DPP, OPP, or DWB sources, and result registers split A/R, G/B, and C channels into 16-bit fields.
- `ADR_CFG_CUR_VUPDATE_LOCK_SET{0..3}`, `ADR_CFG_VUPDATE_LOCK_SET{0..3}`, `ADR_VUPDATE_LOCK_SET{0..3}`, `CFG_VUPDATE_LOCK_SET{0..3}`, and `CUR_VUPDATE_LOCK_SET{0..3}` define per-pipe vertical-update lock sets for atomic cursor/address/config updates.
- `MPC_DWB0_MUX` and `MPC_OUT{0..3}_MUX` define output routing and flow/rate control. Output mux fields select source paths, expose overflow errors, and include error-ack bits.
- `MPC_OUT{0..3}_DENORM_*`, `MPC_OUT_CSC_COEF_FORMAT`, and `MPC_OUT{0..3}_CSC_*` define denormalization clamps and output CSC matrices. Matrix coefficients are split into 16-bit pairs and A/B banks.
- `DC_PERFMON22_*` and `DC_PERFMON23_*` define event selection, counter state, run gating, count-off interrupts, interrupt ack/status bits, and high/low counter readback.
- `AFMT5_*` defines audio formatter controls: VBI packet pacing, audio packet layout/channel controls, HDMI/DP audio stream ID, IEC 60958 channel-status words, audio CRC generation/result, ramp/test controls, FIFO overflow status/ack, infoframe update, source selection, and memory power state.
- `VPG9_*` defines video packet generator generic packet byte access, frame/immediate update controls for generic packets 0-14, pending flags, conflict status/clear, memory power state, ISRC packet data, and MPEG infoframe update.
- `DME9_*` defines display metadata engine enable, HUBP requester ID, stream type, double-buffer pending/taken/clear, missed-transmission status/clear, and memory power controls.
- `HPO_TOP_*` defines high-performance output clock gating controls for display, SoC, HDMI stream/char, DP stream, and symbol clocks plus top-level HPO IO enable.
- `DP_STREAM_MAPPER_CONTROL{0..3}` maps each stream to a link target through a 3-bit target field.
- `ABM{0..3}_*` repeats the adaptive backlight management register layout for four instances. Each instance includes PWM level registers, ABM enable/bypass, IPS color-space coefficient selection, ACE offset/slope/threshold programming, missed-frame flags, HGLS read-progress and read-missed flags, histogram/luma statistics, sample-rate controls, histogram bin shift tables, 24 histogram result registers, and master-lock controls.
- `DPIA_MU_RBBMIF_TIMEOUT_CTRL`, `DPIA_MU_RBBMIF_TIMEOUT_CTRL2`, and the first three `DPIA_MU_RBBMIF_STATUS` shift definitions expose timeout delay/hold, timeout disable, invalid-access flag/type/address field positions for the DPIA memory-unit RBBM interface.

## Control Flow

There is no C control flow in this chunk. Runtime control flow appears in consumers that include this generated header and pass these constants into register helper macros.

The implied hardware programming flow is:

1. Driver resource construction selects the DCN 3.5.1 register set for matching ASICs and includes `dcn_3_5_1_sh_mask.h`.
2. Display block constructors build per-block register, shift, and mask tables from generated macros.
3. Runtime display code uses those tables to update bitfields during mode set, pipe programming, CRC capture, audio/video packet updates, ABM programming, and diagnostics.
4. Status fields in this chunk are polled or read back to decide whether an update took effect, whether a double-buffered write is pending, whether a CRC/result is ready, or whether an error condition must be acknowledged.

Several field groups imply important sequencing:

- `*_LOCK`, `*_REG_UPDATE_PENDING`, `*_UPDATE_AT_FRAME_START`, and `*_READBACK_DB_REG_VALUE_EN` fields on MPCC/ABM/VPG paths indicate double-buffered or frame-bound programming. Writers must lock or stage values, request update at a safe boundary, then wait for pending bits to clear before assuming hardware has latched the new value.
- `MPC_CRC_CTRL` has enable, continuous/one-shot pending, source select, update-enabled, and update-lock fields. CRC tests must sequence source selection before enabling capture and read result fields only after the relevant pending/update state is resolved.
- `MPC_OUT*_MUX` includes rate-control overflow and error-ack fields. Error handling must preserve routing fields while writing ack bits.
- `AFMT5` and `VPG9` packet update bits are separate from pending/status bits; packet payload writes through indexed byte registers should be followed by frame or immediate update requests and checked for conflict/pending status.
- `DME9_DME_CONTROL` double-buffer and missed-transmission bits require clear-on-write style handling for taken/missed flags.

## State and Persistence Behavior

The macros describe persistent MMIO register fields. Values programmed through these fields live in display hardware state until overwritten, reset, or power-gated. They are not filesystem state and do not persist across GPU reset or relevant display block power loss.

Stateful categories in this chunk:

- Latched configuration: color matrices, denorm clamps, mux selections, ABM PWM parameters, ACE thresholds/slopes, sample-rate values, audio packet metadata, and stream-to-link mapper targets.
- Double-buffered/frame-synchronous state: MPCC gamut-remap modes and coefficient banks, MPC pending-update status, ABM group locks, VPG packet updates, AFMT infoframe/audio channel-status updates, and DME metadata double-buffer controls.
- Diagnostic/readback state: MPC CRC result registers, DC perfmon counters and interrupt status, AFMT audio CRC/status, VPG conflict status, ABM histogram/luma readbacks, read-in-progress/missed-frame bits, and DPIA RBBMIF invalid-access/timeout status.
- Power/clock state: MPC/HPO clock gate disable fields, AFMT/VPG/DME memory power control fields, and ABM lock/update-at-frame-start fields that interact with display timing.

The line range contains a partial `DPIA_MU_RBBMIF_STATUS` definition. Any consumer needing complete DPIA status decode must use the full header, not just this chunk, because this chunk includes only three status shifts and not the remaining status masks.

## Dependencies and Integration Points

This header is generated from AMD ASIC register metadata and is tightly coupled to matching register-offset headers, block-specific register table macros, and AMD display helper macros. It depends on convention rather than C symbols: the macro names must match register table initializers in DCN block code.

Observed integration points in the surrounding tree include:

- DC resource and block constructors for DCN 3.5/3.5.1 include generated `dcn_3_5_1_sh_mask.h` and populate per-block shift/mask structs for MPC, ABM, AFMT/VPG, DME, HPO, perfmon, and related display engines.
- `dce_abm.h` uses `ABM_SF(...)` style macros against ABM register field names matching the ABM families in this chunk. The repeated `ABM0`-based field lists in common ABM code are adapted across ABM instances by generated register tables.
- CRC register names such as `MPC_CRC_CTRL` are referenced from display hardware sequencing and resource definitions. These constants support debugfs/KMS CRC capture and validation paths.
- `dmub/src/dmub_dcn351.c` includes the same generated header for DCN 3.5.1 register initialization, although this specific chunk is mostly display-pipe/audio/video/backlight rather than DMUB mailbox state.
- Link/audio/video programming code relies on AFMT, VPG, DME, HPO, and DP stream mapper field positions to align audio infoframes, generic packets, metadata, and link routing with stream encoder and link-encoder state.

## Risks and Edge Cases

- This is generated hardware-interface code; manual edits are high risk. A one-bit shift or mask error can silently misprogram unrelated bits in a display register.
- The chunk begins mid-family at `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_26_27`, where some shift definitions for region 26 are outside the chunk. Research consumers should merge adjacent chunks before making final per-file conclusions.
- The chunk ends mid-register at `DPIA_MU_RBBMIF_STATUS`; the remaining status fields and masks are outside this chunk. Treating this chunk as a complete DPIA status definition would miss timeout readback and clear bits.
- Several registers include write-one-to-clear or ack-like fields (`*_ACK`, `*_CLEAR`, `*_CLR`, error ack, missed-frame clear). Register update helpers must avoid read-modify-write patterns that accidentally re-clear status bits or preserve stale ack bits.
- Double-buffered fields can be timing-sensitive. Programming ABM, VPG, AFMT, DME, or gamut-remap fields without respecting lock, pending, and frame-start bits can cause missed frames, stale readback, or visible color/backlight artifacts.
- `MPC_SOFT_RESET` and clock/memory-power fields affect shared display blocks. Incorrect writes may reset active MPCC/SFR/SFT paths, gate clocks while a block is in use, or leave memory in a forced low-power state.
- Repeated instance blocks (`MPC_OUT0..3`, `ABM0..3`, `DP_STREAM_MAPPER_CONTROL0..3`) invite copy/paste mistakes in table generation. Instance N register names must map to instance N offsets.
- Mask widths encode hardware limits: e.g. 16-bit CSC coefficients, 10-bit luma thresholds, 17-bit PWM levels, 24-bit pixel counts, 32-bit histogram results, and 3-bit DP link targets. Higher-level code must clamp or validate values before packing them.

## Test Signals

Useful validation signals for consumers of these macros:

- Build coverage for DCN 3.5.1 display code with `dcn_3_5_1_sh_mask.h` included catches renamed or missing macro fields at compile time.
- KMS CRC tests and debugfs CRC capture should exercise `MPC_CRC_CTRL`, source selection, pending bits, and result field extraction.
- Atomic modeset and plane/cursor update tests should verify that `MPC_DPP_PENDING_STATUS`, `MPC_PENDING_STATUS_MISC`, and vertical-update lock-set fields converge after commits.
- Color-management tests should exercise MPCC OGAM/gamut-remap and MPC output CSC programming, including A/B double-buffer transitions and coefficient-format selection.
- Audio over HDMI/DP tests should verify AFMT packet controls, IEC 60958 channel-status programming, audio CRC completion, FIFO overflow handling, and infoframe update behavior.
- HDR/metadata and infoframe tests should exercise VPG generic packet updates, VPG conflict clear, MPEG/ISRC packet programming, and DME metadata double-buffer/missed-transmission flags.
- DisplayPort/HPO link tests should confirm DP stream mapper target selection and HPO clock/IO enable behavior during link bring-up and teardown.
- Backlight/ABM tests should verify PWM level programming, ambient/user/target/current/final duty-cycle readback, ABM enable/bypass, frame-start updates, missed-frame flags, luma statistics, and histogram result stability across all four ABM instances.
- Perf counter diagnostics should confirm `DC_PERFMON22` and `DC_PERFMON23` event selection, run gating, interrupt status/ack behavior, and high/low counter readback.
- Error-injection or register-access diagnostics should validate the complete DPIA RBBMIF status register using the full header, since this chunk only contains the first status shift fields.

### subset-b-002108: lines 46514-48830

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 46514-48830

## Purpose

This chunk is a generated shift/mask register-field slice for AMD DCN 3.5.1 display hardware. It has no executable functions or C types; its API surface is a large set of `#define` constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. Consumers pair these constants with the matching `dcn_3_5_1_offset.h` register offsets and AMDGPU/DC register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_SET`, and `REG_UPDATE_*`.

The covered lines span several hardware areas: DisplayPort/USB4 DPIA RBBMIF status, Azalia/HDA controller 1 command and response rings, generic HDA global registers, DCCG and DMU clock/power controls, DMCUB security/scratch/interrupt fields, DWB/MCIF writeback watermark and pstate fields, DCHUBBUB memory arbitration and SDPIF security fields, HUBP/HUBPREQ/HUBPRET pipe memory status for pipes 0-3, DPP top-level pipe enables, MPCC movable color-management placement, and the beginning of MPCC MCM shaper/3DLUT/1DLUT color-management fields for instance 0 plus the start of MCM1 shaper fields.

## Important APIs and register groups

- `DPIA_MU_RBBMIF_STATUS` exposes invalid-access and timeout reporting fields, including `RBBMIF_INVALID_ACCESS_FLAG`, access type/address, timeout readback, and `RBBMIF_INVALID_ACCESS_STATUS_CLEAR`.
- `AZCONTROLLER1_*`, `GLOBAL_*`, `INTERRUPT_*`, `STREAM_SYNCHRONIZATION`, `CORB_*`, `RIRB_*`, and endpoint immediate-command fields describe HDA/Azalia control surfaces: command output ring buffer (CORB), response input ring buffer (RIRB), immediate verb writes, response reads, DMA position buffer base addresses, stream interrupt enable/status bits 0-15, wall clock, wake/state-change, global reset/flush, and 64-bit address/stream-count capabilities.
- `DCE_VERSION`, `DCCG_GATE_DISABLE_CNTL2/5/6`, `SYMCLK*`, `DSCCLK_DTO_CTRL`, `DPPCLK_CTRL`, `PHY*SYMCLK_CLOCK_CNTL`, `DMU_CLK_CNTL`, `DMU_*CGTT_BLK_CTRL_REG`, and `ZPR_CLK_UNGATE_DELAY` define clock gating, root gating, dynamic clock, symbol-clock, DSC, DPP, PHY, and DMU clock-control bits.
- `DISP_INTERRUPT_STATUS_CONTINUE23/25`, `DCPG_INTERRUPT_DEST2`, `DCPG_INTERRUPT_STATUS_3`, and `DCPG_INTERRUPT_CONTROL_2/3` define display interrupt status, routing, and enable fields for idle/power-gating domains and additional display events.
- `DOMAIN22` through `DOMAIN25` provide power-gating config/status bits (`DOMAIN_POWER_FORCEON`, `DOMAIN_POWER_GATE`, `DOMAIN_PGFSM_PWR_STATUS`, and `DOMAIN_PGFSM_READ_DATA`), while `LONO_MEM_PWR_REQ_CNTL`, `AZ_MEM_GLOBAL_PWR_REQ_CNTL`, `COMPBUF_MEM_PWR_CTRL_2`, and `MPCC_MCM0_MPCC_MCM_MEM_PWR_CTRL` expose memory power request/disable/state controls.
- `DMCUB_RBBMIF_SEC_CNTL`, `DMCUB_SEC_CNTL`, `DMCUB_REGION3_TMR_AXI_SPACE`, `DMCUB_INTERRUPT_STATUS`, `DMCUB_SMU_INTERRUPT_CNTL`, and `DMCUB_SCRATCH16` through `DMCUB_SCRATCH23` are the DMUB/DMCUB integration fields for trusted-region access, security mode, SMU interrupts, and firmware scratch mailboxes.
- `MCIF_WB_*`, `DWB_ENABLE_CLK_CTRL`, and `MMHUBBUB_CLOCK_CNTL` cover display writeback, MCIF writeback pstate/watermark latency, and MMHUBBUB clock gating.
- `DCHUBBUB_ARB_*` defines display memory arbitration controls: QoS force during pstate transitions, DRAM/cstate policy, UCLK/FCLK/user-retraining watermarks A-D, HostVM threshold control, watermark-change mode, and MALL enable/power policy.
- `DCHUBBUB_SDPIF_*` defines SDPIF config/security classification per pipe for normal data, no-allocate, metadata, DCC metadata, cursor, and GPUVM requests, plus request-rate limiting.
- `HUBP0` through `HUBP3` and `HUBPREQ0` through `HUBPREQ3` define per-pipe HUBP clock, virtual memory page, MALL/SubVP, debug/status, UCLK pstate force, request-status, and read-line control fields. The `HUBP*_HUBP_MALL_STATUS` groups are dense status bitmaps for MALL requests, responses, local/cursor prefetch, SubVP retrieve, outstanding DRQ/MRQ/CRQ work, and static-screen or pstate-related MALL use.
- `DPP_TOP0_DPP_CONTROL` through `DPP_TOP3_DPP_CONTROL` expose per-pipe DPP top-level enable bits.
- `MPCC0` through `MPCC3_MPCC_MOVABLE_CM_LOCATION_CONTROL` describe movable color-management placement: output CM, 3D LUT, shaper, and 1D LUT location selection.
- `MPCC_MCM0_*` is the largest group in this chunk. It defines shaper offsets/scales/index/data/write enables, shaper RAMA/RAMB piecewise-linear region start/end tables, 3DLUT mode/index/data/read-write/output-normalization/output-offset fields, 1DLUT mode/select/PWL-disable/current-state, LUT index/data/control fields, 1DLUT RAMA/RAMB start slopes/bases/ends/offsets/region tables, and MCM memory power controls. `MPCC_MCM1_*` begins the same shaper layout and reaches `MPCC_MCM1_MPCC_MCM_SHAPER_RAMA_REGION_12_13__...SHIFT` at the chunk boundary.

## Control flow and usage model

There is no local control flow. The generated constants are data for higher-level register tables. A typical consumer flow is:

1. Include `dcn_3_5_1_offset.h` and this shift/mask header for ASIC-specific addresses and bit encodings.
2. Build per-block register, mask, and shift tables with macros such as `SR`, `SF`, `HUBBUB_SF`, `DMUB_SF`, `FD_MASK`, and `FD_SHIFT`.
3. Let block code call register helpers to read, modify, or write fields without hardcoding bit positions.

The DCN 3.5.1 DMUB path includes this header in `display/dmub/src/dmub_dcn351.c`; `dmub_srv_dcn351_regs_init()` copies offsets, masks, and shifts into `dmub->regs_dcn35`. Hubbub code uses fields from this chunk through the DCN35/DCN32 register lists; for example `hubbub32_force_usr_retraining_allow()` updates `DCHUBBUB_ARB_ALLOW_USR_RETRAINING_FORCE_VALUE` and `DCHUBBUB_ARB_ALLOW_USR_RETRAINING_FORCE_ENABLE` in `DCHUBBUB_ARB_USR_RETRAINING_CNTL`. MPC headers for DCN32/DCN42 use the MPCC MCM fields to populate color-management register tables, including shaper, 3DLUT, and 1DLUT masks.

## State and persistence behavior

The header itself has no mutable state. The state lives in MMIO or indexed hardware registers and persists according to display hardware lifecycle: boot initialization, modeset/reprogramming, DC/DMCUB firmware init, runtime power-management transitions, suspend/resume, GPU reset, and display IP reset.

Several groups are explicitly stateful in hardware:

- HDA/Azalia CORB/RIRB pointers, DMA enables, base addresses, response interrupts, global reset/flush, and immediate-command busy/result bits track live audio-controller command flow.
- DCCG/DMU/DCPG/domain fields affect clock and power-gating state. Incorrect persistence can leave blocks gated while in use or force blocks on and increase power.
- DCHUBBUB watermarks and pstate/cstate policy fields control when memory clocks, fabric clocks, and user retraining may change. These values must track active timing, bandwidth, and safe-to-lower policy.
- HUBP MALL/SubVP status fields reflect transient cache/prefetch/retrieve/outstanding-request state. Some fields are diagnostic/status readbacks rather than software-owned controls.
- MPCC MCM shaper/3DLUT/1DLUT RAM index/data/control fields represent programmed color pipeline tables. The instance, RAM bank, channel, index, and write-enable fields must stay consistent while programming LUT contents.
- DMUB scratch/security/interrupt fields are shared with firmware and the SMU, so persistence and ordering matter across firmware handshakes.

## Dependencies and integration points

- Requires `dcn_3_5_1_offset.h` for the corresponding register addresses and base indices. Representative matches in that file include `regDCHUBBUB_ARB_USR_RETRAINING_CNTL`, `regHUBP0_HUBP_MALL_STATUS`, `regMPCC_MCM0_MPCC_MCM_SHAPER_CONTROL`, and `regAZCONTROLLER1_CORB_CONTROL`.
- Depends on AMDGPU/DC register macro infrastructure to turn generated names into table entries and field operations. The names must match exactly; there is no type checking for a misspelled field beyond compilation failures or unused orphan defines.
- Integrates with DMUB service initialization for DCN 3.5.1, the DC IRQ service for DCN 3.5.1, DC Hubbub watermarks/memory arbitration, HUBP memory/cache behavior, DCCG/DMU clock and power management, HDA display-audio control, and MPC color-management programming.
- Shares layouts with nearby DCN versions. Many fields in this chunk appear in DCN 3.2, 3.5.0, 4.1, and 4.2 generated headers, but some bitmaps differ by generation, especially MALL status fields and added/removed power/security controls. Cross-version copy assumptions are risky.

## Risks and edge cases

- Generated-header drift: offset and shift/mask headers must be regenerated as a pair. A valid mask with a stale offset silently targets the wrong hardware register.
- Packed-field corruption: many registers have adjacent control/status bits. Full-register writes can clobber reserved or status bits; callers should use read-modify-write helpers where appropriate.
- Width and sign errors: fields such as 8-bit ring pointers, 14-bit user-retraining watermarks, 16-bit UCLK/FCLK watermarks, 19-bit shaper offsets, 9-bit LUT offsets, and 3-bit segment counts require clamping before shifting.
- Instance mismatch: HUBP0-3, HUBPREQ0-3, DPP_TOP0-3, MPCC0-3, and MCM0/MCM1 fields repeat similar names. Using the wrong instance can make a bug look like a timing, cache, or color issue on only one pipe.
- Status versus control confusion: `*_STATUS`, `*_CURRENT`, `*_READBACK`, and MALL/HUBPREQ status fields are not necessarily software-owned. Writing status masks as if they were controls can acknowledge interrupts, clear diagnostics, or do nothing depending on hardware semantics.
- Power and clock hazards: `*_FORCEON`, `*_POWER_GATE`, clock-gating disable, low-power-mode, and memory-power fields can create hangs or excess power if changed outside the expected sequencing.
- Firmware handshake hazards: DMUB scratch, security, SMU interrupt, and RBBMIF fields may be accessed by firmware or secure paths. Reordering or unsynchronized host writes can break firmware-visible protocols.
- Color pipeline artifacts: MPCC MCM shaper/3DLUT/1DLUT programming is table- and bank-oriented. Wrong write-enable masks, bank selection, index increments, or region segment counts can cause visible color errors that only appear with HDR, color-managed, or multi-plane configurations.
- Boundary truncation: this chunk ends in the middle of the `MPCC_MCM1` shaper RAMA region definitions, so final per-file analysis must reconcile the continuation in the next chunk before drawing complete conclusions for MCM1.

## Test signals

- Build with DCN 3.5.1 enabled and ensure all consumers of `dcn_3_5_1_sh_mask.h` compile with matching `dcn_3_5_1_offset.h` symbols.
- Static consistency checks can compare field masks/shifts against generated offsets for representative registers and verify repeated pipe/instance groups have expected bit-identical layouts where the hardware block is repeated.
- Display bring-up and modeset tests should exercise pipes 0-3, HUBP MALL/SubVP paths, DPP enables, and MPCC color-management placement.
- Watermark and power tests should cover UCLK/FCLK pstate transitions, user retraining force/allow behavior, cstate/deepsleep policy, suspend/resume, and safe-to-lower watermark paths.
- Audio tests should cover HDMI/DP HDA enumeration, CORB/RIRB DMA operation, immediate command response handling, stream interrupts, and DMA position buffer behavior.
- DMUB/SMU tests should validate scratch mailbox handshakes, SMU interrupt signaling, DMCUB security enablement, and RBBMIF invalid-access reporting/clear behavior.
- Color-management tests should load shaper, 3DLUT, and 1DLUT tables, verify RAM bank/channel/index programming, and compare rendered output for SDR/HDR and color-managed modes.
- Runtime diagnostics should inspect register dumps around `HUBP*_HUBP_MALL_STATUS`, `HUBPREQ*_HUBPREQ_STATUS_REG*`, `DCHUBBUB_ARB_*`, and `MPCC_MCM*_MEM_PWR_CTRL` when debugging pstate stalls, MALL issues, power regressions, or color artifacts.

### subset-b-002109: lines 48831-51051

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 48831-51051

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata for the MPCC MCM color-management block. It contains no executable logic; it exports preprocessor constants that define field shifts and masks for MMIO registers. The constants are paired with the corresponding DCN 3.5.1 offset header and consumed by AMD display register helpers to read, write, and update individual hardware fields.

The requested range covers the tail of the `MPCC_MCM1` block, the full `MPCC_MCM2` block, and most of the `MPCC_MCM3` block. These MPCC instances expose shaper LUT control, shaper RAM A/B piecewise regions, 3D LUT programming, 1D LUT programming, LUT RAM A/B region descriptors, and memory power controls. Although this repository path is under a local `ceph-client` mirror, this source is AMDGPU display hardware metadata and is unrelated to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or includes in this range. The exported interface is entirely generated macros:

- `MPCC_MCM*_REGISTER__FIELD__SHIFT`: the bit position for a field in an MPCC MCM register.
- `MPCC_MCM*_REGISTER__FIELD_MASK`: the bit mask for the same field.

Major macro families in this chunk:

- `MPCC_MCM1` tail: starts inside `MPCC_MCM_SHAPER_RAMA_REGION_12_13`, then completes shaper RAMA regions through `32_33`, all shaper RAMB start/end/region descriptors, 3D LUT control/data registers, 1D LUT control/data/register programming, 1D LUT RAMA/RAMB start/end/offset/region descriptors, and `MPCC_MCM_MEM_PWR_CTRL`.
- `MPCC_MCM2`: complete instance-local definitions for shaper control, shaper LUT index/data/write-enable/mode/selection/scales/offsets, shaper RAMA/RAMB start/end/region descriptors, 3D LUT mode/index/data/30-bit/read-write/norm-factor/output-offset fields, 1D LUT control/index/data/LUT-control fields, 1D LUT RAMA/RAMB start/end/slope/base/offset/region descriptors, and memory power control/state fields.
- `MPCC_MCM3`: complete definitions from shaper control through `MPCC_MCM_1DLUT_RAMB_REGION_20_21`, then starts `MPCC_MCM_1DLUT_RAMB_REGION_22_23` with shift fields only before the requested range ends.

Important represented fields include LUT bypass/mode/select/current status, read/write selection, host access selection, write color masks, LUT indices/data payloads, 3D LUT size/RAM select/config status/30-bit enable, output normalization and RGB offsets, per-channel shaper and 1D LUT start/end/base/slope/offset values, per-region LUT offsets and segment counts for regions 0 through 33, and low-power/power-disable/power-state fields for shaper, 3D LUT, and 1D LUT memories.

The repeated region registers use a consistent packed layout. For most `REGION_N_N` pairs, region N uses LUT offset bits starting at shift `0x0` and segment-count bits at `0xc`; region N+1 uses LUT offset bits at `0x10` and segment-count bits at `0x1c`. Masks are typically `0x000001FFL`, `0x00007000L`, `0x01FF0000L`, and `0x70000000L` for the four packed fields.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from the display driver code that includes this generated metadata:

1. DCN 3.5.1 code includes `dcn_3_5_1_sh_mask.h` with the matching register offset header.
2. Register-list and field-list macros token-paste register and field names into per-block register, shift, and mask tables.
3. Runtime MPC/color-management code calls helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_WAIT`, and table-building macros such as `SF`/`SRII`.
4. Those helpers use these shift/mask constants to isolate, compose, and preserve fields during MMIO read-modify-write sequences.

The implied runtime flows are MPCC MCM color-pipeline programming: selecting shaper and 1D LUT RAM banks, loading LUT entries through host-visible index/data windows, programming piecewise-linear region boundaries and segment counts, enabling or bypassing shaper/1D/3D LUTs, setting 3D LUT dimensions and precision, applying RGB output offsets, and managing SRAM power state around LUT use.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on its own. It describes MMIO-backed GPU display state.

Represented hardware state includes active/pending LUT modes, selected RAM banks, current in-use RAM selections, LUT host access routing, 1D and shaper RAM contents through index/data windows, region geometry for piecewise LUT interpolation, RGB start/end/base/slope/offset values, 3D LUT configuration and data payloads, normalization factors, output offsets, and memory power force/disable/state bits.

Persistence is determined by the MPCC MCM hardware block. Control fields usually remain in hardware until reprogrammed, modeset, power-gate transition, suspend/resume, display reset, or ASIC reset. LUT RAM contents and region descriptors may be lost or invalid while the relevant memory is disabled or in a low-power state. Current/status fields are hardware-reflected and may lag requested state until the block has accepted new programming.

## Dependencies And Integration Points

This chunk depends on AMD's generated register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides the corresponding MMIO offsets and instance selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h`, which defines symbolic values for MPCC MCM LUT modes, RAM selection, LUT segment counts, 3D LUT size/bit-depth, gamut remap modes, and memory power states.
- AMD display register helper infrastructure used by MPC/resource code to turn generated shift/mask macros into typed register tables.

Representative integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which includes the DCN 3.5.1 offset and mask headers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.c`, where MPCC MCM fields are used for 1D LUT power control, LUT RAM selection, region programming, and shaper/3D LUT behavior inherited by later DCN versions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h`, which lists MPCC MCM register instances and fields for resource construction.
- DRM color-management paths such as `amdgpu_dm_color.c` and `amdgpu_dm_colorop.c`, which feed shaper LUT, 3D LUT, transfer-function, and plane color-operation state into lower-level DC programming.

The later merge lane should combine this with adjacent chunks because this range starts in the middle of `MPCC_MCM1_MPCC_MCM_SHAPER_RAMA_REGION_12_13` and ends in the middle of `MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_22_23`.

## Risks And Edge Cases

- Shift/mask drift is the primary risk. These untyped constants can compile successfully while targeting the wrong hardware bits, causing subtle color-management failures.
- The repeated MPCC instances are copy-sensitive. `MPCC_MCM2` and `MPCC_MCM3` should be structurally equivalent; an instance-specific typo can affect only one blending/composition pipe and be missed by simple single-plane or single-display testing.
- The requested chunk has artificial boundaries. `MPCC_MCM1_SHAPER_RAMA_REGION_12_13` is missing its first shift definition from this range, and `MPCC_MCM3_1DLUT_RAMB_REGION_22_23` has shifts without the matching masks here. Complete validation needs adjacent chunks.
- Packed region descriptors are easy to corrupt. Bad LUT offset or segment-count masks can load the wrong piecewise region boundaries, producing banding, clipping, non-monotonic transfer curves, or channel-specific color errors.
- Host index/data programming is sequencing-sensitive. Wrong index, data, RAM-select, host-select, or write-color-mask fields can write the wrong RAM bank, wrong channel, or wrong LUT entry.
- Current/select status fields can be confused with request fields. Code must distinguish requested RAM/mode selections from hardware-current status before flipping active LUT banks.
- Memory power fields affect availability of LUT SRAMs. Incorrect power-disable/force/low-power masks can lose LUT contents, make writes ineffective, or cause `REG_WAIT` timeouts while waiting for power state.
- 3D LUT precision and size fields are compact control bits. Wrong masks can select the wrong cube size, 30-bit mode, RAM target, or read/write behavior, causing visible color transforms to differ from DRM color state.

## Test Signals

Useful validation signals combine generated-header checks and display color behavior:

- Build AMDGPU/DCN 3.5.1 paths with register-table construction enabled; missing or malformed macros should fail at compile time where `SF`, `SRII`, or `REG_*` users reference them.
- Mechanically verify each complete register group in this range has paired `__SHIFT` and `_MASK` definitions and that masks align with expected shifts and field widths. Exclude the known partial boundary groups until adjacent chunks are merged.
- Diff `MPCC_MCM2` and `MPCC_MCM3` definitions against each other and against nearby generated DCN generations, especially DCN 3.2/3.5 MPCC MCM headers, where most field layouts are expected to remain stable.
- Exercise DRM plane color pipelines that use shaper LUT, 3D LUT, and 1D LUT programming: bypass modes, identity LUTs, nontrivial transfer functions, per-channel curves, 17-cube 3D LUTs, and RAM bank flips.
- Validate visible output with color ramps and calibration patterns for banding, clipping, wrong channel mapping, wrong gamma, stale LUT contents, and differences between MPCC instances.
- Test modeset, plane enable/disable, atomic color property updates, suspend/resume, and display hotplug while color transforms are active to catch lost SRAM contents or incorrect power-state handling.
- Monitor kernel logs and DC debug output for register wait timeouts, color-management programming failures, blank frames during LUT updates, and mismatches between requested and current LUT mode/RAM selection.

## Cross-Chunk Notes

The previous chunk owns the beginning of `MPCC_MCM1`, including the omitted start of `MPCC_MCM1_MPCC_MCM_SHAPER_RAMA_REGION_12_13`. The next chunk owns the rest of `MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_22_23`, later `MPCC_MCM3` region descriptors, and any remaining MPCC MCM fields. The final per-file report should merge those adjacent ranges before making complete claims about all MPCC MCM instance definitions in `dcn_3_5_1_sh_mask.h`.

### subset-b-002110: lines 51052-53401

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 51052-53401

## Purpose

This chunk is the tail of the generated DCN 3.5.1 register shift/mask header for AMD display hardware. It contains only preprocessor constants, not executable code. Each `#define` maps a hardware register field to its bit shift (`__SHIFT`) or mask (`_MASK`) so the display driver can use common register helpers (`REG_SET`, `REG_UPDATE`, `REG_GET`, and macro-generated register structures) without hard-coding bit positions in functional code.

The covered range spans multiple display pipeline blocks:

- MPCC MCM 1D LUT region and memory power fields.
- OPP clock gate reporting disable.
- OTG0-OTG3 long-vblank, DLPC snapshot/resync, CRC readback-window, and DRR count fields.
- DP0-DP4 stream/link symbol counters, ALPM scrambled-zero control, MSA transmission enable, and MST stream allocation table encryption bits.
- DIG0-DIG4 front-end/back-end clock, enable, FIFO, HDMI mode, and stream-mapper fields.
- AFMT0-AFMT5 ACP audio packet fields.
- DIO DPIA mux, I2C clock-enable, DIO status/clock-gating, PSP interrupt, stream mapper, UNIPHY channel enable, DLPC intercept/reset, GPIO drive, and panel power-sequence fields.
- DSCC/DSC top configuration and interrupt fields.
- HDMI FRL/link/stream/TB encoder fields, including generic packet scheduling, ACR N/CTS, metadata packets, CRC, encryption, buffers, memory power, and FIFO status.
- DP stream encoder, DP sym32 encoder, DP DPHY sym32, and DPIA microcontroller/perf-counter fields.
- Azalia F2 and F0 endpoint ACP packet fields.

## Important APIs, Types, And Macros

This header does not declare C types or functions. Its public surface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field bitmask.
- Repeated instance prefixes (`OTG0`-`OTG3`, `DP0`-`DP4`, `DIG0`-`DIG4`, `AFMT0`-`AFMT5`, `DSCC0`-`DSCC3`, `DP_SYM32_ENC0`-`3`, `DP_DPHY_SYM320`-`1`, `AZF0ENDPOINT0`-`4`) encode hardware instance selection.

The main consumers are the register-list and field-list macros in the DC resource and block headers. For DCN 3.5.1, `dcn351_resource.c` includes `dcn/dcn_3_5_1_offset.h` and this `dcn/dcn_3_5_1_sh_mask.h`, then expands macros such as `SR`, `SRI`, `SR_ARR`, `SR_ARR_INIT`, and `*_MASK_SH_LIST(...)` to populate block-specific register, shift, and mask structs. Examples visible from the integration path include:

- AUX engines using `DP_AUX0_AUX_CONTROL__AUX_RESET_MASK` as the common reset mask while instance-specific register offsets are generated separately.
- DIO and HW sequencer mask lists pulling clock-gating, reset, DIO, DPIA, and power fields into typed mask/shift tables.
- Audio code accessing Azalia codec endpoint registers indirectly through indexed register writes, with ACP-related fields represented here for packet control and endpoint state.

## Control Flow

There is no runtime control flow in this chunk. Control flow is indirect:

1. DCN 3.5.1 resource construction includes this header during compilation.
2. Resource initialization macros copy selected constants into register-block tables.
3. Runtime display code calls register helpers with symbolic field names.
4. The helper macros combine a register address from offset headers with the shift/mask constants from this header to write or read the correct bits.

The header therefore acts as a compile-time hardware ABI layer. If a field definition is wrong, the fault appears later as bad MMIO programming in unrelated-looking display code.

## State And Persistence Behavior

The constants describe fields that control or report hardware state, but the header itself stores no state and persists nothing. Hardware state represented by this range includes:

- Persistent-until-reset programming state such as HDMI packet controls, generic packet line scheduling, ACR values, DIG clock enables, stream mapper targets, DIO DPIA mux source selection, GPIO drive impedance, panel power-sequence drive settings, and DSC/DSCC configuration.
- Volatile status/readback state such as OTG CRC window readbacks, long-vblank counters, DP symbol counters, DP link cycle counters, HDMI CRC results, FIFO error/status bits, DPIA interrupt/status bits, and memory power-state readbacks.
- Power-management state such as MPCC MCM LUT memory power controls, HDMI borrow-buffer memory power controls, DSC dynamic clock gating, DIO clock gates, OPP fine-grain clock gate reporting, and DPIA clocks/resets.

Because many masks cover clock, reset, power, and packet scheduling fields, incorrect values can survive across modesets until the affected block is reset or reprogrammed.

## Dependencies And Integration Points

This file depends on the matching DCN 3.5.1 offset header for register addresses. The shift/mask names must match the register names used by block-specific resource macros in `drivers/gpu/drm/amd/display`.

Key integration points:

- `dc/resource/dcn351/dcn351_resource.c` includes this header and builds DCN 3.5.1 resource tables for AUX, DIO, HW sequencer, clock, DSC, stream/link encoders, audio, I2C, and related display blocks.
- `dc/dce/dce_aux.h` defines common AUX register and field-list macros; the resource layer supplies the DCN-specific shifts/masks.
- DIO/DPIA fields integrate USB4 DisplayPort Input Adapter routing, mux control, clocking, reset, local interrupts, hidden-port status, glue enable, and performance counters. Higher-level DPIA behavior also involves DMUB commands and notifications for AUX-over-DPIA and bandwidth allocation.
- DP/DIG/HDMI/AFMT fields integrate with stream encoder and link encoder programming for DisplayPort, HDMI, FRL/TMDS, audio info/ACP packets, MST encryption status, ALPM, and symbol-count diagnostics.
- OTG/OPTC/DLPC fields integrate timing-generator behavior, dynamic refresh/long-vblank handling, CRC capture, and display logic power control snapshots.
- Azalia endpoint fields integrate with the display audio path, including indexed endpoint register access and ACP packet support.

## Risks

- Generated-header drift: the constants must match the ASIC register specification and the matching offset header. A stale or mismatched mask silently corrupts unrelated fields in MMIO writes.
- Instance symmetry assumptions: many blocks repeat identical field layouts across instances. If one instance differs but retains copied masks, only specific pipes/connectors fail.
- Clock/reset/power hazards: DIO, DIG, HDMI, DSC, DPIA, OPP, and MPCC power fields can hang or blank displays if toggled with an incorrect bit position.
- Packet scheduling hazards: HDMI generic packet, metadata, ACP, ACR, and audio fields are timing-sensitive. Wrong masks can cause missing HDR/Dolby Vision metadata, audio clock drift, invalid infoframes, or link training failures.
- Security/status ambiguity: DP MST SAT encryption enable/status fields and HDMI encryption control fields are only bit definitions here. Incorrect field mapping can misreport or misprogram encrypted transport state.
- Diagnostics fragility: CRC, symbol-count, FIFO, and DPIA perf-counter fields are often used for validation and debug. Bad masks can hide real hardware failures or create misleading test signals.

## Test Signals

Since this chunk is compile-time register metadata, direct unit tests are unlikely. Useful validation signals are integration and hardware-facing:

- Successful build of AMD display code using `dcn_3_5_1_sh_mask.h` with no missing macro names in DCN 3.5.1 resource initialization.
- Display bring-up on DCN 3.5.1 hardware across DP, HDMI, eDP/panel, and USB4 DPIA paths.
- Modeset and link-training tests covering DP0-DP4, DIG0-DIG4, HDMI FRL/TMDS, DSC, and DPIA-routed endpoints.
- Audio validation for HDMI/DP audio, ACP packet programming, ACR N/CTS stability, and Azalia endpoint access.
- CRC/debugfs or display validation tests that read OTG/HDMI/DP CRC and symbol counter status fields.
- Power-management tests for suspend/resume, display idle, clock gating, memory low-power states, and DPIA reset/interrupt handling.
- MST/HDCP or encrypted-transport validation for DP SAT encryption status and HDMI encryption-related fields where supported.

### subset-b-002111: lines 53402-53464

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 53402-53464

## Purpose

This chunk is the tail of the generated DCN 3.5.1 shift/mask header for AMD display hardware. It defines bit positions and bit masks for Azalia/HDA function 0 endpoint registers on endpoints 4, 5, 6, and 7, then closes the header include guard. The covered registers are:

- `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`
- `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`
- `AZF0ENDPOINT6_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`
- `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`
- `AZF0ENDPOINT4..7_AZALIA_F0_ENDPOINT_FGCG_REP_DIS`

The `ACP_DATA` fields describe the HDA codec pin Audio Content Protection/Audio Info capability data. Each endpoint exposes the same layout: `ACP_INDEX` in bits 0-5, `SUPPORTS_AI` at bit 6, `ACP_PACKET_ENABLE` at bit 7, `ACP_TYPE` in bits 8-9, and two type-dependent bytes in bits 16-23 and 24-31. The `ENDPOINT_FGCG_REP_DIS` register has a single bit at bit 0 used to disable fine-grain clock-gating reporting for that endpoint.

## Important APIs, Types, And Macros

This file does not define callable APIs or C types. Its exported interface is preprocessor symbols consumed by AMD display register helper macros:

- `*_SHIFT` constants provide the low bit index for a field.
- `*_MASK` constants provide the already-positioned 32-bit field mask.
- The symbols are intended for use through AMD's `set_reg_field_value`, `get_reg_field_value`, `REG_UPDATE`, and related register access macros rather than open-coded shifts.
- The matching address/index definitions live in `dcn_3_5_1_offset.h`. For these endpoints, `ixAZF0ENDPOINT4..7_AZALIA_F0_ENDPOINT_FGCG_REP_DIS` is index `0x0070`; the matching ACP data index is the HDA pin control ACP data node register used by the endpoint indirect access path.

The main integration type is `struct dce_audio` from `display/dc/dce/dce_audio.h`, which owns `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask`. Resource files such as `display/dc/resource/dcn351/dcn351_resource.c` allocate per-instance audio register tables for DCN 3.5.1 audio objects, while common DCE audio code uses those tables to access endpoint registers.

## Control Flow

There is no runtime control flow inside this generated header. At build time, including DCN 3.5.1 resource and hardware headers makes these constants available to the display core. Runtime control flow is in the audio path:

1. DC resource construction creates audio objects for available audio endpoints and assigns register, shift, and mask tables.
2. Display mode/connector commits propagate sink audio information into `struct audio_info`.
3. `dce_aud_az_configure()` programs Azalia/HDA pin-control registers through `AZ_REG_READ()` and `AZ_REG_WRITE()`.
4. For ACP data, the common audio implementation reads `AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`, updates `SUPPORTS_AI` from `audio_info->flags.info.SUPPORT_AI`, and writes the value back.
5. The endpoint-specific generated symbols allow the same logical operation to target endpoint instances without hard-coding endpoint-specific bit arithmetic.

The `FGCG_REP_DIS` bit is part of the hardware control surface for clock-gating reporting. This chunk only exposes the field encoding; any policy that toggles clock gating lives in DC hardware sequencing/resource code.

## State And Persistence

These macros are compile-time constants and do not hold state. The state they describe is hardware register state:

- `ACP_DATA` persists in the HDA/Azalia endpoint register until reprogrammed or reset by the device/power-management path.
- `SUPPORTS_AI` reflects sink capability programming for audio info packets.
- `ACP_PACKET_ENABLE`, `ACP_TYPE`, and type-dependent bytes are available for packet/capability configuration even though the common code path observed in `dce_audio.c` primarily updates `SUPPORTS_AI`.
- `ENDPOINT_FGCG_REP_DIS` affects endpoint clock-gating reporting behavior until hardware reset or explicit rewrite.

Because these are MMIO or indirect codec endpoint fields, persistence is hardware-lifetime persistence rather than filesystem or kernel-object persistence.

## Dependencies And Integration Points

This chunk depends on generated register naming consistency across:

- `dcn_3_5_1_offset.h` for register indices/offsets.
- DCN 3.5.1 resource files for selecting the right register block for each audio instance.
- `display/dc/dce/dce_audio.c` for common Azalia endpoint configuration.
- `display/dc/dce/dce_audio.h` for the audio register/shift/mask table structures and common audio register-list macros.
- DRM audio component integration in `display/amdgpu_dm/amdgpu_dm.c`, which binds GPU display audio state to the kernel audio component and updates ELD/audio instance notifications.

The endpoint numbering is significant: these macros cover high endpoint instances 4-7, matching GPUs that expose multiple display audio pins. Endpoint table size and resource-pool `audio_count` must stay aligned with the generated register namespace.

## Risks

- Generated mask drift can silently corrupt HDA endpoint programming. For example, an incorrect `SUPPORTS_AI` mask would make sink audio info capability reporting wrong without a compile error.
- Endpoint copy/paste symmetry hides errors. Endpoints 4-7 intentionally share identical field layouts; one endpoint with a mismatched shift or mask would only fail on that audio instance.
- The final `#endif` means this chunk closes the entire generated header. Accidental edits around this range can break every DCN 3.5.1 consumer at compile time.
- These constants are hardware-contract data. Driver tests can catch compilation and some behavioral regressions, but incorrect values may only appear on affected ASICs, connectors, audio sinks, or power-management states.
- Clock-gating reporting fields are power/diagnostic sensitive. Wrong `FGCG_REP_DIS` semantics can interfere with clock-gating debug/telemetry and may mask power-management issues.

## Test Signals

Useful validation signals include:

- Kernel build coverage for AMDGPU DC with DCN 3.5.1 enabled; missing or renamed macros should fail compile in resource/register initialization code.
- Display audio enumeration across endpoints 4-7, especially systems with enough connectors/audio pins to exercise high endpoint instances.
- HDMI/DP audio playback after hotplug and mode set, with ELD visible to the audio component and `audio_inst` updates delivered through `amdgpu_dm_audio_eld_notify()`.
- Sink capability behavior for Audio Info support, since `dce_aud_az_configure()` writes `SUPPORTS_AI` into `AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`.
- Suspend/resume and runtime power-management tests that verify audio returns and clock-gating state does not regress.
- Register-dump comparison against the ASIC register specification for endpoint ACP data and `ENDPOINT_FGCG_REP_DIS` bit placement.
