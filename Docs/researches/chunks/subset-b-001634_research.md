# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 59504-62232

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask header. It contains no executable C logic; it publishes compile-time bit layouts for DCN 2.0 hardware registers as paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros.

The range is centered on Azalia/HDA audio and legacy indexed display registers:

- The tail of `AZSTREAM4` output stream descriptor fields, then complete `AZSTREAM5`, `AZSTREAM6`, and `AZSTREAM7` descriptor field layouts.
- Legacy VGA sequencer, CRTC, graphics-controller, and attribute-controller indexed registers: `SEQ00`-`SEQ04`, `CRT00`-`CRT22`, `GRA00`-`GRA08`, and `ATTR00`-`ATTR14`.
- Function group 2 Azalia codec endpoint, descriptor, sink-info, CRC result, input endpoint, and root codec indexed fields.
- Sixteen `AZF0STREAM<n>` stream-indirect blocks that expose FIFO sizing and latency counter fields.
- The start of the F0 endpoint-indirect blocks, including all of `AZF0ENDPOINT0` and the beginning of `AZF0ENDPOINT1`.

These macros are a hardware contract for code that packs and extracts fields from memory-mapped or indexed registers. They must line up with the matching address definitions in `dcn_2_0_0_offset.h` and with the enum values in generated Navi10 register enum headers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or storage objects in this chunk. The macro namespace is the API surface.

The `AZSTREAM4` tail and `AZSTREAM5`-`AZSTREAM7` groups describe HDA output stream descriptor registers. Each complete stream block has fields for:

- `OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`: reset/run, interrupt-on-completion enable, FIFO and descriptor error interrupt enables, stripe control, traffic priority, stream number, completion/error status bits, and FIFO-ready status.
- `LINK_POSITION_IN_CURRENT_BUFFER`, `CYCLIC_BUFFER_LENGTH`, `LAST_VALID_INDEX`, and `FIFO_SIZE`.
- `FORMAT`: channel count, bits per sample, sample-base divisor, sample-base multiple, and sample-base rate.
- `BDL_POINTER_LOWER_BASE_ADDRESS` and `BDL_POINTER_UPPER_BASE_ADDRESS`, including the unimplemented low address bits in the lower pointer.
- `LINK_POSITION_IN_CURRENT_BUFFER_ALIAS`.

The VGA indexed register groups expose the classic VGA programming model inside DCN 2.0's generated address space. `SEQ*` covers reset, clocking, map masks, character map select, and memory mode bits. `CRT*` covers horizontal/vertical timing fields, cursor location, start address, offset, underline/row scan controls, mode control, line compare, and other CRTC state. `GRA*` covers set/reset, enable set/reset, color compare, data rotate, read map select, graphics mode, miscellaneous mode, color-don't-care, and bit mask fields. `ATTR*` covers palette entries, mode control, overscan, color plane enable, horizontal pixel panning, and color-select fields.

The `AZALIA_F2_CODEC_*` groups describe a function group 2 HDA codec endpoint. Converter fields include audio format, channel/stream ID, digital converter channel-status bits, keepalive, stripe control, ramp rate, GTC embedding, widget capabilities, supported rates/sizes, and stream-format capabilities. Pin fields include connection list response, widget control, unsolicited response, pin sense, default configuration words, speaker and channel allocation, down-mix info, audio descriptor indexing/data, multichannel enable/mute bits, lipsync, HBR, sink-info access, IEC 60958 channel-status override words, LPIB snapshots, coding type, format-change reporting, wireless display identification, remote keepalive, and pin capabilities.

The descriptor and sink-info blocks are data-style indexed registers. `AUDIO_DESCRIPTOR0`-`AUDIO_DESCRIPTOR13` expose audio descriptor payload fields such as maximum channels, sample-rate mask, byte-oriented audio descriptor fields, and speaker information. `SINK_DESCRIPTION0`-`SINK_DESCRIPTION17`, manufacturer/product IDs, description length, and port IDs expose monitor/sink identity data used by audio enumeration.

The CRC blocks define per-channel full-width result fields for `AZALIA_INPUT_CRC0`, `AZALIA_INPUT_CRC1`, `AZALIA_CRC0`, and `AZALIA_CRC1`. These are diagnostic readback fields for audio data paths.

The `AZALIA_F2_CODEC_INPUT_*` groups mirror the output codec model for input-side converter and pin controls. They include input converter format, channel/stream ID, digital converter status, widget capabilities, supported formats, pin widget control, unsolicited response, pin sense, default configuration, channel allocation, per-channel multichannel enables, HBR, LPIB snapshot/readback, input status control, infoframe fields, channel status low/high, and input pin capabilities.

The `AZALIA_F2_CODEC_ROOT_*` and `AZALIA_F2_CODEC_FUNCTION_*` groups expose root/function identity and control fields: vendor/device ID, revision ID, subordinate node counts, power-state set/read status, subsystem ID words, converter synchronization, reset, group type, supported rates/formats, and power-state capabilities.

The `AZF0STREAM0` through `AZF0STREAM15` groups repeat the same stream-indirect layout for sixteen stream instances. Each has `AZALIA_FIFO_SIZE_CONTROL` fields for FIFO allocation, `AZALIA_LATENCY_COUNTER_CONTROL`, and readback counters for worst-case latency, cumulative latency, and cumulative request count.

The `AZF0ENDPOINT0` group is a large endpoint-indirect layout. It includes converter capabilities/control, audio format, digital converter channel-status bits, stream/rate support, stripe/ramp/GTC controls, GTC counter delta statistics, pin capabilities, unsolicited response and pin sense, widget control, channel/speaker allocation, fourteen audio descriptor registers, multichannel enables, lipsync/HBR response fields, sink-info fields, hot-plug control, forced unsolicited response, default configuration, channel-status override words, LPIB snapshot/readback, coding type, format-change state, wireless display and remote keepalive controls, audio-enable status, and audio enable/disable/format-change interrupt status.

The chunk ends after the start of `AZF0ENDPOINT1`; it includes that endpoint's converter widget capabilities, converter format, channel/stream ID, digital converter bits, and stream-format field, while later lines continue the remaining supported-size/rate and endpoint fields.

## Control Flow

This header range has no runtime control flow. It is preprocessor metadata consumed by display and audio hardware programming paths.

A typical consumer flow is:

1. Select a DCN 2.0 register address or index from `dcn_2_0_0_offset.h`, such as `mmAZSTREAM5_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`, `ixAZALIA_F2_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`, or `ixAZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_WIDGET_CONTROL`.
2. Use this header's matching mask and shift macros to pack, clear, or extract the desired register field.
3. Access the register through AMDGPU/DC display register helpers, HDA/Azalia indexed-register paths, DMUB paths, or low-level SOC15 register helpers.
4. Let hardware execute the requested state change, such as stream start/stop, FIFO allocation, audio format update, unsolicited-response enable, hotplug reporting, LPIB snapshot, or CRC capture.

Control-sensitive actions represented here include resetting and running HDA stream descriptors, enabling stream completion/error interrupts, programming HDA BDL pointers and cyclic buffer lengths, assigning stream IDs/channels, changing PCM/non-PCM format fields, enabling digital audio transmission, muting or enabling multichannel lanes, reporting HBR and lipsync data, exposing sink descriptors, forcing or acknowledging unsolicited responses, controlling hotplug status delivery, and reading latency or CRC diagnostics. The macros do not enforce the required ordering, ownership, polling, clear-on-write, or read-only restrictions for those actions.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in DCN 2.0 hardware registers.

The represented state includes:

- HDA stream descriptor state: run/reset bits, interrupt enables and status, stream number, FIFO readiness, current buffer position, cyclic buffer length, last valid BDL index, FIFO size, stream format, and BDL base addresses.
- Legacy VGA state: indexed sequencer, CRTC, graphics-controller, and attribute-controller fields used for VGA compatibility and early/legacy display modes.
- Codec and pin identity state: vendor/device IDs, revision IDs, subordinate-node counts, function group type, pin default configuration, association information, sink manufacturer/product/port IDs, sink description strings, audio descriptors, supported rates, supported bit depths, and stream-format capability masks.
- Audio transport state: converter format, channel/stream IDs, IEC 60958 channel-status bits and override enables, digital converter enable/status bits, keepalive, non-audio/pro/copy/pre-emphasis bits, speaker/channel allocation, HBR, lipsync, coding type, and wireless display identification.
- Interrupt and event state: unsolicited response enable/tag, hotplug enable/status, audio enabled/disabled/format-changed flags and masks, format-change reason/response fields, and forced unsolicited response controls.
- Diagnostics and counters: LPIB snapshots and timers, CRC results, FIFO allocation, latency counter control, worst-case latency, cumulative latency, cumulative request counts, and GTC counter deltas.

Persistence is hardware-defined. Some fields are programmed values that persist until mode-set, reset, power-gating, suspend/resume, or firmware intervention; some are live status readbacks; some are sticky interrupt/status bits; and some are read-only capability or identity values. This generated header does not encode which fields are read-only, write-one-to-clear, self-clearing, latched, indexed, or side-effecting.

## Dependencies And Integration Points

The direct companion for these field masks is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h`, which supplies the matching `mm...` and `ix...` register addresses and base indices. This chunk's address blocks match offset-header blocks such as `dce_dc_hda_azstream5_azdec`, `vga_vgaseqind`, `azendpoint_f2codecind`, `azendpoint_descriptorind`, `azendpoint_sinkinfoind`, `azf0controller_azcrc*resultind`, `azinputendpoint_f2codecind`, `azroot_f2codecind`, `azf0stream<n>_streamind`, and `azf0endpoint<n>_endpointind`.

Known include points for `dcn_2_0_0_sh_mask.h` in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`

The generated `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h` file provides semantic enum values for many Azalia fields in this chunk, including converter format sample-rate, bit-depth, channel-count, stream-type, digital converter status bits, widget control, unsolicited response, down-mix, and multichannel mute/enable fields. Consumers use those enum values with these masks/shifts to make packed register values readable and hardware-correct.

Although this path sits under a local `ceph-client` source tree, this source file is AMDGPU display/audio hardware metadata. It has no Ceph filesystem protocol logic, distributed filesystem state, or storage persistence behavior.

## Risks And Edge Cases

The main risk is silent register misprogramming. A wrong shift or mask can compile cleanly while changing the wrong hardware bit, corrupting adjacent fields during read-modify-write, or returning misleading status from diagnostics.

High-risk Azalia stream fields include `STREAM_RUN`, `STREAM_RESET`, interrupt enable/status bits, `STREAM_NUMBER`, `FORMAT`, BDL pointer fields, cyclic buffer length, last valid index, and FIFO size. Bad constants in these fields can prevent audio playback/capture, point DMA at the wrong BDL address, report incorrect buffer positions, trigger spurious interrupts, or mask real FIFO/descriptor errors.

Codec and pin fields are also sensitive. Incorrect converter format, channel/stream ID, digital converter bits, speaker/channel allocation, HBR, lipsync, channel-status override, sink-info, or audio descriptor fields can cause missing HDMI/DP audio, wrong channel count, wrong sample rate/depth, broken non-PCM passthrough, failed sink enumeration, or compliance failures.

Interrupt and event fields need conservative handling. Unsolicited response, hotplug, audio enabled/disabled, and format-change flags may be sticky, masked, or side-effecting. Using these masks without the correct clear/ack protocol can drop notifications or leave interrupt status stuck.

The repeated stream and endpoint patterns create copy-generation risk. `AZSTREAM5`-`AZSTREAM7`, `AZF0STREAM0`-`AZF0STREAM15`, CRC channel 0-7 groups, audio descriptor arrays, sink description arrays, and multichannel enable groups are highly repetitive. A single instance suffix, channel number, or mask-width mismatch would likely affect only one stream, endpoint, channel, or descriptor and may be hard to catch through compilation alone.

The VGA indexed-register block is legacy-sensitive. These fields may be touched in bring-up, VGA compatibility, firmware handoff, or diagnostic paths rather than normal atomic display mode-setting. Incorrect masks here can affect legacy console modes or boot-time display behavior in ways that are not covered by modern HDMI/DP tests.

This chunk has artificial boundaries. It starts partway through `AZSTREAM4_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS` and ends after the first `AZF0ENDPOINT1_AZALIA_F0_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` masks, before the rest of endpoint 1's converter and pin fields. The final per-file research pass should treat those as chunking artifacts, not missing source content.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Kernel/driver builds for DCN 2.0/Navi10 display paths should compile every referenced field name and include this header together with `dcn_2_0_0_offset.h`.
- Generated-register validation should compare every `*_MASK` and `*__SHIFT` pair in this line range against AMD's register database and against the matching `mm...`/`ix...` addresses in `dcn_2_0_0_offset.h`.
- HDMI/DP audio playback tests should verify channel count, sample rate, bit depth, PCM/non-PCM passthrough, HBR, speaker allocation, channel-status values, and sink descriptor enumeration.
- Audio hotplug and format-change tests should exercise unsolicited responses, audio enable/disable interrupts, format-change flags, hotplug control/status, and forced response paths.
- DMA-style HDA stream tests should exercise stream reset/run, BDL pointer programming, cyclic buffer length, last valid index, LPIB readback/snapshot, FIFO ready, and completion/error interrupt behavior for streams 4-7 where hardware exposes them.
- Latency and diagnostics tests should confirm `AZF0STREAM0`-`AZF0STREAM15` FIFO allocation, latency counter controls/readbacks, CRC channel results, and GTC delta fields transition as expected.
- VGA compatibility testing should cover boot console, firmware handoff, and legacy VGA modes enough to detect broken `SEQ*`, `CRT*`, `GRA*`, or `ATTR*` field layouts.
- Suspend/resume, runtime power management, hotplug stress, and modeset stress should not lose audio routing, leave stale interrupt flags, corrupt HDA stream descriptors, or report inconsistent sink/descriptor data after power transitions.

Regression symptoms from bad constants include missing HDMI/DP audio, wrong audio format or channel mapping, silent non-PCM passthrough failure, repeated audio hotplug or format-change events, stuck stream-run/reset state, DMA descriptor errors, FIFO underrun/overrun reporting anomalies, incorrect LPIB position, invalid sink descriptors, broken boot VGA output, and mismatches in audio CRC or latency diagnostics.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_0_sh_mask.h` define the beginning of `AZSTREAM4` and the preceding DCN 2.0 register-mask families. Later chunks complete `AZF0ENDPOINT1` and continue through subsequent generated DCN 2.0 hardware register definitions. The final per-file document should describe the whole source as a generated mask/shift contract for DCN 2.0 display, audio, and supporting hardware blocks rather than as algorithmic code.
