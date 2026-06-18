# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002218`: lines 1-3171, `Docs/researches/chunks/subset-b-002218_research.md`
- `subset-b-002219`: lines 3172-5538, `Docs/researches/chunks/subset-b-002219_research.md`
- `subset-b-002220`: lines 5539-7886, `Docs/researches/chunks/subset-b-002220_research.md`
- `subset-b-002221`: lines 7887-10355, `Docs/researches/chunks/subset-b-002221_research.md`
- `subset-b-002222`: lines 10356-12776, `Docs/researches/chunks/subset-b-002222_research.md`
- `subset-b-002223`: lines 12777-15093, `Docs/researches/chunks/subset-b-002223_research.md`
- `subset-b-002224`: lines 15094-17728, `Docs/researches/chunks/subset-b-002224_research.md`
- `subset-b-002225`: lines 17729-20256, `Docs/researches/chunks/subset-b-002225_research.md`
- `subset-b-002226`: lines 20257-22731, `Docs/researches/chunks/subset-b-002226_research.md`
- `subset-b-002227`: lines 22732-25252, `Docs/researches/chunks/subset-b-002227_research.md`
- `subset-b-002228`: lines 25253-27781, `Docs/researches/chunks/subset-b-002228_research.md`
- `subset-b-002229`: lines 27782-30308, `Docs/researches/chunks/subset-b-002229_research.md`
- `subset-b-002230`: lines 30309-32771, `Docs/researches/chunks/subset-b-002230_research.md`
- `subset-b-002231`: lines 32772-35325, `Docs/researches/chunks/subset-b-002231_research.md`
- `subset-b-002232`: lines 35326-37792, `Docs/researches/chunks/subset-b-002232_research.md`
- `subset-b-002233`: lines 37793-40200, `Docs/researches/chunks/subset-b-002233_research.md`
- `subset-b-002234`: lines 40201-42616, `Docs/researches/chunks/subset-b-002234_research.md`
- `subset-b-002235`: lines 42617-45015, `Docs/researches/chunks/subset-b-002235_research.md`
- `subset-b-002236`: lines 45016-47434, `Docs/researches/chunks/subset-b-002236_research.md`
- `subset-b-002237`: lines 47435-49893, `Docs/researches/chunks/subset-b-002237_research.md`
- `subset-b-002238`: lines 49894-52359, `Docs/researches/chunks/subset-b-002238_research.md`
- `subset-b-002239`: lines 52360-54779, `Docs/researches/chunks/subset-b-002239_research.md`
- `subset-b-002240`: lines 54780-57274, `Docs/researches/chunks/subset-b-002240_research.md`
- `subset-b-002241`: lines 57275-59767, `Docs/researches/chunks/subset-b-002241_research.md`
- `subset-b-002242`: lines 59768-62225, `Docs/researches/chunks/subset-b-002242_research.md`
- `subset-b-002243`: lines 62226-64689, `Docs/researches/chunks/subset-b-002243_research.md`
- `subset-b-002244`: lines 64690-67202, `Docs/researches/chunks/subset-b-002244_research.md`
- `subset-b-002245`: lines 67203-67286, `Docs/researches/chunks/subset-b-002245_research.md`

## Chunk Research

### subset-b-002218: lines 1-3171

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 1-3171

## Purpose

This chunk is generated AMD DCN 4.2.0 register field metadata. It has no executable C logic; it publishes `#define` constants for bit shifts and masks used by AMDGPU display code when packing, updating, and reading fields inside MMIO registers. The companion `dcn_4_2_0_offset.h` header supplies register addresses and base indices, while this header supplies the bit layout within those registers.

The assigned range starts at the header guard and covers early DCN 4.2.0 blocks: HDA/Azalia controller command transport, DC perfmon debug counters, writeback and hubbub debug windows, ODM/RBBMIF/IHC/DMU/DCPG debug buses, DisplayPort/DIG debug-indirect blocks for DP0 through DP4, DIO/APG/DCOH/AUX/HPD/HPO/HDMI/DP stream and symbol encoder debug windows, DP link encoder and DPHY debug buses, Azalia sink-info and CRC result windows, Azalia F0 streams 0 through 15, and the beginning of Azalia endpoint0 codec converter/pin parameter fields. The chunk ends at line 3171 in the middle of `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`; the remaining masks for that register and the rest of the endpoint block are in a later chunk.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU display-driver hardware metadata and is unrelated to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or callbacks in this chunk. Its public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position of a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field.
- Numeric instance suffixes such as `DP0`, `DP4`, `DIG3`, `DP_AUX2`, `HPD4`, `AZF0STREAM15`, and `DP_DPHY_SYM323` describe repeated hardware instances.
- `// addressBlock:` comments group macros by generated hardware address block; they are not consumed by the C preprocessor but are important for human and tooling alignment.

Major macro families in this line range:

- `AZCONTROLLER0_*`: HDA/Azalia CORB and RIRB command/response ring pointers, pointer reset bits, DMA enables, ring sizes/capabilities, memory error status, immediate command write/read windows, immediate command busy/result-valid status, DMA position buffer base-address fields, and wall-clock alias readback.
- `PERFMON_DEBUG*`: debug-indirect perfmon counter low/high words, event selectors, start/stop enable fields, and per-clock counter-off fields for debug clocks 0 through 7.
- `MCIF_WB_DEBUG_ID`, `IDxx_WB_*`, `DCHUBBUB_KEY_STATUS_DEBUG_*`, `ODM[0-3]_OPTC_INPUT_DEBUG*`, `RBBMIF_DEBUG_*`, `IHC_CLIENT_DEBUG_*`, `DMU_MISC_DEBUG_*`, and `DCPG_CONTROL_DEBUG_BUS*`: mostly full-width debug data windows where the generated field covers all 32 bits.
- `DP[0-4]_DP_DEBUG_*`, `DP[0-4]_DP_FE_*`, and `DP[0-4]_DP_FE_DPREFCLK_*`: repeated DisplayPort main, front-end/symbol-clock, and DP reference-clock debug selectors/data fields.
- `DIG[0-4]_DIG_BE_CLKGEN_DEBUG0` and `DIG[0-4]_DIG_FE_DEBUG_ID/VPG_DEBUG*`: repeated digital encoder backend and frontend video packet generator debug windows.
- `DIO_RBBMIF_DEBUG_*`, `DIGA` through `DIGE` RBBMIF/DME/resync FIFO debug fields, `I2C_DEBUG_BUS`, `APG_SOCCLK_DEBUG*`, `APG_ENCCLK_DEBUG*`, and `DCOH_TOP_DEBUG_ID`: DIO and display-output infrastructure debug buses.
- `DP_AUX[0-4]_AUX_DEBUG_DISPCLK_ID`, `DP_AUX[0-4]_DP_AUX_DEBUG_H/I`, `DP_AUX[0-4]_AUX_DEBUG_REFCLK_ID`, and `DP_AUX[0-4]_DP_AUX_DEBUG_A..G/J`: AUX debug windows split by display clock and reference clock domains.
- `HPD[0-4]_HPD_DEBUG_*`, `HPO_TOP_DEBUG_ID`, `HDMI_LINK_ENC_DEBUG_ID`, `HDMI_FRL_ENC_DEBUG_ID`, `HDMI_STREAM_ENC_*_DEBUG*`, `DP_STREAM_ENC[0-3]_*_DEBUG_ID`, and `DP_SYM32_ENC[0-3]_*_DEBUG_ID`: hotplug, high-performance output, HDMI, DP stream encoder, and DP symbol encoder debug IDs/data.
- `DP_LINK_ENC[0-3]_DP_LINK_ENC_DEBUG_*` and `DP_DPHY_SYM32[0-3]_DP_DPHY_SYM32_DEBUG_BUS0..23`: DP link-encoder debug buses and 24 full-width DPHY symbol32 debug buses per instance.
- `AZALIA_F2_CODEC_PIN_CONTROL_*`, `SINK_DESCRIPTION0..17`, `AZALIA_INPUT_CRC[0-1]_CHANNEL[0-7]`, and `AZALIA_CRC[0-1]_CHANNEL[0-7]`: HDMI/DP audio sink identification, sink description bytes, and CRC result channels.
- `AZF0STREAM[0-15]_AZALIA_*`: repeated stream FIFO min/max/latency capability fields, latency counter reset, worst-case/cumulative latency counters, cumulative request counters, and stream debug data.
- `AZF0ENDPOINT0_AZALIA_F0_CODEC_CONVERTER_*`: beginning of endpoint0 codec converter fields for widget capabilities, converter format, channel/stream ID, digital converter controls, stream formats, supported size/rates, stripe control, ramp rate, and the start of pin widget capabilities.

Most definitions are one full-width field at shift `0x0` with mask `0xFFFFFFFFL`, reflecting debug data registers. The non-debug portions use narrower masks for protocol-visible fields such as HDA ring pointers, base-address alignment, FIFO sizes, audio format bits, stream/channel IDs, digital converter status/control bits, sink IDs, and sink-description bytes.

## Control Flow

This header has no runtime control flow. Runtime use is indirect:

1. DCN 4.2.0 display code includes generated offset and shift/mask headers for the ASIC family.
2. Token-pasting helper macros build register and field names from block-specific register tables.
3. Initialization code stores offsets, masks, and shifts in per-block register tables for audio, DIO, AUX/HPD, HPO, DMU, hubbub, writeback, perfmon, and display-output blocks.
4. Operational code later uses register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_UPDATE_N`, and `REG_GET` to access individual hardware fields without corrupting adjacent bits.

The macros do not encode sequencing. Callers must still perform hardware ordering correctly: initialize command rings before enabling DMA, poll immediate command busy/result-valid bits, preserve shared debug selector state, select the right indirect debug ID before reading debug data, reset or latch latency counters before interpreting them, and avoid treating status/readback registers as ordinary writable configuration.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU/display/audio state:

- HDA/Azalia controller fields represent CORB/RIRB pointers and resets, DMA enable bits, base-address alignment, ring sizes, interrupt controls/status, immediate command status, DMA position buffer control, and wall-clock readback.
- Debug-indirect fields expose transient internal hardware state from perfmon clocks, writeback, hubbub, ODM, RBBMIF, IHC, DMU, DCPG, DP, DIG, DIO, APG, DCOH, AUX, HPD, HPO, HDMI, DP link encoders, DP stream/symbol encoders, and DPHY symbol buses.
- Sink-info fields expose Azalia F2 codec pin control identity data: manufacturer ID, product ID, port IDs, sink-description length, and 18 one-byte sink description registers in this chunk.
- CRC result fields expose per-channel Azalia input and output CRC result registers for two result banks.
- Azalia stream fields expose hardware FIFO capability, latency support, latency-counter reset, worst-case/cumulative latency counters, request counters, and stream debug data for streams 0 through 15.
- The partial endpoint0 fields expose codec converter capability/control state: converter and pin audio-widget capability bits, audio stream format fields, channel/stream assignment, digital converter status bits, supported rates/sizes, stripe control, and ramp rate.

Persistence is hardware-defined. Configuration fields usually remain until reprogrammed, power-gated, firmware reset, suspend/resume, or ASIC reset. Debug, CRC, latency, busy, result-valid, pointer reset, and status fields can be volatile, sticky, self-clearing, read-only, write-one-to-clear, or timing-sensitive. This generated mask file does not state access type, reset value, volatility, or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DCN 4.2.0 register database and with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which supplies matching register offsets and base indices.
- DCN 4.2 display resource code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/`, which uses generated register tables for display, audio, output, AUX/HPD, and debug paths.
- DMUB and firmware-mediated display code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/`, which relies on generated register masks for firmware-facing register access where DCN 4.2 is supported.
- Audio and HDA/Azalia integration code that programs command rings, immediate codec commands, stream format/channel IDs, DMA position buffers, latency counters, sink info, and CRC diagnostics.
- Debugfs, tracing, register dump, and diagnostics paths that read the many full-width debug bus fields exposed in this range.

The main integration pattern is C preprocessor token pasting. Macro spelling is therefore a source-level ABI between generated headers and handwritten or templated driver tables. Missing or renamed symbols generally fail at compile time; incorrect numeric masks or shifts can compile cleanly and fail only during hardware exercise.

## Risks And Edge Cases

- Generated masks are untyped constants. A wrong shift or mask can silently update neighboring hardware fields and appear as no audio, broken command transport, bad latency reporting, missed hotplug/AUX events, link-training failures, display blanking, or misleading debug telemetry.
- The chunk boundary is artificial. It cuts off after line 3171, before the complete mask set for `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`; consumers must not evaluate field-pair completeness across this boundary without considering the next chunk.
- Many debug registers are full-width opaque buses. A correct mask still does not tell callers which selected internal signal is present; the debug ID/selector programming and interpretation must come from hardware documentation or matching driver debug tables.
- HDA CORB/RIRB and DMA position base-address fields include unimplemented/alignment bits. Treating masks as full address fields or writing low reserved bits can break DMA ring transport or position reporting.
- Immediate command fields include busy and result-valid bits. Code that uses the masks without polling and timeout handling can race command completion or read stale responses.
- Azalia stream latency counters and CRC result registers are diagnostic state. Reading them without reset/latch semantics can create non-reproducible values, especially across stream enable/disable and suspend/resume.
- Stream format fields pack channel count, bits per sample, base divisor/multiple/rate, and stream type into a small 16-bit area. Bad masks can create valid-looking but wrong audio formats.
- Digital converter fields include audio/control bits such as `DIGEN`, validity, copy/professional/non-audio flags, channel status `CC`, and `KEEPALIVE`. Wrong updates can affect HDMI/DP audio behavior even though the header itself is only metadata.
- Repeated DP/DIG/AUX/HPD instance macros are easy to mix up. Using `DP3` masks with `DP4` offsets or AUX ref-clock debug fields with disp-clock debug offsets can read plausible but unrelated hardware state.
- `I2C_DEBUG_BUS` is a partial-width field at shift `0x12` with mask `0xFFFC0000L`, unlike most nearby full-width debug fields. Generic full-width debug assumptions would be wrong for that register.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 4.2 enabled. Token-pasting register table consumers should catch missing or renamed macros from this range.
- Mechanically verify complete `__SHIFT` macros in lines 1-3171 have matching `_MASK` macros and that masks align with their shifts and intended widths. Exclude the endpoint0 pin-widget capability register that is deliberately cut by the chunk boundary.
- Diff this DCN 4.2.0 range against AMD's authoritative register database and neighboring generated DCN headers when compatibility is expected; focus on non-full-width fields and repeated instance numbering.
- Exercise HDMI/DP audio command paths: CORB/RIRB setup, immediate codec commands, ring pointer reset, DMA position buffer readback, wall-clock readback, stream format/channel mapping, digital converter enable/state, and stream latency counters.
- Exercise audio stream diagnostics for streams 0 through 15: FIFO capability readback, latency-counter reset, worst-case/cumulative latency counts, request counts, and stream debug data.
- Exercise sink-info and CRC diagnostics: manufacturer/product/port ID readback, sink description length and bytes, input CRC result banks, and output CRC result banks.
- Exercise DP0 through DP4 and DIG0 through DIG4 modesets and debug reads across hotplug, link training, link disable/enable, DP AUX transactions, HDMI FRL paths, HPO stream/symbol encoder paths, and suspend/resume.
- Exercise DPHY and link encoder debug readout for all four HPO DP link instances, including all 24 symbol32 debug buses per instance.
- Monitor kernel logs, DC traces, debugfs/register dumps, display output, and audio playback for no-audio, stale immediate responses, ring DMA errors, bad CRC/latency values, hotplug/AUX failures, link-training instability, and incorrect per-instance debug output.

## Cross-Chunk Notes

This is a chunk-level document, not a final per-file report. Later chunks are required for the rest of `dcn_4_2_0_sh_mask.h`, including the remaining `AZF0ENDPOINT0` pin widget capability masks, additional Azalia endpoints/input endpoints/root/stream blocks, DCCG, DMU, hubbub, HUBP, DPP, OPP, OTG, DIO, DSC, HPO, MPC, and the closing header guard. The merge lane should preserve this source path and line range when reconciling the final per-file document.

### subset-b-002219: lines 3172-5538

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 3172-5538

## Scope And Purpose

This chunk is part of the generated DCN 4.2.0 register shift/mask header for AMD display hardware. It contains preprocessor constants for Azalia/HD-audio endpoint register fields under the `AZF0ENDPOINT<n>_AZALIA_F0_*` namespace. These constants do not implement runtime logic directly; they define bit positions (`__SHIFT`) and bit masks (`_MASK`) that runtime code uses to pack, unpack, and update memory-mapped hardware register values through AMD display register helper macros.

The range starts inside endpoint 0 pin audio widget capability definitions, then covers the remainder of endpoint 0 pin controls and endpoint status fields. It then includes full repeated endpoint blocks for `AZF0ENDPOINT1`, `AZF0ENDPOINT2`, and `AZF0ENDPOINT3`, and the beginning of endpoint 4 through `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE`. The continuation of endpoint 4 appears after this chunk.

The generated structure is source-tree aligned with the DCN/DCE audio implementation: higher-level display code programs HDMI, DisplayPort, eDP, and MST audio metadata by naming logical Azalia codec registers and fields, while this header supplies the exact bit layout for DCN 4.2.0 silicon.

## Macro Families Covered

The chunk defines roughly two thousand register-field macros. Each field normally has a pair:

- `REG__FIELD__SHIFT`: the least-significant bit position for the field.
- `REG__FIELD_MASK`: the bit mask for the field in the register value.

The major groups are:

- Codec converter metadata for endpoints 1-4: converter/pin debug, audio widget capabilities, converter format, channel/stream id, digital converter control, supported stream formats and rates, stripe control, and ramp rate.
- Pin parameter capabilities: audio widget capabilities and pin capabilities such as input/output support, HDMI/DP flags, EAPD support, VREF control, jack detection, and impedance sense capability.
- Pin runtime controls: unsolicited responses, pin sense, widget output enable, speaker/channel allocation, HDMI/DP connection flags, ACP data, and audio descriptors.
- Audio descriptor arrays: `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, with fields for max channels, supported frequencies, descriptor byte 2, and the stereo-frequency extension on descriptor 0.
- Multichannel enable controls: per-pair enable, mute, and channel-id fields for channels 01, 23, 45, and 67, plus `MULTICHANNEL_ENABLE2` in the complete endpoint blocks.
- Sink and display identity: sink manufacturer/product id, sink description length, port IDs, and display-name character packing across sink info registers.
- Hotplug, unsolicited force, configuration default, association info, digital output status, LPIB snapshot/control, coding type, format-change status, wireless display identification, remote keepalive, audio enable/disable/format-change interrupt status, and endpoint fine-grain clock-gating reporting.
- Endpoint 4 is incomplete in this chunk: it includes the converter and pin blocks through the first multichannel-enable register, but response lipsync/HBR, sink info, hotplug, status, and clock-gating definitions continue later.

## Important APIs, Types, And Consumers

There are no C functions, structs, or callable APIs in this chunk. The important interface is the macro naming contract consumed by display register-access infrastructure.

The primary consumer pattern is the AMD display `REG_*` and `AZ_REG_*` register helpers used by `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`. Those helpers combine register addresses from `dcn_4_2_0_offset.h` with field shifts/masks from this header. `set_reg_field_value()` and `get_reg_field_value()` depend on the mask/shift constants matching the hardware specification exactly.

DCN42 includes this header in several integration points:

- `display/dc/resource/dcn42/dcn42_resource.c` and `dcn42_resource.h`, where DCN42 resource tables bind register and mask/shift metadata for audio and other display blocks.
- `display/dc/dce/dce_audio.c`, through common DCE audio abstractions that program Azalia endpoint data indirectly.
- `display/dc/irq/dcn42/irq_service_dcn42.c`, GPIO translation/factory code, clock-manager code, and DMUB DCN42 code, which include the same generated register header for their own DCN42 register fields.

For audio specifically, `dcn42_resource.h` maps the endpoint index/data fields with `SF(AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX, AZALIA_ENDPOINT_REG_INDEX, mask_sh)` and related entries. Runtime endpoint register accesses are then performed through an indirect index/data scheme, so the field layouts in this chunk support endpoint-local Azalia register programming even when the high-level code names generic `AZALIA_F0_CODEC_PIN_CONTROL_*` registers.

## Runtime Control Flow Enabled By These Fields

The header itself has no branches or control flow. Its constants participate in the following runtime flows:

- Audio enable/disable: `dce_aud_az_enable()` and `dce_aud_az_disable()` update `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` fields such as `AUDIO_ENABLED` and `CLOCK_GATING_DISABLE`. This chunk provides those fields for the endpoint blocks that include hotplug control.
- HBR and lipsync programming: helper functions read/write `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR` and `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_LIPSYNC`, using `HBR_CAPABLE`, `HBR_ENABLE`, `VIDEO_LIPSYNC`, and `AUDIO_LIPSYNC` masks. Endpoint 0-3 definitions are complete here; endpoint 4's equivalent fields are outside this chunk.
- HDMI/DP audio configuration: `dce_aud_az_configure()` writes `CHANNEL_SPEAKER` fields for speaker allocation, channel allocation, HDMI/DP connection flags, extra connection info, LFE playback level, level shift, and down-mix inhibit.
- ACP packet data: the audio configure path writes `AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA` using fields such as `SUPPORTS_AI`, `ACP_PACKET_ENABLE`, `ACP_TYPE`, and type-dependent bytes.
- Audio format advertisement: the configure path loops across audio format indexes and writes `AUDIO_DESCRIPTOR0 + format_index`. The repeated `AUDIO_DESCRIPTOR0..13` masks define max channel count, supported frequencies, codec descriptor byte 2, and stereo frequency capabilities.
- Sink identity reporting: the configure path writes sink manufacturer/product IDs, description length, port IDs, and the display-name character registers from `SINK_INFO0..8`.
- Interrupt/status handling: audio enabled, disabled, and format-changed interrupt status fields expose flag, mask, and type bits; these are expected to be wired to display interrupt service code or diagnostic paths.

## State And Persistence Behavior

These macros are compile-time constants and hold no process state. State lives in hardware registers and in the display driver's cached audio configuration structures. Writes through the fields in this chunk persist in the device's Azalia endpoint registers until overwritten, reset, or power-gated by the hardware/driver.

Several field groups are stateful from the hardware point of view:

- Hotplug and audio enable fields determine whether the endpoint is exposed as active audio to the OS/audio stack.
- Audio descriptor and speaker-allocation fields persist the sink's current advertised capabilities for the audio codec function.
- Sink info fields persist display identity and port metadata derived from EDID/audio info.
- Interrupt status fields represent latched or maskable events such as audio enabled, disabled, and format changed.
- LPIB snapshot/timer fields and remote keepalive fields are runtime transport/status registers, not stable configuration.
- Clock-gating report/disable fields interact with power-management state, so stale or wrong bit definitions can affect register accessibility and power behavior.

Because the constants are generated from an ASIC register database, source edits should be treated as hardware ABI changes. A single wrong mask can silently corrupt adjacent fields during read-modify-write sequences.

## Dependencies And Integration Points

This chunk depends conceptually on the paired DCN 4.2.0 offset header, `dcn_4_2_0_offset.h`, which supplies register addresses and indexed register names. The shift/mask header only supplies field layout; it is not independently useful without the register addresses and the display register access framework.

Important integration points include:

- `display/dc/dce/dce_audio.h`: declares the common DCE audio register, shift, and mask structs, and macro lists that initialize those structs from generated `SF()` macro expansions.
- `display/dc/resource/dcn42/dcn42_resource.h`: defines the DCN42 audio mask/shift list that selects DCN42-specific generated names.
- `display/dc/dce/dce_audio.c`: programs channel/speaker allocation, ACP data, audio descriptors, sink info, HBR, lipsync, hotplug, and codec parameters using these field definitions.
- The Linux DRM AMDGPU display stack and the audio driver contract: the fields program the GPU's HD-audio codec endpoint so the OS audio stack sees the correct HDMI/DP audio capabilities and hotplug state.

The repeated endpoint layout implies multiple display/audio endpoints with mostly identical register schemas. Endpoint-specific macro names must remain aligned with endpoint-specific offsets from the offset header.

## Risks And Edge Cases

The largest risk is a mask/shift mismatch against hardware. These constants are used by generic read-modify-write helpers, so a wrong field width or shift can overwrite neighboring bits without compiler errors.

Endpoint repetition increases copy/generation risk. Endpoint 1-3 appear structurally complete and highly repetitive; endpoint 0 begins mid-block due to chunking, and endpoint 4 is truncated at the end of this range. Merge/reconciliation should avoid treating this chunk as a complete per-file endpoint inventory.

Audio descriptor programming assumes descriptor registers are consecutive because runtime code writes `AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0 + format_index`. If the generated offset table or descriptor layout breaks that assumption, audio formats could be advertised incorrectly.

Some fields represent read-only or status semantics even when generic helpers can write them. The audio code already notes that `LFE_PLAYBACK_LEVEL` may be read-only in the register spec. Incorrect generated masks can make such questionable writes more harmful by touching unrelated bits.

Clock-gating fields require care. Code temporarily disables clock gating before programming hotplug/audio state and then restores it. If `CLOCK_GATING_DISABLE`, audio enable, or endpoint clock-gating report masks are wrong, register access can race power-gated hardware or leave audio blocks unnecessarily powered.

Interrupt field definitions include flag/mask/type triplets. Mislabeling flag and mask fields can invert interrupt behavior: events may be lost, permanently masked, or repeatedly reported.

Sink display-name fields pack bytes into 32-bit registers. Incorrect byte shifts in `SINK_INFO4..8` would produce garbled monitor names or could expose stale bytes beyond the intended display-name length.

## Test Signals

The best validation signal is a DCN42 build that compiles all consumers of `dcn_4_2_0_sh_mask.h`. Because these are macros, missing or renamed constants usually fail at compile time in resource tables or register-helper call sites.

Runtime test signals are hardware or emulator dependent:

- HDMI and DisplayPort audio devices appear and disappear correctly on hotplug and mode changes.
- `dce_aud_az_configure()` produces correct speaker allocation, channel count, supported sample rates, HBR capability, and sink name as observed by the OS audio stack.
- Audio continues to work across suspend/resume, display hotplug, MST topology changes, and clock-gating transitions.
- Interrupt traces show expected audio enabled, disabled, and format-changed events without spurious repeats.
- Register dumps on DCN42 hardware match expected field values after audio configuration, especially for `CHANNEL_SPEAKER`, `ACP_DATA`, `AUDIO_DESCRIPTOR*`, `SINK_INFO*`, `RESPONSE_HBR`, `RESPONSE_LIPSYNC`, and `HOT_PLUG_CONTROL`.
- Negative tests should include endpoints beyond endpoint 0 to ensure the repeated endpoint-specific masks line up with their endpoint-specific offsets, not just the first endpoint's generic path.

Static review should compare this generated header against the authoritative ASIC register specification and the adjacent generated offset file. Hand-authored unit tests are unlikely to catch all field-layout defects because the failure mode is usually hardware-visible register corruption rather than C-level logic failure.

### subset-b-002220: lines 5539-7886

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 5539-7886

## Scope And Purpose

This chunk covers lines 5539-7886 of the generated AMD DCN 4.2.0 shift/mask header. It contains register-field constants for the Azalia/HDA display-audio endpoint indirect-register blocks. The range starts in the middle of `AZF0ENDPOINT4` pin-control multichannel definitions, then covers the tail of output endpoint 4, complete output endpoints 5-7, complete input endpoint 0, and the beginning of input endpoint 1 through `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`.

The file is not executable driver logic. Its purpose is to publish the hardware bit layout used by AMDGPU Display Core register helpers: `REGISTER__FIELD__SHIFT` gives a bit position, and `REGISTER__FIELD_MASK` gives the already-positioned bit mask. Companion offset definitions in `dcn_4_2_0_offset.h` provide the endpoint index/data register addresses and indirect register indices; this header supplies the field extraction and update constants.

This assigned range contains 2,348 source lines, 2,045 `#define` lines, 1,018 shift definitions, 1,027 mask definitions, 293 comment/register markers, and five address-block markers.

## Register Families In This Chunk

The covered output endpoint families are `AZF0ENDPOINT4`, `AZF0ENDPOINT5`, `AZF0ENDPOINT6`, and `AZF0ENDPOINT7`. Endpoint 4 is partial because earlier lines contain its converter and pin blocks; endpoints 5-7 are complete output endpoint maps in this chunk. Each full output endpoint exposes:

- Converter capabilities and controls: audio widget capabilities, converter format, channel/stream ID, digital converter status/control bits, supported stream formats, supported size/rate capabilities, stripe control, and ramp rate.
- Pin widget capabilities and controls: pin audio widget capabilities, HDMI/DP pin capabilities, unsolicited response enable/tag, pin sense, widget output enable, speaker/channel mapping, ACP packet data, audio descriptor registers, multichannel enable and channel-ID fields, HBR/lipsync response fields, sink information, hot-plug/audio enable status, forced unsolicited response, and default configuration response.
- IEC 60958 channel-status override registers `CODEC_CS_OVERRIDE_0` through `CODEC_CS_OVERRIDE_8`, covering mode/source number, clock accuracy, word length, sampling frequency, original sampling frequency, CGMS-A, channel numbers, and channel status validity bits.
- Runtime endpoint status fields for audio enablement, enabled/disabled interrupts, format-changed interrupts, and fine-grain clock-gating repeat-disable.

The covered input endpoint families are `AZF0INPUTENDPOINT0` and the first part of `AZF0INPUTENDPOINT1`. Input endpoint 0 is complete in this chunk; input endpoint 1 continues into the following chunk. These input blocks expose input converter format, stream/channel ID, digital converter status bits, supported formats/rates, input pin capabilities, input pin sense, input enable, multichannel layout, HBR response, channel allocation, hot-plug/audio enable, forced unsolicited response, default configuration, LPIB snapshots, input activity/channel-layout status, and captured infoframe fields.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or callable APIs declared here. The interface is the generated macro naming contract:

- `AZF0ENDPOINT<n>_AZALIA_F0_<REGISTER>__<FIELD>__SHIFT`
- `AZF0ENDPOINT<n>_AZALIA_F0_<REGISTER>__<FIELD>_MASK`
- `AZF0INPUTENDPOINT<n>_AZALIA_F0_<REGISTER>__<FIELD>__SHIFT`
- `AZF0INPUTENDPOINT<n>_AZALIA_F0_<REGISTER>__<FIELD>_MASK`

The most important field groups are:

- Format fields: `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, `SAMPLE_BASE_DIVISOR`, `SAMPLE_BASE_MULTIPLE`, `SAMPLE_BASE_RATE`, and `STREAM_TYPE` describe the HDA converter stream format word.
- Stream routing fields: `CHANNEL_ID`, `STREAM_ID`, multichannel `*_ENABLE`, `*_MUTE`, and `*_CHANNEL_ID` fields connect codec channel widgets to HDA streams and logical speaker/channel placement.
- Digital audio status fields: `DIGEN`, validity/configuration bits, pre-emphasis, copy/non-audio/professional mode, level, channel-status category/code fields, and `KEEPALIVE` describe IEC 60958/HDMI/DP audio stream metadata.
- Sink and descriptor fields: audio descriptors encode channel count, sample rates, byte offsets, and sample sizes. Sink info fields encode manufacturer/product IDs, port IDs, and up to 18 bytes of sink description.
- Event and status fields: unsolicited response enable/force, pin sense/presence detect, hot-plug audio enabled, enabled/disabled/format-changed interrupt masks, input activity, channel layout, and infoframe valid bits.
- Position reporting fields: `LPIB`, `LPIB_SNAPSHOT_LOCK`, `CYCLIC_BUFFER_WRAP_COUNT`, and timer snapshots expose audio DMA position tracking for output and input endpoints.

The constants are consumed through AMD register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, and structure initializers that build per-block mask/shift tables.

## Control Flow And Hardware Behavior

This header has no local control flow. It participates in control flow when AMDGPU display/audio code includes the generated offset and shift/mask headers and performs register operations.

The HDA/Azalia endpoint model is indirect: `dcn_4_2_0_offset.h` defines per-endpoint index and data registers such as `regAZF0ENDPOINT5_AZALIA_F0_CODEC_ENDPOINT_INDEX`, `regAZF0ENDPOINT5_AZALIA_F0_CODEC_ENDPOINT_DATA`, `regAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX`, and `regAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA`. It also defines matching indirect register indices such as `ixAZF0ENDPOINT5_AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` and `ixAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`. Callers select an indirect endpoint register through the index register, then read or write the data register using the masks and shifts from this chunk.

Driver-side behavior is therefore a sequence of register-table setup, indirect register selection, field extraction/update, and hardware response polling or interrupt handling. Converter format fields control how an HDA stream is interpreted. Pin and multichannel fields determine which endpoint channels are enabled, muted, or mapped. Status and interrupt fields expose changes such as audio enabled/disabled and format changes. LPIB fields let software snapshot audio buffer progress without racing a live hardware counter.

## State And Persistence Behavior

The header itself has no runtime state and persists no data. It is a compile-time hardware ABI description.

The underlying registers are hardware-resident state. Some fields are configuration that persists until reset or a later write, such as stream format, channel stream ID, digital converter enables, multichannel mapping, channel-status override enables, unsolicited-response enables, hot-plug/audio enable controls, and input activity unsolicited-response enables. Other fields are status or latched event state, such as pin sense, HBR capability/enable response, audio enabled status, interrupt status bits, format-changed flags, LPIB values, timer snapshots, input activity, infoframe validity, and cyclic-buffer wrap counts.

The header does not encode access type, reset value, ownership, or side effects. In particular, similarly named status, mask, clear, and force fields must be interpreted through the hardware register specification and existing driver programming sequences. Reserved or undocumented bits should be preserved by read-modify-write operations.

## Dependencies And Integration Points

The direct generated dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which supplies the physical endpoint index/data register offsets and indirect register indices aligned with these field masks.

Known DCN 4.2 integration points include:

- `display/dc/resource/dcn42/dcn42_resource.c`, which includes both `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h` while building DCN 4.2 display-resource register tables, including audio-related DCN/DCE components.
- `display/dmub/src/dmub_dcn42.c`, which includes this header and initializes DMUB register mask/shift tables through `FD_MASK` and `FD_SHIFT`; that file mainly uses DMCUB fields from other chunks of the same header, but it demonstrates the generated-header consumption pattern.
- `display/dc/irq/dcn42/irq_service_dcn42.c`, which includes this header for interrupt register masks and acknowledges. Audio endpoint interrupt status definitions in this chunk are part of the broader generated IRQ/status surface for DCN 4.2.
- `display/dc/gpio/dcn42/hw_factory_dcn42.c`, `display/dc/gpio/dcn42/hw_translate_dcn42.c`, and `display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, which include the same generated header for DCN 4.2 register access infrastructure.
- Higher-level DCE audio and DCN stream-encoder code, which relies on Azalia/HDA endpoint programming to expose HDMI/DisplayPort audio capabilities, set stream formats, update channel allocation, and respond to hot-plug or sink-capability changes.

The output endpoint repetition is an integration contract: endpoints 5-7 have the same field layout, and endpoint 4 appears to share the same layout across adjacent chunks. Generic endpoint-indexed code depends on identical bit positions across endpoint instances. Input endpoints use a related but distinct input-specific layout with `INPUT_CONVERTER` and `INPUT_PIN` names.

## Risks And Edge Cases

- A wrong mask or shift silently targets the wrong hardware bit. For audio this can manifest as missing HDMI/DP audio, wrong channel count, swapped or muted channels, invalid channel-status metadata, failed HBR audio, or broken sink capability reporting.
- The line range starts and ends inside repeated endpoint families. Endpoint 4 and input endpoint 1 are partial in this chunk, so final per-file analysis must merge adjacent chunks before concluding that fields are absent.
- Output endpoint and input endpoint names are similar but not interchangeable. Accidentally using `AZF0ENDPOINT` masks for `AZF0INPUTENDPOINT` registers, or vice versa, can corrupt unrelated indirect endpoint state.
- The endpoint index/data access model makes address/mask alignment critical. A correct field mask applied after selecting the wrong indirect index still reads or writes the wrong codec register.
- Interrupt and unsolicited-response fields have enable, force, payload, and status-like names. Confusing those semantics can drop hot-plug/audio events or generate unexpected unsolicited responses.
- Full-width masks such as `0xFFFFFFFFL` for LPIB, timer snapshot, stream formats, port IDs, and description/descriptor payload fields require callers to preserve only the intended field ownership and avoid assuming narrower values.
- Channel-status override registers include paired value and override-enable fields. Enabling stale override values can advertise the wrong sampling frequency, word length, channel number, or content metadata to an HDMI/DP sink.
- The generated header lacks access policy. Some fields may be read-only, write-only, sticky, self-clearing, firmware-owned, or affected by power state; callers cannot infer that from `_SHIFT` and `_MASK` constants alone.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware audio behavior:

- Build AMDGPU display code with DCN 4.2 enabled. Missing or renamed macros should fail in users of the generated register helpers and DCN 4.2 resource/IRQ/DMUB setup.
- Run generated-register consistency checks that every `__SHIFT` field has a matching `_MASK`, masks have widths and positions compatible with their shifts, and every register family in this range has matching indirect indices in `dcn_4_2_0_offset.h`.
- Compare endpoint 5, 6, and 7 output field layouts and endpoint 0/1 input field layouts for expected bit-position symmetry.
- On DCN 4.2 hardware or simulation, exercise HDMI/DisplayPort audio enumeration, hot-plug, ELD/sink-info reporting, speaker allocation, stereo and multichannel PCM, HBR-capable streams, mute/unmute, and format changes.
- Validate LPIB and timer-snapshot behavior during active playback/capture so position reporting is monotonic and wrap-count fields behave as expected.
- Check kernel logs for AMDGPU DC audio failures, HDA codec enumeration errors, missing audio devices after hot-plug, wrong channel allocation, unsolicited-response storms, interrupt storms, and audio loss across suspend/resume or display mode changes.

### subset-b-002221: lines 7887-10355

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 7887-10355

## Scope And Purpose

This chunk is part of the AMD DCN 4.2.0 generated register shift/mask header. It provides C preprocessor constants for bit positions and masks in several display and audio hardware register blocks: Azalia/HDA codec input endpoint widgets, DSC compressor debug windows, DPIA debug windows, audio descriptor registers, immediate-command interfaces, and the first HDA output stream descriptor fields.

The file is not executable code. Its role is to act as a compile-time hardware ABI map. Companion offset headers provide MMIO or indirect register addresses; this header provides the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants needed by AMDGPU Display Core, DMUB-facing register tables, and low-level register helper macros to read, update, or decode fields without open-coded bit arithmetic.

The requested range contains 2,000 `#define` entries across 365 register names. There are 1,001 shift definitions and 999 mask definitions; the imbalance is because the range begins inside `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR` with only the `HBR_ENABLE_MASK` visible, and ends inside `AZSTREAM1_0_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS` before the corresponding masks appear in the next chunk.

## Register Families In This Chunk

The chunk starts at the tail of `AZF0INPUTENDPOINT1`, then contains complete repeated HDA/Azalia input endpoint blocks for `AZF0INPUTENDPOINT2` through `AZF0INPUTENDPOINT7`. Each endpoint exposes the same main groups:

- Converter debug and converter parameters: `INPUT_CONVERTER_PIN_DEBUG`, `PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `PARAMETER_STREAM_FORMATS`, and `PARAMETER_SUPPORTED_SIZE_RATES`.
- Converter controls: `CONTROL_CONVERTER_FORMAT`, `CONTROL_CHANNEL_STREAM_ID`, and `CONTROL_DIGITAL_CONVERTER`.
- Input pin parameters: `INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `INPUT_PIN_PARAMETER_CAPABILITIES`.
- Input pin controls and responses: unsolicited response tag/enable, input pin sense, widget input enable, HBR capability/enable, channel allocation, hot-plug clock/audio enable, forced unsolicited response payload, configuration default, LPIB snapshot/timer state, input activity/status, and audio infoframe decode.
- Multichannel input routing: `MULTICHANNEL_ENABLE` covers channels 0 through 3 and `MULTICHANNEL_ENABLE2` covers channels 4 through 7, with enable, mute, and four-bit channel ID fields per lane.

The DSC/DPIA debug portion contains mostly full-width debug readout fields:

- `DSCC_DEBUG_ID` plus `DSCC_DEBUG_0` through `DSCC_DEBUG_28`. The first four expose `DSCC_RATE_BUFFER_MODEL_FULLNESS_LEVEL<n>` with an 18-bit mask; the rest are generic 32-bit debug words.
- `DSCC_DISPCLK_DEBUG_ID` plus `DSCC_DISPCLK_DEBUG_0` through `DSCC_DISPCLK_DEBUG_33`. Early registers expose output-buffer fullness levels, initial-transmit-delay state, last-slice pixel count, output-buffer pixel threshold, and total output-buffer pixel count; later registers are generic debug words.
- `DSCCIF_DEBUG_ID`, `DSCCIF_DEBUG_0`, `DSCCIF_DEBUG_1`, and `DSC_TOP_DEBUG_ID` through `DSC_TOP_DEBUG_2`.
- Per-port DPIA debug windows for `DPIA_PORT0` through `DPIA_PORT5`, each with a full-width debug ID and debug bus word.
- Per-mainlink DPIA debug windows for `DPIA_PORT_ML0` through `DPIA_PORT_ML5`, each with a test debug ID and seven full-width mainlink debug data words.
- Per-AUX DPIA debug windows for `DPIA_PORT_AUX0` through `DPIA_PORT_AUX5`, each with a test debug ID and seven full-width AUX test debug words.
- `DPIA_MU_DEBUG_ID`, a full-width microcontroller or management-unit debug selector/readout.

The audio descriptor and HDA control tail contains:

- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, each with `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, `DESCRIPTOR_BYTE_2`, and `SUPPORTED_FREQUENCIES_STEREO` fields laid out across the 32-bit descriptor word.
- Immediate command output/input/root interface data and index registers: `AZENDPOINT0_*`, `AZINPUTENDPOINT0_*`, and `AZROOT0_*`.
- A complete `AZSTREAM0_0_OUTPUT_STREAM_DESCRIPTOR_*` set for stream control/status, link position, cyclic buffer length, last valid BDL index, FIFO size, stream format, BDL lower/upper base addresses, and link-position alias.
- The first three shift fields of `AZSTREAM1_0_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`, with the remaining fields and masks outside this chunk.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or storage definitions in this chunk. The important API is the generated macro contract:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a field.
- `REGISTER__FIELD_MASK` gives the unshifted register mask for that field.
- Repeated endpoint, port, mainlink, AUX, descriptor, and stream names encode the hardware instance number directly in the macro name.

These constants are intended for AMD register helper layers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD`, `FN`, `FD_SHIFT`, and `FD_MASK`. Callers combine the offset macro from the matching DCN 4.2.0 offset header with these shift/mask macros to do read-modify-write access. The macros also provide a stable naming surface for generated register tables used by Display Core and DMUB support code.

Important field groups include:

- HDA format fields: `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, `SAMPLE_BASE_DIVISOR`, `SAMPLE_BASE_MULTIPLE`, `SAMPLE_BASE_RATE`, and `STREAM_TYPE`.
- HDA digital converter status/control bits: `DIGEN`, validity, category-code bits, copyright/pre-emphasis/non-audio flags, professional/consumer mode, generation level, and `KEEPALIVE`.
- HDA pin capability and detection bits: impedance sense, trigger requirement, jack detection, headphone/output/input capability, HDMI/DP capability, VREF control, EAPD capability, and presence detect.
- HDA stream DMA fields: stream reset/run, interrupt enables, stripe control, traffic priority, stream number, completion/FIFO/descriptor error status, FIFO readiness, LPIB, cyclic buffer length, BDL base address, and stream format.
- DSC/DPIA debug fields: debug IDs, rate/output buffer fullness, pixel counters, initial transmit delay state, and full-width opaque debug data registers.

## Control Flow And Hardware Behavior

This header has no software control flow, but the fields describe hardware control surfaces that higher-level code sequences:

- HDA input endpoint programming follows codec widget semantics. Driver or firmware code reads widget capabilities, selects converter format and stream/channel IDs, enables digital conversion, configures pin widget input enablement, programs multichannel routing, and observes input activity or infoframe state.
- Hot-plug and unsolicited-response fields form an event path. The tag/enable register arms unsolicited responses, the force register can synthesize a payload, and the input status control fields expose or enable unsolicited reporting for activity and channel-layout/channel-status infoframe changes.
- Audio stream descriptor fields implement the HDA DMA run path. Software sets BDL base addresses and length, programs format and stream number, sets `STREAM_RUN`, and observes position, FIFO readiness, completion status, FIFO errors, and descriptor errors. Reset and interrupt-enable bits gate transitions around that flow.
- Audio descriptors advertise display-audio formats to the HDA codec path. Each descriptor packs maximum channels, frequency support, a descriptor byte, and stereo frequency support into a fixed layout.
- DSC and DPIA debug windows are diagnostic/telemetry paths. Typical control flow selects or reads a debug ID, then samples full-width debug words or named counters to inspect rate-buffer fullness, output-buffer fullness, transmit-delay milestones, AUX transactions, mainlink state, or debug buses.

Because these macros are field definitions only, they do not encode access type, reset values, write-one-to-clear behavior, polling intervals, firmware ownership, or ordering requirements. Those semantics live in generated register specifications, hardware programming guides, and the calling driver/firmware code.

## State And Persistence Behavior

The header itself has no runtime state and persists nothing. It is a static description compiled into code that includes it.

The underlying hardware registers represent several kinds of state:

- Configuration state: converter format, channel/stream IDs, digital-converter enable/configuration bits, pin widget input enable, multichannel enable/mute/channel IDs, hot-plug clock gating, audio enabled state, stream BDL addresses, cyclic buffer length, last valid index, stream format, stream number, and interrupt enables.
- Advertised capability state: audio widget capability, stream format support, supported size/rates, pin capabilities, HBR capability, audio descriptors, HDMI/DP capability, and configuration default.
- Transient status or counters: LPIB, LPIB timer snapshot, cyclic buffer wrap count, input activity, channel layout, infoframe validity, presence detect, stream completion/error/FIFO-ready status, FIFO size, DSC buffer fullness, initial transmit delay reached, and DPIA debug data.
- Latched or synthetic event state: unsolicited response tag/enable, forced unsolicited response payload/force bit, input activity unsolicited-response enable, and infoframe-change unsolicited-response enable.

Configuration fields generally persist until reset, power-gating, reinitialization, or a later write from the kernel, firmware, or diagnostic tooling. Debug and status fields may change every display/audio clock cycle. Some stream status bits may be sticky or clear-on-write by HDA convention, but the mask header alone does not specify that behavior.

## Dependencies And Integration Points

The direct dependency is the DCN 4.2.0 generated register set:

- The corresponding `dcn_4_2_0_offset.h` and related offset headers must define addresses or indirect indices matching these register names.
- AMDGPU Display Core register helpers must see both offset and shift/mask headers with consistent naming.
- HDA/HDMI/DisplayPort audio code depends on the Azalia endpoint, audio descriptor, immediate-command, and stream descriptor fields being aligned with the hardware codec exposed by the display engine.
- DSC code and diagnostic paths depend on the DSCC, DSCCIF, and DSC_TOP debug definitions for inspecting Display Stream Compression rate-control and buffer behavior.
- DPIA, USB4/DisplayPort tunneling, AUX, and link debug paths depend on the per-port, per-mainlink, and per-AUX debug windows.
- DMUB firmware and kernel display code may share ownership of some of these blocks, so register access must respect whichever layer owns a given display generation or power state.

The repeated instance pattern is a key integration contract. `AZF0INPUTENDPOINT2` through `AZF0INPUTENDPOINT7`, `DPIA_PORT0` through `DPIA_PORT5`, `DPIA_PORT_ML0` through `DPIA_PORT_ML5`, `DPIA_PORT_AUX0` through `DPIA_PORT_AUX5`, and `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` expose the same fields at instance-specific offsets. Generic code can safely index instances only if the offset header and this mask header stay generated from the same schema.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask, shift, or instance name can make register helper code silently read or write the wrong bits.
- The chunk boundaries split two register definitions. `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR` is only represented by its final `HBR_ENABLE_MASK`, and `AZSTREAM1_0_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS` only has its first three shift macros here. Any completeness check must merge neighboring chunks before flagging these as true defects.
- Many debug registers are full-width opaque fields. They are useful for diagnostics but weakly self-describing, so tests should not infer stable public ABI meaning from names such as `DSCC_DEBUG_4` or `DPIA_PORT_ML_DEBUG_DATA<n>` without the generated spec.
- HDA stream descriptor writes can affect DMA. Misprogramming BDL base addresses, cyclic buffer length, stream format, or stream run/reset can cause audio underruns, memory access faults, stuck streams, or interrupt storms.
- Status, interrupt enable, and control bits are packed into the same stream control/status register. Callers must use read-modify-write helpers and preserve unrelated status or reserved bits rather than writing literal register values.
- The pin and converter fields mirror HDA codec concepts. Incorrect HBR, channel allocation, multichannel, stream ID, or infoframe handling can break HDMI/DP audio routing even when display scanout is otherwise correct.
- Debug-window access may depend on power, clock, or firmware state. Reading while DSC/DPIA blocks are gated, owned by firmware, or not instantiated can return stale values or trigger access faults depending on the platform.
- The mask header does not express read-only, write-only, volatile, self-clearing, sticky, write-one-to-clear, or access-width constraints.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for AMDGPU display configurations that include `dcn_4_2_0_sh_mask.h` and instantiate DCN 4.2.0 display/audio register tables.
- Generated-header consistency checks that every visible `__SHIFT` has a matching `_MASK`, with explicit allowance for this chunk's two boundary-split registers.
- Cross-header checks that every register prefix in this slice has a matching offset or indirect-index definition in the DCN 4.2.0 offset headers.
- Instance-layout checks confirming identical field layouts for `AZF0INPUTENDPOINT2` through `AZF0INPUTENDPOINT7`, `DPIA_PORT*`, `DPIA_PORT_ML*`, `DPIA_PORT_AUX*`, and `AUDIO_DESCRIPTOR*`.
- Display audio smoke tests covering HDMI/DP audio enumeration, codec immediate commands, HBR enablement, channel allocation, multichannel routing, infoframe detection, stream start/stop, suspend/resume, and hotplug.
- HDA DMA tests that exercise BDL programming, stream reset/run, LPIB movement, FIFO readiness, completion interrupts, FIFO error reporting, descriptor error reporting, and cyclic buffer wrap behavior.
- DSC and DPIA diagnostics that sample DSCC buffer fullness, initial transmit delay counters, DPIA port debug bus data, mainlink debug data, and AUX debug data during active links and while blocks are power-gated.
- Runtime tracing or register-dump comparison against known-good hardware captures for DCN 4.2.0 systems, especially around display audio bring-up and USB4/DPIA link paths.

### subset-b-002222: lines 10356-12776

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 10356-12776

## Purpose

This chunk is a generated AMD DCN 4.2.0 shift/mask header slice for display, audio, clock-generation, Azalia codec, and display performance-monitor registers. It contains no executable C code; its public interface is a dense set of `#define` constants describing bit positions (`__SHIFT`) and bit masks (`_MASK`) for fields inside MMIO registers.

The requested range contains 2,102 generated definitions. It starts inside the `AZSTREAM1_0_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS` field list, covers Azalia output stream descriptor instances 1 through 7, covers a large `DCCG` display clock generator block, covers display-clock dentist control, covers Azalia function/converter/pin/input codec node fields, and ends inside the `DC_PERFMON1_PERFCOUNTER_STATE` group. The range boundaries are artificial: `AZSTREAM1` begins in the previous chunk, and `DC_PERFMON1` continues in the next chunk.

Although this file is under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The ABI-like surface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the register.
- `<REGISTER>__<FIELD>_MASK`: the field's bit mask inside the register.

The main register-field families in this chunk are:

- `AZSTREAM1_0` through `AZSTREAM7_0`: HDA output stream descriptor control/status, link position, cyclic buffer length, last valid index, FIFO size, stream format, buffer descriptor list lower/upper base address, and link-position alias fields. The control/status fields include stream reset/run, completion/FIFO/descriptor interrupt enables, stripe control, traffic priority, stream number, completion status, FIFO/descriptor error status, and FIFO ready.
- `PHYPLL[A-E]_PIXCLK_RESYNC_CNTL`: pixel-clock resynchronization delay, enable, and status fields for PHY PLL paths.
- `DP_DTO_DBUF_EN`, `DP_DTO[0-3]_PHASE`, and `DP_DTO[0-3]_MODULO`: DisplayPort DTO double-buffer enables and per-stream phase/modulo values.
- `DSCCLK[0-3]_DTO_PARAM` and `DSCCLK_DTO_CTRL`: DSC clock DTO phase/modulo and per-DSC-clock enable/read-update controls.
- `DPPCLK[0-3]_DTO_PARAM`, `DPPCLK_DTO_CTRL`, and `DPPCLK_CTRL`: DPP clock DTO controls and DPP clock enable bits.
- `DPREFCLK_*`, `DISPCLK_*`, `SOCCLK_*`, `SYMCLK_*`, `DTBCLK_P_CNTL`, `HDMICHARCLK0_CLOCK_CNTL`, `HDMISTREAMCLK_CNTL`, `DPIA*`, and `PHY*SYMCLK_CLOCK_CNTL`: DCCG clock source selection, enable, frequency-change, clock-gating, fine-grain clock-gating repeat, and ref/symbol clock control fields.
- `DCCG_GATE_DISABLE_CNTL` through `DCCG_GATE_DISABLE_CNTL6`: root and leaf gate-disable bits for DISPCLK, SOCCLK, DPREFCLK, HDMICHARCLK, HDMISTREAMCLK, DPSTREAMCLK, DPPCLK, DSCCLK, DTBCLK, PHY symbol/ref clocks, and SYMCLK32 paths.
- `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO0/1_PHASE`, and `DCCG_AUDIO_DTO0/1_MODULE`: display audio DTO source selection and phase/module programming.
- `DCCG_VSYNC_*`: OTG vsync latch values, selectable vsync counter start/end events, counter run/clear, max count, interrupt enable/ack/status bits, and interrupt-trigger mode.
- `DCCG_PERFMON_CNTL` and `DCCG_PERFMON_CNTL2`: DCCG performance measurement controls including run, mode, OTG selection, event-count mode, monitor select, and MUX/debug source fields.
- `DENTIST_DISPCLK_CNTL`: display-clock dentist divider programming, change mode, and change-done fields.
- `AZALIA_F2_CODEC_ROOT_*` and `AZALIA_F2_CODEC_FUNCTION_*`: function group vendor/device ID, revision, node counts, power state, subsystem ID response, converter synchronization, reset, size/rate, stream format, and power-state capability fields.
- `AZALIA_F2_CODEC_CONVERTER_*`: output converter format, stream/channel ID, digital converter controls, stripe/ramp controls, widget capabilities, supported rates/formats, and audio descriptor-related fields.
- `AZALIA_F2_CODEC_PIN_*` and `AZALIA_F2_PIN_CONTROL_*`: output pin widget control, unsolicited response, pin sense, default configuration, speaker/channel allocation, downmix, ACP/audio descriptors, multichannel enables, lipsync, HBR, audio sink info, channel-status override, pin association, LPIB snapshot/readback, coding type, format changed status, wireless display ID, remote keepalive, and pin capability fields.
- `AZALIA_F2_CODEC_INPUT_*`: input converter and input pin control fields, including input converter format/stream/channel/digital control, input pin sense/default config, channel allocation, multichannel enables, HBR, LPIB snapshots, input status/control, infoframe, channel status, and capabilities.
- `DC_PERFMON0` and the start of `DC_PERFMON1`: display performance-counter event selection, counted-value selection/type, increment mode, hardware run/stop control, count-off selection, restart/interrupt/active bits, per-counter state readback, perfmon state/report count, count-off interrupt control/status/ack, counter-value interrupt status/ack bits, and low/high counter readback fields.

## Control Flow

This header has no runtime control flow. It participates in compile-time construction of register, shift, and mask tables:

1. DCN42 driver code includes `dcn_4_2_0_offset.h` and this matching `dcn_4_2_0_sh_mask.h`.
2. Resource and hardware-block headers use token-pasting macros such as `SR`, `SRI`, `DCCG_SF`, `DCCG_SFI`, `DCCG_SFII`, `SF`, and related register-list helpers to bind generic field names to generated DCN42 register-field constants.
3. Runtime objects receive register offsets plus field shift/mask tables during construction.
4. Shared AMD display helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use those tables to read, write, and update MMIO bitfields.

The macros in this chunk do not encode sequencing. Stream descriptor start/stop, HDA buffer programming, DCCG clock programming, DTO update timing, Azalia codec verbs, audio DTO setup, vsync counter use, and performance-counter sampling are controlled by driver code and hardware rules outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields:

- HDA output stream state: run/reset controls, descriptor and FIFO errors, buffer-completion interrupts, FIFO ready, stream number, stream format, BDL base address, cyclic buffer length, last valid descriptor index, and link position.
- DCCG clock state: clock source selection, enables, DTO phase/modulo values, double-buffer update controls, divider settings, resync status, gate-disable overrides, soft resets, CAC status, time-base divisors, and test/debug mux selection.
- Audio clock state: audio DTO source selection plus phase/module values used to derive audio clocks from display timing or link/reference clocks.
- Azalia codec state: function/converter/pin capabilities and controls, ELD/audio descriptors, speaker and channel allocation, pin sense, stream/channel IDs, HBR and multichannel controls, channel-status overrides, LPIB snapshots, format-change status, and remote/wireless-display information.
- Performance-monitor state: event selection, counter run/stop controls, active state, interrupt enable/status/ack bits, selected counter states, count-off behavior, and readback values.

Persistence and side effects are hardware-defined. Configuration fields usually remain until modeset, stream disable, audio reconfiguration, suspend/resume, clock gating/power gating, GPU reset, or ASIC reset rewrites them. Status and interrupt fields can be latched, write-one-to-clear, self-clearing, or valid only while their block is powered and clocked. This file only provides bit positions and masks; it does not describe those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DCN 4.2.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` supplies the matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` includes both generated headers and builds DCN42 resource objects, including audio, AUX/I2C, DCCG, DIO, DSC, HPO, IRQ, and other display block tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn42/dcn42_dccg.h` consumes many DCCG names from this range through `DCCG_MASK_SH_LIST_DCN42_COMMON`, including DPPCLK, DISPCLK frequency change, DP/HDMI stream clocks, SYMCLK32, OTG pixel-rate dividers, DTBCLK, audio DTO, dentist display clock, gate-disable, DSCCLK, and PHY symbol-clock fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn42/dcn42_dccg.c` programs those DCCG fields through the register/shift/mask tables created from this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines the shared audio register and mask/shift lists for audio DTO and Azalia capability fields; DCN42 resource construction uses this style for audio object setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` uses audio register tables to enable/disable Azalia, configure audio stream format, program DTOs, and derive display audio timing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c` includes this header for DMUB/DCN42 register initialization, although this specific chunk is more directly relevant to display clocking, audio, and perfmon fields than to the DMUB boot/reset fields near the top of that source.

Behaviorally, this range is an endpoint for HDMI/DP audio stream programming, display clock tree programming, DTO and clock-gating setup, Azalia codec verb exposure, and display/DCCG performance-monitor instrumentation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting only one hardware bitfield at runtime.
- The file is generated. Manual edits risk divergence from the authoritative register database, the offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first lines are missing the beginning of `AZSTREAM1_0_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`, and the final lines stop before the rest of `DC_PERFMON1`; adjacent chunk reports must be reconciled before making whole-block claims.
- HDA stream descriptors are DMA-facing. Bad masks for BDL base address, cyclic buffer length, last valid index, stream number, or run/reset can cause silent audio, underruns, descriptor errors, FIFO errors, or DMA to the wrong address.
- Link position and LPIB fields are used for synchronization. Incorrect masks can break audio position reporting, A/V sync, underrun diagnosis, and snapshot-based debug.
- DCCG clock controls are sequencing-sensitive. Incorrect enables, source selections, DTO values, or divider fields can produce blank display, bad link rates, unstable pixel clocks, stuck update-pending behavior, or clock-domain glitches during modeset.
- Gate-disable fields have power and stability implications. Wrong masks can leave clocks ungated and waste power, or gate clocks required by active pipes, DSC, DPP, HDMI, DP, PHY, or audio paths.
- Audio DTO source/phase/module fields must match signal type and timing. Mistakes can create HDMI/DP audio sample-rate drift, channel-status mismatch, or no audio only on specific display modes.
- Azalia codec capability and pin/control fields are externally visible to the OS audio stack. Wrong capability masks can advertise unsupported sample rates, channel counts, HBR support, speaker allocation, ELD/audio descriptors, or power states.
- Pin sense, unsolicited response, remote keepalive, and format-change status fields may be interrupt or status sensitive. Bad masks can produce stale connector/audio presence state or repeated/missed audio notifications.
- Performance-monitor interrupt status/ack fields are easy to misuse. Wrong masks can leave interrupts asserted, miss counter overflow/count-off events, or read the wrong high/low counter value.
- Repeated instance families are copy-sensitive. `AZSTREAM1-7`, DPPCLK/DP DTOs, OTG pixel-rate controls, PHY clocks, and `DC_PERFMON0/1` are structurally similar; a generator error can affect only one stream, pipe, PHY, or perfmon instance.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display/audio behavior:

- Build DCN42 AMDGPU display support. Missing or renamed macros should surface in `dcn42_resource.c`, `dcn42_dccg.h`, `dcn42_dccg.c`, `dce_audio.h`, `dce_audio.c`, and DMUB register initialization paths.
- Mechanically compare this range against the authoritative DCN 4.2.0 register-field database and ensure every `_MASK` has the expected paired `__SHIFT` definition.
- Cross-check this shift/mask range against `dcn_4_2_0_offset.h` so every field register in the chunk has a corresponding register offset and base-index entry.
- Run static repeated-instance checks for `AZSTREAM1-7`, `PHYPLL[A-E]`, `DP_DTO0-3`, `OTG0-3`, `DPPCLK0-3`, `DSCCLK0-3`, `SYMCLK[A-E]`, and `DC_PERFMON0/1`, while allowing intentional per-instance prefixes and any documented per-instance omissions.
- Exercise HDMI and DP audio across common and edge sample rates, channel counts, HBR/non-HBR modes, suspend/resume, display hotplug, and modeset transitions. Expected signals are stable audio, correct stream/channel IDs, no FIFO/descriptor errors, correct position reporting, and matching channel/speaker allocation.
- Validate DCCG programming across display modes that change DISPCLK, DPPCLK, DSCCLK, DP stream clocks, HDMI stream clocks, PHY symbol clocks, and DTBCLK. Expected signals are successful modesets, stable pixel/link clocks, no stuck frequency-change done/update bits, and no underrun-like symptoms.
- Exercise DSC-enabled modes to cover DSCCLK DTO/gate fields that feed the compressor path.
- Verify clock-gating and power behavior with active/inactive pipes, DP/HDMI displays, and audio enabled/disabled. Expected signals include no display/audio regressions and expected power-state transitions.
- Use register dumps around audio DTO and Azalia node programming to confirm advertised capabilities, ELD/audio descriptors, pin sense, HBR, multichannel, and LPIB fields match the connected sink and active stream.
- Exercise `DC_PERFMON0` and `DC_PERFMON1` counter programming, readback, count-off interrupts, and ack paths. Expected signals are monotonic counter values for selected events, correct high/low readback, and clearable interrupt status.

## Cross-Chunk Notes

The previous chunk owns `AZSTREAM0_0` and the beginning of `AZSTREAM1_0_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`. This chunk starts at the `FIFO_ERROR_INTERRUPT_ENABLE` shift for `AZSTREAM1_0`, so the full `AZSTREAM1` control/status field list must be reconstructed during merge. The next chunk continues after `DC_PERFMON1_PERFCOUNTER_STATE`; it should cover the remaining `DC_PERFMON1` fields and later register families. The final per-file research document should reconcile these boundaries before describing all DCN 4.2.0 HDA stream, DCCG, Azalia, or perfmon metadata.

### subset-b-002223: lines 12777-15093

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 12777-15093

## Scope And Purpose

This chunk is part of the generated AMD DCN 4.2.0 register shift/mask header. It contains preprocessor constants that describe bit positions and bit masks for display microcontroller, power-gating, interrupt-status, timer-position, and interrupt-destination registers. The companion offset header provides register addresses; this header provides the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants used by AMDGPU Display Core and DMUB register helpers to access individual hardware fields.

The range contains 2,190 `#define` lines across 116 register names: 1,096 shift definitions and 1,094 mask definitions. The mismatch is expected for this chunk because it starts in the middle of `DC_PERFMON1_PERFCOUNTER_STATE` mask definitions and ends in the middle of `DIG_INTERRUPT_DEST` shift definitions. There are no C functions, structs, or executable code in this range.

## Register Families In This Chunk

The first section completes the `DC_PERFMON1` block, covering perfmon control, report count, counter-off interrupt enable/status/ack, clock/run-enable selection, counter interrupt status/ack bits, and low/high counter value read fields.

The `dce_dc_dmu_dc_pg_dispdec` address block defines display power-gating controls. `DOMAIN*_PG_CONFIG` and `DOMAIN*_PG_STATUS` fields cover force-on, gate request, desired power state, and PGFSM power status for domains 0-3, 16-19, and 22-26. `DCPG_INTERRUPT_STATUS*` and `DCPG_INTERRUPT_CONTROL_*` expose power-up/power-down interrupt occurrence, mask, and clear bits for those domains. `DC_IP_REQUEST_CNTL` and `LONO_MEM_PWR_REQ_CNTL` provide small control fields for IP requests and LONO memory power request disablement.

The `dce_dc_dmu_dmu_dcperfmon_dc_perfmon_dispdec` block defines a complete `DC_PERFMON2` instance. It mirrors the perfmon counter-control shape used by `DC_PERFMON1`: event selection, counted-value source/type, increment mode, hardware stop controls, restart and interrupt enable, counter state selection, perfmon state/report controls, cvalue interrupt/status/ack fields, and low/high counter reads.

The `dce_dc_dmu_dmu_misc_dispdec` block contains miscellaneous DMU controls: `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, DMCUB/SMU interrupt messaging, ZSC control/status, down-spread/deep-sleep allowance forcing, CGTT block control for display and SOC clocks, and ZPR clock ungate delay.

The `dce_dc_dmu_ihc_dispdec` block dominates the rest of the chunk. It defines GPU timer start-position/read controls, `DISP_INTERRUPT_STATUS` plus `DISP_INTERRUPT_STATUS_CONTINUE` through `CONTINUE25`, and interrupt-destination registers. The status chain covers OPTC underflow, OTG snapshot/force-vsync/force-count/TRIGA/TRIGB/vsync/vstartup/vready/vupdate/vertical/DRR events, DIGA-DIGH fast-training and video-stream-disable events, HPD and HPD RX events, AUX software/link-service done events, DIO ALPM, RBBMIF timeout, I2C events, HPO ALPM wake, MCIF CWB/DWB events, perfmon interrupts for DCCG/DMU/DIO/WB/DPP/DWB/MPC/OPP/DSC/HPO, histogram-ready interrupts, DCCG vsync latch and OTG DRR timing updates, ODM underflow, AZ audio endpoint events, I2C DDC hardware/read-request events, DCPG power events, DMCUB mailbox/timer/general-data/fault events, DSC core errors, DPIA, and DMCUB register inbox/outbox interrupts.

The interrupt-destination section maps interrupt sources to destination selector bits for DCCG, DMU, DCPG, MMHUBBUB, writeback, DCHUB, DCHUB perf counters, DPP perf counters, MPC, OPP, OPTC, OTG0-OTG5, and the beginning of DIG destination routing.

## Important APIs, Types, And Macros

This chunk's API surface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a hardware field.
- `REGISTER__FIELD_MASK` gives the unshifted mask used to isolate or update that field.
- Register names are grouped by generated address-block comments, while actual MMIO addresses come from `dcn_4_2_0_offset.h`.

These macros are consumed by AMD register helper idioms such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `REG_GET`, `REG_SET`, and `REG_UPDATE`. For DCN 4.2, `display/dmub/src/dmub_dcn42.c` includes both `dcn_4_2_0_offset.h` and this header, then initializes DMUB register tables by expanding field masks and shifts through `FD_MASK` and `FD_SHIFT`. `display/dc/irq/dcn42/irq_service_dcn42.c` also includes this header for DCN 4.2 interrupt programming.

## Control Flow And Hardware Behavior

The file has no software control flow. It describes hardware state machines and interrupt-routing surfaces that other code drives through read-modify-write and polling sequences.

Power-gating fields model a control/status flow: software or firmware can request force-on/gate states, observe desired power state and PGFSM status, then use DCPG interrupt status/control fields to detect and clear power-up or power-down transitions.

Perfmon fields model counter configuration and reporting flow. Callers select an event and counted-value source, choose increment/run-enable behavior, optionally enable restart or counter-off interrupts, then read low/high counter values and acknowledge counter interrupts.

The IHC interrupt-status chain is a hardware event fan-in. Each `DISP_INTERRUPT_STATUS_CONTINUE*` register exposes a subset of latched display events and usually reserves bit 31 as the continuation bit for the next status register. IRQ handling code can walk or decode this chain to identify events from timing generators, display pipes, hotplug/AUX/I2C, DMCUB mailbox/fault paths, performance counters, power-gating domains, and display compression blocks.

The interrupt-destination registers are routing controls. Their fields select where a given interrupt source is delivered, which is distinct from status, clear, and mask semantics in the interrupt-control registers.

GPU timer start-position registers encode per-pipe event positions for vupdate, vstartup, vready, flip, vupdate-no-lock, and flip-away events. These fields support precise timing of display events relative to OTG and pipe timing.

## State And Persistence Behavior

The header itself stores no runtime state and persists no data; it is a compile-time hardware ABI description.

The underlying registers represent live device state. Status fields are transient or latched hardware observations, such as perf counter interrupts, power-gating transitions, DMCUB mailbox readiness, HPD/AUX/I2C events, OTG timing events, underflow/error events, and perfmon counter events. Control fields such as perfmon configuration, interrupt masks/clears, destination routing, clock-gating controls, power-gating requests, and timer start-position encodings persist in hardware until reset, power transition, firmware update, or another kernel/firmware writer changes them.

The macros do not encode access type, reset value, write-one-to-clear behavior, self-clearing behavior, or firmware ownership. Callers must rely on hardware register specs and existing DCN/DMUB sequencing when deciding whether a field can be written, polled, acknowledged, or preserved.

## Dependencies And Integration Points

The direct dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which must remain synchronized with this shift/mask file. Offset/header drift would make otherwise-correct field operations hit the wrong register or bit.

DCN 4.2 integration points in this source tree include:

- `display/dmub/src/dmub_dcn42.c`, which builds DMUB register tables from `FD_MASK` and `FD_SHIFT`.
- `display/dc/irq/dcn42/irq_service_dcn42.c`, which maps DCN interrupt source IDs into DAL interrupt sources and includes this header for register programming.
- `display/dc/resource/dcn42/dcn42_resource.c`, `display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, and DCN 4.2 GPIO factory/translation code, which include the same offset and mask headers for display resource, clock, and GPIO register access.
- Firmware integration through the DCN 4.2 DMCUB binary path and DMCUB mailbox/outbox interrupt fields represented in this chunk.

The chunk also depends on broader AMDGPU Display Core conventions: generated field macros must match register helper naming, repeated instance layouts must remain consistent across OTG/DIG/DPP/DSC/HPO instances, and interrupt source naming must match the `ivsrcid/dcn` definitions used by IRQ services.

## Risks And Edge Cases

Generated-header drift is the primary risk. A wrong shift, mask, register name, or stale offset pairing can silently corrupt unrelated hardware fields because register helpers compile cleanly even when the hardware map is wrong.

This chunk contains several similarly named interrupt concepts: status, continuation, control mask/clear, and destination. Confusing these can drop interrupts, route them to the wrong consumer, fail to acknowledge latched events, or create interrupt storms.

The range starts and ends mid-register. Any per-register completeness analysis must merge adjacent chunks before concluding that `DC_PERFMON1_PERFCOUNTER_STATE` or `DIG_INTERRUPT_DEST` is missing fields or masks.

Power-gating and clock-gating fields are sensitive to firmware and hardware ownership. Incorrect writes can keep display domains forced on, gate active hardware, break low-power entry/exit, or race with DMUB/SMU-managed power transitions.

Perfmon and timer-position fields are low-level diagnostics/timing surfaces. Incorrect event selection, start-position encoding, or interrupt enablement can cause misleading telemetry, missed timing events, or excessive interrupts without obvious functional failure.

Reserved or absent bits are not described by these macros. Callers should update fields with read-modify-write helpers and preserve unrelated bits rather than writing whole-register literals.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for DCN 4.2 display, DMUB, IRQ, resource, clock manager, and GPIO code that includes `dcn_4_2_0_sh_mask.h`.
- Generated-register consistency checks that verify each complete `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, while allowing the known chunk-boundary partials.
- Cross-header checks that every register represented here has a matching DCN 4.2 offset definition and that instance families such as `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST` preserve identical bit layouts where expected.
- IRQ smoke tests for vblank/vupdate/vline, page flip, HPD/HPDRX, AUX/I2C, DMCUB outbox/inbox, DSC error, DPIA, underflow, and DCPG power events.
- Suspend/resume and display idle tests that exercise DCPG domain transitions, DMU clock gating/deep-sleep allowance, and DMCUB/SMU interrupt messaging.
- Hardware or simulator perfmon tests that program DC perf counters, trigger counter-off interrupts, read low/high values, and verify status/ack behavior.
- Mode-set and variable-refresh tests that exercise OTG DRR timing, vstartup/vready/vupdate-no-lock, GPU timer start-position fields, and interrupt routing under multi-display configurations.

### subset-b-002224: lines 15094-17728

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 15094-17728

## Purpose

This chunk is a generated AMD DCN 4.2.0 display register shift/mask header slice. It contains no executable C logic; its public surface is 2,101 `#define` constants that name bit positions (`__SHIFT`) and bit masks (`_MASK`) for DCN 4.2 hardware register fields.

The range starts in the tail of `DIG_INTERRUPT_DEST`, covers several display interrupt-routing destination registers, then moves through the DMU/DMCUB firmware interface, DMCUB memory regions/mailboxes/interrupts, MCIF writeback and MMHUBBUB registers, DC perfmon blocks, Azalia/HDA audio registers, and ends in the beginning of DCHUBBUB SDPIF/VM security and address fields. Although this file is stored under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO accesses in this range. The API contract is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field inside the same register.

The important register-field families in this chunk are:

- Interrupt destination groups: `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, `DSC_INTERRUPT_DEST`, `HPO_INTERRUPT_DEST`, and `DPP_INTERRUPT_DEST`. These route display, I2C/DDC, HPD, audio, AUX, DSC, HPO, and DPP events to interrupt handling paths.
- `DMCUB_RBBMIF_SEC_CNTL` plus `RBBMIF_*`: security control, timeout status, timeout-disable masks, interrupt status, and sticky status flags for the DMCUB RBBM interface.
- `DMCUB_REGION*` and `DMCUB_REGION3_CW*`: DMCUB firmware memory windows, base/top addresses, offsets, high-address halves, per-window enables, and TMR AXI-space selection.
- `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, `DMCUB_INTERRUPT_TYPE`, and external interrupt registers: timer, inbox, outbox, GPINT, IH, fault, and register-mailbox interrupt bits.
- DMCUB control and mailbox registers: `DMCUB_SEC_CNTL`, `DMCUB_MEM_CNTL`, inbox/outbox base/size/read/write pointers, timer registers, scratch registers 0 through 23, `DMCUB_CNTL`, `DMCUB_CNTL2`, GPINT data registers, fault-address registers, low-speed wake interrupt enable, memory power control, `HOST_INTERRUPT_CSR`, and register inbox/outbox message/status registers.
- MCIF writeback: `MCIF_WB_BUFMGR_*`, buffer pitch/status/address/size/resolution fields for four buffers, arbitration and SCLK/P-state/self-refresh controls, clock gating, security level, VMID/TMZ, QoS, VCE control, luma/chroma sizes, and high address halves.
- MMHUBBUB: writeback latency watermark, general watermark, warmup config/control/base/region/security/VMID fields, min TTO, SMU watermark control, WBIF misc/outstanding counters, memory power status/control, clock control, soft reset, DMU interface error status, and client unit ID.
- DC perfmon instances 3 and 4: counter select, clear, enable, state, window, interrupt control, compare values, and high/low counter readback fields.
- Azalia/HDA audio: stream index/data windows for streams 0 through 15, clock and global memory-power controls, straps, endpoint/input-endpoint indirect index/data windows, controller clock gating, DTO and SOCCLK controls, DMA controls, RIRB/CORB controls, payload capabilities, CRC controls/results, codec root parameters, function power/reset controls, converter synchronization, and audio port connectivity.
- DCHUBBUB SDPIF and VM fields at the end: `DCHUBBUB_SDPIF_CFG0/1/2`, `VM_REQUEST_PHYSICAL`, force-IO status, framebuffer and AGP base/top/offset fields, local HBM address start/end/lock, and pipe security/noalloc levels for surface, DMDATA, DCC metadata, cursor, 3DLUT, and GPUVM requests.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to register-table construction:

1. DCN 4.2 display code includes the matching generated offset header and this shift/mask header.
2. Block-specific headers use macro families such as `SR`, `SRI`, `SF`, `DMUB_SR`, `DMUB_SF`, `HUBBUB_SF`, and `HWS_SF` to bind generic register-field tables to these generated `dcn_4_2_0_sh_mask.h` names.
3. Runtime objects for DMUB, IRQ service, hubbub, MMHUBBUB/writeback, audio, and hardware sequencing receive register offsets plus these shift/mask tables.
4. Driver helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use the tables to access MMIO bitfields.

The macros in this chunk do not define programming order. DMCUB boot/setup, mailbox messaging, interrupt enable/acknowledge, writeback buffer management, audio initialization, perfmon programming, and DCHUBBUB VM/SDPIF setup are controlled by consumer code and hardware specifications outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing by itself. It names hardware-visible state fields whose lifetime is controlled by DCN hardware, firmware, display driver sequencing, power gating, suspend/resume, and reset paths.

Important state named by this range includes:

- Interrupt routing and status state for display links, HPD, DDC/I2C, AUX, audio, DSC, HPO, DPP, DMCUB, and host register mailboxes.
- DMCUB boot/runtime state: secure reset/status, memory region mappings, code-window enables, inbox/outbox ring base/size/pointers, register-mailbox readiness/messages/responses, GPINT data, timers, scratch registers, firmware fault addresses, and memory power controls.
- MCIF writeback state: buffer ownership/status, pitch, luma/chroma addresses, high address bits, buffer dimensions, interrupt enables/acknowledges, lock state, VMID/security/TMZ, arbitration, self-refresh, P-state, and QoS controls.
- MMHUBBUB state: warmup address ranges, writeback and hubbub power status, clock-gating controls, soft reset, DF/DMU error status, and performance counters.
- Azalia audio state: stream and endpoint indirect register windows, DTO and SOCCLK controls, controller clock gating, codec capabilities, DMA state, CRC generation/result registers, power-state controls, endpoint synchronization, and audio connectivity reports.
- DCHUBBUB SDPIF/VM state: request-credit enable/status/errors, response status clear bits, host-VM security levels, force-IO address/status capture, framebuffer/AGP apertures, local HBM address lock, and per-pipe security/noalloc levels.

Access semantics are not encoded here. Many fields are configuration bits that persist until rewritten or reset, while status/interrupt fields may be latched, write-one-to-clear, self-clearing, read-only, or valid only when the relevant display block is powered and clocked.

## Dependencies And Integration Points

This generated file must remain synchronized with AMD's DCN 4.2 register database and the companion offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`.

Observed DCN 4.2 consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c` includes this header and programs the DMCUB region windows, inbox/outbox pointers, register mailboxes, host interrupts, GPINT/IH interrupt enables, fault/debug readback, and system-memory DMUB setup described by this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.h` builds `dmub_srv_dcn42_reg_offset`, `dmub_srv_dcn42_reg_shift`, and `dmub_srv_dcn42_reg_mask` tables from `DMCUB_*`, `HOST_INTERRUPT_CSR`, `MMHUBBUB_SOFT_RESET`, and DCN VM fields covered here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c` includes this header for HPD and DMCUB outbox interrupt source setup, including `DMCUB_INTERRUPT_ENABLE` and `DMCUB_INTERRUPT_ACK` fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.h` consumes `DCN_VM_FB_LOCATION_*`, `DCN_VM_AGP_*`, `DCHUBBUB_SDPIF_CFG0/1`, and related DCHUBBUB masks in hubbub register/field tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.c` writes SDPIF request/port-control fields through those tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn42/dcn42_mmhubbub.c` updates `MMHUBBUB_CLOCK_CNTL` fine-grain clock-gating fields that are part of the MMHUBBUB family in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` initializes DCN 4.2 audio resources using `AZALIA_AUDIO_DTO`, `AZALIA_CONTROLLER_CLOCK_GATING`, and endpoint/root codec field masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h` defines audio field-list macros for endpoint index/data, supported rate/power-state fields, and related Azalia codec metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce/dce_hwseq.h` supplies shared hardware-sequencer audio register and field-list macros consumed by DCN 4.2 hardware sequencing.

Behaviorally, this range sits at several display integration boundaries: display firmware command transport, interrupt routing, captured-frame/writeback memory traffic, display audio, performance observation, and hubbub memory/VM request policy.

## Risks And Edge Cases

- These are untyped preprocessor constants. An incorrect shift or mask can compile cleanly and only surface as a runtime register-programming failure on specific hardware paths.
- The header is generated. Manual edits risk divergence from AMD's register source, the offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are artificial. The first lines are the tail of `DIG_INTERRUPT_DEST`, and the final lines stop inside the DCHUBBUB SDPIF pipe security/noalloc family. Adjacent chunk reports are needed before making whole-file claims.
- Interrupt destination, enable, acknowledge, and status fields are especially side-effect-sensitive. Wrong masks can route events incorrectly, leave interrupt status stuck, miss HPD/AUX/audio/DMUB events, or create interrupt storms.
- DMCUB region and mailbox fields are boot-critical. Bad base/top/offset/high-address masks can make firmware fetch the wrong memory, corrupt ring buffers, break command submission, or make debug/fault readback misleading.
- DMCUB register mailbox and `HOST_INTERRUPT_CSR` fields form a host/firmware synchronization path. Incorrect ready, response, status, enable, or acknowledge bits can deadlock command exchanges or lose outbox notifications.
- RBBMIF timeout-disable and status bits can hide or misreport DMCUB bus timeouts. Overly broad masks could disable detection for unrelated clients.
- MCIF writeback buffer address, high-address, VMID, security, TMZ, pitch, size, and resolution fields affect memory writes. Wrong masks risk corrupted captures, writes to wrong memory, VM/security violations, overrun/underrun reports, or failures only with high addresses or protected surfaces.
- MMHUBBUB memory-power, clock-gating, soft-reset, and warmup fields are sequencing-sensitive and can interact with suspend/resume, idle power states, display writeback, and firmware initialization.
- Azalia endpoint, stream, DMA, DTO, clock-gating, power-state, and CRC fields affect display audio. Incorrect masks can produce silent audio, format/rate capability mismatches, bad DMA behavior, clocking issues, or unreliable CRC diagnostics.
- DCHUBBUB framebuffer/AGP/local-HBM address fields and pipe security/noalloc levels affect display memory request policy. Incorrect masks can produce VM faults, security-level mismatches, incorrect physical request behavior, or failures under host-VM/RIOMMU paths.
- Perfmon fields are diagnostic but still sensitive: bad select, clear, enable, or compare masks can invalidate performance data or trigger misleading interrupts.

## Test Signals

Useful validation should combine generated-header consistency checks with runtime display and firmware behavior:

- Build DCN 4.2 AMDGPU display support. Missing or renamed macros should surface in `dmub_dcn42.c`, `dmub_dcn42.h`, `irq_service_dcn42.c`, `dcn42_hubbub.h`, `dcn42_hubbub.c`, `dcn42_mmhubbub.c`, `dcn42_resource.c`, `dcn42_resource.h`, and shared DCE audio/hardware-sequencer headers.
- Mechanically compare this range against the authoritative DCN 4.2 register-field database and verify every `_MASK` has the expected paired `__SHIFT`.
- Cross-check registers in this range against `dcn_4_2_0_offset.h` so every field-bearing register has a matching offset/base-index entry.
- Boot DCN 4.2 hardware with DMUB enabled and verify firmware load, region-window setup, inbox/outbox ring pointer movement, register mailbox responses, GPINT/IH behavior, and DMCUB debug/fault readbacks.
- Exercise DMUB outbox interrupts and host register mailbox interrupts. Expected signals are one interrupt per event, correct acknowledge behavior, no stuck status bits, and no missed ready/response notifications.
- Force or simulate DMCUB fault and timeout paths where possible, then check `DMCUB_INST_FETCH_FAULT_ADDR`, `DMCUB_DATA_WRITE_FAULT_ADDR`, `DMCUB_UNDEFINED_ADDRESS_FAULT_ADDR`, and RBBMIF status/flag registers.
- Exercise display writeback across buffer slots, high physical addresses, protected/TMZ paths, different pitches/resolutions, and rapid enable/disable transitions. Watch for MCIF writeback overrun, slice interrupt, buffer-status, VMID/security, and address-fence anomalies.
- Test suspend/resume, idle power transitions, and clock-gating toggles with DMUB, MMHUBBUB, audio, and writeback active; expected results are restored register state and no stuck memory-power status.
- Exercise display audio on all exposed DCN 4.2 audio instances: stream enable/disable, format/rate changes, endpoint capability reads, clock gating, DTO programming, and CRC diagnostics. Expected signals are stable audio, correct capabilities, and no DMA/RIRB/CORB errors.
- Validate interrupt routing for HPD, HPD RX, I2C/DDC, AUX, DSC, HPO, DPP, and audio event families on real connectors where available.
- Use perfmon instances 3 and 4 to select counters, clear counters, run a workload, and read high/low values; expected signals are monotonic or workload-correlated values and correct compare/interrupt behavior.
- Exercise host-VM, AGP/framebuffer aperture, local-HBM, SDPIF credit/error, and pipe security/noalloc paths under multi-plane display workloads. Expected signals are no unexpected VM faults, no SDPIF credit errors, and valid force-IO status only when intentionally triggered.

## Cross-Chunk Notes

This chunk begins after the semantic start of `DIG_INTERRUPT_DEST`, so earlier `DIG_INTERRUPT_DEST` fields are owned by the previous chunk. It ends inside the DCHUBBUB SDPIF pipe field family after `DCHUBBUB_SDPIF_PIPE_GPUVM_SEC_LVL`; adjacent later chunks should cover any remaining pipe-security/noalloc, DCHUBBUB, or VM fields. The merge lane should reconcile those boundaries before producing whole-file conclusions for `dcn_4_2_0_sh_mask.h`.

### subset-b-002225: lines 17729-20256

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 17729-20256

## Purpose

This chunk is generated AMD DCN 4.2.0 display register-field metadata. It contains C preprocessor constants for bit shifts and masks, not executable logic. Runtime AMDGPU display and DMUB code combine these constants with `dcn_4_2_0_offset.h` and register helper macros to read, write, and update individual fields inside DCN 4.2.0 memory-mapped display registers.

The requested range covers 2,093 `#define` lines: 1,047 `__SHIFT` macros and 1,046 `_MASK` macros. It starts at `SDPIF_REQUEST_RATE_LIMIT`, moves through DCHUBBUB return-path, arbitration, VM, performance, HUBP0, HUBPREQ0, HUBPRET0, cursor, and perfmon definitions, and ends inside `HUBP1_DCHUBP_VMPG_CONFIG`. The final `FORCE_ONE_ROW_FOR_FRAME_MASK` for that last register is on the next physical line, outside this chunk, so the missing mask is a chunk-boundary artifact.

Although the repository path is under `ceph-client`, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Register Families In This Chunk

The chunk is organized by generated `addressBlock` comments:

- `dce_dc_dchubbubl_hubbub_ret_path_dispdec`: SDPIF memory power, return-path memory power, DCHUBBUB CRC capture, DCC statistics, compression-buffer and DET sizing, memory power modes/status, reserved compbuf space, and return-path debug index/data.
- `dce_dc_dchubbubl_hubbub_dispdec`: DCHUBBUB arbitration, QoS, DRAM/self-refresh/p-state watermark sets A-D, HostVM controls, watermark-change handshake, MALL controls, timeout enables, global timer, VTG controls, soft reset, clock controls, performance measurement, timeout interrupt status, and FMON controls.
- `dce_dc_dchubbubl_dchubbub_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON5_*` perf counter, perfmon state, control, current-value, high, and low fields.
- `dce_dc_dchubbubl_hubbub_vmrq_if_dispdec`: `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` page-table controls/base/start/end fields, default fault address fields, and VM fault control/status/address fields.
- `dce_dc_dcbubp0_dispdec_hubp_dispdec`: HUBP0 surface format, tiling, viewport, request-size, control, clock, VM page, MALL, debug, measurement-window, and MALL status fields.
- `dce_dc_dcbubp0_dispdec_hubpreq_dispdec`: HUBPREQ0 pitch, VMID, primary/secondary luma/chroma surface and metadata addresses, surface control, flip control, flip interrupts, in-use addresses, TTU/QoS, DMDATA VM, VM aperture/TLB, prefetch, vblank, flip, nominal and per-line delivery timing, cursor settings, memory power, p-state force, and request status fields.
- `dce_dc_dcbubp0_dispdec_hubpret_dispdec`: HUBPRET0 control, memory power, read-line programming/value/status, and interrupt fields.
- `dce_dc_dcbubp0_dispdec_cursor0_dispdec`: cursor plane control/address/size/position/hot-spot/stereo, cursor memory power, DMDATA address/control/QoS/status/software data, and HUBP 3DLUT control/address/DLG fields.
- `dce_dc_dcbubp0_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON6_*` perf counter and perfmon field definitions for HUBP-related monitoring.
- `dce_dc_dcbubp1_dispdec_hubp_dispdec`: beginning of HUBP1 display pipe metadata, covering surface config, address config, tiling, primary/secondary viewports, request-size config, HUBP control, clock control, and most of VM page config.

The range contains both global DCHUBBUB register metadata and the full first HUBP/HUBPREQ/HUBPRET/CURSOR instance for pipe 0, then starts the analogous HUBP1 instance. The repeated HUBP0/HUBP1 shape is important because higher-level display code often instantiates hardware blocks by pipe index.

## Important APIs, Types, And Macros

No functions, structs, enums, variables, locks, allocations, or persistence APIs are declared here. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted register-word mask for isolating that field during read-modify-write.

These names are consumed through AMD display register helper layers, including `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, `SF`, `SR`, `SRI`, `HUBBUB_SF`, `HUBP_SF`, `IPP_SF`, `TF_SF`, `FD_SHIFT`, and `FD_MASK` style macros. The companion offset header supplies addresses; this header supplies field layout inside each address.

Important field groups include:

- DCHUBBUB memory sizing and power: `DCHUBBUB_COMPBUF_CTRL`, `DCHUBBUB_DET0_CTRL` through `DCHUBBUB_DET3_CTRL`, `DCHUBBUB_MEM_PWR_MODE_CTRL`, `DCHUBBUB_MEM_PWR_STATUS`, `DCHUBBUB_SDPIF_MEM_PWR_*`, `DCHUBBUB_RET_PATH_MEM_PWR_*`, and `COMPBUF_MEM_PWR_CTRL_*`.
- DCHUBBUB arbitration and bandwidth: `DCHUBBUB_ARB_DF_REQ_OUTSTAND`, `DCHUBBUB_ARB_SAT_LEVEL`, `DCHUBBUB_ARB_QOS_FORCE`, `DCHUBBUB_ARB_DRAM_STATE_CNTL`, watermark registers A-D, `DCHUBBUB_ARB_HOSTVM_CNTL`, `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL`, and `DCHUBBUB_ARB_MALL_CNTL`.
- VM request metadata: repeated `DCN_VM_CONTEXT<n>_*` fields for page-table depth, block size, base address, start logical page, and end logical page, plus `DCN_VM_FAULT_*`.
- HUBP surface fetch metadata: `HUBP0_DCSURF_*`, `HUBP0_DCHUBP_*`, `HUBPREQ0_DCSURF_*`, `HUBPREQ0_DCN_*`, and equivalent beginning `HUBP1_*` definitions.
- Flip and interrupt metadata: `HUBPREQ0_DCSURF_FLIP_CONTROL`, `HUBPREQ0_DCSURF_FLIP_CONTROL2`, `HUBPREQ0_DCSURF_SURFACE_FLIP_INTERRUPT`, `HUBPRET0_HUBPRET_INTERRUPT`, and DCHUBBUB timeout/performance interrupt fields.
- Cursor and metadata planes: `CURSOR0_0_CURSOR_*`, `CURSOR0_0_DMDATA_*`, and `CURSOR0_0_HUBP_3DLUT_*`.
- Performance/debug: `DCHUBBUB_CRC_*`, `DCHUBBUB_DCC_STAT*`, `DCHUBBUB_PERFORMANCE_MEASUREMENT_*`, `FMON_CTRL`, `DC_PERFMON5_*`, `DC_PERFMON6_*`, HUBP debug muxes, HUBP measure-window controls, and status registers.

## Control Flow And Hardware Behavior

This header has no C control flow. It describes hardware control surfaces that other code sequences with MMIO operations.

For DCHUBBUB, driver code programs buffer allocations, watermarks, arbitration policy, HostVM behavior, MALL behavior, and power modes. A typical flow writes requested DET or compression-buffer sizes, waits for `*_SIZE_CURRENT` fields when the hardware reports a committed size, checks error/status bits such as `CONFIG_ERROR`, then programs watermark sets A-D and requests a watermark change through `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL`.

For VM contexts, runtime code supplies page-table layout and logical aperture information per VMID. The fields here encode page-table depth/block size and high/low portions of page table base, start, and end logical page numbers. Fault control and status fields expose whether invalid/missing PTE/PDE activity is reported, which VMID/client caused it, and the faulting address.

For HUBP/HUBPREQ, the control flow is mode-set and flip oriented. Software programs surface format, tiling, viewport dimensions, request size, VMID, luma/chroma addresses, metadata addresses, DCC/TMZ/encryption-related surface-control bits, TTU/QoS and prefetch/vblank/flip/nominal timing parameters, then arms or observes flip control and flip interrupt state. The macros also describe underflow, timeout, blanking, outstanding-request, and reset fields that mode-set, recovery, and diagnostics paths may poll or clear.

For cursor and DMDATA paths, software uses these fields to configure cursor enable/mode/pitch/size/position/hot spot, cursor memory addresses, DM data addresses, QoS, software data injection, and 3DLUT access. These are typically per-pipe state programmed during cursor updates, plane updates, or color-management updates.

For perfmon and debug, fields describe selectable counters, event selectors, current values, high/low counter reads, interrupt/status fields, CRC one-shot/continuous capture, DCC statistics, FMON, and test-debug index/data windows. Those paths are usually diagnostic, validation, or performance-measurement flows rather than normal scanout setup.

## State And Persistence Behavior

The header itself stores no state and persists no data. It is compile-time metadata.

The underlying registers are live DCN hardware state. Configuration fields such as watermarks, buffer sizes, VM page-table bases, surface addresses, tiling, viewport dimensions, DCC/TMZ flags, MALL selection, cursor geometry, and clock/power enables generally persist until reprogrammed, the block is reset, display power is gated, suspend/resume restores state, or the ASIC resets.

Status and handshake fields are more transient. Examples include `*_CURRENT` size fields, `*_DONE` bits, outstanding-request bits, flip-pending/flip-ready/flip-status bits, underflow and timeout status, VM fault status, perf counter state, CRC one-shot pending, memory power state, MALL status, and HUBPRET interrupt status. Clear fields and interrupt-clear fields likely have side effects by hardware convention, but access type is not encoded in this generated header.

Several blocks cross software and firmware ownership boundaries. DMUB and kernel Display Core can both rely on this generated metadata for DCN 4.2.0 register access. The header does not state which actor owns a given register at a given time, so sequencing, locking, and ownership are provided by higher-level DC/DMUB code and firmware protocols.

## Dependencies And Integration Points

Direct dependencies are the generated AMD DCN 4.2.0 register database and companion headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` supplies matching MMIO offsets and base-index values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c` includes both `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h` for DCN42 DMUB register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.h` defines DCN42 register offset/shift/mask storage used by the DMUB service layer.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.h` references DCHUBBUB fields such as `DCHUBBUB_COMPBUF_CTRL` and `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL` through hubbub register-table macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.h` consumes cursor-control fields through transform/DPP register tables.
- Existing HUBP, hubbub, VMID, IRQ, cursor, and perfmon code from earlier DCN generations shows the same integration pattern: block-specific register tables token-paste register names into generated offset, shift, and mask constants, then runtime helpers perform read-modify-write or polling.

Functional integration points include display mode set, plane address programming, page flip, cursor update, color management/3DLUT setup, memory compression/DCC handling, secure/TMZ surface handling, VM fault reporting, DET/compbuf allocation, bandwidth watermark programming, MALL/sub-viewport behavior, memory power management, underflow/timeout recovery, CRC capture, and display performance monitoring.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can compile cleanly while reading or writing the wrong MMIO bits, corrupting adjacent fields or leaving hardware in an unexpected state.
- The macros are untyped preprocessor constants. The compiler cannot verify that a field belongs to the register being updated, that a value fits in the field width, or that reserved bits are preserved.
- Address and field metadata must match. Using `dcn_4_2_0_sh_mask.h` with the wrong offset header or with a mismatched silicon register table can silently program unrelated registers.
- Chunk boundaries are artificial. This range ends before `HUBP1_DCHUBP_VMPG_CONFIG__FORCE_ONE_ROW_FOR_FRAME_MASK`; adjacent chunks must be merged before making whole-register completeness claims for HUBP1.
- Many fields are side-effect-sensitive. Interrupt clear bits, flip-clear bits, timeout/underflow clears, VM fault acknowledgement, soft reset, memory power force/disable, and debug index/data windows should not be written by generic code without hardware sequencing.
- Repeated indexed blocks can hide copy/generation errors. HUBP0 and HUBP1 are expected to have parallel field layouts for shared hardware features; a single missing or shifted field can produce pipe-specific failures.
- Watermark, arbitration, and p-state fields affect display underrun margins. Incorrect values may only fail under high bandwidth, low memory clocks, self-refresh entry/exit, MALL use, multiple displays, high refresh rates, or suspend/resume.
- Surface address, VM, DCC, and TMZ fields are security- and correctness-sensitive. Bad programming can fetch from the wrong memory, trigger VM faults, expose stale data, break encrypted surfaces, or corrupt scanout.
- Status fields often reflect clocked or power-gated domains. Reads while HUBP, DCHUBBUB, cursor, or memory power domains are disabled can be stale, blocked, or undefined depending on hardware rules not expressed in this header.
- Perfmon, FMON, CRC, and test-debug fields are diagnostic surfaces. Leaving them enabled or mis-selecting sources can perturb validation, hide real underflows, or produce misleading measurements.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU display code with DCN 4.2.0 support enabled; missing or renamed macros should fail in DMUB DCN42, hubbub, DPP/cursor, HUBP, VMID, IRQ, and register-table construction paths.
- Mechanically compare this range against the authoritative generated DCN 4.2.0 register database and `dcn_4_2_0_offset.h`, allowing for the known end-boundary split in `HUBP1_DCHUBP_VMPG_CONFIG`.
- Check every `__SHIFT` macro has the expected `_MASK` partner within the merged source-file view, and verify each mask's least significant set bit matches the declared shift.
- Exercise mode-set and page-flip tests across pipe 0 and pipe 1, including primary and secondary surfaces, stereo/viewport variants, DCC-enabled buffers, chroma planes, metadata addresses, and VMID changes.
- Run cursor movement, cursor format, cursor memory power, DMDATA, and 3DLUT/color-management tests that cover the `CURSOR0_0_*` and HUBP register fields.
- Run memory-pressure and bandwidth tests that stress DET/compbuf sizing, watermark sets A-D, p-state and self-refresh entry/exit, MALL/sub-viewport behavior, high refresh rates, multi-display, and suspend/resume.
- Validate VM fault paths by inducing controlled invalid mappings or aperture violations and confirming `DCN_VM_FAULT_STATUS` and fault address fields report expected VMID/client/address information.
- Verify interrupt and status behavior for flip completion, HUBPRET events, timeout detection, underflow, memory power status, and watermark-change completion; confirm clear bits do not drop unrelated events.
- Use CRC, DCC statistics, perfmon, FMON, and debug counter tests to confirm measurement fields select sources correctly and read high/low values coherently.

## Cross-Chunk Notes

Earlier chunks contain the preceding DCHUBBUB SDPIF pipe security/no-allocate fields that lead into this range. Later chunks continue HUBP1 beyond `HUBP1_DCHUBP_VMPG_CONFIG` and should include the rest of HUBP1 MALL, debug, HUBPREQ, HUBPRET, cursor, and perfmon metadata. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 4.2.0 register families or all pipe instances.

### subset-b-002226: lines 20257-22731

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 20257-22731

## Scope

This chunk is part of the generated DCN 4.2.0 ASIC shift/mask header for AMD display hardware. It contains preprocessor constants only. Every exported item is a `#define` for a hardware register field's `__SHIFT` bit offset or `_MASK` value; there are no C functions, structs, enums, branches, allocations, locks, or direct MMIO accesses in this range.

The line range covers 2,122 macro definitions: 1,061 `__SHIFT` definitions and 1,061 matching `_MASK` definitions. It starts inside the tail of the `HUBP1_DCHUBP_VMPG_CONFIG` register, completes the remaining HUBP1/HUBPREQ1/HUBPRET1/cursor/perfmon field metadata, covers the corresponding HUBP2/HUBPREQ2/HUBPRET2/cursor/perfmon metadata, and then begins the HUBP3/HUBPREQ3 sequence through `HUBPREQ3_DCSURF_SECONDARY_SURFACE_ADDRESS`.

The visible address blocks are:

- `dce_dc_dcbubp1_dispdec_hubpreq_dispdec`
- `dce_dc_dcbubp1_dispdec_hubpret_dispdec`
- `dce_dc_dcbubp1_dispdec_cursor0_dispdec`
- `dce_dc_dcbubp1_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`
- `dce_dc_dcbubp2_dispdec_hubp_dispdec`
- `dce_dc_dcbubp2_dispdec_hubpreq_dispdec`
- `dce_dc_dcbubp2_dispdec_hubpret_dispdec`
- `dce_dc_dcbubp2_dispdec_cursor0_dispdec`
- `dce_dc_dcbubp2_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`
- `dce_dc_dcbubp3_dispdec_hubp_dispdec`
- start of `dce_dc_dcbubp3_dispdec_hubpreq_dispdec`

## Purpose

The purpose of this chunk is to publish the exact bit layout for several repeated DCN 4.2 display pipe front-end blocks. Runtime driver code combines these field constants with companion register-offset constants to read and update hardware registers through AMD display register helpers. The chunk is silicon metadata, not driver logic.

The covered hardware themes are:

- HUBP front-end surface and viewport programming for pipes 2 and 3, plus the tail of pipe 1 MALL/debug/status metadata.
- HUBPREQ request-side surface address, pitch, VM, flip, timing, QoS, prefetch, memory-power, pstate-force, and status metadata for pipes 1 and 2, plus the beginning of pipe 3.
- HUBPRET return-side control, memory-power, read-line, interrupt, and status metadata for pipes 1 and 2.
- Cursor0 metadata for pipes 1 and 2, including cursor surface geometry, cursor memory power, display metadata transport, and HUBP 3D LUT programming.
- DC performance monitor metadata for perfmon instances 7 and 8.

These constants let higher-level DCN code avoid hard-coded bit arithmetic when configuring scanout, memory fetch, page-table traffic, cursor fetch, flip interrupts, MALL usage, display metadata, and performance counters.

## Important Macros and Field Families

The generated macro naming contract is the public API of this header:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Prefixes such as `HUBPREQ1`, `HUBP2`, `CURSOR0_2`, and `DC_PERFMON8` bind otherwise repeated fields to a specific hardware instance.

Important families in this chunk include:

- `HUBP1_DCHUBP_MALL_*`, `HUBP2_DCHUBP_MALL_*`, and `HUBP3_DCHUBP_MALL_*`: select MALL use, cursor MALL use, sub-viewport MALL retrieval start lines, MALL request/response/in-use flags, local cursor retrieve/prefetch state, CRQ/MRQ/DRQ outstanding state, and one-row-for-frame status.
- `HUBP2_DCSURF_*` and `HUBP3_DCSURF_*`: surface format, rotation, horizontal mirror, swizzle, tiling, meta/independent block sizing, primary and secondary viewport start/dimension, chroma viewport start/dimension, request size, detile buffer heights, swath heights, chunk heights, minimum chunk sizes, pte row heights, and meta row heights.
- `HUBP2_DCHUBP_CNTL` and `HUBP3_DCHUBP_CNTL`: HUBP enable, blank enable, cursor enable, VM context selection, soft reset, timeout status/clear/interrupt enable, and underflow status/clear fields.
- `HUBP2_HUBP_CLK_CNTL` and `HUBP3_HUBP_CLK_CNTL`: HUBP clock enable, DISPCLK/DPPCLK/DCFCLK gate-disable and clock-on status fields, fine-grain clock-gating disable, and test clock selection.
- `HUBPREQ1_*` and `HUBPREQ2_*`: surface pitch, VMID, primary/secondary surface addresses, primary/secondary metadata addresses, TMZ/DCC surface controls, flip controls, flip interrupt controls, surface in-use latches, timing/QoS parameters, VM apertures, TLB controls, prefetch/vblank/flip/nominal delivery parameters, cursor delivery parameters, memory-power controls/status, pstate-force controls, and status registers.
- `HUBPRET1_*` and `HUBPRET2_*`: control fields for detile buffer address, crossbar source, DST_Y prefetch behavior, read-line enables/modes, read-line values, read-line status, and HUBPRET interrupt mask/type/clear/status/ack fields.
- `CURSOR0_1_*` and `CURSOR0_2_*`: cursor enable, request mode, 2x magnify, cursor mode, TMZ, pitch, rotation/mirroring bypass, lines per chunk, address, size, position, hot spot, stereo offsets, destination offset, cursor memory-power state, display metadata address/control/QoS/status/software data, and HUBP 3D LUT control/address/deadline fields.
- `DC_PERFMON7_*` and `DC_PERFMON8_*`: event selection, counter value selection, increment mode, run-enable, restart, interrupt enable/status/ack, counter state for eight counters, perfmon state, count-off controls, clock enable, run start/stop selection, captured values, and read selectors.
- `HUBPREQ3_DCSURF_*` at the end of the chunk: the first pipe-3 request-side fields for pitch, VMID, and primary surface address metadata; the rest of the pipe-3 HUBPREQ block continues in the next chunk.

## Control Flow and Runtime Integration

There is no executable control flow in this header. Runtime behavior is indirect:

1. DCN 4.2 source files include `dcn/dcn_4_2_0_offset.h` together with this `dcn/dcn_4_2_0_sh_mask.h` header.
2. Register table macros in DCN code pair address constants from the offset header with shift/mask constants from this header.
3. Helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and DMUB register-table expansion macros compose the actual read/modify/write operations.
4. The hardware-visible behavior occurs in the display engine registers; this header only supplies the compile-time field metadata used to generate correct register values.

Observed direct include sites for this header include DCN 4.2 resource construction, IRQ service mapping, GPIO translation/factory code, and DMUB register initialization. For example, `dmub_srv_dcn42_regs_init()` expands `DMUB_DCN42_FIELDS()` into masks and shifts using `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`, which depend on definitions from this file.

The represented programming flow for these fields is typically:

- Program HUBP surface format, viewport, tiling, request-size, and clock/enable state for a pipe.
- Program HUBPREQ surface addresses, metadata addresses, DCC/TMZ controls, VMID/aperture/TLB details, and delivery-time/QoS parameters.
- Arm or lock surface flips, control flip timing, then observe or clear flip interrupt/status bits.
- Program cursor state, cursor address/geometry, display metadata payloads, and optionally HUBP 3D LUT settings.
- Use HUBPRET and HUBPREQ status/read-line fields for synchronization and diagnostics.
- Use perfmon fields to select events, run counters, read captured values, and acknowledge counter interrupts.

## State and Persistence Behavior

The header owns no mutable state. All state represented by these macros lives in hardware registers and persists only according to the display engine's register-reset and power-state rules.

The represented hardware state includes:

- Surface state: format, rotation, swizzle, tiling, meta address mode, DCC enable, DCC independent block selection, primary/secondary surface addresses, meta-surface addresses, pitch, chroma pitch, viewport start and dimensions, and in-use/earliest-in-use address latches.
- Protection and compression state: TMZ bits for luma/chroma and primary/secondary metadata surfaces, plus DCC enable and DCC block-independence fields. Misprogramming these fields can affect protected memory access and decompression behavior.
- Flip state: update lock, flip type, vupdate skip count, pending status, stereo-sync mode, pending delay, minimum pending time, GSL enable/mask, triple-buffer enable, immediate-flip buffer tracking, flip interrupt masks/types, occurrence bits, status bits, and clear bits.
- VM and memory-fetch state: VMID, DMDATA VM controls, system aperture low/high addresses, L1 TLB policy, VM group/request timing during vblank and flip, PTE/meta chunk timing, pstate force bits, self-refresh status, QoS urgent status, and MPTE/chunk request progress.
- Power state: HUBP clock gates and clock-on status, HUBPREQ request SRAM power controls/status for DPTE/MPTE/meta/PDE/TPTE memories, HUBPRET detile-buffer memory power controls/status, and cursor CROB memory power controls/status.
- MALL state: selection of MALL use, cursor MALL use, sub-viewport MALL retrieval line selection, MALL prefetch/retrieve frame state, outstanding request state, and busy state across CRQ/MRQ/DRQ paths.
- Cursor and metadata state: cursor enable/mode/geometry, surface address, stereo offsets, hot spot, memory-power state, display metadata address, display metadata update/repeat/mode/size, QoS, done/underflow/clear status, software metadata data, and 3D LUT control/address/done state.
- Diagnostic state: HUBP debug mux selections, measurement-window controls, HUBPREQ debug buses, HUBPRET read-line values/status, DC perfmon event/counter control, counter state, counter interrupts, and captured values.

Register state may be reset or lost across GPU reset, display engine reset, pipe reset, power gating, suspend/resume, mode set, or DCN resource reinitialization. Higher-level display state remains the software source of truth and must reprogram these registers when the hardware context is rebuilt.

## Dependencies

This chunk depends on the matching generated address metadata in `dcn_4_2_0_offset.h`. Shift/mask constants alone do not identify MMIO addresses or base indices.

Other important dependencies are:

- AMD display register-helper infrastructure that consumes generated field names through `FD_MASK`, `FD_SHIFT`, `REG_FIELD`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and related macros.
- DCN 4.2 resource and hardware object code, especially HUBP, hubbub, IRQ, DMUB, GPIO, and resource initialization paths that include this header.
- DCN 4.2 hardware register-generation inputs. Because this is generated silicon metadata, manual edits are unsafe unless synchronized with the source register database and companion offset headers.
- Display mode programming and validation logic that computes surface addresses, pitch, tiling, DCC, cursor, prefetch, vblank, flip, and QoS values before register writes occur.
- Interrupt service code that maps HUBP flip events to DAL IRQ sources and relies on the corresponding interrupt mask/status/clear fields being correct.
- Debug and performance tooling that expects perfmon and debug-bus fields to match silicon behavior.

## Integration Points

Primary integration is the macro-name ABI between generated headers and DCN runtime code. A field reference such as `HUBPREQ2_DCSURF_FLIP_CONTROL__SURFACE_FLIP_PENDING` or `CURSOR0_2_DMDATA_STATUS__DMDATA_UNDERFLOW_CLEAR` must resolve to the correct shift and mask for the register helper layer.

Subsystem-level integration points include:

- Plane programming: surface format, viewport, tiling, pitch, rotation/mirror, DCC, TMZ, meta-address, and request-size fields feed scanout setup for each HUBP instance.
- Memory management: VMID, system aperture, TLB, PTE/meta timing, and request memory-power fields connect display scanout to GPU virtual memory and page-table fetch behavior.
- Flip scheduling and IRQs: flip control and flip interrupt fields integrate with page-flip handling, vupdate/vblank timing, stereo synchronization, triple buffering, GSL, and IRQ service status/clear handling.
- Clock and power management: HUBP clock-gating fields, memory-power force/disable/status fields, MALL usage state, UCLK pstate force/status fields, and self-refresh/pstate-allow status bits connect display pipe operation to power-management policy.
- Cursor and metadata: cursor address/shape/position fields and DMDATA fields integrate cursor plane programming with display metadata transport, QoS, underflow detection, and protected-memory operation.
- Color pipeline support: HUBP 3D LUT control, address, TMZ, width, crossbar, and deadline fields connect HUBP-side LUT fetch/setup to later color-pipeline processing.
- Diagnostics: HUBP debug muxes, measurement windows, HUBPREQ/HUBPRET status, read-line status, MALL status, and DC perfmon fields integrate with debugfs-style inspection, trace/debug captures, and performance counter collection.

## Risks and Failure Modes

- Incorrect shift or mask values corrupt adjacent register fields. In these blocks, that can cause bad scanout addresses, wrong protected-memory attributes, DCC mismatch, viewport errors, missed flips, cursor corruption, or memory-fetch underflow.
- Repeated instance prefixes are easy to confuse. `HUBPREQ1`, `HUBPREQ2`, and `HUBPREQ3` contain mostly identical field names; a prefix/offset mismatch can break only one display pipe and escape simple single-monitor testing.
- The chunk starts and ends inside larger generated sequences. The first line is the tail of a HUBP1 VMPG register and the last line is inside the beginning of the HUBPREQ3 address block; the final per-file report must reconcile neighboring chunks before drawing whole-file conclusions.
- Clear, status, and interrupt-ack fields need exact write semantics. Treating clear/ack bits as normal persistent configuration can lose interrupts, repeatedly retrigger interrupts, or hide flip/DMDATA/perfmon events.
- Surface address high fields are narrow while low fields are 32-bit. Consumers must preserve address split semantics and avoid truncation when programming primary, secondary, metadata, cursor, DMDATA, or 3D LUT addresses.
- TMZ and DCC fields affect security and memory interpretation. Stale or wrong masks can lead to protected-buffer access failures, decompression artifacts, or memory faults.
- Timing and QoS fields affect underflow margins. Bad vblank/flip/nominal delivery timing, TTU, refcyc, prefetch, or QoS urgent metadata can produce intermittent underflow tied to resolution, refresh rate, memory clock, cursor state, or multi-plane composition.
- Clock-gating and memory-power masks can wedge register access or fetch paths if force/disable/status fields are misidentified.
- High-bit fields such as `0x80000000L` are common for done/status/debug/ack bits. Consumers should avoid signed or narrow arithmetic assumptions when composing register values.
- Perfmon control and interrupt fields share registers with state/captured values. Bad masks can make diagnostics misleading even when normal display output appears correct.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Build coverage: DCN 4.2 display, DMUB, IRQ, GPIO, and resource code compiles without missing or renamed generated macros.
- Register table validation: `dcn_4_2_0_offset.h` and this shift/mask header remain in sync for HUBP/HUBPREQ/HUBPRET/cursor/perfmon instances 1, 2, and 3.
- Plane scanout tests: primary and secondary surfaces across formats, tiling modes, rotations, mirroring, DCC on/off, TMZ on/off, chroma planes, and meta surfaces.
- Multi-pipe tests: one, two, three, and more active display pipes to catch repeated-instance prefix errors in `HUBPREQ1/2/3`, `HUBP2/3`, `CURSOR0_1/2`, and `DC_PERFMON7/8`.
- Page-flip tests: immediate and synchronized flips, vupdate skip, pending delay, triple buffering, GSL, stereo-sync, flip-away events, and interrupt clear/status handling.
- Underflow and QoS tests: high-resolution/high-refresh modes, memory-clock changes, pstate transitions, self-refresh entry/exit, cursor movement, DMDATA traffic, and MALL use.
- Suspend/resume and reset tests: verify HUBP/HUBPREQ/HUBPRET/cursor/perfmon registers are reinitialized correctly after hardware state is lost.
- Cursor tests: different cursor sizes, modes, hot spots, stereo cursor offsets, protected cursor memory, cursor memory power transitions, DMDATA update/repeat/software paths, and DMDATA underflow clear.
- 3D LUT tests: HUBP 3D LUT enable, addressing, width, crossbar selection, TMZ, address split, deadline parameter, and done status.
- Perfmon diagnostics: event selection, counter run/stop/restart, counter interrupt status/ack, captured value high/low reads, and perfmon clock-enable behavior for instances 7 and 8.
- Debug readback: HUBP/HUBPREQ/HUBPRET status registers, MALL status, read-line status, MPTE/chunk request status, and clock-on/gate status should match expected hardware behavior during mode set, flip, vblank, and pstate transitions.

## Chunk Notes

This report intentionally covers only lines 20257-22731 of `dcn_4_2_0_sh_mask.h`. It is a chunk artifact for an oversized generated header, so the complete per-file report must later merge this with neighboring chunks. The partial HUBPREQ3 block at the end should be interpreted with the following chunk before final per-file conclusions are made.

### subset-b-002227: lines 22732-25252

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 22732-25252

## Purpose

This chunk is a generated AMD DCN 4.2.0 register shift/mask slice. It contains no executable C; its exported interface is a large set of preprocessor constants that describe bit positions and masks for fields inside DCN display hardware registers. The covered range starts in the middle of the `HUBPREQ3` surface-address block, crosses several display-pipe sub-blocks for hub request/return, cursor, performance monitor, DPP top, converter/color, scaler/sharpener, and CM0 color management, and ends at the start of `DC_PERFMON10_PERFCOUNTER_CNTL2`.

The range contains 2,113 `#define` lines: 1,058 `__SHIFT` constants and 1,055 `_MASK` constants. It is a chunk boundary, not a semantic boundary: the first register has its shift in the previous chunk, and the `DC_PERFMON10` block continues in the next chunk. Although the repository path includes `ceph-client`, this file is AMDGPU display hardware metadata, not distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, or direct MMIO operations here. The important API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register word.
- Paired offset headers, especially `dcn_4_2_0_offset.h`, provide the matching register addresses.

The field macros are consumed through AMD display register helpers and token-pasting tables such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and DPP `TF_SF`/`TF2_SF` field lists. For DCN42 specifically, `display/dmub/src/dmub_dcn42.c` includes both `dcn/dcn_4_2_0_offset.h` and this header, then initializes DMUB register masks and shifts with `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`. DPP code follows the same pattern; `display/dc/dpp/dcn401/dcn401_dpp.h` references many of this chunk's `CM0`, `CNVC_CFG0`, and `DSCL0` fields in transfer-function/scaler register tables.

## Register Families In This Chunk

Major register groups covered by the range are:

- `HUBPREQ3_*`: pipe 3 hub request fields for surface and metadata addresses, TMZ/DCC control, flip control, flip interrupts, in-use/earliest-in-use addresses with VMID, request expansion, TTU QoS watermarks, VM aperture/TLB control, blank and destination dimensions, prefetch/vblank/flip/nominal delivery timing, cursor timing, memory power control/status, UCLK p-state forcing, and status registers.
- `HUBPRET3_*`: hub return control fields for DET buffer addressing, channel crossbar selection, memory power control/status, read-line window configuration, vblank/read-line interrupts, read-line snapshots, and read-line status.
- `CURSOR0_3_*`: cursor plane 3 fields for enable/mode/TMZ/pitch, address, size, position, hot spot, stereo offsets, destination offset, cursor memory power, display metadata address/control/status/software data, and HUBP 3D LUT address/control/timing.
- `DC_PERFMON9_*` and partial `DC_PERFMON10_*`: display performance monitor counter selection, counted-value selection, increment/run/interrupt modes, per-counter state, perfmon global state, count-off interrupt controls, counter interrupt status/ack, and high/low counter values.
- `DPP_TOP0_*`: DPP top-level control, soft reset, CRC value/control, and host-read control.
- `CNVC_CFG0_*`: conversion/configuration fields for surface pixel format, format control, floating-point bias/scale, color keying, alpha LUTs, pre-dealpha, pre-degamma, pre-realpha, pre-CSC mode and matrix coefficients, and coefficient formats.
- `CM_CUR0_*`: cursor color-management fields for cursor color values, FP scale/bias, matrix mode, and two cursor matrix banks.
- `DSCL0_*`: scaler and image-sharpening fields for coefficient RAM, scaler mode/taps/ratios/init values, overscan, OTG blanking, recout/MPC sizes, line-buffer data/memory, scaler/OBUF memory power, EASF horizontal/vertical filtering, super-conversion matrices, ringing-estimation gains/reductions, BF/PWL tables, `ISHARP` control/delta/noise/LBA tables, and delta LUT memory power.
- `CM0_*`: color-management fields for bypass and post-CSC, bias, gamma-correction control/LUT, RAMA/RAMB gamma-correction region programming for regions 0-33, HDR multiplier, gamma/histogram memory power/status, dealpha, coefficient formats, debug index/data, histogram selection/scales/biases, histogram lock/index/data/status, and histogram-ready interrupt control.

## Control Flow And Hardware Behavior

This header does not implement control flow. Runtime control flow is created when DCN42 driver, DMUB, IRQ, DPP, cursor, scaler, and color-management code uses these constants to compose register reads and writes.

The fields describe several hardware sequencing surfaces:

- Surface programming and flip sequencing use `HUBPREQ3_DCSURF_*` address/control fields, `SURFACE_UPDATE_LOCK`, pending/away interrupt bits, stereo flip selection, GSL, triple buffering, in-use address readbacks, and VMID fields.
- Hub request timing uses TTU, QoS, prefetch, vblank, flip, nominal delivery, per-line delivery, cursor settings, and p-state fields to keep memory request scheduling aligned with display scanout.
- Hub return and cursor blocks expose vblank/read-line interrupt status/clear/mask fields, cursor address/TMZ/mode state, metadata transfer status, and 3D LUT completion.
- DPP/CNVC/CM/DSCL fields encode the per-pixel processing pipeline: source format conversion, pre-CSC, cursor color transforms, scaling/filtering, sharpening, post-CSC, gamma correction, HDR multiplication, histogram collection, and optional bypass/dealpha behavior.
- Performance monitor fields configure event selection, run/stop conditions, counter active state, counter interrupts, and counter high/low values for display performance diagnostics.

Consumers normally perform read-modify-write operations: fetch a register, clear a field with the `_MASK`, shift the new value by `__SHIFT`, write the updated word, or extract status by applying the mask and shifting back. Interrupt and status paths poll or acknowledge bits using the same definitions, but the header does not encode which fields are read-only, sticky, write-one-to-clear, or self-clearing.

## State And Persistence Behavior

The header itself has no runtime state and persists nothing. It is a compile-time hardware ABI description.

The represented hardware registers are live display state. Configuration fields such as surface addresses, DCC/TMZ enables, QoS levels, VM/TLB controls, scaler ratios, CSC coefficients, LUT region tables, color-key settings, gamma-correction regions, memory-power force/disable bits, and perfmon counter selections typically persist until reprogrammed by modeset, plane update, cursor update, color-management update, power-management code, DMUB firmware, suspend/resume, or GPU reset.

Status and handshake fields are more transient. Examples include flip pending/occurred/status bits, in-use/earliest-in-use address readbacks, read-line/vblank status, cursor metadata done/underflow, 3D LUT done, perfmon active/counter interrupt status, current CSC/gamma mode readbacks, memory-power state bits, histogram ready/in-use/skipped/overflow/incomplete state, and scaler update-pending state. Clear or ack fields, such as flip interrupt clears, hub return interrupt clears, metadata underflow clear, perf counter interrupt acks, and histogram-ready interrupt control, are side-effect-sensitive and must be used with the hardware programming model.

## Dependencies And Integration Points

This chunk depends on the AMD generated register ecosystem staying synchronized:

- `dcn_4_2_0_offset.h` supplies the address/base-index side for these fields.
- DCN42 code includes the header from `dmub_dcn42.c`, `dcn42_clk_mgr.c`, `hw_factory_dcn42.c`, `hw_translate_dcn42.c`, `irq_service_dcn42.c`, and `dcn42_resource.c`.
- DPP and color-management code integrates many `CM0`, `CNVC_CFG0`, and `DSCL0` fields through transfer-function and scaler register lists.
- Cursor, hubp/hubpret, IRQ, DMUB, and perf diagnostics code can consume the corresponding generated names through the same register-helper macros.

Functional integration points include atomic plane flips, display scanout memory requests, cursor updates, display metadata transfer, vblank/read-line interrupts, DPP reset/CRC/debug, format conversion, color keying, pre/post color-space conversion, scaling, sharpening, gamma correction, histogram collection, memory power gating, and display performance monitoring.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong mask or shift can compile successfully while programming the wrong hardware bits.
- The chunk is partial at both ends. The initial `HUBPREQ3_DCSURF_SECONDARY_SURFACE_ADDRESS` register is missing its shift in this range, and `DC_PERFMON10_PERFCOUNTER_CNTL2` continues in the following chunk.
- Many fields are side-effect-sensitive. Confusing interrupt status, clear, mask, and type bits can drop flip/vblank/read-line/perf/histogram events or create interrupt storms.
- Surface address, VMID, TMZ, DCC, VM aperture, TLB, and p-state fields affect memory access and protected-surface behavior; bad masks can cause scanout faults, blanking, stale frames, or security-sensitive address/protection mistakes.
- Timing fields for TTU, prefetch, vblank, flip, per-line delivery, scaler init, and QoS are workload- and mode-dependent. Incorrect values can appear only under high-resolution, high-refresh, multi-plane, cursor, or bandwidth-stress modes.
- Color/scaler/gamma fields are numerically dense. Off-by-one masks in CSC coefficients, LUT indices/data, RAMA/RAMB region tables, EASF/ISHARP PWL tables, or histogram coefficients can produce subtle image-quality defects rather than obvious failures.
- Memory power force/disable/state fields span HUBPREQ, HUBPRET, cursor, DSCL/OBUF, CM gamma, and histogram memories. Incorrect sequencing around power-gated blocks can produce stale status reads or lost writes.
- Perfmon registers use repeated counter fields and high/low value pairs. Incorrect counter select, ack, or active-state masks can make diagnostics misleading without affecting normal display output.

## Test Signals

Useful validation signals for this chunk include:

- Build DCN42 AMDGPU display code that includes `dcn_4_2_0_sh_mask.h`, especially DMUB, IRQ, GPIO, clock-manager, and resource paths.
- Static generated-header checks that every `__SHIFT` has a matching `_MASK`, masks are aligned with shifts, and every register in this chunk has a matching offset/base-index entry in `dcn_4_2_0_offset.h`.
- Modeset and atomic plane-flip tests covering primary and secondary surfaces, DCC, TMZ, stereoscopic/flip pending paths, GSL/triple buffering, and multi-plane scanout.
- Bandwidth and timing stress tests across high refresh, high resolution, cursor movement, vblank/read-line interrupts, FCLK/UCLK p-state changes, and suspend/resume.
- Cursor tests covering address, size, hot spot, stereo offset, metadata transfer, underflow clear, memory power, and HUBP 3D LUT completion.
- Color pipeline tests for CNVC format conversion, color keying, pre/post CSC, cursor matrix/color transforms, gamma correction RAMA/RAMB programming, HDR multiplier, histogram collection/readback, and dealpha behavior.
- Scaler and sharpening tests covering coefficient RAM programming, tap counts, ratios/init values, overscan, line-buffer partitioning, EASF, ISHARP, PWL table writes, and scaler update-pending state.
- Perfmon diagnostics that program `DC_PERFMON9` and adjacent `DC_PERFMON10` counters, verify active/state transitions, read high/low values, and acknowledge only intended counter interrupts.

## Cross-Chunk Notes

The preceding chunk is needed to complete the first `HUBPREQ3_DCSURF_SECONDARY_SURFACE_ADDRESS` shift/mask pair and earlier HUBPREQ3 setup. The following chunk is needed for the rest of `DC_PERFMON10` and any later DPP performance-monitor definitions. Final per-file analysis should reconcile these boundaries before drawing conclusions about missing fields or complete register families.

### subset-b-002228: lines 25253-27781

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 25253-27781

## Scope

This chunk is a generated AMD DCN 4.2.0 register shift/mask header slice. It contains C preprocessor constants only: every exported symbol maps a hardware register field to either a bit shift (`__SHIFT`) or a bit mask (`_MASK`). There are no functions, structs, enums, storage objects, branches, or direct runtime side effects in this slice.

The slice starts in the tail of the `DC_PERFMON10_PERFCOUNTER_CNTL2` field definitions, then covers the DPP1 display-pipe register field metadata, and ends at the start of `DSCL2_DSCL_EASF_V_RINGEST_3TAP_CNTL3`. It is therefore a chunk-level view of a larger file; adjacent chunks are needed for the full `DC_PERFMON10` start and the rest of the DPP2 scaler/EASF block.

## Purpose

The header gives the AMD display driver compile-time knowledge of DCN 4.2.0 register bit layouts. Driver code combines these `_MASK` and `__SHIFT` macros with register-address macros and register helper macros to read, update, and compose values for display controller hardware.

Within this chunk, the hardware domains are:

- `DC_PERFMON10` and `DC_PERFMON11`: display performance monitor counter controls, state, current-value, interrupt status/ack, read select, and low/high counter values.
- `DPP_TOP1` and `DPP_TOP2`: display pipe processor top-level clock gating, soft reset, DPP CRC, and host-read rate control fields.
- `CNVC_CFG1` and `CNVC_CFG2`: converter pixel format, format expansion/conversion, alpha, color keying, pre-dealpha, pre-color-space conversion matrices, coefficient format, pre-degamma, and pre-realpha fields.
- `CM_CUR1` and `CM_CUR2`: cursor enable/mode/color, cursor floating-point scale/bias, and two cursor matrix banks.
- `DSCL1` and the beginning of `DSCL2`: scaler coefficient RAM, scaler mode, tap counts, fixed-point scale ratios and initial phases, chroma/luma variants, black color, update/autocal controls, overscan, blanking, recout/MPC sizes, line-buffer and output-buffer controls, memory power state, EASF sharpening/ring-estimation controls, image-sharpening controls, and LUT memory power fields.
- `CM1`: color management bypass/update, post-CSC matrices, bias, gamma correction LUT and piecewise region programming for RAM A/B, HDR multiplier, memory power, dealpha, debug, histogram collection/status, and histogram interrupt fields.

## Important APIs, Types, And Macros

This chunk exports macro constants following the generated naming contract:

- `REGISTER__FIELD__SHIFT`: bit offset of `FIELD` within `REGISTER`.
- `REGISTER__FIELD_MASK`: bit mask of `FIELD` within `REGISTER`.

The most important macro families in this chunk are:

- Performance monitor macros such as `DC_PERFMON10_PERFCOUNTER_STATE__PERFCOUNTER_CNT0_STATE_MASK`, `DC_PERFMON10_PERFMON_CNTL__PERFMON_CNTOFF_INT_ACK_MASK`, and the parallel `DC_PERFMON11_*` symbols.
- DPP top-level control macros such as `DPP_TOP1_DPP_CONTROL__DPP_CLOCK_ENABLE_MASK`, `DPP_TOP1_DPP_SOFT_RESET__DSCL_SOFT_RESET_MASK`, `DPP_TOP1_DPP_CRC_CTRL__DPP_CRC_SRC_SEL_MASK`, and the same `DPP_TOP2_*` family.
- Converter macros such as `CNVC_CFG1_FORMAT_CONTROL__CNVC_BYPASS_MASK`, `CNVC_CFG1_COLOR_KEYER_*`, `CNVC_CFG1_PRE_CSC_*`, and matching `CNVC_CFG2_*` symbols.
- Cursor macros such as `CM_CUR1_CURSOR0_CONTROL__CUR0_ENABLE_MASK`, `CM_CUR1_CUR0_MATRIX_MODE__CUR0_MATRIX_MODE_CURRENT_MASK`, and matrix-bank constants for `_A` and `_B`, plus the `CM_CUR2_*` mirror.
- Scaler macros such as `DSCL1_SCL_MODE__DSCL_MODE_MASK`, `DSCL1_SCL_TAP_CONTROL__SCL_H_NUM_TAPS_MASK`, `DSCL1_SCL_HORZ_FILTER_SCALE_RATIO__SCL_H_SCALE_RATIO_MASK`, `DSCL1_DSCL_MEM_PWR_CTRL__LB_MEM_PWR_MODE_MASK`, `DSCL1_OBUF_MEM_PWR_CTRL__OBUF_MEM_PWR_STATE_MASK`, `DSCL1_DSCL_EASF_*`, and the opening `DSCL2_*` mirror.
- Color-management macros such as `CM1_CM_POST_CSC_*`, `CM1_CM_GAMCOR_CONTROL__CM_GAMCOR_MODE_MASK`, `CM1_CM_GAMCOR_LUT_*`, `CM1_CM_GAMCOR_RAMA_REGION_*`, `CM1_CM_GAMCOR_RAMB_REGION_*`, `CM1_CM_HIST_STATUS__CM_HIST_COUNT_OVERFLOW_MASK`, and `CM1_CM_HIST_INT_CONTROL__CM_HIST_RDY_INT_EN_MASK`.

The header itself defines no helper API, but the macro names are designed for AMD display register helpers that concatenate register and field names, commonly through local `FN(reg_name, field_name)` macros and `REG_GET`, `REG_SET`, `REG_UPDATE`, or related register-access wrappers in the display driver.

## Control Flow

There is no executable control flow. The effective runtime flow happens in consumers:

1. A DCN 4.2 component includes this mask header together with the matching register-address header.
2. The component's register tables or helper macros reference a `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` pair.
3. The register helper reads or writes a MMIO register, masking and shifting the field into or out of the register value.
4. The hardware changes display pipeline state, reports status, or returns latched counter/histogram data depending on the specific register field.

The ordering in this chunk is hardware-address-block oriented. DPP1 blocks are grouped as top, converter, cursor, scaler, color management, and DPP-local perfmon. DPP2 then begins with the same repeated structure, indicating multiple display pipes with identical or near-identical bit layouts under different register instances.

## State And Persistence Behavior

The macros do not persist state. They describe persistent hardware register fields whose values live in GPU display controller registers while the device is powered and configured.

State-bearing hardware represented by this chunk includes:

- Perfmon control and counter state: enable/state bits, counter active flags, interrupt enable/status/ack bits, counted-value selectors, counter low/high values, and current-value high/low fields.
- DPP pipeline state: clock enable/gating-disable bits, soft-reset bits for converter/scaler/color/output-buffer/histogram subblocks, and CRC control/readback state.
- Converter and cursor state: pixel format, alpha plane enable, color key and alpha LUT configuration, pre-CSC matrices and current selection bits, cursor enable/update-pending bits, cursor colors, and cursor matrix banks.
- Scaler state: coefficient RAM selection/current bits, phase and ratio registers, autocal pipe identifiers, viewport/blanking/recout sizes, line-buffer partitioning, memory power state/status, output-buffer status, EASF/sharpening controls, and sharpening LUT memory power state.
- Color-management state: post-CSC matrices and current mode bits, gamma LUT index/data/control, RAM A/B gamma region programming, memory power status, histogram lock/index/data/status fields, and histogram ready interrupt enable/status.

Because these are MMIO field definitions, persistence is hardware-specific. Values may be reset by GPU reset, display pipe reset, power-gating, mode set reprogramming, or explicit writes by the display manager. `*_UPDATE_PENDING`, `*_CURRENT`, `*_STATUS`, and `*_STATE` fields are especially sensitive to hardware sequencing and may reflect latched or asynchronous state rather than a simple software-owned value.

## Dependencies

Direct dependencies are limited to the C preprocessor and the surrounding generated register header set. The include guard and SPDX/copyright header live outside this chunk, but this slice depends on the whole file being included as a normal header.

Runtime consumers depend on:

- Matching DCN 4.2.0 register address headers that define the register offsets corresponding to these field masks.
- AMD display register helper infrastructure that uses mask/shift pairs to perform safe field updates.
- Hardware register specifications for DCN 4.2.0, because the correctness of every constant is defined by the ASIC register map rather than by local source logic.

Repository usage search shows `dcn_4_2_0_sh_mask.h` is included by DCN 4.2 display paths such as DMUB support, IRQ service, and GPIO translation/factory code. Broader DC register programming patterns use `FN()` and `REG_*` helpers to bind generated field names into component-specific register tables.

## Integration Points

This chunk integrates with:

- DCN 4.2 display enablement code that constructs per-block register structures for DPP, CNVC, DSCL, CM, cursor, perfmon, and related display subblocks.
- Display mode programming paths that set scaler ratios, taps, phase initialization, viewport/recout sizing, color conversion, degamma/gamma/post-CSC, cursor format, and alpha behavior.
- Diagnostics and validation paths that read CRC values, performance counters, histogram data/status, debug data, and memory power status.
- Power-management and reset sequencing through DPP clock-gating fields, DPP soft reset bits, scaler/color/output-buffer memory power control fields, and related state/status masks.
- Interrupt/status handling for perfmon counter interrupts and CM histogram-ready interrupts.

The repeated `*1` and `*2` register families indicate per-pipe integration: DPP1 and DPP2 use the same software programming model with different physical register instances. This lets shared display code operate on an indexed pipe by selecting the right generated register addresses and field masks.

## Risks And Edge Cases

- Generated constant drift is the primary risk. A wrong mask or shift can silently write the wrong bits in a hardware register, corrupting adjacent fields such as clock gating, reset, color conversion, scaler phase, or interrupt ack bits.
- Several fields are write-one-to-clear or ack-like by convention (`*_ACK`, interrupt status/ack, update-pending/current fields). Consumers must know hardware semantics; the mask alone does not encode whether a bit is read-only, write-one-to-clear, self-clearing, or latched.
- Packed matrix, gamma, PWL, and scaler fields often share 32-bit registers as two 16-bit values or multiple narrower values. Incorrect value range checks in callers can overflow into neighboring fields even when masks are correct if helpers are bypassed.
- DPP1 and DPP2 families are near-identical. Copy/paste or table-index mistakes can program one pipe using another pipe's register address set even though the field masks look valid.
- This chunk begins and ends mid-family. Whole-file analysis must reconcile the incomplete `DC_PERFMON10_PERFCOUNTER_CNTL2` lead-in and the incomplete `DSCL2_DSCL_EASF_V_RINGEST_3TAP_CNTL3` tail with adjacent chunks.
- Large generated headers can hide duplicate or inconsistent symbols across ASIC versions. Build coverage catches syntax/name collisions, but hardware validation is needed to catch semantically wrong bit positions.

## Test Signals

Useful validation signals for this chunk are:

- C build coverage for all DCN 4.2 include consumers, proving the generated macro names, include guard, and integer constants compile.
- Static checks that every `__SHIFT` has a corresponding `_MASK` for the same register field and that masks align with shifts and expected field widths.
- Cross-version diffs against nearby DCN mask headers, especially repeated DPP1/DPP2/CNVC/DSCL/CM fields, to flag unexpected layout changes.
- Register programming tests or hardware bring-up logs showing DPP clock/reset, scaler ratios/taps, cursor setup, color conversion/gamma, CRC readback, histogram readback, and perfmon interrupts operate on DCN 4.2 hardware.
- Runtime debugfs or driver traces confirming `REG_UPDATE`/`REG_GET` calls compose values that stay within these masks and do not disturb adjacent fields.
- Display validation tests for mode set, scaling, color management, cursor, CRC, histogram, and power-gating scenarios, because those are the hardware behaviors represented by this field metadata.

### subset-b-002229: lines 27782-30308

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 27782-30308

## Purpose

This chunk is a generated AMD DCN 4.2.0 shift/mask header slice for display pipeline registers. It contains no executable C logic; its public interface is a set of preprocessor constants that map register fields to bit positions (`__SHIFT`) and bit masks (`_MASK`) for the DCN42 display pipeline.

The requested range contains 2,113 generated definitions and 400 commented register headings. It starts inside the `DSCL2` display scaler block, covers the rest of DSCL2 enhanced adaptive scaler and image-sharpening controls, covers the `CM2` color-management block, covers the `DC_PERFMON12` performance-monitor block, then starts DPP instance 3 with `DPP_TOP3`, `CNVC_CFG3`, `CM_CUR3`, `DSCL3`, and the beginning of `CM3` gamma-correction RAM metadata. The chunk boundary is artificial: DSCL2 started before line 27782, and the final `CM3_CM_GAMCOR_RAMB_REGION_*` series continues after line 30308.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO reads/writes in this range. The generated macro naming convention is the API:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the field mask within the same register.

The main register families in this chunk are:

- `DSCL2_DSCL_EASF_*`: enhanced adaptive scaler fields for horizontal and vertical ring-estimation force, blur-filter control, final max/min limits, BF1 piecewise-linear segments 0-7, and BF3 piecewise-linear segments 0-5. These define the tuning surface for adaptive sharpening/ringing behavior on DPP/scaler instance 2.
- `DSCL2_ISHARP_*`: image sharpening controls, delta LUT host/index/data fields, nonlinear delta soft clipping, noise-detection thresholds, noise-gain PWL fields, LBA PWL segments, and image-sharpening delta LUT memory-power control/status.
- `CM2_CM_*`: color-management fields for bypass/update state, post-CSC controls and matrix coefficients, bias, gamma-correction control, gamma LUT index/data/control, RAM A and RAM B gamma-correction region starts/slopes/bases/ends/offsets/region tables, HDR multiplier, memory-power control/status, dealpha, coefficient format, test-debug registers, and histogram controls/data/status/interrupt controls.
- `DC_PERFMON12_*`: display performance counter and perfmon control/state/value registers. This block names fields such as counter enable/reset/mode, event selection, perfmon state, manual trigger, and counter high/low/current-value fields.
- `DPP_TOP3_*`: DPP instance 3 top-level control, soft reset, CRC values/control, and host-read control.
- `CNVC_CFG3_*`: converter-format and pre-color-processing fields for DPP instance 3, including surface pixel format, format expansion/crossbar/clamping, fixed-point bias/scale, color/luma keyer limits, alpha 2-bit LUT values, pre-dealpha, pre-CSC mode/matrices, pre-degamma, and pre-realpha.
- `CM_CUR3_*`: cursor color-management fields for cursor mode/enable/expansion, color entries, floating-point scale/bias, and cursor matrix mode/coefficient sets.
- `DSCL3_*`: instance 3 scaler fields for coefficient RAM, scaler mode/taps, viewport/output sizes, line-buffer format/memory, update/autocal, overscan/blanking, scaler ratios/init values, memory power, output buffer, scaler color-conversion matrix, EASF, iSharp, and bottom-field vertical init values.
- `CM3_CM_*` beginning: DPP instance 3 color-management and gamma-correction RAM A/B field definitions. This chunk reaches only the early part of `CM3_CM_GAMCOR_RAMB_REGION_*`.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN42 display code includes `dcn_4_2_0_offset.h` and this matching `dcn_4_2_0_sh_mask.h`.
2. `dcn42_resource.c` builds per-instance DPP register tables with `DPP_REG_LIST_DCN42_COMMON_RI(id)` and initializes global `dcn42_dpp_shift` / `dcn42_dpp_mask` tables with `DPP_REG_LIST_SH_MASK_DCN42_COMMON(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN42_COMMON(_MASK)`.
3. `dcn42_dpp_create()` initializes `dpp_regs[0..3]` and passes the selected instance register table plus the shared shift/mask tables to `dpp42_construct()`.
4. Runtime DPP code uses generic register helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_*`, `REG_GET`, and `REG_WAIT`. Those helpers consume the register offsets and these generated shift/mask values to program hardware fields.

The macros in this chunk do not describe programming order. Sequencing for scaler setup, sharpening, gamma LUT programming, CSC updates, cursor conversion, histogram reads, memory-power transitions, and perfmon sampling is implemented in DPP/resource/hardware-sequencer code and constrained by hardware behavior outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields:

- DSCL2/DSCL3 scaler configuration: scaling modes, tap counts, coefficient RAM selectors/data, horizontal/vertical scale ratios, initial phases, recout/MPC dimensions, overscan, blanking windows, line-buffer memory layout, update-pending state, autocal parameters, scaler color-conversion matrix, EASF tuning, iSharp tuning, and scaler/LUT/output-buffer memory-power controls.
- CM2/CM3 color-management state: bypass/update-pending bits, pre/post CSC modes and matrices, bias and HDR multiplier, gamma-correction LUT RAM selection and current selection, LUT index/data access windows, RAM A/B PWL region descriptors, memory-power state, dealpha/coefficient format, histogram controls/data/status/lock, and test-debug muxes.
- CNVC_CFG3 and CM_CUR3 state: input format conversion, alpha handling, color keying, pre-degamma/pre-CSC/pre-dealpha/pre-realpha, cursor enable/mode/color, cursor FP scale/bias, and cursor matrix selection/current state.
- DPP_TOP3 state: DPP clock enable, soft reset, CRC capture/readback, and host-read control.
- DC_PERFMON12 state: performance-counter control, selected event source, counter state, high/low/current-value registers, and manual/auto perfmon controls.

Persistence and side effects are hardware-defined. Configuration fields typically remain until modeset, plane update, pipe disable, power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status fields can be latched, read-only, write-one-to-clear, double-buffered, or valid only while the relevant DPP/scaler/color block is powered and clocked. This file only supplies bit locations; it does not encode those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DCN 4.2.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` supplies matching register offsets and base-index values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` includes both generated headers, creates `dpp_regs[4]`, `tf_shift`, and `tf_mask`, and constructs DPP instances from those tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h` defines the DPP register list. It expects many register names covered here, especially `CM_GAMCOR_*`, `CM_HIST_*`, `DSCL_*`, `CNVC_CFG_*`, and `CM_CUR_*` fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.h` defines `DPP_REG_LIST_SH_MASK_DCN42_COMMON(mask_sh)`, `struct dcn42_dpp_shift`, and `struct dcn42_dpp_mask`. The macro uses instance-0 generated names, and `SRI_ARR` register lists bind the same generic field layout to instances 0-3.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.c` uses these fields for histogram control/readout and inherits DPP setup behavior from earlier DCN DPP implementations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp_cm.c` and related DPP code consume the gamma-correction fields by copying shifts/masks into transform/gamma helper structures and programming RAM A/B LUTs, offsets, starts, slopes, end points, and region descriptors.

Behaviorally, this chunk is part of the DPP path that transforms plane pixels before composition/output. It describes register fields for scaling, sharpening, format conversion, cursor blending/color conversion, color correction, gamma correction, histogram collection, CRC/debug readback, and DPP-local performance monitoring.

## Risks And Edge Cases

- These constants are untyped preprocessor metadata. A wrong shift or mask can compile cleanly while silently programming the wrong hardware bits.
- The file is generated. Manual edits risk divergence from the authoritative register database, companion offset header, firmware expectations, and hardware documentation.
- Chunk boundaries are not semantic. The first lines start after earlier `DSCL2` scaler/EASF fields, and the final lines stop inside the `CM3_CM_GAMCOR_RAMB_REGION_*` table. Whole-block claims require adjacent chunks.
- The DPP shift/mask tables use instance-0 field names as the generic field layout while register offsets select each instance. Per-instance generated copies must remain structurally consistent; an instance-only mismatch can affect only DPP2 or DPP3 planes.
- DSCL/EASF/iSharp fields are image-quality sensitive. Incorrect masks for PWL segments, ring-estimation gains, noise thresholds, soft clipping, or delta LUT access can produce visible ringing, blur, oversharpening, flicker, or format-specific artifacts rather than obvious failures.
- Scaler ratio/init/tap/memory fields are timing and format sensitive. Bad values can cause underflow, incorrect chroma placement, wrong recout size, corruption on interlaced/bottom-field paths, or failures only at high scaling ratios.
- Gamma-correction RAM fields are double-buffer and RAM-select sensitive. Wrong masks for `CM_GAMCOR_SELECT`, `*_CURRENT`, region descriptors, offsets, start/end slopes, or LUT host/index/data access can swap RAM A/B unexpectedly, corrupt color curves, or cause tearing during color updates.
- Histogram fields use lock/index/data/status sequencing. Incorrect status or lock masks can cause stale reads, mixed buffer data, missed ready status, or repeated accumulation of old bins.
- Memory-power control/status fields are sequencing-sensitive. Bad masks can leave LUT/line-buffer/output-buffer/gamma memories powered off while programming or prevent expected power savings.
- DPP_TOP3 clock/reset/CRC fields can break a single pipe. A wrong clock-enable or soft-reset bit can disable instance 3, while CRC masks can make debug validation misleading.
- Perfmon field mistakes often appear only in diagnostics. Wrong event-select or counter-state masks can produce plausible but invalid performance data.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display coverage:

- Build DCN42 AMDGPU display support. Missing or renamed macros should surface in `dcn42_resource.c`, `dcn42_resource.h`, `dcn42_dpp.h`, and DPP color/scaler implementation files.
- Mechanically compare this range against the authoritative DCN 4.2.0 register-field database and ensure each `_MASK` has the expected paired `__SHIFT`.
- Cross-check every register family in this chunk against `dcn_4_2_0_offset.h` so each field group has a corresponding register offset/base-index entry.
- Run static repeated-instance checks across `DSCL2` versus `DSCL3`, `CM2` versus `CM3`, `CNVC_CFG3`, and `CM_CUR3`, allowing intentional instance prefixes but flagging missing or shape-mismatched fields.
- Exercise scaling on planes routed through DPP2 and DPP3: upscaling, downscaling, chroma formats, alpha-enabled formats, interlaced/bottom-field paths, high-resolution/high-refresh modes, and rapid plane size changes. Watch for corruption, underflow, wrong recout/MPC dimensions, or stuck update-pending state.
- Exercise EASF/iSharp controls with visual/CRC comparisons and register dumps. Look for ringing, blur, clipping, noise gain anomalies, and correct delta LUT memory-power state.
- Validate color-management programming with gamma ramps, HDR multiplier changes, pre/post CSC matrices, bias, dealpha, RAM A/B gamma selection flips, and suspend/resume. Expected signals are correct color output, stable current-selection readback, and no stale LUT RAM selection.
- Exercise cursor formats and matrix paths on DPP3 with alpha and FP scale/bias variations.
- Read DPP histograms using `dcn42_dpp.c` paths across RGB/luma modes. Expected signals are ready status, correct lock/index/data sequencing, and plausible channel bin accumulation.
- Validate `DPP_TOP3` CRC and soft-reset behavior with display CRC/debug tooling where available.
- Exercise `DC_PERFMON12` counters through existing debug/perf instrumentation and confirm counter state, high/low values, and event selection match the selected DPP pipeline.

## Cross-Chunk Notes

The previous chunk owns the earlier DSCL2 scaler/EASF definitions before `DSCL2_DSCL_EASF_RINGEST_FORCE`. This chunk owns the DSCL2 EASF tail, DSCL2 iSharp, all visible CM2/perfmon/DPP_TOP3/CNVC_CFG3/CM_CUR3/DSCL3 definitions, and the beginning of CM3 gamma-correction metadata. The next chunk must complete `CM3_CM_GAMCOR_RAMB_REGION_*` and any remaining CM3 fields before a final per-file document makes whole-block claims about DPP3 color management.

### subset-b-002230: lines 30309-32771

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 30309-32771

## Purpose

This chunk is generated AMD DCN 4.2.0 register-field metadata. It contains no executable C logic; it exports preprocessor constants that describe bit positions and masks for several display color-management, performance-monitor, DisplayPort AUX, hotplug-detect, mux, formatter, display-pattern-generator, OPP buffer, OPP pipe, and pipe-CRC registers. AMDGPU Display Core pairs these definitions with `dcn_4_2_0_offset.h` and register-helper macros to pack, extract, and update individual MMIO fields.

The range contains 2,463 `#define` lines: 1,078 `__SHIFT` macros and 1,091 `_MASK` macros. It starts inside `CM3_CM_GAMCOR_RAMB_REGION_2_3`: the register comment and all shifts are included, but the previous chunk owns the preceding `REGION_0_1` register and line 30309 begins in the `REGION_2_3` definitions. It ends inside `DPG1_DPG_DIMENSIONS`: the active-height/width shifts and active-height mask are included, while the active-width mask and the rest of DPG1 continue after this chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, callbacks, or direct MMIO reads/writes in this range. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for encoding or decoding a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, preserving, clearing, or writing that field.

Major register families in this chunk:

- `CM3_CM_GAMCOR_RAMB_*`, `CM3_CM_HDR_MULT_COEF`, `CM3_CM_MEM_PWR_*`, `CM3_CM_DEALPHA`, `CM3_CM_COEF_FORMAT`, `CM3_CM_TEST_DEBUG_*`, and `CM3_CM_HIST_*`: DPP3 color-management gamma-correction RAM-B region layout, HDR multiplier coefficient, color/histogram memory power controls and status, dealpha and coefficient-format controls, CM debug index/data, histogram source selection, coefficients, bias, lock/index/data/status, and histogram-ready interrupt control.
- `DC_PERFMON13_*`: DPP3 performance counter controls, counter state, perfmon control, comparison/increment interrupt configuration, and counter high/low value fields.
- `DP_AUX0_*` through `DP_AUX4_*`: five DisplayPort AUX channel instances. Each instance exposes AUX enable/reset, low-speed read control, HPD selection, impedance calibration/test mode, software transaction control, software/DMCU arbitration, interrupt enables and acknowledgements, software and low-speed status/error reporting, software and low-speed data/index fields, AUX DPHY TX/RX timing controls, TX/RX PHY status, and AUX PHY wake request/status fields.
- `HPD0_*` through `HPD4_*`: five hotplug-detect blocks. Each instance contains HPD interrupt and sense status, interrupt polarity/enable/ack, RX interrupt enable/ack, connection/RX timers, HPD enable, fast-train delays/enables, and connect/disconnect toggle filter delays.
- `DPIA_MUX0_*` through `DPIA_MUX5_*`: DPIA mux controls for HPD selection, AUX selection, link selection, USB4 DPALT disable, stream enable, and reserved-programming fields.
- `PHY_MUX0_*` through `PHY_MUX4_*`: PHY mux controls for PHY link selection, lane enables, lane-to-PHY mapping, and port type.
- `DCOH_TOP_*` and `DCOH_DCN_STATUS`: top-level DCOH clock, clock-on status, spare, and DCN status fields.
- `FMT0_*` and `FMT1_*`: formatter clamp components, dynamic expansion, pixel encoding, subsampling, dithering/truncation, dither seeds and offsets, clamp color format, side-by-side stereo active width, 4:2:0 memory power controls/status, and 4:2:2 edge pixel control.
- `DPG0_*` and partial `DPG1_*`: display pattern generator enable/mode/dynamic-range/bit-depth/resolution/field-polarity, ramp controls, active dimensions, colors, offset segment, and double-buffer status for instance 0; the chunk includes only DPG1 control, ramp control, and the beginning of dimensions.
- `OPPBUF0_*`, `OPP_PIPE0_OPP_PIPE_CONTROL`, and `OPP_PIPE_CRC0_*`: OPP buffer active width/segmentation/overlap/repetition/double-buffer and 3D dummy-data parameters, OPP pipe clock/digital-bypass control, and output-pipe CRC enable/mode/source/result fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display and DMUB code:

1. DCN 4.2.0 code includes `dcn_4_2_0_sh_mask.h` with the matching offset header.
2. Register tables and hardware-block constructors token-paste symbolic register and field names into mask/shift structures.
3. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, field-definition helpers, and related indexed/MMIO helpers to access hardware registers.
4. The numeric shift/mask values from this chunk determine which bits are touched when the driver handles color/histogram programming, perf counter setup, AUX transactions, HPD interrupts, USB4/DPIA/PHY mux routing, formatter output format, DPG test patterns, OPP buffering, OPP clocks, and pipe CRC capture.

The macros do not encode ordering constraints. Consumers must still follow hardware sequencing for AUX arbitration and transaction completion, HPD interrupt acknowledgement, mux ownership, formatter double-buffer updates, DPG programming, memory power transitions, CRC one-shot/continuous capture, and reads of status or sticky interrupt fields.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware-backed DCN state:

- Color-management state includes gamma-correction RAM-B region segmentation, HDR multiplier, histogram configuration/data/status, debug index/data, dealpha mode, coefficient format, and CM memory power state.
- AUX state includes active transactions, request/done bits, arbitration ownership between software and DMCU/firmware, low-speed data snapshots, RX/TX status, PHY wake handshakes, error flags, reply byte counts, and interrupt acknowledgement bits.
- HPD state includes live sense, delayed sense, RX interrupt status, connection timers, filtering timers, polarity, enable, and acknowledgement fields.
- Mux state binds DPIA, AUX, HPD, link, PHY, lane, port-type, and stream-enable resources to display pipelines and physical outputs.
- Formatter and OPP state includes clamp ranges, pixel encoding and chroma subsampling, dithering/truncation behavior, dither seeds, map420 memory power state, DPG test-pattern configuration, OPP buffer geometry, OPP pipe clock/bypass state, and pipe CRC results.

Persistence is hardware-defined. Configuration fields usually survive until modeset, link reconfiguration, output reprogramming, power gating, suspend/resume, GPU reset, or driver reinitialization. Status, pending, ready, interrupt, acknowledgement, error, double-buffer, and one-shot fields may be transient, sticky, self-clearing, write-one-to-clear, read-only, or valid only while relevant clocks and power domains are active. This generated header does not express those access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 4.2.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which provides matching register offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`, which includes the DCN 4.2.0 offset and shift/mask headers for DMUB register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c`, which includes these headers for DCN 4.2 interrupt service tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c`, which include these headers for DCN 4.2 GPIO/HPD/AUX translation.
- OPP and formatter code that uses shared `FMT*`, `DPG*`, `OPPBUF*`, `OPP_PIPE*`, and `OPP_PIPE_CRC*` field names through ASIC-specific register lists.
- Link, AUX, HPD, USB4/DPIA, PHY mux, diagnostics, CRC, color, histogram, and perf-monitor code paths that rely on consistent field layouts across repeated instances.

The repeated AUX0-4, HPD0-4, DPIA_MUX0-5, PHY_MUX0-4, FMT0-1, and DPG0-1 patterns are integration contracts. Generic instance-indexed driver code can only be correct if each instance keeps the expected register layout and if the matching offset header maps the same symbolic registers to the correct hardware block.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while reading or writing the wrong hardware bits.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the matching offset header, firmware expectations, and silicon documentation.
- The range is partial at both ends. Complete reasoning about `CM3_CM_GAMCOR_RAMB_REGION_2_3` should account for adjacent gamma-region definitions, and complete reasoning about `DPG1_DPG_DIMENSIONS` requires the following chunk for the active-width mask and later DPG1 fields.
- AUX status, interrupt, acknowledgement, arbitration, and data fields are sequencing-sensitive. Using the wrong mask can miss a HPD disconnect, miscount reply bytes, corrupt an AUX payload/index, or break software versus DMCU ownership handoff.
- HPD interrupt status/control fields have similar names across status, ack, polarity, enable, and RX interrupt paths. Confusing them can lose hotplug events, repeatedly signal stale interrupts, or invert expected polarity.
- Mux controls connect logical display resources to physical links, AUX channels, HPD pins, USB4/DPIA paths, and PHY lanes. Wrong fields can route a stream to the wrong connector or leave link training using the wrong AUX/HPD source.
- Formatter, DPG, and OPP fields are user-visible. Incorrect clamp, pixel-encoding, subsampling, dithering, test-pattern, buffer, or CRC masks can cause color shifts, bad 4:2:0/4:2:2 output, display artifacts, incorrect diagnostic CRCs, or blanking.
- Power/status fields for CM histogram memory and formatter 4:2:0 memory may be invalid during power gating or reset. Drivers need existing power-domain and double-buffer sequencing; the header alone cannot indicate safe access windows.
- Repeated instance layouts are copy-sensitive. Testing only AUX0/HPD0/FMT0/DPG0 may miss an instance-specific typo in AUX4, HPD4, FMT1, or DPG1.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.2.0 display behavior:

- Build AMDGPU display support with DCN 4.2.0 enabled. Missing or renamed macros should fail in DMUB, IRQ, GPIO, OPP, link, or resource register-table construction.
- Mechanically verify every field in this range has matching shift and mask definitions, while allowing boundary exceptions caused by the chunk split, including `DPG1_DPG_DIMENSIONS__DPG_ACTIVE_WIDTH_MASK` immediately after line 32771.
- Diff this slice against AMD's authoritative DCN 4.2.0 register database and the paired `dcn_4_2_0_offset.h`; repeated AUX/HPD/DPIA/PHY/FMT/DPG instances should have identical field layouts where the hardware schema expects them.
- Exercise DisplayPort AUX transactions on AUX0-4: DPCD reads/writes, I2C-over-AUX EDID reads, timeout/error handling, HPD disconnect during transaction, low-speed status updates, and firmware/software arbitration.
- Exercise HPD0-4 connect/disconnect and HPD RX IRQ paths, including debounce/toggle filtering, interrupt polarity, acknowledgement, fast-train delays, suspend/resume, and hotplug storms.
- Validate USB4/DPIA and PHY mux routing across all exposed ports, including link selection, AUX/HPD selection, stream enable, lane mapping, and port-type reporting.
- Run formatter and OPP output tests covering RGB/YCbCr pixel encoding, chroma subsampling, clamp ranges, truncation, spatial/temporal dithering, 4:2:0 memory power transitions, DPG patterns, OPP buffer segmentation, pipe clock gating, and pipe CRC one-shot/continuous reads.
- Use CM histogram/perfmon diagnostics to verify histogram ready/status/overflow behavior, memory power state reporting, perf counter event selection, counter high/low reads, interrupt enables, and counter restart/active states.
- Monitor kernel logs, display hotplug events, AUX transaction failures, link-training traces, CRC mismatches, color-format failures, blanking, and resume-only issues as high-signal indicators of bad mask/shift metadata.

## Cross-Chunk Notes

The previous chunk owns earlier CM3 gamma-correction RAM-B fields, including `CM3_CM_GAMCOR_RAMB_REGION_0_1`. This chunk owns the rest of CM3 gamma region pairs 2-33, CM histogram/perfmon, complete AUX0-4, HPD0-4, DPIA mux0-5, PHY mux0-4, DCOH top, complete FMT0, complete DPG0, OPPBUF0, OPP pipe0, OPP pipe CRC0, complete FMT1, and the opening DPG1 control/ramp/dimensions fields. The next chunk owns the remaining `DPG1_DPG_DIMENSIONS` mask and the rest of DPG1 and following generated register families. The final per-file research document should reconcile these adjacent chunks before making complete claims about all DCN 4.2.0 CM, OPP, AUX, HPD, mux, and DPG register coverage.

### subset-b-002231: lines 32772-35325

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 32772-35325

## Purpose

This chunk is a generated DCN 4.2 ASIC register field-definition section for AMD display hardware. It contains C preprocessor constants only: `__SHIFT` values and `_MASK` values for MMIO bitfields. The constants are consumed by the AMD Display Core register helper layer to compose, update, poll, and decode register fields without hard-coding bit positions in functional code.

The covered range spans output-pixel-processor and timing-generator register blocks. It starts in the middle of the `dce_dc_opp_dpg1_dispdec` definitions, continues through OPP/FMT/DPG instances 1-3, OPP top-level and DSC-remap forwarding fields, then covers ODM0-ODM3 input controls and OTG0/OTG1 timing-generator controls through `OTG1_OTG_STATIC_SCREEN_CONTROL`.

## Contents and Important Definitions

The chunk contains 2,120 `#define` entries grouped by commented register names and 25 address blocks:

- `dce_dc_opp_oppbuf1_dispdec`, `dce_dc_opp_opp_pipe1_dispdec`, `dce_dc_opp_opp_pipe_crc1_dispdec`: output buffer, OPP pipe clock/bypass, and pipe CRC controls for OPP instance 1.
- `dce_dc_opp_fmt2_dispdec`, `dce_dc_opp_dpg2_dispdec`, `dce_dc_opp_oppbuf2_dispdec`, `dce_dc_opp_opp_pipe2_dispdec`, `dce_dc_opp_opp_pipe_crc2_dispdec`: formatter, display pattern generator, output buffer, pipe control, and OPP CRC fields for OPP/FMT/DPG instance 2.
- `dce_dc_opp_fmt3_dispdec`, `dce_dc_opp_dpg3_dispdec`, `dce_dc_opp_oppbuf3_dispdec`, `dce_dc_opp_opp_pipe3_dispdec`, `dce_dc_opp_opp_pipe_crc3_dispdec`: equivalent field layout for instance 3.
- `dce_dc_opp_opp_top_dispdec`: top-level OPP clock and ABM control fields.
- `dce_dc_opp_dscrm0_dispdec` through `dce_dc_opp_dscrm3_dispdec`: DSC remap forwarding configuration, including `DSCRM_DSC_FORWARD_EN`, `DSCRM_DSC_OPP_PIPE_SOURCE`, and forward-enable status.
- `dce_dc_opp_opp_dcperfmon_dc_perfmon_dispdec`: DC perfmon counter control, value, high/low, state, and overflow-style control fields.
- `dce_dc_optc_odm0_dispdec` through `dce_dc_optc_odm3_dispdec`: ODM/OPTC input global control, underflow status/clear, segment source selection, data format, DSC byte count, width, clock, memory, and spare fields.
- `dce_dc_optc_otg0_dispdec` and `dce_dc_optc_otg1_dispdec`: OTG timing, trigger, stereo, status, interrupt, update-lock, CRC, static-screen, dynamic refresh-rate, global sync, p-state, encryption, and spare fields. The chunk ends at the static-screen control masks for OTG1.

Important repeated field families are:

- `FMTx_FMT_BIT_DEPTH_CONTROL`: truncation, spatial dither, temporal dither, RGB/frame/high-pass randomization, FRC selectors, and temporal reset/level fields.
- `FMTx_FMT_CONTROL`: pixel encoding, 4:2:0 or 4:2:2 subsampling control, stereo sync override, CbCr reduction bypass, and double-buffer pending status.
- `DPGx_DPG_*`: display-pattern-generator enable/mode, dynamic range, bit depth, dimensions, colors, segment offset, ramp increments, and double-buffer pending.
- `OPPBUFx_OPPBUF_*`: active width, display segmentation, overlap pixels, pixel repetition, 3D dummy data/vertical active spaces, padded segment pixels, and double-buffer pending.
- `OPP_PIPE_CRCx_*`: OPP pipe CRC enable, continuous/one-shot state, stereo/interlace modes, source/pixel select, mask, and result registers.
- `ODMx_OPTC_*`: ODM input segmentation and source selection, DSC formatting, segment widths, input clocks, underflow/RSMU underflow status and clear bits, and memory selection/status.
- `OTGx_OTG_*`: full timing generator control surface for horizontal/vertical totals, blank/sync windows, triggers, count/status snapshots, interrupts, double-buffering, CRC windows/results/readbacks, static-screen detection, GSL/global update lock, DRR, and p-state-related control.

## APIs, Types, and Integration Points

This header does not define functions or types. Its "API" is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The functional driver code maps these generated macros into typed shift/mask tables. In `drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`, DCN42 constructs static tables such as `opp_shift`, `opp_mask`, `dsc_shift`, `dsc_mask`, `optc_shift`, and `optc_mask` using list macros. The register addresses come from companion offset headers, while this file supplies the bit layout.

Key consumers include:

- OPP construction: `dcn42_opp_create()` initializes four OPP register tables and passes `opp_regs[inst]`, `opp_shift`, and `opp_mask` into `dcn20_opp_construct()`. The relevant list macros include `OPP_MASK_SH_LIST_DCN20(__SHIFT)` and `OPP_MASK_SH_LIST_DCN20(_MASK)`, which depend on this header's `FMT0/DPG0/OPPBUF0` field macros as canonical layout definitions. The chunk also supplies instance 1-3 equivalents for per-instance direct register tables.
- OPP programming: `dcn10_opp.c`, `dcn20_opp.c`, and related OPP code use `REG_UPDATE_*`, `REG_READ`, and state-dump paths for `FMT_BIT_DEPTH_CONTROL`, `FMT_CONTROL`, `OPPBUF_CONTROL`, `DPG_*`, and `OPP_PIPE_CRC_CONTROL`.
- DSC forwarding: `dcn401_dsc.h` and `dcn401_dsc.c` consume `DSCRM0_DSCRM_DSC_FORWARD_CONFIG` field shifts/masks for enable, OPP pipe source selection, and enable status. Functional paths use `REG_GET_2`, `REG_UPDATE_2`, `REG_UPDATE`, and `REG_WAIT` around `DSCRM_DSC_FORWARD_CONFIG`.
- OPTC/timing generation: `dcn42_optc.h` maps many `OTG0_*` and `ODM0_*` fields into `dcn_optc_shift` and `dcn_optc_mask`. Runtime code uses those tables for timing programming, static-screen events, CRC capture, underflow handling, ODM segmentation, global update locks, GSL synchronization, DRR, and p-state windows.
- DMUB, IRQ, GPIO, clock manager, and resource files include `dcn_4_2_0_sh_mask.h` alongside `dcn_4_2_0_offset.h` when they need DCN42 register-field access.

## Control Flow

There is no executable control flow in this chunk. Runtime flow is indirect:

1. DCN42 resource construction includes this header and builds static shift/mask tables from generated macros.
2. Hardware block constructors receive register-address tables plus these shift/mask tables.
3. Register helper macros such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_UPDATE_3`, `REG_SET_2`, `REG_GET`, `REG_GET_2`, `REG_READ`, and `REG_WAIT` use the per-block tables to modify or inspect the intended bitfields.
4. Hardware state changes occur through MMIO writes to the registers described here; readback/status fields report hardware state back to the driver.

Because field layout is selected at compile time, a bad shift or mask produces deterministic but hardware-specific misprogramming rather than a local C runtime failure.

## State and Persistence Behavior

The definitions are compile-time constants and have no in-memory state by themselves. They describe persistent hardware-visible state in DCN registers:

- Double-buffer pending bits appear in DPG, OPPBUF, FMT, ODM, OTG, and DRR-related controls and are used to determine when staged updates have latched.
- Status fields report clock-on, underflow, CRC pending/results, static-screen status, stereo eye/frame count, force-count events, interrupt status, and update-lock status.
- Control fields persist in hardware registers until changed by the driver, reset, or power-gated hardware state transitions.
- Readback fields for OTG CRC windows provide a hardware-latched view of programmed CRC window coordinates.

The generated constants also shape debug and state collection. For example, OPP and OPTC read-reg-state paths read raw registers whose bit meanings are defined here.

## Dependencies

This chunk depends on the broader AMD DC register-generation scheme:

- Companion register address definitions in `dcn_4_2_0_offset.h`.
- Register helper macros and block-specific structures in AMD Display Core, especially OPP, DSC, and OPTC headers.
- Consistent generated naming across instances. Many table macros use instance 0 field layouts as the canonical shift/mask source because corresponding instance registers are expected to share the same bit layout.
- Hardware documentation or generation inputs that guarantee the numeric shifts/masks match DCN 4.2 silicon.

## Risks and Maintenance Hazards

- Shift/mask drift is high impact. If a generated bit position differs from the actual DCN 4.2 register layout, the driver may write neighboring fields, leave requested fields unchanged, or misread status.
- Instance symmetry is assumed by consumer macros. The chunk shows instance-specific definitions for OPP/FMT/DPG/ODM/OTG blocks, while many consumer tables use instance 0 macros as the shared layout. Any future asymmetric instance layout would require consumer-list changes, not only generated definitions.
- Double-buffer and pending fields are timing-sensitive. Misdefined pending bits can cause waits to time out, updates to be applied too early, or state validation to report false readiness.
- CRC fields are used for display validation and debug. Incorrect CRC masks, window fields, or result fields can silently invalidate CRC-based diagnostics.
- Underflow clear/status fields are operationally important. Incorrect ODM/OPTC underflow masks can hide real display underflow or clear the wrong interrupt/status bit.
- This line range starts mid-register for `DPG1_DPG_DIMENSIONS`; the corresponding active-height shift/mask and active-width shift are immediately before the chunk. Merge-lane research should join this with the adjacent chunk to avoid treating `DPG1_DPG_DIMENSIONS` as incomplete at file level.

## Test and Validation Signals

Useful signals for changes touching this generated section include:

- Build coverage for DCN42 display code, because unresolved or renamed macros should fail at compile time in `dcn42_resource.c`, `dcn42_optc.h`, OPP headers, DSC headers, DMUB, IRQ, GPIO, and clock/resource paths.
- Display bring-up on DCN 4.2 hardware with multiple pipes, especially OPP instances 1-3 and ODM split/merge paths.
- Modeset and hotplug tests that exercise OTG timing programming, update locks, vertical interrupts, DRR, and p-state windows.
- CRC validation paths, including OTG CRC window programming/readback and OPP pipe CRC result reads.
- DSC enable/disable and DSC-forwarding tests that cover `DSCRM_DSC_FORWARD_CONFIG` enable, source selection, and status waits.
- Underflow injection or stress tests that verify ODM/OPTC underflow status, clear, and interrupt fields.
- Static-screen detection tests that verify `OTG_STATIC_SCREEN_CONTROL` event mask/frame count programming and status/interrupt behavior.

### subset-b-002232: lines 35326-37792

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 35326-37792

## Scope

This chunk is a generated AMD DCN 4.2.0 register shift/mask header slice. It covers lines 35326-37792 of `dcn_4_2_0_sh_mask.h`, beginning in the tail of `OTG1_OTG_STATIC_SCREEN_CONTROL`, defining the end of the `OTG1` timing-generator block, all visible `OTG2` and `OTG3` timing-generator field definitions, then entering shared OPTC miscellaneous, DC perfmon, and DC I2C/DDC field definitions. The slice contains 2,141 `#define` entries: 1,070 `__SHIFT` constants and 1,071 `_MASK` constants.

## Purpose

The file is not executable logic. It is the bitfield contract for MMIO registers used by the AMD display driver for DCN 4.2 hardware. Each macro maps a hardware register field to a shift offset and/or bit mask. Display code combines these values with register-offset macros from `dcn_4_2_0_offset.h` and helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `SRI`, and `SR` to write or read specific hardware fields without hard-coded numeric bit positions in the driver logic.

Within this slice, the main hardware areas are:

- `OTG1`, `OTG2`, and `OTG3` output timing generator fields for display timing, vblank/vupdate/vready events, master-update locking, global swap lock, dynamic refresh rate, CRC, stereo/3D, interlace, vertical interrupts, static screen detection, P-state keepout, and pipe-update status.
- `GSL_SOURCE_SELECT`, `OPTC_DLPC_CONTROL`, `OPTC_CLOCK_CONTROL`, and `ODM_MEM_PWR_*` fields for OPTC-level synchronization, clock gating, and ODM memory power behavior.
- `DC_PERFMON15_*` fields for one display performance monitor instance, including counter selection, run/interrupt state, counter values, and counter interrupt acknowledgement.
- `DC_I2C_*` fields for display I2C/DDC arbitration, software and hardware completion interrupts, status/error bits, DDC line status, DDC speed, and the beginning of DDC1 setup.

## Important Macros And Field Families

The chunk is organized by comment headers naming registers, followed by paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. There are no types or functions defined here.

Important OTG field families:

- `OTG*_OTG_H_TOTAL`, `OTG*_OTG_H_BLANK_START_END`, `OTG*_OTG_H_SYNC_A`, and `OTG*_OTG_H_SYNC_A_CNTL` describe horizontal totals, blanking, sync window, sync polarity, and horizontal timing divider mode.
- `OTG*_OTG_V_TOTAL`, `OTG*_OTG_V_TOTAL_MIN`, `OTG*_OTG_V_TOTAL_MAX`, `OTG*_OTG_V_TOTAL_MID`, and `OTG*_OTG_V_TOTAL_CONTROL` describe vertical totals and min/max/mid switching used for variable/dynamic refresh behavior.
- `OTG*_OTG_GLOBAL_SYNC_STATUS`, `OTG*_OTG_VSTARTUP_PARAM`, `OTG*_OTG_VUPDATE_PARAM`, and `OTG*_OTG_VREADY_PARAM` define timing event positions, event occurrence/status bits, clear bits, and interrupt enable/type fields.
- `OTG*_OTG_MASTER_UPDATE_LOCK`, `OTG*_OTG_GLOBAL_CONTROL0..4`, `OTG*_OTG_GSL_CONTROL`, `OTG*_OTG_GSL_WINDOW_X/Y`, and `OTG*_OTG_VUPDATE_KEEPOUT` define update-lock windows and global-swap-lock coordination.
- `OTG*_OTG_TRIGA_CNTL`, `OTG*_OTG_TRIGB_CNTL`, `OTG*_OTG_TRIGA_MANUAL_TRIG`, and `OTG*_OTG_TRIGB_MANUAL_TRIG` define trigger source selection, polarity, edge detection, frequency, delay, clear, and manual trigger bits.
- `OTG*_OTG_CONTROL`, `OTG*_OTG_CLOCK_CONTROL`, `OTG*_OTG_MASTER_EN`, and `OTG*_OTG_STATUS*` define enable state, clock/reset state, muxing, current counters, active/blanking state, and frame counts.
- `OTG*_OTG_INTERRUPT_CONTROL` and `OTG*_OTG_VERTICAL_INTERRUPT{0,1,2}_*` define CRTC/timing-generator interrupt sources, line positions, enable/status/clear/type fields.
- `OTG*_OTG_CRC_CNTL`, `OTG*_OTG_CRC*_DATA_*`, `OTG*_OTG_CRC*_WINDOW*_*`, and readback variants define output CRC selection, windows, readback coordinates, and CRC result fields used for display validation.
- `OTG*_OTG_DRR_*`, `OTG*_OTG_PSTATE_REGISTER`, `OTG*_OTG_PIPE_UPDATE_STATUS`, and `OTG*_OTG_PWA_FRAME_SYNC_CONTROL` define dynamic-refresh timing transitions, memory/P-state allow windows, pending update visibility, and PWA frame synchronization.

Important non-OTG families:

- `GSL_SOURCE_SELECT__GSL{0,1,2}_READY_SOURCE_SEL` selects ready sources for global swap lock.
- `OPTC_CLOCK_CONTROL__OPTC_FGCG_REP_DIS` controls an OPTC clock-gating behavior.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS` define memory power-mode controls, block masks, and status fields for ODM memory.
- `DC_PERFMON15_PERFCOUNTER_CNTL`, `DC_PERFMON15_PERFCOUNTER_CNTL2`, `DC_PERFMON15_PERFCOUNTER_STATE`, `DC_PERFMON15_PERFMON_CNTL`, `DC_PERFMON15_PERFMON_CNTL2`, `DC_PERFMON15_PERFMON_CVALUE_INT_MISC`, `DC_PERFMON15_PERFMON_CVALUE_LOW`, `DC_PERFMON15_PERFMON_HI`, and `DC_PERFMON15_PERFMON_LOW` define one display perfmon counter bank, including event selection, cvalue selection, increment/run modes, interrupt status/ack fields, high/low counter values, and read selector bits.
- `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, `DC_I2C_DDC{1..5}_HW_STATUS`, `DC_I2C_DDC1_SPEED`, and the start of `DC_I2C_DDC1_SETUP` define DDC/I2C bus ownership, soft reset/go/send-reset controls, transaction count and DDC select fields, completion interrupts, NACK/timeout/abort/status bits, hardware request/urgent/done bits, EDID detect status/state, prescale/timing, and DDC1 setup enable/drive/delay fields.

## Integration Points

This header is included by DCN 4.2 display code alongside `dcn_4_2_0_offset.h`, including:

- `display/dc/resource/dcn42/dcn42_resource.c`, where token-pasting macros such as `SR`, `SRI`, `SR_ARR`, and `SRI_ARR` build register-address tables from offset macros.
- `display/dc/optc/dcn42/dcn42_optc.h`, where `OPTC_COMMON_MASK_SH_LIST_DCN42(mask_sh)` maps timing-generator field names into `struct dcn_optc_shift` and `struct dcn_optc_mask` compatible data. Many fields in that list are defined in this chunk, including timing totals, update locks, GSL, CRC windows, vertical interrupts, DRR, P-state, and pipe-update fields.
- `display/dc/resource/dcn42/dcn42_resource.h`, where `TG_COMMON_REG_LIST_DCN42` creates per-instance OTG register arrays for `OTG0...OTG3` style register names. This chunk supplies the `OTG2` and `OTG3` field names for the same register families used by the timing generator.
- `display/dc/dce/dce_i2c_hw.h`, where `I2C_COMMON_MASK_SH_LIST_*` uses `I2C_SF(DC_I2C_DDC1_SETUP, ...)`, `I2C_SF(DC_I2C_CONTROL, ...)`, `I2C_SF(DC_I2C_ARBITRATION, ...)`, `I2C_SF(DC_I2C_DDC1_SPEED, ...)`, and `I2C_SF(DC_I2C_SW_STATUS, ...)`. The I2C definitions in this chunk populate `struct dce_i2c_shift` and `struct dce_i2c_mask`.
- `display/dc/gpio/dcn42/hw_translate_dcn42.c`, which includes this header for GPIO/DDC mask constants and register offset translation.
- `display/dc/irq/dcn42/irq_service_dcn42.c`, which includes this header for interrupt register field constants used by the DC IRQ service.

The chunk also depends on the naming conventions and register offsets generated in `dcn_4_2_0_offset.h`. A field macro here is only useful when its register has a matching `reg...` offset macro and when consumer field-list macros refer to the exact generated token.

## Control Flow And State Behavior

There is no direct control flow, memory allocation, locking, or persistence in this header. Runtime behavior comes from consumers:

1. DCN 4.2 resource initialization includes this header and `dcn_4_2_0_offset.h`.
2. Register-list macros build tables of MMIO offsets for timing generators, I2C engines, IRQ sources, clock/power blocks, and other DC components.
3. Mask/shift-list macros build field metadata tables, usually one table of shifts and one table of masks.
4. Register helpers use the offset, mask, and shift metadata to read/modify/write hardware registers during display bring-up, modeset, vblank/vupdate handling, CRC collection, I2C/DDC transactions, power management, and timing-generator synchronization.

The state controlled by these definitions is hardware state, not software-owned persistent state. Writes affect live display hardware registers; reads sample live hardware counters/status bits. Some fields are sticky status/interrupt bits with explicit clear/ack fields, such as vstartup/vupdate/vready event clears, vertical interrupt clears, perfmon interrupt ACK bits, and I2C done ACK bits. Some fields represent pending or busy state, such as `OTG_BUSY`, update-pending bits, I2C request/status bits, and perfmon active/status bits.

## Dependencies

Key dependencies are:

- The AMD DC register-generation naming scheme: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.
- `dcn_4_2_0_offset.h` for the corresponding register addresses and base-index values.
- DC register helper macros that expect a mask/shift pair to exist for each field named in local field-list macros.
- Hardware documentation/RTL for DCN 4.2 register bit positions. This header is effectively a generated view of that hardware contract.
- The Linux DRM AMD display stack, especially timing generator, resource, IRQ, GPIO/DDC, I2C, and hardware sequencer code.

## Risks And Fragile Areas

- Incorrect mask/shift values can silently program the wrong MMIO bits. That can affect display timing, vblank/vupdate interrupt delivery, update-lock behavior, CRC reporting, I2C/DDC bus access, power gating, or perfmon state.
- Token spelling is a hard ABI between this generated header and consumer macros. A renamed field that is not reflected in `OPTC_COMMON_MASK_SH_LIST_DCN42`, `I2C_COMMON_MASK_SH_LIST_*`, GPIO code, IRQ code, or resource register lists causes compile failures. A stale but still defined field can compile while targeting the wrong hardware semantics.
- The chunk begins and ends mid-register-family: it starts after the first `OTG1_OTG_STATIC_SCREEN_CONTROL` fields and ends before the remaining `DC_I2C_DDC1_SETUP` masks. Merge logic must preserve neighboring chunks to reconstruct the complete file-level research.
- Many OTG definitions are repeated per instance. Copy/generation errors that affect only `OTG2` or `OTG3` can produce instance-specific bugs, such as one display pipe failing while another works.
- Several status/clear/ack pairs are adjacent. A bit-position swap between status and clear/ack fields would be particularly risky because writes intended to acknowledge events could touch enable/type/status fields instead.
- I2C/DDC fields cover display detection and EDID reads. Bad masks around `DC_I2C_DDC_SELECT`, `DC_I2C_TRANSACTION_COUNT`, NACK/timeout bits, or DDC setup timing can break monitor detection or cause unreliable AUX/DDC fallback behavior.
- Power and clock fields such as `ODM_MEM_PWR_CTRL*`, `OPTC_CLOCK_CONTROL`, and `OTG_CLOCK_CONTROL` can create resume, blanking, or clock-gating failures if generated values do not match hardware.

## Test And Validation Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration checks:

- Build coverage for DCN 4.2 display code should catch missing or misspelled macro names referenced by `dcn42_resource.c`, `dcn42_resource.h`, `dcn42_optc.h`, `dce_i2c_hw.h`, IRQ service code, and GPIO/DDC translation code.
- Static consistency checks can verify that every `__SHIFT` in the chunk has a matching `_MASK` for the same `REGISTER__FIELD` and that masks are aligned with shifts.
- Register-generation diffs against AMD hardware register sources or adjacent ASIC versions can flag unexpected changes in repeated OTG2/OTG3 fields, especially where OTG instance fields should be identical.
- Runtime display tests should cover modeset, vblank/vupdate interrupts, vertical line interrupts, global update lock, GSL/multidisplay synchronization, VRR/DRR transitions, static screen signaling, P-state keepout behavior, and CRC collection.
- Connector tests should cover DDC/EDID detection over DDC1-DDC5, I2C timeout/NACK paths, software-vs-hardware I2C arbitration, and HPD/DDC interactions.
- Power-management tests should include suspend/resume and idle/display-off paths where `ODM_MEM_PWR_*`, I2C light sleep, OPTC clock gating, and OTG clock/reset status are exercised.

## Open Questions For Merge Lane

- Neighboring chunks should confirm the complete `OTG0` and `OTG1` definitions and the continuation of `DC_I2C_DDC1_SETUP` plus later DDC2-DDC6/VGA setup fields.
- The generated typo `OTG*_OTG_DRR_CONTOL2` appears in this chunk and likely matches the hardware-generated token. Consumers must use the exact spelling if they reference it.
- This chunk does not show final include guard closure or file-level generation metadata beyond the header start read separately; the merge lane should summarize those at whole-file scope.

### subset-b-002233: lines 37793-40200

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 37793-40200

## Purpose

This chunk is a generated DCN 4.2.0 shift/mask register contract for AMD display I/O. It contains 2,170 `#define` constants and no executable C. Each register field is represented as a `__SHIFT` macro and a `_MASK` macro; consumers combine these with register offsets from `dcn_4_2_0_offset.h` through AMDGPU display helper macros such as `SE_SF`, `LE_SF`, `HWS_SF`, `REG_UPDATE`, `REG_SET`, and field encode/decode helpers.

The line range spans the end of the DC I2C/DDC controller fields, the DIO miscellaneous block, DIG stream mapping, a DC perfmon instance, the first VPG/APG/DME blocks, the first DIG front-end/back-end/HDMI/TMDS block, and the first DP link block through the beginning of AUX-less ALPM control. It is therefore a hardware ABI description for connector sideband access, display stream encoding, audio packet generation, metadata sideband packets, DP main-link timing/training/MST, low-power modes, and packet double-buffering.

## Important APIs, Types, And Macros

This header does not define functions, structs, enums, or static data. The API is the preprocessor namespace used to populate per-IP register field tables.

- `DC_I2C_DDC2_SPEED` through `DC_I2C_DDC5_SETUP` describe hardware DDC timing and line-drive configuration: threshold, filter stall behavior, start/stop timing, prescale, data/clock drive enable, reset length, EDID detection, intra-byte delay, inter-transaction delay, and time limit. The chunk also carries the tail of `DC_I2C_DDC1_SETUP`.
- `DC_I2C_TRANSACTION0..3`, `DC_I2C_DATA`, `DC_I2C_EDID_DETECT_CTRL`, and `DC_I2C_READ_REQUEST_INTERRUPT` define the transaction descriptor, byte/index access, EDID-detect policy, and read-request IRQ/ack/mask fields for DDC1-DDC6 plus VGA DDC.
- `DIO_SCRATCH0..7`, `DIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS`, `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, `DIO_MEM_PWR_CTRL2`, `DIO_CLK_CNTL`, `DIO_POWER_MANAGEMENT_CNTL`, `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, `DIO_PSP_INTERRUPT_STATUS`, `DIO_PSP_INTERRUPT_CLEAR`, and `DIO_STATUS` expose DIO scratch storage, per-DIG ALPM wake status, I2C/DP memory light-sleep state and controls, display/reference/symbol/SOC clock gating, reset/busy signaling, HDMI RX-status timer fields, PSP interrupt state, and DIO enable status.
- `DIG0_STREAM_MAPPER_CONTROL` through `DIG4_STREAM_MAPPER_CONTROL` map DIG stream encoders to link targets. DCN42 stream encoder code consumes `DIG0_STREAM_MAPPER_CONTROL__DIG_STREAM_LINK_TARGET`.
- `DC_PERFMON16_*` defines a display perf counter instance: counter control/select/clear/status, increment/decrement/range events, perfmon enable/clear/overflow/status, current value interrupt behavior, and 64-bit counter high/low value registers.
- `VPG0_*` covers generic packet access/data, frame-update and immediate-update controls for generic stream packets 0-11, VPG status/conflict clear, VPG memory power fields, and ISRC packet data access. These fields back HDMI/DP generic packet and infoframe update paths.
- `APG0_*` describes audio packet generator control, debug packet sources, ACP and audio-info payload fields, IEC 60958 channel-status bits, audio CRC control/result, debug ramp generation, audio/HBR/FIFO status, debug audio DTO, APG memory power, and spare register access.
- `DME0_DME_CONTROL` and `DME0_DME_MEMORY_CONTROL` define display metadata engine routing and update handshakes: HUBP requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable, missed transmission status, and DME memory low-power control.
- `DIG0_*` front-end, back-end, HDMI, and TMDS fields cover source selection, stereo sync, FE/BE clocks and resets, FIFO calibration/error state, HDMI metadata packets, scrambling, clock-channel rate, Dolby Vision enable/missed status, pixel encoding/color format, deep color, HDMI audio/ACR/VBI/infoframe/generic packet controls, HDMI double-buffering, ACR values/status, audio muxing, BE source/HPD selection, TMDS control symbols, DC balancing, pattern generation, and DIG version.
- `DP0_*` fields cover DP link status, pixel format, MSA colorimetry/misc/timing/VBID, lane count, video stream enable/defer/status, steer FIFO, video M/N generation, link framing, HBR2/DPHY test/training patterns, FEC, PRBS, scrambler, CRC, transfer unit control, secondary-data packet control, audio timestamps/N/M values, MST/MSE rates and slot-allocation tables, MSO secondary packet enables, metadata transmission, double-buffer status, ALPM, GSP8-GSP11 controls, and generic stream packet enable double-buffer pending status.

## Control Flow

There is no runtime control flow in this file. The effective control flow is compile-time table construction followed by runtime register helper use:

1. DCN42 resource code includes this generated field header and the matching offset header.
2. Resource constructors populate register address tables and field shift/mask tables. In this tree, `dcn42_resource.c` uses `HWSEQ_DCN42_MASK_SH_LIST`, while `dcn42_dio_stream_encoder.h` and `dcn42_dio_link_encoder.h` use `SE_COMMON_MASK_SH_LIST_DCN42` and `LINK_ENCODER_MASK_SH_LIST_DCN42`.
3. Runtime DIO, stream encoder, link encoder, I2C, HW sequencer, audio, and DP helpers call generic macros such as `REG_UPDATE`, `REG_UPDATE_N`, `REG_SET`, `REG_GET`, and packet programming helpers.
4. Those helpers use the precomputed shift/mask values from this chunk to isolate fields inside MMIO register words.

The main programmed sequences represented by the fields are:

- DDC/I2C setup: enable the selected DDC engine, program bus timing/prescale/delays, describe up to four transaction segments, write/read byte data through indexed data fields, and service read-request interrupt/ack bits.
- DIO power/clock sequencing: force or release I2C/DP memory light sleep, query memory power state, gate or ungate DIO clocks, and control DIO reset/busy state.
- Stream/link binding: map each DIG stream to a link target, enable FE/BE clocks and resets, route source streams, select HPD/link backends, and enable the FE/BE datapath.
- HDMI/packet programming: enable HDMI attributes, program scrambling/deep color/clock-channel rate, schedule audio/ACR/VBI/infoframe/generic/metadata packets by line, and commit double-buffered packet updates.
- DP programming: set pixel format, MSA timing and colorimetry, M/N timing, main-link framing, DPHY training/FEC/scrambler/test/CRC controls, video stream enable/defer, secondary-data packet enables, MST slot allocation, MSO packet replication, and ALPM sleep/standby requests.

## State And Persistence

The header is stateless, but its fields describe persistent hardware state in powered DCN blocks.

- DDC/I2C state persists in controller configuration registers until changed, reset, or power-gated. It affects monitor EDID reads, AUX/DDC GPIO behavior, and read-request interrupt handling.
- DIO memory and clock bits control low-power entry for I2C, DP, VPG/APG/DME, and symbol-clock related logic. Incorrect values can leave blocks powered when they should sleep or sleeping when software expects them available.
- Stream encoder and link encoder state persists across active modes: FE/BE source routing, FIFO calibration, HDMI format attributes, TMDS control generation, DP MSA timing, secondary-data packets, MST slot allocation, and ALPM state are all mode-set or link-training sensitive.
- Packet and metadata registers often use double-buffer handshakes (`*_DB_PENDING`, `*_DB_TAKEN`, `*_DB_TAKEN_CLR`, `*_DB_DISABLE`, and update-lock fields). Software must respect pending/taken state so new packets land on the intended frame or vupdate.
- Status and clear fields are mixed with control fields. Examples include FIFO errors, HDMI audio/error interrupts, packet missed indicators, APG CRC done clear, DME missed transmission clear, DIO PSP interrupt clear, and DP GSP deadline-missed/pending/active flags.

There is no filesystem persistence. State is in MMIO-visible display hardware and is reset by GPU reset, display engine reset, suspend/resume power transitions, or explicit driver reprogramming.

## Dependencies And Integration Points

- `dcn_4_2_0_offset.h` provides the register address side for the field names in this chunk. The shift/mask macros are only useful when paired with the corresponding `reg*` offset and `_BASE_IDX`.
- `display/dc/resource/dcn42/dcn42_resource.c` populates DCN42 HW sequencer fields including `DIO_MEM_PWR_CTRL__I2C_LIGHT_SLEEP_FORCE`, connecting this chunk to display power sequencing and I2C light-sleep control.
- `display/dc/dio/dcn42/dcn42_dio_stream_encoder.h` consumes many fields from this range through `SE_COMMON_MASK_SH_LIST_DCN42`: DP pixel format, HDMI control/audio/ACR/generic packets, DP secondary packets, DP MSA timing, DME metadata, HDMI/DP metadata packets, DIG FE/FIFO/stream mapper, and audio mux fields.
- `display/dc/dio/dcn42/dcn42_dio_link_encoder.h` consumes link-side fields through `LINK_ENCODER_MASK_SH_LIST_DCN42`: DIG BE enable/source/HPD selection, DPHY training/test/FEC/PRBS/scrambler controls, link framing, DP lane configuration, MST slot allocation, AUX/HPD fields from adjacent chunks, and DIO clock gating fields from this chunk.
- Generic stream encoder implementations in `display/dc/dce/dce_stream_encoder.c` and DCN stream/link encoder code use the field tables to program HDMI generic packets, infoframes, audio/ACR, DP secondary packets, and metadata.
- Generic I2C hardware code in `display/dc/dce/dce_i2c_hw.c` uses the DIO memory power field to force/release I2C light sleep around hardware I2C operations; the rest of the DDC field family is the register contract for DDC setup and transaction programming.
- DP MST/MSO, HDR/Dolby Vision metadata, audio packet generation, DSC/PPS-related GSP11 usage, and ALPM are all represented here as field contracts but orchestrated by higher-level DC mode-set, link-training, audio, and power-management paths.

## Risks

- This is generated hardware ABI data. A wrong bit position or mask can silently corrupt unrelated fields in the same register even when the C code compiles and the register offset is correct.
- Repeated instances hide copy/paste drift. DDC2-DDC5, transaction0-3, DIG0-DIG4 stream mappers, GSP fields, MST slot fields, and generic packet fields are highly regular; one bad field affects only a particular connector, packet slot, stream, or MST source.
- Some field names differ across DCN generations. DCN42 stream/link headers deliberately choose DCN42 names such as `PIXEL_ENCODING_TYPE`, `UNCOMPRESSED_PIXEL_FORMAT`, and the DCN42 `DIO_CLK_CNTL` clock-gating fields. Reusing older DCN masks would misprogram the same logical feature.
- Packet double-buffer fields are timing-sensitive. Misplaced pending/taken/clear/disable masks can cause HDMI/DP infoframes, metadata, DSC PPS, or generic secondary packets to update late, update on the wrong frame, or miss their deadline.
- Link-training and PHY fields are high impact. Errors in DPHY training pattern, FEC, scrambler, PRBS, symbol, CRC, lane count, or link framing fields can cause blank displays, link training failures, intermittent CRC errors, or DP compliance failures.
- Power and clock fields can produce non-obvious failures. Bad `DIO_MEM_PWR_CTRL`, `DIO_MEM_PWR_CTRL2`, `DIO_CLK_CNTL`, VPG/APG/DME memory-power, or ALPM masks can surface as resume failures, I2C timeouts, audio loss, packet drops, or wakeup interrupt issues.
- Status/clear bit confusion can lose diagnostics. Interrupt ack/clear and missed/deadline/status bits share registers with enables in several blocks; a wrong clear mask may hide a real fault or clear a status before software observes it.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage with DCN 4.2 enabled. Macro renames or missing fields should fail in `dcn42_resource.c`, `dcn42_dio_stream_encoder.h`, `dcn42_dio_link_encoder.h`, and shared DCE/DCN encoder code.
- DDC/EDID tests on every connector: hardware I2C transaction success, EDID detect timing, DDC read-request interrupt ack/mask behavior, and suspend/resume recovery after I2C light sleep.
- DIO power and clock tests: runtime power management, display hotplug after idle, PSP/DIO interrupt status handling, ALPM wakeup status, and clock-gating toggles for DIG/HDCP/symbol-clock paths.
- HDMI validation: deep color, scrambling and clock-channel-rate modes, AVMUTE, audio packets, ACR CTS/N values for 32/44.1/48 kHz families, infoframes, generic packets 0-14, metadata packets, Dolby Vision enable/missed status, and double-buffer update behavior.
- DP SST validation: link training, lane-count programming, FEC, enhanced framing, video M/N timing, MSA timing/colorimetry, VBID behavior, DPHY scrambler/CRC/test pattern controls, video stream enable/defer, and stream disable interrupts.
- DP MST/MSO validation: MSE rate programming, slot allocation table programming/status for sources 0-5, SAT update handshakes, MSO secondary packet enable masks, and secondary packet replication across GSP slots.
- Audio and packet generator validation: APG enable/reset, HBR/audio status, FIFO overflow clear, IEC 60958 channel-status fields, audio CRC done/clear/result, VPG generic packet conflict status, ISRC access/data, and metadata engine double-buffer/missed-transmission handling.
- Low-power and ALPM tests: DP ML PHY sleep/standby requests and pending bits, AUX-less ALPM sleep repeat/delay/interval fields, force-scrambled-zero behavior, and link-training transitions around ALPM.

### subset-b-002234: lines 40201-42616

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 40201-42616

## Scope

This chunk is part of the generated AMD DCN 4.2.0 ASIC register shift/mask header. It contains preprocessor constants only: each hardware field is represented by a `...__SHIFT` bit offset and a matching `..._MASK` bit mask. There are no C functions, structs, branches, allocations, locks, direct MMIO accesses, or persistence mechanisms in this range.

The slice contains 2,165 `#define` entries across 224 register-comment blocks and 9 `addressBlock` markers. It starts inside the DP0 AUX-less ALPM register family at `DP0_DP_AUXLESS_ALPM_CNTL2__DP_ML_PHY_SLEEP_HOLD_TIME__SHIFT` and ends inside `DIG2_DIG_OUTPUT_CRC_CNTL` after the shift definitions, before the corresponding masks. Adjacent chunks are required to reconstruct the complete `DP0_DP_AUXLESS_ALPM_CNTL1/2` boundary context and the full `DIG2_DIG_OUTPUT_CRC_CNTL` register.

## Purpose

The purpose of this chunk is to publish exact bitfield metadata for DCN 4.2.0 display I/O blocks. Runtime display code uses these generated names with matching register-address headers and AMD display register-helper macros to read, update, poll, or write individual register fields without hard-coded bit arithmetic.

Major covered areas:

- Tail of DP0 DisplayPort controls: AUX-less ALPM sleep/wakeup/FEC timing, stream and link symbol counters, panel replay tunneling optimization, and DPHY fast-training controls/status.
- DIG1 VPG, APG, DME, and front/back-end digital encoder blocks: generic packet storage/update controls, ISRC packet access, audio packet generation/debug/CRC/status, metadata engine control, DIG FE/BE clocking, test patterns, FIFOs, HDMI packet controls, TMDS controls, and DIG version.
- DP1 DisplayPort transport block: link control, pixel format, MSA/timing fields, stream control, FIFO steering, DPHY training/test/CRC/scrambler/TU controls, secondary-data/audio/metadata packet controls, MST/MSE scheduling, ALPM, GSP double-buffer status, symbol counters, panel replay, and fast training.
- DIG2 VPG/APG/DME blocks: instance-2 copies of the generic video-packet generator, audio packet generator, and metadata engine bitfields.
- Opening DIG2 front-end fields: source selection, stereosync, digital bypass, FE clock/reset/gating status, FE enable, and the first output-CRC control shifts.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit position inside the register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used by register-helper update paths.
- Instance prefixes are semantically important. `DP0_`, `DIG1_`, `DP1_`, `VPG2_`, `APG2_`, `DME2_`, and `DIG2_` map these fields to specific display pipe, packet, audio, metadata, or link instances.

Important register families in this chunk include:

- `DP0_DP_AUXLESS_ALPM_CNTL2` through `CNTL5`: sleep hold time, wakeup send/immediate/pending, FEC enable immediate/pending, ML PHY lock period, wakeup/FEC line numbers, hardware-mode enable/status, current ALPM state, frame number, wakeup interrupt mask/occurred/status/clear, and interrupt frame/line capture.
- `DP0_DP_STREAM_SYMBOL_COUNT_*` and `DP0_DP_LINK_SYMBOL_COUNT_*`: stream BS count, link SR count, link cycle count, enable bits, and reset bits for symbol-count diagnostics.
- `DP0_DP_SYM8_ENC_VID_PANEL_REPLAY_CONTROL`: panel replay tunneling optimization enable, double-buffer enable, and double-buffer pending status.
- `DP0_DP_DPHY_FAST_TRAINING*`: RX fast-training capability, software start, VBlank edge detect, stream reset behavior, TP1/TP2 timing, fast-training state, completion occurrence, interrupt mask, and acknowledge fields.
- `VPG1_*` and `VPG2_*`: generic packet byte-indexed access, 15 generic packet frame-update and immediate-update bits, pending/status mirrors, memory power controls, and ISRC1/2 data access.
- `APG1_*` and `APG2_*`: audio enable/HBR/sample-rate/source selection, debug generator controls, packet send flags, ACP and audio-info packet fields, IEC 60958 channel-status fields, audio CRC control/result, debug ramp counters, status/overflow clear, DTO debug fields, memory power controls, and spare bits.
- `DME1_*` and `DME2_*`: metadata HUBP requestor selection, engine enable, stream type, double-buffer pending/taken/clear/disable, missed-transmission status/clear, and DME memory power controls.
- `DIG1_*`: front-end source/stereosync/bypass selection, FE clock/reset/gating, FE enable, output CRC control/result, clock/test/random pattern generation, FIFO reset/start/clock-source/pixel-per-cycle/status, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet controls, DB control, ACR values and readback status, FE audio control, BE clock/control/enable, TMDS control-character/sync/DC-balance/control-bit generation, and version fields.
- `DP1_*`: DP link control, pixel format/colorimetry/configuration, stream control, FIFO steering, MSA misc/timing/VBID, DPHY internal/training/symbol/8b10b/PRBS/scrambler/CRC controls, TU control, secondary data/audio/timestamp/packet controls, MSE SAT/rate/timing/status fields, MSO/steer FIFO controls, metadata transmission, ALPM, GSP enable double-buffer status, AUX-less ALPM, symbol counters, panel replay, and fast-training fields.
- `DIG2_DIG_FE_*` and partial `DIG2_DIG_OUTPUT_CRC_CNTL`: front-end source/stereosync/bypass selection, clock/reset/gated-clock state, FE enable, and output CRC enable/link/data selection shift definitions.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime behavior is indirect:

1. DCN 4.2.0 display code includes this generated shift/mask header with the matching register offset/address headers.
2. Register tables and helper macros pair a register address, such as a `mm` or `ix` offset from the companion headers, with the field shift/mask constants from this file.
3. The AMD display driver uses masked register get/set/update/wait helpers to isolate fields and program the display hardware.
4. Hardware state changes occur in the display, DP, HDMI/TMDS, audio, packet, metadata, and PHY-related registers; this file only supplies compile-time metadata for those operations.

The represented flow is typically: select and enable a DIG front end, configure DP or HDMI/TMDS output formatting and timing, program packet/audio/metadata generators, arm double-buffered updates, drive DP link training or fast training, optionally enable ALPM or panel replay behavior, and poll status/CRC/counter/pending fields for validation or completion.

## State and Persistence Behavior

The file itself has no mutable or persistent state. All state described by these macros resides in hardware registers.

The hardware state represented by this chunk includes:

- Link and stream state: DP link enable/control, training pattern and DPHY modes, TU settings, pixel format/colorimetry, MSA timing and VBID, MST/MSE slot/rate scheduling, MSO control, ALPM state, panel replay optimization, and fast-training state.
- Packet-generation state: VPG generic packet data, generic packet update/immediate-update/pending flags, HDMI generic/infoframe/audio/ACR/VBI packet controls, GSP enable double-buffer pending status, ISRC packet contents, and secondary-data packet controls.
- Audio and metadata state: APG audio enable/HBR/sample-rate/source/debug-generator fields, IEC 60958 channel status, audio CRC counters/results, audio FIFO overflow status, DME metadata engine enable, HUBP requestor, DB pending/taken state, and missed-transmission status.
- Digital encoder state: DIG FE/BE source selection, bypass paths, clock enables, resets, gated-clock status, FIFO enable/reset/read-start state, test/random/clock pattern controls, TMDS sync/control/DC-balance fields, and output CRC selection/result.
- Power-management state: VPG/APG/DME memory power disable/force/state/default low-power fields and DP AUX-less ALPM sleep/wakeup timing.

Persistence is limited to the lifetime of the hardware register programming. Values can be lost or require reprogramming after GPU reset, display engine reset, DIG/DP block reset, power gating, suspend/resume, hotplug retraining, mode set, or link reconfiguration. Higher-level display state in the driver remains the source of truth.

## Dependencies

This chunk depends on matching generated DCN 4.2.0 register-address headers. Shift and mask constants alone do not identify an MMIO or indirect register address.

It also depends on:

- AMD display register-helper infrastructure that consumes generated `__SHIFT` and `_MASK` names for masked reads, writes, updates, and polling.
- DCN 4.2.0 silicon register specifications or register database inputs used to generate this header.
- Display core, link encoder, DP, HDMI/TMDS, audio, metadata, and packet-generator code that programs these fields during mode set, link training, packet emission, audio bring-up, power management, and diagnostics.
- Generated register descriptor tables that preserve correct instance naming for DP0/DIG1/DP1/DIG2 and their VPG/APG/DME sub-blocks.

Because this is generated silicon metadata, manual changes are risky unless synchronized with the register database, companion offset headers, and any generated register tables.

## Integration Points

Primary integration points are the macro names used by AMD display code and register tables. A consumer naming a field such as `DP1_DP_DPHY_TRAINING_PATTERN_SEL__DPHY_TRAINING_PATTERN_SEL` or `DIG1_HDMI_GENERIC_PACKET_CONTROL0__HDMI_GENERIC0_SEND` relies on this header to supply the correct bit position and mask.

Integration surfaces include:

- DP link bring-up and training: `DP1_DP_LINK_CNTL`, `DP1_DP_CONFIG`, DPHY training/symbol/8b10b/PRBS/scrambler/CRC controls, TU control, MSA timing, VBID, and fast-training status.
- DP power and replay features: DP0 and DP1 AUX-less ALPM timing/status/interrupt fields, panel replay tunneling optimization, wakeup and FEC enable timing, and symbol counters.
- HDMI/TMDS output: DIG1 HDMI packet controls, ACR values/status, GC and infoframe controls, TMDS control characters, sync patterns, DC-balancer controls, and BE clock/control/enable bits.
- Packet and metadata generators: VPG generic packets, ISRC access, APG audio packets/status/CRC/debug fields, DME metadata engine state, and secondary-data packet controls.
- Diagnostics and validation: output CRC, DPHY CRC, stream/link symbol counters, audio CRC, random/test/clock patterns, FIFO reset/status fields, GSP pending status, metadata missed transmission flags, and APG overflow status.
- Multi-instance display mapping: the instance prefixes in this chunk must remain aligned with the matching address namespace so writes target DP0, DIG1, DP1, VPG2/APG2/DME2, or DIG2 as intended.

## Risks and Failure Modes

- Incorrect shifts or masks can corrupt adjacent fields in the same register, causing blank display, broken link training, invalid HDMI/DP packet emission, audio loss, metadata loss, CRC false positives, or unstable power transitions.
- Instance-prefix mistakes can compile cleanly while programming the wrong display pipe or packet/audio/metadata engine.
- Double-buffer and pending fields require correct semantics. Misprogramming generic packet, GSP, MSE SAT, or metadata DB fields can leave stale packets active or prevent updates from taking effect.
- ALPM, panel replay, and fast-training fields affect timing-sensitive DP behavior. Wrong masks can cause missed wakeups, FEC timing errors, failed fast training, or intermittent link recovery issues.
- HDMI/TMDS packet and ACR fields are format-sensitive. Bad bit definitions can break sink audio/video interpretation even when the link remains electrically active.
- Status/clear fields, such as audio FIFO overflow clear, metadata missed-transmission clear, fast-training acknowledge, CRC clear/done, and DB taken clear, must be updated with precise masks to avoid losing events or holding stale state.
- This chunk starts and ends inside larger register families. A final per-file report must reconcile the partial `DP0_DP_AUXLESS_ALPM_CNTL2` beginning context and the partial `DIG2_DIG_OUTPUT_CRC_CNTL` ending context with neighboring chunks.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DCN 4.2.0 display code builds without missing `DP0_`, `DIG1_`, `DP1_`, `VPG2_`, `APG2_`, `DME2_`, or `DIG2_` shift/mask symbols.
- Register-table sanity: generated register tables pair these field constants with the matching DCN 4.2.0 offsets and preserve correct instance ordering.
- DP smoke tests: DP mode set, hotplug, link retraining, suspend/resume, GPU reset, fast training, AUX-less ALPM entry/exit, panel replay paths, and lane-rate/lane-count variation.
- HDMI/TMDS smoke tests: HDMI mode set, audio enable, ACR programming/readback, infoframe/generic packet transmission, TMDS control character generation, and sink compatibility checks.
- Packet and metadata validation: VPG generic packets, ISRC data, APG audio packets, DME metadata transmission, DB pending/taken transitions, missed-transmission reporting, and GSP pending status.
- Diagnostics: output CRC and DPHY CRC results, stream/link symbol counters, audio CRC done/result, FIFO reset-done/read-start behavior, random/test pattern output, and APG/DME/VPG memory power state readback.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create the final per-file synthesis for `dcn_4_2_0_sh_mask.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.

### subset-b-002235: lines 42617-45015

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 42617-45015

## Purpose

This chunk is a generated AMD DCN 4.2.0 shift/mask register-field header slice. It contains no executable C logic; it exports preprocessor constants that encode field bit positions (`__SHIFT`) and masks (`_MASK`) for display-controller MMIO registers. Runtime AMDGPU display code pairs these constants with the matching DCN 4.2.0 offset header to build typed register tables for register helper calls.

The requested range contains 2,168 `#define` entries: 1,083 shift definitions and 1,085 mask definitions. The apparent imbalance is caused by field names that themselves end in `_MASK`, such as `HDMI_ERROR_MASK`, `DP_VID_STREAM_DISABLE_MASK`, `DP_STEER_OVERFLOW_MASK`, `DPHY_FAST_TRAINING_COMPLETE_MASK`, and `DP_ALPM_WAKEUP_INTERRUPT_MASK`; those fields generate macro names ending in `__SHIFT` and `_MASK_MASK`.

The range starts in the tail of `DIG2_DIG_OUTPUT_CRC_CNTL`, covers the rest of the DIG2 stream encoder and its DP2 DisplayPort register block, then covers VPG3, APG3, DME3, and most of the DIG3 HDMI/DIG front/back-end block through the first `DIG3_DIG_BE_EN_CNTL` shift. The boundaries are artificial chunk boundaries: the first register group begins in the previous chunk, and the final `DIG3_DIG_BE_EN_CNTL` mask continues in the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The public contract is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate or preserve the field during MMIO read-modify-write.

The major field families in this chunk are:

- `DIG2_*`: output CRC result/control tail, clock and test pattern generation, random-pattern seed, FIFO control/status/calibration, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic packet controls, double-buffer status, TMDS control-character/sync/DC-balancer fields, front-end audio selection, back-end clocking, back-end source/HPD selection, and DIG version.
- `DP2_*`: DisplayPort link control, pixel format, MSA colorimetry/misc/timing/VBID, video stream control, steer FIFO control/status, DPHY internal controls, link framing, HBR2/PRBS/scrambling/CRC/training-pattern fields, TU control, secondary-data packet controls, audio M/N readback/programming, MST/MSE slot-allocation tables and status, MSO controls, DP double buffering, metadata transmission, ALPM/AUX-less ALPM, generic stream packet controls, stream/link symbol counters, panel replay, and fast-training status.
- `VPG3_*`: video packet generator generic packet access/data, generic stream packet frame-update and immediate-update controls for packet slots 0 through 14, generic status, memory power, and ISRC1/2 access/data fields.
- `APG3_*`: audio packet generator reset/enable, DP audio stream ID and channel override, debug generator controls, debug ACP/audio-info/channel-status payload fields, audio CRC controls/result, ramp debug controls, enable/HBR/FIFO overflow/output-active status, audio DTO debug, memory power, and spare bits.
- `DME3_*`: DME control and memory-control fields, including enable/reset/reset-done, dynamic metadata packet timing, outstanding request counters, DL delta, memory power controls, and memory power state.
- `DIG3_*`: front-end selection/clock/enable, output CRC, clock/test/random patterns, FIFO controls, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic packet controls, double-buffer status, ACR programmed/readback values, front-end audio selection, and back-end clock/source/HPD selection. The chunk ends immediately after `DIG3_DIG_BE_EN_CNTL__DIG_BE_ENABLE__SHIFT`.

The repeated HDMI generic packet controls are dense. `HDMI_GENERIC_PACKET_CONTROL0` has send/continuous/line-reference/update-lock-disable fields for packet slots 0-7. `CONTROL6` adds the same controls for slots 8-14. `CONTROL5` exposes immediate-send and immediate-send-pending bits for slots 0-14. `CONTROL1-4` and `CONTROL7-10` hold packet-line fields, with `CONTROL10` also carrying enable double-buffer pending bits.

The DP2 secondary-data and MST families are also central. `DP_SEC_CNTL*` covers global secondary-packet enable, audio/video stream source, packet stream selection, SDP split, VSC/metadata/AS SDP controls, PPS/metadata/DSC/audio timestamp controls, DB pending/taken handshakes, and double-buffering. `DP_MSE_SAT*` and matching status registers describe MST slot allocation, stream source, slot count, and update state.

## Control Flow

This header has no runtime control flow. Its values are consumed through compile-time table construction:

1. DCN 4.2 code includes `dcn_4_2_0_offset.h` and this `dcn_4_2_0_sh_mask.h`.
2. Resource and block headers use token-pasting macros such as `SE_SF`, `VPG_SF`, `APG_SF`, `AUX_SF`, `LE_SF`, `SRI`, `SRI_ARR`, and `SR_ARR_INIT` to pair register offsets with these generated shift/mask constants.
3. DCN 4.2 constructors store those register, shift, and mask tables in stream encoder, VPG, APG, AUX, link encoder, HPD, audio, HPO stream/link encoder, DMUB, IRQ, GPIO, and clock-management objects.
4. Runtime helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use the numeric field metadata to access individual hardware bits.

Programming order is not encoded here. HDMI packet setup, DP link training, stream enable/disable, secondary-data packet scheduling, MST allocation, ALPM entry/exit, audio packet generation, DME operation, double-buffer latching, clock gating, and reset sequencing are controlled by driver code and hardware rules outside this generated header.

## State And Persistence Behavior

The file stores no software state and persists nothing itself. It names hardware-visible state fields:

- DIG2/DIG3 stream encoder state for front-end source selection, encoder enable, FIFO reset/calibration/error status, output CRC/test-pattern diagnostics, HDMI mode flags, TMDS pixel encoding/color format/deep-color state, Dolby Vision metadata state, AVMUTE/general-control state, audio clock regeneration values, packet lines, generic packet send modes, and HDMI double-buffer pending/taken bits.
- DP2 link and stream state for link enable/training, pixel format and MSA fields, video timing, VBID, stream disable/interrupt control, DPHY PRBS/scramble/CRC/error state, TU/steer FIFO, secondary-data packets, DP audio M/N, MST slot allocation, MSO, metadata, ALPM/AUX-less ALPM, generic stream packets, symbol counters, panel replay, and fast training.
- VPG3 state for generic packet memory access, frame-based and immediate packet update requests, update-pending readbacks, generic status, ISRC data, and VPG memory power.
- APG3 state for audio packet generation, debug packet sources, channel-status payloads, audio CRC capture, ramp debug controls, status/overflow clear bits, DTO debug, and APG memory power.
- DME3 state for dynamic metadata engine enable/reset/timing and memory power.

Persistence and side effects are hardware-defined. Configuration fields generally remain until modeset, link reset, stream disable, suspend/resume, power gating, GPU reset, or ASIC reset reprograms them. Status, interrupt, pending, taken, clear, and reset-done fields can be latched, write-one-to-clear, self-clearing, or valid only while the corresponding display block is powered and clocked. This header only provides bit geometry; access semantics come from the register specification and consuming driver code.

## Dependencies And Integration Points

This generated header must stay synchronized with AMD's DCN 4.2.0 register database and with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which supplies the companion register offsets and base indices.

Direct DCN 4.2 include users include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`, which builds resource-pool register tables. This chunk feeds `vpg_regs`, `apg_regs`, `stream_enc_regs`, `link_enc_aux_regs`, `link_enc_regs`, `hpo_dp_stream_enc_regs`, and related shift/mask tables through `DCN31_VPG_MASK_SH_LIST`, `DCN31_APG_MASK_SH_LIST`, `SE_COMMON_MASK_SH_LIST_DCN42`, `DCN_AUX_MASK_SH_LIST`, `LINK_ENCODER_MASK_SH_LIST_DCN42`, and `DCN4_2_HPO_DP_STREAM_ENC_MASK_SH_LIST`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h`, which defines DCN 4.2 register-list and mask-list shapes, including audio and stream/link encoder field lists.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_stream_encoder.h` and `.c`, which consume `DIGx`, HDMI, TMDS, VPG, and APG tables for DIO stream encoder construction and programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_link_encoder.h` and `.c`, which consume DIO link-encoder fields such as DIG back-end clock/source controls and DP DPHY controls.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_aux.h`, whose AUX field-list macros use `DP_AUXn_*` style shift/mask constants from this generated header. This exact chunk does not contain the `DP_AUX2_*` block but it does contain the DP2 stream/link-side fields that pair with AUX/DDC link management.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h`, which define VPG/APG field-list contracts consumed by `VPG3_*` and `APG3_*` definitions here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, which include the DCN 4.2 generated headers for register access across service, interrupt, GPIO, and clock-management paths.

Behaviorally, this chunk sits on the display-output path: stream encoder programming for HDMI/TMDS and DP, DP secondary-data packet delivery, MST/MSO allocation, low-power and fast-training link features, audio/video packet generation, dynamic metadata transport, and diagnostic CRC/test-pattern/status reporting.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing the wrong MMIO bit, corrupting an adjacent field, missing a status condition, or breaking only one encoder instance.
- The file is generated. Manual edits risk divergence from the authoritative register database, the matching offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. `DIG2_DIG_OUTPUT_CRC_CNTL` starts before this range, and `DIG3_DIG_BE_EN_CNTL` continues after it. Adjacent chunk reports must be reconciled before making whole-register or whole-file claims.
- `DIG2` and `DIG3` are structurally similar but not interchangeable. Copy-sensitive generator errors can affect only one DIO pipe, causing failures tied to a specific connector routing or encoder assignment.
- HDMI packet-control fields have multiple state models: one-shot send, continuous send, immediate send, line scheduling, update-lock disabling, double-buffer pending, and DB taken/clear. Wrong masks can produce missing HDR/AVI/audio infoframes, stale metadata, repeated packets, or update races around vblank.
- Audio clock regeneration fields (`HDMI_ACR_*` CTS/N, status readback, and packet controls) are interoperability-sensitive. Incorrect masks can cause HDMI audio drift, silence, receiver-specific sample-rate failures, or broken ACR auto-send behavior.
- TMDS and HDMI mode fields such as scrambling, clock-channel rate, deep color, pixel encoding, color format, control characters, sync characters, and DC balancing can produce link-only failures where DP paths still work.
- DP2 DPHY/link-training/status fields are sequencing-sensitive. Wrong training-pattern, scramble, PRBS, CRC, fast-training, link-framing, or stream-disable bits can manifest as failed link training, intermittent blanking, bad compliance-test output, or false error reporting.
- DP secondary-data and metadata controls are broad. Bad PPS, VSC, metadata, SDP split, audio timestamp, or double-buffer masks can break DSC metadata delivery, HDR metadata, Adaptive Sync/panel replay sideband data, or audio packet timing.
- MST/MSE slot allocation fields must be coherent across allocation registers, status registers, and update/timing controls. A field error can affect only MST topologies or only high-bandwidth multi-stream scenarios.
- ALPM and AUX-less ALPM fields are low-power handshake state. Incorrect masks can cause missed wake interrupts, stuck low-power entry/exit, resume-only blanking, or panel replay/ALPM interactions that are hard to reproduce.
- VPG/APG/DME memory-power fields interact with power gating and clock gating. Wrong force/state/default-low-power masks can create resume failures, diagnostics that read as idle when active, or packet generator stalls after power transitions.
- Fields ending in `_MASK` generate macro names such as `_MASK__SHIFT` and `_MASK_MASK`. Naive scripts that identify masks by suffix can miscount or mishandle these fields.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU display support with DCN 4.2 enabled. Missing or renamed macros should surface in `dcn42_resource.c`, DCN 4.2 DIO stream/link encoder code, VPG/APG headers, AUX helpers, DMUB setup, IRQ, GPIO, and clock-manager users.
- Mechanically compare lines 42617-45015 against the authoritative DCN 4.2.0 register-field database and ensure each register-field has the expected shift and mask, allowing for artificial chunk boundaries and `_MASK`-named fields.
- Cross-check this range against `dcn_4_2_0_offset.h` so every register family has matching offsets and base-index entries.
- Exercise all DIO stream encoders that can map to `DIG2` and `DIG3`: HDMI modes, DP modes, connector hotplug, encoder reassignment, suspend/resume, and rapid modeset sequences. Watch for pipe-specific failures.
- Validate HDMI/TMDS paths with deep color, scrambling, FRL/TMDS clock-rate changes where applicable, HDR/Dolby Vision metadata, generic infoframes, AVMUTE, and HDMI audio. Expected signals are stable link, correct metadata on a sink analyzer, no stuck HDMI DB pending/taken bits, and valid ACR CTS/N behavior.
- Exercise DP2 link paths across link training, retraining, fast training, PRBS/compliance patterns, CRC capture, stream disable/enable, pixel-format changes, MST, MSO, panel replay, ALPM/AUX-less ALPM, and suspend/resume. Watch for false DPHY errors, stuck update-pending bits, failed wake interrupts, or stream symbol counter anomalies.
- Validate DP secondary-data packet behavior with DSC PPS, VSC, HDR metadata, Adaptive Sync/panel replay sideband traffic, and audio timestamps. Register dumps should show coherent enable, line, DB pending/taken, and packet scheduling state.
- Exercise VPG3/APG3 packet generation through both DIO and HPO mappings in `dcn42_resource.c`. Expected signals are correct generic packet data writes, frame/immediate update completion, valid APG audio status, no APG FIFO overflow, and stable memory-power state after idle/resume.
- Exercise DME3 dynamic metadata paths if exposed by the platform, including metadata enable/disable and power-state transitions.
- Run repeated instance consistency checks across `DIG2`/`DIG3` and corresponding DP/VPG/APG/DME instances, while allowing intentional per-instance prefixes and known boundary splits.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DIG2_DIG_OUTPUT_CRC_CNTL`. This chunk starts with its mask definitions and then covers the rest of DIG2 and DP2 plus VPG3/APG3/DME3 and most of DIG3 HDMI/DIG metadata. The next chunk should continue `DIG3_DIG_BE_EN_CNTL` with its mask and then cover the remaining DIG3, DP3, and subsequent DCN 4.2.0 register families. The final per-file document should merge these boundaries before describing all DCN 4.2.0 stream encoder, DP, VPG, APG, or DME metadata.

### subset-b-002236: lines 45016-47434

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 45016-47434

## Purpose

This chunk is a generated AMD DCN 4.2.0 shift/mask header slice for display hardware register fields. It contains no executable C code; its public surface is a set of `#define` constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for fields in DCN display-controller registers.

The requested range contains 2,166 generated definitions over 2,419 source lines. It starts in the tail of the `DIG3_DIG_BE_EN_CNTL` group, covers the `DIG3` TMDS and version fields, covers the complete `DP3` DisplayPort stream/link encoder register field block, then covers `VPG4`, `APG4`, `DME4`, and most of the `DIG4`/HDMI/TMDS stream-encoder surface. It then starts the `DP4` DisplayPort block and stops inside `DP4_DP_MSO_CNTL1`, before that register's remaining shifts/masks and later `DP4` registers. The boundaries are artificial chunk boundaries rather than semantic register-block boundaries.

Although the file is under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocations, or direct MMIO operations in this range. The API contract is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for `FIELD`.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for `FIELD`.

The main register-field families in this chunk are:

- `DIG3` tail: `DIG_BE_ENABLE`, TMDS sync/control-character generation, TMDS feedback, stereo sync selection, sync-character patterns, control bits, DC balancer controls, per-control-lane generation controls, and `DIG_TYPE`.
- `DP3`: DisplayPort link status/training, pixel format, MSA colorimetry/misc/timing, lane configuration, stream enable/status, steer FIFO status and overflow interrupt bits, video M/N timing, link framing, DPHY training/symbol/scrambler/PRBS/CRC controls, transfer-unit control, secondary-data packet controls, audio M/N/timestamp registers, MST/MSE rate and slot-allocation table fields, HBlank/MSA timing, MSO secondary packet enables, steer FIFO control, generic secondary packet controls 8 through 11, double-buffer control/status, ALPM and AUX-less ALPM fields, stream/link symbol counters, panel replay controls, and fast-training status.
- `VPG4`: generic packet data access, generic packet payload bytes, frame-update/immediate-update enables for generic secondary packets, conflict status/clear, memory-power controls, and ISRC1/2 packet data access.
- `APG4`: audio packet generator debug channel enable fields and APG memory-power controls.
- `DME4`: dynamic metadata engine enable/reset/ready/configuration fields plus memory-power controls.
- `DIG4`: front-end and back-end control, source selection, stereo sync, clock controls, enable/reset, output CRC, test and random patterns, FIFO controls, HDMI metadata and generic packet controls, HDMI core/deep-color/scrambler/status/audio/ACR/VBI/infoframe/general-control fields, HDMI double-buffer controls, audio front-end control, TMDS controls, and `DIG_TYPE`.
- `DP4` beginning: the same DisplayPort stream/link/DPHY/MSA/MSE/MSO field families as `DP3`, but only through the early `DP4_DP_MSO_CNTL1` shifts in this chunk.

Several fields in this range are consumed through generic instance-0 shift/mask tables even though the chunk itself is for instances 3 and 4. The codebase commonly uses macros such as `SE_SF(DP0_DP_PIXEL_FORMAT, PIXEL_ENCODING_TYPE, mask_sh)` to define a generic field table, while register address tables select the concrete instance (`DP3`, `DP4`, `DIG4`, and so on).

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 4.2.0 code includes `dcn_4_2_0_offset.h` and this matching `dcn_4_2_0_sh_mask.h`.
2. Resource macros in `dcn42_resource.c` and `dcn42_resource.h` use token-pasting helpers such as `SRI_ARR`, `SR_ARR`, `SE_SF`, and `LE_SF` to bind generated register addresses, shifts, and masks into typed register tables.
3. Runtime display objects receive those tables during resource-pool construction for stream encoders, link encoders, VPG/APG blocks, AUX/HPD blocks, and HPO-related paths.
4. Common AMD display register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use the tables to access MMIO bitfields.

The macros in this chunk do not prescribe programming order. DisplayPort link training, stream enable/disable, secondary-packet programming, HDMI packet programming, TMDS setup, DME/VPG/APG packet updates, MST slot-allocation updates, ALPM entry/exit, panel replay, CRC capture, and memory-power sequencing are implemented by driver code and hardware rules outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields:

- DisplayPort stream state: link-training completion/status, lane count, pixel encoding, component depth, compressed format, stream enable/status, video timing M/N generation, MSA misc/timing values, VBID controls, and HBlank minimum symbol width.
- DisplayPort physical/link state: DPHY bypass, 8b/10b, training-pattern selection, lane symbols, PRBS, scrambler advance/count, CRC control/results/status, HBR2 pattern control, BS/SR swap load/done, fast-training capability/status, and FEC-related fields from the common link-encoder consumers.
- Secondary packet and metadata state: DP generic secondary packet enables/line numbers/priorities, audio timestamp and M/N fields, HDMI generic packet sends/lines, HDMI infoframe/VBI/audio/ACR controls, VPG packet data/update controls, APG audio-stream/debug fields, and DME dynamic-metadata control.
- MST/MSO state: MSE rate update, SAT source/encryption/slot-count entries and status readback, SAT update and keepout bits, MSE link timing/misc controls, and MSO packet enable masks.
- Power and debug state: VPG/APG/DME memory-power controls, HDMI and DIG double-buffer controls, output CRC, FIFO controls, test-pattern generators, and symbol/link counters.

Persistence and side effects are hardware-defined. Configuration fields usually remain until a modeset, stream disable, link reset, power-gating transition, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, counter, update-pending, reset-done, and CRC fields can be latched, write-one-to-clear, self-clearing, read-only, or valid only while the relevant block is powered and clocked. This file only provides bit positions and masks; it does not encode those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DCN 4.2.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` supplies the matching register offsets and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` includes this header and initializes DCN 4.2.0 stream encoder, VPG, APG, AUX, HPD, and link encoder register/shift/mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h` defines `SE_DCN42_REG_LIST_RI(id)` and `VPG_DCN42_REG_LIST_RI(id)`, which require the `DIG`, `DP`, `DME`, and `VPG` register names represented in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_stream_encoder.h` defines `SE_COMMON_MASK_SH_LIST_DCN42`, which consumes the generic stream-encoder field names for DP pixel format, stream control, secondary packets, MSA timing, HDMI packet controls, DME, and DIG controls.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_link_encoder.h` defines `LINK_ENCODER_MASK_SH_LIST_DCN42`, which consumes DIG back-end, TMDS, DP DPHY/link/framing/MSE, AUX, HPD, and DIO clock-gating field names. The concrete `DIG3`/`DP3` and `DIG4`/`DP4` instances in this chunk are part of the repeated generated set behind those tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h` provide the VPG/APG field-list macros that map onto the generated `VPG4` and `APG4` field layout.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h` provides shared `DCN2_AUX_REG_LIST_RI(id)` and `HPD_REG_LIST_RI(id)` macros used by DCN 4.2.0 for AUX and HPD register-address tables adjacent to this stream/link encoder metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c` includes the same generated header for DCN 4.2.0 interrupt-source register setup, especially HPD-related plumbing outside this exact slice.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`, `dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, and `dc/gpio/dcn42/*` also include the generated offset and shift/mask headers for DCN 4.2.0 block control.

Behaviorally, this chunk supports the DIO stream and link paths for later digital engines: DP/HDMI stream encoding, TMDS output setup, DisplayPort physical/link training, MST/MSO scheduling, generic secondary packet generation, HDMI audio/infoframe/ACR packet generation, VPG/APG/DME metadata/audio blocks, and low-power/panel-replay features.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting only one bitfield at runtime.
- The file is generated. Manual edits risk divergence from the authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are not semantic. The first line is only the mask half of `DIG3_DIG_BE_EN_CNTL__DIG_BE_ENABLE`, and the final line stops inside `DP4_DP_MSO_CNTL1` before the remaining shifts/masks. Adjacent chunk reports must be merged before making whole-register or whole-instance claims for those two boundary groups.
- Repeated instances are copy-sensitive. `DP3` and `DP4`, plus `DIG3` and `DIG4`, are structurally similar but used for different physical/logical display engines. A generator or table-index error can break only one connector path or only modes routed through one encoder instance.
- HDMI and DP packet controls are dense. Bad masks for generic packet send/line/continue bits, infoframe controls, VSC/HDR/adaptive-sync metadata, or DSC PPS secondary-packet fields can cause missing metadata, sink misconfiguration, HDR/VRR failures, or visible mode issues without obvious compile-time failures.
- MST/MSO and MSE slot-allocation fields must be coherent. Wrong source, slot-count, update, keepout, or status masks can produce bandwidth allocation errors, failed MST displays, or transient corruption during payload-table updates.
- DisplayPort link-training and DPHY fields are sequencing-sensitive. Incorrect masks for training pattern, scrambler, PRBS, CRC, BS/SR swap, fast training, FEC, lane count, or stream-enable/status fields can cause blank displays, link instability, or failures limited to certain link rates or lane counts.
- MSA timing fields directly encode sink-visible timing. Bad masks for totals, starts, sync widths, polarities, width/height, M/N generation, or VBID controls can cause invalid modes even when the higher-level timing calculation is correct.
- HDMI deep color, scrambling, clock-channel-rate, TMDS control, and audio/ACR fields interact with sink capabilities and pixel clock. Incorrect masks can cause HDMI 2.0 high-clock failures, audio dropouts, or incompatibility only on particular monitors.
- VPG/APG/DME memory-power controls can interact with packet update paths. If memory light-sleep or force bits are wrong, metadata/audio packet generation can fail after idle, suspend/resume, or display power-gating transitions.
- Status and counter fields may be read-only, latched, or clear-on-write according to hardware. Treating generated masks as access-policy documentation can lead to stuck status bits or missed diagnostics.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display behavior:

- Build DCN 4.2.0 AMDGPU display support. Missing or renamed macros should surface in `dcn42_resource.c`, `dcn42_resource.h`, `dcn42_dio_stream_encoder.h`, `dcn42_dio_link_encoder.h`, `dcn31_vpg.h`, `dcn31_apg.h`, and `irq_service_dcn42.c`.
- Mechanically compare this range against the authoritative DCN 4.2.0 register-field database and ensure every complete field in the slice has the expected `__SHIFT` and `_MASK` values.
- Cross-check this shift/mask range against `dcn_4_2_0_offset.h` so every completed register group has a corresponding register offset and base-index entry.
- Run static repeated-instance checks across `DP3` and `DP4`, and across `DIG3` and `DIG4`, while allowing the artificial start/end truncation at `DIG3_DIG_BE_EN_CNTL` and `DP4_DP_MSO_CNTL1`.
- Exercise DisplayPort SST on connectors routed through the later DIG/DP instances: link training at multiple rates/lane counts, stream enable/disable, modeset transitions, CRC capture where available, and suspend/resume. Expected signals are stable link training, correct stream status, no stuck FIFO reset/overflow state, and sane MSA timing register dumps.
- Exercise DisplayPort MST/MSO payload allocation and reallocation on `DP3`/`DP4` paths. Expected signals are correct SAT slot counts/status readback, no stuck MSE rate/SAT update state, and stable multi-monitor hotplug/modeset behavior.
- Exercise HDMI/DVI/TMDS modes through the affected DIG instances, including deep color, high pixel clocks requiring scrambling, audio, ACR values, generic packets, and infoframes. Expected signals are working video, correct sink-reported metadata, stable audio, and no HDMI status errors.
- Exercise VPG/APG/DME users: HDR/static metadata, adaptive sync or other generic packets, HDMI/DP audio packet generation, and dynamic metadata paths. Include idle and power-gated transitions to catch memory-power field mistakes.
- Validate low-power and replay features represented here: ALPM, AUX-less ALPM, symbol counters, and panel replay controls/status. Expected signals are correct entry/exit behavior and no stream loss after replay or ALPM transitions.
- Use register dumps around the chunk boundaries to verify `DIG3_DIG_BE_EN_CNTL` and `DP4_DP_MSO_CNTL1` only after the adjacent chunks are reconciled, because this chunk alone does not include those complete register-field groups.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DIG3_DIG_BE_EN_CNTL` and earlier `DIG3` back-end fields. This chunk starts with only the `DIG_BE_ENABLE_MASK` line. The next chunk continues `DP4_DP_MSO_CNTL1`, then covers the remaining `DP4` registers. The final per-file research document should reconcile these boundaries before describing all DCN 4.2.0 DIO stream/link encoder metadata or all instance-4 DP behavior.

### subset-b-002237: lines 47435-49893

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 47435-49893

## Purpose

This chunk is generated AMD DCN 4.2.0 register-field metadata. It contains no executable C logic; its contract is a large set of C preprocessor constants that map hardware register fields to bit shifts and masks. AMDGPU display code combines these `_SHIFT` and `_MASK` macros with the matching register offsets in `dcn_4_2_0_offset.h` to program DisplayPort stream encoder state, Display Stream Compression (DSC) engines, DSC client-interface blocks, DSC compressor cores, and DC performance counters.

The range contains 2,139 `#define` entries across 275 register names: 1,067 `__SHIFT` definitions and 1,072 `_MASK` definitions. The first line is a chunk-boundary artifact inside `DP4_DP_MSO_CNTL1`: earlier fields for the same register are just above this range. The final line range ends inside the fourth DSC compressor instance, after `DSCC3_DSCC_PPS_CONFIG9`; the next chunk continues with `DSCC3_DSCC_PPS_CONFIG10` and later fields. Although this repository subtree is named `distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata, not Ceph or filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, heap allocations, includes, or direct MMIO accesses in this range. The public interface is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field in a register value.

The chunk's main register groups are:

- `DP4_DP_*`: tail-end DisplayPort stream encoder 4 fields. These include multi-stream operation and secondary-data enablement, steering FIFO control, generic secondary packet send/pending/deadline/line-number controls for GSP1-GSP7 and GSP11/PPS, double-buffer state, MSA/VBID override fields, secondary metadata transmission state, ALPM/AUX-less ALPM timing, stream/link symbol counters, panel replay/SYM8 encoder control, and DPHY fast-training status.
- `DSC_TOP0` through `DSC_TOP3`: top-level DSC instance control and debug fields. These cover `DSC_CLOCK_EN`, display and DSC clock root-gate disables, fine-grain clock-gating repeat disable, dynamic DSC clock gating, debug enable, debug clock mux selection, spare debug, and top test-debug index/data registers.
- `DSCCIF0` through `DSCCIF3`: DSC client-interface configuration fields for input pixel format, bits per component, and double-buffer update-pending state.
- `DSCC0` through `DSCC3`: DSC compressor core fields. For instances 0-2, this chunk covers configuration, status, interrupt controls/status, PPS registers 0-22, memory power controls, squared-error counters, maximum absolute error, output/rate-buffer fullness, and test/debug buses. For instance 3, this chunk starts the same sequence but only reaches PPS config 9.
- `DC_PERFMON17` through `DC_PERFMON19`: performance-counter and performance-monitor control/state/value registers attached to DSC instances 0-2 in the address blocks. Fields include enable/reset/start/stop/clear/status controls, counter mode/selection, C-value interrupt/status/clear bits, and low/high counter value fields.

Representative field families include DSC PPS parameters (`DSC_VERSION`, `PPS_IDENTIFIER`, `BITS_PER_PIXEL`, `PIC_WIDTH`, `PIC_HEIGHT`, `SLICE_WIDTH`, `SLICE_HEIGHT`, delay/scale/BPG offsets, RC model size, RC buffer thresholds, and range QP/BPG table entries), compressor status and interrupt bits (`RATE_CONTROL_BUFFER_MODEL_OVERFLOW`, output overflow/underflow, end-of-frame-not-reached, and matching clear bits), memory low-power state controls, quality/error observation counters, and debug bus selection/index/data fields.

## Control Flow

This header has no runtime control flow. Its effect is compile-time token expansion:

1. DCN 4.2 display code includes generated offset and shift/mask headers for the target ASIC.
2. Register-table macros such as stream-encoder field macros and DSC field macros token-paste register and field names into generated register descriptors.
3. Runtime driver code uses those descriptors with `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or equivalent helpers to read or write MMIO fields.
4. Hardware state machines perform the real sequencing for secondary-data packet send, ALPM/panel replay, symbol counting, fast training, DSC clocking, DSC PPS programming, buffer/RC monitoring, memory power state, and debug/perf-counter capture.

The DP4 prefix binds this slice to the fifth DisplayPort stream encoder instance. The DSC and DSCC prefixes are instance-specific. Most DSC driver field tables are written against instance 0 names and then remapped by register lists; generated metadata for instances 1-3 must remain layout-compatible where the hardware instances are mirrored.

## State And Persistence Behavior

The chunk stores no software state and persists nothing directly. It defines encodings for hardware-visible state:

- DP secondary-data state: GSP enablement, send request bits, send-pending and deadline-missed status, line-number scheduling, "send any line" control, PPS routing via GSP11, double-buffer pending/taken flags, and active/idle send observation.
- DP low-power/replay state: ALPM enable/configuration, AUX-less ALPM PHY timing and debounce parameters, panel replay/SYM8 controls, symbol count start/clear/status fields, and link/stream symbol counters.
- DP link-training state: fast-training capability/configuration and status bits.
- DSC compressor state: top-level clock enable/gating bits, input format, bits per component, slices per line/vertical direction, ICH settings, rate-control buffer model size, PPS payload fields, double-buffer update-pending status, memory power state, and debug/test mux selection.
- DSC fault and observation state: interrupt enable/status/clear fields for rate-control model overflow, output-buffer overflow/underflow, and end-of-frame-not-reached; squared-error and maximum-absolute-error counters; output/rate-buffer fullness high-water marks; and performance-counter values.

Persistence is hardware-defined. Configuration fields generally survive until reprogrammed, reset, power-gated, or overwritten by a mode-set/link-training/compression programming path. Status, pending, taken, clear, counter, and debug-data fields may be read-only, sticky, write-one-to-clear, self-clearing, valid only while clocks are enabled, or valid only after a capture/control bit is asserted. The generated mask header does not encode access direction, reset value, timing, volatility, or side effects.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus AMD's generated register-header convention. The matching DCN 4.2.0 offset header provides register addresses and base indices, for example `regDP4_DP_SEC_CNTL2`, `regDP4_DP_AUXLESS_ALPM_CNTL1`, `regDSC_TOP0_DSC_TOP_CONTROL`, `regDSCC0_DSCC_PPS_CONFIG0`, `regDC_PERFMON17_PERFCOUNTER_CNTL`, and `regDSCC3_DSCC_PPS_CONFIG6` in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`.

Important consumers and integration points include:

- DisplayPort stream encoder code and field tables in `drivers/gpu/drm/amd/display/dc/dio/*`, including GSP/secondary-data controls for VSC, SPD, HDR metadata, adaptive sync, PPS, and immediate or line-scheduled packet sending.
- Link encoder and link training paths that use `DP_DPHY_FAST_TRAINING` and related fields for fast-training capability and behavior.
- Panel replay and ALPM paths in the display link code and DMUB-facing paths, with this chunk providing the DP4 hardware control fields that back those features.
- DSC code in `drivers/gpu/drm/amd/display/dc/dsc/dcn401/dcn401_dsc.h`, where `DSC_REG_LIST_SH_MASK_DCN401(mask_sh)` maps `DSC_TOP0`, `DSCC0`, and `DSCCIF0` field names into the driver's DSC register/shift/mask tables.
- DRM DSC parameter handling via `drm/display/drm_dsc.h` and AMD DSC types, which provide the software PPS/compression model that must be encoded into these hardware PPS registers.
- DC perfmon/debug infrastructure that reads the `DC_PERFMON17`-`DC_PERFMON19` counters and DSC debug buses for diagnostics and performance analysis.

Because this is generated silicon ABI metadata, edits must be synchronized with the authoritative AMD register database and with paired offset/base-index headers. A manual change can compile cleanly while making the driver program the wrong hardware bits.

## Risks And Edge Cases

- The macros are untyped. Incorrect shifts or masks compile but can corrupt adjacent hardware fields, especially in dense PPS, interrupt status, and packed QP/range table registers.
- The line range is not semantically aligned. `DP4_DP_MSO_CNTL1` begins before this chunk, and `DSCC3` continues after it; whole-register and whole-instance conclusions require adjacent chunks.
- Status and clear fields share similar names. Confusing `*_OCCURRED*`, `*_CLEAR*`, and `*_INT_EN*` fields can leave interrupts latched, mask real DSC faults, or clear diagnostics before software observes them.
- DSC PPS fields directly affect compressed stream generation. Wrong bit positions can cause blank displays, corrupted frames, downstream DSC decoder failures, link bandwidth miscalculation, or intermittent errors only on modes that require DSC.
- Instance symmetry matters. `DSCC0`, `DSCC1`, `DSCC2`, and `DSCC3` are expected to mirror many layouts, but this chunk only partially includes `DSCC3`; copy/paste or generated-name drift can break only one compressor instance.
- DP4-specific fields only affect one stream encoder. Bugs may appear only on a connector or pipeline assignment that maps to DP4, making regressions topology-dependent.
- ALPM, AUX-less ALPM, panel replay, and symbol counters are timing-sensitive. Misprogramming debounce, wake, counter start/clear, or training fields can create resume, replay, or low-power entry/exit failures that basic mode-set tests may miss.
- Debug and perfmon registers can have capture windows or clear-on-write behavior. Generic read/modify/write helpers must preserve unrelated fields and avoid clearing counters unintentionally.
- Reserved or spare debug fields expose full-width masks such as `0xFFFFFFFFL`; production code should not treat them as general-purpose policy fields unless the hardware programming guide requires it.

## Test Signals

Useful validation is mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU display code that includes `dcn_4_2_0_sh_mask.h` with `dcn_4_2_0_offset.h`. Missing or renamed symbols should surface in stream-encoder, DSC, link-encoder, and perfmon field tables.
- Mechanically compare this range against AMD's authoritative DCN 4.2.0 register database, treating the first and last registers as partial-boundary cases.
- Check that every `__SHIFT` macro has a matching `_MASK` macro where the source database defines a normal field. This chunk has a small 1,067/1,072 shift-mask imbalance due to range boundaries or generated partial entries and should be reconciled with neighboring chunks.
- Validate mirrored DSC layouts across instances 0-3, especially PPS registers, interrupt status/clear fields, buffer fullness counters, memory power controls, and debug buses.
- Exercise DisplayPort output through a topology that uses DP4, including hotplug, mode-set, MST/MSO where applicable, HDR/VSC/SPD/adaptive-sync info packets, PPS metadata, and secondary packet scheduling.
- Test DSC-enabled modes across slice counts, bits per component, bits per pixel, RGB/YUV formats, and high-bandwidth modes. Watch for blanking, visual corruption, downstream DSC negotiation failures, and interrupt status for output-buffer overflow/underflow or RC model overflow.
- Cover panel replay and ALPM/AUX-less ALPM entry and exit, including idle, wake, selective update, suspend/resume, and link retraining.
- Use symbol-count and perfmon/debug paths during stress modes to confirm counters start, stop, clear, and report plausible values without stale or stuck status bits.

## Cross-Chunk Notes

The preceding chunk contains the beginning of `DP4_DP_MSO_CNTL1` and earlier DP4 stream-encoder fields. This chunk then covers the remainder of the DP4 secondary-data/low-power/replay/statistics area and most of DSC instances 0-2 plus the beginning of DSC instance 3. The following chunk is required to complete `DSCC3` PPS/configuration/debug coverage before a final per-file report can make complete claims about all DCN 4.2.0 DSC compressor metadata.

### subset-b-002238: lines 49894-52359

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 49894-52359

## Purpose

This chunk is generated AMD DCN 4.2.0 register-field metadata. It contains only C preprocessor constants for hardware bit positions and masks; it does not implement executable driver logic. AMDGPU display code combines these `...__SHIFT` and `..._MASK` constants with the matching DCN 4.2.0 register offsets to pack, extract, preserve, clear, or update individual MMIO fields through common register helpers.

The requested range contains 2,121 `#define` lines: 1,062 shift macros and 1,059 mask macros across 307 register-like macro groups. The shift/mask imbalance is caused by the range ending inside `DP_STREAM_ENC1_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1`; the remaining three masks for that register are on lines 52360-52362, immediately after this chunk. The first included register, `DSCC3_DSCC_PPS_CONFIG6`, is complete in this range, although its comment line is immediately before the chunk at line 49893.

Although the source path sits under a local `ceph-client` mirror, this header is AMDGPU display hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, allocations, locks, or includes in this range. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset used to encode or decode a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, clear, preserve, or update that field.

Major register families covered in this chunk:

- `DSCC3_DSCC_*`: tail of DSC compressor 3 picture-parameter-set metadata, memory power controls, compression quality/error counters, output and rate-buffer fullness telemetry, and test/debug index/data registers. PPS fields include DSC version-adjacent rate-control values such as BPG offsets, initial/final offsets, flatness QP limits, RC model size, buffer thresholds, and 15 range min-QP/max-QP/BPG-offset entries.
- `DC_PERFMON20_*` and `DC_PERFMON21_*`: display performance monitor counter selection, counter-control, counter-state, perfmon control, interrupt/status/mask fields, and high/low counter-value access. `DC_PERFMON20` is under the DSC3 perfmon address block; `DC_PERFMON21` is under the writeback perfmon block.
- `DWB_*` and `FC_*`: writeback top-level clock/memory power, frame-composition mode/flow/window/source-size controls, update and CRC controls, CRC masks/values, output control, MMHUBBUB backpressure counting, host-read control, overflow status/counter, soft reset, debug controls, HDR multiplier, gamut remap modes and coefficients, output gamma controls, OGAM LUT index/data/control, and OGAM RAM A/B start/end/offset/region programming.
- `DCHVM_*`: display client HVM control, clock control, memory control, RIOMMU control, and RIOMMU status fields.
- `DP_STREAM_ENC0_*` and beginning of `DP_STREAM_ENC1_*`: HPO DisplayPort stream encoder clock gating/status, pixel/audio input muxes, APG clock enable, clock-ramp-adjuster FIFO control/status, FIFO level calibration fields, and spare fields. The `DP_STREAM_ENC1` FIFO status/control1 group is partial at the chunk boundary.
- `APG5_*`: audio packet generator debug audio generation and APG memory power fields for stream encoder 0.
- `DME5_*`: data mapper engine control and memory control fields, including enable/reset-style control fields and low-power memory controls.
- `VPG5_*`: video packet generator generic packet access/data, generic stream packet frame-update and immediate-update controls, generic status, memory power, and ISRC1/2 packet access/data fields.
- `DP_SYM32_ENC0_*`: HPO DP 32-symbol encoder controls for video FIFO, MSA double buffering, pixel format, MSA payload fields, HBLANK behavior, generic SDP/GSP controls 0-14, audio SDP controls, metadata packet control, MSA/VBID/stream/panel-replay controls, video CRC control/results/status, symbol counting, ALPM sleep/wake/request/ready/hardware-mode/status/start/interrupt fields, memory power control, and spare fields.
- `DP_LINK_ENC0_*`: HPO DP link encoder clock control and spare fields.
- `DP_DPHY_SYM320_*`: HPO DP DPHY/SYM32 control and status, SAT update and virtual-channel rate control/status, eDP mode and ASSR seeds, ALPM sleep/wake/control parameters, test-pattern configuration and PRBS/custom pattern data, error-status bits, and symbol/cycle counting controls.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 4.2.0 source files include `dcn_4_2_0_sh_mask.h` together with `dcn_4_2_0_offset.h`.
2. Resource, DMUB, GPIO, DWB, HPO DP, DSC, and packet-generator code builds register tables by token-pasting symbolic register names with matching offset, shift, and mask macros.
3. Runtime paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, and poll/wait variants.
4. The constants in this chunk determine which bits those helpers touch while programming DSC PPS/rate-control state, writeback capture and color processing, performance counters, HPO DP stream/link/symbol encoders, packet generators, DPHY/SAT/eDP/ALPM state, and related debug or status registers.

The macros do not encode ordering rules. Consumers must still follow hardware sequencing for DSC enable and PPS load, writeback clock and memory power-up, LUT and gamma programming, update latching, CRC/overflow status handling, DP stream encoder FIFO reset/calibration, VPG packet update timing, MSA/SDP/VBID programming, DPHY virtual-channel setup, ALPM entry/exit, and interrupt/status acknowledgement.

## State And Persistence Behavior

This chunk stores no mutable software state and persists nothing to disk. It describes hardware-backed register state in DCN 4.2.0 display blocks:

- DSC compressor state: PPS and rate-control fields configure how DSCC3 compresses a stream, while quality/error/fullness/debug counters expose compressor health and diagnostics.
- Performance monitor state: counter-selection, enable, overflow, interrupt, and value fields are live hardware telemetry controlled by perfmon programming.
- Writeback state: DWB/FC fields configure capture dimensions, source and output routing, CRC masking/readback, overflow tracking, backpressure counts, host reads, soft resets, gamut remap matrices, HDR multiplier, and OGAM LUT/RAM state.
- Power and clock state: `*_MEM_PWR*`, clock-control, APG, DME, VPG, stream encoder, symbol encoder, DPHY, and HVM fields can control or reflect power-gated or clock-gated domains.
- DisplayPort packet and stream state: HPO stream encoder, VPG, DP SYM32, link encoder, and DPHY fields control stream source muxes, audio source muxes, generic packets, SDP/GSP timing, MSA/pixel format/VBID, video CRC, symbol counters, virtual-channel rates, eDP ASSR, ALPM, and test patterns.
- Diagnostic state: debug buses, counters, CRC results, overflow flags, symbol counts, DPHY error bits, FIFO calibration/status, and SAT virtual-channel status are readback-oriented or event/status-oriented fields.

Persistence is hardware-defined. Values may survive only until modeset, stream disable/enable, writeback disable, display block reset, GPU reset, suspend/resume, firmware reinitialization, or clock/power gating. Status and event fields can be read-only, sticky, self-clearing, write-one-to-clear, or valid only while their block clock is active. The generated shift/mask header does not distinguish configuration fields from status, write-clear, or latch-trigger fields; consuming code and the hardware programming guide must supply those semantics.

## Dependencies And Integration Points

This chunk must remain synchronized with AMD's generated DCN 4.2.0 register database and the matching offset/base-index definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`.

Direct inclusion points found in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c`

Functional integration points include:

- DSC programming paths that construct PPS register writes and read compressor error/fullness telemetry.
- DWB and color-management paths, including generic DWB register definitions in `display/dc/dwb/dcn30/dcn30_dwb.h` and OGAM programming in `display/dc/dwb/dcn30/dcn30_dwb_cm.c`.
- HPO DP stream encoder code that uses stream encoder field lists such as `DP_STREAM_ENC_CLOCK_EN` in `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`.
- VPG/APG/DME packet and audio-data paths for generic stream packets, ISRC packets, audio packet generation, and data mapping.
- DP SYM32/DPHY/link encoder paths that program MSA, SDP, VBID, CRC, symbol-count, ALPM, SAT virtual-channel, eDP ASSR, and test-pattern behavior.
- Perfmon and diagnostic tooling that reads display counter, CRC, overflow, FIFO, symbol-count, DPHY error, and debug-bus fields.

The critical ABI is the macro name and numeric value. Register-helper tables rely on exact symbolic spellings such as `DWB_OGAM_RAMA_REGION_0_1__DWB_OGAM_RAMA_EXP_REGION0_LUT_OFFSET_MASK` or `DP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_CONTROL__DP_STREAM_ENC_CLOCK_EN__SHIFT`, while the paired offset header supplies the register address and base index.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong hardware bits.
- This is generated metadata. Manual edits risk divergence from AMD's source register database, the paired offset header, firmware expectations, and silicon documentation.
- The range ends inside `DP_STREAM_ENC1_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1`. Complete validation for that register requires the three following mask lines outside this chunk.
- Many blocks are instance-sensitive. `DSCC3`, `DC_PERFMON20/21`, `APG5`, `DME5`, `VPG5`, `DP_STREAM_ENC0/1`, `DP_SYM32_ENC0`, `DP_LINK_ENC0`, and `DP_DPHY_SYM320` prefixes must match the intended hardware instance; a copied macro with the wrong instance can target a plausible but unrelated register.
- Writeback color processing is highly table-sensitive. Bad OGAM region, offset, base, slope, or gamut-remap masks can produce subtle color, HDR, or capture-output corruption rather than an obvious failure.
- DSC PPS/rate-control fields are stream-format sensitive. Incorrect BPG, QP, threshold, offset, or model-size masks can cause visible compression artifacts, underflow, or link-bandwidth mismatches.
- Clock, memory-power, reset, FIFO, and calibration fields often require strict sequencing and polling. Correct masks used in the wrong order can leave DWB, packet, stream encoder, or DPHY blocks inactive or partially calibrated.
- Status and interrupt fields can be sticky or write-clear. Bad masks can clear unrelated error bits, miss overflow/CRC/FIFO/ALPM events, or report stale diagnostics.
- DPHY SAT/eDP/ALPM/test-pattern fields affect link-layer behavior and may fail only for specific panels, link rates, MST/SST topologies, power states, or compliance-test modes.
- High-bit masks such as `0x80000000L` should be handled with unsigned-safe register operations by consumers.

## Test Signals

Useful validation combines generated-header consistency checks with hardware-facing display tests:

- Build AMDGPU display support with DCN 4.2.0 enabled. Missing or renamed macros should fail in DMUB, resource, GPIO, DWB, HPO DP, DSC, packet-generator, or register-table code.
- Mechanically verify that each complete register field in the chunk has one `__SHIFT` and one `_MASK`, allowing the expected boundary exception for `DP_STREAM_ENC1_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1`.
- Diff this slice against AMD's authoritative DCN 4.2.0 register database and against nearby generated DCN headers where layout compatibility is expected.
- Exercise DSC-enabled display modes across bpp, slice sizes, native 4:2:0/4:2:2, suspend/resume, modeset, and link retraining; watch for compressor underflow, quality/error counters, rate-buffer fullness, and visible artifacts.
- Exercise DWB capture with scaling/window/source-size changes, CRC generation, overflow/backpressure monitoring, host reads, gamut remap, HDR multiplier, and OGAM LUT/RAM programming; compare captured color output and CRC/error counters.
- Exercise HPO DP stream encoder and DP SYM32 paths across hotplug, MST/SST where supported, audio packets, generic SDP/GSP metadata, MSA/pixel-format changes, VBID, panel replay, ALPM, and video CRC.
- Exercise DPHY/eDP/SAT behavior with ASSR, ALPM sleep/wake, virtual-channel rate fields, symbol/cycle counters, PRBS/custom test patterns, and error-status readback.
- Monitor kernel logs, DCN debug traces, register dumps, perfmon counters, CRC results, FIFO status, DPHY error status, symbol counters, overflow counters, and visual/audio output for stuck status bits, wrong channel routing, missed packet updates, color corruption, or resume-only failures.

## Cross-Chunk Notes

The previous line, 49893, contains the comment for `DSCC3_DSCC_PPS_CONFIG6`; all six shift/mask definitions for that register are included in this chunk. The following lines 52360-52362 contain the remaining `FIFO_MAXIMUM_LEVEL`, `FIFO_CAL_AVERAGE_LEVEL`, and `FIFO_CALIBRATED` masks for `DP_STREAM_ENC1_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1`, followed by `DP_STREAM_ENC1_DP_STREAM_ENC_SPARE`. The final per-file report should reconcile this boundary before making complete claims about every `DP_STREAM_ENC1` stream-encoder register in `dcn_4_2_0_sh_mask.h`.

### subset-b-002239: lines 52360-54779

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 52360-54779

## Scope

This chunk is part of the generated AMD DCN 4.2.0 ASIC register shift/mask header. It contains C preprocessor constants only: each hardware field is exported as a `...__SHIFT` bit position and a matching `..._MASK` bit mask. There are no functions, structs, branches, allocations, locks, or direct MMIO accesses in this range.

The range contains 2,118 `#define` entries and spans HPO DisplayPort stream/link encoder register families. It starts at the tail of `DP_STREAM_ENC1_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1`, then covers APG/DME/VPG, DP SYM32 encoder, link encoder, and DPHY SYM32 blocks for stream/link instances 1 and 2, and ends inside the VPG8 immediate-update fields for stream encoder 3. Adjacent chunks are needed for complete boundary context around the first `DP_STREAM_ENC1` FIFO register and the remaining `VPG8_VPG_GSP_IMMEDIATE_UPDATE_CTRL` fields.

## Purpose

The purpose of this chunk is to publish the bitfield contract for DCN 4.2.0 HPO DisplayPort stream processing and symbol/link transmission blocks. Runtime AMDGPU display code combines these field macros with matching offset definitions from `dcn_4_2_0_offset.h` and AMD display register helpers to program DisplayPort stream encoders, audio/debug packet generators, metadata engines, generic secondary-data packets, symbol encoders, link clocks, and DP physical-layer symbol scheduling.

Important covered areas:

- `DP_STREAM_ENC1/2/3` stream encoder control surfaces: clock enables/status, pixel stream mux selection, audio stream mux selection, APG clock enable, clock-ramp FIFO reset/read-level/calibration/status/error fields, and spare fields.
- `APG6/7/8` audio packet generator support: debug generator enable/reset, per-channel audio enable, test-channel disable, and APG memory power force/disable/state/default-low-power controls.
- `DME6/7/8` metadata engine support: HUBP requestor selection, metadata enable, stream type, double-buffer pending/taken/clear/disable states, missed-transmission detection/clear, and DME memory power controls.
- `VPG6/7/8` video packet generator support: generic packet RAM indexed access, generic packet byte packing, frame-update and immediate-update triggers/pending bits for 15 generic packets, conflict/lock status, VPG memory light-sleep controls, and ISRC indexed data for VPG6/7. VPG8 is only partially present in this chunk.
- `DP_SYM32_ENC1/2` symbol encoder support: enable/reset/status, pixel-to-symbol FIFO controls, MSA and pixel-format double buffering, MSA payload registers, HBLANK symbol width, 15 GSP SDP control registers, SDP/audio/metadata packet controls, MSA/VBID/video-stream controls, panel replay tunneling optimization, video CRC, symbol counters, ALPM sleep/wake scheduling, wake interrupts, memory power, and spare fields.
- `DP_LINK_ENC1/2` link encoder clocks: link encoder clock enable/on-status on `SYMCLK32`, plus spare fields.
- `DP_DPHY_SYM321/322` physical/link symbol scheduler fields: DPHY enable/reset, precoder, mode, lane count, output mode, sleep start, status, SAT updates, VC rate controls, stream allocation table programming/status, eDP security/ASSR seeds, ALPM timing, training pattern generation, PRBS/custom pattern data, error status, and LLCP/cycle symbol counters.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` is the bit offset of a field in the hardware register.
- `<REGISTER>__<FIELD>_MASK` is the field mask to preserve adjacent fields during masked updates.
- Prefixes identify replicated hardware instances. `DP_STREAM_ENC2_*`, `DP_SYM32_ENC2_*`, `DP_LINK_ENC2_*`, and `DP_DPHY_SYM322_*` belong to the second HPO DP path; APG/DME/VPG instance numbers are offset (`APG7`, `DME7`, `VPG7`) for stream encoder 2.

Notable field families include:

- Stream encoder FIFO and clocking: `DP_STREAM_ENC*_DP_STREAM_ENC_CLOCK_CONTROL`, `...INPUT_MUX_CONTROL`, `...AUDIO_CONTROL`, and `...CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL0/1` define enable/status bits, source selection, FIFO reset/read-start level/read-clock source, video-active, overflow/underflow error, overwrite level, recalibration, min/max/average levels, and calibrated status.
- Packet generation and metadata: `APG*_APG_DBG_GEN_CONTROL`, `DME*_DME_CONTROL`, and `VPG*_VPG_GENERIC_PACKET_*` fields support audio debug packets, metadata packet handoff from HUBP, generic secondary-data packet storage, and update synchronization.
- VPG update control: `VPG*_VPG_GSP_FRAME_UPDATE_CTRL` and `...IMMEDIATE_UPDATE_CTRL` have paired trigger bits and pending bits for `VPG_GENERIC0` through `VPG_GENERIC14`, allowing packet changes to be synchronized to frame boundaries or applied immediately.
- Symbol encoder video programming: `DP_SYM32_ENC*_VID_PIXEL_FORMAT`, `...VID_MSA0` through `...VID_MSA8`, `...VID_MSA_CONTROL`, `...VID_VBID_CONTROL`, and `...VID_STREAM_CONTROL` carry pixel encoding/depth, main stream attributes, compressed-stream flag timing, and stream enable/defer/status behavior.
- Secondary-data packet scheduling: `DP_SYM32_ENC*_SDP_GSP_CONTROL0` through `...CONTROL14`, `...SDP_CONTROL`, `...SDP_AUDIO_CONTROL0/1`, and `...SDP_METADATA_PACKET_CONTROL` define continuous or one-shot GSP transmission, idle/video transmission enable, payload size, SOF reference, line-number scheduling, pending/deadline flags, CRC16 enable, ASP/ATP/AIP/ACM/ISRC audio packet enablement, audio mute, and metadata packet double buffering.
- Low-power and diagnostics: `DP_SYM32_ENC*_ALPM_*`, `...VID_CRC_*`, and `...SYMBOL_COUNT_*` fields define ALPM sleep/wake request timing, hardware mode/status/start state, wake interrupts, CRC result/valid/ack fields, and BS symbol counters.
- DPHY scheduling and allocation: `DP_DPHY_SYM32*_CONTROL`, `STATUS`, `SAT_UPDATE`, `VC_RATE_CNTL0-3`, `SAT_VC0-3`, and `SAT_VC_STATUS0-3` configure active/test/training modes, lane count, output target, stream virtual-channel rates, stream allocation slots, encryption flags, and update/status polling.
- DPHY eDP, ALPM, and training/test support: `EDP_CONFIG0`, `EDP_ASSR0-3`, `ALPM_SLEEP_CONFIG0`, `ALPM_WAKE_CONFIG0`, `ALPM_CONTROL`, `TP_CONFIG`, `TP_PRBS_SEED0-3`, `TP_SQ_PULSE`, and `TP_CUSTOM0-10` expose embedded DisplayPort security/ASSR seed programming, low-power pattern timing, training pattern selection, PRBS seeds, square pulse width, and custom pattern words.
- DPHY error and counter status: `ERROR_STATUS`, `SYMBOL_COUNT_STATUS0/1`, and `SYMBOL_COUNT_CONTROL` publish total-slot, rate, duplicate stream-source, missing ACT, unexpected mode transition, illegal symbol, counter overflow, cipher, ALPM wake timing, LLCP count, and cycle count signals.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime flow is indirect:

1. DCN 4.2 display components include this header with `dcn_4_2_0_offset.h`.
2. Register tables or helper macros pair a `reg...` offset with the corresponding `__SHIFT` and `_MASK` definitions.
3. AMD display register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and indexed variants perform masked MMIO or indirect register operations.
4. Hardware then applies the state changes in stream encoder, packet generator, symbol encoder, link encoder, and DPHY blocks.

The represented hardware flow is typically: enable clocks for the stream/link path, choose pixel and audio sources, configure video format and MSA data, program generic/audio/metadata SDP packets, arm double-buffered or immediate updates, enable the video stream, configure DPHY mode/lane count/rate/allocation-table state, and poll status/pending/error/counter fields for completion or failure.

## State and Persistence Behavior

The file itself has no mutable or persistent state. All state described by these macros lives in GPU display hardware registers.

Hardware state represented in this chunk includes:

- Clock and reset state for stream encoders, SYM32 encoders, link encoders, APG/DME/VPG memory blocks, and DPHY symbol scheduler blocks.
- Stream routing state, including pixel-stream and audio-stream source selectors.
- FIFO calibration and health state, including reset-done, active-video, error, level, min/max, average, overwrite, and calibrated bits.
- Packet RAM and packet scheduling state for VPG generic packets, ISRC data, SYM32 GSP SDP controls, audio packets, and metadata packets.
- Double-buffer and pending state for MSA, pixel format, GSP packets, metadata packets, frame updates, immediate updates, ALPM requests, and wake interrupts.
- Video link state for MSA payloads, pixel encoding/depth, HBLANK symbol width, VBID compressed-stream flags, stream enable/defer/status, panel replay tunneling optimization, CRC results, and symbol counters.
- DPHY state for mode/lane/output configuration, SAT and VC rate programming, eDP security/ASSR, ALPM pattern timing, training/test pattern generation, error flags, and LLCP/cycle counters.

Persistence is limited to hardware programming lifetime. Values can be lost or require reprogramming after display engine reset, GPU reset, power gating, suspend/resume, hotplug retraining, mode set, stream reallocation, or link disable. Higher-level DC state, link-training policy, and DMUB firmware state remain the durable software authority; these macros only define how software encodes bits in the hardware registers.

## Dependencies

This chunk depends on:

- `dcn_4_2_0_offset.h`, which supplies the register addresses corresponding to these field names.
- AMD display register-helper infrastructure that token-pastes register and field names into masked reads/writes/updates/waits.
- DCN 4.2 display components that include the generated mask header, including DMUB support, IRQ service, resource construction, GPIO translation/factory code, and clock-manager code.
- Generated register tables and DCN 4.2 hardware descriptions that keep stream/link instance prefixes aligned across offset and mask headers.
- Related enum definitions such as the SOC24 `DP_STREAM_ENC`, `DP_SYM32_ENC`, and `DP_DPHY_SYM32` enum blocks, which document expected symbolic values for many of these bitfields.

Because the header is generated silicon metadata, manual edits are risky unless regenerated from the same register database as the offsets and any associated register tables.

## Integration Points

Main integration points are the macro-name ABI and register-field layout contract consumed by AMDGPU display code.

- Display mode programming uses `DP_STREAM_ENC*` and `DP_SYM32_ENC*` fields to route streams, program pixel format/MSA, configure stream enable/defer behavior, and synchronize double-buffered updates.
- Audio and secondary-data packet programming uses APG, VPG, DME, and SYM32 SDP fields to transmit audio, generic packets, ISRC, metadata, and other DisplayPort sideband data with frame or line timing.
- Link training and link operation use DPHY control/status, training pattern, lane-count, mode, rate, SAT, and error fields to transition from training patterns to active transmission and to diagnose protocol-level problems.
- Power management uses APG/DME/VPG/SYM32 memory power fields, ALPM sleep/wake scheduling, wake interrupts, and DPHY ALPM controls.
- Validation and debug paths use CRC result/status, symbol counters, FIFO error/level fields, DPHY error status, PRBS/custom pattern controls, LLCP/cycle counters, generic packet conflict status, and deadline/pending bits.
- DMUB/DCN42 resource and clock code depend on the generated header resolving consistently when building register tables or firmware-facing control paths.

## Risks and Failure Modes

- A wrong shift or mask can corrupt neighboring fields in the same 32-bit register, causing blank display, bad packet timing, audio loss, metadata loss, broken ALPM entry/exit, or link-training failures.
- Instance-prefix mistakes are easy in this repeated generated section. A field from stream 1, 2, or 3 can compile while targeting the wrong stream/link/APG/DME/VPG/DPHY instance if paired with the wrong offset macro.
- Boundary incompleteness matters: this chunk starts after some `DP_STREAM_ENC1` FIFO fields and ends before the rest of `VPG8_VPG_GSP_IMMEDIATE_UPDATE_CTRL`, so final per-file synthesis must reconcile neighboring chunks before drawing whole-register conclusions.
- Pending, clear, reset, and status bits have hardware-specific write semantics. Misusing masks for `*_PENDING`, `*_CLR`, `*_RESET`, `*_RESET_DONE`, `*_VALID_ACK`, `*_OCCURRED`, or `*_CLEAR` fields can hang update flows or lose diagnostics.
- Generic packet update conflicts can happen if VPG lock/conflict fields and frame/immediate pending bits are ignored when packet RAM is rewritten.
- DPHY SAT/VC rate mistakes can allocate the wrong stream source, slot count, or rate, producing protocol errors that only appear at specific lane counts, link rates, MST/SST layouts, or DSC/compression modes.
- ALPM and eDP ASSR/security fields are timing-sensitive. Incorrect masks can create intermittent resume/wake failures, early wake requests, unexpected mode transitions, or panel-specific blanking.
- High-bit masks such as `0x80000000L`, `0xFFFF0000L`, and `0xFE000000L` require unsigned-safe register math in consumers.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Build coverage for DCN 4.2 display code with all referenced `DP_STREAM_ENC*`, `APG*`, `DME*`, `VPG*`, `DP_SYM32_ENC*`, `DP_LINK_ENC*`, and `DP_DPHY_SYM32*` `__SHIFT`/`_MASK` symbols resolving.
- Register-generation consistency checks comparing `dcn_4_2_0_sh_mask.h` against the matching `dcn_4_2_0_offset.h` and the authoritative DCN 4.2 register database.
- Display smoke tests covering DP/eDP mode set, hotplug, link retraining, suspend/resume, GPU reset, stream enable/disable, MST if supported, DSC/compressed stream paths, and different lane-count/link-rate combinations.
- Packet tests covering generic SDP/VSC/HDR-style metadata, ISRC, audio packet enable/mute, metadata double buffering, VPG frame/immediate update pending bits, and packet conflict status.
- Link/PHY diagnostics covering DPHY mode/lane/output programming, SAT update pending/status, VC rate programming, training pattern generation, PRBS/custom pattern paths, DPHY error status, LLCP/cycle counters, and link error recovery.
- Power-management tests covering APG/DME/VPG/SYM32 memory power state transitions, ALPM sleep/wake request timing, ALPM wake interrupt occurrence/clear behavior, and panel replay tunneling optimization.
- CRC/counter validation using SYM32 video CRC valid/ack/result fields and BS symbol counters to confirm stream data path integrity.

## Chunk Notes

This is a source-tree-aligned chunk research document only. It intentionally does not create the final per-file report for `dcn_4_2_0_sh_mask.h`; that synthesis belongs to the merge/reconciliation lane after all chunks for the generated header are available.

### subset-b-002240: lines 54780-57274

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 54780-57274

## Scope

This chunk is part of AMD's generated DCN 4.2.0 register shift/mask header. It contains preprocessor constants only: each hardware bitfield is represented by a `...__SHIFT` bit position and a matching `..._MASK` mask value. There are no C functions, structs, enums, variables, includes, locks, allocations, branches, or direct MMIO operations in this range.

The requested range contains 2,092 `#define` lines across 374 distinct register names. It starts at an artificial boundary inside `VPG8_VPG_GSP_IMMEDIATE_UPDATE_CTRL`, completes the tail of the HPO VPG8 generic-packet block, covers HPO DP symbol32 stream/link/DPHY instance 3, covers MPCC mixer instances 0 through 3, covers complete MPCC output-gamma/gamut-remap instances 0 and 1, and ends inside the beginning of `MPCC_OGAM2_MPCC_OGAM_RAMA_REGION_6_7`. Neighboring chunks are required for the complete boundary registers and for the rest of MPCC_OGAM2.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement distributed filesystem behavior.

## Purpose

The purpose of this chunk is to publish exact DCN 4.2.0 bitfield metadata for high-performance DisplayPort output, generic packet generation, stream/link PHY control, MPC blending, output gamma, and gamut remap hardware. Runtime display code combines these field constants with matching register offsets from `dcn_4_2_0_offset.h` and AMD display register helpers to perform masked reads, writes, updates, and polling without hand-coded bit arithmetic.

Important covered surfaces:

- `VPG8_*` tail fields define HPO generic packet update/status, VPG memory-power control, and ISRC indexed payload access.
- `DP_SYM32_ENC3_*` defines the third HPO DP 32-bit-symbol stream encoder fields for enable/reset, pixel-to-symbol FIFO, MSA double buffering, pixel format, video MSA payload words, generic SDP/GSP scheduling, audio SDP, metadata packets, VBID, stream enable, panel replay, CRC, symbol counters, ALPM, wake interrupt state, memory power, and spare bits.
- `DP_LINK_ENC3_*` defines HPO DP link-encoder clock-control and spare fields for the same output path.
- `DP_DPHY_SYM323_*` defines symbol32 DP DPHY control/status, VC-rate programming, slot-allocation-table entries and status for virtual channels 0-3, eDP ASSR, ALPM, test-pattern generation, error status, and symbol counters.
- `MPCC0_*` through `MPCC3_*` define Multi-Plane Composition Controller mixer fields for input selection, OPP routing, blending/alpha/global gain, stereo/segment mode, update lock selection, background color, OGAM memory power, and status.
- `MPCC_OGAM0_*` and `MPCC_OGAM1_*` define complete output-gamma and gamut-remap bitfields for two MPCC OGAM instances: LUT access, RAM A/B piecewise-linear curve controls and region tables, coefficient format, gamut-remap mode/current status, and A/B matrix coefficient banks.
- `MPCC_OGAM2_*` begins the same OGAM layout for instance 2, from control/LUT access through the first RAM A region-table registers. This block continues after the chunk boundary.

## Important APIs, Types, And Macros

There are no typed C APIs in this range. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used by AMD register helpers to preserve unrelated bits.
- Address-block comments, such as `dce_dc_hpo_dp_sym32_enc3_dispdec` and `dce_dc_mpc_mpcc_ogam0_dispdec`, preserve the register-database grouping used by generated offset and field headers.

Major macro families:

- VPG8 generic-packet fields: `VPG_GENERIC*_IMMEDIATE_UPDATE`, `VPG_GENERIC*_IMMEDIATE_UPDATE_PENDING`, `VPG_GENERIC_LOCK_STATUS`, `VPG_GENERIC_CONFLICT_OCCURED`, `VPG_GENERIC_CONFLICT_CLR`, `VPG_GSP_MEM_LIGHT_SLEEP_DIS`, `VPG_GSP_LIGHT_SLEEP_FORCE`, `VPG_GSP_MEM_PWR_STATE`, `VPG_ISRC1_2_DATA_INDEX`, and four indexed ISRC data bytes.
- DP symbol32 stream encoder fields: `DP_SYM32_ENC_ENABLE`, reset/reset-done, pixel FIFO enable/reset/overflow, MSA and pixel-format double-buffer enable/pending, `PIXEL_ENCODING_TYPE`, uncompressed pixel encoding and component depth, `MSA_DATA`, HBLANK minimum symbol width, and 15 replicated `SDP_GSP_CONTROLn` blocks.
- GSP/SDP scheduling fields in each `SDP_GSP_CONTROLn`: continuous video/idle transmission enable, one-shot trigger and position, double-buffer enable/pending, payload size, SOF reference, deadline missed, transmission pending, and transmission line number.
- Audio and metadata packet fields: audio SDP continuous/line/send-at-hblank controls, audio HBLANK/TU interval, metadata packet enable/pending/deadline status, MSA/VBID controls, and stream-control fields.
- CRC and diagnostic fields: video CRC enable/continuous/selection, four CRC result registers, CRC status, symbol count status/control, DPHY error status, DPHY symbol count status/control, and test-pattern configuration/data fields.
- ALPM and panel replay fields: panel replay enable/status update, ALPM sleep and wake minimum symbol counts, request-offset, ready control, hardware mode control, ALPM status, ALPM start, and wake interrupt enable/status.
- DP DPHY VC and SAT fields: `DPHY_SYM32_ENABLE`, reset/reset-done, lane enable, link-rate, power-down, mux mode, PHY status, VC rate programming and update, SAT slot assignments for VC0-VC3, SAT/VC update requests, and update-pending/status bits.
- MPCC mixer fields: top/bottom select, OPP ID, MPCC mode, alpha blend/multiplied mode, active-overlap-only, global alpha/gain, background bit depth, bottom gain mode, control-current status, stereoscopic mode control, update lock select, top/bottom gains, movable color-management location, background RGB/YCbCr components, memory power controls, and disabled/idle/busy status.
- OGAM LUT and RAM fields: `MPCC_OGAM_MODE`, select/current status, PWL disable, LUT index/data/control, write color mask, read color select/debug, host select, config mode, RAM A/B start/end/offset/base/slope controls for B/G/R channels, and 34 curve-region descriptors per RAM.
- Gamut-remap fields: coefficient format, mode/current status, and A/B banks of matrix coefficient registers such as `C11_C12`, `C13_C14`, `C21_C22`, `C23_C24`, `C31_C32`, and `C33_C34`.

The repeated instance prefixes are semantically important. `DP_SYM32_ENC3`, `DP_LINK_ENC3`, and `DP_DPHY_SYM323` belong to one HPO DP output path; `MPCC0` through `MPCC3` are separate composition/mixer instances; and `MPCC_OGAM0` through `MPCC_OGAM2` are per-MPCC output gamma/remap instances.

## Control Flow

This header has no executable control flow. Runtime flow is created by consumers that include this file with the matching offset header and expand register-list macros into register tables.

Typical use is:

1. DCN 4.2 display code selects `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`.
2. Component headers and constructors token-paste symbolic register names into register descriptors, pairing offsets/base indexes with these shift/mask definitions.
3. Runtime paths call AMD display helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, or wait/poll helpers against those descriptors.
4. The driver uses the resulting masked operations during modeset, atomic plane composition, color-management programming, DP link setup, secondary-data packet scheduling, audio/metadata setup, ALPM/panel-replay handling, diagnostics, and power-management transitions.

The hardware programming order is not encoded here. For example, stream encoder enable/reset, FIFO reset, MSA/pixel-format double-buffer updates, GSP packet one-shot or continuous transmission, DPHY VC-rate/SAT programming, ALPM wake/sleep sequencing, MPCC update locks, OGAM LUT loads, and gamut-remap bank switching are sequenced by the display driver and hardware specification.

## State And Persistence Behavior

The file itself holds no mutable or persistent software state. All represented state lives in hardware registers.

Hardware-backed state described by this chunk includes:

- VPG state: generic packet update requests and pending bits, conflict/lock state, indexed ISRC data bytes, and VPG GSP memory power state.
- HPO DP stream state: encoder enable/reset state, pixel-to-symbol FIFO state, MSA words, pixel format, SDP/GSP packet scheduling, audio SDP timing, metadata packet state, VBID/stream enable, panel replay, CRC state/results, symbol counts, and ALPM control/status.
- HPO DP link/PHY state: link encoder clock state, DPHY lane/link/mux/power/reset state, virtual-channel rates, slot-allocation tables, eDP ASSR registers, ALPM configuration, test-pattern generator state, error status, and symbol counters.
- MPCC composition state: selected top/bottom inputs, selected OPP, blend mode, alpha/global gain, background color, stereo mode, movable color-management location, update-lock target, OGAM memory-power controls, and idle/busy/disabled status.
- OGAM state: selected mode and LUT bank, indexed LUT payload, RAM A/B curve start/end/base/slope/offset and region tables, gamut-remap coefficient format, active/current gamut-remap mode, and A/B matrix coefficient banks.

Persistence is hardware-defined. Values usually remain programmed until modeset, atomic update, block disable, power gating, suspend/resume, GPU reset, display engine reset, or ASIC reset rewrites them. Status, pending, interrupt-like, CRC, overflow, reset-done, and update-pending fields may be read-only, sticky, self-clearing, or valid only while the relevant block is powered and clocked. This generated header does not encode those access semantics.

## Dependencies And Integration Points

Direct dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` supplies the matching register offsets and base-index selectors for these field names.
- AMD display register-helper infrastructure supplies the masked register access macros that consume `__SHIFT` and `_MASK` symbols.
- AMD's DCN 4.2.0 register database is the authoritative source for the generated names and bit positions.

Important integration points visible from the naming and surrounding tree:

- HPO DP stream/link code consumes `DP_SYM32_ENC*`, `DP_LINK_ENC*`, and `DP_DPHY_SYM32*` field lists for DP 2.x stream encoder, link encoder, DPHY VC-rate/SAT, ALPM, panel replay, CRC, and diagnostics.
- Generic packet and metadata paths consume the `VPG8_*`, `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL*`, audio SDP, and metadata packet fields during infoframe, SDP, audio, ISRC, and metadata programming.
- MPC/MPCC code consumes `MPCC0_*` through `MPCC3_*` for plane blending, OPP routing, update-lock selection, stereo mode, background color, and memory-power handling.
- Color-management code consumes `MPCC_OGAM*` fields for output gamma LUT programming, RAM A/B PWL region setup, bank selection/current-mode checks, and gamut-remap matrix programming.
- Generated register tables depend on exact instance alignment. The stream encoder instance `3`, link encoder instance `3`, and DPHY instance `323` must pair with the matching offsets, while MPCC and OGAM instance numbers must line up with the resource-pool pipe/plane topology.

## Risks And Failure Modes

- A wrong shift or mask can compile cleanly while corrupting adjacent fields in the same register. Failures may appear only as runtime display symptoms.
- Chunk boundaries are not semantic. This range starts after the first `VPG8_VPG_GSP_IMMEDIATE_UPDATE_CTRL` fields and ends in the middle of `MPCC_OGAM2`; final per-file reconciliation must merge adjacent chunks before making whole-block claims.
- HPO DP instance alignment is critical. Mixing `DP_SYM32_ENC3`, `DP_LINK_ENC3`, or `DP_DPHY_SYM323` with another instance's offsets can program the wrong stream or PHY path.
- GSP/SDP packet controls have trigger, pending, deadline-missed, double-buffer, and line-number fields. Incorrect masks can cause missed infoframes, stale metadata, one-shot packets that never fire, or packet updates at the wrong scanline.
- Reset, reset-done, overflow, pending, clear, and interrupt-status fields require correct access semantics in the caller. This header gives only bit positions, so consumers must preserve write-one-to-clear, self-clear, and poll timing rules from the hardware model.
- DP DPHY VC-rate and slot-allocation-table fields are bandwidth critical. Bad masks can break MST-style allocation, high-bandwidth modes, eDP ASSR, ALPM wake/sleep, panel replay, or symbol-rate accounting.
- MPCC blend and routing fields are multi-plane sensitive. Errors may only appear with certain plane counts, alpha modes, stereo modes, OPP mappings, or background formats.
- OGAM LUT and RAM A/B region fields are dense and repeated. A single wrong mask can distort color, break bank switching, corrupt only one color channel, or affect only instance 0, 1, or 2.
- Gamut-remap coefficient banks rely on paired 16-bit fields and active/current mode bits. Misprogramming can cause color matrix errors that are visible only under specific color-management configurations.
- Memory-power fields for VPG, stream encoder, MPCC OGAM, and related blocks can produce timing-dependent failures if consumers write them while a block is active or read status while clocks are gated.

## Test Signals

Useful validation signals include:

- Build AMDGPU display with DCN 4.2 enabled. Missing or renamed macros should fail in HPO DP, MPC/MPCC, VPG/APG/DME, color-management, DMUB, IRQ, or resource-table compilation.
- Mechanically compare this shift/mask range against the matching `dcn_4_2_0_offset.h` range and AMD's register database so each consumed register has matching address and field metadata.
- Validate HPO DP output path 3 with modeset, stream enable/disable, link training, high-bandwidth modes, MST or VC allocation where supported, eDP ASSR, panel replay, ALPM sleep/wake, suspend/resume, and GPU reset.
- Exercise generic packet flows: infoframes/SDPs, audio SDP, metadata packets, ISRC indexed writes, immediate and frame update requests, one-shot triggers, continuous transmission, pending/deadline status, and conflict-clear behavior.
- Exercise DP diagnostics: video CRC enable/results/status, symbol counts, DPHY error status, test patterns, PRBS/custom pattern programming, and FIFO overflow status.
- Exercise MPCC instances 0-3 with single-plane and multi-plane composition, alpha blending, global gain/alpha, top/bottom selection, OPP routing, stereo mode, background color, update locks, and memory-power transitions.
- Exercise OGAM instances 0-2 with LUT index/data access, RAM A/B PWL loads, region table programming, mode/current status polling, bank switching, gamut-remap coefficient format, and A/B matrix coefficient programming.
- Include reset and power-management scenarios: hotplug, atomic modeset, suspend/resume, display-engine reset, GPU reset, clock gating, and memory low-power transitions. Expected signals are no stuck pending bits, no unexpected CRC/overflow/error status, stable link training, and visually correct color output.

## Cross-Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not attempt a final per-file synthesis for `dcn_4_2_0_sh_mask.h`; the merge/reconciliation lane should combine this with adjacent chunks. The previous chunk is needed for the start of `VPG8_VPG_GSP_IMMEDIATE_UPDATE_CTRL`, and the next chunk is needed for the rest of `MPCC_OGAM2` after `MPCC_OGAM2_MPCC_OGAM_RAMA_REGION_6_7`.

### subset-b-002241: lines 57275-59767

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 57275-59767

## Purpose

This chunk is a generated AMD DCN 4.2.0 register shift/mask header slice. It contains no executable C code; it exposes preprocessor constants that describe bit positions and masks for display-controller MMIO register fields.

The requested range contains 2,493 lines. It starts in the middle of the `MPCC_OGAM2` output-gamma block, covers the full `MPCC_OGAM3` output-gamma block, covers `MPC_OUT0` through `MPC_OUT3` output mux, denorm, and output CSC fields, covers complete `MPC_RMCM0` and almost-complete `MPC_RMCM1` reusable/movable color-management fields, and ends at the beginning of `DC_PERFMON22` performance-counter state fields. The chunk boundaries are mechanical: earlier `MPCC_OGAM2` control/RAMA fields are in the previous chunk, and most `DC_PERFMON22` fields continue in the next chunk.

Although this file is under a local `ceph-client` source mirror, this range is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct register accesses in this range. The API surface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field within its register.

The main register-field families in this chunk are:

- `MPCC_OGAM2`: tail of output gamma instance 2, including RAMA region descriptors 6-33, all RAMB start/end/offset/region descriptors, and MPCC gamut remap mode/format plus A/B coefficient banks.
- `MPCC_OGAM3`: complete output gamma instance 3, including mode/select/PWL disable/current status, LUT index/data/control, per-channel RAMA and RAMB segmented PWL programming, offsets, and gamut remap coefficient banks.
- `MPC_OUT0` through `MPC_OUT3`: output mux selection/status, output rate/flow-control fields, denormalization mode and clamp bounds, and per-output CSC mode plus 3x4 coefficient matrices for A/B banks.
- `MPC_OCSC_TEST_DEBUG_INDEX` and `MPC_OCSC_TEST_DEBUG_DATA`: debug index/data window for output CSC diagnostics.
- `MPC_RMCM0` and `MPC_RMCM1`: shaper LUT control, RGB offsets/scales, shaper LUT index/data/write enable, shaper RAMA/RAMB region descriptors, 3D LUT mode/index/data/read-write controls, 30-bit data path, output normalization/bias/scale, gamut remap mode/format/coefficient banks, memory power controls, fast-load select/status, and top-level RMCM control.
- `DC_PERFMON22`: beginning of a display performance monitor block, covering `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, and the first `PERFCOUNTER_STATE` field.

The field names map directly into DCN 4.2 register-table construction. In particular, `MPC_RMCM0_*` names are consumed by `MPC_COMMON_MASK_SH_LIST_DCN42()` in `display/dc/mpc/dcn42/dcn42_mpc.h` and replicated for both RMCM instances by `MPC_RMCM_REG_LIST_DCN42(0/1)` in `display/dc/resource/dcn42/dcn42_resource.c`.

## Control Flow

This header has no runtime control flow. Its constants participate in compile-time table initialization:

1. DCN 4.2 display code includes `dcn_4_2_0_offset.h` and this matching `dcn_4_2_0_sh_mask.h`.
2. Resource construction macros bind register offsets, shifts, and masks into typed tables such as `dcn42_mpc_registers`, `dcn42_mpc_shift`, and `dcn42_mpc_mask`.
3. Runtime MPC code accesses those tables through AMD display register helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_GET_2`, `REG_GET_3`, and `REG_GET_4`.
4. Higher-level color-management paths program output gamma, gamut remap, output CSC, RMCM shaper LUT, RMCM 3D LUT, fast-load selection, and memory power by field name, while this file supplies only bit layout.

Programming order is not encoded here. Sequencing for LUT bank selection, memory power, clock ungating, fast load, modeset synchronization, debug reads, and perfmon sampling is controlled by driver code and hardware rules outside this generated header.

## State And Persistence Behavior

The file stores no software state and persists nothing itself. It describes hardware state fields that generally remain in registers until explicitly reprogrammed or reset by modeset, plane detach/attach, color-management updates, suspend/resume, power gating, GPU reset, or ASIC reset.

The chunk names several persistent display-pipeline states:

- MPCC output gamma state: active/current gamma mode, selected LUT bank, PWL disable, LUT host/read/write selection, per-channel segmented RAMA/RAMB PWL parameters, offsets, and gamut remap matrix bank state.
- MPC output state: output mux routing/status, denormalization mode, clamp windows, output rate and flow-control fields, and output CSC matrix selection and coefficients.
- RMCM state: shaper LUT mode/current mode, shaper PWL tables in RAMA/RAMB, 3D LUT mode/current mode and size, 3D LUT data/index/read/write controls, fast-load source selection and completion/underflow status, output bias/scale/norm factor, gamut remap matrices, and memory power force/disable/low-power/state bits.
- Perfmon state at the end of the chunk: event selection, counted-value selection, increment mode, hardware control/start/stop selectors, restart/interrupt enables, active/off status, and selected counter state.

Side effects are hardware-defined. Some status/current fields are readback-only or latched. Some interrupt/status bits may require write-one-to-clear semantics in adjacent perfmon registers. Memory-power and fast-load fields are especially sequencing-sensitive because the driver must power and clock memories before programming their contents.

## Dependencies And Integration Points

This generated shift/mask header must stay synchronized with the companion offset header and AMD's DCN 4.2 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` provides matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` includes the generated DCN 4.2 headers, initializes `mpc_shift`/`mpc_mask`, and registers two RMCM instances with `MPC_RMCM_REG_LIST_DCN42(0)` and `(1)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.h` defines `MPC_COMMON_MASK_SH_LIST_DCN42()`, which consumes the MPCC OGAM, MPC output, and RMCM shift/mask names represented here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.c` programs RMCM shaper LUTs, 3D LUT size/bank/bit-depth/output bias/scale, fast-load select, memory power, and RMCM readback state through these field tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h` and older MPC headers show the predecessor macro patterns for MPCC OGAM and output CSC fields; DCN 4.2 extends this path with RMCM fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h` supplies related MPCC OGAM enum values such as LUT bank selection, LUT config mode, PWL disable, read color selection, and segment count values.

Behaviorally, this range is on the user-visible color pipeline: plane composition feeds MPCC/MPC, then output gamma, gamut remap, output CSC/denorm, and RMCM shaper/3D LUT transformations affect final pixels before scanout or writeback. The perfmon fields at the end are diagnostic instrumentation rather than image-processing state.

## Risks And Edge Cases

- The constants are untyped preprocessor macros. A bad mask or shift can compile cleanly while silently programming the wrong register bits.
- The file is generated. Manual edits risk divergence from the authoritative hardware register database, the offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. This range begins after `MPCC_OGAM2` control and early RAMA fields, and stops inside `DC_PERFMON22_PERFCOUNTER_STATE`; adjacent chunk reports must be merged before making whole-block claims.
- Repeated instances are copy-sensitive. `MPCC_OGAM2`, `MPCC_OGAM3`, `MPC_OUT0-3`, and `MPC_RMCM0-1` are structurally similar, so a generator or paste error can affect only one pipe, one output, or one RMCM instance.
- LUT programming is banked and mode/current-mode based. Wrong `*_MODE`, `*_SELECT`, `*_RAM_SEL`, or `*_MODE_CURRENT` fields can display stale LUT contents, switch to the wrong bank, or report the wrong active bank.
- PWL region masks encode offsets and segment counts. Bad RAMA/RAMB region masks can make gamma/shaper curves non-monotonic, truncate a region, overflow the intended LUT span, or produce visible banding.
- Per-channel fields are easy to alias. Swapping R/G/B offset, scale, start/end, or coefficient masks can create color casts that only appear under color-managed modes.
- Matrix coefficients use paired 16-bit fields and A/B banks. Incorrect masks can corrupt only half of a coefficient register or only the inactive/active bank being flipped during modeset.
- RMCM memory-power fields gate shaper and 3D LUT memories. Programming LUT RAM while power-disabled or clock-gated can lead to lost writes, underflow status, or inconsistent readback.
- RMCM fast-load fields depend on `hubp_index`, LUT size, bit-depth, bias/scale, and bank selection. Wrong masks can connect fast load to the wrong HUBP, leave it disconnected, or misreport soft/hard underflow.
- `MPC_RMCM_CNTL` appears to gate/select RMCM participation. A wrong mask can disable the color module for a pipe or route the wrong MPC/RMCM path.
- Perfmon fields include event selection, run enable, stop/count-off controls, restart, interrupt enable, active state, and counter selector bits. Incorrect masks can make performance diagnostics misleading or cause stuck perfmon interrupts when adjacent status/ack fields are used.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display/color tests:

- Build DCN 4.2 AMDGPU display support. Missing or renamed macros should surface in `dcn42_resource.c`, `dcn42_mpc.h`, and `dcn42_mpc.c`.
- Mechanically compare this range with the authoritative DCN 4.2 register database and verify every `_MASK` has the expected paired `__SHIFT`.
- Cross-check each register family against `dcn_4_2_0_offset.h`, especially instance-specific offsets for `MPCC_OGAM2/3`, `MPC_OUT0-3`, `MPC_RMCM0/1`, and `DC_PERFMON22`.
- Run repeated-instance consistency checks for `MPCC_OGAM2` versus `MPCC_OGAM3`, all `MPC_OUT` instances, and `MPC_RMCM0` versus `MPC_RMCM1`, while allowing intentional instance prefixes and chunk-boundary omissions.
- Exercise color-managed modes that program MPCC output gamma, gamut remap, output CSC, and denorm/clamp. Expected signals are correct color transforms, no channel swaps, no visible banding, and expected register readbacks.
- Test both LUT banks and mode/current-mode readback for output gamma and RMCM shaper/3D LUT paths. Bank flips should not show stale or partially programmed tables.
- Exercise RMCM shaper and 3D LUT fast-load on both RMCM instances, including 17x17x17 and 33x33x33-equivalent size selections where supported, 10-bit and non-10-bit data paths, and different HUBP sources. Watch `*_FL_DONE`, `*_FL_SOFT_UNDERFLOW`, and `*_FL_HARD_UNDERFLOW`.
- Exercise suspend/resume, rapid modesets, plane disable/enable, and memory-low-power debug settings while RMCM and OGAM LUTs are enabled. Expected signals are stable color state after resume and no lost LUT programming.
- Use debugfs or driver state dumps that call `mpc42_read_mpcc_state()` to verify RMCM fields read back coherently for instances 0 and 1.
- If perfmon support is exposed for this block, configure `DC_PERFMON22` counters for known events and confirm active/state/readback behavior matches expected display activity without spurious interrupts.

## Cross-Chunk Notes

The previous chunk should cover the beginning of `MPCC_OGAM2`, including its control, LUT index/data/control, RAMA start/end/offset, and RAMA regions 0-5. This chunk covers the rest of `MPCC_OGAM2`, all `MPCC_OGAM3`, output CSC/denorm/mux, and RMCM0/1 up to `MPC_RMCM1_MPC_RMCM_CNTL`. The next chunk should continue `DC_PERFMON22_PERFCOUNTER_STATE` and the remaining perfmon control/value/readback fields before moving into later address blocks.

### subset-b-002242: lines 59768-62225

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 59768-62225

## Scope And Purpose

This chunk is part of the generated DCN 4.2.0 register shift/mask header used by the AMD display driver. It contains only preprocessor constants, not executable control flow. The constants define bit positions and masks for hardware register fields so the display code can issue safe read-modify-write operations through `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and the `SF(...)` register-table macros.

The range starts at the tail of the `DC_PERFMON22` performance monitor block, then covers the `dce_dc_mpc_mpcc_mcm0_dispdec` and `dce_dc_mpc_mpcc_mcm1_dispdec` address blocks for MPCC movable color-management hardware, and ends partway through `dce_dc_mpc_mpcc_mcm2_dispdec` shaper RAM A region definitions. The MPCC MCM blocks describe color pipeline controls behind the MPC/MPCC path: shaper LUTs, 3D LUTs, post 1D LUTs, two gamut remap matrices, LUT memory power control, and 3D LUT fast-load status.

Because this is a generated `*_sh_mask.h` file, the semantic contract is the exact pairing of every `__SHIFT` value with its corresponding `_MASK` value and the exact register/field names consumed by the DCN42 object headers. A mismatch here does not fail locally in this header; it causes later register writes to touch the wrong hardware bits.

## Important Register Families

`DC_PERFMON22_*` fields complete one display-core performance monitor instance. The visible registers include:

- `DC_PERFMON22_PERFCOUNTER_STATE`, with eight packed counter-state fields and state-select bits.
- `DC_PERFMON22_PERFMON_CNTL` and `DC_PERFMON22_PERFMON_CNTL2`, controlling monitor state, report count, count-off interrupt enable/status/ack, clock enable, run-enable start/stop selectors, and interrupt type.
- `DC_PERFMON22_PERFMON_CVALUE_INT_MISC`, packing per-counter interrupt status and ack bits plus the high bits of the current value.
- `DC_PERFMON22_PERFMON_CVALUE_LOW`, `DC_PERFMON22_PERFMON_HI`, and `DC_PERFMON22_PERFMON_LOW`, exposing counter value and read-selection fields.

`MPCC_MCM0_*` and `MPCC_MCM1_*` are full repeated MPCC MCM instances. Each instance includes the same broad field groups:

- Shaper control and LUT programming: `MPCC_MCM_SHAPER_LUT_MODE`, current mode, per-channel offsets/scales, LUT index/data, write color mask, RAM select, RAM A/B start/end controls, and RAM A/B region descriptors.
- `MPCC_MCM_3DLUT_*`: mode, size, current mode, index, 24-bit and 30-bit data paths, read/write controls, output normalization, per-channel output offset/scale, fast-load source selection, and fast-load status bits for done, soft underflow, and hard underflow.
- `MPCC_MCM_1DLUT_*`: mode/select/current mode, LUT index/data/control, RAM A/B start and end controls, region slope/base/offset fields, and region descriptor pairs from region 0/1 through 32/33.
- First and second gamut remap controls: coefficient format, mode/current mode, and packed matrix coefficients `C11` through `C34` for banks A and B.
- `MPCC_MCM_MEM_PWR_CTRL`: force, disable, low-power-mode, and power-state fields for shaper, 3DLUT, and 1DLUT memories.

`MPCC_MCM2_*` begins another repeated instance, but this chunk only covers the shaper setup through `MPCC_MCM2_MPCC_MCM_SHAPER_RAMA_REGION_26_27`. Its remaining RAM A fields, RAM B fields, 3DLUT, 1DLUT, gamut remap, and memory-power definitions fall outside this chunk.

## APIs, Types, And Integration

The header does not define C types or functions directly. Its API surface is the macro naming convention:

- `REGISTER__FIELD__SHIFT` gives the field shift used to position a value.
- `REGISTER__FIELD_MASK` gives the field mask used for extraction or read-modify-write preservation.

The main DCN42 integration point is `drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.h`. `MPC_COMMON_MASK_SH_LIST_DCN42(mask_sh)` references many fields from this chunk through `SF(MPCC_MCM0_..., FIELD, mask_sh)`. `drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` then instantiates:

- `static const struct dcn42_mpc_shift mpc_shift = { MPC_COMMON_MASK_SH_LIST_DCN42(__SHIFT) };`
- `static const struct dcn42_mpc_mask mpc_mask = { MPC_COMMON_MASK_SH_LIST_DCN42(_MASK) };`

At runtime, `dcn42_mpc_construct()` stores those tables in `struct dcn42_mpc`. MPC programming code then expands `FN(reg, field)` into `mpc42->mpc_shift->field` and `mpc42->mpc_mask->field`.

The actual programming paths are mostly in shared DCN32/DCN401 MPC code plus DCN42-specific RMCM code. Examples include shaper and post-1DLUT programming, 3DLUT programming, gamut remap programming, LUT fast-load setup, memory-power handling, and state readback. These paths depend on the generated macros in this chunk to address the right bits while writing `MPCC_MCM_*` registers.

The `DC_PERFMON22` definitions integrate with display performance-monitor and debug tooling through the same generated register model. This chunk provides field layout only; address constants live in `dcn_4_2_0_offset.h`, and enum values for performance events live in the SoC enum headers.

## Control Flow

There is no runtime control flow in this chunk. The effective flow is compile-time data generation:

1. The generated header exposes register-field shifts and masks.
2. DCN42 object headers collect selected fields into per-block shift and mask structs using `SF(...)`.
3. Resource construction binds register addresses, shifts, and masks into hardware objects.
4. Runtime display code calls register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, and `REG_WAIT`.
5. Those helpers combine the address from `*_offset.h` with shift/mask constants from this header to modify or read the intended field.

For the MCM color pipeline, the runtime sequence usually powers/ungates the relevant memory, selects a target RAM bank, writes index/data registers or matrix coefficient registers, switches mode/select fields, and later reads current-mode/status fields to confirm state. For 3DLUT fast load, the driver programs fast-load source selection and checks done/underflow status. For memory power, the driver writes disable/force/low-power-mode fields and may wait for power-state fields.

## State And Persistence Behavior

The header has no mutable state and performs no persistence. Persistence is entirely in hardware registers programmed through these definitions.

The fields in this chunk describe several hardware state classes:

- Performance monitor state: counter state, current values, interrupt status, interrupt ack, and monitor clock/run-enable controls.
- Active color-processing state: current shaper, 3DLUT, 1DLUT, and gamut-remap modes; selected LUT banks; coefficient formats; and selected fast-load source.
- LUT contents and region configuration: shaper/1DLUT RAM A/B region tables, LUT index/data ports, 3DLUT data ports, and output normalization/offset/scale fields.
- Power state: shaper, 3DLUT, and 1DLUT memory force/disable/low-power configuration plus readback state.

Many MCM registers are banked as RAM A/RAM B or matrix bank A/B. That banked layout lets software populate an inactive bank and flip a mode/select field after programming, reducing visible color-pipeline disruption. The generated masks must preserve that bank distinction precisely.

## Dependencies

This chunk depends on the generated DCN 4.2.0 register-address header for register offsets and base indices. It also depends on the AMD display register-helper framework that interprets shift/mask pairs.

Important local consumers include:

- `drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.h`, which names the MPCC MCM fields included in `struct dcn42_mpc_shift` and `struct dcn42_mpc_mask`.
- `drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`, which includes `dcn_4_2_0_sh_mask.h`, instantiates the shift/mask tables, and constructs the MPC object.
- `drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.c`, which uses those tables for DCN42 RMCM and MPCC state handling.
- Shared MPC implementations under `drivers/gpu/drm/amd/display/dc/mpc/dcn32` and `dcn401`, which program shaper, 3DLUT, 1DLUT, gamut remap, fast-load, and memory-power paths through the same abstract field names.

The repeated `MPCC_MCM0`, `MPCC_MCM1`, and `MPCC_MCM2` prefixes encode hardware instances. Driver arrays indexed by `mpcc_id` assume register lists, offset lists, and shift/mask definitions remain aligned across those repeated instances.

## Risks And Edge Cases

Generated-header drift is the main risk. If a register name or field name changes here but the DCN42 `SF(...)` list is not updated, compilation fails. If a shift or mask value is wrong but the name still matches, compilation succeeds and hardware programming corrupts adjacent fields.

Partial instance coverage matters for chunking. This range contains full MCM0 and MCM1 definitions but only the beginning of MCM2. Any per-file synthesis must merge the following chunk before claiming complete MCM2 behavior.

Packed channel fields are easy to misuse. Several registers pack two fields into one word, such as G/B scale fields, 3DLUT data lanes, output offset/scale pairs, gamut coefficients, and region pairs. Incorrect masks can silently swap or truncate color values.

Bank-selection and current-mode fields are sensitive. The shaper, 1DLUT, 3DLUT, and gamut-remap paths use mode/current and select/current pairs to avoid switching to partially programmed RAM. Programming the wrong bank select or using a stale current-mode field can produce visible color corruption or a black screen.

Memory-power fields must stay consistent with programming sequences. The runtime code may force or disable MCM memories, then wait for power-state fields before programming or enabling a LUT. Bad masks in `MPCC_MCM_MEM_PWR_CTRL` can leave LUT RAM powered down, prevent low-power entry, or make readback diagnostics misleading.

3DLUT fast-load status includes done, soft-underflow, and hard-underflow bits. If these masks are wrong, fast-load workflows can falsely report success or miss underflow, leading to incomplete LUT contents being used.

Performance-monitor fields include write-ack interrupt bits and packed high/low counter values. Incorrect ack masks can fail to clear interrupts; incorrect high/low extraction can make debug counters unreliable.

## Test Signals

Build coverage should compile DCN42 display code with `dcn_4_2_0_sh_mask.h` included by `dcn42_resource.c`, `dcn42_mpc.h`, and related hardware object sources. A missing or renamed macro in this chunk should fail at the shift/mask table initializers.

Runtime validation should focus on hardware-visible color and state-readback paths:

- Program shaper LUTs on MPCC MCM0 and MCM1 with both RAM A and RAM B, then verify current mode/select readback and color output.
- Program 3DLUT in 24-bit and 30-bit modes, including output offset/scale, fast-load source selection, and fast-load done/underflow status.
- Program post 1DLUT RAM A/B region tables and LUT data, then verify region boundaries and per-channel writes.
- Exercise first and second gamut-remap matrices with bank A/B coefficients and confirm mode/current-mode readback.
- Toggle MCM memory power controls and check power-state readback, especially around LUT programming sequences.
- Read MPCC state through DCN42 debug/readback paths and confirm MCM state fields decode consistently.
- Use display CRC or visual test patterns to catch color-channel swaps, coefficient packing mistakes, truncated LUT data, and wrong bank selection.
- Exercise `DC_PERFMON22` counters and interrupt ack/status paths through display performance-monitor/debug tooling, checking counter value consistency and interrupt clearing.

Good regression symptoms to watch for are compile failures in `MPC_COMMON_MASK_SH_LIST_DCN42`, incorrect colors after applying LUTs or gamut remap, LUT fast-load underflow not reported, hangs while waiting for memory power state, unexpected power residency changes, and misleading MPCC/perfmon debug readouts.

## Cross-Chunk Notes

The preceding chunk contains the start of the `DC_PERFMON22` block, including at least `PERFCOUNTER_CNTL` and `PERFCOUNTER_CNTL2`. This chunk starts at `DC_PERFMON22_PERFCOUNTER_STATE`.

The following chunk is required for a complete `MPCC_MCM2` description. This chunk stops after `MPCC_MCM2_MPCC_MCM_SHAPER_RAMA_REGION_26_27`; later MCM2 shaper region definitions, RAM B definitions, 3DLUT/1DLUT/gamut-remap definitions, memory-power fields, and fast-load fields are outside this range.

### subset-b-002243: lines 62226-64689

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 62226-64689

## Purpose

This chunk is a generated AMD DCN 4.2.0 register shift/mask header slice. It contains no executable C logic; its public surface is a large set of preprocessor constants that map hardware register fields to bit positions (`__SHIFT`) and bit masks (`_MASK`) for DCN display MMIO programming.

The requested range starts in the middle of the `MPCC_MCM2_MPCC_MCM_SHAPER_RAMA_REGION_26_27` field list, completes the rest of MPCC MCM2 shaper/1DLUT/3DLUT/gamut-remap/memory-power/fast-load fields, contains a complete `dce_dc_mpc_mpcc_mcm3_dispdec` block for MPCC MCM3, covers global MPC configuration/status/CRC/update-lock/HUBP fast-load/DWB mux fields, and ends in the middle of `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1` for the first HPO HDMI timing-buffer encoder.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, callbacks, or direct MMIO accesses in this range. The API-like contract is the generated macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: field mask for extracting or updating that register field.

Important register-field families in this chunk include:

- `MPCC_MCM2_MPCC_MCM_SHAPER_*`: tail of shaper RAM A region metadata and complete RAM B start/end/region fields. These describe programmable piecewise shaper LUT region starts, ends, bases, LUT offsets, and segment counts for blue, green, and red channels.
- `MPCC_MCM2_MPCC_MCM_3DLUT_*`: 3D LUT mode, size/current mode, index/data writes, 30-bit data path, RAM selection, write-enable mask, read selection, output norm factor, output offsets/scales, fast-load select, and fast-load status.
- `MPCC_MCM2_MPCC_MCM_1DLUT_*`: 1D LUT mode/select/current state, host RAM selection, write/read color selection, RAM A/RAM B start slopes/bases/regions/offsets, and LUT data/index controls.
- `MPCC_MCM2_MPC_MCM_FIRST_GAMUT_REMAP_*` and `MPCC_MCM2_MPC_MCM_SECOND_GAMUT_REMAP_*`: coefficient format, remap mode/current mode, and 3x4 matrix coefficients split across A/B registers.
- `MPCC_MCM2_MPCC_MCM_MEM_PWR_CTRL`: low-power disable, force, and state fields for shaper, 3DLUT, and 1DLUT memories.
- `MPCC_MCM3_*`: the same MCM color-management surface for MPCC instance 3, starting at shaper control/offset/scale fields and continuing through shaper RAMs, 3DLUT, 1DLUT, first/second gamut remaps, memory power, and fast-load status.
- `MPC_CLOCK_CONTROL` and `MPC_SOFT_RESET`: MPC clock gate/test selections, disable controls, and soft-reset bits for shared MPC sub-blocks including mux, MPCC instances, memory power controller, CRC, and DWB mux paths.
- `MPC_CRC_*`: CRC enable, mode, stereo/interlace behavior, source selection, and AR/GB/result readback fields used for display validation/debug.
- `MPC_DPP_PENDING_STATUS` and `MPC_PENDING_STATUS_MISC`: per-DPP and miscellaneous pending-current flags for DPP, OPP, DWB, HUBP, ODM, MPC output mux, cursor, and configuration updates.
- `ADR_CFG_CUR_VUPDATE_LOCK_SET[0-3]`, `ADR_CFG_VUPDATE_LOCK_SET[0-3]`, `ADR_VUPDATE_LOCK_SET[0-3]`, `CFG_VUPDATE_LOCK_SET[0-3]`, and `CUR_VUPDATE_LOCK_SET[0-3]`: update-lock selectors for synchronizing address, configuration, cursor, and combined update domains.
- `HUBP[0-3]_3DLUT_FL_CONFIG` and `HUBP[0-3]_3DLUT_FL_BIAS_SCALE`: HUBP-side 3DLUT fast-load address, mode, format, bank select, finish, 10-bit enable, bias, and scale fields.
- `MPC_DWB0_MUX`: display writeback mux select and mux status fields.
- `HDMI_STREAM_ENC_*`: HPO HDMI stream encoder clock control, source/mux selection, clock-ramp adjuster FIFO status/control, and audio source/APG clock enable fields.
- `HDMI_TB_ENC_*`: HDMI timing-buffer encoder enable/reset, pixel format/deep color/DSC mode, packet limits, ACR packet control, VBI packet controls, GC AVMUTE/default phase state, and generic packet send/continuous/lock/line-reference fields for packet slots 0 through the beginning of slot 14.

## Control Flow

This header has no runtime control flow. It participates in compile-time construction of register access tables:

1. DCN42 resource code includes `dcn_4_2_0_offset.h` and this matching `dcn_4_2_0_sh_mask.h`.
2. Hardware-block headers define register-list and field-list macros such as `MPC_REG_LIST_DCN42`, `MPC_COMMON_MASK_SH_LIST_DCN42`, `SE_COMMON_MASK_SH_LIST_DCN42`, and HPO encoder list macros.
3. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` expands offset macros (`SR`, `SRI`, `SR_ARR`, etc.) into register-address structs and expands field macros (`SF`, `SE_SF`, etc.) into shift/mask structs.
4. Runtime objects such as `struct dcn42_mpc`, `struct dcn10_stream_encoder`, and HPO encoder objects receive those register and shift/mask tables during construction.
5. Driver functions then call `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`; those helper macros use the tables generated from this header to update MMIO bitfields.

The sequencing rules for powering LUT memories, programming shaper/3DLUT data, switching gamut-remap modes, waiting for update-pending bits, running CRC, enabling HDMI stream clocks, and sending HDMI packets live in C source files and hardware documentation, not in this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields that are programmed or sampled by the display driver:

- MPCC MCM color state: shaper LUT RAM selection and region tables, 3DLUT mode/size/bank/data, 1DLUT mode/bank/data, gamut-remap matrices, current-mode readbacks, and output bias/scale.
- MCM memory-power state: force/disable/low-power mode and state readback for shaper, 3DLUT, and 1DLUT SRAMs.
- MPC global state: clock gating, soft resets, host-read mode, DPP and miscellaneous update-pending status, DWB mux selection, update-lock routing, and CRC configuration/results.
- HUBP fast-load state: which HUBP feeds 3DLUT fast load, the address/mode/format/bank, completion indication, 10-bit enable, bias, and scale.
- HDMI stream/timing-buffer state: stream encoder clock/reset/active status, ramp-adjuster FIFO thresholds and error status, audio muxing and APG clocking, deep-color/pixel-encoding/DSC mode, ACR and VBI packet scheduling, AVMUTE/default phase, and generic packet slot controls.

Persistence and side effects are hardware-defined. Many configuration fields remain until modeset, plane update, color-management update, stream disable, suspend/resume, power-gating, or GPU reset rewrites them. Status fields may be latched, self-clearing, write-one-to-clear, or valid only while the relevant display clock/power domain is enabled. This chunk only supplies bit positions and masks; it does not encode those access semantics.

## Dependencies And Integration Points

This file must stay synchronized with AMD's DCN 4.2.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` supplies the matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` includes this header and creates DCN42 resource objects. In this chunk's area it builds `mpc_regs`, `mpc_shift`, and `mpc_mask` from `MPC_REG_LIST_DCN42` and `MPC_COMMON_MASK_SH_LIST_DCN42`, and it builds stream-encoder shift/mask tables from `SE_COMMON_MASK_SH_LIST_DCN42`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.h` lists the DCN42 MPC/MCM fields consumed from this generated header, including MPCC MCM shaper, 3DLUT, 1DLUT, gamut-remap, fast-load, memory-power, DWB mux, update-lock, and CRC fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.c` programs color-management and MPC fields through these masks. Examples include MCM shaper LUT setup, RAM A/B region programming, 3DLUT fast-load selection, bit-depth programming, bias/scale programming, memory power toggling with `REG_WAIT`, and DWB mux/color-path updates.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_color.c` and plane/stream update paths feed DRM color state into DC plane/stream color structures that eventually cause the MPC/MCM programming using these fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_stream_encoder.h` and `.c` consume HDMI stream-encoder related masks for HDMI stream attributes, audio clock enable, info packets, generic packets, metadata packets, and DP/HDMI stream control. This chunk's `HDMI_STREAM_ENC_*` and `HDMI_TB_ENC_*` families are part of the newer HPO HDMI/FRL-facing register surface, while legacy DIG HDMI fields are also present elsewhere in the generated header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h` includes HPO FRL stream encoder register-list entries for `HDMI_STREAM_ENC_AUDIO_CONTROL`, `HDMI_TB_ENC_MEM_CTRL`, and `HDMI_FRL_ENC_MEM_CTRL`, tying nearby HPO HDMI register families into DCN42 resource initialization.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c` also includes the DCN42 offset and shift/mask headers for DMUB/DCN42 register access, though this particular range is mainly display color, MPC, and HDMI encoder metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h` provides enum values for many named fields in this range, including MPCC MCM 3DLUT modes, RAM selections, LUT segment counts, gamut-remap formats/modes, memory-power states, HUBP 3DLUT fast-load modes, MPC CRC modes/source selections, update-lock booleans, and HDMI stream/TB encoder field values.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift compiles cleanly and can corrupt one hardware bitfield at runtime.
- The file is generated. Manual edits risk divergence from AMD's register database, the matching offset header, firmware expectations, and silicon documentation.
- The source chunk boundaries are artificial. The first line is only the final mask from `MPCC_MCM2_MPCC_MCM_SHAPER_RAMA_REGION_26_27`, and the final line stops before all `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1` masks are present. Adjacent chunk research must be reconciled before making full-register claims.
- MPCC MCM and LUT programming is ordering-sensitive. Incorrect RAM-select, write-enable, index, region, or current-mode masks can produce bad color, stuck LUT updates, partial bank swaps, visible flicker, or invalid HDR/CTM/gamma behavior.
- Shaper and 1DLUT region fields repeat across 34 regions and RGB channels. Copy/generator mistakes can affect only one color, region pair, RAM bank, or MPCC instance, making failures mode- and content-dependent.
- 3DLUT fast-load fields cross MPCC/MPC and HUBP surfaces. Wrong source selection, address, bank, completion, format, 10-bit, bias, or scale masks can load the wrong LUT data or mark an incomplete DMA-style fast load as usable.
- Memory-power fields interact with clock gating and register programming. Incorrect force/disable/state masks can program powered-down SRAM, fail `REG_WAIT` polling, leave memory powered unnecessarily, or trigger underflow/error states.
- MPC pending-status and update-lock fields affect atomic update sequencing. Incorrect masks can make the driver believe an update has landed when it has not, or can keep updates locked/pending indefinitely.
- CRC field errors are often diagnostic-only but high impact for validation. Bad CRC source/mode/result masks can break display test automation, self-tests, and hardware debug without affecting ordinary display output.
- `MPC_SOFT_RESET` and clock-control masks are broad. A wrong bit can reset or ungate/gate an unrelated MPC sub-block, producing blank display, DWB failures, stale color state, or power regressions.
- HDMI stream encoder and timing-buffer fields are packet- and timing-sensitive. Incorrect deep-color, pixel-encoding, DSC mode, ACR, GC, AVMUTE, VBI, generic packet, or FIFO threshold/status masks can cause bad HDMI timing, missing infoframes, audio clock drift, repeated packet errors, or sink compatibility failures.
- HPO HDMI/FRL register naming differs from older DIG HDMI paths. Code that accidentally mixes legacy `DIG0_HDMI_*` fields with `HDMI_STREAM_ENC_*` or `HDMI_TB_ENC_*` fields can compile if names exist elsewhere but target the wrong hardware block.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display behavior:

- Build AMDGPU DCN42 display support. Missing or renamed macros should surface in `dcn42_resource.c`, `dcn42_mpc.h`, `dcn42_mpc.c`, `dcn42_dio_stream_encoder.h`, `dcn42_dio_stream_encoder.c`, and HPO/FRL resource initialization paths.
- Mechanically compare this range against the authoritative DCN 4.2.0 register-field database. Every `_MASK` should have the expected paired `__SHIFT` and every register in the chunk should have a matching offset/base-index entry in `dcn_4_2_0_offset.h`.
- Run repeated-instance checks across `MPCC_MCM2` and `MPCC_MCM3`, including shaper RAM A/B regions `0_1` through `32_33`, 1DLUT RAM A/B regions, 3DLUT controls, gamut-remap coefficient registers, memory-power fields, and fast-load fields. Allow the intentional partial boundary at `MPCC_MCM2_SHAPER_RAMA_REGION_26_27`.
- Exercise DRM color-management paths that program plane/stream CTM, shaper LUTs, 1D LUTs, 3D LUTs, HDR transfer functions, and gamut remap. Expected signals are correct visual output, successful modesets, no color banding/regression, and stable bank switching.
- Test 3DLUT fast-load with each HUBP/MPCC combination used by DCN42. Expected signals include fast-load completion, no soft/hard underflow status, correct bias/scale, and expected output after bank swap.
- Validate suspend/resume, GPU reset recovery, and power-management paths with color-management enabled. Expected signals are memory-power state readbacks that settle, no `REG_WAIT` timeouts, and no lost LUT state after reprogramming.
- Exercise MPC CRC setup/readback in one-shot and continuous modes over DPP/OPP/DWB-related sources where supported. Expected signals are stable, repeatable CRC results and correct enable/source/mode behavior.
- Exercise atomic plane updates, cursor movement, DWB capture, and multi-pipe modes while watching pending-status/update-lock behavior. Expected signals are no stuck pending bits, no stale cursor/address/config updates, and correct DWB mux output.
- Exercise HDMI 2.x/FRL-capable and non-FRL sink modes across deep color, RGB/YCbCr encodings, DSC on/off, audio enabled/disabled, HDR/AVI/vendor/SPD/infoframe updates, AVMUTE transitions, hotplug, and modesets. Expected signals are stable video, correct packet delivery, no ACR/audio drift, and no ramp-adjuster FIFO overflow/underflow statuses.

## Cross-Chunk Notes

The previous chunk owns most of `MPCC_MCM2_MPCC_MCM_SHAPER_RAMA_REGION_26_27`; this chunk begins with only the `REGION27_NUM_SEGMENTS_MASK` tail and then continues from `REGION_28_29`. The next chunk should continue `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1` after the `HDMI_GENERIC10_CONT_MASK` line and likely cover the remaining HPO HDMI packet/encoder registers. The final per-file research document should merge these boundaries before summarizing full MPCC MCM2 or HDMI TB encoder register coverage.

### subset-b-002244: lines 64690-67202

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 64690-67202

## Purpose

This chunk is generated AMD DCN 4.2.0 register-field metadata. It contains no executable C logic; it exports C preprocessor constants that describe bit shifts and masks for MMIO register fields. AMDGPU display code pairs these definitions with `dcn_4_2_0_offset.h` and register helper macros to pack, update, and read individual fields without hard-coding bit positions.

The range covers the tail of HDMI transmitter packet/audio/control definitions, HPO HDMI stream/link/FRL encoder support blocks, HPO top clock/performance controls, ABM backlight and adaptive-brightness blocks for instances 0 through 3, DPIA MU and DPIA glue/performance-counter fields, the Azalia/HDA controller command transport block, endpoint immediate-command windows, and output stream descriptors for Azalia streams 0 through the beginning of stream 6. It starts mid-register in `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1` and ends mid-register in `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT`; both partial boundaries must be reconciled with adjacent chunks.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, callbacks, or direct MMIO operations in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for isolating or updating the field.
- `// addressBlock:` comments group the generated definitions by hardware block; they are not C syntax, but they preserve the register-database layout for humans and tools.

This line range contains 2,091 `#define` lines: 1,034 shift macros and 1,057 mask macros. Major register families are:

- `HDMI_TB_ENC_*`: HDMI transmitter generic-packet controls, immediate-send and pending bits, per-packet line selection/EMP flags, double-buffer pending/disable status, ACR CTS/N programming and status for 32/44.1/48 kHz families, buffer prefill and memory-power controls, metadata packet control, active/blank timing fields, CRC configuration/result fields, EESS encryption control, borrow mode, and input FIFO error status.
- `APG9_*`, `VPG9_*`, and `DME9_*`: HPO HDMI stream encoder audio packet generator, video packet generator, and dynamic metadata engine fields. These include generic packet byte/index windows, frame and immediate update controls for generic packets 0-14, lock/conflict status, ISRC data windows, metadata requestor selection, engine enable, double-buffer state, missed-transmission flags, and memory-power controls.
- `HDMI_LINK_ENC_*` and `HDMI_FRL_ENC_*`: HDMI link encoder enable/reset/clock fields plus FRL lane count, link training, scrambler disable, per-lane training pattern, jitter-threshold, meter-buffer, and memory-power fields.
- `HPO_TOP_*`, `DP_STREAM_MAPPER_CONTROL*`, and `DC_PERFMON23_*`: top-level HPO clock enables/status for HDMI/FRL/DP stream and link encoders, stream mapping controls, and HPO performance-monitor counter selection, state, compare/increment interrupt setup, and counter readback fields.
- `ABM0_*` through `ABM3_*`: four adaptive backlight management instances. Each instance defines PWM ambient/user/target/current/final/minimum levels, ABM/PWM control and update-rate fields, ABM enable/bypass, IPCSC coefficient selection, ACE PWL index/data/lock fields, missed-frame/read-progress status, histogram and luma-stat controls, luma sums/min/max/pixel counts, threshold/count registers, sample rates, histogram bin shift/index/result windows, and the backlight master lock.
- `DPIA_MU_*`, `DPIA_GLUE_CTRL`, and `DPIA_PERF_COUNT_*`: USB4/DPIA message-unit clocks, per-port clock/reset controls for ports 0-3, TPI credit/status fields, per-port and local interrupt status/masks/acknowledgements, RBBMIF timeout and invalid-access status, microsecond reference divider, hidden-port status, glue debug bus selectors, six performance-counter controls, counter index/data, and spare bits.
- `GLOBAL_CAPABILITIES`, version, payload capability, global control/status, wake/state-change, interrupt control/status, wall clock, stream synchronization, CORB/RIRB, immediate command, and DMA position fields: the Azalia/HDA controller view of stream counts, reset/accept-unsolicited controls, codec wake/status bits, per-stream interrupt masks/status, stream sync bits, command output ring and response input ring base pointers/pointers/control/status/sizes, immediate command output/data/index/response/status, DMA position base addresses, and wall-clock alias.
- `AZENDPOINT1_*`, `AZINPUTENDPOINT1_*`, and `AZROOT1_*`: small endpoint/root immediate command data/index windows.
- `AZSTREAM0_1_*` through `AZSTREAM6_1_*`: output stream descriptor control/status, link position, cyclic buffer length, last valid index, FIFO size, format, buffer descriptor list lower/upper base address, and position alias fields. The stream 6 format register is only partially included in this chunk.

## Control Flow

This header has no local control flow. Runtime sequencing is supplied by AMDGPU display and audio code:

1. DCN 4.2 components include `dcn_4_2_0_offset.h` and this shift/mask header.
2. Resource, IRQ, clock, GPIO, DMUB, link, audio, ABM, and diagnostics code token-pastes symbolic register/field names into register tables and helper calls.
3. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, and indexed variants to touch the fields described here.
4. The numeric masks and shifts determine which bits are read or written while programming HDMI packets and FRL training, sending metadata, enabling HPO clocks, collecting perf counters, controlling ABM/backlight state, routing DPIA/USB4 events, handling HDA command rings, and starting/stopping audio stream DMA.

The macros do not encode ordering constraints. Consumers must still follow hardware sequencing for generic-packet double buffering, immediate-send pending polling, metadata DB handoff, FRL/link training, memory power transitions, ABM histogram/luma-stat latching, DPIA interrupt acknowledgement, CORB/RIRB setup, immediate command busy/result-valid polling, and HDA stream reset/run programming.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware-backed state:

- HDMI/HPO state includes packet scheduling, immediate packet pending bits, line references, ACR CTS/N values and readbacks, metadata enable/missed flags, buffer levels, memory power state, CRC result state, link/FRL enable/training/scrambler state, and clock-on status.
- ABM state includes PWM input/output levels, automatic brightness controls, ACE PWL programming, missed-frame/read-progress flags, histogram bins/results, luma statistics, sample rates, and master-lock state for each of four instances.
- DPIA state includes per-port clock/reset control, TPI credit counts, interrupt and acknowledgement state, timeout and invalid-access diagnostics, port hidden-status bits, debug bus selection, and performance-counter values.
- Azalia controller state includes global capability and reset/status bits, wake/status/interrupt masks, stream synchronization, wall-clock counter, CORB/RIRB DMA ring base addresses/pointers/control/status/sizes, immediate command windows, and DMA position buffer base addresses.
- Azalia stream state includes stream reset/run, interrupt enables and sticky status bits, FIFO ready/error, traffic priority, stream number, DMA position, cyclic-buffer length, last valid BDL index, format fields, BDL base address, and position alias readback.

Persistence is hardware-defined. Configuration fields typically remain until modeset, audio reconfiguration, power gating, suspend/resume, GPU reset, or driver reinitialization. Pending, missed, busy, interrupt, reset, FIFO-ready, error, timeout, read-progress, status-clear, and acknowledgement fields may be transient, sticky, self-clearing, write-one-to-clear, read-only, or only valid while their clock and power domains are active. This generated header does not express access type, volatility, reset values, or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 4.2.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which provides matching register offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`, which includes this header for DCN 4.2 resource/register-table construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`, which includes the generated offset and shift/mask headers for DCN 4.2 DMUB register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c`, which includes this header for DCN 4.2 interrupt table definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, which includes this header for DCN 4.2 clock-manager register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c`, which include this header for GPIO/HPD/AUX translation on DCN 4.2 hardware.
- Shared display code for ABM/backlight, HDMI/HPO packet generation, FRL/link training, DPIA/USB4 routing, HDA/Azalia audio, perfmon diagnostics, and register dump/debug paths.

The integration contract is mostly macro spelling plus numeric bit layout. Missing or renamed macros usually fail at compile time through token-pasted register tables. Incorrect numeric values are more dangerous because the build can succeed while runtime code reads or writes the wrong hardware bits.

## Risks And Edge Cases

- These are untyped preprocessor constants. A bad mask or shift can compile cleanly and still corrupt adjacent fields or read misleading status.
- The chunk is partial at both ends. `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1` begins in the previous chunk, and `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT` continues in the next chunk.
- Generic-packet and metadata fields have update, pending, lock, conflict, missed, DB taken, and DB disable bits. Using masks without the expected double-buffer or pending-bit sequencing can drop HDMI infoframes, metadata, ISRC, or other generic packets.
- HDMI ACR, timing, FRL, and link encoder fields are user-visible. Bad values can cause audio clock recovery errors, link-training failures, blank output, CRC mismatches, or unstable HDMI FRL behavior.
- Memory-power fields appear in HDMI buffer, APG, VPG, DME, and FRL blocks. Status bits may be invalid when clocks are gated, and force/disable bits can interact with broader power-management policy.
- ABM fields mix live statistics, latch/read-progress state, missed-frame flags, PWL programming, locks, and PWM levels. Wrong masks can create brightness jumps, stale histogram/luma reads, missed-frame loops, or incorrect backlight duty-cycle updates.
- DPIA MU fields cover clocks, resets, interrupts, TPI credits, timeout diagnostics, and per-port state. Incorrect interrupt masks or acknowledgements can hide USB4/DPIA port events, leave resets incomplete, or misdiagnose RBBMIF timeouts.
- HDA CORB/RIRB and DMA position fields include base-address alignment and unimplemented low bits. Treating them as unconstrained full-width addresses can break command transport or DMA position reporting.
- Immediate command status requires busy/result-valid handling. Masks alone do not provide the polling/timeout logic needed to avoid stale codec responses.
- Azalia stream descriptors contain reset/run bits, interrupt enable/status bits, error flags, FIFO-ready status, stream number, format, BDL base address, and cyclic-buffer metadata. Wrong fields can cause no audio, descriptor errors, FIFO errors, incorrect sample format, or DMA overrun/underrun behavior.
- Repeated ABM and AZSTREAM instances are copy-sensitive. Testing only ABM0 or stream0 can miss an instance-specific generated typo in ABM3 or stream6.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.2 hardware behavior:

- Build AMDGPU display support with DCN 4.2 enabled. DMUB, IRQ, clock-manager, GPIO, resource, audio, ABM, HDMI, DPIA, and diagnostics code should catch missing or renamed symbols.
- Mechanically verify every complete field in this range has both a `__SHIFT` and `_MASK` definition, allowing for the deliberate boundary exceptions in `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1` and `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT`.
- Diff this slice against AMD's authoritative DCN 4.2.0 register database and the paired `dcn_4_2_0_offset.h`; repeated ABM0-3 and AZSTREAM0-6 layouts should match the expected per-instance schema.
- Exercise HDMI output paths that program generic packets, metadata packets, ISRC data, ACR CTS/N, active/blank timing, CRC collection, EESS/AVMUTE-related behavior, and input FIFO error reporting.
- Exercise HPO HDMI FRL modes, including link encoder reset/enable, clock-on status, FRL lane count/training patterns, scrambler control, jitter/meter-buffer status, and FRL memory power transitions.
- Exercise ABM/backlight control on all exposed instances: PWM ambient/user/target/current/final/minimum levels, auto-update behavior, ACE PWL programming, histogram/luma-stat sampling, missed-frame clears, result-index/data reads, and master-lock behavior.
- Exercise DPIA/USB4 flows across ports 0-3 and interrupt/status coverage for ports 0-5: clock/reset sequencing, TPI credit counts, local interrupt acknowledge, timeout diagnostics, hidden-port state, glue debug selection, and performance counters.
- Exercise HDA/Azalia controller command paths: global reset, CORB/RIRB base pointer and size setup, write/read pointer handling, DMA enable/status, immediate command output/response polling, DMA position buffer programming, and wall-clock readback.
- Exercise output audio stream descriptors for streams 0-6: reset/run transitions, stream number assignment, interrupt enables/status clears, FIFO ready/error handling, cyclic buffer length, last valid index, BDL lower/upper base address alignment, link position alias, and format fields for channel count, bits per sample, divisor/multiple, and base rate.
- Monitor display/audio logs, DC traces, link-training traces, hotplug/audio events, register dumps, CRC results, ABM brightness behavior, RBBMIF timeout reports, FIFO/descriptor errors, and suspend/resume behavior as high-signal indicators of bad field metadata.

## Cross-Chunk Notes

The previous chunk owns the beginning of `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1`; this chunk starts with the masks for generic packet 8-14 in that register and then owns `HDMI_TB_ENC_GENERIC_PACKET_CONTROL2` and the following HDMI/HPO/ABM/DPIA/Azalia blocks through the first five fields of `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT`. The next chunk owns the remaining stream6 format masks, stream6 BDL pointer and position-alias fields, stream7 descriptors, and the closing guard. The merge lane should preserve this source path and line range and reconcile the boundary-split registers before producing the final per-file report.

### subset-b-002245: lines 67203-67286

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 67203-67286

## Purpose

This chunk is the final slice of the generated AMD DCN 4.2.0 register shift/mask header. It contains compile-time preprocessor constants for HDA audio stream descriptor fields, specifically the tail of `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_*` and the complete `AZSTREAM7_1_OUTPUT_STREAM_DESCRIPTOR_*` block, followed by the header guard close.

The macros describe bit positions and masks for DCN audio output stream descriptor registers. Runtime AMDGPU Display Core and DMUB code pairs these constants with the matching address definitions in `dcn_4_2_0_offset.h` and with register helper macros to reset, start, format, locate, and monitor HDMI/DisplayPort audio DMA streams. This source path is under a `ceph-client` mirror, but the content is AMDGPU display hardware metadata and does not implement distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, includes, callbacks, locks, allocation paths, or direct MMIO operations in this range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for encoding or decoding a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, preserve, clear, or update that field.

The `AZSTREAM6_1` portion starts mid-register at `OUTPUT_STREAM_DESCRIPTOR_FORMAT__BITS_PER_SAMPLE__SHIFT`; the preceding line outside this chunk contains `NUMBER_OF_CHANNELS__SHIFT`. This chunk then completes the `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT` masks and covers the BDL lower pointer, BDL upper pointer, and link-position alias fields.

The `AZSTREAM7_1` portion covers the full output stream descriptor set:

- `CONTROL_AND_STATUS`: stream reset/run controls, interrupt enables for completion/FIFO/descriptor errors, stripe control, traffic priority, stream number, completion status, FIFO error, descriptor error, and FIFO-ready status.
- `LINK_POSITION_IN_CURRENT_BUFFER`: 32-bit playback/DMA position within the current buffer.
- `CYCLIC_BUFFER_LENGTH`: 32-bit cyclic buffer length field.
- `LAST_VALID_INDEX`: 8-bit last valid Buffer Descriptor List index.
- `FIFO_SIZE`: 16-bit FIFO size.
- `FORMAT`: channel count, bits per sample, sample base divisor, sample base multiple, and sample base rate fields.
- `BDL_POINTER_LOWER_BASE_ADDRESS`: lower Buffer Descriptor List base address bits, with low 7 unimplemented/alignment bits.
- `BDL_POINTER_UPPER_BASE_ADDRESS`: upper 32 bits of the Buffer Descriptor List address.
- `LINK_POSITION_IN_CURRENT_BUFFER_ALIAS`: 32-bit alias for link position reporting.

## Control Flow

This header has no runtime control flow. It contributes constants to driver control paths that perform the actual sequence:

1. DCN 4.2.0 code includes `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`.
2. Register-list and helper macros token-paste register and field names into offset, mask, and shift tables.
3. Runtime audio/display code programs stream descriptor registers through read-modify-write helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, or related ASIC-specific wrappers.
4. Hardware consumes the programmed fields to reset or run the audio stream, select format and stream number, locate the cyclic DMA buffer through the BDL pointer, expose link position, and report completion/FIFO/descriptor status.

The macros do not encode required sequencing. Consumers must still follow HDA/audio stream programming order: quiesce or reset a stream before changing descriptors, program buffer length and BDL address with the required alignment, set format and stream number consistently with the audio engine, enable interrupts deliberately, start the stream, and handle status or error bits according to hardware semantics.

## State And Persistence Behavior

The header itself stores no state and persists nothing to disk. The underlying hardware registers represent live stream state:

- Control fields such as `STREAM_RESET`, `STREAM_RUN`, interrupt enables, stripe control, traffic priority, and stream number persist in the hardware register until changed, reset, power-gated, or reinitialized.
- Format fields persist as the active audio stream sample/channel encoding while the stream is configured.
- Buffer fields persist the DMA ring geometry: cyclic buffer length, last valid descriptor index, and lower/upper BDL base address.
- Link-position fields expose transient playback position counters or aliases.
- Completion, FIFO error, descriptor error, and FIFO-ready status fields are hardware state observations and may be sticky, transient, read-only, write-one-to-clear, or self-clearing depending on the register specification.

These generated masks do not indicate reset values, read/write permissions, clearing rules, or firmware ownership. Driver code must rely on the hardware specification and existing AMDGPU sequencing for safe access.

## Dependencies And Integration Points

The direct dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which defines the matching register addresses and base indices. In that offset header, `AZSTREAM6_1` descriptor registers map to the `0x4b7050` range with the alias at `0x4b7851`, while `AZSTREAM7_1` maps to the `0x4b7058` range with the alias at `0x4b7859`; both use base index `3`.

The same shift/mask header is included by DCN 4.2 integration code such as:

- `display/dmub/src/dmub_dcn42.c`, which initializes DMUB register access tables from generated offsets, shifts, and masks.
- `display/dc/irq/dcn42/irq_service_dcn42.c`, which depends on generated register metadata for DCN 4.2 interrupt programming.
- `display/dc/gpio/dcn42/hw_factory_dcn42.c` and `display/dc/gpio/dcn42/hw_translate_dcn42.c`, which include the same ASIC register headers for DCN 4.2 GPIO/HPD/AUX translation.
- DCN 4.2 resource construction and audio/display paths that rely on consistent generated register naming across repeated AZ stream instances.

The repeated `AZSTREAM6_1` and `AZSTREAM7_1` field layouts are an integration contract: generic audio stream setup code can reuse common descriptor logic only if each instance's field names, masks, shifts, and offset-header entries stay synchronized.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while programming the wrong hardware bits, causing silent audio stream failures.
- This chunk begins in the middle of `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT`; final per-register completeness checks must merge with the previous chunk before concluding whether the format field set is complete.
- BDL lower-address programming uses low 7 unimplemented bits and an address mask of `0xFFFFFF80L`. Callers must preserve alignment requirements and avoid treating the lower address as an arbitrary 32-bit value.
- `FIFO_SIZE` and `FORMAT` share the same offset in the companion header for each stream instance, so callers must use field masks carefully rather than whole-register writes that clobber unrelated fields.
- Completion, FIFO error, descriptor error, and FIFO-ready fields have status semantics that are not visible in this header. Misinterpreting status bits as normal writable fields can lose interrupts, fail to clear errors, or create repeated interrupts.
- Stream reset/run and descriptor programming are sequencing-sensitive. Updating BDL address, cyclic buffer length, last valid index, or format while a stream is running can race the audio DMA engine.
- The file is generated hardware ABI metadata. Manual edits can diverge from AMD's register database, silicon documentation, firmware assumptions, and the paired offset header.
- The final `#endif` means this is the end of the full header. Accidental edits near this boundary can break every translation unit including `dcn_4_2_0_sh_mask.h`.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU Display Core with DCN 4.2 support enabled. Missing or renamed macros should surface through compile failures in DMUB, IRQ, GPIO, resource, or audio/display register-table code.
- Mechanically compare all complete fields in this chunk against `dcn_4_2_0_offset.h` and AMD's generated DCN 4.2.0 register database; `AZSTREAM6_1` and `AZSTREAM7_1` should preserve the expected repeated descriptor layout.
- Check that every `__SHIFT` in this chunk has a corresponding `_MASK`, accounting for the known chunk-boundary exception where `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT__NUMBER_OF_CHANNELS__SHIFT` is immediately before line 67203.
- Exercise HDMI/DisplayPort audio playback paths that use the later stream descriptors, including stream start/stop, reset, format changes, channel-count changes, and suspend/resume reinitialization.
- Test DMA buffer setup with different cyclic buffer sizes and BDL lengths, including validation that lower address alignment and upper address handling work on systems using addresses above 4 GiB.
- Enable and observe completion, FIFO error, and descriptor error interrupt paths. Kernel logs, audio underruns, stream stalls, and repeated interrupt reports are high-signal indicators of bad status or enable masks.
- Read link-position registers during playback and compare monotonic/progress behavior against expected audio DMA movement.

## Cross-Chunk Notes

The previous chunk owns the beginning of the `AZSTREAM6_1` descriptor block, including `CONTROL_AND_STATUS`, link position, cyclic buffer length, last valid index, FIFO size, and the first `FORMAT` shift line. This chunk completes `AZSTREAM6_1`, owns all of `AZSTREAM7_1`, and closes `dcn_4_2_0_sh_mask.h`. The final per-file research document should reconcile this tail chunk with earlier chunks before making whole-file claims about all DCN 4.2.0 audio stream descriptor instances.
