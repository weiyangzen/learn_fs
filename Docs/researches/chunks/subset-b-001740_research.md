# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 44534-47180

## Purpose

This chunk is generated AMD DCN 3.0.1 register field metadata. It contains no executable C logic; it publishes preprocessor constants for field shifts and bit masks used when AMDGPU display code reads, writes, or updates individual fields inside DCN 3.0.1 MMIO and indexed registers.

The requested range starts in the middle of the `ABM1_DC_ABM1_HG_MISC_CTRL` field list, then covers the tail of ABM1 luma/histogram/backlight masks, complete ABM2 and ABM3 ambient-backlight-management field masks, legacy VGA sequencer/CRTC/graphics/attribute indexed register masks, and a large Azalia/HD-audio register-mask area for output codecs, descriptors, sink info, CRC counters, input codecs, root-function registers, stream latency counters, and the beginning of `AZF0ENDPOINT0` endpoint-0 fields.

Although this path is under a local `ceph-client` source mirror, the file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: mask for the same field.

The chunk contains 2,065 `#define` lines: 1,033 shift macros and 1,032 mask macros. The off-by-one is expected from the artificial chunk boundary: line 44534 begins after the first `ABM1_DC_ABM1_HG_MISC_CTRL` shift in the prior chunk, while this range still includes all visible masks for that register.

Major macro families in this slice:

- `ABM1`, `ABM2`, `ABM3`: adaptive backlight management, PWM/ambient/user/target/current/final/minimum duty-cycle levels, ABM enable/bypass, IPS color-space coefficient selection, histogram/luma-statistics read-progress and missed-frame bits, histogram bin controls, luma min/max/pixel-count thresholds, sample-rate controls, 24 histogram result registers, and master/double-buffer lock fields.
- `SEQxx`, `CRTxx`, `GRAxx`, `ATTRxx`: legacy VGA sequencer, CRTC, graphics-controller, and attribute-controller indexed fields for reset, plane maps, font selection, timing totals, blank/sync positions, cursor, pitch, address mode, graphics write/read modes, palettes, overscan, panning, and color-select controls.
- `AZALIA_F2_CODEC_CONVERTER_*`: HD-audio output-converter format, channel/stream IDs, IEC 60958 digital-converter status/control bits, stripe control, keepalive, ramp rate, GTC presentation-time embedding, audio widget capabilities, supported sizes/rates, and stream formats.
- `AZALIA_F2_CODEC_PIN_*`: output pin widget control, unsolicited responses, pin sense and presence detect, default configuration words, speaker/channel allocation, downmix data, audio descriptors, multichannel enables, lipsync, HBR, sink-info index/data, LPIB snapshot/status, coding type, format-changed notification, wireless-display identification, remote keepalive, association/status fields, and IEC 60958 channel-status overrides.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`: ELD/EDID-like audio descriptor and sink-description payload fields.
- `AZALIA_INPUT_CRC*` and `AZALIA_CRC*`: per-channel CRC result fields for input and controller CRC paths.
- `AZALIA_F2_CODEC_INPUT_*`: input converter and input pin equivalents for format, stream/channel ID, digital-converter bits, widget capabilities, pin sense/default config, channel allocation, multichannel enable/mute, HBR, LPIB, input status, infoframe, and channel-status words.
- `AZALIA_F2_CODEC_ROOT_*` and `AZALIA_F2_CODEC_FUNCTION_*`: root/function vendor, revision, subordinate-node count, power state, subsystem ID, converter synchronization, reset, group type, supported formats, and power-state capability fields.
- `AZF0STREAM0` through `AZF0STREAM15`: repeated stream FIFO-size, latency counter control, worst-case latency, cumulative latency, and cumulative request-count fields.
- `AZF0ENDPOINT0_*`: endpoint-0 output converter and pin fields, including widget capabilities, converter format, stream/channel ID, digital converter flags, stream-format/rate capabilities, stripe and ramp controls, GTC counters, pin capabilities, unsolicited response, pin sense, widget output enable, channel/speaker/downmix allocation, and audio descriptor fields 0 through 7.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display and DMUB code:

1. DCN 3.0.1 code includes `dcn_3_0_1_offset.h` and this `dcn_3_0_1_sh_mask.h` together.
2. Register-table macros build register offsets from the offset header and field metadata from this mask header.
3. Access helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `FD_MASK`, `FD_SHIFT`, and DMUB `REG_OFFSET`/field-table construction use the generated shift/mask values to isolate fields without hard-coding bit positions in handwritten driver code.
4. Higher-level display, audio, backlight, and firmware paths decide the actual order: modeset, backlight update, histogram sampling, audio stream setup, sink capability reporting, interrupt/unsolicited-response handling, CRC capture, suspend/resume, and reset.

The macros themselves do not express whether a field is read-only, sticky, self-clearing, write-one-to-clear, double-buffered, or safe to modify while a block is active. Those behaviors are hardware contract details that must be honored by the consuming driver code.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes bit-level layout for hardware-backed state:

- ABM/PWM registers hold ambient light level, user level, computed ABM target/current/final duty cycle, minimum duty cycle, sample-rate counters, histogram configuration, luma statistics, histogram results, and double-buffer/master-lock state.
- Legacy VGA indexed registers describe emulation/compatibility state for sequencer, CRTC timing, graphics plane, palette, cursor, and attribute behavior.
- Azalia codec and endpoint registers hold audio format, sample rate, channel count, channel-status bits, stream/channel IDs, pin presence/configuration, speaker/channel allocation, ELD-style descriptors, sink strings, LPIB/timestamp snapshots, keepalive, HBR, infoframe, and unsolicited-response state.
- CRC and latency/counter registers expose hardware counters and diagnostic state for audio/input streams.

Persistence is hardware-defined. Configuration fields may survive until a modeset, audio reconfiguration, power gating, suspend/resume, function reset, or ASIC reset. Status/counter/clear/ack fields may be transient, sticky, or side-effect-sensitive. This generated header intentionally does not encode those policy differences.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.1 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h` for the corresponding register offsets.
- AMD register-access helpers that derive `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` from names in this file.
- Related generated enum metadata such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h`, which names many Azalia field values for converter format, digital-converter flags, audio descriptors, channel allocation, multichannel mute/enable, and power states.

The directly observed include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`, which includes both `dcn_3_0_1_offset.h` and `dcn_3_0_1_sh_mask.h` and builds `dmub_srv_dcn301_regs` with `REG_OFFSET`, `FD_MASK`, and `FD_SHIFT`. Other DCN display code uses the same generated-header style for register programming, even when a particular macro in this chunk is only consumed through generated tables or firmware-facing register lists.

Integration points by hardware area:

- ABM/backlight programming paths use the ABM fields when enabling/disabling adaptive backlight processing, selecting histogram/luma sampling behavior, reading statistics/results, and committing PWM or ABM updates at frame boundaries.
- Display bring-up, VGA compatibility, or early/legacy paths can use the `SEQ`, `CRT`, `GRA`, and `ATTR` field masks to program indexed VGA state without open-coded bit shifts.
- Display audio paths use the Azalia converter/pin/root/stream fields for HDMI/DP audio format negotiation, stream ID routing, ELD/sink data exposure, HBR/multichannel enablement, channel-status overrides, pin presence/unsolicited response handling, and latency/CRC diagnostics.
- DMUB uses the generated field tables to let firmware-facing code manipulate DCN 3.0.1 registers with consistent offsets, masks, and shifts.

## Risks And Edge Cases

- Generated macro drift is the primary risk. A wrong shift or mask compiles cleanly but can write the wrong bits in hardware, producing silent backlight, display, or audio failures.
- The chunk starts and ends inside larger register families. The first visible ABM register is incomplete because its earlier shifts are in the prior chunk; the final `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR7` register continues at the next chunk boundary.
- ABM registers are timing-sensitive. Misusing lock, update-pending, frame-start, readback, missed-frame-clear, or sample-rate fields can cause stale luma statistics, missed histogram reads, flickering backlight, or brightness jumps.
- VGA indexed registers are compact 8-bit legacy fields. Mask/shift mistakes can affect unrelated timing, plane, cursor, or palette bits and may only show up in firmware console, boot graphics, or compatibility modes.
- Azalia fields are externally visible through HDMI/DP audio behavior. Incorrect format, channel count, sample-rate, descriptor, channel-allocation, speaker-allocation, ELD, stream-ID, or channel-status masks can cause missing audio, wrong channel layout, receiver incompatibility, HBR failures, or format-change storms.
- Status, CRC, latency, LPIB, unsolicited-response, and format-change fields may be clear-on-write or sticky. Treating them like normal configuration bits can lose diagnostics or leave interrupts asserted.
- Repeated `AZF0STREAM0` through `AZF0STREAM15` blocks are copy-sensitive. Instance-specific mistakes may only occur under high stream counts, multi-display audio, or unusual firmware routing.

## Test Signals

Useful validation is a mix of generated-header consistency and hardware behavior:

- Build AMDGPU/DCN 3.0.1 and DMUB support; missing or renamed macros should fail in register-table construction, especially in `dmub_dcn301.c`.
- Mechanically verify that every complete field in lines 44534-47180 has matching `__SHIFT` and `_MASK` macros, allowing for the known range-boundary exception at the initial `ABM1_DC_ABM1_HG_MISC_CTRL` tail.
- Diff this chunk against AMD's authoritative DCN 3.0.1 register database and adjacent DCN headers where the same ABM, VGA, and Azalia blocks are expected to be identical or intentionally changed.
- Exercise ABM/backlight on supported panels: enable/disable ABM, vary ambient/user brightness levels, check smooth duty-cycle transitions, read luma/histogram results, and test suspend/resume and modeset boundaries.
- Exercise display audio over HDMI and DP: stereo and multichannel PCM, HBR/compressed formats where supported, sample-rate changes, channel allocation, hotplug, receiver ELD parsing, silent-stream/keepalive behavior, and format-change notifications.
- Use enough active streams/endpoints to stress `AZF0STREAM0` through `AZF0STREAM15` latency and request counters, plus CRC/status paths.
- Watch kernel logs and display/audio diagnostics for missed-frame ABM reads, stuck update-pending bits, backlight flicker, VGA console corruption, audio enable/disable interrupt storms, pin-sense mismatch, LPIB/timestamp anomalies, CRC mismatches, and resume regressions.

## Cross-Chunk Notes

Adjacent chunks are required for full-file claims. The prior chunk owns the beginning of `ABM1_DC_ABM1_HG_MISC_CTRL` and earlier ABM1 fields. The next chunk continues `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR7` and the rest of the DCN 3.0.1 shift/mask namespace. The final per-file research document should merge those boundaries before making complete statements about all ABM instances or all Azalia endpoint fields.
