# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 28782-30999

## Purpose

This chunk is generated AMD DCN 3.5.0 shift/mask register-field metadata. It contains preprocessor constants only; there are no executable C functions, structs, enums, storage objects, branches, locks, allocations, or direct MMIO operations. Each visible field is represented by a bit-position macro named `<REGISTER>__<FIELD>__SHIFT` and a bit-isolation macro named `<REGISTER>__<FIELD>_MASK`.

The requested range covers stream-output field definitions for the end of `DIG1`, the complete visible `DIG2`/`DP1`-centered stream-encoder/link slice, and the beginning of `DP2`. It starts mid-register with `DIG1_HDMI_GENERIC_PACKET_CONTROL8__HDMI_GENERIC11_LINE_MASK`, then proceeds through DIG/HDMI/TMDS fields, DisplayPort stream/link fields, VPG2 packet-generator fields, AFMT2 audio-formatter fields, and DME2 metadata-engine fields. It ends mid-register at `DP2_DP_MSA_TIMING_PARAM2__DP_MSA_VSTART_MASK`; the matching `DP_MSA_HSTART_MASK` is on the next line outside this chunk.

The range has 2,228 `#define` lines: 1,109 `__SHIFT` macros and 1,119 `_MASK` macros. The count is intentionally imbalanced because both boundaries split field pairs. Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no APIs in the function-call sense. The public interface is the generated macro namespace consumed by AMDGPU Display Core register helpers:

- `<REGISTER>__<FIELD>__SHIFT`: field bit offset for packing or extracting values.
- `<REGISTER>__<FIELD>_MASK`: field mask for preserving, clearing, or extracting bits during read-modify-write operations.

Major macro families in this chunk are:

- `DIG1_*`: the tail of the `DIG1` HDMI/TMDS stream-encoder field set. It includes HDMI generic-packet line selection, generic-packet double-buffer pending flags, HDMI double-buffer control, HDMI ACR `CTS`/`N` values for 32/44.1/48 kHz families and readback status, AFMT audio clock gating, DIG back-end source/HPD routing, TMDS sync/control-character generation, DC balancer controls, TMDS control-bit generation, and DIG type/version.
- `DP1_*`: a broad DisplayPort instance-1 field set. It covers link status/training completion, pixel format, MSA colorimetry/misc/timing/VBID fields, video stream enable/status/defer/change keepout, steer FIFO and TU overflow, DPHY internal scrambler controls, video `M/N` generation, link framing, video interrupts, DPHY training pattern/lane control/symbol/8b10b/PRBS/scrambler/CRC/fast-training controls, secondary-data packet controls, audio `M/N`, MST payload and slot-allocation controls, MSO controls, DSC enablement, GSP packet controls, metadata transmission, and AUX-less ALPM controls.
- `VPG2_*`: Video Packet Generator instance-2 fields for generic-packet access/data, MPEG info packets, ISRC data access, generic status, memory power, and GSP frame/immediate update controls for packet slots 0 through 11.
- `AFMT2_*`: Audio Formatter instance-2 fields for VBI and audio packet control, audio info words, IEC 60958 channel-status words, audio ramp control, audio CRC control/results, status/interrupt/ack/mask fields, audio-source selection, infoframe control, and AFMT memory-power state.
- `DME2_*`: Display Metadata Engine instance-2 fields for metadata engine enable/update/reset, interrupt flag/ack/mask, payload select, compression and priority controls, virtual start address, buffer mode, stall controls, stutter mode, memory power controls, and memory shutdown/deep-sleep status.
- `DIG2_*`: the next stream-encoder instance, including DIG front-end/back-end control, clock/test patterns, FIFO controls, output CRC, HDMI control/status/metadata/audio/ACR/generic-packet fields, HDMI double-buffering, TMDS controls, and DIG version.
- `DP2_*`: the start of DisplayPort instance 2, structurally mirroring the `DP1` families from link control through DPHY, secondary-data packet, MST/MSE, and early MSA timing fields. The chunk stops before the complete `DP2` timing/MSO tail.

The field layouts are highly repetitive. `DIG2` mirrors the earlier DIG stream-encoder pattern, and `DP2` mirrors the `DP1` DisplayPort pattern. `VPG2`, `AFMT2`, and `DME2` are instance-specific copies of packet/audio/metadata helper blocks used by stream encoder instance 2.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by AMDGPU Display Core and DMUB-facing code:

1. DCN 3.5 code includes `dcn_3_5_0_offset.h` with this `dcn_3_5_0_sh_mask.h` companion.
2. Resource, DIO, stream-encoder, link-encoder, IRQ, and DMUB macros token-paste register and field names into per-block register tables.
3. Driver objects store offsets, masks, and shifts for the relevant hardware instance.
4. Modeset, link-training, audio, packet, metadata, hotplug, suspend/resume, and debug paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and polling helpers; those helpers use these constants to touch only the requested MMIO fields.

The constants do not encode ordering. Consumers must still sequence stream enable/disable, clock and memory-power transitions, double-buffer updates, HDMI audio clock regeneration, DP link training, DPHY pattern generation, MST slot allocation, secondary-data packet transmission, interrupt acknowledgement, and link/audio power transitions according to hardware rules.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO-backed DCN 3.5 display hardware state:

- HDMI/DIG state for generic-packet line placement, double-buffer pending/taken bits, HDMI ACR values, AFMT clock enable/status, DIG source/HPD routing, TMDS control symbols, DC balancing, FIFO/test-pattern state, output CRC, metadata packets, and HDMI status/error bits.
- DisplayPort video state for link-training completion/status, stream enable/status, pixel encoding/depth, MSA timing/colorimetry/VBID, video `M/N`, steer FIFO/TU sizing, framing, MSO/DSC, and stream-disable interrupts.
- DisplayPort PHY and validation state for lane control, training-pattern selection, DPHY symbols, 8b10b reset/disparity, PRBS generation, scrambler controls, CRC capture and MST CRC phase status, HBR2 pattern control, fast-training state/ack/mask, and AUX-less ALPM wake controls.
- Secondary-data and audio packet state for DP SEC stream/ASP/ATP/AIP/ACM/GSP/MPG enables, packet line references, send/pending/deadline flags, framing widths, audio mute/status, audio `M/N` and readback values, timestamp mode, ASP coding/version/channel-count override, metadata packets, and HDMI generic packets.
- MST/MSE state for payload rate control, rate-update pending, stream allocation table source/slot counts and status, 16-MTP keepout, link frame/line timing, blank/timestamp/zero-encoder controls, and slot allocation update.
- `VPG2`, `AFMT2`, and `DME2` state for video metadata packet data, ISRC/MPEG info, generic packet status, audio packet controls, IEC 60958 channel status, audio CRC/status interrupts, audio source selection, infoframe controls, metadata-engine payload buffers, and block memory power.

Persistence is hardware-defined. Configuration fields generally retain values until reprogrammed, reset, power-gated, or restored after suspend/resume. Status, interrupt, pending, ack, clear, CRC, FIFO, packet-send, and training fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while related clocks and power domains are enabled. This generated header does not record access type, reset value, side effects, or polling requirements.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DCN 3.5 register database and with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which provides matching MMIO register offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c` and `dmub_dcn35.h`, which include the generated headers and build DMUB register/field tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c` and related resource headers, which include this mask header for DCN35 resource construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_stream_encoder.h`, whose stream-encoder field lists reference HDMI generic packets, HDMI ACR fields, DP SEC fields, AFMT clock fields, FIFO fields, metadata packet fields, and stream mapper fields through token-pasted `SE_SF(...)` macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_link_encoder.h`, whose link-encoder field lists reference DIG back-end, TMDS, and DP secondary-data fields through `LE_SF(...)` macros.

Functional integration points include HDMI/DP stream encoder programming, DP link encoder setup, DP secondary-data packet scheduling, HDMI generic/info/metadata packet generation, audio packet generation, DP MST/MSO/DSC support, DPHY validation/training, output CRC diagnostics, VPG/AFMT/DME packet-memory power management, and DMUB-mediated register access.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while touching an adjacent hardware field, causing display blanking, audio loss, link-training failure, packet corruption, or stuck interrupts.
- The range is boundary-partial. The first line is only the mask for `DIG1_HDMI_GENERIC_PACKET_CONTROL8__HDMI_GENERIC11_LINE`, whose shift is above the chunk. The last line omits `DP2_DP_MSA_TIMING_PARAM2__DP_MSA_HSTART_MASK`, which appears immediately after the chunk. Several apparent shift/mask count imbalances are caused by these artificial boundaries and by fields whose names end in `MASK`.
- Repeated instances are copy-sensitive. `DP1` and `DP2`, plus `DIG1`/`DIG2` and `VPG2`/`AFMT2`/`DME2`, have similar layouts but instance-specific names; a generator or manual edit error may affect only one connector, link, stream, or packet engine.
- Side-effect fields are mixed with configuration fields. Interrupt flags, ack bits, masks, pending bits, send triggers, CRC valid bits, training-start bits, reset bits, and memory-power controls require access semantics that are not visible in this header.
- DP link and DPHY fields are timing-sensitive. Incorrect training pattern, scrambler, PRBS, 8b10b disparity, fast-training, lane-count, or CRC fields can produce failures that only appear at certain rates, lane counts, MST topologies, or after resume.
- Packet scheduling fields are interoperability-sensitive. Bad HDMI generic packet line placement, DP SEC/GSP send/deadline fields, metadata packet controls, or audio packet controls can cause missing HDR metadata, bad infoframes, audio mutes, packet collisions, or receiver-specific failures.
- MST/MSO/MSE fields depend on external allocation logic. Incorrect rate, slot-count, SAT update, keepout, or status handling can break multi-stream transport while single-stream DP continues to work.
- Memory-power and clock fields in AFMT/VPG/DME/DIG blocks can make later register writes ineffective if consumers program packet or audio registers while the block is powered down or clock-gated.

## Test Signals

Useful validation combines generated-header checks with DCN 3.5 hardware behavior:

- Build AMDGPU Display Core with DCN35 enabled. Missing or renamed fields should fail in DIO stream/link encoder, resource, IRQ, DMUB, and register-table construction paths.
- Mechanically compare lines 28782-30999 against a regenerated AMD DCN 3.5.0 register database. Account for the known boundary exceptions at `DIG1_HDMI_GENERIC_PACKET_CONTROL8__HDMI_GENERIC11_LINE` and `DP2_DP_MSA_TIMING_PARAM2__DP_MSA_HSTART`.
- Cross-check this range against `dcn_3_5_0_offset.h` so every register family used here has a matching offset/base-index entry for the same instance.
- Exercise HDMI on the affected DIG instances: modesets, generic/info/metadata packet updates, ACR programming, audio playback, AV mute, TMDS modes, deep color, output CRC, hotplug, suspend/resume, and packet double-buffer updates.
- Exercise DP on instances corresponding to `DP1` and `DP2`: link training, rate/lane changes, pixel-format changes, MSA timing programming, stream enable/disable, DSC/MSO where supported, MST payload allocation, and AUX-less ALPM wake paths.
- Validate DP secondary-data and audio behavior with audio playback, metadata/HDR packet changes, GSP sends on fixed and any-line modes, packet collision/deadline status, audio mute/status, and `M/N` readback checks.
- Validate DPHY diagnostic paths with training patterns, PRBS/scrambler settings, CRC capture, MST CRC phase status, HBR2 pattern controls, and fast-training start/complete/ack behavior.
- Monitor kernel logs, display diagnostics, and sink behavior for link-training timeouts, black screens, FIFO/TU overflow, CRC mismatches, metadata loss, audio dropouts, stuck packet pending bits, interrupt storms, memory-power timeouts, and resume-only failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of the `DIG1` stream-encoder field group, including the shift half of the first visible line here. Later chunks continue `DP2` MSA timing, MSO, DSC, GSP, metadata, AUX-less ALPM, and subsequent DCN 3.5 register families. The final per-file research document should merge adjacent chunks before making whole-file claims about every `DIG`, `DP`, `VPG`, `AFMT`, or `DME` instance.
