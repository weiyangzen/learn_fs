# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 17815-18209

## Scope And Purpose

This chunk is the closing section of the generated AMD DCE 12.0 register offset header. It contains C preprocessor constants only: no functions, structs, enums, storage, or executable logic. The range starts at the tail of the `azf0inputendpoint3_inputendpointind` block, covers full input endpoint 4 through 7 indirect register windows, the `f2codecind` Azalia codec window, descriptor and sink-info indirect windows, Azalia CRC result windows, legacy VGA indexed windows, and then closes the header guard with `#endif`.

The purpose of these definitions is to give DCE 12.0 display/audio code stable symbolic names for indirect-register offsets. The `ix*` naming distinguishes these from direct MMIO `mm*` offsets elsewhere in the same header. Consumers combine these constants with AMDGPU/DC register access helpers and matching shift/mask headers to program HDMI/DP audio widgets, inspect audio stream status and CRCs, expose sink capability data, and access legacy VGA sequencer/CRT/graphics/attribute indexed registers.

## Important APIs, Types, And Macro Families

The public interface is the macro namespace. Each `#define` maps a symbolic register name to a numeric indirect offset. There are no C APIs or types in this chunk, but the macro families are part of the ABI between generated ASIC register descriptions and driver code.

Important macro groups:

- `ixAZF0INPUTENDPOINT3_*` tail entries for input endpoint 3: LPIB timer snapshot, input status control, and infoframe offsets complete the previous chunk's endpoint.
- `ixAZF0INPUTENDPOINT4_*` through `ixAZF0INPUTENDPOINT7_*`: four repeated input endpoint indirect blocks. Each endpoint exposes input converter capability/control offsets (`AUDIO_WIDGET_CAPABILITIES`, `CONVERTER_FORMAT`, `CHANNEL_STREAM_ID`, `DIGITAL_CONVERTER`, `STREAM_FORMATS`, and `SUPPORTED_SIZE_RATES`) plus input pin capability/control offsets for unsolicited responses, pin sense, widget control, multichannel enable state, HBR, channel allocation, hotplug control, forced unsolicited responses, configuration defaults, LPIB snapshots, input status, and infoframes.
- `ixAZALIA_F2_CODEC_ROOT_*` and `ixAZALIA_F2_CODEC_FUNCTION_*`: root and function-node offsets for vendor/device ID, revision, subordinate node count, power state, subsystem ID response words, converter synchronization, function reset, group type, size/rate support, stream formats, and power states.
- `ixAZALIA_F2_CODEC_CONVERTER_*`: output converter control, format, stream/channel ID, digital converter controls, stripe control, ramp rate, GTC embedding, and capability/format parameter offsets.
- `ixAZALIA_F2_CODEC_PIN_*` and `ixAZALIA_F2_PIN_CONTROL_CODEC_CS_OVERRIDE_*`: output pin widget offsets for connection list, widget control, unsolicited response, pin sense, configuration defaults, speaker/channel allocation, downmix, audio descriptors, multichannel enables, lip-sync, HBR, sink-info index/data, codec channel-status override words, association information, digital output status, LPIB snapshot/readback, coding type, format-changed indication, wireless display identification, and remote keepalive.
- `ixAZALIA_F2_CODEC_INPUT_*`: input converter and input pin offsets for format/stream/digital-converter programming, capabilities, pin sense/config defaults, channel allocation, multichannel enable state, HBR, LPIB, input status, infoframe, channel status low/high, and input pin parameters.
- `ixAUDIO_DESCRIPTOR0` through `ixAUDIO_DESCRIPTOR13`: descriptor-indirect offsets that hold HDMI/DP audio Short Audio Descriptor-like capability records.
- `ixAZALIA_F2_CODEC_PIN_CONTROL_MANUFACTURER_ID`, `PRODUCT_ID`, `SINK_DESCRIPTION_LEN`, `PORTID0`, `PORTID1`, and `ixSINK_DESCRIPTION0` through `ixSINK_DESCRIPTION17`: sink-info indirect offsets used to expose monitor/audio sink identity and description bytes.
- `ixAZALIA_INPUT_CRC0_CHANNEL*`, `ixAZALIA_INPUT_CRC1_CHANNEL*`, `ixAZALIA_CRC0_CHANNEL*`, and `ixAZALIA_CRC1_CHANNEL*`: per-channel CRC result offsets for input and output Azalia audio validation paths.
- `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*`: legacy VGA sequencer, CRT controller, graphics controller, and attribute controller indexed offsets.

## Control Flow And Data Flow

This header section has no runtime control flow. Data flow is compile-time substitution: C source includes `dce_12_0_offset.h`, passes an `ix...` constant to an indirect-register read/write helper, and the helper selects the corresponding hardware register inside an indexed address block.

The implied hardware flows are:

- Audio endpoint setup writes converter format, stream/channel ID, digital converter, multichannel, HBR, channel allocation, and widget-control offsets for each endpoint that participates in HDMI/DisplayPort audio.
- Hotplug and sink capability discovery reads pin sense, configuration defaults, audio descriptor records, sink-info index/data, manufacturer/product IDs, port IDs, and sink-description bytes.
- Audio playback/capture progress and diagnostics read or snapshot LPIB and LPIB timer registers, input status, digital output status, infoframe state, channel status, and CRC result windows.
- Codec lifecycle operations can use F2 function power-state, reset, converter synchronization, and parameter offsets to discover capabilities or bring the codec block into a programmed state.
- Legacy VGA paths use the sequencer, CRT controller, graphics controller, and attribute-controller indexed offsets when emulating or preserving VGA-compatible display state.

Because the values are offsets, not full behavior, ordering requirements live in the calling driver code and the hardware specification. For example, a caller normally chooses the endpoint or indexed block, writes an index/address register, then reads or writes the selected data register; this chunk supplies the index values for that transaction.

## State And Persistence Behavior

The file stores no state. The mutable state represented by these constants exists in DCE 12.0 hardware registers and can persist until rewritten, reset, power-gated, or reinitialized by display/audio bring-up.

State categories represented in this chunk include:

- Audio format and routing configuration: converter format, channel/stream IDs, digital converter controls, stripe/ramp/GTC controls, multichannel enable registers, HBR selection, channel allocation, and channel status.
- Sink and connector-observed state: pin sense, hotplug control, unsolicited response state, configuration defaults, audio descriptor data, sink manufacturer/product IDs, sink description, and port IDs.
- Runtime audio progress and status: LPIB snapshots, LPIB timer snapshots, input status control, infoframe registers, digital output status, coding type, format-changed state, remote keepalive, and wireless display identification.
- Capability and discovery state: root/function/converter/pin parameters for supported size/rates, stream formats, widget capabilities, pin capabilities, power states, group type, and subordinate node counts.
- Diagnostic state: Azalia input/output CRC channels and legacy VGA indexed register readbacks.
- Legacy display state: VGA sequencer, CRT controller, graphics controller, and attribute controller registers that can affect boot console compatibility, handoff, and VGA aperture behavior.

Wrong offsets can cause state changes to land in the wrong register within an indirect block. That can leave audio silent, misreport sink capabilities, break hotplug/audio ELD style discovery, corrupt channel allocation, hide status/CRC failures, or disturb VGA compatibility state until the relevant block is reprogrammed or reset.

## Dependencies And Integration Points

This header is included by DCE 12.0 display code such as `display/dc/dce120/dce120_timing_generator.c`, `display/dc/hwss/dce120/dce120_hwseq.c`, `display/dc/irq/dce120/irq_service_dce120.c`, `display/dc/resource/dce120/dce120_resource.c`, DCE 12.0 GPIO factory/translation code, and `amdgpu/gmc_v9_0.c`. This specific chunk's Azalia and VGA offsets are part of the same generated namespace even when direct references are sparse in this repository snapshot; other DCE/DCN generations expose nearly identical names for their audio and VGA paths.

Primary integration points:

- DRM/KMS connector and encoder audio support for HDMI/DisplayPort, including sink capability discovery and audio packet configuration.
- AMD DC resource and hardware sequencing code that includes DCE 12.0 register offsets alongside matching shift/mask headers.
- Interrupt and hotplug handling paths that may interact with Azalia pin sense, unsolicited response, hotplug control, and format/status change registers.
- Audio validation, diagnostics, or bring-up code that reads descriptor, sink-info, LPIB, infoframe, channel-status, and CRC result registers.
- Legacy VGA compatibility and handoff code that must preserve or program indexed VGA state while modern display pipes are active.
- Generated ASIC register-header maintenance: this chunk must remain consistent with sibling DCE and DCN offset headers and the corresponding `dce_12_0_sh_mask.h` field definitions.

## Risks And Edge Cases

The main risk is generated-header drift from the ASIC register database. These constants are opaque numeric offsets, so the compiler can catch missing names but cannot prove that `0x3776`, `0x779c`, or a VGA index value selects the intended register.

Specific risks:

- Chunk boundary: lines 17815-17817 are only the end of input endpoint 3; endpoint 3's converter and earlier pin offsets are in the previous chunk.
- Repeated endpoint blocks: input endpoint 4 through 7 are structurally identical and differ only by endpoint number, making copy/paste or generation errors hard to notice in review.
- Alias-like offsets: `ixAZALIA_F2_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR` and `ixAZALIA_F2_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR_DATA` both map to `0x3776`, so callers must understand whether they are treating the register as an index selector or data window.
- Naming overlap between F0 endpoint-specific offsets and F2 codec offsets can lead to using an offset from the wrong indexed address block.
- Sink-info and descriptor windows are indexed data areas; off-by-one descriptor or description offsets can produce plausible but wrong audio capability data.
- LPIB, timer snapshot, CRC, and channel-status registers are diagnostic/status oriented; stale reads or writes to the wrong block can make audio validation misleading.
- Legacy VGA register names are short and historically overloaded. Misusing `SEQ`, `CRT`, `GRA`, or `ATTR` offsets can affect boot-console compatibility or VGA state restoration.
- The final `#endif` means this chunk also closes the include guard; accidental insertion after it would not be protected by `_dce_12_0_OFFSET_HEADER`.

## Test Signals

There are no unit tests for this header section alone. Useful validation signals are build coverage, generated-header comparison, and hardware/display-audio behavior:

- Build AMDGPU/DC configurations that include `dce_12_0_offset.h`; this catches missing or renamed macros and header guard problems.
- Compare this range against the authoritative DCE 12.0 register database or a known-good upstream generated header, especially the repeated endpoint 4-7 blocks, F2 codec offsets, descriptor/sink-info windows, CRC offsets, and VGA index values.
- Exercise HDMI/DisplayPort audio on DCE 12.0 hardware: verify stream format, channel allocation, HBR/multichannel modes, channel status, infoframes, and audible output.
- Test hotplug and sink capability discovery with monitors exposing different audio descriptors and sink-info data; confirm the driver reports the expected formats, rates, channels, and connector identity.
- Validate LPIB snapshot/readback, format-changed status, remote keepalive, and input/output CRC channels through debug or hardware validation paths.
- Run suspend/resume and power-state transitions that reset or reprogram the Azalia F2 function and endpoints.
- Exercise VGA handoff or legacy VGA-compatible modes to verify sequencer, CRT controller, graphics controller, and attribute-controller indexed state remains readable and restorable.
