# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 27133-29716

## Scope

This chunk covers a generated AMD DCN 3.0.3 shift/mask header region. It contains C preprocessor constants only: register grouping comments plus `__SHIFT` and `_MASK` `#define` entries. There are no C functions, structs, enums, storage objects, or direct MMIO operations in this slice.

The range starts in the middle of the HDA/Azalia RIRB base-address definitions, covers HDA response-ring, immediate-command, DMA-position, wall-clock, legacy VGA indexed-register, Azalia F2 codec, descriptor, sink-info, CRC, input-codec, root-codec, stream-latency, and AZF0 endpoint 0 field definitions, then ends inside AZF0 endpoint 1 audio descriptor definitions. Adjacent chunks are needed for complete coverage of the opening RIRB lower-base register and the remainder of endpoint 1 plus later endpoints.

## Purpose

The purpose of this header region is to define bit positions and masks for DCN 3.0.3 display audio and legacy display-adapter register surfaces. AMD display and audio code uses these generated constants through register-helper macros so implementation files can address hardware fields symbolically instead of hard-coding bit shifts and masks.

The covered hardware areas are:

- HDA/Azalia controller response path: RIRB base address, write pointer, interrupt count, RIRB control/status/size, immediate command/response registers, DMA position buffer address, and wall-clock counter alias.
- Azalia endpoint immediate command data/index windows for output and input endpoints.
- Legacy VGA sequencer, CRTC, graphics-controller, and attribute-controller indexed register field layouts.
- Azalia F2 codec converter and pin widgets for output and input paths, including audio format, stream/channel mapping, digital converter state, GTC embedding, widget capabilities, pin capabilities, pin sense, speaker/channel allocation, audio descriptors, multichannel enable/mute/channel IDs, lipsync/HBR, channel-status overrides, LPIB snapshots, format-changed status, and remote keepalive.
- Endpoint descriptor and sink-info indexed blocks that expose HDMI/DP audio descriptors, ELD-like sink metadata, manufacturer/product IDs, port IDs, and sink description bytes.
- Azalia input and output CRC result banks for channels 0-7.
- Azalia F2 root codec function parameters and controls, including vendor/device ID, revision, subordinate-node count, power state, subsystem ID, converter synchronization, reset, group type, size/rate capabilities, stream formats, and power states.
- AZF0 stream 0-15 FIFO and latency counter fields.
- AZF0 endpoint 0 full converter/pin/audio-enable interrupt surface and the beginning of AZF0 endpoint 1.

This is a hardware contract file. The behavioral importance is that each mask and shift must match the DCN 3.0.3 register database and the matching offset header; the code that consumes it often compiles even if a numeric value is wrong, but it will then program or read the wrong hardware bits.

## Important APIs, Types, And Constants

There are no callable APIs or concrete types in this chunk. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- Address-block comments such as `// addressBlock: azendpoint_f2codecind` and register comments such as `//AZALIA_F2_CODEC_PIN_CONTROL_CHANNEL_ALLOCATION` preserve the hardware grouping used by register-table and indirect-register macros.

Important register families in this chunk include:

- `RIRB_*`, `RESPONSE_INTERRUPT_COUNT`, `IMMEDIATE_COMMAND_*`, `IMMEDIATE_RESPONSE_INPUT_INTERFACE`, `DMA_POSITION_*`, and `WALL_CLOCK_COUNTER_ALIAS`, which define HDA command/response transport fields. Notable fields include RIRB base-address alignment masks, write-pointer reset, response and overrun interrupt bits, RIRB DMA enable, immediate-command busy/result-valid status, and DMA-position buffer enable/address fields.
- `AZENDPOINT_IMMEDIATE_COMMAND_*` and `AZENDPOINT_IMMEDIATE_COMMAND_INPUT_*`, which define endpoint-local immediate command data/index windows with 32-bit data payloads and 17-bit index fields.
- `SEQ00` through `SEQ04`, `CRT00` through `CRT22`, `GRA00` through `GRA08`, and `ATTR00` through `ATTR14`, which define legacy VGA indexed register fields for resets, clocking, map enables, font selection, timing totals, blank/sync positions, cursor and display start, line compare, graphics read/write modes, chain/odd-even behavior, attribute palette entries, mode control, overscan, color plane enable, pixel panning, and color select.
- `AZALIA_F2_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`, which packs number of channels, bits per sample, sample base divisor/multiple/rate, and stream type.
- `AZALIA_F2_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID`, which maps the codec channel ID and HDA stream ID.
- `AZALIA_F2_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER`, `_2`, and `_3`, which define digital audio enable/status bits such as `DIGEN`, `V`, `VCFG`, `PRE`, `COPY`, `NON_AUDIO`, `PRO`, `L`, channel-status `CC`, and silent-stream `KEEPALIVE`.
- `AZALIA_F2_CODEC_CONVERTER_CONTROL_GTC_EMBEDDING` and the AZF0 endpoint GTC registers, which define presentation-time embedding enable, offset-changed, group selection, and GTC counter delta/min/max fields.
- `AZALIA_F2_CODEC_*_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `*_SUPPORTED_SIZE_RATES`, `*_STREAM_FORMATS`, and `*_PARAMETER_CAPABILITIES`, which expose codec/widget capability bitmaps such as format override, stripe, unsolicited response, connection list, digital, power control, LR swap, widget type, HDMI/DP pin capabilities, VREF, and EAPD.
- `AZALIA_F2_CODEC_PIN_CONTROL_*` and `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_*`, which define pin widget control and response data: pin sense/presence, configuration default fields, speaker allocation, channel allocation, downmix info, audio descriptors, multichannel enables, HBR, LPIB snapshots, input status, infoframe, channel status, and format-changed reasons/responses.
- `AZALIA_F2_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`, which define IEC 60958 channel-status override fields for mode, source number, clock accuracy, word length, sampling frequency, CGMS-A, and per-channel numbers.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, which pack EDID/CTA-style audio descriptor fields for maximum channels, format code, supported frequencies, descriptor byte 2, and stereo-frequency overrides.
- `AZALIA_INPUT_CRC0/1_CHANNEL<n>` and `AZALIA_CRC0/1_CHANNEL<n>`, which expose 32-bit CRC readback fields per audio channel.
- `AZF0STREAM<n>_AZALIA_FIFO_SIZE_CONTROL`, `LATENCY_COUNTER_CONTROL`, `WORSTCASE_LATENCY_COUNT`, `CUMULATIVE_LATENCY_COUNT`, and `CUMULATIVE_REQUEST_COUNT`, repeated for streams 0-15, which expose FIFO bounds, maximum latency support, counter reset, and 32-bit latency/request counters.
- `AZF0ENDPOINT0_AZALIA_F0_*` and `AZF0ENDPOINT1_AZALIA_F0_*`, which are endpoint-instance-prefixed versions of the converter and pin register surfaces. Endpoint 0 is covered through audio enable/status and interrupt-status registers; endpoint 1 is covered from converter/widget capability through audio descriptor 5 at the end of the chunk.

Related semantic values live outside this header. Generated enum headers such as `soc24_enum.h` and older ASIC enum headers define values for fields such as audio sample sizes/rates, stream type, digital converter bits, RIRB size/reset, HBR, downmix, and descriptor format codes. This file only defines bit placement.

## Control Flow

This chunk has no runtime control flow. Its effective control flow is compile-time macro expansion into register-helper and indirect-register operations:

1. DCN 3.0.3 display code includes `dcn_3_0_3_sh_mask.h` with the matching `dcn_3_0_3_offset.h`.
2. Resource and audio register-list macros bind generated register and field names into register, shift, and mask tables. In this tree, `dcn303_resource.c` includes this header and uses field-list entries such as `SF(AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX, AZALIA_ENDPOINT_REG_INDEX, mask_sh)` and `SF(AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_DATA, AZALIA_ENDPOINT_REG_DATA, mask_sh)`.
3. Runtime code in the display audio layer uses helper macros such as `REG_SET`, `REG_UPDATE`, `REG_READ`, `AZ_REG_READ`, and `AZ_REG_WRITE`.
4. The helper layer uses the generated shifts and masks to construct MMIO or indirect-register reads/writes for the selected Azalia controller, endpoint, stream, or indexed codec register.

The runtime consumers provide the real flow. Typical audio flows write an endpoint index, write or read the endpoint data register, update pin/sink/audio descriptor fields from display sink information, configure converter format and channel allocation, set HBR/lipsync/status bits, and enable or disable audio when a connector/stream changes. HDA command flows use RIRB/immediate-command fields to transport codec verbs and responses. Stream-latency consumers reset and read latency counters. This header only supplies field layout for those sequences.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes stateful hardware registers:

- RIRB base, write pointer, size, DMA-enable, interrupt-enable, and status fields persist HDA response-ring configuration until driver reprogramming, controller reset, power transition, or ASIC reset.
- Immediate-command busy/result-valid fields reflect transient command execution state. The command write payload, codec address, endpoint index, and endpoint data registers are used as short-lived command windows rather than durable software state.
- DMA position buffer base/enable and wall-clock alias fields participate in audio position reporting and timing. Bad base-address alignment or enable bits can break position reporting without necessarily breaking display output.
- Legacy VGA indexed registers persist adapter compatibility state such as timing, attribute palette, plane routing, cursor, and text/graphics mode controls. Modern DC paths may rarely touch these fields, but the masks remain part of the ASIC register contract.
- Codec converter and pin control fields persist audio format, stream/channel routing, digital converter state, HBR enable, channel allocation, speaker allocation, sink capabilities, sink info, and channel-status override values used by HDMI/DP audio presentation.
- Capability and parameter registers represent hardware-advertised state. This header does not encode read-only versus writable direction, so capability fields appear as ordinary masks.
- LPIB, LPIB timer, CRC, latency, cumulative request, and worst-case latency registers expose counters or snapshots whose values change as audio traffic flows.
- GTC embedding and counter-delta fields persist presentation-time embedding configuration and measurement state for audio/video timing correlation.
- Audio enable/status and enabled/disabled/format-changed interrupt status fields persist or latch endpoint audio state changes until acknowledged according to the hardware's interrupt semantics.

Persistence is hardware-defined. Writable control fields remain until later driver updates, endpoint reset, display/audio power-state transitions, or full ASIC reset. Status and counter fields can change asynchronously with hardware, audio DMA, hotplug, and codec-response activity.

## Dependencies And Integration Points

This chunk depends on several generated and handwritten AMD display/audio components staying synchronized:

- The matching `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h` supplies MMIO and indirect-register offsets for the register names described here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c` includes the DCN 3.0.3 offset and shift/mask headers and builds the audio register/field table used by the DC resource layer.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c` includes the same DCN 3.0.3 generated headers for DMUB-side register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines audio register structures and macros for endpoint index/data and Azalia fields; `dce_audio.c` uses `AZ_REG_READ`, `AZ_REG_WRITE`, `REG_SET`, and related helpers to program audio descriptors, channel allocation, HBR, lipsync, sink info, hotplug control, power capabilities, and endpoint register windows.
- Older non-DC display paths such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v6_0.c`, `dce_v8_0.c`, and `dce_v10_0.c` show the same Azalia endpoint-index/data programming model and direct use of Azalia field masks/shifts, which helps validate the intended semantics even when DCN 3.0.3 uses different generated names.
- Generated enum headers, including `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h` and earlier ASIC enum files, provide symbolic values for many fields in this chunk. This shift/mask header does not define those values.
- The Linux HDA/HDMI audio stack, DRM connector hotplug flow, EDID/ELD parsing, DC stream state, and DMUB/display power management indirectly depend on these fields being correct when enabling audio over HDMI or DisplayPort.

The main integration contract is preprocessor naming. If a register or field macro is missing or renamed, table construction generally fails at compile time. If a mask or shift is numerically wrong, the driver can compile and then silently program the wrong endpoint, audio descriptor, interrupt bit, or stream counter field.

## Risks And Edge Cases

- The line range starts after the `RIRB_LOWER_BASE_ADDRESS` register comment and ends inside endpoint 1 audio descriptors. The merge lane must combine adjacent chunks before making whole-file statements about HDA RIRB coverage or all AZF0 endpoint instances.
- HDA base-address fields intentionally reserve or mask low alignment bits. Treating the lower base as a full 32-bit address instead of using `RIRB_LOWER_BASE_ADDRESS_MASK` or `DMA_POSITION_LOWER_BASE_ADDRESS_MASK` can create unaligned DMA state.
- RIRB status and control bits are small and adjacent. A wrong overrun/response interrupt bit can cause lost codec responses, interrupt storms, or missed overrun diagnostics.
- Immediate-command status has separate busy and result-valid bits. Polling the wrong bit can read stale responses or issue overlapping codec verbs.
- Endpoint index masks differ by block: top-level immediate command index fields include 16-bit or 17-bit windows depending on path. Using the wrong indexed-register width can address the wrong codec or endpoint register.
- Legacy VGA register fields are byte-sized and heavily packed. Accidental reuse of these masks outside their indexed-register path can corrupt unrelated VGA state.
- F2 codec output and input register families share many field names but have different prefixes. Mixing output pin fields with input pin fields can compile if names are manually expanded elsewhere, but would program the wrong direction's widget.
- Audio descriptor registers repeat with nearly identical layouts. Descriptor 0 includes `SUPPORTED_FREQUENCIES_STEREO` in several endpoint-specific blocks while later descriptors may not; assuming one descriptor layout for all entries risks overwriting high bits.
- Multichannel enable registers use paired and per-channel variants (`MULTICHANNEL01_ENABLE`, `MULTICHANNEL23_ENABLE`, then `MULTICHANNEL1_ENABLE`, `MULTICHANNEL3_ENABLE`, and so on). Confusing the pair fields with single-channel fields can mute or map the wrong channels.
- IEC 60958 channel-status override fields are spread across nine small registers. A wrong mask can change copy/pro/audio/sample-rate signaling without obvious driver errors, causing sink compatibility or compliance problems.
- Sink-info and sink-description fields are plain 32-bit or byte-like data fields. Endianness and packing assumptions in higher-level ELD/EDID handling must match the register definitions.
- CRC and latency counters are readback/status surfaces. The shift/mask header does not mark them as read-only, so accidental write paths are not prevented by the macro interface.
- AZF0 stream latency blocks are repeated 16 times with instance numbers embedded in macro names. Copy/paste or generation mistakes are easy to miss because neighboring streams look identical.
- Endpoint 0 and endpoint 1 register names are nearly identical except for the instance prefix. Endpoint selection bugs can appear as audio only working on one connector or one encoder path.
- Cross-generation reuse is risky. DCN 3.0.0, 3.0.2, 3.0.3, and later DCN headers contain similar Azalia names, but the offset header and shift/mask header must match the target ASIC.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Compile the DCN 3.0.3 AMD display driver paths that include this header, especially `dcn303_resource.c` and `dmub_dcn303.c`, to catch missing or renamed `__SHIFT`/`_MASK` macros in register-field table expansion.
- Preprocess representative `dce_audio.c` and DCN 3.0.3 resource objects to confirm that Azalia endpoint index/data fields resolve to the expected generated constants.
- Compare this chunk against the matching DCN 3.0.3 register database and `dcn_3_0_3_offset.h` to verify field/register coverage, especially the repeated AZF0 stream 0-15 and endpoint 0/1 blocks.
- Exercise HDMI and DisplayPort audio enable/disable on DCN 3.0.3 hardware. Expected signals are correct audio enumeration, stable hotplug behavior, and correct audio-enabled/audio-disabled interrupt status.
- Test PCM formats across channel counts, sample rates, and bits per sample; failures can implicate converter format, channel/stream ID, descriptor, or supported size/rate masks.
- Exercise HBR/non-PCM audio and verify the HBR enable/capable fields, stream type, coding type, and audio descriptor signaling.
- Validate speaker allocation and channel allocation using sinks with stereo, multichannel LPCM, and compressed-format capabilities; watch for wrong speaker map or muted channels.
- Check ELD/sink-info programming by comparing driver-visible sink metadata and hardware register readback for manufacturer/product IDs, port IDs, sink description, and audio descriptors.
- Run suspend/resume and display power-transition tests with audio active, because endpoint state, RIRB/DMA-position state, and stream latency counters may be reset or stale across power changes.
- Use register readback or debug traces around `RIRB_STATUS`, `IMMEDIATE_COMMAND_STATUS`, `AZALIA_F2_CODEC_PIN_CONTROL_FORMAT_CHANGED`, endpoint audio interrupt-status fields, and AZF0 stream latency counters to verify that status bits move through the expected masks.
- On hardware or simulation that exposes CRC result registers, compare audio CRC channels before and after format/channel changes to detect wrong channel mapping or stale endpoint programming.

## Open Cross-Chunk Questions

- The later merge lane should combine this with the previous chunk to recover the full `RIRB_LOWER_BASE_ADDRESS` context and any earlier HDA/CORB/controller fields.
- The later merge lane should combine this with the next chunk to document complete `AZF0ENDPOINT1` coverage and the remaining endpoint instances expected for DCN 3.0.3.
- Whole-file analysis should verify that the endpoint and stream instance counts in this shift/mask header match the DCN 3.0.3 offset header and the DCN audio resource register-list macros.
