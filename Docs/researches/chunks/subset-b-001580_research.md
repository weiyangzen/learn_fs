# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h lines 13112-14114

## Scope And Purpose

This chunk is the tail of the generated AMD DCN 1.0 register-offset header. It contains no executable driver logic; it publishes C preprocessor constants for indirect Azalia/HDA audio codec register offsets used by AMDGPU display code. The requested range has 869 `#define` entries and 33 generated `addressBlock` group comments.

The range starts in the middle of the `AZALIA_F2` codec input-pin/root codec indirect namespace, covering response configuration defaults, channel allocation, multichannel enable controls, high-bit-rate audio, LPIB snapshots, input status/infoframe, channel status, and root/function parameters. It then defines 16 stream-indirect blocks, `AZF0STREAM0` through `AZF0STREAM15`, each with FIFO size and latency counter registers. Most of the chunk is repeated output endpoint metadata for `AZF0ENDPOINT0` through `AZF0ENDPOINT7`, followed by input endpoint metadata for `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7`. The chunk ends with the header guard `#endif`.

Although the repository path is under `ceph-client`, this file is AMDGPU Linux kernel hardware metadata for DCN 1.0 display/audio blocks. It has no Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, classes, or local variables in this chunk. The public interface is the generated macro namespace:

- `ixAZALIA_F2_CODEC_*` macros describe function group 2 codec root/function/input-pin indirect offsets. They include vendor/device ID, revision, subordinate-node count, power state, subsystem ID response words, converter synchronization, reset, supported size/rates, stream formats, and power states.
- `ixAZF0STREAM<N>_AZALIA_*` macros, for streams 0 through 15, expose the five common per-stream indirect offsets: FIFO size control, latency counter control, worst-case latency count, cumulative latency count, and cumulative request count.
- `ixAZF0ENDPOINT<N>_AZALIA_F0_CODEC_CONVERTER_*` macros, for endpoints 0 through 7, describe output converter capability, format, stream/channel ID, digital converter, supported formats/rates, stripe/ramp/GTC embedding controls, and GTC counter delta/min/max offsets.
- `ixAZF0ENDPOINT<N>_AZALIA_F0_CODEC_PIN_*` and `ixAZF0ENDPOINT<N>_AZALIA_F0_PIN_CONTROL_*` macros describe output pin capability, unsolicited response, pin sense, widget control, channel speaker, audio descriptors 0-13, multichannel enable/mode, lipsync/HBR responses, sink info 0-8, hot-plug control, configuration default, channel-status override words, LPIB snapshots, coding type, format change, wireless display identification, remote keepalive, audio enable state, and audio enabled/disabled/format-changed interrupt status.
- `ixAZF0INPUTENDPOINT<N>_AZALIA_F0_CODEC_INPUT_*` macros, for input endpoints 0 through 7, provide the smaller input converter/pin set: audio widget capabilities, converter format, channel stream ID, digital converter, stream formats, supported size/rates, input pin capabilities, unsolicited response, input pin sense, widget control, multichannel enable controls, HBR response, channel allocation, hot-plug and force unsolicited response, configuration default, LPIB snapshot registers, input status control, and infoframe.

The `ix` prefix denotes indirect-register offsets rather than flat `mm...` MMIO addresses. Consumers must combine these constants with the appropriate Azalia indirect access mechanism and address-block selection; the header itself does not encode the access method.

## Control Flow

This header chunk has no runtime control flow. Each line is declarative metadata consumed by AMD display/audio driver code or register-description tables.

The implied consumer flow is:

1. Select the relevant Azalia root, stream, output endpoint, or input endpoint instance.
2. Use the matching `ix...` macro as the indirect register index for the hardware operation.
3. Access the register through AMDGPU/DC Azalia register helpers or generated register-table plumbing.
4. For status or interrupt-like registers, read, poll, snapshot, acknowledge, or mask according to the hardware programming guide and companion mask/shift definitions.

The chunk does not describe sequencing requirements. Correct order is external to this file: audio format programming must line up with stream IDs and converter state, endpoint hot-plug/unsolicited-response behavior must match connector events, LPIB snapshots must be captured consistently, and interrupt/status fields must be interpreted with the hardware-defined polarity.

## State And Persistence Behavior

The macros have no mutable software state, locking, allocation, reference ownership, or persistence. They are compile-time numeric constants.

The hardware state identified by these offsets is persistent only in the DCN/Azalia hardware registers. Examples include codec function power/reset state, supported-format and capability readbacks, per-stream latency counters, converter format and digital converter controls, stream/channel routing, endpoint audio descriptors, multichannel and HBR state, pin sense and hot-plug controls, sink info, channel-status override data, LPIB snapshots, audio enable status, and input endpoint status/infoframe data.

Persistence and volatility are register-specific and not encoded here. Some registers are static capabilities, some are live counters or snapshots, some are control fields that remain programmed until modeset/audio reconfiguration/suspend/resume/GPU reset, and some status bits may be sticky, write-one-to-clear, self-clearing, or read-only. The offset header does not communicate those access semantics.

## Dependencies And Integration Points

This file depends on AMD's generated DCN 1.0 ASIC register database. The numeric values must match the hardware indirect register map and the companion DCN 1.0 mask/shift and enum headers in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/`.

In this source tree, `dcn_1_0_offset.h` is directly included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c`, which uses generated offset and mask metadata to map DCN 1.0 interrupt sources. Other practical consumers may reach these constants through generated register tables or shared AMD display/audio include paths rather than explicit direct textual references to every macro.

The chunk also mirrors Azalia endpoint families visible in adjacent AMD DCE offset headers, so it is part of a larger generated convention spanning display IP generations. Integration surfaces include HDMI/DisplayPort audio enablement, HDA codec enumeration, audio stream setup, ELD/sink information handling, hot-plug and unsolicited response handling, HBR/multichannel audio configuration, latency/counter diagnostics, and DCN interrupt/status plumbing.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. A wrong `ix...` value can compile cleanly while reading or writing the wrong indirect register, producing broken HDMI/DP audio, incorrect codec capability reporting, missed hot-plug or unsolicited events, bad stream routing, disabled audio, bogus LPIB/latency diagnostics, or interrupt storms.

The range is highly repetitive. Streams 0-15 and endpoints 0-7 share near-identical register layouts, while input endpoints use a smaller but similarly repeated set. Generator mistakes, copy/paste edits, or manual review errors can affect only one stream or endpoint instance, so tests that exercise only the first connector or first stream may miss instance-specific defects.

The chunk begins mid `AZALIA_F2_CODEC_INPUT_PIN` family and ends at the file guard, so neighboring chunk context is needed before making whole-file claims about all DCN 1.0 Azalia offsets. The final merge lane should treat the initial `AZALIA_F2` lines as a continuation from the previous chunk, not as the beginning of that logical block.

Names such as `*_INT_STATUS`, `*_UNSOLICITED_RESPONSE_FORCE`, `*_HOT_PLUG_CONTROL`, `*_RESET`, `*_POWER_STATE`, `*_LPIB_SNAPSHOT_CONTROL`, and `*_FORMAT_CHANGED` expose hardware conventions, not high-level boolean APIs. Callers must not infer ack polarity, reset side effects, or snapshot timing only from macro names.

Output and input endpoints differ. Output endpoints include audio descriptors, sink info, channel-status overrides, lipsync, coding type, format-change, wireless-display, remote-keepalive, and audio enable/disable status registers. Input endpoints omit most of that surface and instead use input-pin sense/status/infoframe offsets. Treating the two families as layout-compatible would misprogram later offsets.

## Test Signals

Useful validation is mostly generated-header comparison, build coverage, and hardware/display-audio behavior:

- Build AMDGPU/DCN 1.0 targets and ensure all generated offset users compile without missing, duplicated, or mismatched macro names.
- Compare the 869 constants in this range against AMD's source register database and against sibling DCE/DCN generated headers where the Azalia layout is expected to match.
- Exercise HDMI/DisplayPort audio enumeration so codec root/function parameters, subordinate node counts, supported rates, stream formats, power states, and endpoint capabilities are read correctly.
- Test all available endpoint instances, not only endpoint 0, with hotplug, audio enable/disable, format changes, HBR, multichannel modes, and sink-info updates.
- Run audio playback/format tests covering common PCM rates, channel counts, HBR-capable formats, stream/channel ID programming, and repeated modesets.
- Check LPIB snapshot and latency counter behavior for streams 0-15 where supported, watching worst-case and cumulative latency/request counters for sane monotonic behavior.
- Validate interrupt/status paths for audio enabled, audio disabled, format changed, hot-plug, and unsolicited response events, including masking/acknowledgement behavior in the DCN 1.0 IRQ service.
- Include suspend/resume, GPU reset, connector unplug/replug, and display mode changes while audio is active to catch stale register state or missed reprogramming.

Regression symptoms from bad constants include absent HDMI/DP audio devices, wrong supported audio formats, no sound despite video output, audio dropouts after modeset or hotplug, incorrect multichannel/HBR behavior, stale LPIB snapshots, implausible latency counters, persistent format-change status, or endpoint-specific failures limited to higher-numbered streams/connectors.

## Cross-Chunk Notes

Previous chunks own the earlier DCN 1.0 offset header content and the beginning of the Azalia F2 input-pin block. This chunk completes the file. During reconciliation, the full file should be described as generated DCN 1.0 register-offset metadata, not as algorithmic code, with this range specifically representing the final Azalia stream and endpoint indirect-register namespaces.
