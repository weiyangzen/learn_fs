# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 47302-49696

## Purpose

This chunk is a generated AMD DCN 4.1.0 register shift/mask slice for DisplayPort stream-encoder, audio packet-generator, metadata-engine, VPG, and HPO 32-symbol encoder blocks. It has no executable C code. Its interface is a set of preprocessor constants that define bit offsets and masks for individual MMIO register fields.

The requested range contains 2,395 lines and 2,136 `#define` entries: 1,067 `__SHIFT` macros and 1,069 `_MASK` macros. The mismatch is caused by artificial chunk boundaries. The slice begins in the middle of `VPG6_VPG_GENERIC_PACKET_DATA`, where earlier byte-field shifts are just before line 47302, and ends in the middle of `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL4`, where the remaining masks continue after line 49696.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation sites, locks, or direct includes in this chunk. The exported surface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit position used to pack or extract a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used for field isolation, preservation, and read-modify-write operations.

The main register families in this exact range are:

- `VPG6_*`, `VPG7_*`, and `VPG8_*`: video packet generator fields for generic packet indexing/data, GSP frame-update and immediate-update triggers, pending bits, lock/conflict status, memory power, ISRC data indexing, MPEG info packet bytes, and packet payload byte lanes. `VPG6` is partial at the start of the slice; `VPG7` and `VPG8` are complete VPG groups in this range.
- `DP_SYM32_ENC1_*`, `DP_SYM32_ENC2_*`, and `DP_SYM32_ENC3_*`: HPO DisplayPort 32-symbol encoder fields. Encoder 1 is complete in this range, encoder 2 is complete, and encoder 3 begins near the end and stops during `SDP_GSP_CONTROL4`.
- `DP_STREAM_ENC2_*` and `DP_STREAM_ENC3_*`: stream encoder clock, pixel input mux, audio source mux, clock-ramp-adjuster FIFO status/control, and spare fields.
- `APG2_*` and `APG3_*`: audio packet generator fields for reset/enable, DP audio stream ID, channel-count override, debug generator/channel enable, ACP packet source/debug content, audio infoframe fields, IEC 60958 channel-status debug fields, audio CRC controls/results, ramp generator controls, audio/HBR/FIFO status, audio DTO debug controls, memory power, and spare bits.
- `DME7_*` and `DME8_*`: metadata engine control and memory power fields, including HUBP requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable bits, missed-transmission status/clear bits, and low-power memory controls.

The `DP_SYM32_ENC*` groups are especially dense. They describe encoder reset/enable, pixel-to-symbol FIFO reset/status, MSA and pixel-format double buffering, MSA payload registers 0-8, HBLANK minimum symbol width, GSP sideband packet controls 0-14, SDP stream control, audio SDP controls, metadata packet scheduling, SDP framing, ATP audio-frequency override, idle-pattern timing, MSA/VBID transmission, video stream enable/defer/status, Panel Replay tunneling optimization, CRC control/results/status, symbol count, ALPM sleep/wake/request/ready/hardware/status/start/interrupt controls, memory power, and spare fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code that includes this generated header together with `dcn_4_1_0_offset.h`:

1. DCN 4.0.1/4.1.0 display initialization includes the offset and shift/mask headers.
2. Register-list macros token-paste register and field names into typed register tables for DMUB services, IRQ handling, clock management, GPIO translation/factory code, resource creation, stream encoders, VPG, APG, and metadata-engine users.
3. Runtime paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT`.
4. Those helpers use the offset header for the MMIO address and this header's shift/mask constants to modify only the intended bits.

The macros do not encode ordering constraints. Consumers must still reset and enable blocks in the right sequence, wait for reset-done and pending/status bits where required, program double-buffered fields at safe scanout points, clear sticky status bits correctly, and coordinate audio/video/metadata packet scheduling with link timing.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware state in DCN display registers:

- VPG packet RAM/index state, generic-packet update request bits, update-pending bits, conflict/lock status, ISRC and MPEG packet data, and VPG memory power state.
- DP stream encoder clock and mux state that selects pixel and audio stream sources and exposes FIFO calibration, reset, active, and error state for the clock-ramp-adjuster FIFO.
- APG state for audio packet enablement, stream ID, channel-count override, debug packet generation, ACP/audio info/IEC 60958 data, audio CRC capture, generated ramp parameters, audio enable/HBR/FIFO overflow status, DTO debug parameters, and APG memory power.
- DME state for metadata stream enablement, HUBP request routing, double-buffer handoff, missed-transmission status, and metadata-engine memory power.
- HPO DP symbol encoder state for stream enablement, MSA and SDP sideband packet programming, audio packets, metadata packets, CRC collection, ALPM sleep/wake scheduling, symbol counting, Panel Replay support bits, idle-pattern behavior, and encoder memory power.

Persistence is hardware-defined. Configuration fields generally remain until modeset reprogramming, stream teardown, power gating, suspend/resume, GPU reset, or ASIC reset. Status, pending, done, clear, and interrupt-style fields can be read-only, sticky, self-clearing, write-one-to-clear, or meaningful only while the relevant clocks and power domains are active. This generated header does not document access semantics; the register specification and consuming driver code define them.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DCN 4.1.0 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h` supplies the companion MMIO offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c` includes this header for DCN401 DMUB register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c`, `dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, `dc/gpio/dcn401/hw_translate_dcn401.c`, `dc/gpio/dcn401/hw_factory_dcn401.c`, and `dc/resource/dcn401/dcn401_resource.c` include this same header and depend on its field names matching DCN401 register-list macros.
- HPO stream encoder code, including the common `dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.*` pattern, consumes `DP_SYM32_ENC*` field names through register tables for reset, FIFO control, pixel format, MSA, SDP/GSP, audio, metadata, CRC, and HBLANK operations.
- VPG code, including the common `dc/dcn30/dcn30_vpg.*` pattern, consumes `VPG*_VPG_GENERIC_*` fields for writing generic info packets and triggering immediate or frame-synchronized packet updates.

The most direct behavioral surfaces in this range are DisplayPort/HPO stream bring-up, sideband packet scheduling, audio info packet generation, metadata packet delivery, CRC diagnostics, ALPM timing, Panel Replay-related signaling, and per-block memory power control.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while writing the wrong MMIO bit or corrupting an adjacent field.
- The file is generated metadata. Manual edits can diverge from the authoritative register database, the matching offset header, firmware expectations, and silicon documentation.
- The range is heavily repetitive across instances 1, 2, and 3. A generator or copy/paste error can affect one stream encoder, VPG, APG, DME, or DP symbol encoder instance while adjacent instances appear correct.
- The chunk boundaries are artificial. `VPG6_VPG_GENERIC_PACKET_DATA` starts before the requested range, and `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL4` continues after it. Whole-register or whole-instance conclusions need adjacent chunks.
- Pending, done, clear, overflow, CRC-valid, reset-done, and interrupt-status fields are side-effect-sensitive. Treating status bits like normal configuration bits can cause missed packets, stuck update pending bits, stale CRCs, or interrupt/status storms.
- Double-buffered fields and line-number scheduling fields are timing-sensitive. Incorrect masks for `*_DOUBLE_BUFFER_PENDING`, `*_TRANSMISSION_LINE_NUMBER`, `MSA_TRANSMISSION_LINE_NUMBER`, metadata packet scheduling, or ALPM sleep/wake timing can produce frame-boundary glitches or packets on the wrong scanline.
- Audio packet and IEC 60958 fields are interoperability-sensitive. Incorrect APG or SDP audio masks can lead to silent audio, wrong channel layout, incorrect sample-rate signaling, HBR failures, or receiver-specific DP audio problems.
- Power-control fields can interact with clock and reset sequencing. Incorrect memory power force/default/state masks can leave APG, DME, VPG, or DP symbol encoder memories unavailable during programming or prevent expected low-power entry.

## Test Signals

Useful validation combines generated-header checks with DCN hardware behavior:

- Build AMDGPU display support with DCN401/DCN 4.1 enabled. Missing or renamed macros should fail in the DCN401 include users and in register-table construction for DMUB, IRQ, clock, GPIO, resource, VPG, APG, DME, and HPO stream-encoder paths.
- Mechanically compare this range with the matching `dcn_4_1_0_offset.h` register names and AMD's authoritative register database. Allow for the known artificial boundary imbalance at the beginning and end of this chunk.
- Run a macro-pair check for fields in the chunk and flag unpaired shift/mask names, while explicitly accounting for the partial `VPG6_VPG_GENERIC_PACKET_DATA` and `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL4` records.
- Exercise DisplayPort modesets using multiple stream-encoder instances, especially streams that map to encoder/VPG/APG/DME instances 2 and 3. Watch for failed reset-done waits, FIFO errors, blank output, wrong pixel format, missing MSA data, or link-training/display glitches after modesets.
- Validate VPG generic packets through HDR/vendor/infoframe changes, ISRC/MPEG packet updates, immediate updates, frame-synchronized updates, and repeated hotplug/modeset cycles. Watch for VPG conflict bits, stuck pending bits, stale packets, or missed frame updates.
- Validate DP audio through plug/unplug, sample-rate changes, channel-layout changes, HBR/compressed formats, suspend/resume, and stream disable/enable cycles. Watch for silent audio, wrong channel allocation, wrong IEC 60958 signaling, APG FIFO overflow, bad CRC status, or audio mute status that does not match the driver request.
- Exercise metadata packet delivery and Panel Replay/ALPM paths where supported. Watch for metadata double-buffer pending bits that never clear, missed-transmission status, incorrect ALPM wake interrupt status, bad sleep/wake line timing, or Panel Replay regressions.

## Cross-Chunk Notes

This is a middle chunk of `dcn_4_1_0_sh_mask.h`. The previous chunk contains the start of the `dcn_dcec_hpo_dp_stream_enc1_vpg_vpg_dispdec` VPG6 block, including earlier `VPG6_VPG_GENERIC_PACKET_DATA` fields. The next chunk continues the `DP_SYM32_ENC3` sideband packet control block and the remaining encoder 3 fields. The final per-file research document should merge adjacent chunks before making complete claims about all DCN 4.1.0 registers or all instances of a repeated register family.
