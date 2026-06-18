# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 54371-56929

## Purpose

This chunk is generated AMD DCN 3.0.2 register field metadata. It contains no executable C code; it publishes `#define` constants for field shifts and masks used by AMDGPU display code when packing and unpacking DCN 3.0.2 register values.

The selected range spans 2,054 macro definitions. It starts in the middle of the legacy VGA CRTC indexed register field block, covers the VGA graphics and attribute indexed fields, then covers a large part of the Azalia/HD-audio display-audio register model. The Azalia coverage includes F2 codec converter/pin/root fields, audio descriptor and sink-info indexed fields, CRC result fields, input endpoint fields, stream latency/FIFO fields for streams 0 through 15, all endpoint 0 converter and pin-control fields, and endpoint 1 fields through the first `AZF0ENDPOINT1_AZALIA_F0_CODEC_PIN_CONTROL_SINK_INFO8__DESCRIPTION16__SHIFT` line. The following endpoint 1 hot-plug, configuration-default, multichannel-enable2, channel-status override, and later fields are outside this chunk.

Although this file is under a local `ceph-client` source mirror, the content is AMDGPU display-controller hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation sites, locks, or callbacks in this range. Its public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a field within the register value.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field, normally written with an `L` suffix.

Major macro families in this slice:

- VGA CRTC tail: `CRT07` through `CRT22` fields for legacy timing extension bits, row scan and byte pan, cursor position and shape, display start, vertical sync/blank/display-end values, pitch, underline, address-count mode, line compare, and basic decode status fields.
- VGA graphics indexed registers: `GRA00` through `GRA08` fields for set/reset bits, set/reset enables, color compare, rotate/function select, read map select, write/read mode, odd/even addressing, graphics/address-select mode, color don't-care bits, and bit mask.
- VGA attribute indexed registers: `ATTR00` through `ATTR14` fields for palette entries, graphics/monochrome/line-graphics/blink/panning/pixel-clock/color-select modes, overscan color, plane enable, horizontal pixel pan, and color select.
- `AZALIA_F2_CODEC_CONVERTER_*`: converter stream format, stream/channel ID, digital converter control, stripe control, ramp rate, GTC embedding, audio widget capabilities, supported rates, and stream-format capabilities.
- `AZALIA_F2_CODEC_PIN_CONTROL_*`: connection list, widget control, unsolicited response, pin sense, configuration defaults, speaker/channel allocation, downmix, audio descriptor selection/data, multichannel controls, lipsync, HBR, sink-info index/data, LPIB snapshot/readback, coding type, format-change status, wireless display identification, and remote keepalive.
- `AZALIA_F2_PIN_CONTROL_CODEC_CS_OVERRIDE_*`: IEC 60958 channel-status override fields for mode, source, clock accuracy, word length, sample frequency, original sample frequency, CGMS-A, category, channel numbers, and source number.
- Descriptor and sink-info indexed blocks: `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, `AZALIA_F2_CODEC_PIN_CONTROL_MANUFACTURER_ID`, `PRODUCT_ID`, `SINK_DESCRIPTION_LEN`, `PORTID0/1`, and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`.
- CRC result blocks: `AZALIA_INPUT_CRC0/1_CHANNEL0..7` and `AZALIA_CRC0/1_CHANNEL0..7`, each exposing full-register CRC result fields.
- `AZALIA_F2_CODEC_INPUT_*`: input converter and input pin-control fields for format, stream/channel, digital converter control, capabilities, configuration default, channel allocation, multichannel channels 0 through 7, HBR, LPIB, input status, infoframe header/body/checksum, and audio channel status low/high words.
- `AZALIA_F2_CODEC_ROOT_*` and function-control fields: vendor/device ID, revision ID, node count, power state, subsystem ID response bytes, converter synchronization, reset, group type, supported rates/formats, and power-state capabilities.
- `AZF0STREAM0` through `AZF0STREAM15`: repeated stream FIFO-size control, latency counter control, worst-case latency, cumulative latency, and cumulative request count fields.
- `AZF0ENDPOINT0_AZALIA_F0_*`: endpoint 0 converter and pin fields for capabilities, format programming, GTC counter deltas, pin capabilities, unsolicited response, pin sense, widget control, speaker/channel allocation, descriptors 0 through 13, multichannel enables, lipsync, HBR, sink info, hot-plug control, forced unsolicited response, default configuration, multichannel enable2/mode, channel-status overrides, LPIB/coding/format-change, wireless/keepalive, and audio enable/interrupt status.
- `AZF0ENDPOINT1_AZALIA_F0_*`: endpoint 1 converter and pin fields through sink-info description field `DESCRIPTION16` in `SINK_INFO8`; it mirrors the early endpoint 0 shape but this chunk stops before endpoint 1 hot-plug and later controls.

The masks and shifts are usually consumed through token-pasting macros such as `SF(reg_name, field_name, __SHIFT)` and `SF(reg_name, field_name, _MASK)`, not by handwritten references to every generated macro.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the display driver:

1. DCN 3.0.2 resource code includes `dcn_3_0_2_offset.h` and this matching `dcn_3_0_2_sh_mask.h`.
2. Resource macros such as `SF(reg_name, field_name, post_fix)` paste register and field tokens into names like `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX__AZALIA_ENDPOINT_REG_INDEX_MASK`.
3. Static shift/mask tables are initialized, for example `audio_shift` and `audio_mask` in `dcn302_resource.c`.
4. Component constructors such as `dce_audio_create()` receive the register, shift, and mask tables.
5. Later display-audio, stream-encoder, hotplug, and modeset paths use register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and indexed-register accessors to read, modify, and write the hardware fields.

The selected macros do not encode ordering. Consumers still must sequence power/clock enablement, endpoint index/data access, audio stream setup, sink capability discovery, infoframe and channel-status programming, interrupt clear/ack, hotplug response, and suspend/resume restore correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes bit layouts for MMIO or indexed-register state maintained by the GPU display hardware.

Important hardware state represented by the fields includes:

- Legacy VGA state: CRTC timing extension bits, cursor position, display start, graphics plane behavior, attribute palette/mode/panning/color selection, and decode behavior.
- Display-audio converter state: stream format, channel and stream IDs, digital converter enable/status, non-audio/professional/copyright/emphasis bits, ramp/GTC controls, supported-rate and widget-capability reporting.
- Pin and sink state: pin widget control, unsolicited response tag/enables, pin sense, ELD-like manufacturer/product/port/description data, speaker/channel allocation, descriptor capabilities, HBR and lipsync flags, and default pin configuration fields.
- Audio transport and diagnostics: multichannel enable/mute/channel IDs, LPIB snapshots and timers, input CRC/output CRC result registers, FIFO allocation, worst-case and cumulative latency counters, request counters, and audio enable/format-change interrupts.
- Input-audio state: input converter and pin fields, infoframe payload bytes, input status, and channel status words.

Persistence is hardware-defined. Configuration fields generally remain until overwritten, power-gated, reset, or restored after suspend/resume. Status, interrupt, CRC, counter, snapshot, pin-sense, and unsolicited-response fields may be read-only, sticky, write-one-to-clear, self-clearing, or latch-on-read depending on the register. This generated header gives only masks and shifts; it does not identify access type or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.2 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h`, which supplies matching register offsets and base-index constants.
- DCN base segment definitions used by `BASE(mm..._BASE_IDX)` in resource code.
- Display component register table definitions for audio, AFMT, stream encoders, and DIO blocks that expect these field names to exist.

The direct include site for this ASIC generation in the inspected tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`. That file defines `SR`, `SRI`, and `SF` token-pasting helpers, includes the offset and shift/mask headers, and initializes structures such as `audio_shift` and `audio_mask`. In the audio path, `DCE120_AUD_COMMON_MASK_SH_LIST(__SHIFT)` and `DCE120_AUD_COMMON_MASK_SH_LIST(_MASK)` populate common Azalia endpoint index/data fields plus the base audio field list before `dce_audio_create()` constructs the audio object.

The broader integration point is the AMD Display Core register-helper framework. The generated constants are compile-time data for register packing, not a hardware abstraction on their own.

## Risks And Edge Cases

- Mask/shift drift is the central risk. A wrong value still compiles but can silently write the wrong bits in hardware.
- The selected range is artificially chunked. It begins after the start of the VGA CRTC block and ends inside endpoint 1 sink-info fields, so adjacent chunks are required for complete file-level reasoning.
- Repeated Azalia families are copy-sensitive. F2 codec, input codec, streams 0 through 15, endpoint 0, and endpoint 1 have similar field layouts; an incorrect prefix or channel index can affect only one audio endpoint, stream, or multichannel lane.
- Indexed endpoint access is order-sensitive. Fields behind endpoint index/data registers rely on the caller selecting the correct index before reading or writing data.
- Status and interrupt fields may be sticky or write-one-to-clear. Treating these masks as ordinary read/write configuration bits can lose hotplug, format-change, audio-enabled, audio-disabled, or unsolicited-response events.
- Sink-info and descriptor fields encode externally visible audio capabilities. Bad masks can corrupt ELD-like information, causing wrong channel counts, sample-rate exposure, HBR capability reporting, speaker allocation, or sink description strings.
- Legacy VGA fields are rarely exercised in modern modesets but can matter for firmware handoff, VGA-compatible paths, early boot display, virtualization, and console fallback.

## Test Signals

Useful validation signals for changes touching this chunk or generated data around it include:

- Build coverage of the AMDGPU display driver for the DCN 3.0.2 target; token-pasting users catch missing or renamed field macros at compile time.
- Display bring-up on DCN 3.0.2 hardware with HDMI/DP audio enabled, including stereo and multichannel playback.
- Hotplug and modeset tests that verify audio devices appear and disappear correctly, unsolicited responses are delivered, and audio enable/disable or format-change interrupts are acknowledged.
- EDID/ELD and sink capability checks: channel count, speaker allocation, supported rates, HBR support, manufacturer/product IDs, port ID, and sink description should match the connected display.
- Suspend/resume and runtime power-management tests that verify audio state, endpoint configuration, and legacy display handoff recover after power gating.
- Diagnostic register reads for LPIB, stream latency counters, FIFO allocation, CRC channels, and format-change status when debugging audio underruns, silence, or wrong stream mapping.
