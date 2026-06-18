# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 39375-41781

## Scope And Purpose

This chunk is a generated AMD DCN 3.1.4 register shift/mask header slice. It contains only preprocessor constants and generated grouping comments: `__SHIFT` macros define bit positions, `_MASK` macros define raw 32-bit field masks, and `// addressBlock:` comments delimit display I/O hardware register blocks. There are no functions, structs, enums, executable statements, allocations, locks, or software-owned storage in this range.

The purpose of the slice is to expose the field layout ABI used by AMDGPU Display Core and DMUB-facing DCN 3.1.4 code when programming digital display output hardware. The companion `dcn_3_1_4_offset.h` header supplies register addresses and base indices; this file supplies the bit packing for those registers. Runtime code consumes these symbols through AMD display register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `SRI`, `SE_SF`, and related generated register-list macros.

The range starts mid-register in the `VPG1_VPG_GSP_FRAME_UPDATE_CTRL` field list, continues through VPG1, AFMT1, DME1, DIG1, and DP1 display-output blocks, then covers VPG2, AFMT2, DME2, and the beginning of DIG2. It ends in the middle of `DIG2_HDMI_GENERIC_PACKET_CONTROL0`, so the following DIG2 HDMI generic packet masks are outside this assigned chunk. The slice contains 2,169 `#define` lines: 1,090 shift definitions and 1,079 mask definitions.

This file lives under a local `ceph-client` source mirror, but the content is AMDGPU Display Core register metadata, not Ceph filesystem logic.

## Register Blocks Covered

The tail of `dce_dc_dio_dig1_vpg_vpg_dispdec` covers VPG1 packet update and payload fields:

- Generic secondary packet frame-update and immediate-update control for generic packets 0 through 14, with corresponding pending bits.
- `VPG_GENERIC_STATUS` lock/conflict reporting and conflict clear.
- VPG memory light-sleep controls and memory power state.
- ISRC1/2 indexed data access, MPEG infoframe payload bytes, and MPEG info update fields.

The `dce_dc_dio_dig1_afmt_afmt_dispdec` block covers AFMT1 audio-format and audio-packet state:

- VBI packet controls for ACP and HDMI audio packet scheduling.
- Audio packet layout override, layout select, channel enable mask, DP audio stream ID, HBR override, and IEC 60958 override.
- Audio infoframe payload fields such as checksum, channel count, coding type, checksum offset, extension type, channel allocation, level shift, downmix inhibit, and LFE playback level.
- IEC 60958 channel-status fields across `AFMT_60958_0`, `AFMT_60958_1`, and `AFMT_60958_2`.
- Audio CRC enable/source/channel/count and CRC result/done readback.
- Audio ramp/test controls, AFMT status, audio sample send/update controls, infoframe update, interrupt status, audio source select, and AFMT memory power force/disable/state.

The `dce_dc_dio_dig1_dme_dme_dispdec` block defines DME1 controls for DME enable, stream/MTN mode, dummy stream generation, DME AUX select and connection state, plus DME memory power force/disable/state.

The `dce_dc_dio_dig1_dispdec` block covers DIG1 front-end/back-end and HDMI/TMDS control:

- DIG front-end/back-end enable, source select, CRC controls/results, clock/test/random pattern controls, FIFO controls/status, DB control, version, and force-disable fields.
- HDMI metadata packet scheduling, HDMI control/status, audio delay, ACR packet control and N/CTS values for 32 kHz, 44.1 kHz, and 48 kHz families, ACR status readback, VBI packets, audio/MPEG infoframe controls, generic packet controls 0 through 14, generic immediate send/pending bits, and HDMI GC fields.
- TMDS controls for clock pattern selection, control characters, feedback, stereosync control, sync character patterns, control bits, DC balancer controls, and CTL generation.

The `dce_dc_dio_dp1_dispdec` block is the largest part of the chunk. It covers DP1 link and stream control:

- Link control, pixel format, MSA colorimetry/misc fields, DP configuration, video stream enable/mode/blanking controls, steer FIFO, video M/N timing, link framing, VBID/MSA placement, and video stream-disable interrupt fields.
- DPHY control for FEC, scrambler selection, bypass/skew behavior, training-pattern selection, symbol patterns, 8b/10b state, PRBS generation, scrambler controls, DPHY CRC, MST CRC phase status, fast training, and HBR2 pattern support.
- Secondary-data-packet controls for audio stream packets, timestamps, audio copy management, GSP0 through GSP11, ISRC, MPEG packets, generic packet priorities, line references, send/pending/active/deadline status, and SDP framing widths.
- DP audio N/M and readback registers, ASP packet coding/version/channel override, and audio mute/collision state.
- MST/MSE rate, slot allocation table, slot-allocation update, link timing, status readbacks, and misc blank/timestamp/zero-encoder fields.
- DPIA spare, MSA timing parameters, MSO controls, DSC enable/slice/pixel-clock controls, SEC control extensions, DB control, MSA VBID misc, metadata transmission, ALPM controls, GSP8 through GSP11 controls, GSP enable double-buffer pending status, and AUX-less ALPM timing/wakeup/FEC/interrupt controls.

The `dce_dc_dio_dig2_vpg_vpg_dispdec`, `dce_dc_dio_dig2_afmt_afmt_dispdec`, and `dce_dc_dio_dig2_dme_dme_dispdec` blocks repeat the same VPG, AFMT, and DME surfaces for instance 2. The final `dce_dc_dio_dig2_dispdec` section starts DIG2 and runs through shifts for HDMI generic packet control 0.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit in a 32-bit register.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask in the register word.
- Instance prefixes such as `VPG1`, `AFMT1`, `DME1`, `DIG1`, `DP1`, `VPG2`, `AFMT2`, `DME2`, and `DIG2` are part of the ABI and select the generated hardware instance.
- Generated comments such as `// addressBlock: dce_dc_dio_dp1_dispdec` and `//DP1_DP_SEC_CNTL` are not compiled, but they are important for source-tree-aligned reconciliation because they describe hardware grouping and partial chunk boundaries.

Important field families include:

- Generic packet data and scheduling: `VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG_GENERIC_PACKET_DATA`, `VPG_GSP_FRAME_UPDATE_CTRL`, `VPG_GSP_IMMEDIATE_UPDATE_CTRL`, HDMI `GENERIC_PACKET_CONTROL*`, DP `DP_SEC_GSP*`, and DP metadata transmission controls.
- Audio formatting and packetization: AFMT channel enable/layout, stream ID, HBR override, IEC 60958 channel status, audio infoframe fields, audio CRC, ramp/test controls, HDMI ACR and DP audio M/N fields.
- Link and PHY control: DP pixel/MSA/config/stream fields, DPHY FEC/scrambler/training/pattern/CRC/PRBS fields, TMDS control characters and DC balancing, HDMI scrambling/deep-color/error fields.
- MST/MSO/DSC and bandwidth allocation: DP MSE rate, slot allocation tables/status, MSO mode/format/pixel mode, DSC enable/slice/pixel-clock fields, and MSA timing parameters.
- Power and status: VPG/AFMT/DME memory power fields, FIFO reset/error/calibration fields, HDMI and DP interrupt/ack/clear/status fields, fast-training and ALPM status, and GSP double-buffer pending status.

The primary include site found in this tree for this exact generated header pair is `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which includes both `dcn/dcn_3_1_4_offset.h` and `dcn/dcn_3_1_4_sh_mask.h`. Shared DCN31 display code also defines the consumer shapes for these register families, for example `display/dc/dcn31/dcn31_afmt.h` maps AFMT fields through `AFMT_DCN31_REG_LIST(id)` and `DCN31_AFMT_MASK_SH_LIST(mask_sh)`.

## Control Flow

This chunk has no direct runtime control flow. Its effective flow is compile-time symbol binding followed by runtime register access in other code:

1. A DCN 3.1.4 consumer includes the generated offset and shift/mask headers.
2. Register-list macros bind instance-specific register addresses from `dcn_3_1_4_offset.h` with field shifts and masks from this header.
3. Runtime display, link, audio, HDMI, DP, DMUB, or diagnostic code calls register helpers that combine a register address with the relevant shift/mask pair.
4. Hardware latches, reports, clears, or consumes the resulting MMIO field according to the register's hardware semantics.

The declaration order mirrors the hardware register database. Within most register groups, all `__SHIFT` definitions precede the corresponding `_MASK` definitions. Instance 2 VPG/AFMT/DME definitions intentionally repeat the instance 1 shape with a different prefix. The DP1 block is ordered from stream/link controls through DPHY, secondary packet, MST/MSO/DSC, metadata, and ALPM controls.

The assigned lines have two partial boundaries. The first lines are the end of `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`, with the earlier generic0 through generic5 pending shifts in the previous chunk. The final lines stop after `DIG2_HDMI_GENERIC_PACKET_CONTROL0` shifts, before its masks and later DIG2 HDMI controls.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes hardware register state in the DCN 3.1.4 display I/O subsystem.

Writable state represented by these fields includes packet payload bytes, frame/immediate send requests, audio infoframes, IEC 60958 channel status, audio source and channel layout, audio ACR/N/M values, HDMI scrambling/deep color, TMDS patterns, DP video stream enablement, DPHY training/test controls, FEC and scrambler controls, MST slot allocation, DSC enablement, MSO format/mode, ALPM timing and wake/FEC scheduling, FIFO reset/configuration, and memory power force/disable controls.

Readback or status state includes pending packet updates, generic-packet lock/conflict state, memory power state, CRC results and valid bits, FIFO reset-done/error/calibration, HDMI active AVMUTE and packet errors, DPHY CRC and MST phase status, fast-training state and completion, secondary-packet collision/mute status, MSE slot-allocation status, GSP send pending/active/deadline status, double-buffer pending flags, ALPM current state and wake interrupt state, and DME AUX connection state.

Persistence is hardware-defined. Programmed control fields usually remain until rewritten, reset, power-gated, or reinitialized during display modeset, suspend/resume, hot-plug, link retraining, or firmware-assisted sequences. Status, pending, interrupt, and ACK/clear fields are volatile and may be edge-sensitive or write-one-to-clear. This header does not encode access type, reset values, volatility, clear-on-read behavior, sequencing requirements, or read-only/write-only constraints.

## Dependencies And Integration Points

The critical dependency is the matching generated offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h` supplies register addresses and base indices. Examples in the companion file include `regAFMT1_AFMT_AUDIO_PACKET_CONTROL2` at `0x2175`, `regDP1_DP_LINK_CNTL` at `0x2208`, `regVPG2_VPG_GENERIC_PACKET_ACCESS_CTRL` at `0x2268`, and `regDIG2_HDMI_GENERIC_PACKET_CONTROL0` at `0x229b`, all with base index `2`.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c` includes this header pair for DCN 3.1.4 DMUB register access.
- `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.h` defines the AFMT register-list and field-list shape used by DCN31-family AFMT/audio code. The AFMT1/AFMT2 macros in this chunk must match that consumer shape.
- DCN link, HDMI, DP, audio, and diagnostic code under `drivers/gpu/drm/amd/display/dc` consumes this kind of generated metadata through shared register helper conventions rather than by manually spelling numeric masks.

Integration is mostly by token concatenation. A missing or renamed generated macro generally fails compilation when a register-list macro expands. A wrong numeric mask or shift is more dangerous because it can compile cleanly and then write or read the wrong hardware bits.

## Risks And Edge Cases

- The chunk starts in the middle of `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`; merge/reconciliation must combine it with the previous chunk before presenting VPG1 frame-update control as complete.
- The chunk ends in the middle of `DIG2_HDMI_GENERIC_PACKET_CONTROL0`; the mask definitions for that register and the rest of DIG2 HDMI/DIG/DP2 surfaces belong to later chunks.
- The register families are highly repetitive across instances. Prefix drift such as using `AFMT1` where `AFMT2` is intended, or `DIG1` where `DIG2` is intended, can target the wrong display output instance.
- Many fields are packed into adjacent single-bit controls. Generic packet controls, DP GSP controls, FIFO controls, interrupt ACK/mask bits, and ALPM wake/FEC controls are vulnerable to read-modify-write mistakes that preserve the wrong neighbor bits.
- Several masks use the high bit, for example `0x80000000L` in generic packet update-lock disable, ALPM sleep state, and other fields. Consumers should treat register values as unsigned 32-bit quantities to avoid signedness surprises.
- Status and ACK/clear fields share the same generated macro style as ordinary configuration fields. Examples include HDMI error ACK, DP stream-disable ACK, DPHY MST phase error ACK, fast-training complete ACK, ALPM interrupt clear, and packet collision ACK. Generic write helpers must respect side effects.
- Packet timing fields are line/frame sensitive. Wrong line references, any-line settings, priorities, or pending-bit handling can cause missed generic packets, stale HDR/metadata packets, or packet collisions without a direct software error.
- DP link controls are sequencing-sensitive. FEC, scrambler, training pattern, PRBS, fast training, MSE slot allocation, DSC, MSO, and ALPM fields interact with link training, DPCD state, sink capabilities, and stream timing.
- Memory power controls for VPG, AFMT, and DME can invalidate dependent packet/audio/DME programming if forced or disabled while the corresponding block is active.
- Cross-generation reuse is risky. DCN 3.1.4 names resemble DCN 3.1.2 and other DCN headers, but the offset and sh/mask headers must be paired by the same ASIC generation.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware integration:

- Build AMDGPU display/DMUB code with DCN 3.1.4 support enabled to catch missing generated macro names in `dmub_dcn314.c` and shared DCN31-family register-list consumers.
- Preprocess representative `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `SRI`, and `SE_SF` users to confirm token concatenation resolves to the intended `VPG1`, `AFMT1`, `DME1`, `DIG1`, `DP1`, `VPG2`, `AFMT2`, `DME2`, and `DIG2` symbols.
- Compare this chunk against `dcn_3_1_4_offset.h` and the authoritative AMD register database to verify every covered register selector has the expected shift/mask layout.
- Run static generated-header checks for paired shift/mask definitions, 32-bit mask fit, expected non-overlap within each register, and intentional partial-boundary exceptions at the start and end of this slice.
- Exercise HDMI audio on DCN 3.1.4 hardware: channel layout, IEC 60958 values, HBR override, ACR/N/CTS programming, audio infoframe updates, AVMUTE, deep color, scrambling, and VBI/generic packet scheduling.
- Exercise DisplayPort link training, FEC, DPHY CRC, PRBS/test patterns, fast training, MST slot allocation, DSC/MSO paths, secondary-data packets, metadata transmission, and AUX-less ALPM transitions.
- Verify hot-plug, modeset, suspend/resume, link retrain, audio enable/disable, metadata update, and display reset paths while watching for stale pending bits, missed packets, packet collisions, FIFO errors, and memory-power state mismatches.

## Open Cross-Chunk Questions

- Whole-file reconciliation should join this with adjacent chunks before describing complete VPG1 frame-update or DIG2 HDMI generic-packet coverage.
- Whole-file research should map how DCN 3.1.4 resource construction instantiates the DIO/DIG/DP/AFMT/VPG blocks and whether every generated instance is exposed on every product.
- Whole-file research should compare DCN 3.1.4 DIO field layouts with DCN 3.1.2 to distinguish intended carry-over from ASIC-specific additions such as AUX-less ALPM, MSO, DSC, and extended GSP controls.
