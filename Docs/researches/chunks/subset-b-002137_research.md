# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 47051-49491

## Purpose

This chunk is a generated AMD DCN 3.6.0 register shift/mask slice. It contains no executable logic; it exports C preprocessor constants that describe bit positions and masks for memory-mapped display-controller registers. Runtime DCN code combines these constants with the companion `dcn_3_6_0_offset.h` register offsets and the AMD display register-helper macros so field updates can be expressed by register and field name rather than hard-coded numeric bit layouts.

The requested range contains 1,070 `__SHIFT` macros and 1,078 `_MASK` macros, organized by 237 register-name comments and 21 address-block comments. The range starts in the tail of `DSCC1_DSCC_PPS_CONFIG22` after earlier DSC picture-parameter-set fields for DSC compressor instance 1, covers complete DSC compressor/interface/top/perfmon groups for DSC instances 2 and 3, then covers HPO top, HPO DP stream mapping, HPO perfmon, HPO HDMI link/FRL/stream encoder, AFMT audio packet, DME, VPG, and the beginning of HDMI TB encoder fields. It ends at `HDMI_TB_ENC_HC_ACTIVE_BLANK`, with later HDMI TB CRC/encryption/mode fields continuing after the chunk boundary.

Although this source path is under a local `ceph-client` mirror, this file is AMDGPU DCN display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, or direct I/O operations in this slice. Its only API surface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, preserving, or clearing a field during register read/modify/write.

The main register families in this chunk are:

- `DSCC1_*`: tail of DSC compressor instance 1 PPS range fields for rate-control QP/BPG ranges, DSC memory-power control, squared-error/max-absolute-error counters, rate-buffer and rate-control-buffer fullness levels, and test debug bus rotation.
- `DSCCIF1_*` and `DSC_TOP1_*`: DSC1 input-interface underflow/status, input pixel format, picture dimensions, DSC clock enable/gating, and debug clock selection.
- `DC_PERFMON20_*`: DSC1-side performance counter controls, counted-value mode, state selection for counters 0-7, count-off interrupt control, per-counter interrupt status/ack bits, and low/high counter value reads.
- `DSCC2_*` and `DSCC3_*`: complete DSC compressor layouts for instances 2 and 3, including slice layout, ICH behavior, rate-control buffer model size, status, overflow/underflow interrupt enables/status, full PPS programming registers `PPS_CONFIG0` through `PPS_CONFIG22`, memory-power state, error statistics, fullness counters, and debug bus rotation.
- `DSCCIF2_*`, `DSCCIF3_*`, `DSC_TOP2_*`, and `DSC_TOP3_*`: repeated DSC input-interface, picture-size, clock, dynamic clock-gating, and debug-control fields for DSC instances 2 and 3.
- `DC_PERFMON21_*` and `DC_PERFMON22_*`: performance-monitor instances paired with DSC2 and DSC3, mirroring the `DC_PERFMON20` field model.
- `HPO_TOP_*`: HPO top-level clock-control and hardware-control fields for register clock gating, HDMI stream encoder power state, HDMI character/output-clock enables, test clock selection, and HPO DP stream output enables.
- `DP_STREAM_MAPPER_CONTROL0..3`: HPO DP stream-to-link target selection fields, mapping logical streams onto HPO DP link targets.
- `DC_PERFMON23_*`: HPO-level performance-monitor controls and counters, with the same counter/run/interrupt/read shape as the DSC perfmon groups.
- `HDMI_LINK_ENC_*`, `HDMI_FRL_ENC_*`, and `HDMI_STREAM_ENC_*`: HPO HDMI link encoder enable/clock state, HDMI FRL enable/metadata/meter-buffer/memory-power fields, stream encoder clock/control/mux fields, and clock-ramp-adjuster FIFO status/control.
- `AFMT5_*`: audio formatter packet control and data fields for ACP, VBI/audio packets, audio infoframes, IEC 60958 channel-status words, audio CRC, ramp generator, audio source selection, packet-status bits, and AFMT memory-power controls.
- `DME5_*`: DME enable/reset/ready/state and DME memory-power control.
- `VPG5_*`: generic packet access/data, frame and immediate update controls for generic packets 0-14, packet lock/conflict status, VPG memory power, ISRC data access, and MPEG infoframe byte/update fields.
- `HDMI_TB_ENC_*`: beginning of HDMI TB encoder control, pixel-format, packet-control, ACR, VBI, general-control, generic-packet scheduling/immediate-send, packet line/EMP placement, double-buffer control, ACR CTS/N programmed and status values, borrow/rate-buffer controls, metadata packet scheduling, and active/blank timing fields.

Many groups are generated per hardware instance. `DSCC2` and `DSCC3` repeat the same register-field layout, while `DC_PERFMON20` through `DC_PERFMON23` repeat the same performance-counter layout for different display blocks.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this generated header:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` and this shift/mask header.
2. Register-list macros token-paste register and field names into typed register, shift, and mask tables for DCN display blocks.
3. DCN 3.6 resource, DMUB, IRQ, HPO, HDMI, AFMT, VPG, DSC, and perfmon setup code wires those tables into block objects and hardware service helpers.
4. Runtime display paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers use these masks and shifts to touch only the intended MMIO bits.

The macros do not encode programming order. Consumers still need to sequence DSC PPS programming with stream enablement, program HPO stream mapping before link activation, coordinate HDMI link/FRL/stream clocks, load and schedule infoframes at valid lines, handle audio packet and ACR setup with audio state, acknowledge perfmon/status bits correctly, and respect power/clock gating rules.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It describes hardware-visible state in DCN 3.6 registers:

- DSC compressor state: PPS parameters, slice geometry, rate-control model parameters, QP ranges, buffer thresholds, BPG offsets, initial delays, memory-power controls, status, error counters, buffer fullness counters, and debug-bus rotation.
- DSC input-interface and top-level state: input pixel format, bits per component, picture dimensions, underflow recovery/status/interrupt enables, clock enable, static/dynamic clock-gating controls, and debug clock muxing.
- Performance-monitor state: event selection, counted-value type, hardware start/stop/count-off routing, active/counting state, per-counter interrupt state/acknowledge bits, and low/high counter values.
- HPO and DP stream state: top-level HPO clock/output enable controls and DP stream-to-link target mappings.
- HPO HDMI state: link encoder enable/clock controls, FRL encoding controls, stream encoder mux/clock/ramp-adjuster controls, DME control, TB encoder mode and timing fields, packet scheduling, audio clock regeneration, buffer prefill, and memory-power controls.
- Audio/infoframe metadata state: AFMT audio, VBI, ACP, audio infoframe, IEC 60958, CRC, ramp, and source-selection fields; VPG generic packet, ISRC, MPEG, immediate-update, frame-update, conflict/lock, and memory-power fields.

Persistence is hardware-defined. Configuration fields generally remain until a modeset, link reconfiguration, DSC/FRL enable transition, audio reprogramming, power-gating event, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, pending, CRC, counter, conflict, ready, and error fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the owning block's clocks are running. This generated header does not identify access semantics; consumers must rely on the register specification and block-specific driver code.

## Dependencies And Integration Points

This file must stay synchronized with AMD's generated DCN 3.6.0 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` supplies the companion MMIO register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes this generated shift/mask header for DCN 3.6 DMUB register setup.
- DCN 3.6 resource and IRQ setup code uses the generated register namespace to build hardware register tables for display block construction and interrupt handling.
- Shared HPO DP stream encoder code consumes `DP_STREAM_MAPPER_CONTROL0..3` fields to select HPO DP link targets.
- Shared HDMI/HPO stream and link encoder code consumes the HPO top, HDMI link, FRL, stream encoder, DME, VPG, AFMT, and HDMI TB fields when enabling HDMI 2.1/FRL paths, programming packet transport, and controlling audio/infoframe metadata.
- DSC programming code consumes `DSCC*`, `DSCCIF*`, and `DSC_TOP*` fields when setting Display Stream Compression PPS values, enabling DSC blocks, handling underflow/error status, and coordinating DSC clocks and memory power.
- Performance-monitor and diagnostics paths consume `DC_PERFMON20..23` fields for counter configuration, status, interrupt acknowledgement, and low/high counter reads.

The most direct behavioral integration from this range is display output bring-up and diagnostics for compressed streams and high-bandwidth HPO outputs: DSC PPS/rate-control setup, HPO DP stream mapping, HDMI FRL/link/stream encoder setup, audio clock regeneration, metadata/infoframe scheduling, generic packet updates, and per-block performance monitoring.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong MMIO bit, preserving stale adjacent bits, or silently disabling a hardware feature.
- The file is generated. Manual edits risk divergence from the authoritative register database, matching offset header, firmware assumptions, and silicon documentation.
- The chunk boundaries are not semantic. DSC1 PPS fields started before line 47051, and HDMI TB encoder fields continue after line 49491.
- Repeated DSC and perfmon layouts make generator drift hard to see. DSC2 can be correct while DSC3, or one perfmon instance, is wrong.
- DSC PPS fields are interoperability-sensitive. Incorrect rate-control, slice, buffer, QP, BPG, delay, or bits-per-pixel masks can produce link training failures, blank output, decompressor errors, compression artifacts, or sink incompatibility that appears only for particular resolutions and DSC slice layouts.
- Underflow, overflow, end-of-frame, status, pending, and ack fields are side-effect-sensitive. Confusing status with interrupt enable or ack bits can cause missed diagnostics, stuck interrupts, or interrupt storms.
- HPO stream mapping fields are topology-sensitive. Wrong stream-to-link target masks can route a stream to the wrong link, break MST-style mappings, or leave an enabled stream disconnected.
- HDMI FRL/link/stream encoder fields are timing- and clock-sensitive. Incorrect clock, ramp FIFO, FRL metadata, active/blank timing, pixel-format, or borrow/rate-buffer fields can cause black screens, audio/video dropouts, or failures only at high TMDS/FRL rates.
- AFMT, VPG, and HDMI TB packet fields are protocol-sensitive. Bad packet line, EMP, immediate-update, lock, generic-send, metadata, ISRC, MPEG, ACR, or audio-info masks can cause HDR/VRR/vendor infoframes, audio channel status, or metadata packets to be missing, duplicated, or sent on invalid lines.
- Memory-power fields for DSCC, HDMI FRL, AFMT, DME, VPG, and HDMI TB borrow buffers interact with clock/power gating. Writes at the wrong time can create intermittent resume, modeset, or high-bandwidth-link failures.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 3.6 hardware behavior:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed constants should fail in DCN36 DMUB/resource/IRQ setup or in shared DSC, HPO, HDMI, AFMT, VPG, DME, and perfmon register-table construction.
- Mechanically compare this range against AMD's authoritative DCN 3.6.0 register source and `dcn_3_6_0_offset.h`, allowing for the artificial chunk boundaries at DSC1 PPS and HDMI TB encoder definitions.
- Run static consistency checks that complete register groups have matching `__SHIFT` and `_MASK` definitions, especially across adjacent chunks for the partial `DSCC1_*` and `HDMI_TB_ENC_*` groups.
- Exercise DSC on supported panels and links across no-DSC/DSC transitions, multiple slice counts, different bits-per-pixel and bits-per-component settings, RGB/YUV formats, suspend/resume, hotplug, and high-resolution/high-refresh modes.
- Check DSC underflow/overflow/end-of-frame status paths, buffer fullness counters, error counters, and DSC memory-power transitions during rapid modesets and link changes.
- Exercise HPO DP stream mapping with each available HPO link target and with multi-stream or multiple active display scenarios where routing mistakes are visible.
- Exercise HDMI FRL and stream encoder paths at multiple FRL rates and pixel formats, including clock-ramp FIFO behavior, active/blank timing, metadata packet scheduling, and borrow/rate-buffer prefill controls.
- Validate AFMT/VPG/TB packet behavior through audio playback, audio clock regeneration/ACR status, HDR/static metadata, vendor-specific infoframes, MPEG/ISRC packets where applicable, generic packet immediate updates, and packet lock/conflict status.
- Exercise `DC_PERFMON20` through `DC_PERFMON23` counter setup, start/stop routing, count-off interrupts, status/ack handling, and high/low counter reads.
- Watch kernel logs, display diagnostics, link-training traces, CRCs, and sink behavior for blank output, DSC decode errors, FRL retrains, packet conflicts, missing metadata, audio dropouts, stuck pending bits, interrupt storms, and resume-only failures.

## Cross-Chunk Notes

The previous chunk contains earlier `DSCC1_DSCC_PPS_CONFIG*` fields needed to describe the complete DSC1 PPS layout. The next chunk continues HDMI TB encoder fields after `HDMI_TB_ENC_HC_ACTIVE_BLANK`, including CRC/encryption/mode and later HDMI TB state. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.6 shift/mask definitions, all DSC instances, or the full HDMI TB encoder register set.
