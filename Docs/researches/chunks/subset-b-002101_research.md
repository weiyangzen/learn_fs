# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 30987-33204

## Purpose

This chunk is a generated DCN 3.5.1 register field shift/mask table for the AMD display core. It does not implement executable logic; it provides compile-time constants that let AMDGPU display code encode and decode hardware register fields for DisplayPort, HDMI/DIG, video packet generator, audio formatter, and Display Micro-Engine blocks.

The range begins in the middle of the `DP2` DisplayPort block, covers most of the `VPG3`, `AFMT3`, `DME3`, `DIG3`, and `DP3` stream-encoder/register block, and ends at the start of the `VPG4`/`AFMT4` block. The matching address definitions live in `dcn_3_5_1_offset.h` as `reg*` macros with `_BASE_IDX` companions; consumers include this header and use helper macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `REG_SET*`, and `REG_UPDATE*` to perform packed register operations.

## Important register groups

- `DP2_*`: tail fields for the second DisplayPort stream. The chunk completes MSA timing masks, then defines MSO, DSC enable, secondary-data packet controls, generic secondary packet line scheduling, doorbell status, MSA/VBID miscellaneous fields, metadata transmission, ALPM and AUX-less ALPM controls, and GSP8-GSP11 payload bytes. These fields control DP main-stream attributes, multi-stream output packet replication, DSC mode, secondary packet dispatch, and panel self-refresh/low-power transitions.
- `VPG3_*`: video packet generator 3 fields for indexed generic packet access/data, frame-update and immediate-update triggers for generic packets 0-14, status/conflict bits, memory power controls, ISRC packet data, and MPEG infoframe payload bytes. This block owns the packet memory and update handshakes for the third stream encoder's video/generic packet path.
- `AFMT3_*`: audio formatter 3 fields for VBI/HDMI packet controls, audio packet layout/channel/stream IDs, HDMI audio infoframe bytes, IEC 60958 channel status, audio CRC, ramp controls, formatter status, ACP/infoframe interrupt/control, audio source selection, and AFMT memory power. These are the field constants used when HDMI/DP audio metadata and audio packet generation are programmed for stream 3.
- `DME3_*`: Display Micro-Engine 3 control and memory-control fields. The control register includes clock enable, gating, halt, ready/active state, cache invalidate, stall controls, and memory unit reset. The memory-control register exposes address, data, write enable, and auto-increment fields for DME memory access.
- `DIG3_*`: DIG front-end/back-end/HDMI/TMDS fields for stream encoder 3. The chunk covers FE/BE enables and source selection, FIFO and output CRC controls, test and random patterns, AFMT binding, HDMI control/status, HDMI generic packet scheduling/data selection, metadata and infoframe controls, deep-color/guard-band bits, ACR packet controls and counters, HDMI/VBI audio packet controls, TMDS control symbols and DC-balancer patterns, and TMDS sync/stereo controls.
- `DP3_*`: the full third DisplayPort block in this chunk. It covers video stream format/timing, M/N values, MSA colorimetry and timing, link control/framing, DPHY training/scrambling/PRBS/CRC/fast-training fields, MST/MSE link timing and slot allocation table fields, DP secondary audio and generic-packet controls, metadata transmission, MSO packet enables, DSC mode, GSP8-GSP11 data registers, doorbell/status fields, ALPM/AUX-less ALPM controls, and final MSA/VBID fields.
- `VPG4_*` and `AFMT4_*`: the beginning of the fourth stream packet/audio block. The chunk includes VPG4 generic packet access/data, frame-update and immediate-update controls, status, memory power, ISRC and MPEG fields, then starts AFMT4 VBI/audio packet control and audio info fields before the line range stops.

## API and type surface

The only API surface is preprocessor constants named as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. Each pair describes a bitfield inside a 32-bit hardware register. Examples include `DP3_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE__SHIFT`, `DP3_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE_MASK`, `DIG3_HDMI_GENERIC_PACKET_CONTROL0__HDMI_GENERIC0_SEND_MASK`, and `VPG3_VPG_GSP_FRAME_UPDATE_CTRL__VPG_GENERIC0_FRAME_UPDATE_PENDING_MASK`.

The field constants are coupled to offset macros such as `regDP3_DP_SEC_CNTL`, `regDIG3_HDMI_GENERIC_PACKET_CONTROL0`, `regVPG3_VPG_GSP_FRAME_UPDATE_CTRL`, `regAFMT3_AFMT_AUDIO_PACKET_CONTROL2`, and `regDME3_DME_CONTROL` in `dcn_3_5_1_offset.h`. The DC and DMUB helper layers turn those generated names into register descriptors:

- `reg_helper.h` uses `FN`, `REG_SET*`, and `REG_UPDATE*` style macros to apply masks and shifts while preserving unrelated fields.
- `dmub_reg.h` defines `FD_SHIFT(reg_name, field)` and `FD_MASK(reg_name, field)` as direct token concatenations to these constants.
- `dcn351_resource.c`, `irq_service_dcn351.c`, and `dmub_dcn351.c` include both `dcn_3_5_1_offset.h` and this mask header, so this generated data feeds DC resource construction, IRQ register programming, and DMUB register initialization.

There are no C types, functions, structs, or inline helpers in this range.

## Control flow and programming model

There is no runtime control flow in the header itself. The practical flow is:

1. DCN 3.5.1 display code includes the offset and shift/mask headers for the ASIC.
2. Resource initialization computes absolute register addresses from `reg*_BASE_IDX` and `reg*`.
3. Stream encoder, packet generator, audio formatter, DMUB, or IRQ code chooses a register and field by symbolic name.
4. Register helpers combine a field value with the `*_MASK` and `*__SHIFT` constants.
5. The driver writes the packed value to MMIO, or reads a register and extracts fields for status/diagnostics.

Several groups imply hardware handshakes. `DP*_DP_SEC_CNTL2` and `DP*_DP_SEC_CNTL7` expose send, pending, deadline-missed, active, and idle-send bits for generic secondary packets. `VPG*_VPG_GSP_FRAME_UPDATE_CTRL` and `VPG*_VPG_GSP_IMMEDIATE_UPDATE_CTRL` expose trigger and pending bits for packet-memory updates. `DP*_DP_DB_CNTL` exposes doorbell pending/taken/ack state. DPHY, MSE/SAT, ALPM, and AUX-less ALPM fields represent state-machine configuration and status for link training, MST payload slot allocation, and low-power entry/exit.

## State and persistence behavior

The macros hold no state. State lives in the GPU display hardware registers they describe. Values written through these fields persist until changed by display modeset/reprogramming, stream disable, link retraining, power-gating/reset, suspend/resume restore, or GPU reset.

The state is stream-instance-specific. `DP2` and `DP3` use similar field layouts but target different stream/link register instances. `VPG3`, `AFMT3`, `DME3`, and `DIG3` are tied to the third stream encoder path; `VPG4` and `AFMT4` begin the corresponding fourth path. Any code using these constants must pair the field with the correct register instance and base index.

Some fields directly affect hardware-visible output:

- DP timing/MSA, colorimetry, VBID, M/N, stream format, and pixel-format fields define the main video stream interpretation by sinks.
- Secondary packet and VPG generic packet fields determine whether infoframes, metadata, ISRC, MPEG, audio, DSC PPS, and other sideband packets are emitted and at which lines.
- MST/MSE SAT fields assign stream sources and slot counts for multi-stream transport.
- DPHY and link-framing fields affect training patterns, scrambling, PRBS, HBR2 patterns, CRC capture, and lane/symbol behavior.
- AFMT and HDMI/TMDS fields affect HDMI audio packet generation, IEC 60958 channel status, HDMI deep color and guard bands, ACR timing, and TMDS control-symbol generation.
- ALPM and AUX-less ALPM fields affect low-power panel/link behavior and must remain consistent with sink/panel capabilities.

## Dependencies and integration points

- `dcn_3_5_1_offset.h`: provides the `reg*` address macros paired with these field constants. In this ASIC header, the relevant offsets use `reg` prefixes rather than older `mm` prefixes.
- `drivers/gpu/drm/amd/display/dc/inc/reg_helper.h`: token-pastes register/field names into mask and shift constants and performs masked read/modify/write operations.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h`: exports the same field constants into DMUB register tables through `FD_MASK` and `FD_SHIFT`.
- `drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`: includes the generated DCN 3.5.1 headers while building resource register lists for DCN351.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`: loads generated masks/shifts into DMUB-facing register metadata.
- `drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`: includes the same generated register pack for ASIC-specific interrupt handling.
- Higher-level DC stream encoder, VPG, AFMT, link-training, MST, HDMI, and DMUB code depends on these constants indirectly through register-list structs and helper macros, rather than by hand-coding numeric bit positions.

## Risks and edge cases

- Generated register drift: the shift/mask header and offset header must be generated from the same register database. A wrong shift, mask, or address silently programs the wrong hardware bits.
- Instance mismatch: `DP2` vs `DP3`, `VPG3` vs `VPG4`, and `AFMT3` vs `AFMT4` are easy to confuse because many fields repeat with identical layouts. Pairing a field group with the wrong register instance can corrupt another stream encoder path.
- Packed-register writes: most registers contain multiple independent fields. Callers must preserve unrelated bits using masked updates, especially for status/control registers that combine trigger, pending, clear, and enable bits.
- Width truncation: many fields are narrow nibbles or bytes (`GSP*_PB*`, channel enables, packet-line selectors, SAT slot counts, color/depth selectors). Values must be range-checked before shifting.
- Handshake ordering: trigger bits such as `SEND`, `FRAME_UPDATE`, `IMMEDIATE_UPDATE`, doorbell fields, and metadata transmission bits have pending/status companions. Writing new payload data without waiting for pending bits to clear can lose packets or report conflicts.
- Read/clear hazards: status bits such as conflict, deadline-missed, CRC result/status, doorbell taken/ack, and ALPM state bits may be write-one-to-clear or hardware-updated in surrounding documentation. Generic full-register writes risk clearing useful diagnostic state.
- Link-training and MST fragility: DPHY, MSE/SAT, MSA, and M/N fields are sink-visible and timing-sensitive. Invalid combinations can cause blank displays, failed link training, bad MST payload allocation, or incorrect DSC/secondary packet behavior.
- Power behavior: ALPM, AUX-less ALPM, memory power, clock-enable, and clock-gating fields can change idle power and wake behavior. They also interact with suspend/resume and panel self-refresh flows.

## Test signals

- Build signal: compile AMDGPU display code with DCN351 enabled. Missing or renamed mask/shift symbols should fail at compile time through `FD_MASK`, `FD_SHIFT`, `REG_SET*`, or register-list expansion.
- Generated-header consistency: compare each `REGISTER__FIELD__SHIFT` with its `_MASK` width and position, and verify every used field has a corresponding `regREGISTER` entry in `dcn_3_5_1_offset.h`.
- Cross-instance consistency: verify repeated `DP2`/`DP3`, `VPG3`/`VPG4`, and `AFMT3`/`AFMT4` field layouts where the hardware generation expects identical encodings.
- DisplayPort runtime tests: modeset DP streams, retrain links, exercise DSC, MST, MSA timing/colorimetry, secondary packets, and ALPM/AUX-less ALPM entry/exit while checking for link-training failures, blanking, and sink metadata correctness.
- HDMI/audio runtime tests: validate HDMI output, audio enumeration, channel layouts, IEC 60958 status, ACR stability, audio CRC paths, and deep-color/TMDS behavior through stream encoder 3 and the AFMT3 path.
- Packet-generator tests: update VPG generic packet payloads, ISRC, MPEG, metadata, and DSC PPS packets while polling pending/conflict bits; confirm packets appear on expected frame/line boundaries.
- Power-management tests: suspend/resume, display off/on, PSR/ALPM transitions, and memory/light-sleep paths should preserve or restore programmed register state without stale packet data.
- Debug/diagnostic tests: read DPHY CRC, output CRC, doorbell status, deadline-missed, conflict, and ALPM status fields under stress to catch ordering bugs in register programming.
