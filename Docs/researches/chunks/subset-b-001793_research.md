# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 29717-32085

## Scope

This chunk is a generated AMD DCN 3.0.3 shift/mask header slice. It contains only preprocessor constants and generated register grouping comments; there are no C functions, structs, enums, variables, includes, or executable statements in this range.

The slice starts inside the `AZF0ENDPOINT1_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR5` register, covers the remainder of endpoint 1 pin/audio status fields, then covers complete `azf0endpoint2_endpointind`, `azf0endpoint3_endpointind`, and `azf0endpoint4_endpointind` blocks. It then enters `azf0endpoint5_endpointind` and ends after the masks for `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE2`. The requested range contains 2,049 `#define` lines for register field shifts and masks.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU Display Core hardware metadata for DCN display audio, not distributed filesystem logic.

## Purpose

This region publishes the bit layout for DCN 3.0.3 Azalia/HD-audio endpoint-indirect registers. Runtime display and audio code uses these macros with the matching offset/index definitions to program audio converter widgets and pin widgets behind display outputs. The generated names encode a register and field contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- Address block comments such as `// addressBlock: azf0endpoint2_endpointind` preserve the generated grouping for endpoint instances.

The main value is keeping audio register users symbolic. Code can construct register tables or compose values for fields such as converter format, stream/channel ID, speaker allocation, audio descriptors, hot-plug audio enablement, IEC 60958 channel-status overrides, LPIB snapshots, and audio interrupt status without embedding raw bit positions.

## Important APIs, Types, And Constants

There are no callable APIs or local types. The exported API is the macro namespace for `AZF0ENDPOINT<n>_AZALIA_F0_*` fields.

Important register families in this chunk:

- Endpoint 1 tail: audio descriptor 5 masks plus descriptors 6-13, multichannel controls, lipsync/HBR response fields, sink info, hot-plug control, unsolicited response forcing, default configuration response, IEC 60958 channel-status override fields, LPIB snapshot/readback fields, coding type, format-changed status, wireless display identification, remote keepalive, audio enable status, and enabled/disabled/format-changed interrupt status.
- Endpoints 2-4 complete blocks: converter widget capability parameters, converter format, channel/stream ID, digital converter controls, supported stream formats and rates, stripe/ramp/GTC embedding controls, GTC counter delta/min/max fields, pin widget capabilities, unsolicited response controls, pin-sense/widget-control fields, speaker/channel allocation, audio descriptors 0-13, multichannel controls, sink info, hot-plug audio controls, IEC 60958 override fields, LPIB state, format-change state, keepalive, and audio interrupt status.
- Endpoint 5 partial block: converter and pin capability/control fields through audio descriptors, multichannel enable, lipsync/HBR, sink info, hot-plug, unsolicited response force, default configuration response, and `MULTICHANNEL_ENABLE2`; the following endpoint 5 fields continue in the next chunk.

Notable field groups include:

- Audio descriptor fields: `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, `DESCRIPTOR_BYTE_2`, and for descriptor 0 the stereo-frequency byte in adjacent context. These are the ELD/SAD-style capability payloads exposed through the codec pin.
- Converter format fields: channel count, sample rate/base/multiplier/divider, bits per sample, stream type, and digital converter flags such as validity, VCFG, pre-emphasis, copy protection, non-audio, professional mode, and digital converter enablement.
- Stream routing fields: `CHANNEL_ID`, `STREAM_ID`, stripe control, ramp rate, GTC embedding enable/status bits, and GTC counter delta values.
- Pin capability and response fields: presence detect, ELD valid, connection list, HDMI/DP support, HBR, unsolicited response enable/tag, pin sense, widget control, speaker allocation, lipsync, sink manufacturer/product IDs, port IDs, and sink description bytes.
- Multichannel fields: paired-channel `MULTICHANNEL01/23/45/67` controls and odd-channel `MULTICHANNEL1/3/5/7` controls, each with enable, mute, and channel ID fields.
- Status/interrupt fields: audio enable status, audio enabled/disabled interrupt enable/status/ack, audio format changed enable/status/ack, and format-change sticky/current fields.

## Control Flow

This header has no runtime control flow. Its effective control flow is compile-time macro expansion plus endpoint-indirect register access performed elsewhere:

1. DCN303 code includes `dcn_3_0_3_offset.h` and this shift/mask header.
2. Resource code builds audio and AFMT register tables. In `drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`, `DCE120_AUD_COMMON_MASK_SH_LIST(__SHIFT)` and `DCE120_AUD_COMMON_MASK_SH_LIST(_MASK)` populate `struct dce_audio_shift` and `struct dce_audio_mask`; `dcn303_create_audio()` then passes those tables to `dce_audio_create()`.
3. Runtime audio helpers use the register tables and field masks with `REG_SET`, `REG_UPDATE`, `REG_GET`, endpoint index/data writes, or equivalent helpers to program converter and pin-widget state.
4. Hardware sequencing, such as enabling audio after link setup, updating ELD/SAD-derived descriptors, configuring speaker allocation, acknowledging audio interrupts, and handling hotplug or format changes, is implemented in Display Core audio and stream encoder code. This chunk only supplies bit positions.

Direct DCN303 include sites in this tree include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c`
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c`

The broader Azalia field contract is also visible in older DCE audio code paths, which use the same style of `AZALIA_F0_CODEC_*` masks for HDMI/DP audio setup. Those older files are useful behavioral references, but this chunk is the DCN 3.0.3 generated variant.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes MMIO-backed hardware state for display audio endpoints:

- Converter state: stream format, stream/channel IDs, digital converter enable/status flags, supported stream formats and rates, ramp/stripe policy, and GTC embedding counters.
- Pin state: pin capabilities, pin sense, unsolicited response configuration, widget control, speaker allocation, audio descriptors, HBR/lipsync response, sink metadata, hot-plug audio enablement, and default configuration response.
- Multichannel state: per-channel enable, mute, and channel mapping for paired and odd-channel multichannel modes.
- IEC 60958/channel-status state: override mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, CGMS-A, copyright, additional format info, category code, generation level, and validity-bit override.
- Runtime status state: audio enabled/disabled and format-changed interrupt status/ack bits, current and sticky format-changed indications, LPIB snapshots, LPIB timer snapshots, and remote keepalive.

Persistence is hardware-defined. Programmed fields usually remain until another MMIO write, display audio teardown, modeset, suspend/resume, power gating, or ASIC reset. Status, interrupt, ack, snapshot, pin-sense, hotplug, keepalive, and format-change fields can be asynchronous, sticky, self-clearing, or write-one-to-clear depending on the register. This generated header does not encode access permissions or side effects; callers must follow the audio block programming model.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `dcn_3_0_3_offset.h`, which provides the matching register offsets and endpoint-indirect addresses.
- DCN303 base address data from `sienna_cichlid_ip_offset.h` and associated SOC/DCN register helper macros.
- Display Core audio tables in `dcn303_resource.c`, especially `audio_regs`, `audio_shift`, `audio_mask`, and `dcn303_create_audio()`.
- Shared DCE/DCN audio code that consumes `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` to configure HDMI/DP audio and codec endpoint state.
- Stream encoder and AFMT code paths that generate HDMI/DP audio packets and rely on endpoint audio state matching stream timing and sink capabilities.
- IRQ and hotplug flows that observe audio enabled/disabled, format-changed, HPD, and unsolicited-response behavior.
- DMUB register metadata generation for DCN303, which includes this header for shared field mask/shift definitions.

The direct contract is preprocessor name compatibility. Missing or renamed macros generally fail at build time when register tables expand. Incorrect numeric masks or shifts are more dangerous because the build can pass while the driver programs the wrong bits.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the shifts for endpoint 1 `AUDIO_DESCRIPTOR5` and ends before later endpoint 5 fields such as multichannel mode and IEC 60958 overrides. Whole-file reconciliation must merge adjacent chunks before claiming complete endpoint 1 or endpoint 5 coverage.
- Repetition across endpoints 1-5 is copy-sensitive. A single shifted bit or mask typo can affect only one display audio endpoint, making failures connector- or pipe-specific.
- Endpoint-indirect access is stateful. Consumers must write the correct endpoint index and then read/write endpoint data; a correct field mask still causes bad behavior if paired with the wrong endpoint instance or indirect register offset.
- Audio descriptor and speaker allocation fields are sink-capability sensitive. Bad masks can advertise invalid channel counts, unsupported sampling rates, wrong speaker layouts, or wrong compressed-audio support.
- Hot-plug and unsolicited-response fields interact with display detection. Wrong enable/tag/payload masks can cause missing audio device notifications, hotplug storms, or stale userspace audio devices.
- Interrupt status and ack fields are easy to misuse because enable, status, and acknowledge bits share related register families. Mask drift can lose audio-enabled/disabled or format-changed events, or acknowledge the wrong condition.
- High-bit fields such as `AUDIO_ENABLED` at bit 31 and full-width LPIB/timer snapshots require unsigned-width-safe composition by callers.
- IEC 60958 override bits control externally visible audio metadata. Incorrect masks can produce subtle receiver compatibility issues even when PCM playback appears to work.
- GTC embedding and counter-delta fields affect audio/video synchronization. Incorrect programming can manifest as drift, lipsync errors, or timing-dependent failures rather than immediate link failure.
- Similar Azalia field names exist in DCE and other DCN generation headers. Cross-generation reuse must not assume identical bit layouts without checking the generated header for the target ASIC.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware audio behavior:

- Build AMDGPU Display Core with DCN303 enabled to catch missing `AZF0ENDPOINT*` field names in `SF(...)`, audio table, IRQ, and DMUB expansions.
- Mechanically compare this chunk against the matching DCN 3.0.3 register database and `dcn_3_0_3_offset.h` to ensure every field belongs to a defined endpoint-indirect register.
- Check repeated endpoint blocks for structural consistency: endpoints 2-4 should have matching field sets, while endpoint 1 and endpoint 5 differences should line up with adjacent chunk boundaries rather than generator drift.
- Exercise HDMI and DisplayPort audio on hardware using multiple endpoint instances: hotplug, audio device enumeration, EDID/ELD-derived descriptor programming, stereo and multichannel PCM, compressed formats, HBR-capable sinks, and speaker allocation changes.
- Test audio enable/disable across modesets, connector unplug/replug, DPMS, suspend/resume, and stream reallocation.
- Validate format-change behavior by switching sample rates, channel counts, and bit depths while monitoring kernel logs and userspace audio device state.
- Check interrupt paths for audio-enabled, audio-disabled, and format-changed status/ack behavior; watch for stuck interrupts or missed notifications.
- Validate lipsync/GTC-related behavior with A/V playback, especially after link-rate changes or resume.
- For register-level tests, read back endpoint-indirect registers after programming and verify that fields occupy the expected bits without modifying adjacent status or ack bits.

## Cross-Chunk Notes

Adjacent chunks are required for complete coverage of `AZF0ENDPOINT1_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR5` and the remainder of `AZF0ENDPOINT5_AZALIA_F0_*`. The final per-file document should merge this report with neighboring chunks before summarizing all Azalia endpoint instances or the full `dcn_3_0_3_sh_mask.h` generated ABI.
