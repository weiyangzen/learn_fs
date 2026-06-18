# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 55342-57717

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.1.5 register-field shift/mask header. It contains C preprocessor constants only: `_SHIFT` macros for bit positions, `_MASK` macros for raw register masks, register-name comments, and address-block comments. There are no functions, structs, enums, branches, loops, allocations, locks, or software-owned state objects in the range.

The chunk starts in the tail of the `AZF0STREAM15` stream-indirect Azalia definitions, then covers the indexed Azalia display-audio endpoint field layout for endpoint instances 0 through 3, and ends in the beginning of endpoint instance 4. Endpoints 0 through 3 are complete in this range; endpoint 4 is partial and continues after line 57717. The definitions describe the hardware ABI used to pack and decode fields in HDA/Azalia codec converter and pin-control registers for HDMI/DisplayPort audio over display links.

The exported surface is generated metadata. The matching offset header supplies register/index addresses such as `mmAZF0ENDPOINTx_AZALIA_F0_CODEC_ENDPOINT_INDEX`, `mmAZF0ENDPOINTx_AZALIA_F0_CODEC_ENDPOINT_DATA`, and `ixAZF0ENDPOINTx_AZALIA_F0_*`; this header supplies the bit layout for values read from or written through those indirect endpoint windows.

## Hardware Surface Covered

The first few definitions finish `AZF0STREAM15` stream latency/debug layout:

- `AZF0STREAM15_AZALIA_FIFO_SIZE_CONTROL` tail masks for maximum FIFO size and maximum latency support.
- `AZF0STREAM15_AZALIA_LATENCY_COUNTER_CONTROL` reset bit.
- `AZF0STREAM15_AZALIA_WORSTCASE_LATENCY_COUNT`, `AZF0STREAM15_AZALIA_CUMULATIVE_LATENCY_COUNT`, and `AZF0STREAM15_AZALIA_CUMULATIVE_REQUEST_COUNT`, each exposing a full 32-bit counter field.
- `AZF0STREAM15_AZALIA_STREAM_DEBUG` exposing a debug data shift.

The bulk of the range is repeated endpoint-indirect layout for `azf0endpoint0_endpointind` through `azf0endpoint4_endpointind`. Endpoint instances 0 through 3 include the same broad register families:

- Converter widget capability and control registers, including audio widget capabilities, converter format, channel/stream ID, digital converter status/control, supported stream formats, supported size/rates, stripe control, ramp rate, GTC presentation-time embedding/debug, and GTC counter delta/min/max readbacks.
- Pin widget capability and control registers, including pin audio widget capabilities, pin capabilities, unsolicited response, pin sense, widget output enable, channel/speaker allocation, ACP packet data, audio descriptors 0 through 13, multichannel enable/mute/channel-ID controls, lipsync response, HBR response, sink information registers, hot-plug/audio-enable control, forced unsolicited response payload, configuration default response, multichannel enable2/mode, IEC 60958 channel-status override registers 0 through 8, association info, digital output status, LPIB snapshot/LPIB/timer snapshot, coding type, format-changed response, wireless display identification, remote keepalive, and audio enable/disable/format-changed interrupt status.

Endpoint 4 is present only through the early pin-capability fields in this chunk. The covered endpoint 4 definitions include converter debug/capabilities/control, supported formats/rates, stripe/ramp/GTC fields, pin audio widget capabilities, and the beginning of pin parameter capabilities through `TRIGGER_REQUIRED__SHIFT`. The remaining endpoint 4 fields are outside this work item.

## Important Macros And Field Groups

The generated API follows the standard register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- `// addressBlock: ...` comments identify the hardware index/data aperture for following definitions.
- `AZF0ENDPOINT<n>_` prefixes are instance-specific. The field layouts are mostly identical across endpoints, but callers must select the right endpoint's index/data MMIO registers and the right indirect register index from the companion offset header.

Important converter fields include:

- `*_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` advertises HDA widget traits such as channel capability, amplifier presence, format override, stripe support, processing widget, unsolicited response, connection list, digital widget, power control, LR swap, delay, and widget type.
- `*_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` packs number of channels, bits per sample, sample base divisor/multiple/rate, and PCM/non-PCM stream type. These fields map directly to audio stream format programming.
- `*_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID` packs channel ID and stream ID.
- `*_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER` exposes `DIGEN`, validity/config/preemphasis/copy/non-audio/professional bits, channel status category code, and `KEEPALIVE`.
- `*_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `*_PARAMETER_SUPPORTED_SIZE_RATES` advertise stream format, sample-rate, and sample-size support.
- `*_CODEC_CONVERTER_CONTROL_GTC_EMBEDDING`, `*_GTC_COUNTER_DELTA`, `*_GTC_COUNTER_DELTA_MIN`, and `*_GTC_COUNTER_DELTA_MAX` support presentation-time embedding and timing-delta diagnostics.

Important pin-control fields include:

- `*_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `*_CODEC_PIN_PARAMETER_CAPABILITIES` describe the exposed HDA pin widget, including HDMI/DP capability, output/input capability, jack-detect-style flags, VREF control, EAPD, and widget type.
- `*_CODEC_PIN_CONTROL_CHANNEL_SPEAKER` packs speaker allocation, channel allocation, HDMI/DP connection flags, extra connection information, LFE playback level, level shift, and downmix inhibit.
- `*_CODEC_PIN_CONTROL_ACP_DATA` packs ACP packet index, audio-info support, ACP packet enable, ACP type, and type-dependent bytes.
- `*_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0..13` expose short audio descriptor fields. Descriptor 0 has an additional `SUPPORTED_FREQUENCIES_STEREO` byte; all descriptors share max channels, supported frequencies, and descriptor byte 2 fields.
- `*_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` packs enable/mute/channel-ID controls for channel pairs 01, 23, 45, and 67. `*_MULTICHANNEL_ENABLE2` covers odd-numbered channel controls 1, 3, 5, and 7. `*_MULTICHANNEL_MODE` selects multichannel mode.
- `*_CODEC_PIN_CONTROL_RESPONSE_LIPSYNC` exposes video and audio latency response bytes. `*_RESPONSE_HBR` exposes HBR capability and enable.
- `*_CODEC_PIN_CONTROL_SINK_INFO0..8` pack monitor manufacturer/product ID, sink description length, port IDs, and up to 18 display-name bytes.
- `*_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` controls clock gating disable, reports clock-on state, and carries the `AUDIO_ENABLED` bit.
- `*_CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT` exposes HDA default-configuration fields such as sequence, default association, misc, color, connection type, default device, location, and port connectivity.
- `*_PIN_CONTROL_CODEC_CS_OVERRIDE_0..8` expose IEC 60958 channel-status override fields for mode/source, clock accuracy, word length, sampling frequency, original sampling frequency, coefficients, MPEG surround, CGMS-A, and channel numbers.
- `*_CODEC_PIN_CONTROL_LPIB*`, `*_CODING_TYPE`, `*_FORMAT_CHANGED`, `*_WIRELESS_DISPLAY_IDENTIFICATION`, and `*_REMOTE_KEEPALIVE` provide playback position, format-change, wireless-display, and keepalive surfaces.
- `*_AUDIO_ENABLED_INT_STATUS`, `*_AUDIO_DISABLED_INT_STATUS`, and `*_AUDIO_FORMAT_CHANGED_INT_STATUS` pack flag, mask, and type bits for endpoint audio events.

## Control Flow And State Behavior

This header has no executable control flow. Runtime flow is indirect:

1. DCN resource code builds an audio register table for each audio instance using endpoint index/data MMIO offsets.
2. Audio code writes an indirect endpoint register index through `AZALIA_F0_CODEC_ENDPOINT_INDEX`.
3. It reads or writes endpoint data through `AZALIA_F0_CODEC_ENDPOINT_DATA`.
4. Register helpers and `set_reg_field_value()` use these `_SHIFT` and `_MASK` constants to pack fields into the endpoint data value.
5. Hardware latches, reports, or clears the represented Azalia/HDA codec state.

The state represented by this chunk is hardware state. Persistent configuration includes converter format, channel/stream ID, digital converter enable/status bits, speaker/channel allocation, ACP enable/data, short audio descriptors, multichannel enable/mute/channel IDs, lipsync response values, HBR capability/enable, sink information, audio enable, configuration default, IEC 60958 override fields, coding type, wireless display ID, and remote keepalive. Volatile readback and telemetry include latency counters, GTC counter deltas, pin sense, digital output status, LPIB snapshots, format-changed state, audio enable status, and interrupt/status flag fields. Side-effect-prone fields include latency counter reset, clear-style GTC/min/max controls, unsolicited response force, interrupt flags/masks, LPIB snapshot lock, and hot-plug/audio-enable sequencing.

The macros do not encode ordering. Callers must still obey HDA/Azalia endpoint access sequencing, choose the correct endpoint instance, avoid racing display hotplug/modeset state, preserve unrelated fields during read/modify/write updates, and respect whether a field is read-only, write-only, latched, or side-effecting according to the hardware specification.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.5 offset header, which provides the concrete endpoint index/data MMIO addresses and indirect `ixAZF0ENDPOINT*`/`ixAZF0STREAM15*` register indices. A shift/mask constant from this file is only meaningful when paired with the correct generated offset/index symbol.

The main software integration path is the Display Core audio implementation:

- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines the audio register, shift, and mask structures. `AUD_COMMON_REG_LIST(id)` binds each audio instance to `AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_ENDPOINT_DATA`. The mask/shift list includes `AZALIA_ENDPOINT_REG_INDEX`, `AZALIA_ENDPOINT_REG_DATA`, and global codec function fields.
- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` implements indirect endpoint access through `write_indirect_azalia_reg()` and `read_indirect_azalia_reg()`. It then uses endpoint registers covered by this chunk to enable/disable audio, configure speaker allocation, ACP data, audio descriptors, HBR capability, lipsync values, sink information, hot-plug/audio-enable state, and display-name/port-ID information.
- DCN resource files such as `display/dc/resource/dcn31/dcn31_resource.c` and `display/dc/resource/dcn314/dcn314_resource.c` build `audio_regs[]`, `audio_shift`, and `audio_mask` tables using `AUD_COMMON_REG_LIST(id)` and `DCE120_AUD_COMMON_MASK_SH_LIST(...)`, then call `dce_audio_create(ctx, inst, &audio_regs[inst], &audio_shift, &audio_mask)`.
- Stream encoder and AFMT code integrate with this endpoint state by selecting Azalia audio sources and programming HDMI/DP audio packet and IEC 60958 channel-status transmission. Endpoint programming describes the codec/pin surface exposed to the OS audio stack, while AFMT/stream-encoder programming controls packet insertion on the display link.
- Older amdgpu DCE paths use similar Azalia endpoint indirect programming and the same conceptual register families for response configuration, lipsync, channel/speaker allocation, descriptors, and hot-plug audio enable.

Because this file is generated, most direct references are macro-expansion based. Missing or renamed macros tend to fail compilation where a resource table or helper macro expands. Incorrect numeric masks or shifts can compile cleanly and cause runtime audio misconfiguration.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.5 register specification is the main risk. A wrong shift/mask can silently write the wrong endpoint bits, corrupting audio format, channel mapping, HBR capability, sink information, hot-plug state, or interrupt masking.
- This chunk starts in the middle of `AZF0STREAM15_AZALIA_FIFO_SIZE_CONTROL`; its low-field shifts/masks are in the previous chunk. The final merged report should preserve that neighboring context.
- This chunk ends in the middle of endpoint 4 pin capability definitions. Endpoint 4 should not be treated as complete until the next chunk is reconciled.
- Endpoint blocks are highly repetitive. Copy/paste or generation errors that swap endpoint numbers can still produce valid macro names but target the wrong audio endpoint.
- The display audio code often uses endpoint 0 shift/mask names in resource mask tables for the generic index/data fields, while the register address table selects the endpoint instance. The final report should distinguish generic endpoint index/data masks from per-endpoint indirect register field masks.
- Several fields describe read-only hardware capabilities or status, while driver code writes some related registers as part of endpoint exposure. For example, `dce_audio.c` comments that `LFE_PLAYBACK_LEVEL` is specified as read-only yet is written in one path. Hardware-version differences around such fields need careful validation.
- Audio descriptor 0 has a stereo supported-frequency byte not present in the same way for descriptors 1 through 13. Treating all descriptor registers as identical can lose stereo-rate information for LPCM.
- Hot-plug audio enable and clock-gating fields are sequencing-sensitive. `dce_aud_az_enable()` and `dce_aud_az_disable()` temporarily set `CLOCK_GATING_DISABLE`, update `AUDIO_ENABLED`, then clear clock gating disable. A mask error here can leave audio disabled or clocks unexpectedly gated.
- Interrupt/status fields use flag, mask, and type bits in the same register. Tests and diagnostics should avoid treating mask bits as event flags or vice versa.
- Full-width telemetry fields such as GTC deltas, latency counts, LPIB, and sink port IDs should be handled as unsigned 32-bit values. Partial extraction would produce misleading diagnostics.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build coverage for AMDGPU Display Core with DCN 3.1.5 headers included. This catches malformed macros, missing generated names, and include-time syntax errors.
- Generated-header comparison against the authoritative DCN 3.1.5 register database, especially for endpoint instance repetition and endpoint 4 continuation across chunk boundaries.
- Runtime display-audio smoke tests on DCN 3.1.5 hardware: HDMI audio enumeration, DisplayPort audio enumeration, hotplug enable/disable, audio playback after modeset, and audio recovery after suspend/resume or link retraining.
- EDID/audio capability propagation tests. Programmed short audio descriptors, speaker allocation, HBR capability, sample rates, and sink information should match the connected sink and appear correctly to the OS audio stack.
- HBR and multichannel playback tests for 2-channel, 6-channel, 8-channel, and high-sample-rate modes. These exercise descriptor, HBR, channel allocation, multichannel enable, and IEC 60958 fields.
- Register dump checks around `dce_aud_az_configure()`, `dce_aud_az_enable()`, and `dce_aud_az_disable()`. Only intended masked fields should change, and endpoint instance selection should match the active stream/audio object.
- Interrupt/status observation for audio enabled, audio disabled, and audio format changed events. Flag/mask/type bits should decode consistently with hardware events.
- Latency/GTC/LPIB diagnostics during playback. Counter reset and readback fields should behave monotonically or reset only when explicitly requested.

## Open Questions For Merge

- The final per-file report should connect this chunk with the preceding stream chunks and following endpoint 4 chunk so `AZF0STREAM15` and `AZF0ENDPOINT4` are not described as incomplete hardware blocks.
- The exact DCN 3.1.5 product resource file that includes this generated header may be outside this chunk's immediate search surface; the merge lane should tie the header to the full ASIC include chain used by the relevant DCN 3.1.5 resource module.
