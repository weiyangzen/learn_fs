# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002056`: lines 1-2227, `Docs/researches/chunks/subset-b-002056_research.md`
- `subset-b-002057`: lines 2228-4428, `Docs/researches/chunks/subset-b-002057_research.md`
- `subset-b-002058`: lines 4429-6597, `Docs/researches/chunks/subset-b-002058_research.md`
- `subset-b-002059`: lines 6598-8815, `Docs/researches/chunks/subset-b-002059_research.md`
- `subset-b-002060`: lines 8816-11033, `Docs/researches/chunks/subset-b-002060_research.md`
- `subset-b-002061`: lines 11034-13252, `Docs/researches/chunks/subset-b-002061_research.md`
- `subset-b-002062`: lines 13253-15470, `Docs/researches/chunks/subset-b-002062_research.md`
- `subset-b-002063`: lines 15471-17691, `Docs/researches/chunks/subset-b-002063_research.md`
- `subset-b-002064`: lines 17692-19909, `Docs/researches/chunks/subset-b-002064_research.md`
- `subset-b-002065`: lines 19910-22126, `Docs/researches/chunks/subset-b-002065_research.md`
- `subset-b-002066`: lines 22127-24344, `Docs/researches/chunks/subset-b-002066_research.md`
- `subset-b-002067`: lines 24345-26561, `Docs/researches/chunks/subset-b-002067_research.md`
- `subset-b-002068`: lines 26562-28781, `Docs/researches/chunks/subset-b-002068_research.md`
- `subset-b-002069`: lines 28782-30999, `Docs/researches/chunks/subset-b-002069_research.md`
- `subset-b-002070`: lines 31000-33217, `Docs/researches/chunks/subset-b-002070_research.md`
- `subset-b-002071`: lines 33218-35435, `Docs/researches/chunks/subset-b-002071_research.md`
- `subset-b-002072`: lines 35436-37655, `Docs/researches/chunks/subset-b-002072_research.md`
- `subset-b-002073`: lines 37656-39874, `Docs/researches/chunks/subset-b-002073_research.md`
- `subset-b-002074`: lines 39875-42091, `Docs/researches/chunks/subset-b-002074_research.md`
- `subset-b-002075`: lines 42092-44308, `Docs/researches/chunks/subset-b-002075_research.md`
- `subset-b-002076`: lines 44309-46526, `Docs/researches/chunks/subset-b-002076_research.md`
- `subset-b-002077`: lines 46527-48843, `Docs/researches/chunks/subset-b-002077_research.md`
- `subset-b-002078`: lines 48844-51064, `Docs/researches/chunks/subset-b-002078_research.md`
- `subset-b-002079`: lines 51065-53412, `Docs/researches/chunks/subset-b-002079_research.md`
- `subset-b-002080`: lines 53413-53485, `Docs/researches/chunks/subset-b-002080_research.md`

## Chunk Research

### subset-b-002056: lines 1-2227

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

### subset-b-002057: lines 2228-4428

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 2228-4428

## Scope And Purpose

This chunk is a generated-style AMD DCN 3.5 register shift/mask header segment for Azalia/HD Audio codec endpoint registers. It contains only preprocessor constants: no C functions, structs, runtime branches, or storage definitions. The constants encode bit positions (`__SHIFT`) and bit masks (`_MASK`) used by AMD display/audio register helper macros to read, compose, and update fields in DCN 3.5 audio endpoint registers.

The line range covers 2,201 `#define` entries. It starts mid-register in output endpoint 3 at `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_2__IEC_60958_CS_SAMPLING_FREQUENCY_OVRRD_EN_MASK`, then covers the tail of endpoint 3, all output endpoints 4 through 7, all visible input endpoint 0 fields, and stops partway through input endpoint 1 audio-widget-capability shift definitions. The paired offset header `dcn_3_5_0_offset.h` provides the corresponding register addresses; this file provides the bit layout.

## Register Families Covered

The chunk is organized by endpoint prefix:

- `AZF0ENDPOINT3` lines 2228-2304: tail of output endpoint 3 channel-status overrides, pin control, LPIB snapshot, coding type, format-change, remote keepalive, and audio enable/disable/format-change interrupt status masks.
- `AZF0ENDPOINT4` lines 2305-2774: complete output endpoint 4 converter, pin, channel-status override, and audio status field definitions.
- `AZF0ENDPOINT5` lines 2775-3244: same complete output endpoint layout as endpoint 4.
- `AZF0ENDPOINT6` lines 3245-3714: same complete output endpoint layout as endpoint 4.
- `AZF0ENDPOINT7` lines 3715-4184: same complete output endpoint layout as endpoint 4.
- `AZF0INPUTENDPOINT0` lines 4185-4416: input converter and input pin-control field definitions.
- `AZF0INPUTENDPOINT1` lines 4417-4428: beginning of input converter audio-widget-capability shifts only; masks and later input endpoint 1 fields continue outside this chunk.

For endpoints 4-7, the repeated output endpoint shape includes converter capabilities (`AUDIO_WIDGET_CAPABILITIES`, supported stream formats, supported size/rates), converter controls (`CONVERTER_FORMAT`, `CHANNEL_STREAM_ID`, `DIGITAL_CONVERTER`, `RAMP_RATE`, `GTC_EMBEDDING`), GTC counter delta registers, pin parameters/capabilities, hot-plug/audio enable controls, multichannel assignment controls, HBR/lipsync responses, sink-info registers, IEC 60958 channel-status override registers, LPIB snapshot/status registers, and per-endpoint interrupt status registers.

Input endpoint 0 mirrors part of that model for capture/input use: input converter capabilities and format controls, digital-converter fields, input pin capabilities, unsolicited response controls, input pin sense, input widget enable, multichannel input mapping, HBR response, channel allocation, hot-plug/audio-enabled state, configuration default, LPIB snapshot, input activity/status, and input infoframe fields.

## Important APIs, Types, And Macros

There are no exported functions or C types in this chunk. The meaningful API is the naming contract consumed by AMD register helper macros:

- `REGISTER__FIELD__SHIFT` constants give the low bit of a hardware field.
- `REGISTER__FIELD_MASK` constants give the raw field mask in the register word.
- Register prefixes such as `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` identify endpoint-specific hardware registers or indirect Azalia codec nodes.
- Field suffixes such as `AUDIO_ENABLED`, `CLOCK_GATING_DISABLE`, `HBR_CAPABLE`, `SINK_DESCRIPTION_LEN`, `SUPPORTED_FREQUENCIES`, `NUMBER_OF_CHANNELS`, and `STREAM_ID` are used by helper macros to manipulate values without hard-coding bit positions in driver logic.

The constants are intended to line up with the display driver helper pattern visible in AMD display audio code. `dce_audio.c` selects an indirect Azalia endpoint register through `AZALIA_F0_CODEC_ENDPOINT_INDEX`, reads or writes data through `AZALIA_F0_CODEC_ENDPOINT_DATA`, and uses `set_reg_field_value` with a register name and field name. The helper expansion depends on the `__SHIFT` and `_MASK` symbols being present and correctly named.

## Control Flow

This header segment has no execution control flow. The effective control flow appears in consumers:

1. DCN 3.5 resource, IRQ, or DMUB code includes `dcn_3_5_0_offset.h` and this `dcn_3_5_0_sh_mask.h`.
2. Register tables and helper macros bind a logical register/field name to its offset, base index, shift, and mask.
3. Audio code chooses an endpoint register index, reads the current register value, mutates fields using the shift/mask pair, and writes the new value back.
4. Hardware observes the resulting endpoint register fields to expose or control HDMI/DP audio behavior.

Examples of runtime paths that depend on these symbols include enabling/disabling Azalia audio through `HOT_PLUG_CONTROL.AUDIO_ENABLED`, exposing HBR capability through `RESPONSE_HBR.HBR_CAPABLE`, programming speaker/channel allocation, writing sink-info display-name bytes, programming audio descriptor fields, and updating endpoint format-change or audio-enable interrupt state.

## State And Persistence Behavior

The header itself has no mutable state and no persistence. Its constants describe persistent hardware register state in the GPU display/audio block:

- Endpoint converter controls persist in hardware registers until reprogrammed or reset, including format, channel/stream IDs, digital converter control bits, GTC embedding, and ramp-rate state.
- Pin-control fields describe or control connector-facing state such as hot-plug audio enabled, HBR capability, speaker/channel allocation, sink identity, input activity, and unsolicited response payloads.
- LPIB and timer snapshot fields expose stream position or timing snapshots and wrap counts.
- Interrupt status fields carry event state for audio enabled, disabled, and format changed conditions.

Because these are hardware bit definitions, persistence is ultimately governed by the DCN hardware register file and the driver lifecycle. Suspend/resume, hot-plug, stream reconfiguration, and audio endpoint reinitialization are the scenarios that must preserve or rebuild correct state using these constants.

## Dependencies And Integration Points

The direct dependencies are compile-time:

- `dcn_3_5_0_offset.h` supplies the matching DCN 3.5 Azalia register offsets and base indexes.
- AMD display register helpers such as `REG_SET`, `REG_READ`, `REG_WRITE`, `set_reg_field_value`, and generated shift/mask structs expect the macro names in this header.
- `dcn35_resource.c`, `irq_service_dcn35.c`, and `dmub_dcn35.c` include this header directly for DCN 3.5 display, interrupt, and DMUB integration.
- Common DCE/DC audio code uses the Azalia endpoint names through indirect endpoint-index/data accesses and field helper macros.

The broader integration surface is the Linux DRM AMDGPU display stack. These constants connect C driver code to ASIC-specific DCN 3.5 register layouts for HDMI/DisplayPort audio, codec endpoint discovery, channel mapping, stream format advertisement, sink information, audio hot-plug behavior, and interrupt handling.

## Risks And Edge Cases

- Generated header drift is high impact. A wrong bit shift or mask can silently program the wrong hardware field while the C code still compiles.
- The range starts and ends mid-logical block. Endpoint 3 has earlier channel-status definitions outside this chunk, and input endpoint 1 is incomplete here. Whole-file consumers need adjacent chunks for complete endpoint analysis.
- Endpoints 4-7 are structurally repetitive. Copy-generation mistakes may affect only one endpoint while visual review assumes all repeated blocks are identical.
- Some field names include `MASK` as part of the hardware field name, for example `AUDIO_ENABLED_MASK_MASK`. This is intentional naming but easy to mishandle in scripts that strip suffixes naively.
- Many fields describe externally visible audio capabilities: supported sample rates, bit depths, channel counts, HBR support, sink info, and channel allocation. Bad definitions can cause user-visible audio mode loss, channel misrouting, incorrect EDID/audio exposure, or format-change storms.
- Several state bits are event or interrupt related (`AUDIO_ENABLED_FLAG`, `AUDIO_DISABLED_FLAG`, `AUDIO_FORMAT_CHANGED_FLAG`, unsolicited responses). Mis-masks here can cause missed or spurious audio events.
- Indirect Azalia register access requires correct endpoint selection. These endpoint-specific prefixes must stay aligned with offset/index definitions and any generated register tables.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/audio behavior checks:

- Kernel or module compilation with DCN 3.5 enabled catches missing, renamed, or syntactically malformed macros referenced by register tables and helpers.
- Static generation checks should verify that every visible field has a consistent `__SHIFT`/`_MASK` pair, except known chunk-boundary partials such as the first endpoint 3 mask and final input endpoint 1 shifts.
- Register-header consistency checks should compare this file against `dcn_3_5_0_offset.h` and the source register database used to generate both headers.
- Runtime display audio tests should cover HDMI and DisplayPort audio enable/disable, hot-plug, HBR exposure, multichannel speaker allocation, audio descriptor programming, sink-info propagation, and format changes on DCN 3.5 hardware.
- Interrupt tests should confirm audio-enabled, audio-disabled, and format-changed events are reported and masked as expected for endpoints 4-7.
- Capture/input endpoint validation, where supported by hardware, should exercise input activity, infoframe, pin-sense, multichannel input mapping, and LPIB snapshot fields for `AZF0INPUTENDPOINT0`.

### subset-b-002058: lines 4429-6597

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 4429-6597

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.5.0 register shift/mask header. It contains C preprocessor constants for hardware register bitfields, not executable driver logic. Each macro names a register field and supplies either the bit shift (`__SHIFT`) or the positioned mask (`_MASK`) used by AMD display register helpers when packing and unpacking memory-mapped display hardware registers.

The requested range contains 2,169 `#define` lines: 1,083 shift macros and 1,086 mask macros. There are no local comments in this slice. The imbalance comes from the line boundary starting after some preceding AZALIA input endpoint 1 field shifts and ending before the complete `OTG1_PIXEL_RATE_CNTL` field set.

The chunk covers two broad hardware surfaces:

- HDMI/DisplayPort audio codec endpoint register fields for `AZF0INPUTENDPOINT1` through `AZF0INPUTENDPOINT7`, plus audio descriptor and endpoint immediate-command fields.
- DCN display clock generator fields for pixel clock resync, DTOs, stream clocks, DCCG gating, perf monitors, time bases, DISPCLK ramping, and OTG pixel-rate controls.

## Important Constants And Register Areas

The first large section describes `AZF0INPUTENDPOINT1` through `AZF0INPUTENDPOINT7`. These are generated bitfield layouts for the function-0 AZALIA/HDA input endpoint codec widgets used by display audio. Each endpoint repeats nearly the same register groups:

- Converter widget capability fields, including channel capability, amplifier presence, format override, processing widget, unsolicited response capability, digital/power/LR-swap flags, delay, and widget type.
- Converter format and stream routing fields, including channel count, bits per sample, base-rate divisor/multiple, base rate, stream type, channel ID, and stream ID.
- Digital converter control bits such as `DIGEN`, validity/config/preemphasis/copyright/non-audio/professional flags, category code, and keepalive.
- Supported stream formats, size/rate capabilities, and pin audio widget capabilities.
- Pin capabilities for impedance sense, trigger requirement, jack detect, headphone/output/input support, balanced I/O, HDMI, VREF, EAPD, and DP.
- Pin control/status fields for unsolicited responses, pin sense, widget input enable, multichannel channel enable/mute/channel IDs, HBR support, channel allocation, hot-plug/audio-enabled state, forced unsolicited response payloads, default configuration response, LPIB snapshots, input activity/status, and infoframe channel metadata.

`AZF0INPUTENDPOINT1` starts at line 4429 after the first two shifts of its converter widget capability register were defined in the prior chunk. Endpoints 2 through 7 are complete in this range for the repeated input converter and input pin field groups.

`AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` define compact audio descriptor fields: `MAX_CHANNELS`, `SUPPORTED_RATES`, `DESCRIPTOR_BYTE_2`, and `SUPPORTED_FORMATS` with matching masks. These are the hardware layout used to expose or consume per-format sink audio capabilities.

`AZENDPOINT0_AZENDPOINT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_DATA`, `AZENDPOINT0_AZENDPOINT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_INDEX`, `AZINPUTENDPOINT0_AZENDPOINT_IMMEDIATE_COMMAND_INPUT_INTERFACE_DATA`, and `AZINPUTENDPOINT0_AZENDPOINT_IMMEDIATE_COMMAND_INPUT_INTERFACE_INDEX` define full-width immediate command data and 16-bit index fields for indirect endpoint command paths.

The DCCG section begins at `PHYPLLA_PIXCLK_RESYNC_CNTL` and continues through the beginning of `OTG1_PIXEL_RATE_CNTL`. Important register families include:

- `PHYPLL[A-E]_PIXCLK_RESYNC_CNTL` for PHY PLL pixel-clock resync enable and delay per PHY.
- `DP_DTO_DBUF_EN`, `DPSTREAMCLK_CNTL`, `DTBCLK_P_CNTL`, `DSCCLK[0-3]_DTO_PARAM`, `DCCG_DS_*`, and `DCCG_GTC_*` for display DTO enablement, stream-clock selection, DSC clock DTO phase/modulo, deep-sleep DTOs, and global time counter DTO/current fields.
- `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DCCG_GATE_DISABLE_CNTL4`, and `DCCG_GATE_DISABLE_CNTL5` for display, SOC, DPREF, DPP, DSC, PHY symbol, HDMI character, DTB, DP stream, HPO, and other clock-gate disable bits.
- `DCCG_PERFMON_CNTL` and `DCCG_PERFMON_CNTL2` for selecting and running display clock/perf monitor counters.
- `DISPCLK_FREQ_CHANGE_CNTL` for DISPCLK ramp step delay/size, ramp completion, FIFO error-detection control/state, and forward-correction disable.
- `MICROSECOND_TIME_BASE_DIV` and `MILLISECOND_TIME_BASE_DIV` for time-base dividers and clock source selectors.
- `OTG_PIXEL_RATE_DIV`, `OTG0_PIXEL_RATE_CNTL`, `DP_DTO0_PHASE`, `DP_DTO0_MODULO`, `OTG0_PHYPLL_PIXEL_RATE_CNTL`, and the start of `OTG1_PIXEL_RATE_CNTL` for output timing generator pixel-rate source, DTO enable/status, add/drop pixel correction, pipe DTO source selection, FIFO error reporting, and DP DTO phase/modulo.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. The public surface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives a field bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

These macros are consumed by generated register-list initializers and AMD display register helpers. For DCN 3.5, `drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c` includes this header and builds static `dccg_shift`, `dccg_mask`, `audio_shift`, and `audio_mask` tables from the generated macro names. `drivers/gpu/drm/amd/display/dc/dccg/dcn35/dcn35_dccg.h` defines `DCCG_MASK_SH_LIST_DCN35()`, which maps many fields in this chunk into `struct dccg_shift` and `struct dccg_mask` through `DCCG_SF` and `DCCG_SFII`.

The audio side is indirectly integrated through `drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` and `dce_audio.c`. The runtime helpers write an AZALIA endpoint index and data register with `REG_SET()` and `REG_READ()`. This chunk does not provide the high-level audio programming routines, but its endpoint and descriptor field definitions are the low-level bit layout those routines depend on when an indirect endpoint command or descriptor value is constructed.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs in display driver code that reads or writes the hardware registers described by these bitfields.

The implied audio flow is HDA/AZALIA endpoint programming and readback. Driver code selects an endpoint register through endpoint index/data registers or immediate-command paths, then programs converter format, channel/stream routing, digital converter state, pin capabilities/status, channel allocation, HBR support, LPIB snapshot controls, and infoframe-related status. Hotplug or audio stream changes can cause the higher-level display stack to revisit these fields for audio enablement, supported mode reporting, unsolicited responses, or DP/HDMI audio metadata.

The implied DCCG flow is clock programming and status observation. DCCG code enables or disables DTOs, chooses stream-clock and DTB clock sources, sets phase/modulo values, controls root and leaf clock gating, observes enable status bits, handles DISPCLK ramp/error state, and selects pixel-rate sources for OTGs. The line range contains the register fields that let DCN 3.5 DCCG functions such as clock-gating control, DSC clock control, DP stream clock setup, and pixel DTO setup address the correct bits.

Several fields are sequencing-sensitive. DTO enable bits should be coordinated with phase/modulo programming and status readback. Clock-gate disable bits should be coordinated with active display pipes and PHY/stream ownership. Pixel-rate source and add/drop pixel controls affect live timing generator behavior and therefore must be changed only through established modeset or clock-update paths.

## State And Persistence

The file itself stores no mutable state. It defines how software addresses state stored in DCN 3.5 display hardware registers.

Persistent hardware state represented here includes audio converter format and routing, pin/widget capability and control fields, hotplug/audio-enabled state, audio infoframe/channel allocation state, LPIB snapshot/readback values, audio descriptors, clock source selections, DTO phase/modulo values, clock-gate disables, time-base divisors, perf-monitor configuration, DISPCLK ramp/error controls, and OTG pixel-rate settings. These values may survive across frames and remain active until reset, modeset, suspend/resume restore, hotplug handling, or explicit clock/audio reprogramming changes them.

Readback/status fields in the range include pin presence/input activity, LPIB snapshots, DTO enable status, DCCG perf/run state, FIFO error state/counts, GTC current value, CAC status, and DISPCLK ramp completion/error-detection state. The macros do not encode read-only versus writable semantics; callers must know that from the hardware programming model and use the established helper layer.

## Dependencies And Integration Points

This generated shift/mask header depends on the matching DCN 3.5.0 register-address header, especially `dcn_3_5_0_d.h`, and on the AMD display register helper framework that combines register offsets, shifts, and masks. Numeric values in this chunk are ASIC-generation-specific and should not be mixed with another DCN generation unless a generated register database confirms the layout is identical.

Important integration points include:

- `dcn35_resource.c`, which includes `dcn_3_5_0_sh_mask.h` and instantiates DCCG and audio shift/mask tables.
- `dcn35_dccg.h` and the DCN35 DCCG implementation, where fields such as `DCCG_GATE_DISABLE_CNTL2`, `DCCG_GATE_DISABLE_CNTL5`, `DPSTREAMCLK_CNTL`, `DTBCLK_P_CNTL`, `DSCCLK*_DTO_PARAM`, `OTG*_PIXEL_RATE_CNTL`, `OTG_PIXEL_RATE_DIV`, and `DISPCLK_FREQ_CHANGE_CNTL` are surfaced to `REG_SET`, `REG_UPDATE`, and `REG_READ` helper calls.
- `dce_audio.h` and `dce_audio.c`, where AZALIA endpoint index/data helpers and audio DTO fields bridge display audio policy to hardware registers.
- DC resource construction for DCN 3.5 and DCN 3.6, which reuses `DCCG_REG_LIST_DCN35()` and `DCCG_MASK_SH_LIST_DCN35()` patterns for matching hardware blocks.
- Display modeset, link encoder, DSC, DP/HDMI stream, HPO, power-management, and hotplug paths that depend on correct DCCG and audio register programming.

The register field names are part of the integration contract. A typo, removed field, or layout drift usually breaks compilation only when a consumer references that exact token; a wrong numeric mask or shift may compile cleanly and fail only on hardware.

## Risks And Edge Cases

Generated-header drift is the primary risk. Incorrect shifts or masks can write the wrong audio or clock bits without type-system help. Audio symptoms could include missing channels, wrong sample format reporting, HBR failure, broken hotplug notification, or invalid infoframes. Clock symptoms could include blank displays, unstable links, incorrect pixel rate, FIFO errors, DSC stream failures, or bad suspend/resume restore.

The line boundaries are incomplete. The start omits the first two `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` shifts, and the end cuts off `OTG1_PIXEL_RATE_CNTL` after `OTG1_DIO_ERROR_COUNT__SHIFT`. Whole-file reconciliation must merge adjacent chunks before making complete claims for those two register groups.

Repeated endpoint and clock-instance layouts are easy to mishandle. Endpoints 2 through 7 and many clock fields follow regular patterns, but instance-specific naming still matters. A single instance mismatch can affect only one audio endpoint, PHY, stream, DSC engine, or OTG, so validation must exercise more than the first pipe.

Clock gating fields are side-effect-prone. A value named `*_GATE_DISABLE` often uses inverted semantics where `1` disables gating rather than disables the clock itself. Higher-level code should continue using the DCCG helper functions and initialized mask tables rather than open-coding register writes.

Full-width masks and `L` suffixes require normal register-width discipline. Fields such as DTO phase/modulo and LPIB snapshots use `0xFFFFFFFFL`; consumers should use unsigned 32-bit register values and the central field helpers to avoid sign-extension or shift mistakes.

## Test And Validation Signals

Build validation should include DCN 3.5 display objects that include `dcn_3_5_0_sh_mask.h`, especially `dcn35_resource.c`, `dmub_dcn35.c`, and DCCG/audio consumers. Missing or renamed macros generally surface at compile time through the generated shift/mask table initializers.

Useful generated-data checks include:

- Compare this range against the authoritative DCN 3.5 register database.
- Verify each complete register group has matching shift and mask definitions and that masks do not overlap unexpectedly.
- Diff repeated AZF0 input endpoint instances 2 through 7 for structural consistency while accounting for the incomplete endpoint 1 boundary.
- Diff DCCG fields against the `DCCG_MASK_SH_LIST_DCN35()` consumer list so every referenced field has the expected shift and mask in the DCN 3.5 header.
- Include the next chunk when validating `OTG1_PIXEL_RATE_CNTL`, because this range stops before its mask lines.

Runtime validation signals include successful HDMI/DP audio enumeration and playback across multiple connectors, correct channel allocation and HBR behavior, stable hotplug/unplug audio transitions, successful modesets at varied pixel rates, no DCCG/OTG FIFO error accumulation, stable DSC/HPO/DP stream clocks, correct suspend/resume restore of audio and display clocks, and clean multi-monitor operation where more than one endpoint, PHY, stream clock, and OTG instance is active.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002058_research.md`. Whole-file research for `dcn_3_5_0_sh_mask.h` must merge neighboring chunks to complete the opening AZALIA endpoint 1 capability register and the trailing `OTG1_PIXEL_RATE_CNTL` register group.

### subset-b-002059: lines 6598-8815

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h - subset-b-002059

## Scope

- Chunk id: `subset-b-002059`
- Source lines: 6598-8815
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h`
- Observed content: 2,218 lines, all `#define` entries, with 1,117 `__SHIFT` macros and 1,118 `_MASK` macros.

This chunk is part of the generated AMD DCN 3.5.0 register shift/mask header. It does not define executable C logic. Instead, it publishes bit positions and masks for display clock generation, audio codec control, display performance monitoring, display power gating, DMU/DMCUB-facing clock control, and display interrupt status registers. Runtime DCN code pairs these field constants with matching address macros from `dcn_3_5_0_offset.h` through AMD display register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, and `REG_WAIT`.

## Purpose

The purpose of this slice is to describe hardware register fields for several DCN 3.5 display subsystems:

- DCCG pixel clock and DTO programming for OTG instances, DP DTOs, DPPCLK DTOs, DTBCLK DTOs, DSCCLK DTOs, HDMI stream/character clocks, SYMCLK enables, DCCG soft reset, clock-gating delay controls, audio DTO source selection, and vsync counter controls.
- Azalia/HD-audio codec function, converter, pin, and input-pin controls for HDMI/DP audio capabilities, stream format, channel allocation, channel status, HBR, multichannel enable/mute/channel id, LPIB snapshots, unsolicited responses, configuration defaults, audio descriptors, sink info, and audio format-change status.
- DC performance monitor blocks `DC_PERFMON0`, `DC_PERFMON1`, and `DC_PERFMON2`, including counter control, count mode/window selection, counter state, interrupt mode, current values, and high/low latched values.
- Display power and management fields, including `CC_DC_PIPE_DIS`, `DOMAIN{0,1,2,3,16,17,18,19}_PG_CONFIG`, matching `DOMAIN*_PG_STATUS`, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_1`, `DC_IP_REQUEST_CNTL`, `SMU_INTERRUPT_CONTROL`, `DMU_CLK_CNTL`, and `DMU_MISC_ALLOW_DS_FORCE`.
- Z-state/ZSC fields (`ZSC_CNTL`, `ZSC_CNTL2`, `ZSC_STATUS`) for display idle/power-state coordination.
- Display interrupt status continuation registers from the base `DISP_INTERRUPT_STATUS` chain through the beginning of `DISP_INTERRUPT_STATUS_CONTINUE19`, covering OTG, HUBP, DWB, DMCUB, DMCUB outbox, DCHUBBUB, DSC, DIO/DCIO, DCPG, OPP, OPTC, MMHUBBUB, Azalia, and DIGG interrupt sources.

Driver code should not hard-code the numeric values in this header. These generated names form the field-layout contract between the ASIC register database and the display driver.

## Important APIs, Types, and Macros

There are no functions, structs, enums, or mutable declarations in this chunk. Its public interface is a generated macro namespace with names of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.

Important macro families include:

- Pixel and link clocks: `OTG1_PIXEL_RATE_CNTL` tail masks, complete `OTG2_PIXEL_RATE_CNTL` and `OTG3_PIXEL_RATE_CNTL`, `DP_DTO{1,2,3}_PHASE`, `DP_DTO{1,2,3}_MODULO`, `OTG{1,2,3}_PHYPLL_PIXEL_RATE_CNTL`, `DENTIST_DISPCLK_CNTL`, `DPPCLK_DTO_CTRL`, `DPPCLK{0..3}_DTO_PARAM`, `DTBCLK_DTO{0..3}_{PHASE,MODULO}`, `DTBCLK_DTO_DBUF_EN`, `DSCCLK_DTO_CTRL`, `HDMISTREAMCLK_CNTL`, `HDMISTREAMCLK0_DTO_PARAM`, and `HDMICHARCLK0_CLOCK_CNTL`.
- DCCG reset, gating, and timing: `DPPCLK_CGTT_BLK_CTRL_REG`, `DCCG_CAC_STATUS2`, `SYMCLK{A..E}_CLOCK_ENABLE`, `DCCG_SOFT_RESET`, `DCCG_GATE_DISABLE_CNTL3`, `FORCE_SYMCLK_DISABLE`, `DCCG_VSYNC_CNT_CTRL`, `DCCG_VSYNC_CNT_INT_CTRL`, and `DCCG_VSYNC_OTG{0..5}_LATCH_VALUE`.
- Audio DTO routing: `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO{0,1}_{PHASE,MODULE}`, and `DCCG_AUDIO_DTBCLK_DTO_{PHASE,MODULO}`. The source register includes DTO source selection and 512-FBR DTO selection fields for DTO0/1/2 and audio DTBCLK.
- Azalia codec function and converter fields: `AZALIA_F2_CODEC_ROOT_PARAMETER_*`, `AZALIA_F2_CODEC_FUNCTION_PARAMETER_*`, `AZALIA_F2_CODEC_FUNCTION_CONTROL_*`, `AZALIA_F2_CODEC_CONVERTER_PARAMETER_*`, `AZALIA_F2_CODEC_CONVERTER_CONTROL_*`, `AZALIA_F2_CODEC_CONVERTER_STRIPE_CONTROL`, and `AZALIA_F2_CODEC_CONVERTER_CONTROL_GTC_EMBEDDING`.
- Azalia pin/output audio fields: `AZALIA_F2_CODEC_PIN_PARAMETER_*`, `AZALIA_F2_CODEC_PIN_CONTROL_RESPONSE_*`, `AZALIA_F2_CODEC_PIN_CONTROL_WIDGET_CONTROL`, `CHANNEL_ALLOCATION`, `AUDIO_DESCRIPTOR`, `AUDIO_DESCRIPTOR_DATA`, `HBR`, `MULTICHANNEL*`, `LIPSYNC`, `AUDIO_SINK_INFO_*`, `DIGITAL_OUTPUT_STATUS`, `LPIB*`, `CODING_TYPE`, `FORMAT_CHANGED`, `WIRELESS_DISPLAY_IDENTIFICATION`, `REMOTE_KEEPALIVE`, `DOWN_MIX_INFO`, and pin association fields.
- Azalia input-pin/input-converter fields: `AZALIA_F2_CODEC_INPUT_PIN_PARAMETER_*`, `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_*`, `AZALIA_F2_CODEC_INPUT_CONVERTER_PARAMETER_*`, and `AZALIA_F2_CODEC_INPUT_CONVERTER_CONTROL_*`, covering input widget capabilities, multichannel controls, LPIB snapshots, stream format, and channel stream id.
- Display power and DMU fields: `CC_DC_PIPE_DIS`, `DOMAIN*_PG_CONFIG`, `DOMAIN*_PG_STATUS`, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_1`, `DC_IP_REQUEST_CNTL`, `SMU_INTERRUPT_CONTROL`, `DMU_CLK_CNTL`, and `DMU_MISC_ALLOW_DS_FORCE`.
- Performance monitor fields: `DC_PERFMON{0,1,2}_PERFMON_CNTL`, `*_PERFMON_CNTL2`, `*_PERFMON_LOW`, `*_PERFMON_HI`, `*_PERFMON_CVALUE_LOW`, `*_PERFMON_CVALUE_INT_MISC`, `*_PERFCOUNTER_CNTL`, `*_PERFCOUNTER_CNTL2`, and `*_PERFCOUNTER_STATE`.
- Interrupt status chain: `DISP_INTERRUPT_STATUS`, `DISP_INTERRUPT_STATUS_CONTINUE`, and `DISP_INTERRUPT_STATUS_CONTINUE2` through `DISP_INTERRUPT_STATUS_CONTINUE19`. The fields cover vertical blank/line/update/trigger events, HPD and HPD RX events, AUX/DDC/I2C/DIO events, DWB and DMCUB events, DCHUBBUB/DSC events, HUBP perfmon/IHC events, flip/flip-away events, DCIO DPCS errors, DCPG domain power-down events, Azalia endpoint audio events, and the first DIGG DP events in continue19.

## Control Flow

This header chunk has no local control flow. Runtime behavior comes from code that consumes these constants:

1. DCN 3.5 resource and block files include `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Resource initialization builds per-block register, shift, and mask tables. Observed consumers include `display/dc/resource/dcn35/dcn35_resource.c`, `display/dc/irq/dcn35/irq_service_dcn35.c`, and `display/dmub/src/dmub_dcn35.c`.
3. Block helpers pass those tables into DCCG, clock manager, audio, interrupt, DMUB, power-gating, and hardware-sequencer code.
4. The driver performs read-modify-write, poll, clear, and ack operations through the register helpers. The helper resolves a register address from the offset header and field positions/masks from this header.
5. Hardware then performs the actual state transition: selecting an OTG pixel-rate source, enabling a DTO, changing a DENTIST divider, routing audio DTOs, enabling/disabling a clock gate, servicing a power-domain request, reading a perf counter, acknowledging a status bit, or exposing an interrupt in the chained display status registers.

Common hardware flow idioms in this chunk include enable/status pairs (`DPDTO*_ENABLE_STATUS`, `DTBCLKDTO*_ENABLE_STATUS`), phase/modulo DTO programming, DENTIST write-divider plus change-done polling, soft-reset bits, power-gate request/status pairs, interrupt status/continue chains, perfmon start/stop/count-state fields, Azalia unsolicited-response and format-change response fields, and action-style interrupt clear or mask fields in DCPG interrupt control.

## State and Persistence Behavior

The macros themselves are compile-time constants and retain no state. They describe MMIO fields whose values are stored in DCN hardware registers.

Persistent or semi-persistent configuration state includes DTO phase/modulo values, OTG pixel-rate sources, PHYPLL pixel-rate source selection, DPPCLK/DSCCLK/DTBCLK enable and double-buffer controls, DCCG audio DTO source selections, SYMCLK source/enable fields, clock-gate disable overrides, DENTIST divider values, Azalia function/pin/converter configuration defaults, stream formats, channel allocation, multichannel enable/mute/channel ids, HBR enable, audio descriptors, power-domain force/gate settings, DMU clock-gate controls, and ZSC control values. These values generally remain programmed until the driver rewrites them or hardware reset clears them.

Transient and latched state includes DTO enable status, DIO FIFO error bits and error counters, DENTIST change-done bits, DCCG CAC status, DCCG vsync latch values, DCPG interrupt status, power-domain FSM status, DC perfmon counter current values and overflow/interrupt status, Azalia format-changed/enable/disable events, LPIB snapshots, ZSC status, and every `DISP_INTERRUPT_STATUS*` bit. Status, ack, clear, and interrupt-control fields must be treated according to their hardware semantics rather than as ordinary retained configuration.

Several fields are sensitive to ordering. DTO phase/modulo and enable bits must be programmed consistently with clock source selection. DENTIST divider changes are normally followed by polling `*_CHG_DONE`. Power-domain control fields are paired with status fields and can hang or power down an active block if used out of sequence. Interrupt status chains use continuation bits, so a reader must traverse the chain rather than treating a single register as complete coverage.

## Dependencies

This generated namespace depends on:

- Matching DCN 3.5.0 register addresses from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`.
- AMD display register-helper conventions, including `SR`, `SRI`, `SF`, `DCCG_SF`, `DCCG_SFI`, `HWS_SF`, `DMUB_SR`, `DMUB_SF`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT`.
- DCN 3.5 resource initialization in `display/dc/resource/dcn35/dcn35_resource.c`, which includes this header and wires its fields into block register tables.
- DCCG and clock-manager code such as `display/dc/dccg/dcn35/dcn35_dccg.[ch]`, `display/dc/dccg/dcn32/dcn32_dccg.[ch]`, and `display/dc/clk_mgr/dcn35/dcn35_clk_mgr.c`, which consume DCCG/DENTIST/DTO fields directly or via inherited macro lists.
- Audio support in `display/dc/dce/dce_audio.[ch]`, which consumes DCCG audio DTO source fields and Azalia endpoint access helpers.
- DMUB support in `display/dmub/src/dmub_dcn35.[ch]`, which consumes `DMU_CLK_CNTL` fields.
- Interrupt service code in `display/dc/irq/dcn35/irq_service_dcn35.c` plus source-id definitions such as `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which map status-register fields to driver interrupt sources.
- Power-gating and hardware sequencing code, including DCN family resource tables and later `pg` controllers, which use `DOMAIN*_PG_*`, `DCPG_INTERRUPT_*`, and `DC_IP_REQUEST_CNTL` style fields.

Correctness is tied to the ASIC register database that generated this file. Manual edits to numeric shifts or masks without a matching hardware definition change would silently corrupt MMIO programming.

## Integration Points

DCCG and clock-manager integration is the most direct. `dcn35_dccg.c` updates `DCCG_GATE_DISABLE_CNTL3` for DP stream and SYMCLK root/leaf gating, reads and writes `DENTIST_DISPCLK_CNTL`, waits for `DENTIST_DISPCLK_CHG_DONE`, and relies on DPPCLK DTO field arrays built from `DPPCLK_DTO_CTRL` and `DPPCLK*_DTO_PARAM`. `dcn35_clk_mgr.c` also carries local DENTIST definitions and uses the same hardware semantics for divider changes.

Audio integration spans both DCCG and Azalia. `dce_audio.[ch]` uses `DCCG_AUDIO_DTO_SOURCE` fields to choose DTO sources and 512-FBR DTO behavior. The Azalia F2 codec field set in this chunk describes the hardware endpoint registers used for audio capabilities, ELD-like sink data, stream format, channel status/allocation, HBR, multichannel layout, LPIB snapshots, and unsolicited/format-change events. Display link and audio enable paths depend on these fields matching the endpoint register model.

Interrupt integration is through `irq_service_dcn35.c` and IRQ source tables. The `DISP_INTERRUPT_STATUS*` continuation chain exposes many event domains: OTG timing events, HPD/HPD RX, AUX/I2C/DDC, DIO/DCIO, DWB, DMCUB, DCHUBBUB, DSC, HUBP, OPP, OPTC, MMHUBBUB, DCPG, Azalia endpoint, and DIGG DP status. The continuation bits (`DISP_INTERRUPT_STATUS_CONTINUE*`) are part of the chain walk and must remain aligned.

DMUB and DMU integration appears in `dmub_dcn35.c`, where `DMU_CLK_CNTL` gate-disable fields are updated for display, SoC, and DMCUB clocks. The `SMU_INTERRUPT_CONTROL`, `DMU_MISC_ALLOW_DS_FORCE`, and `DC_IP_REQUEST_CNTL` fields are part of the broader display/SMU/DMUB coordination surface.

Power-gating integration is shared with hardware sequencing and per-generation PG controllers. `DOMAIN0..3` and `DOMAIN16..19` config/status fields encode force-on, gate request, desired power state, and PGFSM status for display domains. `DCPG_INTERRUPT_STATUS*` and `DCPG_INTERRUPT_CONTROL_1` provide interrupt visibility and masking/clearing for domain power-down and miscellaneous PG events.

Performance monitoring integration is diagnostic and profiling oriented. The three `DC_PERFMON` instances expose counter selection, count modes, windowing, overflow/interrupt behavior, current value reads, and state transitions. These fields are typically exercised by debug/perf tooling rather than the steady-state modeset path.

## Risks and Edge Cases

- This is generated register metadata. A one-bit shift or mask error can program the wrong clock source, route audio to the wrong DTO, misread a power-domain state, lose an interrupt, or corrupt performance counter reads.
- The chunk begins in the middle of `OTG1_PIXEL_RATE_CNTL`; its early shifts and some masks are in the previous chunk. It ends inside `DISP_INTERRUPT_STATUS_CONTINUE19` after `DIGG_DP_FAST_TRAINING_COMPLETE_INTERRUPT__SHIFT`; the remaining continue19 masks and later continue registers are in the next chunk.
- DCCG clock fields are timing-sensitive. Incorrect DTO phase/modulo, double-buffer enable, or DENTIST divider fields can cause display underflow, pixel-rate mismatch, or waits that never observe change-done.
- Several clock-gating fields are override-style controls. Accidentally forcing gates disabled or enabled can increase power, break link clocks, or hide idle-power regressions.
- `DCCG_SOFT_RESET` contains many reset bits for refclk, DVO, audio DTO, DP refclk, AMCLK, and PLL config interfaces. Treating reset fields like ordinary state bits can glitch active clocks or leave blocks in reset.
- Azalia codec fields mix capability, control, status, and response registers with similar names. Confusing response/configuration-default/status fields can advertise wrong audio capabilities or mishandle format-change/unsolicited-response events.
- LPIB and audio timer snapshot fields are latched runtime values. Readers must account for snapshot locking and wrap count rather than assuming an always-current linear counter.
- Power-gate request/status pairs can be racy around suspend/resume, idle entry, and DMCUB-driven sequencing. Polling the wrong `DOMAIN*_PG_STATUS` field or using the wrong expected value can cause timeouts or premature access to a powered-down block.
- The interrupt status continuation chain is easy to truncate. Missing a continuation bit or mapping a field to the wrong source id can lose interrupts or create unhandled interrupt storms.
- DCIO/DPCS, DCPG power-down, DMCUB outbox, HUBP IHC timeout, and Azalia endpoint interrupts are often error or state-transition signals. Incorrect masks can make failures appear as display hangs without a useful interrupt trail.
- Perfmon control and state fields are shared diagnostic resources. Incorrect counter selection or clear/overflow handling can produce misleading performance data.

## Test Signals

Useful validation signals for this chunk include:

- DCN 3.5 display build coverage that compiles `dcn35_resource.c`, `irq_service_dcn35.c`, `dmub_dcn35.c`, `dcn35_dccg.c`, and the DCN 3.5 clock manager against this generated header.
- Generated-header consistency checks that every consumed `SF(..., field, __SHIFT)` has a matching `_MASK`, that masks align with shifts, and that field widths match the register database.
- Modeset tests across multiple pipes and links that exercise OTG pixel-rate selection, DP DTO enable/status, DPPCLK DTO phase/modulo programming, DENTIST divider changes, and clock-gating debug state.
- Audio validation over HDMI and DP with format changes, HBR, multichannel layouts, channel allocation/status, LPIB snapshot reads, endpoint enable/disable events, and audio DTO source changes.
- Hotplug, AUX/DDC/I2C, DIO/DCIO error, Azalia endpoint, DMCUB outbox, DWB, DSC, HUBP, OPP, OPTC, and OTG interrupt tests that confirm the status continuation chain and source-id mappings are correct.
- Suspend/resume and idle-power tests covering `DOMAIN*_PG_CONFIG`, `DOMAIN*_PG_STATUS`, `DCPG_INTERRUPT_*`, `DMU_CLK_CNTL`, `DMU_MISC_ALLOW_DS_FORCE`, `SMU_INTERRUPT_CONTROL`, and ZSC status.
- Perfmon/debug tooling tests that start, stop, clear, and read `DC_PERFMON0..2` counters and verify overflow/interrupt state handling.
- Register-dump comparison against known-good DCN 3.5 hardware after boot, modeset, audio enable, power-gate transitions, and interrupt events.

## Chunk Boundary Notes

Line 6598 starts after the beginning of `OTG1_PIXEL_RATE_CNTL`; the previous chunk contains the missing `OTG1_PIXEL_RATE_CNTL` shifts and first masks. Line 8815 stops inside `DISP_INTERRUPT_STATUS_CONTINUE19`; the next chunk contains the remaining fields and masks for that register and subsequent interrupt status continuation registers. The merge lane should combine adjacent chunk documents before making file-level conclusions about those boundary register blocks.

### subset-b-002060: lines 8816-11033

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 8816-11033

## Purpose

This chunk is generated AMD DCN 3.5 register field metadata. It contains no executable driver logic; it publishes C preprocessor constants for field shifts and bit masks in `dcn_3_5_0_sh_mask.h`. Consumers pair these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with the matching DCN 3.5 register-offset header to build typed register tables used by AMDGPU display, DMUB, IRQ, writeback, memory-hub, and diagnostic code.

The requested range starts at `DISP_INTERRUPT_STATUS_CONTINUE19`, covers the rest of the display interrupt-status continuation chain through `CONTINUE25`, then covers GPU timer start-position fields, per-block interrupt-destination routing fields, DMCUB/RBBMIF security and mailbox fields, MCIF writeback buffer-manager and buffer fields, MMHUBBUB/warmup/power fields, DC perfmon instance 3 and the start of instance 4, and finally the Azalia stream index/data registers plus `AZ_CLOCK_CNTL`.

Although the repository path is under a local `ceph-client` source mirror, this file is AMD display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or callbacks in this range. The exported interface is entirely the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: the bit offset for `FIELD` within `REGISTER`.
- `REGISTER__FIELD_MASK`: the bit mask for the same field.

Major macro families in this chunk:

- `DISP_INTERRUPT_STATUS_CONTINUE19` through `DISP_INTERRUPT_STATUS_CONTINUE25`: status bits for Azalia endpoint audio changes, OTG vupdate/vstartup/vready/no-lock and DRR events, I2C/DDC done/read-request events, DMCUB outbox, AUX/DIG/HPD/display block events, and continuation bits linking the status chain.
- `DC_GPU_TIMER_START_POSITION_*`: compact per-pipe start-position fields for vready, flip, vupdate-no-lock, and flip-away timing on display pipes D1 through D6.
- `*_INTERRUPT_DEST`: interrupt routing/destination fields for DCCG, DMU, DCPG, MMHUBBUB, WB, DCHUB, DPP perf counters, MPC, OPP, OPTC, OTG0-OTG5, DIG, I2C/DDC/HPD, DIO, DCIO, HPD, AZ, AUX, DSC, and HPO blocks.
- `DMCUB_*` and `RBBMIF_*`: DMCUB security, region/window, mailbox, timer, scratch, GPINT, interrupt enable/ack/status/type, memory power, reset/control, and fault-address fields, plus RBBMIF timeout and status fields.
- `MCIF_WB_*`: display writeback buffer-manager control/status, per-buffer address/status/resolution, pitch, arbitration, p-state/watermark, security, VMID, and minimum-time-to-output fields.
- `MMHUBBUB_*`, `WBIF*`, `DMU_IF_ERR_STATUS`, and `MULTI_LEVEL_QOS_CTRL`: memory-hub warmup, low-power, clock-gating, reset, watermark, outstanding-counter, and error-status fields.
- `DC_PERFMON3_*` and partial `DC_PERFMON4_PERFCOUNTER_CNTL`: display perf counter event selection, counted-value selection, increment/run/stop controls, counter state, interrupt status/ack, counter high/low values, and perfmon control fields.
- `AZF0STREAM0` through `AZF0STREAM7` and `AZ_CLOCK_CNTL`: indexed Azalia stream register access/data fields and audio clock-gating/test-clock selection fields.

## Control Flow

This header has no runtime control flow. It is compiled into control flow through register helper macros in AMD display code:

1. DCN 3.5 display modules include `dcn_3_5_0_sh_mask.h` alongside the matching offset header.
2. Register-list macros token-paste register and field names into shift/mask table members. For example, DMUB code uses `DMUB_SF(DMCUB_INTERRUPT_ENABLE, DMCUB_GPINT_IH_INT_EN)`, IRQ code uses `IRQ_REG_ENTRY_DMUB(... DMCUB_INTERRUPT_ENABLE, DMCUB_OUTBOX1_READY_INT_EN, DMCUB_INTERRUPT_ACK, DMCUB_OUTBOX1_READY_INT_ACK)`, and MMHUBBUB/writeback code uses `SF(MCIF_WB_BUFMGR_SW_CONTROL, MCIF_WB_BUF_ADDR_FENCE_EN, mask_sh)`.
3. Runtime paths call helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_SET`, and DMUB register helpers. Those helpers use the generated shift/mask constants to preserve unrelated bits while setting, clearing, reading, or acknowledging fields.
4. Hardware sequencing is supplied by the consuming modules. This chunk only says where a field lives; it does not encode whether a field is read-only, write-one-to-clear, sticky, self-clearing, clock-gated, reset-sensitive, or safe to access while a display block is powered down.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on its own. It describes MMIO-backed GPU display state.

Represented state includes interrupt status/routing state, DMCUB firmware control windows and mailboxes, RBBMIF security/timeout state, writeback buffer ownership and address state, MMHUBBUB warmup and power-management state, display perfmon counters, Azalia stream register index/data windows, and audio clock-gating controls.

Persistence is hardware-defined. Configuration fields generally retain values until modeset, block reset, power gating, suspend/resume, or ASIC reset. Status, interrupt, timeout, fault, counter, and ack fields can be sticky, edge-triggered, read-only, write-one-to-clear, or self-clearing depending on the underlying register. Because these are untyped macros, the consuming driver code must know the correct ordering for enabling interrupts, acknowledging status, programming DMCUB windows, changing MCIF buffers, and reading perf counters.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h` for the corresponding MMIO offsets and base-index selectors.
- AMD display register helper infrastructure that consumes `mask` and `shift` tables, including `REG_*`, `SF`, `SRI`, `SRI2`, `DMUB_SR`, `DMUB_SF`, and `IRQ_REG_ENTRY*` style macros.

Representative integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c` and `dmub_dcn35.h`, which include this header and consume `DMCUB_*` fields for DMUB reset, setup windows, mailboxes, scratch/GPINT state, and interrupt control.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`, which uses DMCUB interrupt enable/ack fields for the DMCUB outbox IRQ path and uses generated interrupt register metadata for display IRQ service tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn32/` and related writeback/memory-hub code, whose shared register lists consume `MCIF_WB_*` and `MMHUBBUB_*` shift/mask definitions for writeback buffer programming, address fences, watermarks, memory power, warmup, and reset.
- Display diagnostics and performance-monitoring paths that program `DC_PERFMON*` fields to select events, run counters, read high/low counter values, and handle counter interrupts.
- Audio/display output paths that rely on `AZ_INTERRUPT_DEST`, `AZF0STREAM*`, and `AZ_CLOCK_CNTL` fields for Azalia stream access, audio endpoint events, and audio clock gating.

## Risks And Edge Cases

- Shift/mask drift is the primary risk. These macros are untyped constants; an incorrect bit position can compile cleanly while silently changing the wrong hardware field.
- Interrupt fields are especially sensitive. Bad `DISP_INTERRUPT_STATUS_CONTINUE*`, `*_INTERRUPT_DEST`, or DMCUB enable/ack masks can cause stuck interrupts, missed hotplug, missed vblank/vupdate, I2C/DDC completion loss, audio endpoint event loss, or interrupt storms.
- Repeated instance blocks are copy-sensitive. OTG0-OTG5, MCIF writeback buffers 1-4, DMCUB region3 cache windows 0-7, Azalia streams 0-7, and perfmon instances use near-identical field layouts; an instance-specific typo may only fail on one pipe, stream, buffer, or diagnostic path.
- DMCUB fields cross a firmware boundary. Incorrect region top/offset/high/enable, mailbox pointer, GPINT, scratch, or fault-address field metadata can break firmware boot, command submission, outbox handling, secure-memory windows, or fault diagnosis.
- MCIF writeback fields carry address, pitch, size, VMID, security, and buffer-state information. Wrong masks can corrupt captured frames, program the wrong buffer, mishandle TMZ/security state, or fence/lock buffers incorrectly.
- Power and clock fields in MMHUBBUB, MCIF, WBIF, DMCUB, and Azalia areas can be ignored or harmful when accessed while a block is gated, reset, or not clocked.
- Perfmon fields may have read/ack ordering constraints. Incorrect counter selection, state selection, interrupt ack, or high/low value handling can produce misleading diagnostics without obvious functional failures.
- The chunk boundary is artificial. It begins in the middle of the interrupt continuation definitions and ends inside the `DC_PERFMON4_PERFCOUNTER_CNTL` field group; adjacent chunks are needed for complete file-level conclusions.

## Test Signals

Useful validation signals are a mix of generated-header consistency checks and hardware behavior:

- Build AMDGPU/DC with DCN 3.5 support enabled; missing or renamed macros should fail in DMUB, IRQ, writeback/MMHUBBUB, audio, and perfmon register-table construction.
- Mechanically verify that each field in lines 8816-11033 has matching `__SHIFT` and `_MASK` definitions where the generated pattern expects both, and that masks align with `SHIFT` values and field widths.
- Diff this chunk against AMD's authoritative DCN 3.5 register database and nearby generated headers such as `dcn_3_5_1_sh_mask.h` where compatibility is expected.
- Exercise IRQ-heavy display flows: hotplug, EDID/DDC reads, DP AUX transactions, vblank/vupdate, vstartup/vready/no-lock, DRR v-total reach, HPD, DMCUB outbox, audio endpoint enable/disable/format changes, and suspend/resume.
- Validate DMUB firmware paths: reset/release, backdoor load/window setup, inbox/outbox command traffic, GPINT handling, scratch registers, fault reporting, and secure-region behavior.
- Test display writeback capture with multiple buffers, planar and packed formats, address-fence enablement, buffer locks, overrun/slice interrupts, VMID/security settings, watermarks, p-state changes, and resume.
- Exercise MMHUBBUB warmup, memory power, clock gating, soft reset, low-power transitions, and outstanding-counter diagnostics.
- Program and read DC perfmon counters, including event selection, run/stop conditions, counter overflow/interrupt ack, and high/low counter reads.
- Watch kernel logs and display diagnostics for stuck interrupts, AUX/I2C timeouts, hotplug storms, blank displays, audio dropouts, DMUB command timeouts, writeback corruption, MCIF overflows, power-gating failures, and inconsistent perf counter results.

## Cross-Chunk Notes

Previous chunks own the earlier DCN 3.5 shift/mask definitions, including the beginning of the display interrupt-status chain before `CONTINUE19`. Later chunks continue `DC_PERFMON4_PERFCOUNTER_CNTL` and cover the remaining field metadata in `dcn_3_5_0_sh_mask.h`. The final per-file research document should merge adjacent chunks before making complete claims about all interrupts, all perfmon instances, or the complete DCN 3.5 register field map.

### subset-b-002061: lines 11034-13252

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 11034-13252

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.5.0 register shift/mask header. It contains C preprocessor constants for register bit positions and positioned masks, not executable logic. Consumers combine these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with the matching DCN 3.5.0 offset header and AMD display register helper macros to read, write, or update memory-mapped display hardware fields.

The requested range contains 2,219 `#define` lines: 1,106 `__SHIFT` macros and 1,123 `_MASK` macros across 481 register groups. The imbalance is caused by chunk boundaries. The range starts inside `DC_PERFMON4_PERFCOUNTER_CNTL` after several earlier shift definitions, and it ends inside `HUBP1_DCSURF_ADDR_CONFIG` before the remaining masks for that register.

The substantive hardware covered here is a wide DCN display data path surface: DC performance monitors 4, 5, and 6; Azalia/HD-audio endpoint, stream, DMA, CRC, and memory-power fields; DCHUBBUB fabric, VM, arbitration, watermark, debug, CRC, clock, and timeout fields; DCN VM context and fault fields; HUBP0/HUBPREQ0/HUBPRET0 surface fetch, flip, TTU/QoS, memory-power, interrupt, cursor, and DMDATA fields; and the opening of the HUBP1 surface configuration.

## Important Constants And Register Areas

`DC_PERFMON4_*`, `DC_PERFMON5_*`, and `DC_PERFMON6_*` expose repeated performance-monitor field layouts. Each instance includes counter selection/control, counted value type and hardware stop selection, eight counter state readback selectors, perfmon run/control state, count-off interrupt control/status/ack fields, counter value interrupt status/ack bits, low/high value readback fields, and `PERFMON_READ_SEL`. `DC_PERFMON4_PERFCOUNTER_CNTL` is incomplete at the start of this slice, while `DC_PERFMON5` and `DC_PERFMON6` are complete within it.

The Azalia section covers display audio register layout. It includes output endpoints `AZF0ENDPOINT0` through `AZF0ENDPOINT7`, input endpoints `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7`, stream windows `AZF0STREAM8` through `AZF0STREAM15`, controller clock gating, audio DTO phase/module and force controls, SOCCLK deep-sleep exit behavior, underflow filler samples, data/BDL/CORB/RIRB/DP DMA snoop and isochronous controls, global capabilities, stream arbitration, CRC engines, memory power control/status, codec root/function parameters, power/reset/response controls, GTC group offsets, and audio port connectivity fields.

The DCHUBBUB section covers display hub fabric and memory arbitration. It includes SDPIF credit, response, snoop, and error controls; physical VM request mode; force-IO status capture; framebuffer, AGP, and local-HBM aperture fields; SDPIF and return-path memory power control; DCHUBBUB CRC source/value registers; DCC statistics; compbuf and DET sizing; memory power modes, latencies, and state; debug depth/stall controls; outstanding request limits; QoS force controls; DRAM state gating for self-refresh, p-state, c-state, and DCFCLK deep sleep; watermark sets A through D; HostVM controls; watermark change request/done controls; timeouts; VTG control; soft reset; clock and DCFCLK control; performance measurement windows; global timer; surface-check addresses; test debug index/data; and `FMON_CTRL`.

The DCN VM context section describes contexts 0 through 15. Each context has page-table depth and block-size fields plus high/low base, start, and end logical page number fields. The same section includes default address, fault control/status, and fault address fields. These macros describe how the display hub's VM view is programmed and how VM faults are reported.

The HUBP0 and HUBPREQ0 section covers surface fetch programming for pipe 0. It includes surface pixel format, rotation, mirror, alpha, address/tiling config, primary/secondary viewport start/dimensions for luma and chroma, request-size config, HUBP control and clock gating, VMPG config, DCFCLK/DPPCLK measurement windows, surface pitch, VMID, primary/secondary and metadata surface addresses, TMZ/DCC surface control, flip control, flip interrupts, in-use and earliest-in-use addresses, expansion mode, TTU/QoS watermarks, VM aperture and L1 TLB controls, blank/prefetch/flip/nominal timing parameters, per-line delivery parameters, cursor settings, and HUBPREQ memory power state.

`HUBPRET0_*` covers the return path: control fields, memory-power control/status, read-line programming and status, and interrupt mask/type/clear/status/overflow fields. `CURSOR0_0_*` covers cursor enable/mode/address/size/position/hot-spot/stereo control, memory power state, DMDATA address/control/QoS/status, and software DMDATA injection. The chunk ends with `HUBP1_DCSURF_SURFACE_CONFIG` and the first part of `HUBP1_DCSURF_ADDR_CONFIG`, establishing that the next chunk continues the repeated HUBP instance layout.

Common bitfield shapes in this chunk include full 32-bit value ports, 16-bit low/high address or data halves, 4-bit VMID selectors, status/clear/ack bit pairs, power force/disable/status fields, repeated instance suffixes, and repeated A/B/C/D watermark banks. Several registers contain side-effect fields such as interrupt clear, timeout clear, underflow clear, fault status clear, response status clear, soft reset, clock enable, and memory power force/disable.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. Its API surface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the bit position for a field.
- `REGISTER__FIELD_MASK` gives the field mask already shifted into register position.
- Repeated register prefixes such as `DC_PERFMON5`, `DCHUBBUB`, `DCN_VM_CONTEXT7`, `HUBPREQ0`, and `CURSOR0_0` encode hardware block and instance identity.

Consumers pair these definitions with register offsets from `dcn_3_5_0_offset.h`. The display stack commonly routes generated offsets, shifts, and masks into `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_SEQ`, and block-specific register field list macros. The DMUB DCN35 service also includes this header while initializing DCN35 register metadata. Semantic values, valid ranges, and sequencing rules are not defined here; they come from ASIC documentation, generated enum/value headers, and the higher-level DCN programming code.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior is implied by driver sequences that write and read the described registers.

Performance-monitor flows select events, counted value type, increment mode, run-enable start/stop sources, count-off behavior, and readback selectors, then read low/high counter values or acknowledge counter interrupts. Since perfmon instances 4, 5, and 6 use the same layout, callers can share programming logic across instances once the correct offsets are supplied.

Audio flows program Azalia endpoint and stream indexed data ports, configure audio DTO phase/module, choose DMA snooping and isochronous behavior, handle underflow filler behavior, configure CRC capture, expose codec capabilities, and control codec/function power state. Endpoint and stream register pairs have index/data access patterns, so ordering matters: the index field selects a register, and the data field transfers the payload.

DCHUBBUB and VM flows program memory apertures, page-table contexts, arbitration watermarks, request limits, HostVM behavior, fabric clock/deep-sleep policy, and timeout detection. The visible fields support both normal display timing setup and diagnostic/status paths: CRC values, DCC statistics, force-IO status, surface-check addresses, performance measurements, global timer snapshots, timeout interrupts, and FMON filtering.

HUBP/HUBPREQ/HUBPRET/CURSOR flows program a pipe's surface fetch state. A typical plane update writes surface format, tiling, request sizing, pitches, addresses, VMID, surface control, viewport geometry, prefetch/timing/TTU parameters, and flip controls, then observes flip-pending, in-use, earliest-in-use, underflow, timeout, and interrupt status. Cursor and DMDATA flows separately program cursor memory, position, stereo behavior, metadata payload address or software data, QoS, and underflow/done status.

## State And Persistence

The file itself stores no mutable state. It defines how software addresses state held in DCN 3.5.0 hardware registers.

Persistent hardware state represented in this chunk includes performance counter configuration and values, Azalia stream/endpoint/audio power state, DCHUBBUB memory aperture and VM context state, page-table base/start/end values, fabric arbitration and watermark state, memory power modes and statuses, HUBP surface format/address/tiling/viewport/flip state, TTU/QoS timing parameters, current in-use surface addresses, cursor memory and position state, DMDATA state, and interrupt/status latches. These values can persist across frames and until reset, modeset reprogramming, suspend/resume restore, or block power transitions.

Many fields are hardware-latched or side-effectful rather than ordinary storage. Examples include clear/ack bits, interrupt status, timeout status, underflow status, memory power state readbacks, current-size fields, no-outstanding-request flags, flip-pending and in-use address readbacks, CRC completion/results, VM fault status/address, and performance counter active/state fields. Callers should treat status fields as hardware observations and clear bits as commands.

## Dependencies And Integration Points

This generated header depends on the matching DCN 3.5.0 offset header and AMDGPU display register helper framework. Numeric masks are specific to the DCN 3.5.0 register database and should not be mixed with offsets from other ASIC generations unless explicitly validated.

Important integration points include:

- DCN35 DMUB register initialization, which includes `dcn_3_5_0_sh_mask.h` to populate register mask/shift metadata.
- HUBBUB memory arbitration, watermark, self-refresh, p-state, HostVM, timeout, CRC, and diagnostic code.
- HUBP/HUBPREQ/HUBPRET plane programming paths for surface address, tiling, flip, QoS, prefetch, VM, memory power, and cursor handling.
- Display audio/Azalia code that programs codec endpoints, streams, DTO, DMA policy, CRC, and audio memory power.
- Display VM and fault handling code that programs page-table contexts and decodes VM fault status/address.
- Performance-monitor and diagnostic paths that configure perf counters and read display fabric or pipe performance state.

The macros are intentionally low-level. They provide bit layout only; legal field values, ordering constraints, synchronization points, and read/write permissions are enforced, if at all, by higher-level DCN block code and hardware validation.

## Risks And Edge Cases

Generated-header drift is the primary risk. A wrong shift or mask can compile cleanly while corrupting unrelated bits in a display register, causing underflow, bad audio, wrong surface addressing, missed interrupts, incorrect VM translation, broken power management, or hard-to-debug display timing failures.

Chunk boundaries create local incompleteness. The opening `DC_PERFMON4_PERFCOUNTER_CNTL` group is missing earlier field definitions from the previous chunk, and the closing `HUBP1_DCSURF_ADDR_CONFIG` group is missing later masks from the next chunk. Whole-register validation for those two groups must include adjacent chunks.

Repeated-instance consistency matters. `DC_PERFMON5` and `DC_PERFMON6` should mirror the same field layout as the complete parts of `DC_PERFMON4`; `HUBP1` begins a layout that should match the full `HUBP0` register family where the hardware intentionally repeats instances. A one-instance generation error may only affect specific pipes or diagnostics.

Address, VM, and TMZ/DCC fields are high blast-radius. Wrong VMID, page-table, aperture, surface address, metadata address, DCC, or TMZ bits can point display fetches at the wrong memory, trigger VM faults, expose protected content incorrectly, or generate underflows. These fields should be programmed through established pipe update sequences, not open-coded writes.

Power, clock, and clear/ack fields are side-effect-prone. Memory power force/disable, clock gating, soft reset, underflow clear, timeout clear, interrupt clear, fault clear, and perf counter ack fields can change hardware state immediately. Register helpers should preserve unrelated fields and should use the documented write-one-to-clear or write-one-to-ack convention for each register.

Watermark and TTU fields are timing-sensitive. Incorrect urgency, self-refresh, p-state, prefetch, delivery, or QoS programming may pass compile tests but fail only under bandwidth pressure, high refresh, multi-plane, cursor, stereo, audio, or power-transition scenarios.

## Test And Validation Signals

Build validation should include DCN35 display and DMUB objects that include `dcn_3_5_0_sh_mask.h`. Missing or renamed macros usually fail at compile time; incorrect numeric values usually require generated-data comparison, register-database validation, or hardware testing.

Useful generated-data checks include:

- Compare this range against the authoritative DCN 3.5.0 register database.
- Verify non-overlapping masks and matching shifts for complete register groups, excluding the intentionally incomplete first and last groups.
- Diff repeated perfmon instances 4, 5, and 6 for structural consistency.
- Diff HUBP0/HUBPREQ0/HUBPRET0/CURSOR0 layout against other HUBP instances in adjacent chunks where repetition is expected.
- Cross-check DCN VM context 0 through 15 for identical context register layouts.
- Compare DCHUBBUB watermark banks A through D for consistent field widths and intended per-bank differences.

Runtime validation signals include successful DCN35 modesets, multi-plane flips without underflow or timeout interrupts, correct VM fault reporting and clearing, stable suspend/resume and runtime power transitions, correct cursor and DMDATA behavior, audio playback over display outputs, stable Azalia CRC/debug behavior where supported, correct perf counter readback/interrupt acknowledgment, and no regressions under bandwidth-heavy scenarios such as high refresh, multi-monitor, DCC-enabled surfaces, cursor movement, stereosync, and HostVM/system-memory display paths.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002061_research.md`. Whole-file research for `dcn_3_5_0_sh_mask.h` must merge adjacent chunks to complete the opening `DC_PERFMON4_PERFCOUNTER_CNTL` register group and the closing `HUBP1_DCSURF_ADDR_CONFIG` register group.

### subset-b-002062: lines 13253-15470

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 13253-15470

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.5.0 register shift/mask header. It contains C preprocessor constants for display hardware bitfields, not executable driver logic. Each `REGISTER__FIELD__SHIFT` macro gives a field bit position and each `REGISTER__FIELD_MASK` macro gives the already-positioned mask used by AMD display register helpers.

The requested range contains 2,218 `#define` lines: 1,108 shift macros and 1,110 mask macros. The imbalance is caused by chunk boundaries. The first two lines are only the trailing masks for `HUBP1_DCSURF_ADDR_CONFIG` fields whose shifts appear in the previous chunk, and the range ends immediately after `CURSOR0_3_DMDATA_ADDRESS_HIGH` before `CURSOR0_3_DMDATA_ADDRESS_LOW` and the remaining DMDATA control/status fields continue in the next chunk.

The substantive hardware surface covered here is the DCN 3.5 HUBP pipeline register layout for instances 1 through 3, including surface tiling, viewport geometry, memory request sizing, VM/QoS timing, flip control, HUBPREQ request-side state, HUBPRET return-side state, cursor programming, DMDATA programming for cursor instances 1 and 2, and the start of cursor/DMDATA instance 3.

## Important Constants And Register Areas

`HUBP1_*`, `HUBP2_*`, and `HUBP3_*` define the hub pipe front-end fields used to fetch and present plane data:

- `DCSURF_ADDR_CONFIG` and `DCSURF_TILING_CONFIG` describe memory layout: pipe count, pipe interleave, compressed fragment limits, packetizer count, swizzle mode, dimension type, metadata linearity, and pipe alignment. The requested range only has the final two masks for `HUBP1_DCSURF_ADDR_CONFIG`; `HUBP2` and `HUBP3` include the complete address-config field set.
- `DCSURF_PRI_VIEWPORT_*` and `DCSURF_SEC_VIEWPORT_*`, plus `_C` chroma variants, pack X/Y starts and width/height values in 14-bit halves. These fields establish luma/chroma primary and secondary viewport windows.
- `DCHUBP_REQ_SIZE_CONFIG` and `_C` define swath height, PTE row height, chunk size, meta chunk size, DPTE group size, and VM group size. These fields feed request sizing and address-translation behavior for luma and chroma fetches.
- `DCHUBP_CNTL` contains blank/reset/status/control bits such as `HUBP_BLANK_EN`, no-outstanding-request indicators, soft reset, VTG select, unbounded request mode, TTU disable/mode, timeout status/threshold/interrupt enable, and underflow status/clear bits.
- `HUBP_CLK_CNTL`, `DCHUBP_VMPG_CONFIG`, and `HUBP_MEASURE_WIN_CTRL_DCFCLK/DPPCLK` describe clock enable/gating status, virtual memory page size, and performance measurement windows.

`HUBPREQ1_*`, `HUBPREQ2_*`, and `HUBPREQ3_*` define request-side surface and timing fields:

- Surface pitch, VMID, primary/secondary surface addresses, primary/secondary metadata addresses, and high address halves for luma and chroma.
- Surface control, surface in-use and earliest-in-use tracking, flip interrupt masking/clear/status fields, and flip control fields such as immediate flip, horizontal timing, flip pending/armed status, page-queue and earliest-in-use toggles, and memory format checks.
- TTU/QoS and delivery timing fields: `DCN_GLOBAL_TTU_CNTL`, `DCN_SURF*_TTU_CNTL*`, `DCN_CUR*_TTU_CNTL*`, `DCN_TTU_QOS_WM`, `PREFETCH_SETTINGS`, `PER_LINE_DELIVERY`, nominal/vblank/flip parameters, destination dimensions, blank offsets, and reference-cycle-to-pixel-frequency conversion.
- VM control fields for system aperture low/high addresses, L1 TLB control, and DMDATA VM timing/status/clear fields.
- Request memory power control/status for DPTE, MPTE, metadata, and PDE memories.

`HUBPRET1_*`, `HUBPRET2_*`, and `HUBPRET3_*` define return-side and cursor-return state:

- `HUBPRET_CONTROL` maps DET buffer base address, 3-to-2 packing disable, and crossbar source selection for alpha, Y/G, Cb/B, and Cr/R.
- `HUBPRET_MEM_PWR_CTRL` and `_STATUS` control and report DMROB and PIXCDC memory power state.
- `HUBPRET_READ_LINE_CTRL*`, `READ_LINE0`, `READ_LINE1`, `INTERRUPT`, `READ_LINE_VALUE`, and `READ_LINE_STATUS` define vblank/read-line window programming, interrupt mask/type/clear/status bits, current read line snapshots, and inside/outside window status.

`CURSOR0_1_*` and `CURSOR0_2_*` are complete in this range, while `CURSOR0_3_*` is partial. The complete cursor instances include cursor enable/request mode/magnification/mode/TMZ/pitch/line-per-chunk/perfmon fields, cursor surface address, size, position, hotspot, stereo offsets, destination X offset, cursor ROB memory power fields, and DMDATA address/control/QoS/status/software-control/data fields. The partial instance 3 coverage includes cursor control through `DMDATA_ADDRESS_HIGH`.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. The API surface is the generated macro namespace consumed by higher-level register tables.

The constants pair with `dcn_3_5_0_offset.h`, which supplies matching `reg...` addresses such as `regHUBP1_DCSURF_ADDR_CONFIG` and `regCURSOR0_3_DMDATA_STATUS`. They are then lifted into typed shift/mask structures through display block macros. In the DCN35 HUBP layer, `HUBP_MASK_SH_LIST_DCN35(mask_sh)` extends the DCN32 HUBP field list and is instantiated by DCN35/351/36 resource code as both `__SHIFT` and `_MASK` lists. Runtime code uses register helper APIs such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, `REG_READ`, `REG_WRITE`, and `REG_WAIT` with these generated field definitions.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs when the display driver uses the fields to program memory-mapped DCN hardware.

The implied HUBP surface programming flow is: configure tiling/address layout from framebuffer tiling metadata, set viewport and pitch for luma/chroma planes, program VMID and surface/meta addresses, set request sizing and TTU/QoS timing from DML/DLG calculations, arm flips through `DCSURF_FLIP_CONTROL*`, and observe or clear flip/underflow/timeout status bits. Surface update locking and vblank timing matter because many of these fields are consumed by active scanout hardware.

The implied HUBPRET flow is return-path setup and monitoring: select DET buffer base and color component crossbar mapping, configure read-line/vblank interrupt windows, and sample read-line status for synchronization or diagnostics. Interrupt-related masks and clear/status fields integrate with the DC IRQ service's page-flip and vline/vblank paths.

The implied cursor/DMDATA flow is: program cursor address, size, position, hotspot, format/mode, memory power state, and optional display metadata delivery. For hardware DMDATA mode, the HUBP code toggles `DMDATA_UPDATED`, sets repeat and size, programs low/high address fields, and configures QoS. For software DMDATA mode, it toggles software update fields and writes `DMDATA_SW_DATA`.

## State And Persistence

The file stores no mutable state. It defines how software addresses persistent hardware state in per-pipe HUBP, HUBPREQ, HUBPRET, cursor, and DMDATA registers.

Hardware state represented here persists until reset, modeset reprogramming, plane update, cursor update, DMDATA update, power transition, or suspend/resume restore. Important state includes surface base and metadata addresses, pitch, viewport geometry, tiling mode, VMID, VM aperture/TLB settings, timing and QoS watermarks, flip pending/armed/status bits, read-line interrupt windows, cursor image attributes, DMDATA address/control/QoS settings, and memory power states for HUBPREQ/HUBPRET/cursor memories.

Several fields are status or clear-on-write style controls rather than simple configuration. Examples include underflow clear, timeout status clear, flip interrupt clear, VM fault/underflow status clear, read-line interrupt clear, and DMDATA underflow clear in the complete cursor instances. Callers must preserve write semantics through the central register helpers instead of treating all masks as ordinary persistent configuration bits.

## Dependencies And Integration Points

This generated header must match the DCN 3.5.0 register offset header and the hardware register database used to generate both files. The masks are not independently portable to other ASIC generations unless the register database and block-specific field lists show compatible layouts.

Key integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`, which includes `dcn_3_5_0_offset.h` and this shift/mask header when constructing DCN35 resources.
- `drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.h`, where `HUBP_MASK_SH_LIST_DCN35` feeds DCN35 HUBP shift and mask structures.
- `drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`, which includes the same generated headers for DCN35 interrupt programming, including page-flip sources backed by `DCSURF_SURFACE_FLIP_INTERRUPT`.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which includes this header for DMUB/DCN35 register interaction.
- Generic HUBP, DPP, IRQ, DML/DLG, cursor, and DMDATA paths that use the field names through register helper macros rather than directly referencing instance-specific `HUBP1_`, `HUBPREQ2_`, or `CURSOR0_3_` tokens.

## Risks And Edge Cases

Generated-header drift is the primary risk. Incorrect masks or shifts compile normally but can route writes into adjacent fields, causing wrong tiling, bad scanout addresses, broken flips, cursor corruption, DMDATA failures, false interrupts, or unsafe memory power transitions.

Chunk boundaries are locally incomplete. The opening `HUBP1_DCSURF_ADDR_CONFIG` field group lacks its shift lines in this slice, and `CURSOR0_3_DMDATA_ADDRESS_HIGH` is the last complete register in the requested range. Any whole-file reconciliation must merge neighboring chunks before claiming complete coverage of those boundary register groups.

Repeated-instance consistency is important. HUBP/HUBPREQ/HUBPRET and cursor instances are mechanically parallel, but one wrong instance-specific token or numeric value can produce failures only on a particular pipe. Multi-pipe, multi-monitor, and cursor-on-nonzero-pipe paths are therefore valuable validation targets.

Several fields have sequencing or side-effect hazards. Flip control and flip interrupt fields must be synchronized with surface update locks and vertical timing. Memory power force/disable/status fields must not be changed while dependent request, return, cursor, or metadata memories are actively needed. Clear bits should be written according to established IRQ/status handling paths to avoid losing real fault evidence.

The constants use 32-bit masks with `L` suffixes, including high-bit masks such as `0x80000000L` and `0xFFFF0000L`. Consumers should rely on existing unsigned register helper paths and avoid open-coded signed arithmetic.

## Test And Validation Signals

Compile-time validation should build all DCN35 display users that include this header, especially resource initialization, HUBP construction, IRQ service code, and DMUB DCN35 code. Missing or renamed macros are usually caught at compile time through the generated register field lists.

Generated-data checks should compare this chunk against the authoritative DCN 3.5.0 register database, verify that complete registers have non-overlapping masks matching their shifts, and diff repeated instances (`HUBP1/2/3`, `HUBPREQ1/2/3`, `HUBPRET1/2/3`, `CURSOR0_1/2`) while accounting for intentional boundary incompleteness.

Runtime signals include successful modesets and page flips on DCN35 hardware, correct scanout of tiled and linear buffers, stable chroma/luma viewport programming, no HUBP underflow or VM fault status under normal bandwidth conditions, correct vblank/read-line/page-flip interrupt delivery and clearing, cursor correctness on multiple pipes, DMDATA hardware/software update completion, and clean suspend/resume or runtime power-management transitions.

## Research Notes

This is chunk-level research only for `subset-b-002062`. It intentionally writes only `Docs/researches/chunks/subset-b-002062_research.md`; final per-file synthesis for `dcn_3_5_0_sh_mask.h` must be produced later by the merge/reconciliation lane after adjacent chunks are available.

### subset-b-002063: lines 15471-17691

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 15471-17691

## Purpose

This chunk is generated AMD DCN 3.5.0 register field metadata. It contains C preprocessor constants only: no executable functions, structs, enums, variables, locks, allocation, or persistence code. The exported contract is a large set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros used by AMDGPU display code to pack, update, read, and decode fields in DCN 3.5 MMIO registers.

The assigned range starts at `CURSOR0_3_DMDATA_ADDRESS_LOW` for cursor metadata instance 3, covers DC performance monitor instance 9, the DPP/CNVC/DSCL/CM register-field layouts for display pipe 0 and pipe 1, and ends inside the shift definitions for `DC_PERFMON11_PERFMON_CNTL`. It is a middle chunk of `dcn_3_5_0_sh_mask.h`; adjacent chunks own the preceding `CURSOR0_3_DMDATA_ADDRESS_HIGH` field and the remainder of `DC_PERFMON11`.

Although this source tree is rooted under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It does not implement Ceph, filesystem, distributed-storage, or network behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this range. The important interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: already-positioned bit mask for the field.
- Repeated instance prefixes such as `DPP_TOP0_`/`DPP_TOP1_`, `DSCL0_`/`DSCL1_`, `CNVC_CFG0_`/`CNVC_CFG1_`, `CNVC_CUR0_`/`CNVC_CUR1_`, `CM0_`/`CM1_`, and `DC_PERFMON9/10/11_` expose per-pipe or per-block copies of similar hardware layouts.

Major macro families in this slice:

- `CURSOR0_3_DMDATA_*`: display metadata registers for cursor/hubp instance 3. The chunk includes low address, hardware-mode control, QoS control, completion/underflow status and clear, software-mode control, and 32-bit software data fields.
- `DC_PERFMON9_*`, `DC_PERFMON10_*`, and the beginning of `DC_PERFMON11_*`: performance monitor counter selection, counted-value type, counter state, run/stop control, clock enable, interrupt status/acknowledge, current value, high/low readback, and report-count fields. The `DC_PERFMON11` group is incomplete in this chunk.
- `DPP_TOP0_*` and `DPP_TOP1_*`: DPP clock gating/enable, soft reset for CNVC/DSCL/CM/OBUF subblocks, DPP CRC readback/control, and host-read rate control.
- `DSCL0_*` and `DSCL1_*`: display scaler coefficient RAM selection/data, scaler mode and tap counts, 2-tap/sharpen controls, manual replication, horizontal/vertical scale ratios and initial phases for luma/chroma/bottom fields, black color, update-pending, autocal, overscan, timing blank windows, recout/MPC size, line-buffer data/memory controls, line-buffer counters, DSCL/LB memory power state, and output-buffer controls.
- `CNVC_CFG0_*` and `CNVC_CFG1_*`: converter surface pixel format, format expansion/conversion, alpha-plane enable, bypass/alignment/clamping, channel crossbar, floating-point conversion bias/scale, color keyer ranges, 2-bit alpha LUT, pre-dealpha, pre-CSC matrices and double-buffered B matrices, coefficient format, pre-degamma, and pre-realpha fields.
- `CNVC_CUR0_*` and `CNVC_CUR1_*`: cursor color-converter controls for cursor enable, mode, expansion, pixel inversion, ROM enable, alpha modulation, update-pending, 24-bit palette colors, and FP scale/bias.
- `CM0_*` and `CM1_*`: color-management bypass/update-pending, post-CSC matrices and B matrices, gamut-remap matrices and B matrices, bias, gamma-correction control, gamma LUT index/data/control, gamma RAM A/B start/end/slope/base/offset definitions, 34-region LUT segmentation pairs, HDR multiplier coefficient, gamma memory power control/status, dealpha, and coefficient-format fields.

The chunk also includes a `CM0_CM_TEST_DEBUG_INDEX` field pair, which is an indexed debug selector/write-enable style interface for the CM block.

## Control Flow

This header has no local runtime control flow. Runtime behavior is supplied by AMD display code that includes this generated mask header together with the matching offset header:

1. DCN 3.5 resource, IRQ, and DMUB files include `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Register-list macros in files such as `dcn35_resource.c`, `dcn35_dpp.h`, and common DPP/HUBP headers paste generated register and field tokens into shift and mask identifiers.
3. Resource construction stores these generated constants in per-block register, shift, and mask tables, for example DPP pipe tables created through `DPP_REG_LIST_DCN35_RI(id)` and `DPP_REG_LIST_SH_MASK_DCN35(__SHIFT/_MASK)`.
4. Operational code later uses helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and block-specific wrappers. Those helpers combine register offsets from `dcn_3_5_0_offset.h` with shift/mask constants from this file.

The macros themselves do not encode programming order. Cursor metadata code must still order DMDATA address, size, mode, updated/repeat bits, QoS, and status clear operations correctly. DPP code must still coordinate scaler programming, coefficient RAM updates, CNVC format setup, color-management LUT/matrix programming, double-buffer updates, memory power transitions, CRC control, and soft resets around mode-set and plane-update sequencing.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes MMIO-backed GPU state whose lifetime is controlled by display hardware, power management, reset, suspend/resume, and modeset reprogramming.

Represented hardware state includes:

- Cursor display metadata state for pipe/cursor instance 3: DMDATA low address, hardware/software mode, packet size, repeat/update latches, QoS mode/level/deadline delta, done status, underflow status, and underflow clear.
- Perfmon state for instances 9 and 10, plus the start of instance 11: event selector, counted-value type, run-enable and stop/start selection, counter active state, interrupt enable/status/acknowledge, high/low/current values, and report count.
- DPP top-level state: DPP clock enable/gating overrides, subblock soft-reset bits, CRC enable/one-shot/continuous/source/pixel-format/stereo/interlace/cursor-format masks, CRC results, and host-read throttling.
- DSCL state: scale ratios and phase accumulators, luma/chroma tap counts, coefficient RAM contents and bank selection, scaler mode, overscan/timing/recout geometry, line-buffer layout and partitioning, output-buffer bypass/hold behavior, and DSCL/LB/OBUF memory power force/disable/status bits.
- CNVC state: surface pixel format, alpha-plane handling, format expansion/conversion, component crossbar, positive clamp, color-key thresholds, pre-CSC matrix selection/current state, pre-degamma and pre-alpha behavior, FP conversion bias/scale, and cursor color conversion.
- CM state: post-CSC and gamut-remap matrices, bias, gamma LUT host/index/data selection, gamma RAM A/B PWL region definitions, HDR multiplier, dealpha behavior, coefficient formats, and gamma memory power state.

Some fields are configuration latches; others are live status, update-pending readback, interrupt/status acknowledge, clear bits, or counters. This generated header does not identify access type, self-clearing behavior, write-one-to-clear semantics, read-only fields, or required delays. Consumers must rely on block-level driver code and the ASIC programming guide for those semantics.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which defines matching `reg...` offsets and base-index constants. For this chunk, notable companion offsets include `regCURSOR0_3_DMDATA_*`, `regDC_PERFMON9_*`, `regDC_PERFMON10_*`, `regDC_PERFMON11_*`, `regDPP_TOP0_*`, and `regDPP_TOP1_*`.

Visible DCN 3.5 include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`, which includes the offset and mask headers and constructs DCN 3.5 block register/field tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`, which includes the same generated headers for DCN 3.5 interrupt table support.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which includes the generated DCN 3.5 register metadata for DMUB-side display-microcontroller access.

The DPP integration path is token-paste based. `dcn35_resource.c` initializes per-pipe DPP tables through `DPP_REG_LIST_DCN35_RI(id)` and initializes `struct dcn35_dpp_shift`/`struct dcn35_dpp_mask` through `DPP_REG_LIST_SH_MASK_DCN35`. That field list extends common DPP/DCN3 lists, which consume many macros in this chunk: `DPP_TOP0_DPP_CONTROL`, `DSCL0_*`, `CNVC_CFG0_*`, `CNVC_CUR0_*`, and `CM0_*`. Instance-specific register-list macros map the `0` field names across physical DPP instances.

The cursor DMDATA macros integrate with HUBP code families. Common HUBP field lists in nearby generations consume names such as `CURSOR0_0_DMDATA_CNTL`, `DMDATA_UPDATED`, `DMDATA_SIZE`, `DMDATA_QOS_LEVEL`, and `DMDATA_DONE`; the DCN 3.5 generated instance-3 names in this chunk are the same hardware contract for the fourth pipe/cursor instance.

Because the integration uses preprocessor token pasting, macro spelling is part of the compile-time ABI between generated register headers and AMD display code. A missing, renamed, or stale shift/mask macro can either break compilation or compile while sending `REG_UPDATE` to the wrong bitfield.

## Risks And Edge Cases

- Generated masks are untyped numeric constants. A wrong shift or mask can pass compilation and only appear as hardware-specific display corruption, missing cursor metadata, broken scaling, bad color, or invalid diagnostics.
- The chunk begins after `CURSOR0_3_DMDATA_ADDRESS_HIGH`. Whole DMDATA programming requires both high and low address fields; reviewing this chunk alone cannot validate the full address path.
- DMDATA update/status fields are stateful and timing-sensitive. Bad masks for `DMDATA_UPDATED`, `DMDATA_SIZE`, `DMDATA_QOS_LEVEL`, `DMDATA_DONE`, or `DMDATA_UNDERFLOW_CLEAR` can cause stale metadata, underflows, hidden faults, or repeated metadata transmission.
- Perfmon fields are diagnostic but still side-effect sensitive. Bad counter event, run-enable, interrupt, clear/ack, or read-select masks can corrupt performance data, hide counter overflows, or create spurious interrupts.
- DPP clock gating and soft reset bits can affect active display pipes. Incorrect `DPP_CLOCK_ENABLE`, clock-gate disable, or subblock reset masks may cause intermittent blanking, hangs, or resume-only failures.
- DSCL fields are dense fixed-point geometry and filter controls. Off-by-one shifts in ratio/init/tap/coef fields can produce scaling artifacts, chroma misalignment, overscan errors, line-buffer underflow, or corruption only for specific source/destination sizes.
- CNVC and CM fields directly affect pixel interpretation and color output. Bad format, alpha, color-key, CSC, gamut-remap, gamma, bias, or HDR multiplier masks can create subtle color regressions, wrong alpha blending, cursor color issues, or failures in HDR/wide-gamut modes.
- Gamma RAM A/B and LUT region registers are large repeated tables. Region pair masks must remain consistent across indices 0-33; a single wrong field can damage only part of a PWL transfer function, making failures hard to isolate visually.
- Memory power force/disable/status bits for DSCL, OBUF, and CM are power-state sensitive. Incorrect masks can leave memories powered off while in use or prevent intended low-power transitions.
- `DC_PERFMON11` is split by the chunk boundary. This document covers only its `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, and the first `PERFMON_CNTL` shift definitions; masks and remaining registers are in the next chunk.

## Test Signals

Useful validation is mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU/DC with DCN 3.5 enabled. Token-paste consumers in `dcn35_resource.c`, `irq_service_dcn35.c`, `dmub_dcn35.c`, common DPP code, and HUBP paths should catch missing or renamed macros.
- Mechanically verify every `__SHIFT` macro in this line range has a matching `_MASK` macro where the chunk contains the complete field pair, and that each mask width aligns with the shift and intended field width.
- Cross-check each register in this range against `dcn_3_5_0_offset.h` to ensure the field macros have matching offsets and base indices.
- Diff this chunk against AMD's authoritative DCN 3.5 register database and nearby generated headers such as `dcn_3_2_0_sh_mask.h`, `dcn_3_5_1_sh_mask.h`, or later DCN headers where block layouts are expected to remain compatible.
- Exercise DMDATA paths using hardware and software metadata modes, including repeated metadata, large metadata sizes near the 12-bit size limit, QoS mode changes, underflow injection or stress, and pipe 3 usage.
- Exercise DPP/DSCL paths with scaling up/down, non-integer ratios, chroma subsampling, interlaced/bottom-field cases, overscan, line-buffer pressure, coefficient RAM updates, and repeated modesets.
- Exercise CNVC and CM paths with varied pixel formats, alpha plane enablement, color keying, cursor color modes, pre-CSC/post-CSC, gamut remap, gamma LUT updates, HDR multiplier, and suspend/resume.
- Use CRC/perfmon/debugfs or internal diagnostics where available to verify DPP CRC enable/one-shot/readback behavior and perfmon counter selection/readback for instances 9-11.
- Watch for symptoms such as blanking during modeset, scaler artifacts, color shifts, broken HDR/gamma, wrong cursor colors, metadata underflow logs, invalid perf counters, interrupt storms, or resume-only display failures.

## Cross-Chunk Notes

This is chunk 8 of 25 for `dcn_3_5_0_sh_mask.h`. The previous chunk contains earlier HUBP/cursor metadata fields including `CURSOR0_3_DMDATA_ADDRESS_HIGH`. The next chunk completes `DC_PERFMON11_PERFMON_CNTL` and continues later DCN 3.5 register-field families. The final per-file report should merge this chunk with adjacent chunks before drawing conclusions about complete DPP, DMDATA, or perfmon coverage.

### subset-b-002064: lines 17692-19909

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 17692-19909

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.5.0 register shift/mask header. It contains preprocessor constants for hardware register bitfields, not executable driver logic. Consumers combine these `__SHIFT` and `_MASK` constants with the matching `dcn_3_5_0_offset.h` register offsets and AMD display register helpers to read or write memory-mapped DCN display hardware.

The requested range contains 2,218 `#define` lines: 1,113 shift macros and 1,105 mask macros. The imbalance is caused by chunk boundaries. The range starts inside the tail of `DC_PERFMON11_PERFMON_CNTL`, after earlier `PERFMON_STATE`, `PERFMON_RPT_COUNT`, `PERFMON_CNTOFF_AND_OR`, and `PERFMON_CNTOFF_INT_EN` shift lines, and ends inside `FMT0_FMT_BIT_DEPTH_CONTROL` before the remaining shifts and all masks for that register. There are no source comments in this range.

The substantive hardware covered here is the DCN 3.5 DPP pipe 2 and pipe 3 programming surface, plus adjacent performance monitor instances and the beginning of output formatter instance 0. Major areas are:

- `DC_PERFMON11`, `DC_PERFMON12`, and `DC_PERFMON13` control, counter state, interrupt, and value readback fields.
- `DPP_TOP2` and `DPP_TOP3` DPP clock, reset, CRC, and host-read control fields.
- `CNVC_CFG2`/`CNVC_CUR2` and `CNVC_CFG3`/`CNVC_CUR3` input conversion, surface format, pre-CSC, pre-degamma, color keyer, alpha, cursor, and floating-point bias/scale fields.
- `DSCL2` and `DSCL3` scaler, line buffer, coefficient RAM, recout, overscan, autocalibration, and scaler/OBUF memory power fields.
- `CM2` and `CM3` color-management controls: post-CSC, gamut remap, bias, gamma correction LUT RAM A/B programming, HDR multiplier, dealpha, coefficient format, and CM memory power state.
- The first `FMT0` output formatter fields for clamp ranges, dynamic expansion, pixel encoding/subsampling control, and the initial part of bit-depth/truncation/dither control.

## Important Constants And Register Areas

The `DC_PERFMON11` tail defines perfmon count-off interrupt status and acknowledgement bits, perfmon clock enable, run-enable start/stop selectors, counter interrupt status/ack bits for counters 0 through 7, high/low counter value readback, and read-select fields. `DC_PERFMON12` and `DC_PERFMON13` are more complete in this chunk and add counter event selection, counted-value selection, increment mode, hardware stop selectors, count-off selector, active state, and per-counter state selectors. These are diagnostic/performance measurement registers for display hardware events.

`DPP_TOP2` and `DPP_TOP3` expose the per-DPP top-level control surface. The fields cover `DPP_CLOCK_ENABLE`, DPPCLK and DISPCLK gate-disable bits, dynamic gate disables, test-clock select, soft resets for CNVC/DSCL/CM/OBUF subblocks, CRC values and control, and host read rate control. The same layout is repeated for DPP instances 2 and 3.

`CNVC_CFG2` and `CNVC_CFG3` describe the converter/cursor input side of each DPP. They include surface pixel format and alpha-plane enable, format expansion and 16-bit conversion, alpha enable, bypass and MSB alignment, positive clamp controls, update-pending readback, RGB crossbar selection, floating-point conversion bias and scale per channel, color keyer control and low/high component ranges, a 2-bit alpha LUT, pre-dealpha and pre-realpha controls, pre-CSC mode/current-mode and coefficient matrix banks A/B, pre-degamma mode/select, cursor mode/enable/expansion/inversion/ROM fields, cursor colors, and cursor floating-point scale/bias.

`DSCL2` and `DSCL3` contain the scaler path. Fields cover coefficient RAM tap select/data, scaler mode and current coefficient RAM select, vertical/horizontal and chroma tap counts, 2-tap hardcoded/sharpen controls, manual replication, horizontal/vertical scale ratios and initial phases for luma/chroma/bottom fields, black color, update state, autocalibration mode/pipe id/pipe count, extended overscan, OTG blank timing, recout start/size, MPC size, line-buffer data format and memory configuration, vertical counter, DSCL LUT/ALU/line-buffer/alpha memory power force/disables, corresponding memory power status fields, OBUF mode, and OBUF memory power force.

`CM2` and `CM3` are complete repeated color-management instances for pipes 2 and 3. They include CM bypass/current-mode, post-CSC control and matrix banks A/B, gamut-remap control and matrix banks A/B, bias fields, gamma-correction control, LUT index/data/control, RAM A and RAM B start/end/slope/base/offset fields for B/G/R channels, 34 gamma region descriptors per bank, HDR multiplier, shared/gamma memory power control and status, dealpha controls, and coefficient format. Region descriptor registers pack two regions per 32-bit register, using low/high LUT offsets and segment-count fields.

The `FMT0` tail begins output formatter instance 0. It includes per-channel clamp lower/upper bounds, dynamic expansion enable/mode, formatter control fields for stereosync override, spatial-dither frame counter, pixel encoding, subsampling mode/order, CbCr bit-reduction bypass, and double-buffer update pending. The chunk ends after the early `FMT_BIT_DEPTH_CONTROL` shifts for truncate, spatial dither, randomization, and temporal dither fields; later shifts and masks continue after line 19909.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this source range. The public interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the bit position for packing or extracting a register field.
- `REGISTER__FIELD_MASK` gives the already-positioned field mask.
- Register names encode the hardware block and instance, such as `CNVC_CFG2_*`, `DSCL3_*`, or `CM2_*`.

The macros are consumed indirectly by register-list and field-list structures in the AMD display stack. For DCN 3.5, `dc/resource/dcn35/dcn35_resource.c` includes both `dcn_3_5_0_offset.h` and this shift/mask header, then builds register address and `tf_shift`/`tf_mask` tables for DPP construction. `dc/dpp/dcn35/dcn35_dpp.c` stores those tables in DPP objects and accesses fields through `REG_SET`, `REG_UPDATE`, and related helpers. The output formatter side is similarly represented through OPP structures, and IRQ/DMUB code also includes this generated header for DCN 3.5 register access.

Semantic values are not defined here. Valid enum-like settings for pixel formats, scaler modes, LUT modes, memory power states, dither modes, and performance counter event selectors must come from hardware documentation, generated enum headers, or higher-level DCN code.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior happens when the display driver uses these masks and shifts to program DCN registers during modeset, plane update, color-management update, cursor update, diagnostics, power-management, or debug readback paths.

The implied DPP programming flow starts with top-level DPP clock gating and optional subblock reset, then converter setup for surface format, alpha, bypass, channel swizzle, color keying, pre-CSC/pre-degamma, and cursor state. Scaler setup programs coefficient RAM selection/data, tap counts, scale ratios, initial phases, viewport/recout dimensions, line-buffer format, and autocalibration fields. Color-management programming writes post-CSC and gamut-remap matrices, gamma-correction LUT index/data/control, RAM A/B piecewise region tables, HDR/dealpha controls, and memory power settings. Output formatter programming, beginning at the end of this chunk, handles clamp and dithering/truncation state after DPP processing.

The performance monitor flow is separate: callers select display events, count modes, hardware start/stop/count-off conditions, interrupt behavior, and readback selectors, then observe active state, interrupt status, and counter values. Count-off interrupt acknowledgement fields are side-effecting by nature and should be handled by the established interrupt/debug path rather than casual read-modify-write code.

Repeated instance layout is important control-flow context. The chunk contains the pipe-2 block sequence from `DPP_TOP2` through `CM2`, then repeats the same sequence for pipe 3 from `DPP_TOP3` through `CM3`. Callers rely on instance-indexed register tables so the same DPP/scaler/color code can operate on different hardware pipes by changing the register base and mask/shift table.

## State And Persistence

The file itself stores no mutable state. It defines how software reaches persistent hardware state in DCN registers and internal SRAM/LUT memories.

Hardware state represented here includes DPP clock/reset/gating controls, CRC configuration and values, surface format and converter controls, color key ranges, cursor mode/colors/FP scale and bias, scaler coefficient RAM and filter geometry, line-buffer configuration, scaler and OBUF memory power state, CM post-CSC/gamut-remap matrices, gamma LUT RAM A/B contents and region tables, HDR multiplier, dealpha mode, and FMT clamp/dither/truncation state.

Several fields expose double-buffered or current-state behavior. `*_CURRENT` fields, update-pending fields, coefficient-RAM current selection, CM current mode, pre-CSC current mode, and formatter double-buffer update pending should be treated as hardware readback/state synchronization points. The macros do not document when those values change; timing comes from the higher-level DCN programming sequence and display blanking/update rules.

Memory power fields are persistent and side-effect-prone. `DSCL*_DSCL_MEM_PWR_CTRL`, `DSCL*_OBUF_MEM_PWR_CTRL`, and `CM*_CM_MEM_PWR_CTRL` can force, disable, or observe memories used for scaler LUTs, line buffers, alpha storage, OBUF, and gamma correction. Powering or depowering these memories out of sequence can affect retained table data and active scanout.

## Dependencies And Integration Points

This generated header depends on the matching DCN 3.5.0 address header. The numeric masks are only meaningful with the same register database and ASIC generation; similar-looking DCN 3.2, 3.5.1, or 4.x headers must not be substituted without validation.

Primary integration points are:

- `dc/resource/dcn35/dcn35_resource.c`, which includes the generated offset and shift/mask headers and expands register-list macros for DCN 3.5 hardware objects.
- `dc/dpp/dcn35/dcn35_dpp.c` and inherited DCN 3.0/3.2 DPP code, which program CNVC, DSCL, CM, and DPP top fields through `tf_shift` and `tf_mask` structures.
- `dc/dpp/dcn30/dcn30_dpp.h`, which defines many common DPP register and field list macros used by later DPP versions for CNVC, DSCL, cursor, color, and memory-power programming.
- `dc/opp/dcn35` and inherited OPP code, which consume the `FMT0_*` family for output pixel processing, clamp, bit-depth reduction, and dithering.
- `dc/irq/dcn35/irq_service_dcn35.c` and `display/dmub/src/dmub_dcn35.c`, which include the same generated header for DCN 3.5 interrupt and DMUB-side register access.

The register helper layer is the main API boundary. Direct open-coded bit twiddling against these masks would bypass instance tables, base-index selection, and existing sequencing assumptions.

## Risks And Edge Cases

Generated-header drift is the central risk. A wrong mask or shift generally compiles successfully but writes the wrong hardware bits, causing subtle failures such as incorrect plane format conversion, broken cursor alpha, bad scaler coefficients, incorrect color matrices, gamma LUT corruption, invalid memory power transitions, or broken performance counter readback.

Chunk boundaries are incomplete. The range begins after part of `DC_PERFMON11_PERFMON_CNTL` and ends before `FMT0_FMT_BIT_DEPTH_CONTROL` is complete. Whole-register validation for those two registers requires neighboring chunks.

Repeated instance consistency is a strong maintenance signal. Pipe 2 and pipe 3 blocks should be structurally parallel, and `DC_PERFMON12`/`DC_PERFMON13` should match except for instance numbering. A one-instance generator error may only appear on a specific DPP pipe or diagnostic counter.

Sequencing-sensitive fields need care. LUT RAM index/data/control fields, coefficient RAM selectors, write-enable masks, current-mode readbacks, update-pending bits, and memory power controls have side effects or hardware timing dependencies. Reordering writes or using the wrong RAM bank can produce visible artifacts or stale state.

The `L` suffix on masks such as `0xFFFF0000L`, `0x80000000L`, and `0xC0000000L` means consumers should keep using the driver register helper types rather than signed arithmetic on raw constants.

## Test And Validation Signals

Compile coverage should include DCN 3.5 display objects that include `dcn_3_5_0_sh_mask.h`, especially resource construction, DPP, OPP, IRQ, and DMUB code. Missing or renamed macros usually fail at compile time; incorrect numeric values require generated-data comparison or hardware validation.

Useful static checks include comparing this range against the authoritative DCN 3.5.0 register database, verifying that complete registers have non-overlapping masks and shifts that match their masks, diffing pipe 2 and pipe 3 repeated blocks, and cross-checking the neighboring chunks for the incomplete `DC_PERFMON11_PERFMON_CNTL` and `FMT0_FMT_BIT_DEPTH_CONTROL` boundaries.

Runtime signals include successful modesets on DCN 3.5 hardware, correct scanout across multiple DPP pipes, cursor enable/format/alpha behavior, scaler quality for luma/chroma and 4:2:0 paths, correct color output with pre-CSC, post-CSC, gamut remap, gamma correction, HDR multiplier, and dealpha enabled, stable suspend/resume and runtime power-management transitions, valid DPP CRC readback, working output dithering/truncation through OPP/FMT, and reliable performance monitor counter/interrupt behavior.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002064_research.md`. Whole-file research for `dcn_3_5_0_sh_mask.h` must merge adjacent chunks to complete the leading `DC_PERFMON11_PERFMON_CNTL` register and the trailing `FMT0_FMT_BIT_DEPTH_CONTROL` register.

### subset-b-002065: lines 19910-22126

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 19910-22126

## Purpose

This chunk is generated AMD DCN 3.5.0 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and masks used by AMDGPU display code when packing, updating, and reading MMIO register fields. The companion offset header supplies register addresses, while this file supplies the field layout inside each register.

The assigned range starts in the middle of output-pixel-processor instance 0 metadata at `FMT0_FMT_BIT_DEPTH_CONTROL`, repeats FMT/DPG/OPPBUF/OPP_PIPE/OPP_PIPE_CRC field masks for output instances 0 through 3, covers top-level OPP and DSC forwarding controls, covers DC performance monitor 14, covers ODM/OPTC input controls for instances 0 through 3, then covers all of OTG0 timing-generator fields and the first half of OTG1 through `OTG1_OTG_CRC2_DATA_B`.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It is unrelated to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation sites, or locks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- Instance prefixes such as `FMT0_`, `DPG1_`, `OPPBUF2_`, `ODM3_`, `OTG0_`, and `OTG1_` expose per-pipe/per-block copies of the same hardware layout.

Major macro families in this slice:

- `FMT0_` through `FMT3_`: output formatter controls for component clamps, dynamic expansion, stereo sync override, spatial/temporal dithering, truncation, random seeds, pixel encoding, 4:2:0 memory power, 4:2:2 edge behavior, and double-buffer update-pending state. The chunk starts after the earlier part of `FMT0_FMT_CONTROL`, so instance 0 is split across chunks.
- `DPG0_` through `DPG3_`: display pattern generator controls, ramp programming, active dimensions, two-color RGB/YCbCr values, segment offsets, and double-buffer pending status.
- `OPPBUF0_` through `OPPBUF3_`: OPP buffer active width, display segmentation, overlap pixels, pixel repetition, 3D dummy-data and vertical-space parameters, and segment-padding fields.
- `OPP_PIPE0_` through `OPP_PIPE3_`: OPP pipe clock enable/status and digital bypass controls.
- `OPP_PIPE_CRC0_` through `OPP_PIPE_CRC3_`: OPP pipe CRC enable/continuous mode, stereo/interlace mode, pixel/source selection, one-shot pending, masks, and CRC result fields.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`: top-level OPP fine-grain clock-gating and ambient-backlight-management selection controls.
- `DSCRM0_` through `DSCRM3_`: DSC forwarding selectors that route DSC output toward an OPP pipe and expose enable/power-down related fields.
- `DC_PERFMON14_*`: performance counter control, selection, enable/clear, threshold, overflow/current-value, and state fields for a DC-local perfmon block.
- `ODM0_` through `ODM3_`: OPTC/ODM input global controls, segment source selection, data format and DSC mode, bytes-per-pixel, segment/slice width, input pixel clock enable, underflow controls, memory selection, and spare registers.
- `OTG0_*`: complete timing-generator field coverage for horizontal and vertical totals, blanking, syncs, trigger A/B, force-count interrupts, stereo/interlace, position/frame counters, snapshot, vertical interrupt 0/1/2, CRC windows/results/signature masks, static-screen detection, 3D structure, global sync lock, DRR, DTO, request control, DSC start position, pipe update status, and spare fields.
- `OTG1_*`: the same timing-generator layout begins for instance 1 and runs through CRC2 data in this chunk. Later OTG1 static-screen/global/DRR fields continue in the following chunk.

Within lines 19910-22126 there are 335 distinct register names represented by paired or grouped shift/mask macros. The largest family is OTG, followed by FMT, DPG, OPPBUF, OPP pipe CRC, ODM, DC perfmon, DSCRM, and top-level OPP fields.

## Control Flow

This header has no runtime control flow. Runtime use is indirect:

1. DCN35 resource and DMUB code include `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Register-table macros such as `SR`, `SRI`, `SF`, and block-specific wrappers paste register and field tokens into names from this file.
3. Constructors populate per-block register-offset, shift, and mask tables for OPP, OPTC/timing generator, DSC/ODM routing, performance monitoring, and DMUB-accessible DCN35 registers.
4. Operational code later calls helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and wait/poll helpers. Those helpers use this chunk's shifts and masks to preserve unrelated hardware bits while programming output format, pattern generation, CRC capture, ODM/DSC routing, timing, vertical interrupts, global sync, and dynamic refresh behavior.

The macros do not encode sequencing. Modeset code still has to lock and unlock update domains, wait for double-buffer pending bits, sequence OPP/OPTC/DSC changes around blanking, and respect interrupt/status clear semantics supplied by hardware programming rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- FMT and OPPBUF registers hold per-output-pipe format state: truncation, dither mode/depth, random seeds, clamp format, pixel encoding, subsampling, active width, segmentation, and 3D/pixel repetition parameters.
- DPG registers hold test-pattern state used for diagnostics, validation, and blank-pattern programming.
- OPP pipe and OPP CRC registers hold clock/bypass state, CRC capture configuration, CRC result registers, and one-shot pending status.
- DSCRM registers hold DSC-to-OPP forwarding state, including which OPP pipe receives DSC data.
- ODM/OPTC input registers hold source-segment mapping, segment count, DSC mode, bytes-per-pixel, slice/segment width, input clock enable, memory selection, and underflow status/clear fields.
- OTG registers hold timing-generator state: programmed horizontal/vertical timings, dynamic refresh totals, trigger/interrupt masks and statuses, frame/position counters, stereo/interlace state, CRC windows/results, static-screen detection, global sync lock state, DRR windows, DTO constants, and pipe-update pending status.
- DC perfmon 14 registers hold programmable counter selection, enable, clear, threshold, current-value, overflow, and state fields.

Persistence is hardware-defined. Configuration fields usually remain until modeset reprogramming, power gating, suspend/resume, or ASIC reset. Status, pending, interrupt, clear, snapshot, CRC one-shot, and counter fields can be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated mask file does not identify access type.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which provides the matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`, which includes the generated DCN35 headers and constructs DCN35 display resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, where `dmub_srv_dcn35_regs_init()` maps generated field masks and shifts into DMUB register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn35/dcn35_opp.c`, which consume FMT, OPPBUF, OPP pipe, DPG, DSCRM, and OPP CRC field names for output-pixel-processor setup and state readback.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.h` and `dcn35_optc.c`, whose DCN35 timing-generator field lists consume the OTG/OPTC masks for CRC, update-pending, clock-gating, vertical interrupt, DRR, and timing behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_dpms.c`, which reaches the OPTC DSC programming path when enabling or disabling DSC for a stream.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_hw_sequencer.c`, which coordinates OPP/OPTC/ODM update sequencing, blanking waits, double-buffer waits, and pipe update state.

The main integration pattern is token pasting, so macro spelling is effectively a source-level ABI between generated headers and shared driver tables. Missing, renamed, or stale field names can break compilation; incorrect numeric masks can compile cleanly while corrupting runtime hardware programming.

## Risks And Edge Cases

- Generated masks are untyped constants. A wrong shift or mask can silently affect neighboring fields and show up only as display corruption, CRC mismatch, blanking failure, or timing instability.
- The chunk boundary is artificial. It begins after `FMT0_FMT_CONTROL` shifts/masks have already started in the previous chunk and ends before OTG1's later static-screen, global sync, DRR, DTO, request, DSC-start, and pipe-update fields. File-level analysis must reconcile adjacent chunks.
- FMT dither/truncation/pixel-encoding fields directly affect color depth and subsampling output. Bad masks can cause banding, incorrect RGB/YCbCr conversion behavior, or format-specific corruption.
- DPG and blank-pattern fields are used in diagnostic and transition paths. Incorrect pattern or dimension masks can make blanking/update waits misleading during ODM or pipe transitions.
- OPP pipe clock and bypass bits are power/clock-sensitive. Incorrect masks can leave an output path clock-gated, report false clock status, or bypass digital processing unexpectedly.
- OPP and OTG CRC fields are test/debug critical. Bad window, source-select, one-shot-pending, or result masks can invalidate CRC-based diagnostics and automated display validation.
- ODM/OPTC segment mapping and DSC mode fields are high-risk for wide/high-bandwidth modes. Wrong segment source, segment-count, bytes-per-pixel, slice-width, or DSC-mode masks can break ODM combine, DSC output routing, or multi-pipe timing.
- OTG timing, interrupt, global sync, DRR, and update-lock fields are sequencing-sensitive. Incorrect masks can cause missed vertical interrupts, stuck update-pending bits, invalid dynamic refresh timing, stereo/interlace regressions, or hangs in wait loops.
- Perfmon counter fields are diagnostic but side-effect-sensitive; wrong enable/clear/threshold masks can hide overflows or produce misleading performance telemetry.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN35 support enabled. Token-pasting consumers in resource, DMUB, OPP, OPTC, DSC, and timing-generator code should catch missing or renamed macros.
- Mechanically verify that every `__SHIFT` macro in this line range has the expected matching `_MASK` macro and that each mask aligns with its shift and expected field width.
- Diff the chunk against AMD's authoritative DCN 3.5.0 register database and nearby generated headers such as `dcn_3_5_1_sh_mask.h` or older DCN 3.x headers when hardware compatibility is expected.
- Exercise normal modesets across all active OPP/OTG instances, including pipe enable/disable, blank/unblank, suspend/resume, hotplug, and repeated timing changes.
- Exercise high-bandwidth and ODM/DSC paths: 2:1 or 4:1 ODM combine where supported, DSC enable/disable, native subsampled DSC formats, slice-width changes, and link DPMS transitions.
- Exercise color-output paths that depend on FMT fields: 6/8/10/12 bpc modes, temporal and spatial dithering, truncation, RGB/YCbCr, 4:2:0, and 4:2:2 output formats.
- Use CRC and debugfs-style validation where available: OPP CRC, OTG CRC windows, one-shot and continuous CRC modes, stereo/interlace CRC cases, and compare expected frame signatures.
- Monitor kernel logs, DC traces, hardware readback, and display output for underflow, stuck update-pending bits, missed vertical interrupts, CRC mismatches, black screens, link fallback, visible corruption, or timing-generator wait timeouts.

## Cross-Chunk Notes

Adjacent chunks are required for a complete file report. The previous chunk contains the beginning of `FMT0_FMT_CONTROL` and earlier output block fields. The next chunk continues OTG1 after `OTG1_OTG_CRC2_DATA_B`, including later CRC data, static-screen, global sync, DRR, DTO, DSC start, and pipe-update status fields. The merge lane should preserve that this is chunk 10 of 25 for `dcn_3_5_0_sh_mask.h`.

### subset-b-002066: lines 22127-24344

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h - subset-b-002066

## Scope

- Chunk id: `subset-b-002066`
- Source lines: 22127-24344
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h`
- Observed content: 2,218 source lines, all `#define` register field constants; 1,120 `__SHIFT` macros and 1,098 `_MASK` macros.

This chunk is generated AMD DCN 3.5.0 register field metadata. It does not define executable C, functions, structs, enums, or persistent software objects. Its interface is the preprocessor namespace of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants consumed by AMDGPU display register-access helpers.

## Purpose

The chunk publishes bit layouts for a contiguous display-controller register area that spans timing-generator state, global synchronization, memory power, performance monitoring, and DDC I2C control:

- The first region completes part of `OTG1` output timing generator field coverage, including CRC data/signature masks, static-screen control, 3D/stereo structure control, global sync lock/update status, master-update lock, GSL controls, vupdate keepout, global update controls, DRR timing, DTO, DSC start position, pipe update status, and spare register fields.
- `OTG2_*` and `OTG3_*` then define nearly complete repeated output timing generator layouts: horizontal and vertical timing totals, blanking/sync windows, triggers, count/reset controls, stereo state, snapshots, vertical interrupt controls, CRC windows/data, dynamic refresh rate fields, global update locking, clock control, vstartup/vupdate/vready status, GSL, DSC, and update-pending status.
- `GSL_SOURCE_SELECT` chooses ready and timing-sync sources for global-swap-lock coordination.
- `OPTC_CLOCK_CONTROL` and `OPTC_MISC_SPARE_REGISTER` describe shared OPTC clock/test-clock and spare-register fields.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS` define ODM memory light-sleep or power-state control/status for eight memory slices.
- `DC_PERFMON15_*` defines a display performance-monitor instance with counter event selection, count modes, state readback, report count, counter-value interrupt status/clear masks, and 32-bit low/high counter values.
- `DC_I2C_*` begins shared display DDC hardware I2C field coverage: engine control, arbitration, interrupt/status handling, DDC1-DDC5 status/speed/setup fields, transaction descriptors, indexed data FIFO access, EDID detect control, and read-request interrupt bits through the visible DDC6 ACK shift.

The macros are paired by convention: `REGISTER__FIELD__SHIFT` is the least-significant bit position and `REGISTER__FIELD_MASK` is the already-shifted mask. Register addresses come from the matching DCN 3.5.0 offset/base-index headers.

## Important APIs, Types, and Macros

There are no normal C APIs or types in this range. Important exported macro groups are:

- OTG timing and scanout programming:
  - `OTG2_OTG_H_TOTAL`, `OTG2_OTG_H_BLANK_START_END`, `OTG2_OTG_H_SYNC_A`, `OTG2_OTG_V_TOTAL`, `OTG2_OTG_V_BLANK_START_END`, and `OTG2_OTG_V_SYNC_A` have the same layout repeated for `OTG3`. These fields describe mode timing values programmed during display mode set.
  - `OTG*_OTG_CONTROL`, `OTG*_OTG_MASTER_EN`, `OTG*_OTG_COUNT_CONTROL`, `OTG*_OTG_COUNT_RESET`, `OTG*_OTG_STATUS`, and frame/HV/VF count registers expose enablement, free-run/count behavior, reset, and live timing status.
  - `OTG*_OTG_CLOCK_CONTROL`, `OPTC_CLOCK_CONTROL`, and `OTG*_OTG_H_TIMING_CNTL` expose local timing-generator clock enable/gate/reset state, test-clock selection, and horizontal timing divider mode.
- Update, lock, and interrupt coordination:
  - `OTG*_OTG_MASTER_UPDATE_LOCK`, `OTG*_OTG_VUPDATE_KEEPOUT`, and `OTG*_OTG_GLOBAL_CONTROL0` through `GLOBAL_CONTROL4` define master/global update lock windows, DIG update positions, vupdate blocking, and double-buffer lock regions.
  - `OTG*_OTG_GLOBAL_SYNC_STATUS`, `OTG*_OTG_VSTARTUP_PARAM`, `OTG*_OTG_VUPDATE_PARAM`, and `OTG*_OTG_VREADY_PARAM` define vstartup/vupdate/vready event enable, type, status, clear, and position fields.
  - `OTG*_OTG_VERTICAL_INTERRUPT0/1/2_CONTROL`, `OTG*_OTG_VERTICAL_INTERRUPT*_POSITION`, `OTG*_OTG_INTERRUPT_CONTROL`, `OTG*_OTG_V_TOTAL_INT_STATUS`, `OTG*_OTG_VSYNC_NOM_INT_STATUS`, and `OTG*_OTG_DRR_TIMING_INT_STATUS` provide event and interrupt masks/acks for vertical positions, vtotal updates, nominal vsync, and DRR timing changes.
  - `OTG*_OTG_PIPE_UPDATE_STATUS` exposes pending flip, DC register update, cursor update, and vupdate-keepout status.
- Synchronization, stereo, CRC, and diagnostics:
  - `OTG*_OTG_GSL_CONTROL`, `OTG*_OTG_GSL_WINDOW_X/Y`, `OTG*_OTG_GSL_VSYNC_GAP`, and `GSL_SOURCE_SELECT` define global-swap-lock enable, master mode, timing windows, gap detection, ready-source selection, and lock integration with master-update locks.
  - `OTG*_OTG_STEREO_CONTROL`, `OTG*_OTG_STEREO_STATUS`, `OTG*_OTG_STEREO_FORCE_NEXT_EYE`, and `OTG*_OTG_3D_STRUCTURE_CONTROL` define stereo enablement, eye select, polarity, frame count, and status.
  - `OTG*_OTG_CRC_CNTL`, CRC window registers, `OTG*_OTG_CRCn_DATA_RG/B`, and CRC signature mask registers expose scanout CRC capture, windowing, continuous/triggered behavior, and channel masks.
  - Snapshot, status-position, pixel-data-readback, spare-register, trigger A/B, and manual trigger fields support hardware diagnostics and bring-up.
- DRR, DSC, DTO, and request behavior:
  - `OTG*_OTG_V_TOTAL_MIN/MAX/MID`, `OTG*_OTG_V_TOTAL_CONTROL`, `OTG*_OTG_DRR_*`, and `OTG*_OTG_DRR_CONTROL` define dynamic refresh rate limits, trigger windows, reach ranges, and last-used vtotal readback.
  - `OTG*_OTG_M_CONST_DTO0/1` contains full-width phase/modulo fields for timing DTO programming.
  - `OTG*_OTG_DSC_START_POSITION` and `OTG*_OTG_REQUEST_CONTROL` define DSC start X/line and request mode for horizontal duplicate handling.
- Shared ODM/perfmon/I2C blocks:
  - `ODM_MEM_PWR_CTRL*` and `ODM_MEM_PWR_STATUS` expose force/disable/power-state fields for ODM memories 0-7 and unassigned/vblank power modes.
  - `DC_PERFMON15_PERFCOUNTER_CNTL`, `CNTL2`, `STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_LOW/HI`, and `PERFMON_CVALUE_LOW` configure event counting, run/stop/start selectors, counter states, report counts, interrupt clear/status, and count readback.
  - `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, `DC_I2C_DDCn_HW_STATUS`, `DC_I2C_DDCn_SPEED`, `DC_I2C_DDCn_SETUP`, `DC_I2C_TRANSACTION0-3`, `DC_I2C_DATA`, `DC_I2C_EDID_DETECT_CTRL`, and `DC_I2C_READ_REQUEST_INTERRUPT` define hardware DDC I2C ownership, setup, command sequencing, byte access, EDID detection, and interrupt/status fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is implemented by display code that includes this generated header and uses register helper macros such as `REG_UPDATE`, `REG_GET`, `REG_SET`, `REG_WAIT`, and table-driven mask/shift structures.

The hardware flows implied by this chunk include:

1. Mode-set programming writes OTG horizontal/vertical totals, blanking and sync windows, polarity, divider mode, DTO/DSC fields, then enables the timing generator and watches clock/status fields.
2. Atomic updates and page flips use master/global update lock fields, vupdate keepout windows, vertical interrupt positions, and pipe update pending bits so plane/cursor/DIG updates land at the intended frame boundary.
3. DRR and variable-refresh flows adjust vtotal min/max/mid, DRR trigger windows, vtotal reach ranges, change limits, and timing-update interrupt fields.
4. Multi-pipe or synchronized-display flows configure GSL source selection, GSL windows, gap limits, master mode, and master-update-lock GSL integration across OTG instances.
5. CRC and diagnostics flows select CRC source/window behavior, trigger or continuously capture CRCs, then read CRC data/signature/status and snapshot/pixel-readback fields.
6. ODM power management forces or disables per-memory light-sleep/power modes and validates the resulting memory state before or after display pipe use.
7. Performance monitoring selects DC perf events and counter behavior, starts/stops perfmon capture, reads low/high counters, and acknowledges counter interrupts.
8. DDC I2C transactions acquire I2C register ownership, configure selected DDC speed/setup, program up to four transaction descriptors plus indexed data bytes, assert GO, poll or handle status/interrupts, process NACK/timeout/overflow/stop conditions, and release ownership.

## State and Persistence Behavior

The macros are stateless compile-time constants. They describe MMIO register fields whose state lives in display hardware:

- Persistent configuration until reset or reprogramming: timing totals, blank/sync windows, polarity, stereo control, GSL enable/window/source selection, master update lock windows, vstartup/vupdate/vready offsets, DRR limits, DSC start, clock gating disables, ODM memory power mode bits, perfmon event/counter selection, and I2C speed/setup values.
- Transient command or handshake fields: timing count reset, snapshot trigger/update lock, manual trigger fields, interrupt clear/ack bits, GSL gap clear, static-screen interrupt clear, 3D frame-count reset, DRR timing clear, perfmon counter interrupt clear/ack, I2C GO/soft reset/status reset/send reset, transaction START/STOP, data index write, EDID detect send reset, and read-request ACK bits.
- Status and observation fields: OTG busy/clock-on, frame/HV/VF counters, live vertical/horizontal positions, stereo/field status, trigger occurred/status bits, CRC data, vstartup/vupdate/vready event/status bits, vtotal and DRR event status, pipe update pending flags, ODM memory power states, perfcounter state/active/interrupt bits, I2C hardware/software status, timeout/NACK/overflow/stop, EDID detection, and read-request interrupt state.
- The full-width spare, DTO phase/modulo, perfmon low/high, and CRC data fields are opaque hardware values from the driver point of view and persist only according to the associated hardware domain reset and update rules.

## Dependencies

This chunk depends on the generated AMDGPU/DCN register infrastructure:

- Matching register offsets and base indices in `drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`.
- DC register-access helpers and generated field tables that expect the `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming convention.
- Output pixel processor/timing-generator code in the AMD display stack, especially OPTC/OTG implementations that map these fields into per-generation `dcn*_optc` register/mask/shift tables.
- Interrupt and flip/update code that uses vstartup, vupdate, vready, vertical interrupt, vtotal, DRR timing, and pipe-update status fields.
- CRC/debug and validation paths that depend on the OTG CRC, snapshot, status-position, pixel-readback, trigger, and spare-register fields.
- Display DDC I2C consumers, such as the DCE/DCN hardware I2C implementation, which use `DC_I2C_*` fields for EDID, DDC, and sink-management transactions.
- Performance monitoring and power-management code that uses `DC_PERFMON15_*` and `ODM_MEM_PWR_*` when those hardware blocks are present in the DCN 3.5.0 ASIC.

The path is inside a Ceph client source corpus, but the file content is Linux AMDGPU display-driver register metadata and is not Ceph-specific.

## Integration Points

Important integration points are:

- Kernel mode setting and atomic commit, where OTG timing fields, update locks, and interrupt positions coordinate visible scanout changes.
- Variable refresh rate and dynamic refresh rate, where vtotal min/max/mid and DRR status/trigger fields must align with the mode and stream timing model.
- Multi-display synchronization and multi-pipe composition, where GSL and global update lock fields coordinate multiple timing generators and DIG update points.
- Display diagnostics and automated validation, where CRC capture, frame counters, snapshots, pixel readback, trigger status, and perfmon counters provide hardware evidence.
- Display power management, where ODM memory power controls and OPTC/OTG clock fields interact with suspend/resume, idle, and low-power display paths.
- EDID/DDC and sink communication, where the shared `DC_I2C_*` definitions back hardware I2C transactions on DDC1-DDC5 and read-request interrupt handling across DDC channels.

## Risks and Edge Cases

- Generated mask/shift drift silently corrupts MMIO field access. Timing, update-lock, interrupt-clear, clock/reset, ODM power, and I2C ownership fields are especially sensitive because wrong bits can cause display hangs, missed vblank events, or failed EDID reads.
- `OTG2` and `OTG3` contain large repeated layouts. A generation or copy-index mismatch can compile cleanly while programming the wrong timing generator.
- The chunk starts in the middle of `OTG1` CRC field coverage and ends in the middle of `DC_I2C_READ_REQUEST_INTERRUPT`; adjacent chunks are required for complete per-file interpretation.
- ACK/clear/reset/GO fields likely have write-one or pulse semantics. Generic read-modify-write usage can drop events or retrigger hardware if callers do not follow the register protocol.
- Multi-bit timing and window fields, such as h/v totals, blank/sync starts and ends, GSL windows, global update positions, vupdate offsets, DRR limits, DSC start positions, perfmon selectors, I2C prescale/time limits, and transaction counts require range validation before field insertion.
- Master/global update lock windows can block register updates if programmed around the wrong scan position or never released.
- GSL master/source selection and vsync-gap fields affect synchronization across pipes; incorrect programming can produce frame slips or master/slave deadlocks.
- ODM memory power force/disable fields can make downstream register accesses unreliable if software does not wait for the expected `ODM_MEM*_PWR_STATE`.
- I2C arbitration and status bits represent shared ownership with hardware/firmware users. Failure to acquire or release ownership can starve firmware pollers or corrupt DDC transactions.
- Perfmon counter interrupt/status fields can be stale unless counters are reset, clock enabled, and interrupt status acknowledged in the expected order.

## Test Signals

Useful validation signals for code using this chunk:

- Build coverage for DCN 3.5.0 display code that includes `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`, catching missing, renamed, or misgenerated macros.
- Generated consistency checks that every visible field has coherent shift/mask pairs, masks match shifts and widths, and repeated `OTG2`/`OTG3` and `DC_I2C_DDC1-5` layouts remain equivalent where expected.
- Field insert/extract tests for h/v timing values, global update windows, vertical interrupt positions, DRR limits, GSL windows, CRC channel masks, ODM memory power fields, perfmon selectors/counters, I2C transaction counts, I2C data indexes, and EDID detect controls.
- Hardware smoke tests for mode set, vblank/vupdate/vready interrupt delivery, atomic page flips, cursor updates, VRR/DRR transitions, stereo/3D modes if supported, and multi-pipe GSL synchronization.
- CRC and diagnostic tests that program CRC windows, capture CRC data, use snapshot/status-position registers, and confirm pipe-update pending bits clear after flips and cursor updates.
- Suspend/resume and low-power display tests that exercise ODM memory power states and OTG/OPTC clock control without losing timing-generator state unexpectedly.
- DDC/EDID tests across DDC1-DDC5, including NACK, timeout, overflow, repeated-start transaction descriptors, EDID detect retries, and read-request interrupt ACK/mask handling.
- Perfmon validation that selected events count, counter low/high reads are stable enough for the caller's sampling model, and counter interrupt clear/status behavior matches the expected hardware semantics.

## Chunk Boundary Notes

The first visible line is `OTG1_OTG_CRC2_DATA_B__CRC2_C_MASK`, so earlier `OTG1` CRC2 shifts and masks are in the previous chunk. The final visible line is `DC_I2C_READ_REQUEST_INTERRUPT__DC_I2C_DDC6_READ_REQUEST_ACK__SHIFT`; the DDC6 read-request mask shift and all masks for this register continue after line 24344. The merge/reconciliation lane should combine this report with adjacent chunks before producing the final per-file research document for `dcn_3_5_0_sh_mask.h`.

### subset-b-002067: lines 24345-26561

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 24345-26561

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.5.0 register shift/mask header. It contains C preprocessor constants for hardware register bitfields, not executable driver logic. The macros define bit positions and positioned masks for display I/O, hot-plug detect, performance-monitor, DisplayPort AUX, and the beginning of VPG generic packet registers.

The requested range contains 2,217 `#define` lines: 1,108 `__SHIFT` macros and 1,109 `_MASK` macros. The imbalance is caused by chunk boundaries. The range starts inside the already-open `DC_I2C_READ_REQUEST_INTERRUPT` register, where earlier DDC1-DDC6 shift fields are in the previous chunk, and ends inside `VPG0_VPG_ISRC1_2_DATA`, before the remaining byte fields and masks for that register.

The substantive hardware covered here is the display I/O service surface around DDC/I2C read-request interrupts, scratch registers, DIO memory power and link encoder selection, HPD instances 0 through 4, `DC_PERFMON16`, DP AUX instances 0 through 4, and the first VPG0 generic packet and ISRC packet data registers.

## Important Constants And Register Areas

`DC_I2C_READ_REQUEST_INTERRUPT` provides read-request status, interrupt, acknowledge, and mask bits for DDC1 through DDC6 and DDCVGA, plus global read-request acknowledge-enable and interrupt-type bits. Because the chunk begins mid-register, the visible DDC6/DDCVGA shifts must be reconciled with the earlier shifts before whole-register documentation is final.

`DIO_SCRATCH0` through `DIO_SCRATCH7` expose eight full-width 32-bit scratch registers. These are generic DIO state slots; their meaning is supplied by higher-level firmware or driver conventions rather than by this shift/mask header.

The DIO power and link-selection registers include:

- `DIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS` bits for DIGA through DIGG DisplayPort ALPM wakeup status.
- `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_CTRL2`, covering I2C and DPA-DPG light-sleep force/disable/state fields.
- `DIO_POWER_MANAGEMENT_CNTL`, with reset and all-busy-off fields.
- `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, with enable, type, status, mask, and 12-bit interval fields.
- `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL`, each selecting encoder type and HPO HDMI/DP encoder routing.

`HPD0` through `HPD4` repeat the same hot-plug-detect register layout: interrupt status, interrupt control, timing/control, fast-train delay controls, and toggle-filter delay controls. The status fields include HPD sense, delayed sense, RX interrupt status, and connect/disconnect filter timer values. The control fields include acknowledge, polarity, enable, RX interrupt acknowledge/enable, connection/RX timers, HPD enable, AUX TX delay, fast-train delay, and connect/disconnect debounce delays.

`DC_PERFMON16` defines one display performance-monitor block. It includes perfcounter control and secondary control, eight packed counter-state fields, perfmon run/report/interrupt control, interrupt-status/ack fields for counters 0 through 7, low/high value registers, and read-select fields. These macros are used to program event selection, run-enable behavior, count-off conditions, interrupt handling, and counter readback.

`DP_AUX0` through `DP_AUX4` are repeated DisplayPort AUX controller instances. For each instance the chunk defines:

- AUX enable/reset, local-side read, HPD-disconnect behavior, mode detection, HPD select, impedance calibration request, test/deglitch, and spare bits.
- Software transaction control, arbitration between software and DMCU users, software/local-side done interrupts, and GTC sync interrupt fields.
- Software and local-side status words with done/request, timeout state, timeout, overflow, HPD disconnect, partial-byte, non-AUX mode, invalid stop/start/sync, receive-no-detect, reply byte count, CP IRQ, update, and arbitration status fields.
- Software and local-side data window fields, including 8-bit data, 5-bit index, read/write, and auto-increment-disable controls.
- AUX PHY TX/RX timing controls and status readbacks, including precharge, receive windows, transition filtering, threshold allowance, timeout length, TX/RX state, and half-symbol-period fields.
- AUX GTC sync control, error thresholds, controller status, sync transaction status, and PHY wake control.

The final `VPG0` block starts video packet generator generic packet programming. It includes indexed generic packet byte access, 15 generic packet frame-update bits with matching pending bits, 15 immediate-update bits with matching pending bits, lock/conflict status, VPG GSP memory power state, and the beginning of ISRC1/2 indexed data access. The last visible register, `VPG0_VPG_ISRC1_2_DATA`, is incomplete in this chunk.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. The API surface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the field's bit position within a 32-bit MMIO register.
- `REGISTER__FIELD_MASK` gives the positioned mask for that field.
- Repeated instance prefixes such as `HPD0_`, `DP_AUX3_`, and `VPG0_` bind the field layout to a specific hardware instance.

Consumers pair these macros with matching DCN 3.5.0 register-address macros from the corresponding offset header and with AMD display register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and generated register-field lists. This header supplies bit layout only; enum meanings, legal values, access ordering, and side effects come from the hardware programming guide and caller-side DCN code.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs when AMD display code reads or writes the described MMIO registers.

The implied DDC/I2C and HPD flows are interrupt-oriented. Hardware latches read-request or hotplug status bits; the driver reads status fields, writes acknowledge bits, controls masks/enables, and uses debounce or fast-train timing fields to tune connector event handling. Incorrect acknowledge or mask handling can produce missed hotplug events, interrupt storms, or stale RX interrupt status.

The implied DP AUX flow is transactional. Driver code configures AUX control and PHY timing, arbitrates register ownership, writes indexed transaction data, starts software or local-side requests, waits for done/status bits, handles timeout and protocol error fields, and acknowledges interrupts. GTC sync fields add a secondary state machine for lock acquisition, error thresholds, retry behavior, and critical-error acknowledgement.

The implied DIO and VPG power flows are stateful hardware control flows. Light-sleep force/disable fields and memory power state readbacks must be coordinated with active display paths. VPG generic packet update controls let software request frame-bound or immediate packet updates and poll pending bits until hardware consumes them.

`DC_PERFMON16` defines a performance-monitor control flow: select events and counted values, configure start/stop/count-off behavior, enable reporting or interrupts, run the counter, then read low/high value registers and acknowledge counter interrupts.

## State And Persistence

The file itself stores no mutable state. It defines how software addresses state held in display hardware registers.

Persistent hardware state represented in this chunk includes interrupt masks and acknowledgements, DIO scratch values, memory light-sleep force/disable choices, encoder routing selections, HPD debounce/timer controls, perfmon event and run-control configuration, AUX transaction buffers and arbitration state, AUX PHY timing controls, GTC sync lock/error state, VPG generic packet bytes, VPG update-pending state, and VPG memory power state.

Most of this state persists until reset, suspend/resume reinitialization, modeset programming, or a later register update. Status and acknowledge fields are side-effect-prone: reading status does not necessarily clear it, while writing an ack bit can clear a latched event. Indexed data registers such as AUX SW/LS data and VPG generic packet data depend on an index field and optional auto-increment behavior, so the current index is also part of the effective hardware state.

## Dependencies And Integration Points

This generated header depends on the matching DCN 3.5.0 register offset header and the AMDGPU display register helper framework. The numeric values are ASIC-generation-specific and should not be mixed with other DCN versions unless the generated register database proves compatibility.

Important integration points include:

- DRM connector detection and hotplug handling through HPD status, control, timing, and interrupt fields.
- DDC/I2C and DisplayPort AUX code paths for EDID reads, DPCD access, link training, HDCP/CP IRQ processing, and sideband operations.
- DIO runtime power-management code that controls I2C and DP memory light sleep and observes memory power state.
- Display link encoder routing for DIO_LINKA-F and HPO HDMI/DP encoder selection.
- Display performance diagnostics that program `DC_PERFMON16` counters and collect low/high values.
- Video packet generator paths that load generic and ISRC packets for HDMI/DP infoframes and other stream metadata.

The repeated DP AUX and HPD layouts are especially important integration contracts. Higher-level code often indexes into per-instance register tables; token naming and field consistency across instances must remain stable for generated field-list macros and per-link code to work.

## Risks And Edge Cases

Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can direct writes to the wrong bit, causing missed HPD events, broken AUX transactions, incorrect encoder routing, bad power-state transitions, or corrupted packet updates.

Chunk boundaries create local incompleteness. The first visible register is only the tail of `DC_I2C_READ_REQUEST_INTERRUPT`, and the last visible register is only the start of `VPG0_VPG_ISRC1_2_DATA`. Whole-register validation for those two registers must include adjacent chunks.

AUX arbitration fields include aliases that intentionally share a bit position, such as `AUX_SW_USE_AUX_REG_REQ` and `AUX_SW_PENDING_USE_AUX_REG_REQ`, and similarly for DMCU ownership. Validation scripts must allow these semantic aliases instead of treating every overlapping mask as an error.

Interrupt fields combine status, mask, enable, and acknowledge bits in adjacent positions. Callers must preserve unrelated fields during read-modify-write operations and use established ack semantics; open-coded writes can accidentally clear pending events or unmask unwanted interrupts.

Indexed data windows are ordering-sensitive. Programming AUX or VPG packet bytes with the wrong index or auto-increment setting can silently write the wrong byte lane. VPG frame-update and immediate-update pending bits must be observed before assuming packet data is active.

Power and PHY timing fields affect active links. DIO/VPG memory power, AUX reset, AUX PHY receive thresholds, timeout windows, and GTC sync error thresholds can affect link training, HPD handling, EDID reads, and timing synchronization. These should be changed only through the ASIC-specific display sequences that understand hardware timing requirements.

## Test And Validation Signals

Build validation should include DCN 3.5.0 AMD display objects that include `dcn_3_5_0_sh_mask.h` and instantiate HPD, AUX, DIO, perfmon, and VPG register lists. Missing or renamed macros usually surface at compile time; wrong numeric values usually require generated-data diffing or hardware tests.

Useful generated-data checks include:

- Compare this range against the authoritative DCN 3.5.0 register database.
- Verify every complete register has matching shift and mask fields, while allowing the incomplete first and last registers.
- Diff repeated layouts across `HPD0` through `HPD4` and `DP_AUX0` through `DP_AUX4`, allowing only intentional instance prefix changes and documented aliases.
- Check masks for non-overlap within each complete register, except for explicit alias fields in AUX arbitration and interrupt-mask naming patterns.
- Cross-check matching offset-header entries for every register prefix used here.

Runtime signals include stable hotplug detection across connect/disconnect and RX interrupt events, successful DDC/EDID and DP AUX/DPCD transactions on all exposed links, clean link training without AUX timeout/overflow protocol errors, correct CP IRQ/update status handling, working perfmon counter reads and interrupts, correct VPG generic/ISRC packet updates, and no display regressions across suspend/resume, runtime power management, multi-monitor modesets, and HPD storms.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002067_research.md`. Whole-file research for `dcn_3_5_0_sh_mask.h` must merge adjacent chunks to complete `DC_I2C_READ_REQUEST_INTERRUPT` at the start and `VPG0_VPG_ISRC1_2_DATA` at the end.

### subset-b-002068: lines 26562-28781

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 26562-28781

## Scope

This chunk is a generated DCN 3.5 register bitfield header slice. It contains only preprocessor constants: `*_SHIFT` values and matching `*_MASK` values for fields in VPG, AFMT, DME, DIG/HDMI/TMDS, and DP register blocks. There are no functions, structs, enums, branches, or local storage in this range; its behavior is entirely through compile-time expansion into AMD display register accessor tables.

The range starts in the middle of the `VPG0` ISRC/MPEG payload field definitions, covers complete `AFMT0` and later `AFMT1` audio formatter field sets, `DME0` and `DME1` metadata engine fields, large `DIG0` and `DIG1` stream encoder/HDMI/TMDS field sets, a substantial `DP0` DisplayPort field set, and the beginning-to-middle of `VPG1` video packet generator fields.

## Purpose

The constants define the exact bit positions and masks used by the AMDGPU display core to read and write DCN 3.5 hardware registers. The source file mirrors the hardware register database: each macro name encodes the instance, register, field, and whether the value is a shift or mask.

Examples of covered register families:

- `VPG0_*` and `VPG1_*`: generic packet data, frame/immediate update controls, status/conflict bits, ISRC and MPEG info payload bytes, and VPG memory power state.
- `AFMT0_*` and `AFMT1_*`: HDMI/DP audio formatter programming, audio infoframes, IEC 60958 channel status, audio CRC/test ramp registers, FIFO/status bits, source selection, and AFMT memory power.
- `DME0_*` and `DME1_*`: metadata engine enablement, HUBP requestor selection, stream type, double-buffer state, missed-transmission flags, and memory power control.
- `DIG0_*` and `DIG1_*`: front-end source selection, output CRC, test patterns, FIFO controls, HDMI control/status, HDMI generic packet scheduling, audio clock recovery, global control/AVMUTE, TMDS control characters, back-end clock/reset/source selection, and AFMT clock gating.
- `DP0_*`: DisplayPort stream/link control, MSA and VBID fields, DPHY training/scrambler/FEC/CRC fields, secondary data packet controls, MST/MSE slot allocation, generic secondary packet controls 8-11, metadata transmission, ALPM/AUX-less ALPM, DSC, MSO, and double-buffer status.

## Important APIs, Types, And Macros

This chunk does not declare public C APIs, but it feeds several AMD display macro APIs:

- `SE_SF(register, field, mask_sh)` consumes names such as `DP0_DP_SEC_CNTL` and `DP_SEC_STREAM_ENABLE` to initialize stream encoder mask/shift tables.
- `SRI_ARR(register, block, id)` consumes register names to map indexed hardware instances, for example `SRI_ARR(HDMI_GENERIC_PACKET_CONTROL0, DIG, id)` in the DCN35 resource register lists.
- `REG_UPDATE`, `REG_UPDATE_N`, `REG_SET_N`, and `REG_GET` later use those tables to perform masked read-modify-write and field extraction operations.

Important field groups in this range include:

- AFMT audio send/control fields: `AFMT_AUDIO_SAMPLE_SEND`, `AFMT_AUDIO_CHANNEL_ENABLE`, `AFMT_60958_CS_UPDATE`, `AFMT_AUDIO_LAYOUT_OVRD`, `AFMT_60958_OSF_OVRD`, `AFMT_MEM_PWR_FORCE`, `AFMT_MEM_PWR_DIS`, and `AFMT_MEM_PWR_STATE`.
- VPG generic packet fields: `VPG_GENERIC_DATA_INDEX`, `VPG_GENERIC_DATA_BYTE0..3`, `VPG_GENERIC0..14_FRAME_UPDATE`, `VPG_GENERIC0..14_IMMEDIATE_UPDATE`, pending bits, conflict status/clear fields, and VPG memory power fields.
- HDMI packet fields: `HDMI_GENERIC0..14_SEND`, `HDMI_GENERIC0..14_CONT`, line-reference and line-number fields, immediate-send/pending bits, generic-packet enable double-buffer pending bits, `HDMI_DB_*`, `HDMI_ACR_*`, `HDMI_GC_AVMUTE`, and HDMI status/error fields.
- DP secondary data fields: `DP_SEC_STREAM_ENABLE`, audio packet controls (`DP_SEC_ASP_ENABLE`, `DP_SEC_ATP_ENABLE`, `DP_SEC_AIP_ENABLE`, `DP_SEC_ACM_ENABLE`), generic secondary packet enables, send/pending/deadline bits, packet framing and metadata controls, and `DP_SEC_GSP8..11_*`.
- DP link/PHY fields: stream enable/status/deferred disable, pixel format, `DP_VID_M/N`, link framing, FEC and scrambler controls, training pattern, PRBS, DPHY CRC and fast-training fields.
- DP MST/MSO/ALPM fields: MSE rate and slot allocation, MSO controls, `DP_ALPM_CNTL`, `DP_AUXLESS_ALPM_CNTL1..5`, wakeup/interrupt fields, and GSP enable double-buffer status.

## Control Flow

There is no runtime control flow in this chunk. The practical flow is compile-time and data-driven:

1. Generated macro names provide register field positions and masks.
2. DCN35 resource headers build per-instance register address lists for VPG, AFMT, stream encoder/DIG, and DP blocks.
3. Encoder, VPG, and AFMT headers build mask/shift field tables with `SE_SF`.
4. Runtime display code calls `REG_UPDATE`, `REG_SET`, or `REG_GET`; those helpers combine the register address, field mask, and shift to modify or extract a bitfield.

The duplicated `0` and `1` instance blocks in this chunk let the same runtime code operate on selected hardware instances through register-list indirection. The `DP0` field names are commonly used as the base names for mask/shift tables even when register addresses are supplied per DP instance.

## State And Persistence Behavior

The header itself has no mutable state and persists nothing. The macros describe hardware state that lives in display engine registers. Important state represented by the fields includes:

- Double-buffer and update state: `*_DB_PENDING`, `*_DB_TAKEN`, `*_DB_TAKEN_CLR`, `*_DB_LOCK`, `*_DB_DISABLE`, VPG frame/immediate update pending bits, HDMI generic packet enable pending bits, and DP GSP enable pending bits.
- Interrupt/status/ack state: HDMI error status and error ack, AFMT FIFO overflow and audio-enable-change ack, DPHY fast-training complete/ack bits, DP video stream disable interrupt/ack/mask bits, and AUX-less ALPM wakeup interrupt state.
- Power state: `AFMT_MEM_PWR_*`, `DME_MEM_PWR_*`, and `VPG_GSP_MEM_*` fields for memory power forcing, disabling, and state readback.
- Link/stream state: DP link training complete/status, DP video stream enable/status, DPHY FEC active/ready bits, MSE slot state, and ALPM state.

Several fields are hardware-latched or write-one-to-clear style by convention (`*_ACK`, `*_CLR`, `*_PENDING`, `*_TAKEN`). Callers must respect the hardware programming sequence; this header only supplies the bit encoding.

## Dependencies

Direct dependencies are purely preprocessor-level:

- The companion DCN 3.5 offset header supplies the register addresses that correspond to these masks and shifts.
- AMD display resource files include this header and map registers into block-specific register structs.
- Common AMD display register helper macros require each field to have a matching `_SHIFT` and `_MASK`.

Observed integration points in the tree include:

- `display/dc/resource/dcn35/dcn35_resource.h` uses `SRI_ARR` for `VPG_*`, `AFMT_*`, `HDMI_*`, `DP_*`, and `DME` register arrays that correspond to fields in this chunk.
- `display/dc/dcn31/dcn31_afmt.h` maps AFMT fields from `AFMT0_*` into AFMT mask/shift lists used by audio formatter code.
- `display/dc/dcn31/dcn31_vpg.h` maps VPG generic packet update/status fields.
- `display/dc/dio/dcn32/dcn32_dio_stream_encoder.h` and related DIO stream encoder headers map HDMI generic packet, DP secondary data, MSA, MSE, stream-control, and timing fields into stream encoder register tables.
- `display/dmub/src/dmub_dcn35.c` includes the same DCN 3.5 mask header for DMUB register access, though this specific chunk is mostly display stream/packet oriented rather than DMUB control oriented.

## Integration Notes

The naming pattern is the contract. For a field such as `DP0_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE`, the register helper layer expects both:

- `DP0_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE__SHIFT`
- `DP0_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE_MASK`

The mask values are unshifted hardware masks, while the shift values identify the least-significant bit of the field. Runtime helpers use them to clear, shift, and merge values into a 32-bit MMIO register. If either side is missing or mismatched, compilation or field programming fails.

The chunk also shows several extended DCN35-era capabilities: more HDMI generic packet controls up to packet 14, DP secondary packet controls for GSP8-GSP11, DP metadata transmission, ALPM/AUX-less ALPM controls, and DME metadata engine double-buffering.

## Risks

- A wrong mask or shift can silently program an adjacent hardware field, causing display link training failures, missing infoframes, audio dropouts, corrupted metadata packets, or power-state hangs.
- Instance prefix errors are high risk. `AFMT0`/`AFMT1`, `DME0`/`DME1`, and `DIG0`/`DIG1` blocks are structurally similar, so a generated value copied to the wrong instance can compile but target the wrong register encoding.
- Ack/clear fields must be used carefully. Misusing `*_ACK`, `*_CLR`, or `*_TAKEN_CLR` fields can drop hardware events or leave stale pending state.
- Packet timing fields are sensitive to blanking and line-number programming. Incorrect HDMI generic packet or DP secondary packet line/reference fields can cause deadline-missed status, missing HDR/InfoFrame metadata, or invalid audio/ACR behavior.
- Memory power control fields can affect low-power entry and exit for AFMT, VPG, and DME blocks. Incorrect force/disable/state masks can lead to register-access timing issues or blocks not waking as expected.
- Since this is generated hardware data, manual edits are especially risky. Review should compare against the authoritative register database or vendor drop rather than treating values as hand-maintained logic.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware behavior signals:

- Build coverage for DCN35 AMDGPU display code, ensuring all `SE_SF`/`SRI_ARR` references resolve and no mask/shift macro is missing.
- Register-table initialization tests or compile checks for AFMT, VPG, DIO stream encoder, and DCN35 resource headers.
- Display smoke tests on DCN 3.5 hardware for HDMI and DP: link training, mode set, stream enable/disable, suspend/resume, and hotplug.
- HDMI audio tests covering AFMT channel enable, IEC 60958 status updates, ACR programming, audio sample send, and FIFO overflow status.
- InfoFrame and metadata tests for HDMI generic packets 0-14, VPG generic packet updates, DP secondary data packets, HDR metadata transmission, and packet deadline/pending status.
- DP MST/MSO tests covering MSE rate/slot allocation, GSP enable double-buffer status, stream secondary packet scheduling, and DSC/MSO metadata if supported by the target platform.
- Power-management tests for AFMT/VPG/DME memory power fields and DP ALPM/AUX-less ALPM transitions, including wakeup interrupt status/clear behavior.
- CRC/test-pattern diagnostics using DIG output CRC, AFMT audio CRC, DPHY CRC, PRBS, and TMDS/DIG test pattern fields.

### subset-b-002069: lines 28782-30999

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 28782-30999

## Purpose

This chunk is generated AMD DCN 3.5.0 shift/mask register-field metadata. It contains preprocessor constants only; there are no executable C functions, structs, enums, storage objects, branches, locks, allocations, or direct MMIO operations. Each visible field is represented by a bit-position macro named `<REGISTER>__<FIELD>__SHIFT` and a bit-isolation macro named `<REGISTER>__<FIELD>_MASK`.

The requested range covers stream-output field definitions for the end of `DIG1`, the complete visible `DIG2`/`DP1`-centered stream-encoder/link slice, and the beginning of `DP2`. It starts mid-register with `DIG1_HDMI_GENERIC_PACKET_CONTROL8__HDMI_GENERIC11_LINE_MASK`, then proceeds through DIG/HDMI/TMDS fields, DisplayPort stream/link fields, VPG2 packet-generator fields, AFMT2 audio-formatter fields, and DME2 metadata-engine fields. It ends mid-register at `DP2_DP_MSA_TIMING_PARAM2__DP_MSA_VSTART_MASK`; the matching `DP_MSA_HSTART_MASK` is on the next line outside this chunk.

The range has 2,228 `#define` lines: 1,109 `__SHIFT` macros and 1,119 `_MASK` macros. The count is intentionally imbalanced because both boundaries split field pairs. Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no APIs in the function-call sense. The public interface is the generated macro namespace consumed by AMDGPU Display Core register helpers:

- `<REGISTER>__<FIELD>__SHIFT`: field bit offset for packing or extracting values.
- `<REGISTER>__<FIELD>_MASK`: field mask for preserving, clearing, or extracting bits during read-modify-write operations.

Major macro families in this chunk are:

- `DIG1_*`: the tail of the `DIG1` HDMI/TMDS stream-encoder field set. It includes HDMI generic-packet line selection, generic-packet double-buffer pending flags, HDMI double-buffer control, HDMI ACR `CTS`/`N` values for 32/44.1/48 kHz families and readback status, AFMT audio clock gating, DIG back-end source/HPD routing, TMDS sync/control-character generation, DC balancer controls, TMDS control-bit generation, and DIG type/version.
- `DP1_*`: a broad DisplayPort instance-1 field set. It covers link status/training completion, pixel format, MSA colorimetry/misc/timing/VBID fields, video stream enable/status/defer/change keepout, steer FIFO and TU overflow, DPHY internal scrambler controls, video `M/N` generation, link framing, video interrupts, DPHY training pattern/lane control/symbol/8b10b/PRBS/scrambler/CRC/fast-training controls, secondary-data packet controls, audio `M/N`, MST payload and slot-allocation controls, MSO controls, DSC enablement, GSP packet controls, metadata transmission, and AUX-less ALPM controls.
- `VPG2_*`: Video Packet Generator instance-2 fields for generic-packet access/data, MPEG info packets, ISRC data access, generic status, memory power, and GSP frame/immediate update controls for packet slots 0 through 11.
- `AFMT2_*`: Audio Formatter instance-2 fields for VBI and audio packet control, audio info words, IEC 60958 channel-status words, audio ramp control, audio CRC control/results, status/interrupt/ack/mask fields, audio-source selection, infoframe control, and AFMT memory-power state.
- `DME2_*`: Display Metadata Engine instance-2 fields for metadata engine enable/update/reset, interrupt flag/ack/mask, payload select, compression and priority controls, virtual start address, buffer mode, stall controls, stutter mode, memory power controls, and memory shutdown/deep-sleep status.
- `DIG2_*`: the next stream-encoder instance, including DIG front-end/back-end control, clock/test patterns, FIFO controls, output CRC, HDMI control/status/metadata/audio/ACR/generic-packet fields, HDMI double-buffering, TMDS controls, and DIG version.
- `DP2_*`: the start of DisplayPort instance 2, structurally mirroring the `DP1` families from link control through DPHY, secondary-data packet, MST/MSE, and early MSA timing fields. The chunk stops before the complete `DP2` timing/MSO tail.

The field layouts are highly repetitive. `DIG2` mirrors the earlier DIG stream-encoder pattern, and `DP2` mirrors the `DP1` DisplayPort pattern. `VPG2`, `AFMT2`, and `DME2` are instance-specific copies of packet/audio/metadata helper blocks used by stream encoder instance 2.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by AMDGPU Display Core and DMUB-facing code:

1. DCN 3.5 code includes `dcn_3_5_0_offset.h` with this `dcn_3_5_0_sh_mask.h` companion.
2. Resource, DIO, stream-encoder, link-encoder, IRQ, and DMUB macros token-paste register and field names into per-block register tables.
3. Driver objects store offsets, masks, and shifts for the relevant hardware instance.
4. Modeset, link-training, audio, packet, metadata, hotplug, suspend/resume, and debug paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and polling helpers; those helpers use these constants to touch only the requested MMIO fields.

The constants do not encode ordering. Consumers must still sequence stream enable/disable, clock and memory-power transitions, double-buffer updates, HDMI audio clock regeneration, DP link training, DPHY pattern generation, MST slot allocation, secondary-data packet transmission, interrupt acknowledgement, and link/audio power transitions according to hardware rules.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO-backed DCN 3.5 display hardware state:

- HDMI/DIG state for generic-packet line placement, double-buffer pending/taken bits, HDMI ACR values, AFMT clock enable/status, DIG source/HPD routing, TMDS control symbols, DC balancing, FIFO/test-pattern state, output CRC, metadata packets, and HDMI status/error bits.
- DisplayPort video state for link-training completion/status, stream enable/status, pixel encoding/depth, MSA timing/colorimetry/VBID, video `M/N`, steer FIFO/TU sizing, framing, MSO/DSC, and stream-disable interrupts.
- DisplayPort PHY and validation state for lane control, training-pattern selection, DPHY symbols, 8b10b reset/disparity, PRBS generation, scrambler controls, CRC capture and MST CRC phase status, HBR2 pattern control, fast-training state/ack/mask, and AUX-less ALPM wake controls.
- Secondary-data and audio packet state for DP SEC stream/ASP/ATP/AIP/ACM/GSP/MPG enables, packet line references, send/pending/deadline flags, framing widths, audio mute/status, audio `M/N` and readback values, timestamp mode, ASP coding/version/channel-count override, metadata packets, and HDMI generic packets.
- MST/MSE state for payload rate control, rate-update pending, stream allocation table source/slot counts and status, 16-MTP keepout, link frame/line timing, blank/timestamp/zero-encoder controls, and slot allocation update.
- `VPG2`, `AFMT2`, and `DME2` state for video metadata packet data, ISRC/MPEG info, generic packet status, audio packet controls, IEC 60958 channel status, audio CRC/status interrupts, audio source selection, infoframe controls, metadata-engine payload buffers, and block memory power.

Persistence is hardware-defined. Configuration fields generally retain values until reprogrammed, reset, power-gated, or restored after suspend/resume. Status, interrupt, pending, ack, clear, CRC, FIFO, packet-send, and training fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while related clocks and power domains are enabled. This generated header does not record access type, reset value, side effects, or polling requirements.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DCN 3.5 register database and with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which provides matching MMIO register offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c` and `dmub_dcn35.h`, which include the generated headers and build DMUB register/field tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c` and related resource headers, which include this mask header for DCN35 resource construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_stream_encoder.h`, whose stream-encoder field lists reference HDMI generic packets, HDMI ACR fields, DP SEC fields, AFMT clock fields, FIFO fields, metadata packet fields, and stream mapper fields through token-pasted `SE_SF(...)` macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_link_encoder.h`, whose link-encoder field lists reference DIG back-end, TMDS, and DP secondary-data fields through `LE_SF(...)` macros.

Functional integration points include HDMI/DP stream encoder programming, DP link encoder setup, DP secondary-data packet scheduling, HDMI generic/info/metadata packet generation, audio packet generation, DP MST/MSO/DSC support, DPHY validation/training, output CRC diagnostics, VPG/AFMT/DME packet-memory power management, and DMUB-mediated register access.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while touching an adjacent hardware field, causing display blanking, audio loss, link-training failure, packet corruption, or stuck interrupts.
- The range is boundary-partial. The first line is only the mask for `DIG1_HDMI_GENERIC_PACKET_CONTROL8__HDMI_GENERIC11_LINE`, whose shift is above the chunk. The last line omits `DP2_DP_MSA_TIMING_PARAM2__DP_MSA_HSTART_MASK`, which appears immediately after the chunk. Several apparent shift/mask count imbalances are caused by these artificial boundaries and by fields whose names end in `MASK`.
- Repeated instances are copy-sensitive. `DP1` and `DP2`, plus `DIG1`/`DIG2` and `VPG2`/`AFMT2`/`DME2`, have similar layouts but instance-specific names; a generator or manual edit error may affect only one connector, link, stream, or packet engine.
- Side-effect fields are mixed with configuration fields. Interrupt flags, ack bits, masks, pending bits, send triggers, CRC valid bits, training-start bits, reset bits, and memory-power controls require access semantics that are not visible in this header.
- DP link and DPHY fields are timing-sensitive. Incorrect training pattern, scrambler, PRBS, 8b10b disparity, fast-training, lane-count, or CRC fields can produce failures that only appear at certain rates, lane counts, MST topologies, or after resume.
- Packet scheduling fields are interoperability-sensitive. Bad HDMI generic packet line placement, DP SEC/GSP send/deadline fields, metadata packet controls, or audio packet controls can cause missing HDR metadata, bad infoframes, audio mutes, packet collisions, or receiver-specific failures.
- MST/MSO/MSE fields depend on external allocation logic. Incorrect rate, slot-count, SAT update, keepout, or status handling can break multi-stream transport while single-stream DP continues to work.
- Memory-power and clock fields in AFMT/VPG/DME/DIG blocks can make later register writes ineffective if consumers program packet or audio registers while the block is powered down or clock-gated.

## Test Signals

Useful validation combines generated-header checks with DCN 3.5 hardware behavior:

- Build AMDGPU Display Core with DCN35 enabled. Missing or renamed fields should fail in DIO stream/link encoder, resource, IRQ, DMUB, and register-table construction paths.
- Mechanically compare lines 28782-30999 against a regenerated AMD DCN 3.5.0 register database. Account for the known boundary exceptions at `DIG1_HDMI_GENERIC_PACKET_CONTROL8__HDMI_GENERIC11_LINE` and `DP2_DP_MSA_TIMING_PARAM2__DP_MSA_HSTART`.
- Cross-check this range against `dcn_3_5_0_offset.h` so every register family used here has a matching offset/base-index entry for the same instance.
- Exercise HDMI on the affected DIG instances: modesets, generic/info/metadata packet updates, ACR programming, audio playback, AV mute, TMDS modes, deep color, output CRC, hotplug, suspend/resume, and packet double-buffer updates.
- Exercise DP on instances corresponding to `DP1` and `DP2`: link training, rate/lane changes, pixel-format changes, MSA timing programming, stream enable/disable, DSC/MSO where supported, MST payload allocation, and AUX-less ALPM wake paths.
- Validate DP secondary-data and audio behavior with audio playback, metadata/HDR packet changes, GSP sends on fixed and any-line modes, packet collision/deadline status, audio mute/status, and `M/N` readback checks.
- Validate DPHY diagnostic paths with training patterns, PRBS/scrambler settings, CRC capture, MST CRC phase status, HBR2 pattern controls, and fast-training start/complete/ack behavior.
- Monitor kernel logs, display diagnostics, and sink behavior for link-training timeouts, black screens, FIFO/TU overflow, CRC mismatches, metadata loss, audio dropouts, stuck packet pending bits, interrupt storms, memory-power timeouts, and resume-only failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of the `DIG1` stream-encoder field group, including the shift half of the first visible line here. Later chunks continue `DP2` MSA timing, MSO, DSC, GSP, metadata, AUX-less ALPM, and subsequent DCN 3.5 register families. The final per-file research document should merge adjacent chunks before making whole-file claims about every `DIG`, `DP`, `VPG`, `AFMT`, or `DME` instance.

### subset-b-002070: lines 31000-33217

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 31000-33217

## Purpose

This chunk is a middle slice of AMD's generated DCN 3.5.0 shift/mask register-field header. It contains no executable C code; it exports preprocessor constants that encode bit positions and masks for display, DisplayPort, HDMI, video-packet-generator, audio-format, and related DCN hardware registers. Runtime AMDGPU display code combines these `*_SHIFT` and `*_MASK` definitions with the matching `dcn_3_5_0_offset.h` register offsets to build register tables and to perform field-level MMIO read, write, and read-modify-write operations.

The requested range contains 2,218 `#define` entries: 1,110 `__SHIFT` macros and 1,108 `_MASK` macros. The imbalance is caused by artificial chunk boundaries. Line 31000 is only the mask half of `DP2_DP_MSA_TIMING_PARAM2__DP_MSA_HSTART`, whose shift appears in the previous chunk, and lines 33215-33217 start `AFMT4_AFMT_AUDIO_PACKET_CONTROL2` with three shift definitions whose remaining shifts and masks continue in the next chunk.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata rather than distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locks, or includes in this slice. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, set, preserve, or test that field.

The main register families in this range are:

- `DP2_*`: the tail of the DisplayPort instance 2 register-field layout, covering MSA timing parameters, MSO secondary stream controls, DSC mode, secondary-data-packet send/status controls, generic SDP line numbers, double-buffer status, main-link ALPM and auxless ALPM controls, GSP8-GSP11 controls, and GSP double-buffer pending status.
- `VPG3_*`: video packet generator instance 3 fields for generic packet data indexing and data bytes, frame-update and immediate-update triggers/pending bits for generic packets 0-14, generic lock/conflict status, memory light-sleep controls, ISRC data access, and MPEG infoframe payload bytes.
- `AFMT3_*`: audio formatter instance 3 fields for VBI/audio packet controls, audio infoframe words, IEC 60958 channel-status words, audio CRC control/result, ramp-test generation, status flags, source control, and formatter memory power state.
- `DME3_*`: display micro-engine or metadata-engine fields for control and memory-control programming, including clock gating, mode, reset, generic packet memory selection, and address/data access.
- `DIG3_*`: digital encoder instance 3 fields for front-end controls, CRC/test-pattern generation, FIFO controls, HDMI metadata/control/status, HDMI audio clock regeneration, HDMI generic-packet scheduling, HDMI double-buffer controls, ACR values/status, backend controls, TMDS control characters, DC-balance controls, generated TMDS control bits, and version fields.
- `DP3_*`: full DisplayPort instance 3 coverage in this chunk. It includes link control, pixel format, colorimetry, stream enable/status, FIFO steering, MSA miscellaneous/timing fields, DPHY controls and training/test fields, video M/N generation, link framing, HBR2 pattern, VBID/MSA positioning, stream-disable interrupt bits, DPHY CRC and MST CRC fields, fast-training controls/status, secondary-data-packet controls, audio M/N fields, MST MSE rate and slot-allocation tables/status, DP DB controls, metadata transmission, ALPM/auxless ALPM controls, GSP8-GSP11 controls, and MSO/DSC fields.
- `VPG4_*`: the beginning of video packet generator instance 4, repeating the same generic packet, frame-update, immediate-update, status, memory power, ISRC, and MPEG infoframe field layout as `VPG3`.
- `AFMT4_*`: the beginning of audio formatter instance 4. This chunk includes VBI packet control and only the first three `AFMT_AUDIO_PACKET_CONTROL2` shift definitions before the line boundary.

The repeated instance names matter. `VPG3`/`AFMT3`/`DIG3`/`DP3` are one display pipeline/link instance, while `VPG4`/`AFMT4` starts the next instance. Copying a mask from one numbered block to another only works where the generated register database intentionally kept the same bit layout.

## Control Flow

This header has no runtime control flow. The practical control flow belongs to consumers in the AMDGPU display stack:

1. DCN 3.5 display code includes the matching offset and shift/mask headers.
2. Register-list macros token-paste symbolic register and field names into per-block register tables.
3. Block constructors for stream encoders, link encoders, audio/AFMT/VPG paths, DMUB services, IRQ handling, and related DCN resources store those tables for the correct hardware instance.
4. Runtime paths invoke register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers use the constants in this header to pack, extract, or preserve individual MMIO fields.

The macros do not encode ordering. Callers must still sequence link training, stream enable/disable, packet updates, HDMI/DP audio setup, MST allocation, DSC/MSO programming, ALPM entry/exit, interrupt acknowledgement, double-buffer commits, and power transitions according to hardware rules.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes fields in DCN 3.5.0 hardware registers. The state represented by these masks includes:

- DisplayPort link and stream state: link enable, enhanced framing, VBID/MSA placement, MSA timing totals/starts/sync widths, pixel format, colorimetry, stream enable, FIFO/TU sizing, video M/N, DSC mode, and MSO secondary stream enablement.
- DPHY and training state: FEC enable/status, scrambler controls, training-pattern selection, programmed symbols, PRBS settings, PHY CRC capture, MST CRC slot ranges/status, fast-training start/status/interrupt-like completion fields, HBR2 pattern controls, and low-power ALPM timing.
- Secondary-data-packet state: ASP/ATP/AIP/ACM/MPG/ISRC/GSP enables, GSP send requests, pending/active/deadline-missed bits, per-GSP line numbers, double-buffer pending status, metadata-packet enable/line fields, and collision/audio-mute status.
- HDMI and TMDS state: HDMI control/status, scrambling, deep color, AVMUTE, audio packet delay, ACR CTS/N values and readback status, VBI/infoframe/generic-packet scheduling, HDMI generic packet immediate sends, HDMI double-buffer lock/taken/pending fields, TMDS control-character generation, DC balancing, and backend enable/status fields.
- Audio/VPG state: generic packet payload bytes, frame and immediate update requests, update-pending status, generic packet lock/conflict status, ISRC and MPEG data words, AFMT audio infoframe fields, IEC 60958 channel-status fields, HBR/channel enable/layout overrides, audio CRC controls/results, ramp-test controls, audio enable/status bits, and formatter/VPG memory power settings.
- MST state: MSE rate numerator/denominator fields, SAT source/slot-count entries and status readbacks, SAT update triggers, link timing, blank-code/timestamp/zero-encoder controls, and keepout behavior.

Persistence is hardware-defined. Configuration fields normally persist until a modeset, stream teardown, register reprogramming, power gating, suspend/resume, GPU reset, or ASIC reset. Status, pending, clear, ack, and interrupt fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the relevant display/audio/link clocks and power domains are active. This generated header does not record those access semantics.

## Dependencies And Integration Points

This slice depends on AMD's generated DCN 3.5.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which supplies the matching register offsets.
- Adjacent chunks of `dcn_3_5_0_sh_mask.h`, because this range starts with a mask whose shift is in the previous chunk and ends inside `AFMT4_AFMT_AUDIO_PACKET_CONTROL2`.
- DCN 3.5 display block register-list macros that pair symbolic register names, fields, offsets, shifts, and masks for the correct pipeline instance.
- Stream encoder, link, DIO/audio, VPG/AFMT, HDMI, DP, MST, DSC/MSO, ALPM, IRQ, and DMUB service code that programs these fields through AMD display register helpers.

Behaviorally, this chunk integrates with HDMI/DisplayPort output bring-up, DP link training and diagnostics, MST bandwidth/slot allocation, secondary-data-packet transmission, HDR/vendor/generic packet updates, HDMI audio and infoframe emission, DP audio timestamping, DSC/MSO enablement, low-power link entry/exit, and display interrupt/status reporting.

## Risks And Edge Cases

- The constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while touching the wrong MMIO bits.
- The range is generated metadata. Manual edits can desynchronize the header from silicon documentation, the matching offset header, firmware assumptions, and other generated DCN versions.
- The chunk boundary is not a semantic boundary. `DP2_DP_MSA_TIMING_PARAM2__DP_MSA_HSTART` is split from its shift, and `AFMT4_AFMT_AUDIO_PACKET_CONTROL2` is split from most of its fields and masks.
- Instance repetition hides local errors. `DP2` and `DP3` have very similar field layouts, but a single instance-specific generator error could affect only one link.
- Status, clear, mask, ack, pending, active, and taken bits are easy to confuse. Using a status mask as a clear mask, or clearing a sticky field at the wrong time, can create missed interrupts, stuck pending bits, packet-update failures, or repeated IRQs.
- HDMI/DP packet timing fields are line/frame sensitive. Incorrect line numbers, immediate-update bits, double-buffer-disable bits, or pending polling can emit stale metadata, tear infoframes across frames, or miss audio/video packet deadlines.
- DPHY, FEC, training, ALPM, and fast-training fields are link-stability sensitive. Wrong masks can cause training failures, intermittent link loss, resume failures, or invalid low-power transitions.
- Audio and IEC 60958 fields are interoperability sensitive. Incorrect AFMT masks can produce silent HDMI/DP audio, wrong channel layout, wrong sample-rate metadata, bad HBR behavior, or receiver-specific failures.
- MST MSE/SAT fields affect bandwidth allocation. Bad slot-count/source masks can corrupt multi-stream scheduling without necessarily breaking single-stream DP validation.

## Test Signals

Useful validation for this chunk combines generated-header checks and hardware behavior:

- Build AMDGPU display support with DCN 3.5 enabled. Missing or renamed macros should fail in the DCN 3.5 register-table construction paths that reference these fields.
- Mechanically verify `__SHIFT`/`_MASK` pairing for lines 31000-33217 while allowing the two expected boundary exceptions: the first-line `DP2_DP_MSA_TIMING_PARAM2__DP_MSA_HSTART_MASK` and the partial `AFMT4_AFMT_AUDIO_PACKET_CONTROL2` group at the end.
- Diff this range against AMD's authoritative DCN 3.5.0 register source and nearby generated headers such as `dcn_3_5_1_sh_mask.h` where field layouts are expected to remain compatible.
- Exercise DP instance 3 and DP instance 2 paths on matching hardware: link training, stream enable/disable, MSA programming, DSC, MSO, MST, FEC, fast training, PHY CRC diagnostics, and suspend/resume.
- Exercise HDMI/DIG instance 3: scrambling, deep color, AVMUTE, ACR programming/readback, generic packet sends, infoframes, TMDS control patterns, CRC/test patterns, and double-buffer update behavior.
- Validate VPG/AFMT packet paths with HDR/vendor/generic packets, ISRC/MPEG packets, audio infoframes, IEC 60958 metadata, HBR and multichannel audio, and audio CRC/ramp diagnostics.
- Watch kernel logs and hardware traces for missed stream-disable interrupts, stuck DB pending/taken bits, GSP deadline misses, ALPM wake failures, MST slot allocation errors, stale metadata packets after modeset, silent audio after hotplug, and resume-only link or audio failures.

## Cross-Chunk Notes

This chunk continues the `DP2` register block from the prior chunk, contains a complete `VPG3`/`AFMT3`/`DME3`/`DIG3`/`DP3` middle region, and starts `VPG4`/`AFMT4`. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.5.0 registers or all display/audio/link instances.

### subset-b-002071: lines 33218-35435

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 33218-35435

## Purpose

This chunk is a generated AMD DCN 3.5.0 shift/mask register-field slice. It has no executable C logic; it exports preprocessor constants that describe bit positions and bit masks for MMIO register fields in display, audio, DisplayPort, HDMI/TMDS, metadata, GPIO, AUX/DDC, HPD, UNIPHY, and DCIO blocks. AMDGPU display code combines these constants with matching offsets from `dcn_3_5_0_offset.h` so register-helper macros can pack, update, or extract individual hardware fields without hard-coding numeric bit layouts in handwritten driver code.

The requested range contains 2,218 `#define` lines: 1,117 `__SHIFT` macros and 1,101 `_MASK` macros. The count mismatch is caused by chunk boundaries, not by a complete in-range field mismatch. The range starts after three `AFMT4_AFMT_AUDIO_PACKET_CONTROL2` shifts, so their masks are present here but their shifts are in the previous chunk. It ends after `DC_GPIO_AUX_CTRL_1` shifts and before the corresponding masks for 19 AUX/I2C/DDCVGA fields, which continue in the next chunk.

Although the repository root is a `ceph-client` source tree mirror, this file belongs to the AMDGPU display driver. It is hardware metadata for AMD display silicon, not distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct register accesses in this chunk. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the field mask used by AMD display helpers such as `FD_SHIFT`, `FD_MASK`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and macro-generated register-table initializers.

The major macro families in this range are:

- `AFMT4_*`: audio formatter instance 4 fields for audio infoframes, IEC 60958 channel status, audio CRC, test ramps, FIFO overflow/status ack bits, audio sample send, channel swap, channel enablement, DP audio stream ID, HBR override, audio source select, and AFMT memory power control.
- `DME4_*`: display metadata engine instance 4 controls for HUBP requestor ID, metadata engine enable, stream type, double-buffer pending/taken state, clear bits, DB disable, transmission-missed status, and DME memory power controls.
- `DIG4_*`: digital frontend/backend, HDMI, AFMT clock, and TMDS fields for source selection, stereosync, FIFO/output CRC/test pattern support, HDMI control, VBI/audio/infoframe/metadata packet control, generic packet send modes, immediate-send pending state, generic packet line numbers, HDMI double-buffer status/locking, HDMI ACR CTS/N values, DIG backend mapping, TMDS control characters, sync patterns, DC balancer controls, and control-bit generation.
- `DP4_*`: DisplayPort instance 4 fields for link status, pixel format, MSA colorimetry/timing, stream enable/defer/status, steer FIFO, video timing, VBID/MSA misc values, vid M/N, DPHY controls, training patterns, PRBS/scrambler/CRC, secondary data packet controls, audio M/N, timestamping, MST/MSE allocation tables, MSO routing, DSC mode, GSP packet controls, DP double-buffering, metadata packet transmission, and ALPM/AUX-less ALPM controls.
- `UNIPHYA_*` through `UNIPHYE_*`: link and channel crossbar controls for UNIPHY output routing. A/B/C include `LINK_CNTL` and `CHANNEL_XBAR_CNTL`; D/E in this range include channel crossbar controls.
- `DCIO_*`, `DC_PINSTRAPS`, and `INTERCEPT_STATE`: clock source selection, write-command delay, spare fields, pinstrap status, intercept status for PWRSEQ/DPCS units, pattern generator enable/data, backlight PWM frame-start display selection, genlock/swaplock GSL pad controls, and soft-reset fields for UNIPHY, DSYNC, and PWRSEQ blocks.
- `DC_GPIO_*` and `PHY_AUX_CNTL`: generic GPIO, genlock, DDC1-5, DDCVGA, HPD, PWRSEQ, pad-strength, TX12, AUX pad wake/RX select, and AUX control fields for display connector sideband, hotplug, backlight, generic pins, and AUX/I2C electrical behavior.

Several layouts are mechanically repeated. HDMI generic packet controls cover packet slots 0-14 with send/continuous/line-reference/update-lock and immediate-send/pending bits. DP secondary-data controls cover ASP, ATP, AIP, ACM, GSP0-11, MPG, ISRC, audio mute, line scheduling, DB gating, active/idle status, and deadline-missed flags. GPIO DDC registers repeat the same mask/A/EN/Y shape for DDC1 through DDC5 and DDCVGA.

## Control Flow

This header has no runtime control flow. Runtime behavior is created by consumers that include the generated offsets and shifts/masks:

1. DCN 3.5 modules include `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Register-list macros token-paste register and field names into offset, shift, and mask tables. For example, `dmub_dcn35.c` initializes `regs->mask.reg__field` with `FD_MASK(reg, field)` and `regs->shift.reg__field` with `FD_SHIFT(reg, field)`.
3. Display block constructors hand those tables to register helpers for DMUB, link encoders, GPIO/DDC, IRQ, audio/stream encoder, and other DCN components.
4. Runtime code calls helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`. These helpers use the numeric masks and shifts from this header to preserve unrelated bits during read-modify-write operations and to decode status fields.

The sequencing rules are not encoded here. The handwritten display driver remains responsible for correct ordering around HDMI/DP stream enablement, link training, infoframe or secondary packet updates, double-buffer commit/taken waits, FIFO resets, CRC capture, audio setup, DDC/AUX routing, HPD handling, soft reset assertion/deassertion, power gating, and suspend/resume restore.

## State And Persistence Behavior

The chunk persists no software state by itself. It describes mutable hardware state in DCN 3.5 registers:

- AFMT state includes audio infoframe payload fields, IEC 60958 channel-status values, audio packet send/override controls, FIFO overflow/acknowledgement flags, audio enable and HBR status, test ramp controls, CRC start/result state, selected audio source, and AFMT memory power state.
- DME state includes metadata engine enablement, stream type, DB pending/taken/disable/clear bits, missed-transmission status/clear bits, and low-power memory state.
- DIG and HDMI/TMDS state includes selected frontend/backend routing, FIFO and test-pattern controls, HDMI deep-color/pixel-repetition/packet mode fields, metadata and generic-packet scheduling, ACR N/CTS values, HDMI/vertical-update DB state, AFMT audio clock gating, TMDS sync/control/DC-balance generation, and encoder type.
- DP state includes link-training completion/status, lane count, pixel encoding/depth, stream enable/status/deferred disable, video timing, DPHY training/scrambling/CRC, MSA timing values, secondary packet framing and GSP scheduling, audio M/N values, MST/MSE slot allocations, MSO secondary-stream packet enables, DSC mode, metadata packet line scheduling, and ALPM/AUX-less ALPM counters and enables.
- DCIO, UNIPHY, and GPIO state includes output lane/link routing, channel crossbar mapping, resets, pinstrap-observed configuration, intercept status, pattern generation, PWM frame-start association, genlock/swaplock pad selections, generic GPIO drive/read/enable/mask state, DDC/AUX mode and pull-down behavior, HPD enable/sample/read state, pad strength, and AUX/I2C comparator or bias configuration.

Persistence semantics are hardware-defined. Some fields are latched configuration until the next modeset, power transition, driver reset, or ASIC reset. Some are read-only status, write-one-to-clear acknowledgement bits, self-clearing update bits, sticky fault bits, or double-buffer handshakes. This generated header does not mark access semantics, clock-domain requirements, reset defaults, or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DCN 3.5.0 register database and with the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h` supplies matching MMIO offsets and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c` directly includes this header and uses `FD_MASK`/`FD_SHIFT` to populate DCN35 DMUB register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c` includes this header for DCN35 interrupt register definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h` shows the `SF_DDC(...)` pattern that consumes `DC_GPIO_DDC1_MASK` fields such as DDC data/clock pull-down and AUX pad mode.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.h` and related link-encoder headers show the `LE_SF(...)` pattern that consumes fields such as `DCIO_SOFT_RESET__UNIPHYA_SOFT_RESET`.

The main behavioral integration points from this exact slice are display link and connector operation. AFMT/DIG/DP fields affect HDMI/DP audio and packet transmission. DP DPHY and stream fields affect link training and video transport. DME and DP metadata fields affect HDR or other metadata packet delivery. DCIO/UNIPHY fields affect physical routing and reset. GPIO/DDC/AUX/HPD fields affect monitor discovery, EDID reads, DisplayPort AUX transactions, hotplug detection, panel/backlight signaling, and sideband electrical configuration.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile successfully while writing the wrong MMIO bit or preserving the wrong adjacent field.
- The file is generated. Manual edits can diverge from the authoritative AMD register database, firmware expectations, silicon documentation, and the matching `dcn_3_5_0_offset.h` layout.
- Repeated HDMI generic packet, DP GSP/MSE/MSO, DDC, HPD, and UNIPHY families are vulnerable to instance-specific generator or copy errors. One connector, packet slot, or stream working does not prove the repeated siblings are correct.
- This chunk starts and ends mid-family. The first three `AFMT4_AFMT_AUDIO_PACKET_CONTROL2` shifts are outside this chunk, and the `DC_GPIO_AUX_CTRL_1` masks for 19 fields are outside this chunk. Whole-register conclusions need adjacent chunks.
- Double-buffer and pending/taken fields are sequencing-sensitive. Confusing pending, taken, clear, lock, disable, or update-lock fields can cause stale packets, lost metadata, delayed updates, or waits that never complete.
- Audio fields are interoperability-sensitive. Incorrect AFMT channel enablement, IEC 60958 status, audio packet layout, HBR override, ACR N/CTS, or DP secondary audio M/N fields can cause silent HDMI/DP audio, wrong sample-rate reporting, channel mapping failures, or receiver-specific behavior.
- DisplayPort transport fields are timing-sensitive. Incorrect MSA timing, VBID, DPHY training, scrambling, CRC, MSE slot allocation, MSO enablement, DSC mode, or ALPM control can produce link training failures, blank screens, MST bandwidth errors, or resume-only failures.
- GPIO, DDC, AUX, and HPD fields can affect physical pins. Wrong masks for pull-down, drive enable, pad mode, polarity, slew, strength, comparator, bias, or RX selection can break EDID/AUX communication, hotplug detection, backlight control, or board-specific connector routing.
- Reset and power fields can have broad blast radius. Incorrect `DCIO_SOFT_RESET`, AFMT/DME memory power, or clock-control bits can leave PHYs, DSYNC, PWRSEQ, audio, or packet engines inaccessible until a larger display reset.

## Test Signals

Useful validation combines build-time generated-header checks with hardware tests:

- Build AMDGPU display support with DCN 3.5 enabled. Missing or renamed macros should fail in DCN35 DMUB, IRQ, link encoder, GPIO/DDC, or stream/audio register-table initialization.
- Mechanically verify in this line range that all in-range complete fields have matching `__SHIFT` and `_MASK` values, while accounting for the three `AFMT4_AFMT_AUDIO_PACKET_CONTROL2` masks whose shifts are just before line 33218 and the 19 `DC_GPIO_AUX_CTRL_1` shifts whose masks are just after line 35435.
- Diff the range against AMD's authoritative generated DCN 3.5.0 register database and nearby generated headers, especially DCN 3.2 or DCN 3.5.1 variants where the same AFMT4, DIG4, DP4, DCIO, UNIPHY, and GPIO register layouts are expected to match.
- Exercise HDMI and DisplayPort audio on DCN 3.5 hardware across modesets, plug/unplug, suspend/resume, sample-rate changes, multichannel LPCM, HBR/compressed formats, and audio sink changes. Watch for silent audio, wrong channel allocation, FIFO overflow, ACR instability, and packet-update failures.
- Exercise DisplayPort link training, MST, DSC, MSO, ALPM, metadata packets, and secondary data packet scheduling. Watch for training timeouts, CRC errors, missing HDR metadata, blank screens, underruns, MST slot-allocation mismatches, and ALPM wake failures.
- Exercise DDC/AUX/HPD paths across all exposed connectors. Validate EDID reads, DP AUX transactions, HPD IRQ/level detection, connector wake, panel backlight/PWRSEQ behavior, and resume after display power gating.
- Use register readback or debugfs traces where available to confirm DB pending/taken transitions, CRC done/result fields, DP MSA timing readbacks, DPHY training status, AFMT/DIG packet enables, and GPIO Y/A/EN state changes match the intended programming sequence.

## Cross-Chunk Notes

This chunk continues the AFMT4 audio packet-control/register family from the previous range and stops mid-`DC_GPIO_AUX_CTRL_1`. Adjacent chunks are required before making whole-file claims about all AFMT4 audio packet fields or all AUX control masks. The final merged per-file research should treat this as one slice of the broader DCN 3.5.0 generated shift/mask namespace rather than as an independent handwritten module.

### subset-b-002072: lines 35436-37655

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 35436-37655

## Purpose

This chunk is a generated DCN 3.5.0 register field shift/mask table for AMD display hardware. It does not implement runtime logic directly; it supplies preprocessor constants consumed by AMD Display Core register-access macros to pack, unpack, read, update, and validate MMIO fields for GPIO/AUX/DDC/HPD pads, UNIPHY reserved registers, panel power sequencing/backlight PWM, Display Stream Compression (DSC/DSCC/DSCCIF), and DC perfmon counters.

The line range contains 2,220 lines and 2,217 `#define` entries. Every entry follows the generated `REGISTER__FIELD__SHIFT` or `REGISTER__FIELD_MASK` convention, where the shift is the bit position and the mask is the already-shifted field mask for a 32-bit register value.

## Register Areas Covered

- `DC_GPIO_AUX_CTRL_1` through `DC_GPIO_AUX_CTRL_5` define electrical control fields for AUX, I2C/DDC, DDCVGA, and HPD pads: CSEL/RSEL choices for 0.9 V and 1.1 V domains, bias and resistor enables, slew/fall-slew tuning, spike filter controls, comparator selection, AUX DP/DN swap, hysteresis tuning, AUX control nibbles, DDC pad I2C mode, and AUX pad power-good fields.
- `DC_GPIO_RXEN` and `DC_GPIO_PULLUPEN` map receive-enable and pull-up-enable bits for generic GPIOs, sync/genlock/swaplock pins, and HPD1-HPD6 pins.
- `AUXI2C_PAD_ALL_PWR_OK` provides per-pad power state fields for AUX, I2C, I2C mode, DDCVGA, and HPD pad groups.
- `DCIO_UNIPHY{1..4}_UNIPHY_MACRO_CNTL_RESERVED{0..57}` reserve one full-width field per register instance. The defines expose only a full 32-bit `RESERVED` field shift/mask per register, preserving generated register coverage even where the public driver does not name hardware subfields.
- `PWRSEQ0_*` and `PWRSEQ1_*` cover two panel power-sequencer instances. Fields include GPIO power-sequencer enable/control/mask/output bits, panel DIGON/DIGON override, BLON/BLON override, power-up/down sequence delays, refresh dividers, panel state flags, PWM control and period registers, backlight group register locks, and spare bits.
- `DSC_TOP{0..2}_DSC_TOP_CONTROL`, `DSCCIF{0..2}_*`, and `DSCC{0..2}_*` define three Display Stream Compression instances. The DSCC coverage includes DSC mode/configuration, status and interrupt fields, PPS config registers 0-22, memory power controls, error accumulators, max absolute error fields, rate buffer fullness, rate control buffer fullness, and debug-bus rotation for instance 0.
- `DC_PERFMON17_*`, `DC_PERFMON18_*`, and the beginning of `DC_PERFMON19_*` define display perfmon event selection, count value selection, increment mode, hardware control/start-stop behavior, counter run/active/interrupt state, state selectors, high/low counter values, and current-value interrupt/misc fields.

## Important APIs, Types, and Macros

This header exposes constants only. The important "API" is the generated register-field naming contract used by AMD display macros:

- `REG_SET`, `REG_SET_N`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, `REG_GET_N`, `REG_READ`, and `REG_WRITE` in the display code use register offsets plus these shift/mask constants to manipulate MMIO fields.
- Register list helpers such as `SRI_ARR`, `SR`, `SRIR`, `SF`, `SF_DDC`, and DSC-specific `DSC_SF` expand into structures of register offsets, shifts, and masks.
- `dcn35_resource.c` builds `dsc_shift` and `dsc_mask` from `DSC_REG_LIST_SH_MASK_DCN35(__SHIFT)` and `DSC_REG_LIST_SH_MASK_DCN35(_MASK)`, so the DSCC constants in this chunk become per-instance DSC programming metadata.
- `dcn20_dsc_registers`, `dcn20_dsc_shift`, `dcn20_dsc_mask`, `dcn35_dsc_shift`, and `dcn35_dsc_mask` are the typed storage for the generated DSC register metadata.
- `ddc_regs.h` uses `DC_GPIO_AUX_CTRL_5__DDC_PAD*_I2CMODE` in `DDC_MASK_SH_LIST_DCN2`, tying this chunk to DDC/AUX pad mode configuration.
- Panel control code stores and restores `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, and power-sequencer divider fields through the generated field metadata.

## Control Flow and Runtime Behavior

There is no local control flow in this chunk. Runtime behavior appears when included through DCN 3.5 display resource construction:

1. DCN 3.5 resource initialization includes `dcn_3_5_0_offset.h` and this shift/mask header, then populates register/shift/mask structures for display blocks.
2. GPIO/DDC setup code selects per-connector DDC/AUX register metadata. When a DDC line is configured, the generic GPIO/DDC helpers use the stored mask/shift values for pad pull-down, AUX pad mode, RX selection, and I2C-mode updates.
3. Panel power and backlight code reads PWM state from hardware, caches working values, restores them after BIOS or suspend/resume anomalies, enables PWM output, and unlocks register groups. The power-sequencer constants in this chunk define the bit positions for those operations.
4. DSC creation wires a `dcn20_dsc` object to DCN 3.5 shift/mask tables. DSC enablement resets DSCC memory power control bits before enabling the compressor, then common DSC programming writes PPS config registers 0-22 using the masks/shifts from this chunk.
5. Perfmon consumers can program event selection, run mode, interrupt, state, and counter-value registers for display performance counters 17, 18, and 19.

## State and Persistence

The header itself is stateless and has no persistence. It defines compile-time constants that describe hardware state layout. Persistence concerns are in callers:

- Backlight and panel state are persisted in driver memory via `stored_backlight_registers` and restored to hardware when PWM registers are invalid or reset.
- DSCC memory power fields (`DSCC_MEM_PWR_FORCE`, `DSCC_MEM_PWR_DIS`, and state bits) reflect hardware low-power state. `dsc35_enable()` explicitly clears force/disable bits because DSCC memory can remain unexpectedly shut down after idle exit.
- DSC PPS registers persist the active compression stream parameters in hardware until reprogrammed, reset, or power-gated.
- Perfmon counters and state bits persist in hardware counter registers while the perfmon block is active and are reset or reconfigured by perfmon control writes.

## Dependencies and Integration Points

- Must be paired with `dcn_3_5_0_offset.h`; masks/shifts alone are not usable without matching MMIO register addresses.
- Depends on the AMD Display Core register abstraction in `drivers/gpu/drm/amd/display`, especially the resource construction layer and `REG_*` field-access macros.
- Integrates with `dc/gpio/ddc_regs.h` for DDC/AUX pad mode and RX selection.
- Integrates with `dc/dce` and `dc/dcn301` panel-control paths for PWM/backlight and panel power-sequencer programming.
- Integrates with `dc/dsc/dcn20`, `dc/dsc/dcn35`, and DCN resource headers for DSC PPS programming, interrupt/status reads, memory power handling, and error telemetry.
- Integrates with perfmon infrastructure through generated `DC_PERFMON17`, `DC_PERFMON18`, and `DC_PERFMON19` field layouts.

## Risks and Edge Cases

- Generated constants must match the ASIC register spec exactly. A single wrong shift or mask silently writes the wrong MMIO bits and can break display bring-up, HPD/DDC detection, backlight control, DSC compression, or perfmon reporting.
- Reserved UNIPHY definitions expose full-register masks. Callers must avoid treating these as safe writable public fields unless hardware documentation requires it.
- The DSC PPS fields are tightly packed and often span several fields per register. Incorrect packing can produce invalid DSC PPS payloads, link training/display corruption, or decompression failure on sinks.
- DSCC memory power control is sensitive during idle exit and power transitions. The existing DCN 3.5 DSC code already works around intermittent DSCC memory shutdown by clearing force/disable bits at enable time.
- Panel power and PWM fields affect physical panel sequencing. Bad masks for DIGON/BLON delays, overrides, or PWM duty/period can cause blank panels, flicker, or unsafe sequencing.
- GPIO/AUX/HPD electrical tuning fields affect signal integrity and hotplug/DDC reliability. Wrong masks can look like intermittent cable, EDID, or HPD problems rather than a software failure.
- Perfmon control fields include interrupt and counter restart controls; incorrect bit layout can leave counters inactive, count the wrong event, or generate unexpected interrupts.

## Test Signals

- Build coverage: compile the AMD display driver for DCN 3.5 targets with this header included; type/field mismatches in resource initializers and register macros should fail at compile time.
- Display bring-up: internal/eDP panel powers on, backlight responds, and suspend/resume does not leave PWM period/duty invalid.
- Connector detection: HPD, DDC EDID reads, AUX transactions, and I2C-over-AUX paths work across all exposed connectors and voltage/power states.
- DSC validation: high-bandwidth modes that require DSC light correctly, DSC PPS register dumps match expected stream parameters, and no DSCC interrupt/status errors or rate-buffer anomalies appear.
- Power management: idle exit, S0ix, runtime PM, and display off/on transitions do not leave DSCC memory in shutdown or panel sequencing registers reset.
- Perfmon validation: DC perfmon counters can be configured for known events, become active, increment predictably, and report/clear interrupts as expected.
- Register audit: compare generated masks/shifts against hardware XML/register database for DCN 3.5.0, especially packed PPS fields, panel sequencing fields, and GPIO/AUX electrical controls.

### subset-b-002073: lines 37656-39874

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 37656-39874

## Purpose

This chunk is part of the generated AMD DCN 3.5.0 register shift/mask header used by the DRM AMD display driver. It does not implement executable control flow. Instead, it provides preprocessor constants that describe bit positions and bit masks for hardware register fields in several display blocks: display core performance monitors, Display Stream Compression block 3, Display Writeback, VPG generic packet generation, DisplayPort stream/symbol/link encoders, APG audio packet generation, DCHVM virtual memory control, and DP DPHY symbol32 controls.

The exported surface is the set of `#define` names following the register-field convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted bit mask for that field.

Driver code combines these constants with generated register offsets from neighboring `*_offset.h`/`*_sh_mask.h` headers and common AMD display register macros to write, update, or read individual fields without hard-coding bit arithmetic at each call site.

## Macro Families In This Chunk

The chunk begins mid-register for `DC_PERFMON19_PERFCOUNTER_CNTL` and then defines complete field layouts for `DC_PERFMON19`, `DC_PERFMON20`, and `DC_PERFMON21` performance monitor instances. These macros cover performance counter event selection, counted value type, hardware stop selectors, count-off selectors, counter state selectors for counters 0 through 7, performance monitor state, report count, count-off interrupt enable/status/ack, clock enable, run-enable start/stop selection, counter interrupt status/ack bits, and low/high counter value reads.

The DSC portion describes `DSC_TOP3`, `DSCCIF3`, and `DSCC3` registers. It includes DSC top clock gates, DSCCIF input underflow recovery/status/interrupt fields, input pixel format and bits-per-component fields, picture width/height, DSCC slice layout, rate-control buffer model size, double-buffer pending status, overflow/underflow interrupt status and interrupt-enable bits for rate buffers and rate-control model buffers, many PPS configuration fields, memory power-control fields, squared-error and max-absolute-error readback fields, and maximum fullness counters.

The DWB section covers the Display Writeback pipe. It includes writeback enable and clock gates, memory power control for output FIFO and OGAM LUT memories, frame-capture mode/rate/crop/eye fields, crop/source/window dimensions, update lock/pending bits, CRC controls and masks, output format/denorm/min/max fields, MMHUBBUB backpressure counters, host read rate control, overflow status/counter fields, soft reset, gamut remap coefficients for RAM A/B, OGAM LUT access, OGAM mode, region control, start/end base/slope/offset controls for RAM A and RAM B, and HDR multiplier coefficient.

The VPG5 block defines generic packet controls for frame-update and immediate-update scheduling, packet access/data windows, generic packet lock/conflict status, VPG memory power state, ISRC data access, and MPEG info packet payload fields. The repeated `VPG_GENERIC0` through `VPG_GENERIC14` fields encode individual update request and pending bits in one register word.

The DP encoder area defines the first DisplayPort symbol32/stream/link encoder instance in this chunk. It includes symbol encoder enable/reset/status, video FIFO control, MSA double-buffering and MSA payload registers, pixel-format controls, SDP generic secondary-data-packet controls for GSP packet slots 0 through 14, SDP metadata packet controls, SDP audio controls, stream clock controls and ramp-adjuster FIFO status/control registers, input mux, audio control, link encoder clock control/spare, and DPHY symbol32 controls.

The tail of the chunk reaches `DP_DPHY_SYM320_DP_DPHY_SYM32_*` fields. These describe DPHY enable/reset/precoder/mode/lane control, status and pending update bits, SAT update controls, virtual-channel rate controls, SAT slot/source controls and status for VC0 through VC3, test-pattern selection and PRBS seeds, custom test-pattern payloads, DPHY error status bits, stream symbol override fields, and the first part of DPHY CRC configuration.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or inline helpers in this line range. The important API is the generated macro namespace consumed by C code elsewhere in the AMD display stack.

Important naming patterns:

- `DC_PERFMON19_*`, `DC_PERFMON20_*`, and `DC_PERFMON21_*` identify repeated performance monitor instances. The field layout is nearly identical across the instances, so users can share programming logic while substituting the instance-specific register macro names.
- `DSCC3_*`, `DSCCIF3_*`, and `DSC_TOP3_*` identify DSC engine instance 3 and its interface/top-level controls.
- `DWB_*` names describe Display Writeback programming, color processing, CRC, error, and memory-power registers.
- `VPG5_*` names describe generic packet generator instance 5.
- `DP_SYM32_ENC0_*`, `DP_STREAM_ENC0_*`, `DP_LINK_ENC0_*`, and `DP_DPHY_SYM320_*` describe DisplayPort output instance 0 in symbol32 mode.
- `APG0_*`, `DME5_*`, and `DCHVM_*` provide audio packet generator, DME, and display VM controls that integrate with the stream/output path.

Callers usually interact with these definitions through AMD register-access helpers such as register read/modify/write wrappers, field setter macros, or generated register tables in the DC resource code. Those helpers expect the `__SHIFT` and `_MASK` suffixes to be mechanically consistent.

## Control Flow And Runtime Behavior

This header chunk has no runtime branches, loops, calls, or side effects. Runtime control flow appears in the driver code that includes it. At that higher layer, the typical pattern is:

1. Select a hardware block instance and register address from generated offset tables.
2. Use this header's `__SHIFT` and `_MASK` values to compose a field value or extract a field from a read register word.
3. Program hardware by writing the containing register, often through a register-update macro that preserves unrelated fields.
4. Poll status or pending bits such as double-buffer pending, reset done, update pending, overflow status, interrupt status, rate/SAT pending, or conflict status.

The macro values encode the hardware contract that makes those operations correct. For example, double-buffer pending bits in DSCCIF/DSCC/DWB/DP symbol encoder blocks tell callers whether staged state has been latched, while interrupt status and ack masks define how error/overflow conditions are observed and cleared.

## State And Persistence Behavior

The file itself persists no software state. It represents persistent and transient hardware state fields in memory-mapped registers:

- Configuration state: clock enables, resets, pixel formats, DSC PPS values, DWB output formats, gamut/OGAM coefficients, DP SDP packet controls, MSA payloads, DPHY mode/lane controls, and virtual-channel rates.
- Latched or double-buffered state: update pending bits for DWB, DSC, VPG generic packets, DP MSA/pixel-format controls, and DP/DPHY SAT or rate updates.
- Status and error state: performance counter activity and values, underflow/overflow status, reset done/status, CRC values, backpressure counters, rate buffer fullness, DPHY error bits, VPG conflict status, and interrupt status/ack fields.
- Power-management state: memory power-force/disable/state fields for DSCC, DWB, VPG, DP symbol encoder memory, APG, DME, and DCHVM.

Because these masks are used for direct hardware programming, incorrect values can persist until the next register write, mode set, reset, or power-cycle depending on the affected block.

## Dependencies And Integration Points

This chunk depends on the AMDGPU DCN register-generation scheme. It is meaningful only when paired with:

- Register offset/address headers for DCN 3.5.0.
- AMD display register access helpers that consume `__SHIFT` and `_MASK` names.
- Block-specific DC code for DSC, DWB, VPG, DP stream/link/symbol encoding, APG audio packet setup, DCHVM, and performance monitoring.
- Hardware documentation or generator inputs that define the authoritative field positions for DCN 3.5.0 ASICs.

The integration points are mostly compile-time. If a C source includes this header and references one of these macros, the compiler substitutes the constants into register programming code. There is no link-time symbol from this chunk.

## Risks And Maintenance Notes

- This is generated hardware description data. Manual edits are high risk because a single wrong bit position can silently corrupt an unrelated field in a memory-mapped register.
- Several register names are repeated across numbered hardware instances. Copy/paste or generator bugs can produce instance-specific drift that compiles cleanly but targets the wrong hardware bit.
- The chunk starts in the middle of `DC_PERFMON19_PERFCOUNTER_CNTL` and ends in the middle of `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0`; complete review of both registers requires adjacent chunks.
- Large repeated layouts, especially `DWB_OGAM_RAMA/RAMB_REGION_*`, `VPG5_VPG_GSP_*`, and `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL*`, are easy places for off-by-one field numbering or mask/shift mismatch.
- Status/ack fields such as overflow, interrupt, conflict, reset, and pending bits may have write-one-to-clear or read-only semantics in hardware. The masks do not encode access type, so callers must rely on the register programming guide or higher-level driver conventions.
- Signed or packed coefficient fields such as gamut remap, OGAM bases/slopes/offsets, and DSC PPS ranges require callers to format values correctly before applying the mask.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generator, and hardware integration checks:

- Build coverage for AMD display code that references DCN 3.5.0 DSC, DWB, VPG, DP encoder, APG, DCHVM, and perfmon macros.
- Generator diff checks against the upstream register database to confirm every `__SHIFT` has the expected paired `_MASK`, no fields are missing, and repeated instance layouts remain consistent.
- Static checks that each mask is compatible with its shift and field width, especially for multi-bit ranges such as DSC PPS values, DWB OGAM/gamut coefficients, VPG generic update bitmaps, DP SDP GSP controls, and DPHY VC rate controls.
- Mode-set and display validation on DCN 3.5.0 hardware using DSC, writeback, DP audio/SDP packets, panel replay/MSA changes, and DPHY symbol32 paths.
- Error-path tests or diagnostics for underflow/overflow interrupts, CRC readback, reset-done polling, update-pending polling, DPHY error reporting, VPG conflict handling, and performance counter readback.
- Power-management tests that toggle memory light-sleep/power fields and verify no hangs or stale pending bits across display enable, disable, suspend, resume, and hotplug flows.

### subset-b-002074: lines 39875-42091

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 39875-42091

## Purpose

This chunk is a generated AMD DCN 3.5.0 shift/mask register-field slice. It has no executable logic; it publishes C preprocessor constants that describe bit positions and bit masks inside DCN 3.5.0 display, audio, packet, and high-rate DisplayPort registers. Driver code combines these macros with the companion `dcn_3_5_0_offset.h` offsets and AMD display `REG_*` helper macros to read, write, update, or poll individual MMIO fields.

The requested range contains 2,217 `#define` entries: 1,108 `__SHIFT` macros and 1,109 `_MASK` macros. The count is intentionally unbalanced at the artificial chunk boundaries. The first lines are masks for `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0` fields whose shifts are in the previous chunk, and the final lines are shifts for `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` fields whose masks continue in the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, includes, variables, locks, allocations, or runtime branches in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position of a register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or preserve the same field.

Major macro families in this range are:

- `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_*` tail fields: masks and status/count fields for HPO DP DPHY/SYM32 CRC capture, including CRC enable/reset, lane/tap/scheduler source, start/end events, done state, CRC value, and symbol count.
- `DP_STREAM_ENC1`, `DP_STREAM_ENC2`, and `DP_STREAM_ENC3`: HPO DP stream encoder clock enables and clock-on status for `DISPCLK`, `SOCCLK`, `DPSTREAMCLK`, and `SYMCLK32`; pixel/audio input mux selectors; clock-ramp-adjuster FIFO enable/reset/read-start/read-clock/status/error fields; and spare fields.
- `DP_LINK_ENC1`: link encoder clock-control and spare fields for the high-performance output path.
- `APG1`, `APG2`, and `APG3`: Audio Packet Generator reset, enable, DP audio stream ID, ASP channel-count override, debug generator controls, packet source selectors, audio CRC controls/results, audio/HBR/FIFO overflow status, output-active state, memory power state, and spare fields.
- `DME6`, `DME7`, and `DME8`: metadata engine controls and memory power controls, including metadata requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable, missed transmission flags, memory power force/disable/state, and default low-power state.
- `VPG6`, `VPG7`, and `VPG8`: Video Packet Generator generic packet access/data bytes, frame and immediate update bits for generic packets 0-14, generic-packet conflict status/clear, memory power control, ISRC access/data bytes, and MPEG info bytes.
- `DP_DPHY_SYM321_DP_DPHY_SYM32_*`: a complete DPHY/SYM32 instance for HPO DP link behavior, including reset/enable/precoder/mode/lane count, status and update-pending bits, slot allocation table update, per-VC stream source and slot count, per-VC rate `X/Y` controls, test-pattern configuration, PRBS seeds, square-pulse width, custom symbols, error status, symbol override, and CRC controls/status/count.
- `DP_SYM32_ENC1` and `DP_SYM32_ENC2`: nearly complete HPO DP stream encoder field groups for stream instances 1 and 2, covering encoder reset/enable, video pixel format and double-buffering, FIFO reset/enable/status, stream enable/status/VBID fields, panel replay tunneling, SDP stream and CRC enable, audio SDP controls, metadata-packet controls, MSA control/data words 0-8, GSP controls 0-14, video CRC controls/results/status, memory power control, HBlank minimum symbol width, and spare fields.
- `DP_SYM32_ENC3`: beginning of the same HPO DP stream encoder field group for instance 3. This chunk covers encoder control, video FIFO, pixel format, double-buffer controls, MSA data words, HBlank control, and SDP GSP controls 0 through the shifts for control 6. The corresponding masks for the last control-6 fields and the rest of instance 3 continue after line 42091.

The most repetitive structures are the per-instance register blocks. `APG1-3`, `DME6-8`, `VPG6-8`, `DP_STREAM_ENC1-3`, and `DP_SYM32_ENC1-2` repeat identical or near-identical field layouts with instance-specific prefixes, while `DP_SYM32_ENC3` is truncated only because the chunk ends mid-block.

## Control Flow

This header has no runtime control flow. The runtime flow is supplied by the AMDGPU display stack:

1. DCN 3.5/3.5.1 resource code includes the generated offset and shift/mask headers.
2. Register-list macros paste symbolic instance names into generated macro names and initialize per-block register, shift, and mask tables.
3. Resource constructors attach those tables to stream encoders, HPO DP stream encoders, VPGs, APGs, AFMT/audio sub-blocks, and HPO DP link encoders.
4. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and wait/poll helpers to manipulate the fields described here.

Concrete integration found in this tree includes `dcn351_resource.c`, which builds `vpg_regs`, `apg_regs`, `stream_enc_regs`, and `hpo_dp_stream_enc_regs` tables. The HPO DP stream encoder table uses `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(__SHIFT)` and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(_MASK)` from `dcn31_hpo_dp_stream_encoder.h`; VPG and APG tables use `DCN31_VPG_MASK_SH_LIST()` and `DCN31_APG_MASK_SH_LIST()` from the shared DCN31 headers. HPO DP link behavior is similarly tied to generated DPHY/SYM32 fields through the `dcn31_hpo_dp_link_encoder` register macros.

The generated constants do not encode sequencing. Consumers still have to order clock enablement, reset/de-reset, FIFO reset and enable, stream/audio mux programming, packet-buffer updates, metadata double-buffer handoff, CRC capture, DPHY slot/rate updates, and power-gating transitions correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state in DCN 3.5.0 blocks:

- HPO DP stream encoder state: clock gating/status, mux selections, FIFO calibration/status, stream encoder reset/enable, video stream enable/status, pixel format, MSA payloads, HBlank symbol sizing, panel replay flags, SDP/GSP packet scheduling, metadata packet double buffering, audio SDP controls, video CRC capture, and memory power state.
- Audio packet generator state: APG reset/enable, DP audio stream ID, debug audio generation, packet source selection, audio CRC run/result/clear, FIFO overflow status, HBR/audio enable status, output-active status, and APG memory power.
- Video packet generator state: generic packet payload bytes, ISRC and MPEG info payload bytes, per-packet frame/immediate update request bits, conflict status, and memory power.
- Metadata engine state: requestor selection, metadata engine enable, double-buffer pending/taken/clear/disable state, missed transmission flags, and memory power state.
- HPO DP DPHY/SYM32 state: DPHY reset/enable, precoder/mode/lane settings, SAT and rate update-pending status, per-VC slot/rate controls, test-pattern generation, PRBS/custom-symbol controls, symbol override, error flags, CRC configuration/status/count, and link encoder clock/spare fields.

Persistence is hardware-defined. Configuration fields usually last until a modeset, stream teardown, link retraining, power-gating event, suspend/resume restore, driver reset, firmware reprogramming, or ASIC reset. Status, error, interrupt-like, clear, pending, and done fields may be read-only, sticky, write-one-to-clear, self-clearing, or only valid while related display clocks and power domains are enabled. This generated header does not describe access semantics; consuming code and the hardware register specification provide that context.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which defines the matching MMIO register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which creates DCN351 stream encoder, VPG, APG, and HPO DP stream encoder register tables from generated offsets, shifts, and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`, whose mask/shift list names stream encoder fields that are provided by this header for `DP_STREAM_ENC*` and `DP_SYM32_ENC*`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h`, whose VPG/APG field-list macros are satisfied by the generated `VPG*` and `APG*` definitions here.
- HPO DP link encoder code under `display/dc/hpo/dcn31` and `display/dc/hpo/dcn32`, which consumes DPHY/SYM32 control, status, SAT, rate, and test-pattern fields through generated register tables.
- DMUB DCN35 register initialization in `display/dmub/src/dmub_dcn35.c`, which includes the generated DCN 3.5 offset and shift/mask headers for firmware-facing register access tables.

Operationally, these fields integrate with DisplayPort 2.x/HPO stream setup, high-rate link encoder training and diagnostics, audio packet generation, infoframe and generic packet programming, HDR/metadata packet transmission, video CRC validation, panel replay packet controls, and low-power memory control for packet/metadata/encoder blocks.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while updating the wrong MMIO bits. Symptoms may be limited to one encoder, one HPO DP lane/link, one packet slot, or one audio generator instance.
- The generated namespace is highly repetitive. Instance drift in `APG1-3`, `DME6-8`, `VPG6-8`, `DP_STREAM_ENC1-3`, or `DP_SYM32_ENC1-3` may not be caught by tests that only use the first available display or audio path.
- Chunk boundaries are artificial. This chunk starts after some `DP_DPHY_SYM320` shifts and ends before some `DP_SYM32_ENC3` masks, so full-field pairing must be checked across adjacent chunk documents.
- Status and clear fields are side-effect-sensitive. Confusing pending, done, clear, overflow, missed-transmission, conflict, or error bits can lead to stuck packet updates, stale metadata, CRC waits that never complete, interrupt-like storms, or missed diagnostics.
- Stream encoder clock and reset fields are sequencing-sensitive. Incorrect masks around clock enable/status, FIFO reset/done, or encoder reset/done can produce blank HPO DP streams, underflow, hangs during modeset, or resume-only failures.
- Packet scheduling fields affect protocol-visible data. Bad GSP, SDP, metadata, MPEG, ISRC, MSA, VBID, audio SDP, or line-number fields can corrupt infoframes, HDR metadata, audio transport, DSC/compressed stream signaling, or multi-stream packet timing.
- DPHY/SYM32 SAT and rate fields are link-critical. Wrong per-VC slot count, stream source, or rate `X/Y` masks can break multi-stream allocation, high-rate link training, or payload scheduling in ways that only appear under MST, high bandwidth, or multiple HPO streams.
- Memory-power fields are hardware-state dependent. Writes may be ignored or harmful if the block is clock-gated, power-gated, reset, or firmware-owned at the time of access.

## Test Signals

Useful validation combines generated-header consistency with DCN 3.5 hardware behavior:

- Build AMDGPU/DC with DCN 3.5/3.5.1 support enabled. Missing or renamed symbols should fail in token-pasted stream encoder, HPO DP stream encoder, APG, VPG, HPO link encoder, or DMUB register-table construction.
- Mechanically verify shift/mask pairing across the full file, not just this chunk. For this slice, expected boundary exceptions are `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0` masks at the start and `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` shifts at the end.
- Diff this generated range against AMD's authoritative DCN 3.5.0 register database and nearby generated headers such as `dcn_3_5_1_sh_mask.h` where HPO DP and packet block layouts are expected to match.
- Exercise HPO DisplayPort streams across all exposed HPO stream encoder instances, including stream enable/disable, modeset, link retrain, lane-count/link-rate changes, MST payload allocation, high-bandwidth modes, suspend/resume, and display hotplug.
- Validate packet behavior: generic packets, HDR/metadata packets, MPEG/ISRC payloads, MSA values, VBID/compressed-stream flags, GSP frame/immediate update bits, double-buffer pending behavior, and packet line-number scheduling.
- Validate audio paths through APG: DP audio stream ID selection, audio enable/HBR status, channel-count override, CRC capture and clear, FIFO overflow reporting, mute/unmute, and audio behavior across plug/unplug and format changes.
- Validate diagnostics: DPHY error status, SAT/rate update-pending transitions, CRC done/value/count fields, video CRC result/status fields, FIFO reset/done/status/error fields, and generic-packet conflict flags.
- Watch kernel logs and display diagnostics for HPO DP blanking, link-training failure, MST payload errors, audio dropouts, metadata corruption, CRC mismatches, stuck update-pending bits, FIFO errors, packet conflicts, and resume-only regressions.

## Cross-Chunk Notes

The previous chunk owns the start of the `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0` field definitions, including several shifts whose masks appear at the beginning of this chunk. The next chunk continues `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` masks and the rest of the `DP_SYM32_ENC3` stream encoder block. The final per-file document should merge adjacent chunks before making complete claims about all DCN 3.5.0 HPO DP stream encoder, DPHY/SYM32, VPG, APG, and DME instances.

### subset-b-002075: lines 42092-44308

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 42092-44308

## Purpose

This chunk is generated AMD DCN 3.5.0 register-field metadata. It contains only C preprocessor constants for field bit positions and masks; it does not contain executable code, structs, enums, includes, or storage. Consumers combine these `__SHIFT` and `_MASK` constants with the matching DCN 3.5.0 register-offset header to build typed-looking register access tables for AMDGPU Display Core.

The 2,217 lines in this range contain 2,217 `#define` entries: 1,107 shift macros and 1,114 mask macros. The chunk begins in the middle of `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` mask definitions, continues through generic secondary data packet control groups for DisplayPort stream encoder 3, covers four `MPCC` blender instances, and then covers most of the `MPCC_OGAM` output gamma and gamut-remap register fields for instances 0 through 3. The final line stops inside `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_24_25`, so the matching masks for region 24 segment count and region 25 fields are outside this chunk.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions or types in this chunk. The exported interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask used by register helpers during read-modify-write or decode operations.

The main macro families are:

- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` through `CONTROL14`: generic secondary-data-packet controls for DP stream encoder 3. Each control group describes enable bits for video-continuous and idle-continuous transmission, one-shot trigger and trigger position, double buffering, payload size, start-of-frame reference, missed-deadline and pending status, double-buffer pending status, and a 16-bit transmission line number field.
- `MPCC0_MPCC_*` through `MPCC3_MPCC_*`: per-MPCC blender/combiner fields. Each instance has top and bottom DPP source selection, OPP binding, blend control, stereo/multi-frame control, update-lock selection and status, top and bottom gain controls, background color channels, OGAM memory power controls, and idle/busy/disabled status.
- `MPCC_OGAM0_*` through `MPCC_OGAM3_*`: output gamma and gamut-remap fields attached to MPCC instances. These include `MPCC_OGAM_CONTROL`, LUT index/data/control, RAM A and RAM B piecewise-linear region descriptors, per-channel start/end/base/slope/offset fields, and gamut-remap coefficient format/mode plus matrix coefficient fields.
- `MPCC_OGAM*_MPC_GAMUT_REMAP_*_{A,B}`: A/B coefficient banks for MPCC gamut remap. Coefficients are paired in 32-bit registers, typically with one 16-bit coefficient in low bits and the other in high bits.

Several register layouts repeat mechanically across instances. The MPCC blender group is repeated for MPCC0 through MPCC3. The OGAM group is repeated for `MPCC_OGAM0` through `MPCC_OGAM3`, with the same LUT, RAMA/RAMB, and gamut-remap field shapes until the artificial chunk boundary cuts off part of `MPCC_OGAM3` RAMB region definitions.

## Control Flow

This header has no runtime control flow. Runtime behavior emerges in AMD display code that includes the generated offset and shift/mask headers:

1. DCN 3.5 display code includes `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Register-list macros such as `SRII`, `SRI`, `SF`, and related token-pasting helpers construct per-block register, shift, and mask tables.
3. MPC, MPCC, stream encoder, resource, IRQ, and DMUB objects store those tables.
4. Runtime paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`; those helpers use these shift/mask constants to isolate the intended hardware fields.

The sequencing is not encoded here. Consumers must still order stream encoder SDP updates, MPCC connection/disconnection, blender programming, update locking, OGAM memory power state changes, LUT writes, gamut-remap coefficient updates, and modeset commits according to the hardware programming model.

## State And Persistence Behavior

This chunk persists no software state. It describes hardware state in DCN 3.5.0 display registers:

- DP GSP control state for stream encoder 3 secondary data packet scheduling, including continuous or one-shot send modes, double-buffer status, trigger-pending status, and target transmission line.
- MPCC routing state for selecting top/bottom DPP inputs and associating an MPCC with an output pixel processor.
- MPCC blend state for blend mode, alpha blend mode, premultiplied alpha, active-overlap-only blending, background bits-per-component, bottom gain mode, global alpha, global gain, top gain, bottom gain inside/outside, and background RGB/YCbCr values.
- MPCC stereo or surface-mode state through `MPCC_SM_CONTROL`, including enable, mode, frame/field alternation, forced next-frame or top polarity, and current frame polarity.
- MPCC update-lock state and readback status, used to coordinate atomic or double-buffered programming.
- MPCC OGAM memory power state through force, disable, low-power mode, and state fields.
- OGAM LUT state: active mode, selected RAM bank, PWL disable, current mode/select readback, LUT index, LUT data, color write mask, read color selection, host selection, and LUT configuration mode.
- OGAM RAMA/RAMB piecewise-linear region state: per-channel start/end/base/slope/offset values and region-pair fields for LUT offsets plus number-of-segments encodings.
- MPCC gamut-remap state: coefficient format, selected/current mode, and A/B bank matrix coefficients.

Hardware persistence is power-domain and modeset dependent. Register values generally survive until the display block is reprogrammed, gated, reset, suspended/resumed, or replaced by an atomic commit. Status fields such as busy/idle/disabled, current OGAM selection, update-lock status, pending flags, and double-buffer status reflect live hardware state. The generated mask header does not describe read-only, sticky, self-clearing, write-one-to-clear, or double-buffer semantics; those rules come from silicon documentation and the consuming driver code.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which supplies the matching MMIO register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which includes this header for DCN 3.5 DMUB register definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`, another direct DCN 3.5 include site.
- MPC register table definitions in `display/dc/mpc/dcn10`, `dcn20`, `dcn30`, and `dcn32`, where `MPCC*_MPCC_*` and `MPCC_OGAM*_...` fields are mapped into common MPC structures.
- DCN 3.5 resource construction, which reuses those MPC structures to expose MPCC composition and output color programming to the rest of Display Core.
- Higher-level display color code that selects MPCC output gamma, PWL LUT banks, gamut-remap mode, and coefficient format through `dc_hw_types.h` concepts such as `MPCC_OGAM_GAMUT_REMAP`, `CM_GAMUT_REMAP_MODE_*`, and `CM_GAMUT_REMAP_COEF_FORMAT_*`.
- DisplayPort stream encoder code paths that program generic secondary data packets, where the `DP_SYM32_ENC3_*_GSP_CONTROL*` constants define fields for stream encoder instance 3.

The chunk therefore sits at the boundary between generated hardware descriptions and runtime display features: multi-plane composition, blending, update locking, output gamma LUT programming, gamut conversion, power management of OGAM memories, and DP SDP packet scheduling.

## Risks And Edge Cases

- These values are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing the wrong MMIO bits.
- The file is generated. Manual edits can diverge from AMD's register database, the companion offset header, firmware expectations, and silicon documentation.
- Repetition across MPCC and OGAM instances makes instance-local generator errors easy to miss. MPCC0 working does not prove MPCC1 through MPCC3 have correct masks.
- The range starts and ends inside register families. `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` has only trailing masks in this chunk, and `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_24_25` continues after line 44308.
- Field names ending in `_MASK_MASK`, such as `MPCC_OGAM_LUT_WRITE_COLOR_MASK_MASK`, are valid generated names for a field whose hardware name includes `MASK`. Consumers must not simplify or rename them by hand.
- MPCC blend and routing fields affect visible composition. Incorrect source selection, OPP ID, blend mode, alpha, gain, or background masks can cause black planes, wrong plane ordering, incorrect transparency, or color shifts.
- Update-lock and busy/idle/status fields are sequencing-sensitive. Misinterpreting status masks can lead to timeouts, programming while a block is busy, or stale register snapshots.
- OGAM LUT and PWL region fields are precision-sensitive. Wrong 18-bit data masks, 9-bit LUT offsets, 3-bit segment counts, 18/19-bit base/offset masks, or channel-specific fields can introduce banding, clipping, non-monotonic curves, or channel swaps.
- RAM A/B and current-select fields implement banked updates. Incorrect masks can update the displayed bank instead of the inactive bank, causing visual tearing or partially programmed gamma/gamut state.
- OGAM memory power fields interact with color programming. Programming LUT or remap state while memory is forced off or in the wrong low-power state can drop writes or leave stale color state after resume.
- DP GSP trigger and pending fields are timing-sensitive. A wrong transmission-line mask or double-buffer flag can cause generic SDP packets to be sent on the wrong line, missed, duplicated, or left pending.

## Test Signals

Useful validation is mostly build-time macro coverage plus hardware display behavior:

- Build AMDGPU Display Core with DCN 3.5 support enabled. Missing or renamed macros should fail where DCN35 DMUB, IRQ, resource, stream encoder, or MPC tables reference this header.
- Mechanically check this exact line range for expected shift/mask pairs, allowing boundary exceptions for the partial `DP_SYM32_ENC3...CONTROL6` and partial `MPCC_OGAM3...RAMB_REGION_24_25` groups.
- Diff the chunk against AMD's authoritative DCN 3.5.0 register database and adjacent generated DCN headers where the same MPCC/OGAM register families are expected to match.
- Exercise multi-plane composition with alpha, global alpha/gain, bottom gain, background colors, stereo/surface-mode variants, and plane connect/disconnect. Watch for wrong plane order, unexpected transparency, stale backgrounds, and MPCC idle/busy wait failures.
- Exercise output gamma LUT and gamut-remap programming through KMS color-management paths, including degamma/gamma changes, color transforms, HDR/SDR transitions, and bank switching. Watch for banding, wrong colors, flicker during atomic commits, and incorrect readback/current-mode state.
- Run suspend/resume, runtime power management, display hotplug, and modeset loops while changing gamma/gamut state. Look for lost OGAM programming, memory power state mistakes, or resume-only color corruption.
- Validate DP secondary-data-packet behavior on the stream encoder instance corresponding to `DP_SYM32_ENC3`, including one-shot and continuous packet sends, double buffering, trigger line selection, and pending/deadline status.

## Cross-Chunk Notes

This is a middle chunk of `dcn_3_5_0_sh_mask.h`. Earlier chunks contain the first parts of the stream encoder and display register namespace, including the start of `DP_SYM32_ENC3` GSP control groups. Later chunks continue the remaining `MPCC_OGAM3` RAMB region fields and then proceed into later DCN 3.5.0 register families. The final per-file research should merge adjacent chunks before making whole-file claims about all MPCC, OGAM, stream encoder, or color-management registers.

### subset-b-002076: lines 44309-46526

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 44309-46526

## Purpose

This chunk is a generated AMD DCN 3.5.0 shift/mask register-field slice. It has no executable C logic; it publishes preprocessor constants that describe bit positions and masks for fields inside DCN display, audio, video-packet, performance-counter, and adaptive-backlight MMIO registers. Driver code combines this header with the matching `dcn_3_5_0_offset.h` register offsets and AMD display register-helper macros to pack, extract, and update individual hardware fields.

The requested range starts in the middle of the `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_24_25` field group and ends at only the `__SHIFT` half of `DPIA_MU_RBBMIF_TIMEOUT_CTRL__RBBMIF_TIMEOUT_DELAY`. Within the exact range there are 2,218 `#define` lines: 1,108 `__SHIFT` macros and 1,110 `_MASK` macros. The uneven count is caused by chunk boundaries: the first three lines are masks whose shifts live before line 44309, while the final `DPIA_MU_RBBMIF_TIMEOUT_CTRL` mask and its sibling fields continue after line 46526.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset for encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for isolating, preserving, or clearing that field during MMIO read-modify-write operations.

Major register families in this chunk:

- `MPCC_OGAM3_*`: tail of MPCC 3 output gamma and gamut-remap metadata. It covers RAM-B exponential-region LUT offsets and segment counts for regions 24-33, output-gamma gamut-remap coefficient format/mode fields, and A/B banks of `C11` through `C34` matrix coefficients.
- `MPC_*`: display pipe composition and output processing fields. Covered groups include MPC clock control, global/per-component soft reset bits, CRC control/selection/result fields, perfmon event enable, bypass background color, host-read rate control, DPP/config/surface pending status, frame/update-lock sets, DWB muxing, output muxes 0-3, output denorm controls and clamps, and output CSC format/mode/coefficient fields for outputs 0-3.
- `DC_PERFMON22_*` and `DC_PERFMON23_*`: performance monitor and performance counter selection, trigger, enable, clear, state, current value, high, and low fields for two monitor instances.
- `AFMT5_*`: audio formatter instance 5 fields for VBI packet control, audio packet control, audio info words, IEC 60958 channel-status words, audio CRC control/result, ramp controls, formatter status, infoframe control, audio source control, and AFMT memory power state.
- `VPG9_*`: video packet generator instance 9 fields for generic packet access/data, generic stream packet frame and immediate update controls, update-pending bits, generic status/conflict state, VPG memory power, ISRC data access, and MPEG info payload/update fields.
- `DME9_*`: Display Micro Engine metadata requestor and memory low-power control fields.
- `HPO_TOP_*` and `DP_STREAM_MAPPER_CONTROL[0-3]`: HPO top-level display-clock gating, high-performance-output hardware enable, and DP stream mapper link-target selection fields.
- `ABM0_*` through `ABM3_*`: four repeated adaptive backlight management/PWM instances. Each instance contains ambient/user/target/current/final/minimum duty level fields; ABM PWM control and backlight update sample-rate fields; double-buffer lock/update control; ABM enable/bypass; IPS color-space-conversion coefficient selectors; ACE slope/offset and threshold fields; histogram/luminance-statistics controls, results, sample rates, shift flags, and register-read progress; plus backlight master lock.
- `DPIA_MU_RBBMIF_TIMEOUT_CTRL`: only the first timeout-delay shift appears at the final line; the corresponding hold field and masks are outside this chunk.

Several repeated layouts are significant. `MPC_OUT0` through `MPC_OUT3` share mux, denorm, and output CSC geometry; `ABM0` through `ABM3` are almost mechanically identical, with the same field layout per adaptive-backlight instance; `DC_PERFMON22` and `DC_PERFMON23` repeat the same monitor/counter model.

## Control Flow

This header has no runtime control flow. Runtime sequencing comes from the AMDGPU display driver:

1. DCN 3.5 code includes `dcn_3_5_0_offset.h` and this shift/mask header.
2. Register-list macros token-paste symbolic register and field names into per-block register tables.
3. Resource, DMUB, MPC, output pixel processor, audio formatter, video packet generator, performance monitor, HPO/DP mapping, and ABM code stores those tables in DCN 3.5-specific structures.
4. Runtime paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and wait/poll variants; those helpers use the numeric shift/mask constants to read or modify only the targeted field bits.

The macros do not encode ordering rules. Consumers still have to sequence clock gating, reset, pipe composition, output muxing, color pipeline programming, CRC capture, packet double-buffer updates, audio packet setup, performance-counter start/stop, ABM double-buffer locks, frame-start update timing, and power-gated block access correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes MMIO-backed DCN 3.5 hardware state:

- MPCC output gamma/gamut-remap state, including piecewise RAM-B region layout and 3x4-style gamut-remap coefficient banks.
- MPC global state for clock gating, soft resets, CRC source/result capture, DPP pending status, composition output muxing, denormalization, bypass background color, and output CSC programming.
- Video/audio packet state for `AFMT5` and `VPG9`, including audio infoframes, IEC 60958 channel status, packet update requests, pending bits, CRC, ramp controls, ISRC/MPEG payload bytes, and memory power controls.
- Performance monitor state for two counter instances: selected events, trigger modes, clear/enable flags, current values, high/low counter reads, and state-machine/status fields.
- HPO/DP stream-mapper state that routes DP stream targets and gates/enables top-level HPO hardware.
- ABM/PWM state for four instances: requested and measured backlight levels, duty-cycle limits, ambient light input, adaptive contrast enhancement slope/threshold tables, histogram and luma statistics, sampling intervals, update locks/pending bits, missed-frame indicators, and master locks.
- The beginning of DPIA RBBM interface timeout-control state.

Persistence is hardware-defined. Configuration fields generally last until modeset, pipe/link reconfiguration, ABM disable, display-block power gating, suspend/resume, GPU reset, or driver reinitialization. Status, pending, conflict, missed-frame, clear, CRC, histogram, performance-counter, and power-state fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while the relevant display clocks and power domains are active. This generated header does not express those access semantics; consuming code and the register specification must provide them.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which provides matching MMIO offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which directly includes `dcn_3_5_0_sh_mask.h` and the offset header for DCN 3.5 DMUB register table construction.
- DCN 3.5 resource and block headers that build register lists for MPC, AFMT, VPG, DME, HPO, DP stream mapping, performance monitoring, and ABM through token-pasted `reg`, `shift`, and `mask` names.
- Generic AMD display register helpers that combine offsets, base indexes, shifts, and masks for MMIO read/write/update operations.

The most direct behavioral integration points are display composition/color management, HDMI/DP audio packet formatting, secondary-data packet generation, HPO/DP stream routing, display performance diagnostics, CRC/debug capture, and panel power/backlight adaptation. The `ABM0`-`ABM3` fields integrate with firmware or driver backlight policy, while `AFMT5`/`VPG9` integrate with stream encoder paths for high-numbered display instances.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while modifying the wrong MMIO bits, corrupting adjacent fields, or silently breaking a specific display/audio/backlight path.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the matching offset header, firmware assumptions, and silicon documentation.
- The chunk begins and ends inside field groups. Line 44309 lacks the earlier shifts for `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_24_25`, and line 46526 lacks the rest of `DPIA_MU_RBBMIF_TIMEOUT_CTRL`; reconciliation with adjacent chunks is required before making complete per-register claims.
- Repeated instances are copy-sensitive. `MPC_OUT0`-`MPC_OUT3`, `ABM0`-`ABM3`, and the perfmon instances have similar layouts, so a generator error may affect only one pipe, one output, one backlight block, or one high-numbered stream.
- Lock, update-pending, readback-double-buffer, frame-start-select, missed-frame, and clear bits are sequencing-sensitive. Using the wrong mask can leave stale ABM/ACE/PWM state, miss frame-boundary updates, or clear a diagnostic bit unintentionally.
- Audio/video packet fields are receiver-sensitive. Bad AFMT/VPG masks can cause invalid infoframes, wrong IEC 60958 channel status, broken audio CRC/ramp behavior, missing ISRC/MPEG packets, or update-pending bits that never clear.
- Color pipeline fields are visually high impact. Wrong OGAM/gamut-remap/CSC/denorm masks can produce color shifts, clipping, black output, or failures limited to HDR, color-managed, or multi-plane modes.
- Clock, reset, memory-power, timeout, and HPO enable fields are high risk because writes may be ignored or harmful when the block is power-gated, clock-disabled, reset, firmware-owned, or not present on a given ASIC stepping.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 3.5 hardware behavior:

- Build AMDGPU display support with DCN 3.5 enabled. Missing or renamed macros should fail at compile time in DMUB/resource/block register-table construction.
- Mechanically verify field pairing in this range while allowing the two boundary exceptions: the first `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_24_25` masks pair with shifts before line 44309, and `DPIA_MU_RBBMIF_TIMEOUT_CTRL__RBBMIF_TIMEOUT_DELAY__SHIFT` pairs with masks after line 46526.
- Diff this slice against AMD's authoritative DCN 3.5.0 register database and nearby generated headers where layout compatibility is expected.
- Exercise MPC composition and output color paths across plane enable/disable, multiple outputs, DWB use if supported, CRC capture, CSC/denorm changes, HDR/color-management transitions, and suspend/resume.
- Validate HDMI/DP audio and packet generation on high-numbered instances that can use `AFMT5` and `VPG9`: audio playback, IEC 60958 channel status, infoframes, generic packets, ISRC/MPEG metadata, CRC reporting, packet update timing, hotplug, modeset, and stream disable/enable.
- Test ABM/PWM behavior for all represented instances: brightness transitions, ambient/user/target levels, duty-cycle bounds, frame-start updates, double-buffer locks, ACE threshold/slope updates, histogram/luma readback, missed-frame clear behavior, and resume from low-power states.
- Exercise HPO/DP stream mapping and DME paths where supported, including link bring-up, stream assignment, display-clock gating transitions, metadata memory power states, and error recovery.
- Watch kernel logs, display diagnostics, and hardware counters for stuck update-pending bits, missed-frame flags, CRC mismatches, audio dropouts, color corruption, backlight jumps, perfmon counter anomalies, RBBMIF timeout reports, and resume-only failures.

## Cross-Chunk Notes

The previous chunk owns the start of `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_24_25`, including the missing shift macros for region 24/25 fields. The next chunk owns the rest of `DPIA_MU_RBBMIF_TIMEOUT_CTRL`, follow-on DPIA RBBMIF status fields, and then additional generated register families. The final per-file research document should merge adjacent chunks before making whole-file claims about all MPCC OGAM regions, all DPIA timeout/status fields, or the complete DCN 3.5.0 shift/mask namespace.

### subset-b-002077: lines 46527-48843

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 46527-48843

## Scope

This chunk is part of the generated DCN 3.5.0 ASIC register field header for the AMDGPU display stack. It contains only preprocessor constants: 2,218 `#define`s, arranged as 1,109 `__SHIFT` macros paired with 1,109 mask macros for bitfields in display/audio/power/color-management registers. The chunk is not executable code, but it is consumed by the register-access macro layer to build typed shift/mask tables used by DC, DMUB, hubbub, hubp, irq, and MPC code.

## Purpose

The macros encode bit positions and masks for the tail of the DCN 3.5.0 register map. Drivers combine these constants with register offsets from the sibling `dcn_3_5_0_offset.h` file through helpers such as `FD_MASK`, `FD_SHIFT`, `REG_UPDATE`, `REG_GET`, `HUBBUB_SF`, `HUBP_SF`, and `SF`. This chunk covers:

- Azalia/HDA command, response, stream, global capability, interrupt, and DMA-position fields.
- Display clock, symbol clock, stream synchronization, DCCG, DMU, DMCUB, and DWB clock-gating controls.
- DCHUBBUB arbitration, watermark, P-state, C-state, USR retraining, SDPIF security, and MALL controls.
- HUBP0-HUBP3 page-table, MALL, debug, pstate-force, status, and read-line fields.
- Display power-gating domains 22-25 and DCPG interrupt status/control fields.
- MPCC/MCM color-management registers, especially shaper LUTs, 3DLUT/1DLUT RAM programming fields, region descriptors, and memory power-state controls.

## Important API Surface

There are no functions or types in the chunk. The API surface is macro names with the pattern:

- `REGISTER__FIELD__SHIFT`, whose value is the starting bit number.
- `REGISTER__FIELD_MASK`, whose value is the field mask in the register.

Important register families visible in this range include:

- `AZCONTROLLER1_*`, `AZENDPOINT1_*`, `AZINPUTENDPOINT1_*`, `AZALIA_*`, `GLOBAL_*`, `INTERRUPT_*`, `STREAM_SYNCHRONIZATION`, and `WALL_CLOCK_COUNTER` for HDA/Azalia command rings, RIRB/CORB DMA, immediate commands, payload capability, interrupts, stream sync, and wall clock state.
- `DCCG_GATE_DISABLE_CNTL*`, `DPPCLK_CTRL`, `DSCCLK_DTO_CTRL`, `PHY*SYMCLK_CLOCK_CNTL`, `SYMCLK*`, `DMU_CLK_CNTL`, `DMCUB_SMU_INTERRUPT_CNTL`, `ZSC_CNTL`, `ZPR_CLK_UNGATE_DELAY`, and `DWB_ENABLE_CLK_CTRL` for clock source selection, DTO enables, fine-grain clock-gating repetition disables, clock-stop allowance, and low-power LONO controls.
- `DCHUBBUB_ARB_*`, `DCHUBBUB_SDPIF_*`, `COMPBUF_MEM_PWR_CTRL_2`, `MMHUBBUB_CLOCK_CNTL`, `MCIF_WB_*`, and `SDPIF_REQUEST_RATE_LIMIT` for display memory arbitration, pstate watermark programming, security levels, compression-buffer latency, writeback pstate latency, and request throttling.
- `HUBP[0-3]_*`, `HUBPREQ[0-3]_*`, and `HUBPRET[0-3]_*` for each display pipe's HUBP VM/page-table behavior, MALL selection and status, debug status, UCLK pstate forcing, self-refresh/pstate/USR status signals, and vblank read-line limits.
- `DOMAIN22_PG_*` through `DOMAIN25_PG_*`, `DCPG_INTERRUPT_STATUS_3`, `DCPG_INTERRUPT_CONTROL_2`, and `DCPG_INTERRUPT_CONTROL_3` for power-gating state and interrupt mask/clear pairs.
- `MPCC[0-3]_MPCC_MOVABLE_CM_LOCATION_CONTROL` and `MPCC_MCM[0-1]_*` for movable color-management location, shaper controls, offsets/scales, shaper LUT RAM A/B regions, 3DLUT mode/read-write/data/index, post-1DLUT RAM A/B region tables, and MPCC MCM memory power controls.

## Control Flow and Data Flow

This header contributes compile-time constants only. Runtime control flow happens in consumers:

- DCN 3.5 initialization code includes this header beside `dcn_3_5_0_offset.h`, then expands register-list macros into per-block register, mask, and shift structures. For example, `dmub_srv_dcn35_regs_init()` initializes DMUB/DCN35 register offsets and fills `mask`/`shift` fields using `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`.
- Display block code uses macros such as `HUBBUB_SF(...)`, `HUBP_SF(...)`, and `SF(...)` to map these constants into block-specific `*_shift` and `*_mask` structures. Later `REG_UPDATE_*`, `REG_GET`, `REG_SET_*`, and similar helpers apply the masks and shifts to memory-mapped I/O reads/writes.
- Color-management programming in the MPC path depends on the MPCC/MCM fields here to write LUT indices, LUT data, 3DLUT RAM selection, shaper region descriptors, and post-1DLUT RAM A/B tables. The generated constants decide the exact bit packing, but the algorithms and sequencing live in MPC source files.
- Hubbub and HUBP watermarks/MALL/pstate decisions are made elsewhere; this chunk only provides the bit positions for controls and status reads such as `DCHUBBUB_ARB_USR_RETRAINING_CNTL`, `HUBP*_HUBP_MALL_STATUS`, and `HUBPREQ*_HUBPREQ_STATUS_REG*`.

## State and Persistence

The header itself stores no state and persists nothing at runtime. The values describe persistent hardware register fields:

- Writes to control bits persist in MMIO registers until reset, power-gate transitions, firmware, or later driver writes alter them.
- Status bits expose current hardware state, interrupt latch state, or clear-on-write behavior depending on the register family. Examples in this chunk include RBBMIF invalid-access status, CORB/RIRB memory-error/response interrupts, domain power up/down status, DMCUB interrupt status, HUBP MALL status, and HUBPREQ pstate/self-refresh/flip status.
- LUT and color-management data fields drive hardware RAM programming. Index/data/write-enable fields are stateful hardware interfaces, so incorrect shift/mask constants would corrupt LUT writes rather than just a local software value.
- Power and clock-gating fields such as `*_PWR_FORCE`, `*_PWR_DIS`, `*_LOW_PWR_MODE`, `*_CLK_GATE_DISABLE`, and `*_ALLOW_DS_CLKSTOP` directly affect low-power behavior and can change power/performance stability.

## Dependencies and Integration Points

Key dependencies are the generated register offset header for the same ASIC and the display register-access macros that expect the exact naming convention used here. The chunk integrates with:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which includes `dcn_3_5_0_sh_mask.h` and fills DMUB register masks/shifts.
- DC hubbub headers such as `display/dc/hubbub/dcn35/dcn35_hubbub.h`, where the DCHUBBUB fields in this chunk are selected into hubbub mask/shift tables.
- HUBP headers derived from DCN32/DCN35 patterns, which use `HUBP0_*` names as template fields for per-instance HUBP programming.
- MPC headers and implementations, especially the DCN32-era MPC color-management surface, which reference `MPCC_MCM0_*` shaper, 3DLUT, 1DLUT, and memory-power fields.
- IRQ service code that includes the DCN35 mask header and uses display interrupt status/control masks to decode and clear hardware events.
- Firmware/DMUB paths where DMCUB scratch, interrupt, security, SMU-message, and clock fields must match firmware-visible register semantics.

## Risks

The primary risk is silent hardware misprogramming: these constants are usually trusted by generated accessors, so a one-bit shift or mask error can write the wrong field without compiler warnings. High-risk groups in this chunk are:

- MPCC/MCM LUT region and data fields, because color pipeline corruption can appear as subtle display color errors, failed HDR/gamma programming, or invalid RAM writes.
- DCHUBBUB and HUBPREQ pstate/watermark fields, because bad masks can cause underruns, stutter, hangs during memory-clock changes, or incorrect self-refresh gating.
- HUBP MALL and SubVP fields, because misuse can break static-screen optimization, cursor retrieval, MALL prefetch/retrieve sequencing, or sub-viewport memory fetch behavior.
- Power/clock-gating and DCPG interrupt fields, because incorrect mask/clear bits can leave domains powered unexpectedly, fail to clear interrupts, or disable needed clocks.
- Azalia/CORB/RIRB/immediate-command fields, because ring pointer, DMA-enable, and response-status bit errors affect HDMI/DP audio command transport.
- The chunk ends mid-family at `MPCC_MCM1_MPCC_MCM_SHAPER_RAMA_REGION_10_11__...__SHIFT`, so whole-file research must reconcile continuation chunks before drawing final conclusions about complete MPCC_MCM1 coverage.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build-time: compile configurations that include DCN 3.5.0 display support should catch missing or renamed macros when register-list macros expand.
- Static consistency: for each field, `MASK >> SHIFT` should form the expected field width; every `__SHIFT` in this chunk has a corresponding mask macro in the same range.
- Cross-version checks: compare against `dcn_3_5_1_sh_mask.h` and adjacent DCN versions for expected identical fields or deliberate differences. This chunk appears structurally aligned with DCN 3.5.1 for sampled fields such as `AZCONTROLLER1_CORB_CONTROL`, `DCHUBBUB_ARB_USR_RETRAINING_CNTL`, `HUBP0_DCHUBP_MALL_CONFIG`, and `MPCC_MCM0_MPCC_MCM_SHAPER_CONTROL`.
- Runtime display tests: modeset, multi-plane, cursor, SubVP/MALL, pstate-change, self-refresh, writeback, and suspend/resume paths exercise HUBP/DCHUBBUB/clock/power fields.
- Color tests: gamma, shaper, 3DLUT, post-1DLUT, HDR, and color-management validation exercise the MPCC/MCM field set.
- Audio tests: HDMI/DP audio enumeration and playback exercise Azalia CORB/RIRB, immediate command, stream interrupt, and DMA-position fields.
- Interrupt tests: hotplug, vblank, DCPG power up/down, DMCUB power/resync triggers, and interrupt clear/mask behavior indicate whether status/control fields are correctly packed.

### subset-b-002078: lines 48844-51064

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 48844-51064

## Scope

This chunk is a generated DCN 3.5.0 ASIC register-field shift/mask range for the AMD display MPCC movable color-management (`MPCC_MCM`) blocks. It contains `#define` constants only; there are no C functions, structs, or executable control flow in this header slice. The range starts inside the `MPCC_MCM1_MPCC_MCM_SHAPER_RAMA_REGION_10_11` family, covers the rest of the `MPCC_MCM1` movable color-management block, all visible `MPCC_MCM2` movable color-management definitions, and ends partway through the `MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_20_21` family.

Within the requested lines I counted 2,217 generated field constants across `MPCC_MCM1`, `MPCC_MCM2`, and `MPCC_MCM3`. The main repeated register families are:

- Shaper LUT RAM A/B region programming: `MPCC_MCM_SHAPER_RAMA_REGION_*`, `MPCC_MCM_SHAPER_RAMB_REGION_*`, `*_START_CNTL_{B,G,R}`, and `*_END_CNTL_{B,G,R}`.
- Movable color-management 3D LUT programming: `MPCC_MCM_3DLUT_MODE`, `MPCC_MCM_3DLUT_INDEX`, `MPCC_MCM_3DLUT_DATA`, `MPCC_MCM_3DLUT_DATA_30BIT`, `MPCC_MCM_3DLUT_READ_WRITE_CONTROL`, output normalization, and RGB output offset/scale registers.
- Post-blend 1D LUT programming: `MPCC_MCM_1DLUT_CONTROL`, `MPCC_MCM_1DLUT_LUT_INDEX`, `MPCC_MCM_1DLUT_LUT_DATA`, `MPCC_MCM_1DLUT_LUT_CONTROL`, and RAM A/B PWL region/start/end/offset registers.
- Memory power control: `MPCC_MCM_MEM_PWR_CTRL` for shaper, 3D LUT, and 1D LUT memories.

## Purpose

These macros are the bit-level contract between the DCN 3.5.0 display driver and the MPCC movable color-management hardware. Each `__SHIFT` macro gives the low bit of a field and each `_MASK` macro gives the field mask inside a 32-bit MMIO register. Runtime code combines these with matching offset macros from `dcn_3_5_0_offset.h` and register-list declarations to perform `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` operations without spelling raw bit positions in driver logic.

The covered fields support color-processing stages attached to MPCC instances:

- The shaper LUT maps input values before the 3D LUT using RAM A/RAM B double-buffering.
- The 3D LUT stores tetrahedral LUT data in multiple RAM banks and supports both 17-cube/9-cube sizes and 12-bit/30-bit packed access modes.
- The post-blend 1D LUT applies a PWL/gamma correction stage after the 3D LUT, also with RAM A/RAM B double-buffering.
- The memory power fields let the driver force or observe low-power states for shaper, 3D LUT, and 1D LUT memories.

## Important APIs And Data Shapes

This header chunk does not define callable APIs, but it is consumed by the DC register helper API. The important macro shape is:

- `MPCC_MCMn_REGISTER__FIELD__SHIFT`: field shift for instance `n`.
- `MPCC_MCMn_REGISTER__FIELD_MASK`: field mask for instance `n`.

The corresponding runtime data structures are populated by token-pasting macros in the display resource and MPC layers:

- `MPC_REG_LIST_DCN3_2` and `MPC_REG_LIST_DCN3_2_RI` enumerate MPCC MCM registers such as `MPCC_MCM_SHAPER_RAMA_REGION_10_11`, `MPCC_MCM_3DLUT_MODE`, `MPCC_MCM_1DLUT_RAMA_REGION_32_33`, and `MPCC_MCM_MEM_PWR_CTRL`.
- `MPC_COMMON_MASK_SH_LIST_DCN32(__SHIFT)` and `MPC_COMMON_MASK_SH_LIST_DCN32(_MASK)` load shift and mask values into `struct dcn30_mpc_shift` and `struct dcn30_mpc_mask`.
- The generated definitions here are accessed through `mpc30->mpc_shift->FIELD` and `mpc30->mpc_mask->FIELD` via the `FN(reg_name, field_name)` macro used by `reg_helper.h`.

The field encodings line up with the MPCC MCM enum definitions in `include/soc24_enum.h` and similar SoC enum headers. Relevant enum domains include `MPCC_MCM_3DLUT_30BIT_ENUM`, `MPCC_MCM_3DLUT_RAM_SEL`, `MPCC_MCM_3DLUT_SIZE_ENUM`, `MPCC_MCM_GAMMA_LUT_MODE_ENUM`, `MPCC_MCM_GAMMA_LUT_SEL_ENUM`, `MPCC_MCM_LUT_NUM_SEG`, `MPCC_MCM_LUT_RAM_SEL`, `MPCC_MCM_LUT_READ_COLOR_SEL`, `MPCC_MCM_MEM_PWR_FORCE_ENUM`, and `MPCC_MCM_MEM_PWR_STATE_ENUM`.

## Runtime Control Flow

The generated macros participate in several runtime flows, primarily through `display/dc/mpc/dcn32/dcn32_mpc.c`, which is reused by DCN 3.5-family resources.

For post-blend 1D LUT programming:

1. `mpc32_program_post1dlut()` reads `MPCC_MCM_1DLUT_MODE_CURRENT` and `MPCC_MCM_1DLUT_SELECT_CURRENT` from `MPCC_MCM_1DLUT_CONTROL[mpcc_id]` to determine the active RAM.
2. It powers the 1D LUT memory through `MPCC_MCM_MEM_PWR_CTRL` fields such as `MPCC_MCM_1DLUT_MEM_PWR_DIS`, `MPCC_MCM_1DLUT_MEM_PWR_FORCE`, and `MPCC_MCM_1DLUT_MEM_PWR_STATE`.
3. It configures write color masks and RAM host selection through `MPCC_MCM_1DLUT_LUT_CONTROL`.
4. It programs RAM A or RAM B PWL region settings through `MPCC_MCM_1DLUT_RAMA_*` or `MPCC_MCM_1DLUT_RAMB_*` registers, using region fields for LUT offsets and segment counts.
5. It writes LUT samples through `MPCC_MCM_1DLUT_LUT_INDEX` and `MPCC_MCM_1DLUT_LUT_DATA`, then flips `MPCC_MCM_1DLUT_MODE` and `MPCC_MCM_1DLUT_SELECT` to activate the newly written RAM.

For shaper LUT programming:

1. `mpc32_get_shaper_current()` reads `MPCC_MCM_SHAPER_MODE_CURRENT`.
2. `mpc32_configure_shaper_lut()` sets `MPCC_MCM_SHAPER_LUT_WRITE_EN_MASK`, selects RAM A or B, and resets `MPCC_MCM_SHAPER_LUT_INDEX`.
3. `mpc32_program_shaper_luta_settings()` and `mpc32_program_shaper_lutb_settings()` write start/end control and all 34 exponential region descriptors, including the fields covered at the beginning of this chunk for `MPCC_MCM1` RAM A regions 10-33 and the full RAM B region list.
4. `mpc32_program_shaper_lut()` writes PWL sample data through `MPCC_MCM_SHAPER_LUT_DATA`.
5. `MPCC_MCM_SHAPER_LUT_MODE` selects bypass, RAM A, or RAM B.

For 3D LUT programming:

1. `get3dlut_config()` reads `MPCC_MCM_3DLUT_MODE_CURRENT`, `MPCC_MCM_3DLUT_30BIT_EN`, and `MPCC_MCM_3DLUT_SIZE`.
2. `mpc32_select_3dlut_ram()` chooses the target RAM and 12-bit/30-bit access mode with `MPCC_MCM_3DLUT_RAM_SEL` and `MPCC_MCM_3DLUT_30BIT_EN`.
3. `mpc32_select_3dlut_ram_mask()` sets `MPCC_MCM_3DLUT_WRITE_EN_MASK` and resets `MPCC_MCM_3DLUT_INDEX`.
4. `mpc32_set3dlut_ram12()` writes paired samples through `MPCC_MCM_3DLUT_DATA0` and `MPCC_MCM_3DLUT_DATA1`; `mpc32_set3dlut_ram10()` writes packed 30-bit values through `MPCC_MCM_3DLUT_DATA_30BIT`.
5. `mpc32_set_3dlut_mode()` sets `MPCC_MCM_3DLUT_MODE` and `MPCC_MCM_3DLUT_SIZE` after RAM programming.

## State And Persistence

The state represented by this chunk persists in hardware registers, not in software storage:

- Current active RAM state is exposed through fields such as `MPCC_MCM_SHAPER_MODE_CURRENT`, `MPCC_MCM_1DLUT_MODE_CURRENT`, `MPCC_MCM_1DLUT_SELECT_CURRENT`, and `MPCC_MCM_3DLUT_MODE_CURRENT`.
- LUT content persists in MPCC MCM RAMs until overwritten, reset, or powered down according to hardware behavior.
- Region descriptor registers persist the PWL segmentation model: start coordinate, start segment, end coordinate/base/slope, per-region LUT offset, and per-region number of segments.
- Memory power fields persist hardware power policy and status for shaper, 3D LUT, and 1D LUT memories. The driver may wait for state transitions before writing LUT memory.

The software-visible persistence is indirect: resource construction stores register offsets, masks, and shifts in per-device MPC register tables. The numeric constants in this generated header must remain synchronized with the matching offset header and with the MPC register-list macros.

## Dependencies And Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h` supplies the corresponding MMIO register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h` declares the DCN 3.2-style MPCC MCM register list consumed by DCN 3.5/3.5.1 resource files.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c` instantiates `MPC_REG_LIST_DCN3_2_RI(0..3)` and the DCN32 MPC mask/shift list for a 3.5-family resource.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.c` performs runtime shaper, 3D LUT, 1D LUT, and memory-power programming with these fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_cm_common.c` provides `cm_helper_program_gamcor_xfer_func()` and `cm3_helper_translate_curve_to_hw_format()`, which produce and program the PWL region descriptors used by these fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h` defines symbolic enum values for MPCC MCM modes, RAM selections, segment counts, and memory-power states.

The source-tree integration pattern is generated-register token pasting. A register field such as `MPCC_MCM_1DLUT_RAMA_EXP_REGION0_LUT_OFFSET` appears in runtime code without an instance number, while the mask/shift list resolves it through a representative instance macro such as `MPCC_MCM0_*`; the per-instance offset arrays select `MPCC_MCM1`, `MPCC_MCM2`, or `MPCC_MCM3` at runtime.

## Risks

- Numeric bitfield drift is high impact. If a shift or mask is wrong, LUT programming can silently corrupt color output, select the wrong RAM, write wrong LUT samples, or mis-handle memory power state.
- The chunk starts and ends in the middle of repeated generated families. A reviewer must merge with adjacent chunks before making whole-file completeness claims for `MPCC_MCM1` or `MPCC_MCM3`.
- The RAM A/B double-buffering model depends on current-state fields matching mode/select fields. Wrong masks for `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `*_LUT_MODE`, or `*_LUT_SELECT` can cause updates to target the active RAM or fail to activate new LUT content.
- The region descriptors use compact bitfields: LUT offset uses the low 9 bits, segment count uses a 3-bit field at bit 12 or 28, and paired-region registers pack two regions per word. Off-by-one generation errors in region numbering or masks would be difficult to catch through compilation.
- `MPCC_MCM_MEM_PWR_CTRL` fields control and observe low-power states. Bad masks can make the driver wait on the wrong status field or power down LUT memory while programming it.
- Some runtime code writes RAMB shaper registers with field names carrying `RAMA` in the field token. That works only because the generated field names and masks are intentionally compatible across RAM A/B variants; changing the generated naming convention would break token-pasted access.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for DCN 3.5/3.5.1 display code with `dcn_3_5_0_sh_mask.h`, `dcn_3_5_0_offset.h`, and the DCN32 MPC register/mask lists enabled. Token-paste mismatches should fail compilation.
- KMS color-management tests that exercise shaper LUT, 3D LUT, and post-blend 1D LUT programming on supported hardware.
- Runtime traces or register dumps showing `MPCC_MCM_1DLUT_CONTROL`, `MPCC_MCM_SHAPER_CONTROL`, `MPCC_MCM_3DLUT_MODE`, and `MPCC_MCM_MEM_PWR_CTRL` fields changing as expected when enabling, disabling, and swapping LUTs.
- IGT/DRM color tests with gamma, degamma, CTM/3D LUT, PQ, HLG, and gamma 2.2 transfer functions. The PWL conversion path should produce expected segment distributions and no `DC_LOG_ERROR("Losing delta precision while programming shaper LUT.")` messages.
- Low-power validation with `enable_mem_low_power.bits.mpc` and `.cm` toggled. `REG_WAIT` on `MPCC_MCM_SHAPER_MEM_PWR_STATE`, `MPCC_MCM_3DLUT_MEM_PWR_STATE`, and `MPCC_MCM_1DLUT_MEM_PWR_STATE` should complete without hitting debug breaks.
- Cross-header diffing against adjacent generated DCN headers, such as `dcn_3_2_0_sh_mask.h` and `dcn_3_5_1_sh_mask.h`, for matching MPCC MCM field layout where hardware compatibility is expected.

## Chunk Boundary Notes

This chunk begins after the first lines for `MPCC_MCM1_MPCC_MCM_SHAPER_RAMA_REGION_10_11`; the corresponding `REGION_0_1` through early `REGION_10_11` definitions are in the previous chunk. It ends at `MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_20_21__MPCC_MCM_1DLUT_RAMB_EXP_REGION21_NUM_SEGMENTS__SHIFT`; the remaining masks for that register, later RAMB regions, and the likely `MPCC_MCM3_MPCC_MCM_MEM_PWR_CTRL` fields continue in the next chunk. The final per-file research document should merge these boundaries before summarizing complete per-instance coverage.

### subset-b-002079: lines 51065-53412

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 51065-53412

## Scope

This chunk covers generated DCN 3.5.0 ASIC register shift/mask macros from `dcn_3_5_0_sh_mask.h`, lines 51065-53412. It contains no C functions or runtime control flow; its role is to provide compile-time bitfield metadata for AMD display driver register access helpers.

The slice contains 2,217 `#define` entries: 1,109 `__SHIFT` constants and 1,108 `_MASK` constants. The one-entry imbalance is because this range starts in the middle of the `MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_20_21` field group, so its shift definitions are in an earlier chunk.

## Purpose

The header maps named hardware fields to bit positions and bit masks for DCN 3.5.0 display blocks. Driver code does not normally manipulate these long macro names directly. Instead, block headers use `SF(...)`, `SRI(...)`, `SRI_ARR(...)`, and related macros to build register/field tables, and runtime code then uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and `REG_WRITE` against those tables.

Major hardware areas represented in this chunk:

- MPCC/MCM color memory and 1D LUT RAM region fields, including `MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_20_21` through `REGION_32_33` and `MPCC_MCM3_MPCC_MCM_MEM_PWR_CTRL`.
- OPP/OTG timing, CRC, DRR, long-vblank, and DLPC snapshot/stop-control fields for OTG instances 0-3.
- DP and DIG encoder fields for DP/DIG instances 0-4: DP MSA transmission enable, MST secondary allocation table encryption fields, ALPM scrambled-zero controls, stream/link symbol counters, DIG front-end/back-end clocks and resets, FIFO level, Dolby Vision and TMDS HDMI control fields.
- DIO, DPIA mux, I2C/DDC setup, stream mapper, UNIPHY channel crossbar, DC GPIO drive, PWRSEQ, DSCC, DSC top, and HDMI FRL/stream/TB encoder fields.
- DP 32-bit symbol encoder and DP DPHY symbol fields for DP link encryption and symbol counters.
- DLPC, DPIA MU, DPIA port clocks/resets/TPI status/interrupt/perf-counter fields.
- Azalia/AFMT ACP/audio-packet metadata fields and endpoint clock-gating controls.

## Important APIs, Types, And Macros

This chunk defines macro constants only. The meaningful API contract is the naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the starting bit index for `FIELD`.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask in the 32-bit register value.
- Repeated indexed blocks use a hardware-instance prefix, such as `OTG0_`, `DP3_`, `DIG4_`, `DSCC2_`, `DP_DPHY_SYM321_`, or `DPIA_PORT3`.
- Shared logical fields keep consistent suffix names across instances, which lets block headers refer to a common field name while selecting instance-specific registers.

Representative field groups:

- `MPCC_MCM3_MPCC_MCM_MEM_PWR_CTRL__MPCC_MCM_*`: power force/disable/low-power/state fields for shaper, 3DLUT, and 1DLUT memories.
- `OTGx_OTG_V_COUNT_STOP_CONTROL*`, `OTGx_OTG_DLPC_CONTROL`, and `OTGx_OTG_CRC*_WINDOW*READBACK`: timing-generator stop counters, DLPC snapshots, long-vblank status, and CRC window readbacks.
- `DPx_DP_MSE_SAT*` and `DPx_DP_MSE_SAT*_STATUS`: MST encryption enable/type fields for virtual channels 0-5 and their status mirrors.
- `DPx_DP_STREAM_SYMBOL_COUNT_*` and `DPx_DP_LINK_SYMBOL_COUNT_*`: stream BS, link SR, and cycle counter enable/reset/status fields.
- `DIGx_DIG_FE_CLK_CNTL`, `DIGx_DIG_BE_CLK_CNTL`, `DIGx_DIG_FE_EN_CNTL`, and `DIGx_DIG_BE_EN_CNTL`: front-end/back-end mode, clock enable, reset, and gated-clock status fields.
- `DIO_CLK_CNTL`: display IO clock enables and clock-on status for DPIA, USB-C, DPREF, PHY reference, and RX/TMDS paths.
- `HDMI_FRL_ENC_*`, `HDMI_STREAM_ENC_*`, and `HDMI_TB_ENC_*`: HDMI FRL lane/training/jitter/memory controls, stream encoder clock/FIFO controls, and TMDS/FRL packet-generation controls.
- `DPIA_MU_*`: DPIA microcontroller clock gates, per-port reset completion, TPI credit status, interrupts, microsecond reference, port hidden status, glue IO enable, and performance counter controls.
- `AZALIA_*` and `AZF0ENDPOINT*`: ACP packet data/index metadata and endpoint fine-grain clock-gating repeat disable fields.

## Control Flow

There is no executable control flow in this chunk. Control flow appears in consumers that include this header:

- `display/dc/resource/dcn35/dcn35_resource.c` includes this header while defining DCN 3.5 resource register tables.
- `display/dc/irq/dcn35/irq_service_dcn35.c` includes it for interrupt source/status/ack bit definitions.
- `display/dmub/src/dmub_dcn35.c` includes it for DMUB-facing DCN 3.5 register programming.

Within display block code, these macros are consumed indirectly. For example, `dcn35_optc.h` maps `OTG0_OTG_V_COUNT_STOP_CONTROL` / `OTG_V_COUNT_STOP` through `SF(...)`, and `dcn35_optc.c` writes `OTG_V_COUNT_STOP_CONTROL` and `OTG_V_COUNT_STOP_CONTROL2` while programming vertical count stop behavior. The field widths here therefore bound the values that those runtime helpers can encode into MMIO writes.

## State And Persistence Behavior

This header stores no runtime state. It describes hardware-backed state that persists in registers until reset, power transition, driver reprogramming, or hardware self-clear semantics. Important state surfaces in this chunk include:

- MPCC MCM memory power state and force/disable controls.
- OTG stop-count, long-vblank, CRC readback, and DLPC snapshot/status fields.
- DP MST encryption enable/type status, ALPM status, and stream/link counter status.
- HDMI FRL jitter exceed and meter-buffer overflow status, HDMI stream FIFO calibration/status/error fields, and HDMI TB packet/error/CRC fields.
- DSCC end-of-frame interrupt status and enable fields.
- DPIA MU reset-done, timeout interrupt, TPI credit, port-hidden, and performance-counter state.
- Azalia/ACP endpoint packet configuration and endpoint clock-gating controls.

Persistence risk is indirect: incorrect mask/shift values make higher-level register helpers preserve, clear, or overwrite the wrong bits. That can produce long-lived hardware misconfiguration until the affected block is reset or reinitialized.

## Dependencies And Integration Points

Primary dependency direction is from generated register headers into DC display code:

- `dcn_3_5_0_sh_mask.h` is paired with DCN 3.5.0 register-address headers in `include/asic_reg/dcn/`.
- Display resource and block headers include both address and mask/shift metadata to instantiate per-generation register tables.
- Runtime display code relies on AMD's register helper macros to combine register addresses, masks, and shifts.
- Adjacent generation headers such as `dcn_3_5_1_sh_mask.h`, `dcn_3_6_0_sh_mask.h`, and `dcn_4_2_0_sh_mask.h` carry similarly named fields; cross-generation copy mistakes are plausible when fields move or widths change.

Notable integration points visible from repository search:

- `display/dc/mpc/dcn32/dcn32_mpc.c` uses logical `MPCC_MCM_MEM_PWR_CTRL` fields via register helpers for LUT memory power sequencing and waits on power-state fields.
- `display/dc/optc/dcn35/dcn35_optc.c` writes OTG count-stop controls that are represented by this chunk's `OTGx_OTG_V_COUNT_STOP_CONTROL*` fields.
- `display/dc/resource/dcn35/dcn35_resource.h` maps OTG register arrays with `SRI_ARR(...)`, tying the per-instance masks here to DCN 3.5 resource construction.

## Risks

- Generated macro drift: a wrong bit position or mask compiles cleanly but silently corrupts MMIO programming.
- Partial-field overlap: many fields are tightly packed into 32-bit registers; an incorrect mask can affect adjacent enable/status bits.
- Instance skew: repeated OTG/DP/DIG/DPIA families must remain consistent for all instances unless the hardware truly differs. A single bad instance macro can create port-specific failures.
- Status/control ambiguity: several registers contain both control and status or clear bits, such as reset-done, overflow, interrupt ack/status, and packet-error clear fields. Misusing masks can accidentally clear latched hardware state.
- Range-bound values: fields such as OTG vcount stop, HDMI packet line references, FIFO levels, DPIA counts, and jitter thresholds have fixed widths. Callers must clamp or validate values before using register helpers.
- Chunk boundary risk: this range starts mid-`MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_20_21` group and ends mid-`AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`; the merge lane must combine adjacent chunks before treating either group as complete.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/display behavior based:

- Build coverage for DCN 3.5 display code that includes `dcn_3_5_0_sh_mask.h`, especially `dcn35_resource.c`, `irq_service_dcn35.c`, and `dmub_dcn35.c`.
- Macro table consistency checks comparing `_MASK`/`__SHIFT` pairs for same field names and verifying masks align with shifts and expected widths.
- Cross-generation diffs against `dcn_3_5_1_sh_mask.h` for fields that should remain identical between DCN 3.5 variants.
- Display bring-up tests covering DP/HDMI link enable, MST encryption, ALPM, Dolby Vision/TMDS mode programming, HDMI FRL training, DSC/DSCC paths, and DPIA USB-C paths.
- Runtime register readback tests where available: OTG vcount stop/readback, CRC windows, FIFO status/calibration, DP/HDMI symbol counters, DPIA interrupt/status/perf counters, and memory power-state waits.

## Chunk Notes For Merge Lane

This is a middle chunk of a large generated header. The final per-file research should describe the whole header as a generated DCN 3.5.0 register mask/shift contract, not as isolated hand-written logic. Adjacent chunks are needed to cover the opening include guards/license/generation context, earlier MPCC register families, and the trailing `AZF0ENDPOINT3` masks plus file footer.

### subset-b-002080: lines 53413-53485

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 53413-53485

## Purpose

This chunk is the tail of the generated DCN 3.5.0 shift/mask header for AMD display/audio hardware registers. It defines bit masks for Azalia/HDA function-0 endpoint pin-control ACP data and a fine-grain clock-gating repeat-disable bit for output endpoints 3 through 7. These are not executable routines; they are compile-time register field descriptors used by AMDGPU display/audio code when constructing or decoding register values.

The covered lines begin in the middle of endpoint 3's `AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA` field set and then repeat the complete field layout for endpoints 4, 5, 6, and 7. The final line closes the `_dcn_3_5_0_SH_MASK_HEADER` include guard.

## Important macros and register fields

- `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA__SUPPORTS_AI_MASK` through `...__ACP_TYPE_DEPENDENT_BYTE1_MASK` expose the endpoint 3 ACP data masks at bits 6, 7, 8-9, 16-23, and 24-31. The corresponding shifts for endpoint 3 are immediately before this chunk, at lines 53406-53411.
- `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA__*`, `AZF0ENDPOINT5_...`, `AZF0ENDPOINT6_...`, and `AZF0ENDPOINT7_...` define both shifts and masks for five ACP data fields:
  - `ACP_INDEX`: shift 0, mask `0x0000003f`, a 6-bit ACP payload/index selector.
  - `SUPPORTS_AI`: shift 6, mask `0x00000040`, a one-bit capability flag for audio information support.
  - `ACP_PACKET_ENABLE`: shift 7, mask `0x00000080`, a one-bit enable for ACP packet emission/reporting.
  - `ACP_TYPE`: shift 8, mask `0x00000300`, a 2-bit ACP type selector.
  - `ACP_TYPE_DEPENDENT_BYTE0` and `ACP_TYPE_DEPENDENT_BYTE1`: shifts 16 and 24, masks `0x00ff0000` and `0xff000000`, two 8-bit payload bytes whose interpretation depends on `ACP_TYPE`.
- `AZF0ENDPOINT3_AZALIA_F0_ENDPOINT_FGCG_REP_DIS__ENDPOINT_FGCG_REP_DIS_{SHIFT,MASK}` through endpoint 7 define a single bit at bit 0 for the endpoint fine-grain clock-gating repeat-disable register.

The companion DCN 3.5.0 offset header places each endpoint's `AZALIA_F0_ENDPOINT_FGCG_REP_DIS` indirect register at offset `0x0070` for endpoints 3-7. The same offset header's endpoint blocks around `0x0025`-`0x0028` do not expose an `ixAZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA` macro in this tree, although newer/neighboring generated headers such as DCN 4.1.0 do expose the ACP data register at `0x0027`. That makes this chunk mostly a field-definition surface until paired with a valid address macro or indirect access path.

## Control flow and usage model

There is no runtime control flow in this header. Consumers include it through ASIC-specific register packs, combine the `_MASK` and `__SHIFT` constants with register access helpers, and then read/modify/write the underlying MMIO or indexed endpoint registers. Typical generated-register usage in this driver family is:

1. Select the ASIC-specific offset and shift/mask headers during display/audio IP initialization.
2. Use the offset macro to locate an indexed Azalia endpoint register.
3. Use the field mask/shift macro to encode a field value or extract one from a hardware register value.
4. Submit the final value through AMDGPU/DC register access wrappers.

For the `ENDPOINT_FGCG_REP_DIS` bit, the flow is a normal one-bit hardware control: the driver can read the current endpoint clock-gating repeat behavior, set or clear bit 0, and write it back. For `ACP_DATA`, the flow is a packed metadata operation: the endpoint's ACP index, support flag, enable bit, type, and dependent bytes share one 32-bit register value.

## State and persistence behavior

The macros do not hold state. The persistent state is in GPU hardware registers for each endpoint. Values written through these masks can persist for the lifetime of the display/audio hardware context and may be reset by GPU reset, display IP reset, suspend/resume, modeset reinitialization, or audio endpoint reprogramming. Because endpoints 3-7 use identical field layouts, state must be tracked by endpoint selection/addressing, not by field encoding.

`ACP_PACKET_ENABLE`, `ACP_TYPE`, and the type-dependent bytes are especially stateful from the hardware perspective: stale values could leave a pin advertising or sending the wrong ACP metadata. `ENDPOINT_FGCG_REP_DIS` affects clock-gating behavior and can influence power/performance state rather than externally visible packet contents.

## Dependencies and integration points

- Depends on `dcn_3_5_0_offset.h` or another generated offset source to provide the register address/index. In this tree, `ENDPOINT_FGCG_REP_DIS` offsets exist for endpoints 3-7 at `0x0070`.
- Integrates with AMDGPU/DC register helper macros that know how to apply generated `*_MASK` and `*__SHIFT` symbols.
- Sits under `drivers/gpu/drm/amd/include/asic_reg/dcn`, so it is ASIC/IP-version-specific data rather than reusable business logic.
- Aligns with adjacent generated headers (`dcn_3_5_1_sh_mask.h`, `dcn_4_1_0_sh_mask.h`) that repeat the same endpoint ACP field encodings, indicating the layout is stable across nearby DCN versions.
- The endpoint registers are part of the Azalia/HDA display-audio path, tying display connector/audio pin programming to the AMDGPU DRM display stack and, indirectly, Linux HDA/HDMI/DP audio behavior.

## Risks and edge cases

- Generated-header mismatch: this chunk defines `AZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA` masks, but the DCN 3.5.0 offset header search did not find corresponding `ix...ACP_DATA` offsets. Code using these masks needs a verified address source; otherwise the masks are orphaned or require indirect addressing not represented by the expected offset macro.
- Endpoint copy/paste drift: endpoints 3-7 should remain bit-identical. A single shifted mask or endpoint-number typo would silently target the wrong register field.
- Reserved-bit corruption: packed ACP writes must preserve bits outside the declared masks. Blind full-register writes could alter undocumented/reserved hardware state.
- Width truncation: `ACP_INDEX` is only 6 bits, `ACP_TYPE` is 2 bits, and dependent bytes are 8 bits. Callers must clamp or validate before shifting.
- Power-management impact: changing `ENDPOINT_FGCG_REP_DIS` can disable clock-gating repeat behavior and increase power draw or mask timing bugs.
- Hardware-visible audio regressions: incorrect ACP data can affect audio/content-protection/info packet behavior on HDMI/DP endpoints and may appear only with specific sinks.

## Test signals

- Build coverage: compile AMDGPU/DC with DCN 3.5.0 enabled and treat missing register or field macro references as a generated-header integration failure.
- Header consistency checks: compare endpoint 3-7 field masks/shifts against endpoint 0-2 in the same header and against `dcn_3_5_1_sh_mask.h` for unchanged layouts.
- Offset/mask reconciliation: verify every field group used by code has a matching offset macro or documented indirect-access path; specifically check whether `AZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA` should have an offset at `0x0027` for DCN 3.5.0.
- Runtime register tests on supported hardware: read endpoint `ENDPOINT_FGCG_REP_DIS` before and after display/audio init, suspend/resume, and modeset to confirm bit preservation expectations.
- Audio functional tests: validate HDMI/DP audio enumeration, channel layouts, and sink behavior across endpoints 3-7 when ACP packet programming is exercised.
- Power-management tests: compare idle/display-audio power behavior before and after any code path that writes `ENDPOINT_FGCG_REP_DIS`.
