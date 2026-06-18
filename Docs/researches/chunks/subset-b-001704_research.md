# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 41984-44385

## Scope

This chunk is part of the generated AMD DCN 3.0.0 ASIC register shift/mask header. It exports preprocessor constants for bit positions and bit masks used by AMDGPU display code when programming DCN 3.0 stream-output hardware. There is no executable C logic in this range: no functions, structs, enums, variables, allocation, locking, or persistence code.

The requested line range contains 2,168 `#define` entries: 1,087 `__SHIFT` constants and 1,081 `_MASK` constants. The mismatch is because the chunk boundary is artificial: it starts at the tail of `VPG2_VPG_GENERIC_STATUS` mask definitions and ends inside the `DIG3_HDMI_GENERIC_PACKET_CONTROL10` definition set.

Although the source path is under a local `ceph-client` tree, this file is AMDGPU display-driver hardware metadata, not distributed filesystem code.

## Purpose

The purpose of this chunk is to provide exact bitfield metadata for DCN 3.0 Display IO stream generation blocks. Runtime code combines these constants with the matching register offsets from `dcn_3_0_0_offset.h` so helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SE_SF`, `HWS_SF`, and DMUB field helpers can write or read named hardware fields without open-coded bit arithmetic.

Major hardware domains covered in this slice are:

- Tail fields for `VPG2`, then complete `VPG3` generic packet generator metadata: generic packet access/data, generic stream packet frame/immediate update controls, status, memory power, ISRC packet data, and MPEG infoframe fields.
- `AFMT2` and `AFMT3` audio formatter fields: HDMI audio/VBI packet controls, audio infoframe bytes, IEC 60958 channel-status words, CRC, audio test ramp controls, status/ack bits, audio source selection, and formatter memory power.
- `DME2` and `DME3` display micro-engine control and memory-power fields.
- `DIG2` and beginning of `DIG3` stream encoder front-end and HDMI/TMDS fields: front-end control, output CRC, test/clock/random patterns, FIFO status, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic-packet controls, HDMI double-buffering, TMDS control-symbol generation, lane enable, version, and force-disable controls.
- The full `DP2` stream/link field set: link control, pixel format, MSA, video timing and `M/N`, link framing, DPHY training/test/CRC/scrambler controls, secondary-data packet control, audio packet timing, MST/MSE allocation fields, MSO controls, DSC enable/bytes-per-pixel, ALPM, generic-stream-packet controls, and DP double-buffer status.

## Important API Surface

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important visible register families include:

- `VPG2_VPG_*` and `VPG3_VPG_*` fields for packet table access, generic packet byte programming, per-packet frame/immediate update bits, pending bits, conflict status/clear, GSP memory light sleep, ISRC data indexing, and MPEG info update.
- `AFMT2_AFMT_*` and `AFMT3_AFMT_*` fields for audio layout selection, channel enable masks, DP audio stream ID, 60958 override and channel status, audio CRC source/channel/count/result, test ramp min/max/inc/dec controls, FIFO overflow ack, AZ audio enable-change ack, and audio infoframe line/update behavior.
- `DME2_DME_*` and `DME3_DME_*` fields for DME enable/reset/read-write arbitration, reference clock control, urgent state, memory power modes, and memory power status.
- `DIG2_DIG_*` and `DIG3_DIG_*` fields for stream-encoder front-end start, stereosync, HDMI/DP pixel encoding, TMDS color format, output CRC enable/source, pattern generators, FIFO level/error/calibration state, backend power/status, lane enablement, and forced disable.
- `DIG2_HDMI_*` and `DIG3_HDMI_*` fields for HDMI packet generation version, keepout/deep-color/scramble settings, audio clock regeneration, VBI/infoframe/audio packet send controls, metadata packet controls, generic packet line controls, generic packet send/continuous/immediate/double-buffer pending bits, global control AVMUTE, and HDMI double-buffer lock/taken/clear state.
- `DIG2_TMDS_*` fields for TMDS control characters, sync characters, stereo sync, DC balancer, and generated control-symbol counts. The chunk does not reach the matching `DIG3_TMDS_*` family.
- `DP2_DP_*` fields for stream enable/status/defer, pixel encoding/depth, MSA timing/color/VBID, DPHY training and test patterns, scrambler/8b10b/PRBS/CRC, secondary-data packet enables and pending bits, audio `M/N`/timestamp, MST slot allocation tables, MSO split controls, DSC transport controls, metadata transmission, ALPM, and DP generic stream packets 8 through 11.

These constants are consumed indirectly through field-list macros. For example, `dcn30_resource.c` builds `dcn30_vpg_shift`/`dcn30_vpg_mask` from `DCN3_VPG_MASK_SH_LIST`, `dcn30_afmt_shift`/`dcn30_afmt_mask` from `DCN3_AFMT_MASK_SH_LIST`, and stream encoder field tables from `SE_COMMON_MASK_SH_LIST_DCN30`. `dcn30_dio_stream_encoder.h` lists many `DIG`, `HDMI`, `DP`, and `DME` registers that line up with this chunk.

## Control Flow

This header chunk has no local runtime control flow. The runtime sequence is provided by AMDGPU display code:

1. DCN 3.0/3.0.2 resource, IRQ, GPIO, clock, and DMUB files include `dcn_3_0_0_offset.h` and this mask/shift header.
2. Resource construction token-pastes register and field names into generated constants. Address macros such as `SRI(reg_name, block, id)` bind offsets, while field macros such as `SE_SF(reg, field, __SHIFT)` and `SE_SF(reg, field, _MASK)` bind the bit metadata.
3. Stream encoder, VPG, AFMT, DME, DP, HDMI, TMDS, IRQ, GPIO, and DMUB code uses those tables through register helpers to program modesets, link training, packet generation, audio, metadata, MST allocation, DSC transport, double buffering, status polling, and interrupt/status acknowledgment.

The constants do not encode ordering requirements. Callers must still sequence clock and memory power, register double-buffer locks, infoframe packet writes, GSP frame/immediate update requests, HDMI/DP stream enablement, DP link training, MST payload updates, DSC transport setup, FIFO/status clears, and suspend/resume restoration correctly.

## State And Persistence Behavior

This chunk stores no software state and persists no files. It describes memory-mapped GPU display state:

- VPG state persists packet RAM/index contents, frame/immediate update request bits, pending bits, conflict flags, ISRC/MPEG payload bytes, and packet-generator memory-power settings.
- AFMT state persists HDMI/DP audio packet formatting, channel-status words, audio infoframes, source/channel layout selection, CRC/test-ramp configuration, status/ack bits, and AFMT memory-power state.
- DIG/HDMI/TMDS state persists stream encoder control, pixel encoding/deep color/scrambling, packet generation, audio clock regeneration, generic packet scheduling, double-buffer status, FIFO calibration/error state, CRC capture, test patterns, lane enablement, and TMDS symbol generation.
- DP2 state persists DisplayPort link and stream configuration, MSA timing, secondary-data packet enables, audio timing values, DPHY training/test/scrambler/CRC controls, MST payload allocation state, MSO split state, DSC transport controls, ALPM controls, metadata transmission, and DP generic stream-packet scheduling.

Hardware persistence is power-domain dependent. Values can remain active until a modeset, link reconfiguration, display block reset, power gate, suspend/resume transition, or GPU reset. Status, pending, clear, acknowledge, lock, and power-state fields may be sticky, self-clearing, read-only, write-one-to-clear, or sequencing-sensitive; the generated header only supplies bit positions and masks, not semantic access rules.

## Dependencies And Integration Points

This chunk is tightly coupled to:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which provides the matching MMIO register offsets and base indices.
- AMD display register helpers in `reg_helper.h`, DMUB field helpers in `dmub_reg.h`, and generated field-list macros in DCN stream encoder, VPG, AFMT, DIO, and resource headers.
- DCN 3.0 register database generation. The macro names and numeric constants must match the ASIC specification and the corresponding offset header exactly.

Direct include sites in this repository include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

The most direct functional integration is stream output. `dcn30_resource.c` maps VPG, AFMT, and DME blocks to DIO stream encoder instances. `dcn30_dio_stream_encoder.h` constructs the stream encoder register set for `DIG`, `DP`, `DME`, HDMI, and AFMT programming and lists field names that depend on matching `__SHIFT` and `_MASK` macros from this header family.

## Risks And Edge Cases

- A wrong shift or mask compiles cleanly but targets the wrong hardware bits. High-risk fields here include stream enables, DP link/DPHY training, HDMI deep-color/scrambler controls, audio/ACR timing, generic packet send/pending bits, double-buffer locks, interrupt/status clears, MST allocation, DSC transport, and memory-power controls.
- Repeated instance families are copy-sensitive. `VPG2`/`VPG3`, `AFMT2`/`AFMT3`, `DME2`/`DME3`, and `DIG2`/`DIG3` are structurally similar but not fully interchangeable; a drift can affect only one connector, pipe, or multi-display configuration.
- `DP2` is a dense field set spanning link training, stream timing, secondary packets, MST, MSO, DSC, and ALPM. Small bitfield errors may only appear under specific combinations such as high link rates, DSC-enabled modes, MST topologies, audio, or low-power transitions.
- Status and control bits share many registers. Incorrect read-modify-write masks can fail to clear sticky status, clear a status bit unexpectedly, leave a pending update stuck, or race with hardware double-buffer ownership.
- The range starts and ends mid-family. Whole-file conclusions about `VPG2_GENERIC_STATUS` or `DIG3_HDMI_GENERIC_PACKET_CONTROL10` require adjacent chunks.
- Generated constants are untyped preprocessor macros. They provide no compile-time validation of access width, read/write semantics, reset value, volatile behavior, or required register sequencing.

## Test Signals

Useful validation signals for this chunk are:

- Compile AMDGPU display support for DCN 3.0 and DCN 3.0.2. Missing or renamed macros should fail in resource construction, stream encoder, VPG/AFMT, IRQ, GPIO, clock, and DMUB paths.
- Mechanically verify the generated structure: every complete field in this range should have a matching `__SHIFT` and `_MASK`, while known chunk-boundary exceptions should reconcile with adjacent chunks.
- Diff this slice against AMD's authoritative DCN 3.0 register database and the matching `dcn_3_0_0_offset.h`; also compare repeated instance families where the ASIC expects identical layouts.
- Exercise display outputs using DIO instances 2 and 3: HDMI and DP modesets, hotplug, link-rate/lane-count changes, suspend/resume, blank/unblank, and multi-display configurations.
- Validate HDMI packet behavior: audio playback, ACR generation, infoframes, generic packets, metadata packets, AVMUTE, deep color, scrambling, VBI packets, and double-buffer update/pending behavior.
- Validate DP behavior on instance 2: link training patterns, scrambler/8b10b/PRBS/CRC paths, MSA timing, audio secondary packets, metadata transmission, MST payload allocation, MSO split modes, DSC transport, ALPM, and stream enable/disable sequencing.
- Watch for kernel log or diagnostic symptoms: link-training failures, AUX/DP timeouts, blank displays, FIFO level errors, CRC mismatches, audio dropouts, corrupt infoframes, stuck pending bits, MST bandwidth/allocation errors, DSC artifacts, and resume failures.

## Cross-Chunk Notes

This chunk is a partial view of `dcn_3_0_0_sh_mask.h`. Previous chunks own the beginning of the `VPG2` family, including the missing `VPG2_VPG_GENERIC_STATUS` shift definitions. Later chunks continue `DIG3_HDMI_GENERIC_PACKET_CONTROL10` and cover the rest of the `DIG3`/`DP3` and later DCN 3.0 field namespace. The final per-file research document should merge adjacent chunk reports before making complete claims about all stream encoder instances or all DCN 3.0 register fields.
