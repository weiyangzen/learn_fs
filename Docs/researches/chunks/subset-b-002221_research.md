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
