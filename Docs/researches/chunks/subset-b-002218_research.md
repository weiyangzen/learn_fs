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
