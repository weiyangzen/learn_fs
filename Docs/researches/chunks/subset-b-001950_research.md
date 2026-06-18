# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 52099-54467

## Scope

This chunk is a generated DCN 3.2.0 register shift/mask header segment for AMD display HDA/Azalia output endpoint indirect registers. It contains preprocessor constants only: 2,049 `#define` lines in this range, with 1,025 `__SHIFT` constants and 1,024 `_MASK` constants. There are no C functions, structs, enums, variables, allocations, locks, branches, or direct MMIO accesses here.

The range starts in the tail of `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR8`, covers the rest of endpoint 3, covers complete `AZF0ENDPOINT4`, `AZF0ENDPOINT5`, and `AZF0ENDPOINT6` output endpoint blocks, and enters `AZF0ENDPOINT7` through the beginning of `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_1`. The visible address-block markers are `azf0endpoint4_endpointind`, `azf0endpoint5_endpointind`, `azf0endpoint6_endpointind`, and `azf0endpoint7_endpointind`.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata and does not implement distributed filesystem behavior.

## Purpose

The chunk maps symbolic DCN 3.2.0 Azalia endpoint register fields to exact bit positions and masks. The matching offset header identifies the endpoint index/data MMIO registers; this shift/mask header tells register helpers how to pack and extract fields inside those endpoint-indirect registers.

The hardware surface is HDMI/DisplayPort display audio endpoint state:

- Per-endpoint converter capability and control fields for audio widget capabilities, active converter format, channel/stream ID, digital converter state, supported stream formats, supported size/rate capabilities, stripe control, ramp rate, GTC embedding, and GTC counter delta/min/max values.
- Per-endpoint pin capability and control fields for pin widget capabilities, pin capabilities, unsolicited response setup, pin sense, widget control, speaker/channel allocation, audio descriptors 0-13, multichannel routing, lipsync, HBR, sink metadata, hot-plug/audio enable state, forced unsolicited responses, and default pin configuration.
- IEC 60958 channel-status override fields for mode/source number, clock accuracy, word length, sampling frequency, original sampling frequency, sampling frequency coefficient, MPEG surround, CGMS-A, and channel numbers.
- Runtime status and diagnostic fields for association info, digital output active status, LPIB snapshot control, LPIB/timer readback, coding type, format-change state, wireless display identification, remote keepalive, audio enable status, and enable/disable/format-change interrupt status.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- `//<REGISTER>` comments group the macros for a single endpoint-indirect register.
- `// addressBlock: azf0endpointN_endpointind` comments mark repeated endpoint instances.

There are no C-callable APIs or types in this chunk. Important register families include:

- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_*`: converter-side format, stream/channel binding, digital converter, supported stream/rate descriptors, stripe control, ramp rate, and GTC timing/counter fields.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_PARAMETER_*`: pin widget and pin capability fields such as connection-list support, digital capability, unsolicited response capability, impedance/presence detect support, ELD validity, DP/HDMI identity, and HBR support.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `...13`: EDID/audio-format descriptor fields such as `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, optional stereo-frequency bits, and `DESCRIPTOR_BYTE_2`.
- `...MULTICHANNEL_ENABLE`, `...MULTICHANNEL_ENABLE2`, and `...MULTICHANNEL_MODE`: paired and odd multichannel enable, mute, and channel-ID routing fields.
- `...RESPONSE_LIPSYNC` and `...RESPONSE_HBR`: video/audio latency and HBR capable/enable fields.
- `...SINK_INFO0` through `...SINK_INFO8`: manufacturer/product IDs, description length, port IDs, and byte-packed display-name data.
- `...HOT_PLUG_CONTROL`, `...UNSOLICITED_RESPONSE_FORCE`, and `...RESPONSE_CONFIGURATION_DEFAULT`: audio endpoint exposure, clock-gating control, unsolicited response payload/force, and default pin configuration fields.
- `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `...8`: IEC 60958 channel-status override packing for source, rate, word length, copyright/CGMS-style metadata, and channel-number fields.
- `...LPIB*`, `...FORMAT_CHANGED`, `...REMOTE_KEEPALIVE`, and `...AUDIO_*_INT_STATUS`: stream position snapshots, format-change reporting, remote keepalive, and interrupt flag/mask/type fields.

In this description `n` is the endpoint number. This chunk fully covers endpoints 4-6, partially covers endpoint 3 at the start, and partially covers endpoint 7 at the end.

## Control Flow

This header has no local runtime control flow. Runtime sequencing is provided by shared AMD display audio code:

1. DCN32 resource setup includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. `display/dc/resource/dcn32/dcn32_resource.h` defines `AUD_COMMON_REG_LIST_RI(id)` using `SRI_ARR(AZALIA_F0_CODEC_ENDPOINT_INDEX, AZF0ENDPOINT, id)` and `SRI_ARR(AZALIA_F0_CODEC_ENDPOINT_DATA, AZF0ENDPOINT, id)`.
3. `display/dc/resource/dcn32/dcn32_resource.c` initializes five `audio_regs` entries and creates `dce_audio` instances with DCN32 audio register offsets plus shared audio shift/mask tables.
4. `display/dc/dce/dce_audio.c` selects an endpoint index, reads or writes the endpoint data window, and uses generated shifts/masks through helpers such as `REG_SET`, `REG_READ`, `AZ_REG_READ`, `AZ_REG_WRITE`, and `set_reg_field_value`.
5. HDMI/DP audio configuration writes HBR, lipsync, speaker allocation, audio descriptors, sink identity, hot-plug/audio-enable state, and interrupt/status fields according to the active connector, CRTC timing, DP link state, and EDID-derived `struct audio_info`.

The macros do not encode ordering. Callers must still keep clocks available while programming, choose the intended endpoint instance, respect HDMI versus DP behavior, avoid unsafe read-modify-write sequences on status fields, and follow the audio block's reset/power-gating requirements.

## State And Persistence Behavior

The chunk stores no software state. It describes hardware register state:

- Converter state persists the programmed stream format, stream ID, channel ID, digital converter control, stripe/ramp behavior, and GTC timing parameters until reprogrammed or reset.
- Pin state persists sink-facing capabilities and controls, including pin sense, widget control, speaker allocation, descriptor tables, HBR/lipsync values, multichannel routing, default configuration, sink IDs, port IDs, and display-name bytes.
- Hot-plug and audio-enable fields control whether the endpoint is exposed and whether endpoint programming can proceed with clocks forced on.
- LPIB and timer snapshot fields expose live stream-position/timing readback.
- Audio enable, disable, and format-change fields expose status and interrupt state; depending on hardware semantics, individual bits may be sticky, masked, typed, write-one-to-clear, self-clearing, or read-only.

Persistence is hardware-defined. Values can survive normal display commits but may be lost or reset across endpoint reset, audio disable, display power gating, suspend/resume, or GPU reset. The header only provides bit geometry, not access semantics.

## Dependencies And Integration Points

This chunk depends on exact generated-name alignment with the DCN32 register header family:

- The matching offset file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`.
- DCN32 resource code consumes endpoint offsets via `AUD_COMMON_REG_LIST_RI(id)` and endpoint field shifts/masks via `DCE120_AUD_COMMON_MASK_SH_LIST`.
- Shared audio code in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` uses generic Azalia endpoint register names; per-generation register tables bind those generic operations to the correct DCN32 endpoint instance.
- The hardware access path is indirect: endpoint index/data MMIO registers select an Azalia codec endpoint register, then the field masks in this header pack or decode the selected endpoint-data value.
- EDID/audio parsing and display-link configuration feed the values written into descriptor, HBR, lipsync, sink-info, and channel/speaker fields.

The naming contract is important. A missing macro normally fails compilation, but an incorrect numeric shift or mask compiles cleanly and can silently misprogram audio hardware.

## Risks And Edge Cases

- Numeric drift from the DCN 3.2.0 register specification is the primary risk. Bad masks or shifts can corrupt endpoint format programming, sink capability reporting, HBR, lipsync, speaker allocation, multichannel routing, LPIB snapshots, or interrupt handling.
- Endpoint repetition is copy-sensitive. `AZF0ENDPOINT4`, `AZF0ENDPOINT5`, and `AZF0ENDPOINT6` should be structurally consistent where the hardware spec says they are; an instance-specific generator error may break only one connector or audio endpoint.
- The chunk boundaries are artificial. Endpoint 3 begins before this range, and endpoint 7 continues after it. The merge lane should combine adjacent chunks before claiming complete coverage of endpoint 3 or endpoint 7.
- Audio descriptors are packed tables. Wrong `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, stereo-frequency, or descriptor-byte masks can make the OS or sink see incorrect LPCM/compressed-audio capabilities.
- Sink-info strings are byte-packed across registers. A one-byte shift error can corrupt monitor names or overwrite neighboring descriptor bytes.
- Hot-plug and clock-gating fields are sequencing-sensitive. Incorrect masks can leave audio disabled, keep clocks forced on, or cause endpoint writes to be ignored during power transitions.
- Status, format-change, and interrupt fields may be side-effect-sensitive. Generic read-modify-write helpers require exact masks to avoid losing or fabricating audio enable, disable, and format-change events.
- The `AUDIO_ENABLED_MASK` field name and the generated `_MASK` suffix create similar-looking tokens; automated checks must distinguish field names from mask constants.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU display code with DCN32 support enabled, especially `dcn32_resource.c`, `dcn32_resource.h`, and shared DCE audio code, to catch missing or renamed generated symbols.
- Run generated-header consistency checks that each complete endpoint register family has expected `__SHIFT` and `_MASK` pairs, masks fit in 32 bits, and repeated endpoint 4-6 layouts match where specified.
- Diff this range against AMD's authoritative DCN 3.2.0 register database and neighboring DCN 3.x generated headers, focusing on endpoint instance boundaries and side-effecting control/status fields.
- Exercise HDMI and DisplayPort audio on DCN32 hardware across multiple physical connectors/endpoints, including hotplug, audio enable/disable, format changes, EDID capability programming, LPCM, multichannel, HBR, and DP MST audio where supported.
- Validate sink metadata surfaced to the OS: manufacturer/product IDs, port IDs, display-name length, and all display-name bytes from `SINK_INFO4` through `SINK_INFO8`.
- Check runtime logs and register dumps around suspend/resume, display modesets, connector unplug/replug, clock gating, and power gating for missing audio devices, stale capabilities, audio dropouts, bad HBR/lipsync state, or stuck interrupts.
- Use LPIB snapshot/timer readback and format-change interrupt paths as diagnostic signals when audio playback position or format renegotiation behaves incorrectly.

## Cross-Chunk Notes

Previous chunks own the beginning of endpoint 3, including its converter fields and early pin-control descriptor fields before the `AUDIO_DESCRIPTOR8` tail visible here. Later chunks own the remainder of endpoint 7 after `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_1` and the following input-endpoint Azalia blocks. The final per-file report should merge those adjacent chunks before presenting complete DCN 3.2.0 Azalia endpoint coverage.
