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
