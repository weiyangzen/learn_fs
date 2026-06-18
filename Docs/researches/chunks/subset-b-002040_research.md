# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 32541-34936

## Purpose

This chunk is generated AMD DCN 3.2.1 display-controller register field metadata. It contains no executable C code; it publishes `#define` constants for field shifts and masks used to pack and unpack MMIO register values in the AMDGPU display driver.

The assigned range covers the tail of the `DP3` DisplayPort stream/link block, the complete visible `DIG3` digital encoder front/back-end block, most of the `DP4` DisplayPort block, and the beginning of the `DIG4` digital encoder block. The range contains 2,172 `#define` entries plus generated register-name comments. Every field appears as a pair or set of `__SHIFT` and `_MASK` macros that consumers feed into register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and field-description tables.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, or local control constructs in this span. The public surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position for a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: bitmask for the same field.
- Register comments such as `//DP4_DP_SEC_CNTL2` and address-block comments such as `// addressBlock: dce_dc_dio_dp4_dispdec`, which group the generated symbols by display hardware block.

Major field families in this chunk:

- `DP3_DP_DPHY_*`: DisplayPort PHY control fields for analog-test lane selection, FEC enable/status shadows, scrambler selection, bypass/skew bypass, training pattern selection, explicit 8b/10b symbols, PRBS generation, scrambler behavior, CRC enable/control/results, MST CRC phase status, fast-training timing/status, HBR2 pattern control, and blanking-symbol swap/load state.
- `DP3_DP_SEC_*`: secondary-data packet and audio fields for stream enable, ASP/ATP/AIP/ACM/ISRC/MPG/GSP enable bits, packet framing windows, audio `N`/`M` programming and readback, timestamp mode, ASP packet coding/priority/version, generic stream packet send/pending/deadline/line-number controls, enable double-buffer status, metadata transmission, and DB lock/taken/pending status.
- `DP3_DP_MSE_*`, `DP3_DP_MSO_*`, and `DP3_DP_DSC_CNTL`: MST/MSE stream allocation fields for rate ratio, SAT source/encryption/slot count tables and readback, SAT update, link timing, blank-code/timestamp/zero-encoder controls, MSO split-link secondary-data enables, and a DSC mode bit.
- `DP3_DP_ALPM_*` and `DP3_DP_AUXLESS_ALPM_*`: DisplayPort low-power/AUX-less ALPM controls for main-link PHY sleep/standby sends and pending bits, sleep sequence mode, line-number scheduling, LFPS wakeup timing, immediate wake/FEC enable controls, hardware-mode enable/disable, frame-number fields, and wakeup interrupt mask/status/clear fields.
- `DIG3_DIG_*`: digital encoder front-end/back-end fields for source selection, stereosync, digital bypass, split-link pixel grouping, input pixel select, Dolby Vision enable/missed metadata, symbol clock status, TMDS pixel encoding/color format, output CRC, test/random/static patterns, FIFO enable/reset/read-level/calibration/error, and version/forced-disable controls.
- `DIG3_HDMI_*`: HDMI metadata/control/status/audio fields, including keepout, scrambling, clock-channel rate, packet generator version, error ack/mask, unscrambled-control line, deep-color enable/depth, active AVMUTE, audio/VBI packet errors, audio layout, ACR packet source/timing, VBI/infoframe/generic packet send/continuous/line-reference/update-lock controls, immediate send pending bits, generic-packet line fields, DB lock/taken/pending fields, ACR CTS/N programming and status for 32/44.1/48 kHz families, and GC AVMUTE/packing phase controls.
- `DIG3_TMDS_*`: TMDS sync phase, control-character enables, feedback selection/delay, stereosync control selection, sync-character patterns, control bits, DC balancer controls, and generated control 0/1/2/3 data selection, delay, invert, modulation, feedback, and pattern output fields.
- `DP4_DP_*`: the same high-level DisplayPort link/stream/DPHY/secondary-packet/MSE/MSO/ALPM/GSP/AUX-less ALPM families as `DP3`, but for instance 4. This begins with `DP4_DP_LINK_CNTL`, `DP4_DP_PIXEL_FORMAT`, MSA timing/colorimetry/misc fields, link framing, stream timing, video `M/N`, interrupt controls, and then continues through DPHY, secondary-data, MST/MSE, DSC, DB, metadata, GSP8-GSP11, and AUX-less ALPM fields.
- `DIG4_DIG_*` and initial `DIG4_HDMI_*`: the beginning of digital encoder instance 4, covering front-end source/bypass/Dolby/TMDS-color fields, output CRC, test pattern, FIFO controls, HDMI metadata control, HDMI core control, and the start of HDMI status.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior comes from AMD display code that includes this file together with `dcn_3_2_1_offset.h` and then builds register/field tables.

The key integration path in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes both `dcn/dcn_3_2_1_offset.h` and `dcn/dcn_3_2_1_sh_mask.h`. That file defines token-pasting helpers such as `SR(...)` and `SRI(...)` for register addresses; the corresponding field macros from this chunk are consumed by the broader DC register helper layer when code writes or reads selected fields.

Typical runtime sequencing, outside this generated file, is:

1. DCN 3.2.1 resource construction selects register offsets and field masks for each display block instance.
2. Link encoder, stream encoder, HDMI/DP audio, packet, and modeset code chooses an instance such as `DP3`, `DIG3`, `DP4`, or `DIG4`.
3. Register helper macros combine the instance address from the offset header with the field shift/mask from this header.
4. Driver code programs link training, stream enable/disable, pixel format, MSA timing, secondary-data packets, HDMI packet generation, audio clock regeneration, MST slot allocation, DSC mode, ALPM, and test/debug paths.

The macros do not encode sequencing rules. Correct consumers must still order clock/power enablement, link training, video stream enablement, packet double-buffer updates, interrupt clear/ack writes, FEC/DSC transitions, MST allocation updates, and suspend/resume restoration according to hardware requirements.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes fields in MMIO-backed display hardware state.

Represented hardware state includes:

- Per-instance DP PHY state for FEC, scramblers, training patterns, explicit symbol patterns, PRBS, CRC capture, fast training, HBR2 patterns, and PHY low-power transitions.
- Per-instance DP stream state for link status, pixel format, stream enable/status, MSA timing/colorimetry/misc fields, video `M/N`, VBID overrides, secondary-data packet framing, metadata transmission, audio `M/N`, and packet collision/mute status.
- MST/MSO/MSE state for stream allocation tables, slot counts, encryption bits, rate updates, link timing, MSO secondary-data enables, and SAT status readback.
- Generic stream packet state for GSP0-GSP11 enable/send/line/deadline/pending controls and double-buffer pending status.
- ALPM/AUX-less ALPM state for PHY sleep/standby sends, scheduled wake/FEC enable line numbers, LFPS timing, hardware-mode ALPM enable, frame/line counters, wakeup interrupts, and immediate wakeup behavior.
- DIG/HDMI/TMDS state for selected source, bypass, stereo sync, Dolby Vision metadata, FIFO calibration/error status, output CRC, test patterns, HDMI scrambling/deep-color/keepout/error handling, metadata/infoframe/generic-packet scheduling, ACR CTS/N programming and readback, AVMUTE, and TMDS control-pattern generation.

Persistence is hardware-defined. Configuration fields generally retain values until modeset, link reconfiguration, power gating, suspend/resume, or ASIC reset. Status, pending, clear, ack, readback, interrupt, and calibration fields may be read-only, sticky, self-clearing, or write-one-to-clear depending on the register. This generated header gives only bit locations; it does not identify access type or side effects.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.2.1 register database and must stay consistent with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`, which defines the matching `regDP3_*`, `regDIG3_*`, `regDP4_*`, and `regDIG4_*` register offsets and base indexes.
- AMD display register helper code that interprets `__SHIFT`/`_MASK` pairs as field descriptors for `REG_*` operations.
- DCN 3.2.1 resource initialization in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, the direct include site found in this tree.
- DIO/link encoder, stream encoder, HDMI audio/packet, MST, DSC, ALPM, and hotplug/modeset paths that program DP and DIG blocks through generated register tables.

The repeated instance naming is a major integration contract. `DP3` fields must align with `regDP3_*` offsets, `DIG3` with `regDIG3_*`, `DP4` with `regDP4_*`, and `DIG4` with `regDIG4_*`. Cross-generation comparison shows similar fields in nearby generated headers such as `dcn_3_2_0_sh_mask.h` and `dcn_3_5_1_sh_mask.h`, but the DCN 3.2.1 file is the authoritative mask/shift source for this ASIC generation.

## Risks And Edge Cases

- Generated mask drift is the central risk. A wrong shift or mask compiles cleanly but can update the wrong bits in MMIO, corrupting unrelated hardware state in the same register.
- Instance copy errors are hard to detect statically. `DP3`, `DIG3`, `DP4`, and `DIG4` are structurally similar, so a mismatched instance prefix may only fail on connectors routed to one physical display engine.
- Chunk boundaries are artificial. The first line is the final mask from the previous `DP3_DP_VID_INTERRUPT_CNTL` register, and the final line stops immediately after the start of `DIG4_HDMI_STATUS`; adjacent chunks are required for complete file-level conclusions.
- Status and command fields are side-effect-sensitive. Pending, taken, clear, ack, interrupt clear, wakeup send, immediate send, and deadline-missed fields can be sticky or self-clearing; using the right bit location is necessary but not sufficient.
- MST/MSO fields are table-like and timing-sensitive. Wrong SAT source, slot-count, update, rate, or status masks can produce failures only under MST, MSO, DSC, or multi-stream bandwidth pressure.
- HDMI packet and audio fields interact with vertical blank timing. Incorrect generic-packet line, update-lock, immediate-send, ACR, AVMUTE, or metadata masks can cause intermittent infoframe loss, audio dropouts, or sink-specific HDMI failures.
- ALPM and FEC fields interact with link training and low-power states. Bad wake/sleep/FEC scheduling can create resume-only, low-power-only, or panel-specific blanking issues.
- This file provides no type safety. All macros are integer constants, so build success only proves symbol availability, not hardware correctness.

## Test Signals

Useful validation signals include:

- Build AMDGPU/DC with DCN 3.2.1 support enabled; missing or renamed field macros should fail in resource and display block register-table initialization.
- Mechanically verify that each visible field in lines 32541-34936 has a `__SHIFT` and matching `_MASK` macro, and that each mask is consistent with the implied bit position and field width.
- Diff this span against the same register families in `dcn_3_2_0_sh_mask.h` and AMD's authoritative DCN 3.2.1 register database; intentional differences should be tied to ASIC changes.
- Exercise displays routed through DP/DIG instances 3 and 4, including hotplug, link training, stream enable/disable, mode changes, color-depth/pixel-format changes, suspend/resume, and high-bandwidth modes.
- Test DP secondary-data paths: audio playback, audio mute, metadata packets, GSP packets, ISRC/MPG/ASP/AIP/ACM behavior, packet collision handling, DB pending/taken state, and metadata line scheduling.
- Test HDMI paths on `DIG3` and `DIG4`: scrambling, deep color, AVMUTE, metadata/infoframes, generic packets, ACR CTS/N values, audio at 32/44.1/48 kHz families, and TMDS control/test patterns.
- Validate MST/MSO/MSE behavior on `DP3` and `DP4`: SAT allocation, rate updates, payload timing, slot-count readback, MSO secondary-data enables, DSC mode, and multi-stream reconfiguration.
- Exercise ALPM/AUX-less ALPM and FEC transitions, especially low-power entry/exit, wakeup interrupts, immediate wakeup, FEC enable timing, and resume from panel/link idle states.
- Watch kernel logs and display diagnostics for link-training failures, AUX/ALPM wake failures, stuck pending bits, packet deadline misses, audio dropouts, HDMI packet errors, FIFO errors, CRC mismatches, MST payload errors, and display blanking isolated to connector instances 3 or 4.

## Cross-Chunk Notes

Earlier chunks contain the start of the `DP3` block, including the register fields before `DP3_DP_DPHY_CNTL` and most of `DP3_DP_VID_INTERRUPT_CNTL`. Later chunks continue `DIG4_HDMI_STATUS` and the rest of digital encoder instance 4. The final merged per-file research should combine adjacent chunks before making whole-file claims about all DCN 3.2.1 display register masks or all DP/DIG instances.
