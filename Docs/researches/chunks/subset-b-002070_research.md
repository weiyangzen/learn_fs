# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 31000-33217

## Purpose

This chunk is a middle slice of AMD's generated DCN 3.5.0 shift/mask register-field header. It contains no executable C code; it exports preprocessor constants that encode bit positions and masks for display, DisplayPort, HDMI, video-packet-generator, audio-format, and related DCN hardware registers. Runtime AMDGPU display code combines these `*_SHIFT` and `*_MASK` definitions with the matching `dcn_3_5_0_offset.h` register offsets to build register tables and to perform field-level MMIO read, write, and read-modify-write operations.

The requested range contains 2,218 `#define` entries: 1,110 `__SHIFT` macros and 1,108 `_MASK` macros. The imbalance is caused by artificial chunk boundaries. Line 31000 is only the mask half of `DP2_DP_MSA_TIMING_PARAM2__DP_MSA_HSTART`, whose shift appears in the previous chunk, and lines 33215-33217 start `AFMT4_AFMT_AUDIO_PACKET_CONTROL2` with three shift definitions whose remaining shifts and masks continue in the next chunk.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata rather than distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locks, or includes in this slice. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, set, preserve, or test that field.

The main register families in this range are:

- `DP2_*`: the tail of the DisplayPort instance 2 register-field layout, covering MSA timing parameters, MSO secondary stream controls, DSC mode, secondary-data-packet send/status controls, generic SDP line numbers, double-buffer status, main-link ALPM and auxless ALPM controls, GSP8-GSP11 controls, and GSP double-buffer pending status.
- `VPG3_*`: video packet generator instance 3 fields for generic packet data indexing and data bytes, frame-update and immediate-update triggers/pending bits for generic packets 0-14, generic lock/conflict status, memory light-sleep controls, ISRC data access, and MPEG infoframe payload bytes.
- `AFMT3_*`: audio formatter instance 3 fields for VBI/audio packet controls, audio infoframe words, IEC 60958 channel-status words, audio CRC control/result, ramp-test generation, status flags, source control, and formatter memory power state.
- `DME3_*`: display micro-engine or metadata-engine fields for control and memory-control programming, including clock gating, mode, reset, generic packet memory selection, and address/data access.
- `DIG3_*`: digital encoder instance 3 fields for front-end controls, CRC/test-pattern generation, FIFO controls, HDMI metadata/control/status, HDMI audio clock regeneration, HDMI generic-packet scheduling, HDMI double-buffer controls, ACR values/status, backend controls, TMDS control characters, DC-balance controls, generated TMDS control bits, and version fields.
- `DP3_*`: full DisplayPort instance 3 coverage in this chunk. It includes link control, pixel format, colorimetry, stream enable/status, FIFO steering, MSA miscellaneous/timing fields, DPHY controls and training/test fields, video M/N generation, link framing, HBR2 pattern, VBID/MSA positioning, stream-disable interrupt bits, DPHY CRC and MST CRC fields, fast-training controls/status, secondary-data-packet controls, audio M/N fields, MST MSE rate and slot-allocation tables/status, DP DB controls, metadata transmission, ALPM/auxless ALPM controls, GSP8-GSP11 controls, and MSO/DSC fields.
- `VPG4_*`: the beginning of video packet generator instance 4, repeating the same generic packet, frame-update, immediate-update, status, memory power, ISRC, and MPEG infoframe field layout as `VPG3`.
- `AFMT4_*`: the beginning of audio formatter instance 4. This chunk includes VBI packet control and only the first three `AFMT_AUDIO_PACKET_CONTROL2` shift definitions before the line boundary.

The repeated instance names matter. `VPG3`/`AFMT3`/`DIG3`/`DP3` are one display pipeline/link instance, while `VPG4`/`AFMT4` starts the next instance. Copying a mask from one numbered block to another only works where the generated register database intentionally kept the same bit layout.

## Control Flow

This header has no runtime control flow. The practical control flow belongs to consumers in the AMDGPU display stack:

1. DCN 3.5 display code includes the matching offset and shift/mask headers.
2. Register-list macros token-paste symbolic register and field names into per-block register tables.
3. Block constructors for stream encoders, link encoders, audio/AFMT/VPG paths, DMUB services, IRQ handling, and related DCN resources store those tables for the correct hardware instance.
4. Runtime paths invoke register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers use the constants in this header to pack, extract, or preserve individual MMIO fields.

The macros do not encode ordering. Callers must still sequence link training, stream enable/disable, packet updates, HDMI/DP audio setup, MST allocation, DSC/MSO programming, ALPM entry/exit, interrupt acknowledgement, double-buffer commits, and power transitions according to hardware rules.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes fields in DCN 3.5.0 hardware registers. The state represented by these masks includes:

- DisplayPort link and stream state: link enable, enhanced framing, VBID/MSA placement, MSA timing totals/starts/sync widths, pixel format, colorimetry, stream enable, FIFO/TU sizing, video M/N, DSC mode, and MSO secondary stream enablement.
- DPHY and training state: FEC enable/status, scrambler controls, training-pattern selection, programmed symbols, PRBS settings, PHY CRC capture, MST CRC slot ranges/status, fast-training start/status/interrupt-like completion fields, HBR2 pattern controls, and low-power ALPM timing.
- Secondary-data-packet state: ASP/ATP/AIP/ACM/MPG/ISRC/GSP enables, GSP send requests, pending/active/deadline-missed bits, per-GSP line numbers, double-buffer pending status, metadata-packet enable/line fields, and collision/audio-mute status.
- HDMI and TMDS state: HDMI control/status, scrambling, deep color, AVMUTE, audio packet delay, ACR CTS/N values and readback status, VBI/infoframe/generic-packet scheduling, HDMI generic packet immediate sends, HDMI double-buffer lock/taken/pending fields, TMDS control-character generation, DC balancing, and backend enable/status fields.
- Audio/VPG state: generic packet payload bytes, frame and immediate update requests, update-pending status, generic packet lock/conflict status, ISRC and MPEG data words, AFMT audio infoframe fields, IEC 60958 channel-status fields, HBR/channel enable/layout overrides, audio CRC controls/results, ramp-test controls, audio enable/status bits, and formatter/VPG memory power settings.
- MST state: MSE rate numerator/denominator fields, SAT source/slot-count entries and status readbacks, SAT update triggers, link timing, blank-code/timestamp/zero-encoder controls, and keepout behavior.

Persistence is hardware-defined. Configuration fields normally persist until a modeset, stream teardown, register reprogramming, power gating, suspend/resume, GPU reset, or ASIC reset. Status, pending, clear, ack, and interrupt fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the relevant display/audio/link clocks and power domains are active. This generated header does not record those access semantics.

## Dependencies And Integration Points

This slice depends on AMD's generated DCN 3.5.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which supplies the matching register offsets.
- Adjacent chunks of `dcn_3_5_0_sh_mask.h`, because this range starts with a mask whose shift is in the previous chunk and ends inside `AFMT4_AFMT_AUDIO_PACKET_CONTROL2`.
- DCN 3.5 display block register-list macros that pair symbolic register names, fields, offsets, shifts, and masks for the correct pipeline instance.
- Stream encoder, link, DIO/audio, VPG/AFMT, HDMI, DP, MST, DSC/MSO, ALPM, IRQ, and DMUB service code that programs these fields through AMD display register helpers.

Behaviorally, this chunk integrates with HDMI/DisplayPort output bring-up, DP link training and diagnostics, MST bandwidth/slot allocation, secondary-data-packet transmission, HDR/vendor/generic packet updates, HDMI audio and infoframe emission, DP audio timestamping, DSC/MSO enablement, low-power link entry/exit, and display interrupt/status reporting.

## Risks And Edge Cases

- The constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while touching the wrong MMIO bits.
- The range is generated metadata. Manual edits can desynchronize the header from silicon documentation, the matching offset header, firmware assumptions, and other generated DCN versions.
- The chunk boundary is not a semantic boundary. `DP2_DP_MSA_TIMING_PARAM2__DP_MSA_HSTART` is split from its shift, and `AFMT4_AFMT_AUDIO_PACKET_CONTROL2` is split from most of its fields and masks.
- Instance repetition hides local errors. `DP2` and `DP3` have very similar field layouts, but a single instance-specific generator error could affect only one link.
- Status, clear, mask, ack, pending, active, and taken bits are easy to confuse. Using a status mask as a clear mask, or clearing a sticky field at the wrong time, can create missed interrupts, stuck pending bits, packet-update failures, or repeated IRQs.
- HDMI/DP packet timing fields are line/frame sensitive. Incorrect line numbers, immediate-update bits, double-buffer-disable bits, or pending polling can emit stale metadata, tear infoframes across frames, or miss audio/video packet deadlines.
- DPHY, FEC, training, ALPM, and fast-training fields are link-stability sensitive. Wrong masks can cause training failures, intermittent link loss, resume failures, or invalid low-power transitions.
- Audio and IEC 60958 fields are interoperability sensitive. Incorrect AFMT masks can produce silent HDMI/DP audio, wrong channel layout, wrong sample-rate metadata, bad HBR behavior, or receiver-specific failures.
- MST MSE/SAT fields affect bandwidth allocation. Bad slot-count/source masks can corrupt multi-stream scheduling without necessarily breaking single-stream DP validation.

## Test Signals

Useful validation for this chunk combines generated-header checks and hardware behavior:

- Build AMDGPU display support with DCN 3.5 enabled. Missing or renamed macros should fail in the DCN 3.5 register-table construction paths that reference these fields.
- Mechanically verify `__SHIFT`/`_MASK` pairing for lines 31000-33217 while allowing the two expected boundary exceptions: the first-line `DP2_DP_MSA_TIMING_PARAM2__DP_MSA_HSTART_MASK` and the partial `AFMT4_AFMT_AUDIO_PACKET_CONTROL2` group at the end.
- Diff this range against AMD's authoritative DCN 3.5.0 register source and nearby generated headers such as `dcn_3_5_1_sh_mask.h` where field layouts are expected to remain compatible.
- Exercise DP instance 3 and DP instance 2 paths on matching hardware: link training, stream enable/disable, MSA programming, DSC, MSO, MST, FEC, fast training, PHY CRC diagnostics, and suspend/resume.
- Exercise HDMI/DIG instance 3: scrambling, deep color, AVMUTE, ACR programming/readback, generic packet sends, infoframes, TMDS control patterns, CRC/test patterns, and double-buffer update behavior.
- Validate VPG/AFMT packet paths with HDR/vendor/generic packets, ISRC/MPEG packets, audio infoframes, IEC 60958 metadata, HBR and multichannel audio, and audio CRC/ramp diagnostics.
- Watch kernel logs and hardware traces for missed stream-disable interrupts, stuck DB pending/taken bits, GSP deadline misses, ALPM wake failures, MST slot allocation errors, stale metadata packets after modeset, silent audio after hotplug, and resume-only link or audio failures.

## Cross-Chunk Notes

This chunk continues the `DP2` register block from the prior chunk, contains a complete `VPG3`/`AFMT3`/`DME3`/`DIG3`/`DP3` middle region, and starts `VPG4`/`AFMT4`. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.5.0 registers or all display/audio/link instances.
