# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 15569-16273

## Scope

This chunk is the closing Azalia/audio endpoint section of the generated AMD DCN 3.0.2 register offset header. It contains preprocessor constants only. Each `ix...` macro names an indirect Azalia codec endpoint register index, not a direct MMIO address. The chunk starts in the tail of `azf0endpoint1_endpointind`, covers complete output endpoint index maps for `AZF0ENDPOINT2` through `AZF0ENDPOINT7`, then covers complete input endpoint index maps for `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7`, and ends with the header guard `#endif`.

The companion direct endpoint index/data windows and the start of `AZF0ENDPOINT0`/`AZF0ENDPOINT1` are outside this chunk. For DCN 3.0.2, `dcn302_resource.c` includes this offset header and uses the direct `AZF0ENDPOINT{id}_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `...DATA` registers to build `dce_audio_registers`; the indirect `ix...` values in this chunk are the per-endpoint indices subsequently written through those windows by the DC audio code.

## Purpose

The purpose of these constants is to provide stable symbolic indices for the GPU display audio codec's HD-Audio/Azalia endpoint register space. Driver code does not access the endpoint controls by normal direct-register names. Instead, it selects an endpoint-local index through `AZALIA_F0_CODEC_ENDPOINT_INDEX` and reads or writes `AZALIA_F0_CODEC_ENDPOINT_DATA`. These `ixAZF0ENDPOINT*` and `ixAZF0INPUTENDPOINT*` values are the selected indices.

The output endpoint blocks describe HDMI/DP audio sink capabilities and runtime state advertised to, or consumed by, the audio stack: converter format and stream ID, pin capabilities, speaker/channel allocation, supported audio descriptors, lipsync, high-bit-rate audio, sink identity, hot-plug/audio enable, channel-status overrides, LPIB snapshots, coding/format-change state, wireless display identification, and audio enable/disable interrupt status.

The input endpoint blocks describe a smaller capture/input surface: input converter format and stream ID, input pin capabilities, unsolicited response and pin sense, multichannel enables, HBR response, channel allocation, hot-plug/audio enable, default configuration, LPIB snapshots, input activity/status control, and input infoframe fields.

## Important Macros And Register Families

Output endpoint coverage:

- `ixAZF0ENDPOINT1_*` at lines 15569-15605 is the tail of endpoint 1. It includes `RESPONSE_HBR`, `SINK_INFO0..8`, `HOT_PLUG_CONTROL`, unsolicited response force, default configuration response, multichannel enable/mode, channel-status override slots 0 through 8, association info, digital output status, LPIB snapshot registers, coding/format-change flags, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status.
- `ixAZF0ENDPOINT2_*` through `ixAZF0ENDPOINT7_*` repeat the full output endpoint layout with endpoint-specific macro names. Each complete block maps converter controls at indices `0x0001..0x000e`, pin controls at `0x0020..0x006e`, audio descriptor slots `0x0028..0x0035`, sink-info slots `0x003a..0x0042`, channel-status override slots `0x0059..0x0061`, and endpoint status/interrupt registers `0x006b..0x006e`.

Input endpoint coverage:

- `ixAZF0INPUTENDPOINT0_*` through `ixAZF0INPUTENDPOINT7_*` repeat the input endpoint layout. Each block maps input converter controls at `0x0001..0x0006`, input pin controls at `0x0020..0x0038`, channel allocation at `0x0053`, hot-plug/audio enable and default configuration at `0x0054..0x0056`, LPIB snapshot registers at `0x0064..0x0066`, input status control at `0x0067`, and input infoframe at `0x0068`.

Important endpoint-local indices are intentionally reused across instances. For example, every output endpoint's `...CODEC_PIN_CONTROL_RESPONSE_HBR` is `0x0038`, and every input endpoint's `...CODEC_INPUT_PIN_CONTROL_INFOFRAME` is `0x0068`; the instance is selected by the direct endpoint index/data MMIO window, while the `ix` value selects the endpoint-local register.

## APIs, Types, And Consumers

This chunk defines no C functions, structs, enums, or storage. Its API surface is the macro namespace consumed by generated register helpers and display audio code.

Relevant consumers and integration types observed nearby:

- `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` in `display/dc/dce/dce_audio.h` describe the direct endpoint index/data window and bitfield masks used by the audio object.
- `AUD_COMMON_REG_LIST(id)` in `dce_audio.h` expands to the per-instance `AZF0ENDPOINT{id}_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `...DATA` direct registers. This is the direct register path used to access the indirect `ix` values defined here.
- `dcn302_resource.c` includes `dcn/dcn_3_0_2_offset.h` and `dcn/dcn_3_0_2_sh_mask.h`, creates `audio_regs[]` entries for output endpoints 0 through 6, and wires `dcn302_create_audio()` to `dce_audio_create()`.
- `dce_audio.c` defines `AZ_REG_READ(reg_name)` and `AZ_REG_WRITE(reg_name, value)` as wrappers around `read_indirect_azalia_reg()` and `write_indirect_azalia_reg()`. Those helpers write an `ix...` index to `AZALIA_F0_CODEC_ENDPOINT_INDEX`, then read/write `AZALIA_F0_CODEC_ENDPOINT_DATA`.
- Companion `dcn_3_0_2_sh_mask.h` provides field masks and shifts for the registers named in this offset chunk, such as HBR capable/enable bits, hot-plug/audio enable bits, input infoframe validity, LPIB fields, and default configuration fields.

The generic DC audio code mostly references uninstanced names such as `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR`; preprocessor indirection and resource tables bind those logical names to the selected audio instance's endpoint window. This chunk provides the instance-specific generated names needed for the DCN 3.0.2 register set.

## Control Flow And Runtime Behavior

There is no executable control flow in this header. Runtime behavior appears when these indices are passed through the indirect Azalia access sequence:

1. A DCN 3.0.2 resource pool creates a `struct audio` for an endpoint instance using `audio_regs[inst]`.
2. Audio code selects an indirect endpoint register by writing an `ix...` value into the endpoint's `AZALIA_F0_CODEC_ENDPOINT_INDEX` field.
3. Audio code reads or writes `AZALIA_F0_CODEC_ENDPOINT_DATA` to observe or update the selected endpoint-local register.
4. Higher-level audio flows use those reads/writes to enable or disable audio, program sink capabilities, advertise HBR support, set HDMI/DP connection type, program speaker allocation, write audio descriptor slots, set lipsync values, and publish monitor/sink identity.

Representative flows represented by this chunk:

- Audio enable/disable: `dce_aud_az_enable()` and `dce_aud_az_disable()` manipulate `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, which corresponds to the `ixAZF0ENDPOINT*_...HOT_PLUG_CONTROL` index `0x0054` for output endpoints.
- HBR exposure: `dce_aud_az_disable_hbr_audio()` and `set_high_bit_rate_capable()` read/write `...RESPONSE_HBR` at `0x0038`.
- HDMI/DP sink programming: `dce_aud_az_configure()` programs `...CHANNEL_SPEAKER`, `...AUDIO_DESCRIPTOR0 + format_index`, `...SINK_INFO0..8`, and `...RESPONSE_LIPSYNC`. Those indirect indices are provided for every output endpoint block in this chunk.
- Status and progress snapshots: LPIB snapshot/control/timer indices (`0x0064..0x0066`) allow software to observe audio buffer position state. Output endpoints also expose audio enabled/disabled/format-changed interrupt status at `0x006c..0x006e`.
- Input audio reporting: input endpoints expose input activity/channel layout, infoframe validity, and channel allocation through `INPUT_STATUS_CONTROL`, `INFOFRAME`, and `CHANNEL_ALLOCATION`.

## State And Persistence

The macros themselves are compile-time constants and hold no mutable state. They name hardware-backed registers whose values persist in the display audio hardware until explicitly changed, reset, power-gated, or reinitialized during modeset/resume paths.

Important state categories:

- Configuration state: converter format, stream ID, digital converter control, widget control, channel/speaker allocation, multichannel enable state, multichannel mode, HBR enable/capability, coding type, and input infoframe fields.
- Sink capability state: output endpoint audio descriptors, supported size/rate parameters, pin capabilities, lipsync responses, sink information, wireless display identification, and default configuration response.
- Event/status state: pin sense, unsolicited response controls, format-changed state, digital output status, audio enable/disable interrupt status, audio format change interrupt status, input activity, and infoframe validity.
- Snapshot/counter state: LPIB and LPIB timer snapshot registers are read/lock style hardware state used to correlate buffer position and timing.
- Power/clock gating adjacency: hot-plug control includes clock gating and audio enabled semantics in companion masks; incorrect state can keep the endpoint inactive or prevent low-power behavior.

Because endpoint-local indices are reused across output and input instances, persistence is per selected endpoint window. Writing index `0x0054` through endpoint 2 affects endpoint 2 hot-plug/audio enable state; writing the same index through endpoint 5 affects endpoint 5.

## Dependencies And Integration Points

Primary dependencies:

- Generated DCN 3.0.2 direct register offset macros in the same header, especially `regAZF0ENDPOINT*_AZALIA_F0_CODEC_ENDPOINT_INDEX`, `regAZF0ENDPOINT*_AZALIA_F0_CODEC_ENDPOINT_DATA`, and corresponding input endpoint windows outside this chunk.
- Generated field masks and shifts in `dcn_3_0_2_sh_mask.h`.
- Register helper macros in the DC display code (`REG_SET`, `REG_READ`, `REG_WRITE`, `set_reg_field_value`, `get_reg_field_value`) that combine direct register offsets, field masks, and indirect indices.
- DCN 3.0.2 resource construction in `display/dc/resource/dcn302/dcn302_resource.c`, which selects the correct generated offset/mask headers for this ASIC version.
- `display/dc/dce/dce_audio.c`, which implements HDMI/DP audio capability programming, HBR capability decisions, lipsync programming, sink info publication, and audio enable/disable through these indirect Azalia registers.

Broader integration points include the DRM connector/EDID audio pipeline that fills `struct audio_info`, DisplayPort link information used to limit supported sample rates, HDMI timing calculations, suspend/resume reinitialization, hot-plug handling, and hardware diagnostics for audio enable/status interrupts.

## Risks And Edge Cases

- Generated-header drift is the largest risk. If any `ix` value is wrong, the driver will read or write the wrong endpoint-local register through a valid direct endpoint window. That kind of error may compile cleanly but corrupt audio capabilities, enable state, sink identity, or status handling.
- The chunk begins mid-`AZF0ENDPOINT1`. File-level reconciliation must include the previous chunk for the full endpoint 1 map and endpoint 0 context.
- `dcn302_resource.c` constructs output audio objects for endpoints 0 through 6, while this generated header also exposes output endpoint 7 and input endpoints 0 through 7. The final file report should distinguish generated hardware surface from currently instantiated DCN 3.0.2 resource objects.
- Output and input endpoint maps are similar but not interchangeable. Input endpoints omit sink-info and audio descriptor arrays and instead expose input-specific channel allocation, input status control, and infoframe state. Generic tooling must not assume every `AZF0*ENDPOINT` block has the same register set.
- Several logical register names are used by loops or arithmetic, especially `AUDIO_DESCRIPTOR0 + format_index`. Descriptor indices must remain contiguous from `0x0028` through `0x0035`; a gap or off-by-one would silently program the wrong audio format descriptor.
- Status and force registers have hardware-specific write semantics not expressed in this offset header. Examples include unsolicited response force, interrupt status, format-changed status, and LPIB snapshot locking. Consumers need the companion mask/spec semantics, not only the index values.
- Audio enable sequencing toggles clock-gating disable around writes to hot-plug control. Wrong hot-plug index or mask pairing can leave audio disabled, force clocks on, or race with power management.
- Reused endpoint-local indices require correct endpoint instance selection. A stale or wrong `audio_regs[inst]` direct window would make correct `ix` values operate on the wrong physical audio endpoint.

## Test Signals

Useful validation signals for this chunk are mostly build-time generated-header checks plus hardware display/audio tests:

- Compile DCN 3.0.2 AMDGPU display code with `dcn302_resource.c` including `dcn_3_0_2_offset.h` and `dcn_3_0_2_sh_mask.h`; missing or renamed macros should fail at build time.
- Generated-header consistency checks should verify that output endpoints 2 through 7 have identical local index values for matching register names, that input endpoints 0 through 7 have identical local index values for matching input register names, and that companion sh/mask definitions exist for each generated register where fields are expected.
- HDMI audio tests should verify audio enable/disable, speaker allocation, supported audio descriptor programming, lipsync reporting, HBR capability exposure, and sink name/manufacturer/port ID publication through `SINK_INFO0..8`.
- DisplayPort and eDP audio tests should exercise DP connection selection, HBR exposure under bandwidth constraints, MST audio capability programming, and sample-rate filtering from `dce_audio.c`.
- Hot-plug and modeset tests should watch `HOT_PLUG_CONTROL`, pin sense, default configuration, audio enabled/disabled interrupt status, and format-changed interrupt status across connect/disconnect and mode changes.
- Suspend/resume and runtime power tests should verify that endpoint state is restored after reset or power gating and that clock-gating disable is not left asserted.
- For input endpoints, validation should check channel allocation, input activity/channel layout status, infoframe validity, and LPIB snapshot behavior where hardware and driver paths support audio input.

## Open Questions For Merge Lane

- Confirm from adjacent chunks the complete endpoint 0 and endpoint 1 maps, including the first half of `AZF0ENDPOINT1` before line 15569.
- Determine whether DCN 3.0.2 intentionally exposes output endpoint 7 and all input endpoints without creating corresponding `struct audio` objects in `dcn302_resource.c`, or whether those are reserved/generated-for-parity surfaces.
- Cross-check `dcn_3_0_2_offset.h` against `dcn_3_0_2_sh_mask.h` for every output/input endpoint register in this chunk, especially status/interrupt and force registers where field semantics matter.
