# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 49492-51890

## Purpose

This chunk is a generated AMD DCN 3.6.0 register shift/mask slice. It has no executable code; it exports preprocessor constants that describe bit positions and masks for memory-mapped display-controller registers. Runtime AMDGPU display code pairs these constants with `dcn_3_6_0_offset.h` register offsets and then uses register helpers to pack, isolate, update, or decode individual fields without hard-coding raw bit layouts in driver logic.

The requested range contains 2,139 `#define` entries: 1,070 `__SHIFT` macros and 1,069 `_MASK` macros. It also contains 215 register-name comments and 15 address-block comments. The range starts in the middle of `HDMI_TB_ENC_HC_ACTIVE_BLANK` and ends in the middle of `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_GSP_CONTROL10`, so both boundaries are artificial chunk boundaries rather than semantic hardware boundaries.

Although this source is located under a local `ceph-client` tree, the content in this range is AMDGPU DCN display hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct MMIO operations in this range. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for the named field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

The major register families covered by this chunk are:

- `HDMI_TB_ENC_*`: tail of HDMI timing/block encoder fields for horizontal active/blank count, HDMI CRC control/result, EESS encryption control, borrow/skip mode, and input FIFO error status.
- `DP_STREAM_ENC0_*`, `DP_STREAM_ENC1_*`, and `DP_STREAM_ENC2_*`: HPO DP stream encoder fields for stream-clock enable/status selection, pixel/audio input muxing, FIFO reset/enable/read-start/read-clock selection, calibrated FIFO level reporting, and spare bits.
- `APG0_*`, `APG1_*`, and `APG2_*`: audio packet generator controls for reset, enable, DP audio stream ID, channel-count override, debug audio generation, ACP/audio-info source selection, audio CRC setup/result, audio/HBR/FIFO status, output-active status, memory-power controls, and spare bits.
- `DME6_*`, `DME7_*`, and `DME8_*`: display metadata engine controls for HUBP requestor ID, metadata engine enable, stream type, double-buffer pending/taken/clear/disable state, missed-transmission status/clear, and DME memory-power state.
- `VPG6_*`, `VPG7_*`, and `VPG8_*`: video packet generator generic-packet access/data, generic-stream-packet frame-update and immediate-update trigger bits for generic packet slots 0 through 14, conflict status/clear, memory-power controls, ISRC packet access/data, and MPEG info bytes.
- `DP_SYM32_ENC0_*` and `DP_SYM32_ENC1_*`: mostly complete HPO 32-bit DP symbol encoder layouts for reset/enable, pixel-to-symbol FIFO, MSA and pixel-format double-buffering, pixel format, MSA data lanes, hblank minimum symbol width, generic SDP/GSP controls 0 through 14, audio SDP controls, metadata packet controls, MSA/VBID/video-stream controls, panel replay, video CRC controls/results/status, symbol count status/control, memory power, and spare bits.
- `DP_SYM32_ENC2_*`: beginning of the same symbol-encoder layout for instance 2, through the first two `GSP_CONTROL10` shift fields at the chunk boundary. The remainder of instance 2 is in the next chunk.

The repeated instance numbering matters. `DP_STREAM_ENC0` pairs with `APG0`, `DME6`, `VPG6`, and `DP_SYM32_ENC0`; the next two HPO stream paths repeat as `DP_STREAM_ENC1`/`APG1`/`DME7`/`VPG7`/`DP_SYM32_ENC1` and `DP_STREAM_ENC2`/`APG2`/`DME8`/`VPG8`/`DP_SYM32_ENC2`. The DME/VPG numbering reflects the wider display block namespace rather than a zero-based local sequence.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU display code that includes this generated file:

1. DCN 3.6 resource, IRQ, and DMUB code include `dcn_3_6_0_offset.h` and this `dcn_3_6_0_sh_mask.h` header.
2. Register-list macros such as `SE_SF(...)` token-paste register and field names into shift/mask tables.
3. DCN 3.6 resource construction wires those tables into HPO DP stream encoder, APG, VPG, DME, IRQ, DMUB, and other display block objects.
4. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers rely on the tables populated from these macros to touch only the intended field bits.

The macros do not encode sequencing rules. Consumers still need to reset and enable stream/symbol encoders in the right order, wait for reset-done bits, set muxes before enabling output, program SDP packet memory before triggering transmission, coordinate audio packet generation with audio stream setup, and avoid reading status or CRC fields while the relevant clock or memory block is powered down.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes hardware-visible DCN 3.6 register state:

- HDMI timing/CRC/encryption/mode/FIFO diagnostic state.
- HPO DP stream encoder clock, pixel mux, audio mux, and FIFO state.
- APG reset, audio stream ID, debug generation, packet source, CRC, FIFO overflow, output-active, and memory-power state.
- DME metadata enablement, stream type, double-buffer handoff state, missed-transmission status, and memory-power state.
- VPG generic packet bytes, packet-slot update triggers, generic conflict flags, ISRC/MPEG packet bytes, and GSP memory-power state.
- DP symbol encoder reset/enable, video FIFO, pixel format, MSA payload, SDP/GSP scheduling, audio packet enable/mute controls, metadata packet controls, VBID and stream enablement, panel replay, CRC capture, symbol counting, and memory-power state.

Persistence is hardware-defined. Configuration fields generally remain until a modeset, stream teardown, power-gating transition, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, reset-done, FIFO-error, conflict, CRC, symbol-count, double-buffer-pending, and missed-transmission fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the related clock domain is active. This generated header does not encode those access semantics; driver code and hardware documentation must provide them.

## Dependencies And Integration Points

This file must stay synchronized with AMD's generated DCN 3.6.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` supplies the matching MMIO register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes the generated DCN 3.6 headers for DMUB register setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes the same headers for DCN 3.6 interrupt source tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes this header and builds DCN 3.6 HPO DP stream encoder shift/mask tables from `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(__SHIFT)` and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(_MASK)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` defines the shared HPO DP stream encoder register, shift, and mask table shape that consumes fields such as `DP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_CONTROL`, `DP_SYM32_ENC0_DP_SYM32_ENC_CONTROL`, `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL*`, and `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_AUDIO_CONTROL0`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h` consumes APG field names for reset, enable, DP audio stream ID, debug audio channel enablement, and memory-power forcing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.c` consume VPG generic packet, frame-update, immediate-update, status, and memory-power fields through register helpers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h` provides generated enum values for some fields represented here, including HDMI CRC source/type and input FIFO error values.

The direct behavioral integration surface is HPO DisplayPort and HDMI output programming: stream encoder clocking and input selection, DP symbol generation, audio packet generation, metadata/SDP packet transport, video packet updates, CRC diagnostics, and stream status readback.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting adjacent MMIO fields, disabling output, misrouting audio/video streams, or breaking readback decoding.
- The header is generated. Manual edits risk divergence from the authoritative register database, firmware assumptions, hardware documentation, and `dcn_3_6_0_offset.h`.
- The chunk boundaries are not semantic. The first register group is missing the `HDMI_HC_ACTIVE` shift from the previous line, and the `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_GSP_CONTROL10` group continues after line 51890.
- Instance repetition makes generator or copy drift hard to spot. Instance 0 working does not prove instances 1 or 2 are correct, especially where DME/VPG indices use `6/7/8` while stream/APG/symbol encoder indices use `0/1/2`.
- Reset, enable, and reset-done fields are sequencing-sensitive. Incorrect masks can produce timeout loops, stuck disabled encoders, or writes that appear to succeed while the block remains in reset.
- Clock and FIFO fields are timing-sensitive. Wrong FIFO reset, read-start-level, read-clock-source, or active/error masks can cause intermittent underflow, corruption, or false diagnostics that only appear under high bandwidth or clock-ramp transitions.
- Generic SDP/GSP packet controls are packet-scheduling-sensitive. Incorrect one-shot, continuous, double-buffer, payload-size, SOF-reference, or line-number fields can send HDR/AVI/vendor/audio metadata on the wrong frame, miss deadlines, or leave pending bits stuck.
- APG and audio CRC/status fields are user-visible for DP audio. Mask mistakes can produce missing channels, wrong stream IDs, false FIFO overflow handling, invalid CRC results, or broken HBR audio enablement.
- DME and VPG memory-power fields interact with clock/power gating. Access while the block is gated can produce stale status or dropped packet programming unless the caller follows block-specific power sequencing.
- HDMI CRC and input FIFO fields are mostly diagnostic; a mask error may not affect ordinary display output but can break validation, factory diagnostics, or debug tooling.

## Test Signals

Useful validation combines generated-header checks with DCN 3.6 hardware behavior:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed constants should fail in DCN36 DMUB, IRQ, resource, HPO DP stream encoder, APG, VPG, DME, or register-helper table construction.
- Mechanically compare this range against AMD's authoritative DCN 3.6.0 register source and the adjacent `dcn_3_6_0_offset.h` names, accounting for the artificial line boundaries at the start and end.
- Run static consistency checks that complete register groups have matching `__SHIFT` and `_MASK` entries across chunk boundaries, especially `HDMI_TB_ENC_HC_ACTIVE_BLANK` and `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_GSP_CONTROL10`.
- Exercise HPO DP stream enable/disable, stream mux selection, link bring-up, MST or multi-stream routing where available, hotplug, modesets, suspend/resume, and rapid stream teardown/recreation.
- Exercise DP audio through APG paths, including mute/unmute, channel-count changes, HBR audio, stream ID changes, audio CRC capture, and FIFO overflow status clearing.
- Exercise SDP/GSP metadata paths: HDR metadata, infoframes, vendor-specific packets, ISRC/MPEG packet programming, one-shot versus continuous transmission, frame-update versus immediate-update behavior, and packet-slot conflicts.
- Validate DME metadata double-buffer handling by checking pending/taken/missed-transmission status under normal modesets, high frame rates, and metadata updates near vblank boundaries.
- Validate DP symbol encoder CRC, symbol count, VBID compressed-stream flag fields, panel replay controls, and pixel-format/MSA double-buffering across common pixel formats, DSC/compressed stream scenarios, and low-power transitions.
- Watch kernel logs and display diagnostics for stuck reset-done waits, stream-enable failures, underflow/FIFO errors, packet deadline misses, stale pending bits, audio dropouts, CRC mismatches, memory-power transition failures, and resume-only HPO display artifacts.

## Cross-Chunk Notes

The previous chunk contains the beginning of the HDMI timing/block encoder group, including fields immediately before `HDMI_TB_ENC_HC_ACTIVE_BLANK__HDMI_HC_BLANK__SHIFT`. The next chunk continues `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_GSP_CONTROL10` and the rest of the instance-2 DP symbol encoder fields. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.6 shift/mask definitions or all HPO DP stream encoder instances.
