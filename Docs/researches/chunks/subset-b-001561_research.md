# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 59881-62207

## Scope

This chunk covers lines 59881-62207 of the generated-style DCE 12.0 shift/mask header. The source is C preprocessor register metadata, not executable driver logic. In this range the header defines 2036 `#define` constants over 274 indexed-register names: 1019 `__SHIFT` definitions and 1017 `_MASK` definitions for AMD Azalia F0 HDMI/DP audio codec endpoints.

The chunk begins in the middle of `AZF0ENDPOINT5` pin-control definitions, then covers complete `azf0endpoint6_endpointind` and `azf0endpoint7_endpointind` output endpoint blocks, complete `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint2_inputendpointind` input endpoint blocks, and the beginning of `azf0inputendpoint3_inputendpointind`.

## Purpose

These macros describe bit positions for DCE 12.0 Azalia codec indexed registers. DCE exposes each audio endpoint through an endpoint index/data register pair in the companion offset header, and this file supplies the field-level masks and shifts for the register payload selected by that index. The hardware represented here is the display audio side of AMDGPU: output converter/pin widgets for HDMI/DisplayPort audio, plus input endpoint widgets for audio capture/status paths.

The exported contract is the standard generated AMD register-field naming pattern:

- `REGISTER__FIELD__SHIFT` gives the low bit of the field.
- `REGISTER__FIELD_MASK` gives the already-positioned field mask.
- Address-block comments such as `azf0endpoint6_endpointind` and `azf0inputendpoint0_inputendpointind` map the macro family to the matching indexed endpoint register namespace in `dce_12_0_offset.h`.

Because the file is consumed by preprocessor-based register helpers, the exact macro names are the API. A rename or numeric change can silently misprogram audio hardware even though the C code still compiles.

## Important Macro Families

The tail of `AZF0ENDPOINT5` contains pin-control fields for an output audio endpoint. It starts with pin sense and widget output enable, then covers speaker/channel allocation, audio descriptors 0-13, multichannel routing, lipsync/HBR capability, sink information, hot-plug and unsolicited response controls, default pin configuration, channel-status overrides, association and output status, LPIB snapshots, coding type, format-changed state, wireless-display identification, remote keepalive, and audio enable/disable/format-change interrupt status.

`AZF0ENDPOINT6` and `AZF0ENDPOINT7` repeat the full output endpoint layout. Their converter register families include:

- audio widget capabilities: channel capability, amplifier/format override capability, striping, processing widget, unsolicited response capability, connection list, digital/power/LR-swap capability, widget delay, and widget type;
- converter format: channel count, bits per sample, sample-base divisor/multiple/rate, and stream type;
- channel/stream ID routing;
- digital converter status/control bits such as `DIGEN`, validity, validity configuration, pre-emphasis, copy, non-audio, professional, level, channel status category code, and keepalive;
- stream format and supported size/rate capability masks;
- stripe control and ramp rate;
- global time counter embedding and counter delta/min/max fields.

The output endpoint pin families for endpoints 6 and 7 include:

- pin audio-widget and pin-capability parameters, including HDMI/DP capability, EAPD, VREF, balanced I/O, trigger requirement, presence-detect and unsolicited-response capability;
- unsolicited response tag/enable and forced response payload/force fields;
- pin sense impedance status and widget output enable;
- channel/speaker allocation fields for HDMI and DP connections, extra connection info, LFE level, level shift, and down-mix inhibit;
- short audio descriptor registers `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, where descriptor 0 also carries stereo-frequency capability;
- two multichannel enable layouts: pair-based `MULTICHANNEL01/23/45/67` fields and odd-channel `MULTICHANNEL1/3/5/7` fields, each with enable, mute, and channel ID subfields;
- `MULTICHANNEL_MODE`, channel-status override registers 0-8, association information, digital output status, LPIB snapshot registers, coding type, format-change tracking, wireless-display identification, remote keepalive, and audio enabled/disabled/format-change interrupt status.

`AZF0INPUTENDPOINT0`, `AZF0INPUTENDPOINT1`, and `AZF0INPUTENDPOINT2` repeat an input endpoint layout. They include input converter widget capability, converter format, channel/stream ID, digital converter bits, stream formats, supported size/rates, input pin widget/capability parameters, unsolicited response control, input pin sense, widget control, two multichannel-enable layouts, HBR response, channel allocation, hot-plug/audio-enable state, forced unsolicited response, default pin configuration, LPIB snapshot registers, input activity/status controls, and an input audio infoframe register.

`AZF0INPUTENDPOINT3` begins at the end of the chunk. Lines 62128-62207 cover its input converter capability, format, channel/stream ID, digital converter, stream formats, supported size/rates, and the start of input pin audio-widget capabilities. The rest of input endpoint 3 continues in the next chunk.

## APIs, Types, and Functions

This chunk defines no functions, structs, enums, or callable APIs. Its interface is entirely preprocessor constants used by AMDGPU's register programming macros. The companion APIs live in the display and GPU driver code that includes `dce_12_0_sh_mask.h`, particularly register helper macros that combine an address, mask, shift, and value into read/modify/write operations.

The adjacent generated headers are part of the same API surface:

- `dce_12_0_offset.h` provides the `mmAZF0ENDPOINT*_..._INDEX`, `mmAZF0ENDPOINT*_..._DATA`, `ixAZF0ENDPOINT*_...`, `mmAZF0INPUTENDPOINT*_..._INDEX`, `mmAZF0INPUTENDPOINT*_..._DATA`, and `ixAZF0INPUTENDPOINT*_...` constants that identify the indexed registers.
- `vega10_enum.h` provides generated enum values for many Azalia fields, such as audio widget capability types and boolean capability values.

## Control Flow

There is no runtime control flow in the header. The practical control flow is imposed by callers and by the indexed-register access model:

1. Select an endpoint instance, such as endpoint 6, endpoint 7, or input endpoint 1.
2. Write the indexed-register selector from `dce_12_0_offset.h`.
3. Read or write the endpoint data register.
4. Use this chunk's `*_MASK` and `*__SHIFT` macros to extract or update fields in the selected data payload.
5. For status or interrupt-style registers, read status fields and write the appropriate ack/clear bits according to hardware semantics.

Several field names imply order-sensitive hardware procedures that are implemented outside this header: enabling digital converters, setting stream/channel IDs and audio formats, advertising sink descriptors, programming multichannel allocation, forcing or enabling unsolicited responses, handling hot-plug/audio enabled state, acknowledging audio enable/disable/format-change interrupts, and snapshotting LPIB/timer state.

## State and Persistence

The header itself stores no state. It describes stateful hardware fields in the DCE Azalia function. Those fields persist in hardware registers until changed by MMIO/indexed-register writes, hardware events, reset, power management, or firmware-side initialization.

Important state domains in this chunk include:

- output converter stream setup: sample format, channel count, bit depth, stream ID, channel ID, digital converter enable, channel status bits, keepalive, striping, ramp rate, and GTC embedding;
- output pin capabilities and sink description: HDMI/DP capability, speaker/channel allocation, audio descriptors, lipsync, HBR capability/enable, manufacturer/product IDs, port IDs, and sink description bytes;
- routing and muting: multichannel enable, mute, channel ID, multichannel mode, association info, and digital output active/mute/status fields;
- event and interrupt state: unsolicited response enable/force payloads, audio enabled/disabled/format-change interrupt status and ack bits, input activity UR enables, and input channel-layout/infoframe change UR enables;
- timing/progress state: LPIB values, LPIB snapshot lock, cyclic buffer wrap count, timer snapshots, GTC counter delta ranges, and remote keepalive state;
- input endpoint state: input activity, channel layout, input audio infoframe channel count/allocation/byte 5/valid bit, input pin sense, HBR, hot-plug audio-enabled state, and input converter stream configuration.

Many fields are single-bit controls or status flags, but several are packed multi-bit values: descriptor bytes, channel allocation, channel IDs, manufacturer/product IDs, port IDs, sink description bytes, LPIB snapshots, GTC counters, unsolicited response payloads, and channel-status override bytes.

## Dependencies and Integration Points

This header has only preprocessor-level dependencies, but its values are coupled to several generated and driver-level pieces:

- The register offsets in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h` must match the endpoint and input-endpoint macro families in this chunk.
- DCE 12.0 display code includes this header from timing-generator, IRQ service, GPIO factory/translation, hardware sequencing, resource, and GMC paths. Direct references to the AZF0 endpoint field names may be sparse because many register accesses are generated through macro concatenation.
- The Linux DRM/AMDGPU audio integration depends on these fields indirectly when display audio is configured for HDMI/DP links, when audio hotplug/ELD-like sink capability information is surfaced, and when DCE reports audio-related interrupts.
- `vega10_enum.h` supplies semantic values for several of the same Azalia field names; this shift/mask header supplies placement, while enum headers supply possible values.
- The endpoint index/data access pattern is an integration constraint: using the right field mask against the wrong endpoint instance or wrong index selector can corrupt a different logical widget.

## Risks

The main risk is silent hardware misprogramming. A bad shift or mask will still compile but can place audio format, channel ID, interrupt ack, or sink-descriptor data in the wrong bits. That can show up as missing HDMI/DP audio, wrong channel mapping, stale sink capabilities, interrupt storms, lost format-change events, or incorrect HBR/multichannel behavior.

The repeated endpoint layouts create copy/generation hazards. `AZF0ENDPOINT6` and `AZF0ENDPOINT7` should be structurally identical output endpoint instances, and `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT2` should be structurally identical input endpoint instances. Any one-off field-width difference should be treated as suspicious unless the hardware spec explains it. The chunk also starts and ends mid-block, so reconciliation with adjacent chunks is required before drawing per-file conclusions about endpoint 5 or input endpoint 3.

The indexed-register model increases the blast radius of mistakes. The data register is generic for an endpoint instance, and the selected index controls which logical register is being accessed. If driver code writes data with masks from one indexed register after selecting another, these macros cannot protect against the error.

Interrupt/status fields need special care. Fields named `*_INT_ACK`, `*_INT_STATUS`, `*_AUDIO_ENABLED`, `*_FORMAT_CHANGED`, `UNSOLICITED_RESPONSE_FORCE`, and input activity/infoframe UR enables may have write-one-to-clear, sticky, or event-generation semantics in hardware. Treating them like ordinary read/write configuration bits can drop events or cause repeated unsolicited responses.

Several full-width or wide masks, such as `0xFFFFFFFFL` for stream formats, port IDs, LPIB snapshots, GTC counter deltas, and wireless display identification, rely on callers using 32-bit unsigned intermediates. Signed or narrower temporaries can truncate payloads or propagate sign bits.

## Test Signals

Useful validation is mostly build, static, and hardware integration coverage:

- compile coverage for all DCE 12.0 translation units that include `dce_12_0_sh_mask.h`;
- generated-header checks that every field has a matching shift/mask pair, masks align with shifts and expected field widths, and output/input endpoint instances remain structurally consistent;
- cross-header checks that every `AZF0ENDPOINT*` and `AZF0INPUTENDPOINT*` field macro has the corresponding indexed register in `dce_12_0_offset.h`;
- HDMI/DP audio smoke tests over endpoints 5-7, including hotplug, stream start/stop, mute/unmute, sample-rate/bit-depth changes, channel-count changes, and HBR-capable modes;
- multichannel audio tests that verify speaker allocation, channel allocation, multichannel enable/mute/channel ID fields, and down-mix inhibit behavior;
- sink-capability tests that read back or validate audio descriptor, manufacturer/product ID, port ID, sink-description, lipsync, and HDMI/DP connection fields after monitor hotplug;
- interrupt tests for audio enabled, disabled, format changed, unsolicited responses, input activity, and input channel-layout/infoframe changes;
- LPIB/GTC/keepalive readback tests around active streams to confirm snapshot locks, wrap counts, timer snapshots, counter deltas, and remote keepalive fields land in expected bits.

## Cross-Chunk Notes

This chunk is chunk 25 of 27 for `dce_12_0_sh_mask.h`. The previous chunk contains the beginning of `AZF0ENDPOINT5`, including earlier converter and pin parameter fields. The next chunk continues `AZF0INPUTENDPOINT3` and then likely completes the remaining input endpoint families and file tail. The final per-file research should merge these chunks into one description of DCE 12.0 display audio register masks, preserving the distinction between direct MMIO register fields and indexed Azalia endpoint fields.
