# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 39486-41907

Chunk: `subset-b-001767`
Covered source range: lines 39486-41907 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h`

## Purpose

This chunk is part of AMD's generated DCN 3.0.2 register field mask header. It does not implement executable driver behavior. Its purpose is to publish C preprocessor constants for bit shifts and bit masks used when AMDGPU display code reads, writes, or read-modify-writes DCN digital output, HDMI, DisplayPort, video packet generator, audio format, metadata engine, and DisplayPort secondary-data registers.

The file pairs with DCN register address headers and is directly included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`. Resource construction and hardware block descriptors use these generated names to bind register lists, masks, and shifts for DCN 3.0.2 ASICs. Consumers typically do not use the numeric literals directly; they use register helper macros and hardware sequencer code that combine an address macro with the matching `__SHIFT` and `_MASK` constants.

This range covers the tail of the DIG3 HDMI generic packet block, the remaining DIG3 HDMI/TMDS/backend fields, a full DP3 display-port output block, the beginning-to-end DIG4-side VPG/AFMT/DME/DIG HDMI/TMDS block, and the beginning of DP4 through `DP4_DP_MSE_SAT0`. The high-level register families are:

- DIG3 HDMI generic packet immediate-send, line-selection, double-buffer, guard-band/control, ACR, audio clock, backend enable/source, TMDS control, lane enable, and force-disable fields.
- DP3 DisplayPort link, stream, main stream attribute, video timing, PHY training, 8b/10b, PRBS, scrambler, CRC, fast training, secondary packet, MST/MSE, MSO, DSC, metadata, GSP, ALPM, and double-buffer fields.
- DIG4 VPG generic packet access/data, GSP update/status, memory power, ISRC, and MPEG info fields.
- AFMT4 audio packet, HDMI/DP audio info, IEC 60958 channel-status, audio CRC, ramp/test audio, audio status, audio source, and memory power fields.
- DME4 metadata engine enable, stream selection, HUBP requestor, double-buffer, and memory power fields.
- DIG4 frontend, output CRC, test pattern, FIFO status, HDMI metadata/control/status, ACR/VBI/infoframe/generic packet, HDMI double-buffer, ACR status, audio clock, backend, TMDS, lane enable, and force-disable fields.
- DP4 DisplayPort link, stream, MSA, timing, PHY, CRC, fast training, secondary packet, audio M/N, MSE rate, and the start of SAT0 slot-allocation fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, typedefs, or runtime APIs in this chunk. The public surface is a generated macro API. Each field normally appears as two macros:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to shift a raw field value into or out of a register dword.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate or update that field.

The prefix identifies the display block instance and register domain. `DIG3_*` and `DIG4_*` describe digital encoder/frontend/backend and HDMI/TMDS fields for links 3 and 4. `DP3_*` and `DP4_*` describe DisplayPort link-output registers for DP instances 3 and 4. `VPG4_*`, `AFMT4_*`, and `DME4_*` describe the video packet generator, audio format, and metadata engine blocks associated with DIG4.

Important DIG3 fields in this range include:

- `DIG3_HDMI_GENERIC_PACKET_CONTROL5` immediate-send and pending flags for generic packets 0-14.
- `DIG3_HDMI_GC` AVMUTE, continuous AVMUTE, default phase, packing phase, and packing override fields.
- `DIG3_HDMI_GENERIC_PACKET_CONTROL1` through `CONTROL10` line-number fields for generic packets and `HDMI_GENERIC*_EN_DB_PENDING` double-buffer-pending bits.
- `DIG3_HDMI_DB_CONTROL` pending/taken/clear/lock/disable bits for HDMI and vupdate double-buffer state.
- `DIG3_HDMI_ACR_*` and `DIG3_HDMI_ACR_STATUS_*` CTS/N fields for 32, 44.1, and 48 kHz audio clock regeneration.
- `DIG3_AFMT_CNTL`, `DIG3_DIG_BE_CNTL`, and `DIG3_DIG_BE_EN_CNTL` audio clock, backend source/mode/HPD, DIG enable, and backend symbol clock status fields.
- `DIG3_TMDS_*` sync phase, control characters, sync patterns, control-bit generation, DC balancer, lane enable, DIG version, and force-disable fields.

Important DP3 fields cover nearly the full DisplayPort output programming surface:

- Link and stream control: `DP3_DP_LINK_CNTL`, `DP3_DP_PIXEL_FORMAT`, `DP3_DP_CONFIG`, `DP3_DP_VID_STREAM_CNTL`, `DP3_DP_LINK_FRAMING_CNTL`, and `DP3_DP_VID_INTERRUPT_CNTL`.
- Timing and MSA fields: `DP3_DP_MSA_COLORIMETRY`, `DP3_DP_MSA_MISC`, `DP3_DP_VID_TIMING`, `DP3_DP_VID_N`, `DP3_DP_VID_M`, `DP3_DP_VID_MSA_VBID`, and `DP3_DP_MSA_TIMING_PARAM1` through `PARAM4`.
- PHY and training fields: `DP3_DP_DPHY_CNTL`, `DP3_DP_DPHY_TRAINING_PATTERN_SEL`, `DP3_DP_DPHY_SYM0` through `SYM2`, `DP3_DP_DPHY_8B10B_CNTL`, `DP3_DP_DPHY_PRBS_CNTL`, `DP3_DP_DPHY_SCRAM_CNTL`, `DP3_DP_DPHY_FAST_TRAINING`, and `DP3_DP_DPHY_FAST_TRAINING_STATUS`.
- CRC and diagnostics: `DP3_DP_DPHY_CRC_EN`, `CRC_CNTL`, `CRC_RESULT`, `CRC_MST_CNTL`, and `CRC_MST_STATUS`.
- Secondary data and audio: `DP3_DP_SEC_CNTL`, `SEC_CNTL1` through `SEC_CNTL7`, `SEC_FRAMING1` through `SEC_FRAMING4`, `SEC_AUD_N`, `SEC_AUD_M`, readbacks, timestamp, packet control, metadata transmission, and GSP8-GSP11 controls.
- MST/MSO/DSC: `DP3_DP_MSE_RATE_CNTL`, `MSE_RATE_UPDATE`, `MSE_SAT0` through `SAT2`, `MSE_SAT*_STATUS`, `MSE_LINK_TIMING`, `MSE_MISC_CNTL`, `MSO_CNTL`, `MSO_CNTL1`, `DSC_CNTL`, and `DSC_BYTES_PER_PIXEL`.
- Double-buffer and low-power state: `DP3_DP_DB_CNTL`, `DP3_DP_MSA_VBID_MISC`, `DP3_DP_ALPM_CNTL`, and `DP3_DP_GSP_EN_DB_STATUS`.

DIG4-associated blocks mirror many DIG3 and DP3 concepts for a later instance while adding VPG, AFMT, and DME coverage:

- `VPG4_VPG_GENERIC_PACKET_ACCESS_CTRL`, `DATA`, `GSP_FRAME_UPDATE_CTRL`, `GSP_IMMEDIATE_UPDATE_CTRL`, `GENERIC_STATUS`, `MEM_PWR`, `ISRC1_2_*`, and `MPEG_INFO*` define packet RAM access, update modes, pending status, memory power, and infoframe payload fields.
- `AFMT4_AFMT_*` defines VBI/audio packet control, audio infoframe fields, 60958 channel status, audio CRC controls/results, ramp/test-audio counters, status/overflow bits, source selection, and AFMT memory power state.
- `DME4_DME_CONTROL` and `DME4_DME_MEMORY_CONTROL` define metadata-engine requestor ID, enable, stream type, double-buffer handshake, and memory power controls.
- `DIG4_DIG_FE_CNTL`, output CRC, clock/test/random pattern, FIFO status, HDMI metadata, HDMI control/status, ACR/VBI/infoframe/generic-packet controls, HDMI double-buffer controls, ACR CTS/N, AFMT clock, backend, TMDS, lane enable, and force-disable fields define the DIG4 HDMI/TMDS path.
- `DP4_*` begins another DisplayPort instance. This chunk covers link status, pixel format, stream enable/status, FIFO overflow, MSA/misc/timing, M/N, framing, HBR2 eye pattern, VBID, video interrupt, DPHY FEC/bypass/training/symbol/8b10b/PRBS/scrambler, CRC, fast training, secondary packet/audio fields, MSE rate update, and the first three fields of `DP4_DP_MSE_SAT0`.

## Control Flow

This header chunk has no runtime control flow. It is a compile-time register contract.

Runtime control flow appears in the display driver code that includes the generated header and passes these constants through DC register helper layers. A typical consumer path is:

1. The DCN 3.0.2 resource code selects register, shift, and mask tables for an ASIC generation.
2. Link encoder, stream encoder, audio, VPG, AFMT, DME, or DisplayPort helper code chooses a symbolic register field based on requested display state.
3. Register helpers read the current MMIO dword, clear bits using the `_MASK`, insert a field value shifted by `__SHIFT`, and write the dword back.
4. For handshake fields, the caller may poll status bits such as pending, taken, active, complete, overflow, CRC-valid, FIFO error, link status, or audio/status flags.

The implicit hardware programming sequence for the covered registers is ordered by display bring-up and update flows rather than by this header. For example, HDMI generic packets are prepared in VPG or HDMI packet memory, line/control/send bits are armed, double-buffer pending/taken state is observed, and packets are emitted during the selected video line or immediately. DisplayPort streams similarly require link/training state, pixel format, timing/M/N, MSA/VBID, secondary-data/audio packet setup, and stream enablement to be coherent. The header only defines the bit locations needed by those sequences.

## State And Persistence Behavior

The header itself is stateless and persists no data. It contributes numeric constants to compiled driver objects.

The hardware fields described by the macros are stateful MMIO bits. They include durable-until-reset programming state, transient handshake state, status/interrupt state, and diagnostic counters/results:

- Configuration state: pixel encoding, component depth, lane enables, link framing, MSA timing, video M/N, DP/HDMI packet enables, packet line numbers, audio CTS/N, 60958 audio channel-status, metadata stream selection, memory-power controls, test patterns, DSC mode, MSO/MSE settings, and ALPM/low-power controls.
- Handshake and double-buffer state: HDMI/DP/VPG/DME DB pending/taken/clear/disable/lock fields, generic packet update-pending fields, MSE rate/SAT update-pending fields, GSP send/pending/deadline-missed/active/in-idle fields, and vupdate-taken fields.
- Runtime status: link-training complete/status, stream status, FIFO overflow/error/calibration state, HDMI packet errors, AVMUTE state, AFMT audio enable/FIFO overflow, DPHY CRC valid/results, MST CRC phase status, fast-training state/completion, collision status, audio mute status, metadata-packet missed bits, and GSP enable DB status.
- Test and diagnostic state: output CRC enable/result, PRBS enable/seed, 8b/10b disparity controls, scrambler advance/count/K-code, HBR2 eye pattern, static/random/clock patterns, audio CRC results, and ramp generator counters.

Persistence is indirect and hardware-dependent. Some settings are reprogrammed during modeset, stream enable, audio enable, suspend/resume, link retraining, or GPU reset. Some status bits must be acknowledged using paired ACK or CLR fields. Because the generated masks do not encode access semantics, caller code must know which fields are read-only, write-one-to-clear, pulse-triggered, double-buffered, or safe for read-modify-write.

## Dependencies And Integration Points

Direct dependencies are minimal: a C preprocessor and code including this header. The important dependency is semantic alignment with the rest of the generated DCN 3.0.2 register set:

- matching address headers under `include/asic_reg/dcn/`, which provide register offsets for these field masks;
- DCN 3.0.2 resource definitions in `display/dc/resource/dcn302/dcn302_resource.c`, which include this header and bind register tables for hardware blocks;
- display core register helper macros that expect `__SHIFT` and `_MASK` naming conventions;
- link encoder, stream encoder, audio, VPG, AFMT, DME, DisplayPort, HDMI, MST, DSC, and panel/link power-management code that consumes the generated tables.

The covered registers integrate with external display protocols and AMD display hardware blocks:

- HDMI/TMDS integration includes generic packets, audio/video infoframes, ACR, AVMUTE, deep color, scrambling, metadata packets, VBI packets, control characters, and TMDS DC balancing.
- DisplayPort integration includes link training, MSA/VBID, SST/MST secondary data packets, MSE slot allocation, MSO, FEC, DSC, CRC, PRBS, scrambler, audio M/N, ALPM, and fast training.
- VPG and DME integration covers dynamic metadata, Dolby Vision metadata-missed status, HDR/metadata packet scheduling, and packet-memory access.
- AFMT integration covers audio sample packet generation, audio test/ramp generation, HDMI/DP audio infoframes, IEC 60958 channel-status, FIFO overflow handling, and audio CRC diagnostics.

The same conceptual blocks repeat across DCN instances. DIG3/DP3 and DIG4/DP4 fields are intentionally near-identical in many places, but their prefixes bind them to different hardware instances. Instance confusion can compile cleanly and still program the wrong link.

## Risks And Edge Cases

Generated register headers are silicon contracts. A numeric shift or mask change can silently alter display hardware programming while leaving all C code type-correct.

Important risk areas in this chunk include:

- Double-buffer and pending/taken bits. HDMI, DP, VPG, DME, MSE, and GSP registers contain many pending, taken, clear, disable, and lock bits. Using the wrong mask can leave updates stuck pending, clear a status bit prematurely, or apply packet data at the wrong vupdate boundary.
- Packet scheduling. HDMI generic packets, DP secondary data packets, GSP packets, metadata packets, ISRC, MPEG, audio info, and VBI packets have line-reference and line-number fields. Bad line fields can miss vblank deadlines or produce visible/receiver-side protocol errors.
- Audio correctness. ACR CTS/N, DP audio M/N, AFMT 60958 channel-status, sample-send, FIFO overflow ACK, and audio infoframe fields must match audio format and link timing. Wrong masks can cause muted, distorted, or intermittent HDMI/DP audio.
- Link training and PHY diagnostics. DPHY training pattern, FEC, PRBS, scrambler, 8b/10b, fast-training, HBR2 eye pattern, CRC, and symbol fields affect link bring-up and compliance diagnostics. Accidental writes can destabilize a live link.
- MST/MSO/DSC programming. MSE rate, SAT slot allocation, SAT status, MSO stream enables, and DSC bytes-per-pixel/slice fields are tightly coupled to bandwidth allocation. Incorrect masks can break MST payload allocation or DSC stream decode.
- Status/ACK semantics. Many fields are status, interrupt, or write-one-to-clear style bits. The mask header alone does not distinguish those semantics, so callers must avoid blind read-modify-write patterns on registers containing ACK/CLR/pulse fields.
- Instance boundaries. The chunk begins in the middle of `DIG3_HDMI_GENERIC_PACKET_CONTROL5` and ends in the middle of `DP4_DP_MSE_SAT0`. Final file-level analysis must merge this with adjacent chunks before making conclusions about those complete register groups.

Because this header is generated, manual edits should be treated as high risk unless they are regenerated from the authoritative register database and checked against matching address headers and resource tables.

## Test Signals

The most useful validation is compile-time consistency plus hardware/display behavior:

- Build the AMDGPU DCN 3.0.2 display path, especially translation units that include `dcn_3_0_2_sh_mask.h` through `dcn302_resource.c`.
- Static-check macro consistency: every field used by DCN 3.0.2 register tables has both a `__SHIFT` and `_MASK`, duplicated instance groups retain expected per-instance prefixes, and masks align with shifts and field widths.
- Compare generated output against the authoritative AMD register source for DCN 3.0.2; manual diffs in this file should be suspicious.
- Exercise HDMI modes with generic packets, audio infoframes, metadata packets, ACR, AVMUTE, deep color, scrambling, and TMDS control-character behavior.
- Exercise DisplayPort SST and MST modes that cover stream enable/disable, MSA timing, VBID, secondary data packets, MSE slot allocation, MSO, DSC, FEC, link retraining, fast training, ALPM, and audio M/N.
- Validate packet double-buffer behavior by changing infoframes, metadata, HDR/Dolby Vision packets, and generic packets across vblank without missed-packet or stale-packet artifacts.
- Run audio tests over HDMI and DP for 32 kHz, 44.1 kHz, 48 kHz, HBR/non-HBR, channel-status updates, FIFO overflow handling, and audio CRC diagnostics.
- Run display CRC and DP DPHY CRC tests where supported, checking valid/result bits and ACK behavior.
- Test suspend/resume, hotplug, modeset, link-loss recovery, and GPU reset paths to verify DIG3/DIG4, DP3/DP4, VPG4, AFMT4, and DME4 state is restored or intentionally reinitialized.
- On MST/DSC-capable monitors, verify payload allocation, DSC slice/bytes-per-pixel setup, secondary packet transmission, and metadata packet delivery remain correct across topology changes.
