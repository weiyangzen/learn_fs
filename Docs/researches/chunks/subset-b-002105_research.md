# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 39862-42078

## Purpose

This chunk is a generated AMD DCN 3.5.1 register-field shift/mask slice. It has no executable C logic; it publishes preprocessor constants used by AMDGPU display code to pack, update, and extract MMIO bitfields. Runtime code pairs these `__SHIFT` and `_MASK` values with the matching register offsets in `dcn_3_5_1_offset.h` and with AMD display register helper macros such as `REG_SET`, `REG_UPDATE`, and `REG_GET`.

The range contains 2,217 `#define` entries: 1,108 shift macros and 1,109 mask macros. It begins inside the tail of `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0`, covers HPO DisplayPort stream encoder instances 1 and 2 plus the beginning of instance 3, includes link/DPHY instance 1 fields, and stops inside `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL7`. Boundary completeness therefore depends on adjacent chunks.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, allocations, locks, or direct control paths in this chunk. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for preserving, setting, or reading the field.

The main covered families are:

- `DP_DPHY_SYM320_*`: tail CRC configuration/status/count masks for the first HPO DP DPHY Symbol32 block.
- `DP_STREAM_ENC1`, `DP_STREAM_ENC2`, and `DP_STREAM_ENC3`: stream-encoder clock enable/status, pixel-stream source mux, audio-stream source mux, clock-ramp-adjuster FIFO reset/enable/read-level/status/error/calibration controls, and spare registers.
- `APG1`, `APG2`, and `APG3`: HPO DP audio packet generator reset/enable, DP audio stream ID, debug generator, packet source selection, audio CRC controls/results, audio/HBR/fifo-overflow status, output-active state, memory-power controls, and spare fields.
- `DME6`, `DME7`, and `DME8`: metadata engine controls for HUBP requestor selection, enable, stream type, double-buffer pending/taken/clear/disable, missed-transmission status/clear, and metadata memory-power fields.
- `VPG6`, `VPG7`, and `VPG8`: video packet generator access/data registers, generic packet frame-update and immediate-update controls for generic packet slots 0-14, pending bits, conflict status/clear, memory power, ISRC packet data, and MPEG info packet fields.
- `DP_SYM32_ENC1` and `DP_SYM32_ENC2`: complete Symbol32 stream encoder field sets for enable/reset, pixel-to-symbol FIFO, MSA and pixel-format double buffering, pixel format, MSA payload words, hblank minimum symbol width, generic SDP packet controls 0-14, SDP/audio/metadata controls, MSA/VBID/stream controls, panel replay controls, video CRC controls/results/status, memory-power controls, and spare fields.
- `DP_LINK_ENC1` and `DP_DPHY_SYM321`: HPO DP link encoder 1 clock/spare fields and DPHY instance 1 control, status, SAT update, symbol override, test pattern, frame, FEC, SR insert, register-insert, MST VC payload, timestamp, CRC, error, and clock-pattern fields.
- `DP_SYM32_ENC3`: beginning of Symbol32 stream encoder 3, from reset/FIFO/MSA/pixel format through GSP controls 0-6 and the first two shift definitions for GSP control 7.

The exact shift/mask pairing has five expected chunk-boundary exceptions: lines 39862-39864 contain masks whose shifts are in the previous chunk, and lines 42077-42078 contain shifts whose masks are in the next chunk.

## Control Flow

This header has no runtime control flow. The normal consumer flow is:

1. DCN 3.5.1-specific modules include `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`.
2. Resource initialization in `display/dc/resource/dcn351/dcn351_resource.c` token-pastes generated register and field names into register, shift, and mask tables. Relevant users include `DCN31_APG_MASK_SH_LIST`, `DCN3_VPG_MASK_SH_LIST`, and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST`.
3. HPO DP stream encoder code in `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.*` uses those tables to program clocks, stream input muxing, FIFO reset/enable sequencing, MSA/pixel format, sideband packets, audio mute/ASP enablement, CRC diagnostics, and stream enable/status.
4. APG and VPG helper code uses the APG/VPG field tables for audio packet generation and generic/info packet programming.
5. Runtime modeset, link training, audio setup, metadata, diagnostics, suspend/resume, and disable paths issue register reads/writes through AMDGPU's register helper layer.

The macros do not encode ordering rules. Consumers must still sequence clocks, resets, FIFO enablement, packet double-buffering, stream enablement, link/DPHY programming, and status polling correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes state held in DCN 3.5.1 display hardware registers:

- Stream encoder clock, source mux, audio mux, and clock-ramp FIFO state for HPO DP stream instances 1-3.
- APG audio packet generator reset/enable, debug generation, packet source, CRC, FIFO-overflow, output-active, and memory-power state.
- DME metadata double-buffer and missed-transmission state, including clear bits and memory-power controls.
- VPG generic packet payload bytes, packet update requests, update-pending readbacks, conflict status/clear bits, ISRC/MPEG packet payload, and low-power memory state.
- Symbol32 encoder reset/enable, video FIFO reset/overflow, MSA payload, pixel format, generic sideband packet scheduling, audio packet controls, metadata packet enablement, MSA/VBID timing, stream enable/status, panel replay tunnel optimization, video CRC capture, and memory power state.
- Link/DPHY enable/reset, lane/mode configuration, active/disabled/CRC/error status, test pattern generation, FEC, MST VC payload allocation, timestamp generation, and DPHY symbol override/debug state.

Persistence is hardware-defined. Configuration bits generally remain until driver reprogramming, stream teardown, power-gating, suspend/resume, GPU reset, or ASIC reset. Status bits can be read-only, sticky, write-one-to-clear, self-clearing, or meaningful only while the relevant display clocks and power domains are active. This generated header does not document those access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which supplies the matching DCN 3.5.1 MMIO register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which includes this header and initializes APG, HPO DP stream encoder, HPO DP link encoder, stream encoder, and related register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`, where `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST*` and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST` consume `DP_STREAM_ENC*` and `DP_SYM32_ENC*` fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h` and `dcn31_apg.c`, which consume APG reset/enable/audio-stream/debug/memory-power fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.h` and VPG users, which consume VPG generic packet data, update, pending, and conflict fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c` and `display/dc/irq/dcn351/irq_service_dcn351.c`, which include the same generated DCN351 register headers for firmware service and IRQ register access.

Instance mapping is an important contract. In this range, HPO stream encoder 1 uses `APG1`, `DME6`, `VPG6`, and `DP_SYM32_ENC1`; stream encoder 2 uses `APG2`, `DME7`, `VPG7`, and `DP_SYM32_ENC2`; stream encoder 3 begins with `APG3`, `DME8`, `VPG8`, and `DP_SYM32_ENC3`. The suffixes are not globally interchangeable across APG/DME/VPG/SYM32 families, so resource code must use the intended register tables rather than assuming a simple shared numeric namespace.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing the wrong MMIO bit, corrupting neighboring fields, failing stream enablement, losing audio packets, or breaking link/DPHY status handling.
- The file is generated metadata. Manual edits risk diverging from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- Chunk boundaries split real registers. The opening `DP_DPHY_SYM320...CRC_CONFIG0` masks lack their shifts in this artifact, and the closing `DP_SYM32_ENC3...GSP_CONTROL7` shifts lack their masks here.
- Repeated HPO instances are easy to confuse. `DP_STREAM_ENC1/2/3`, `APG1/2/3`, `DME6/7/8`, `VPG6/7/8`, `DP_SYM32_ENC1/2/3`, and `DP_DPHY_SYM320/321` have similar names but target distinct hardware.
- Reset/status and pending fields are sequencing-sensitive. Polling the wrong `RESET_DONE`, `FIFO_RESET_DONE`, `VID_STREAM_STATUS`, generic-packet pending bit, or CRC-valid bit can cause timeout, stale state, or premature stream activation.
- Sideband and audio packet programming is timing-sensitive. Incorrect GSP payload size, transmission line number, SOF reference, double-buffer enable, ASP/audio mute, metadata enable, or update trigger fields can produce missing HDR/metadata packets, broken audio, or packet conflicts visible only on certain modes.
- Power-state fields can mask bugs. For APG, DME, VPG, Symbol32, and DPHY memory/power controls, invalid masks may only fail after low-power transitions, suspend/resume, or clock-gating paths.
- Link/DPHY fields interact with link training and diagnostics. Mistakes in lane count, mode, FEC, MST VC payload allocation, clock pattern, PRBS/test pattern, symbol override, or CRC/error status can break DisplayPort bring-up or obscure validation failures.

## Test Signals

Useful validation combines generated-header checks and hardware behavior:

- Build AMDGPU display support with DCN351 enabled. Missing or renamed macros should fail in `dcn351_resource.c`, DMUB DCN351 register setup, IRQ service setup, APG/VPG/HPO DP stream encoder tables, or link encoder tables.
- Mechanically verify shift/mask pairs for lines 39862-42078, allowing only the known boundary exceptions: three opening `DP_DPHY_SYM320...CRC_CONFIG0` masks and two closing `DP_SYM32_ENC3...GSP_CONTROL7` shifts.
- Compare this slice against AMD's DCN 3.5.1 register database and nearby generated headers such as `dcn_3_5_0_sh_mask.h` where field layouts are expected to match.
- Exercise HPO DisplayPort streams backed by stream encoder instances 1, 2, and 3 across enable, blank, modeset, disable, suspend/resume, and hotplug. Watch `DP_STREAM_ENC_CLOCK_EN`, FIFO reset-done, FIFO error, `DP_SYM32_ENC_RESET_DONE`, pixel FIFO overflow, and `VID_STREAM_STATUS`.
- Validate audio packet paths using APG1-3: stereo, multichannel LPCM, HBR/compressed formats, mute/unmute, stream ID changes, and audio CRC diagnostics.
- Validate VPG/DME sideband behavior with HDR/static metadata, generic info packets, ISRC/MPEG packets, one-shot versus frame/immediate updates, pending-bit clearing, and conflict status handling.
- Run DisplayPort link and DPHY diagnostics on both HPO DPHY instances where possible, including link training, lane-count changes, MST payload updates, FEC, PRBS/test patterns, symbol overrides, CRC capture, and error status readback.
- Watch kernel logs, display debugfs output, and external sink behavior for HPO stream timeouts, silent audio, missing HDR metadata, packet conflicts, CRC mismatches, DP training failures, resume-only failures, and instance-specific regressions.

## Cross-Chunk Notes

This is a middle chunk of `dcn_3_5_1_sh_mask.h`. The previous chunk is needed for the full `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0` field set and earlier HPO stream/link definitions. The next chunk is needed to complete `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL7` and the rest of Symbol32 encoder 3. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.5.1 HPO DisplayPort, APG, VPG, DME, link, or DPHY fields.
