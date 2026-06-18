# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 49519-51930

## Scope

This chunk is generated AMD DCN 3.1.6 display register field metadata. It contains C preprocessor constants only: paired `__SHIFT` and `_MASK` macros for fields inside Display Stream Compression, HPO, HDMI/DP audio, metadata, video packet generator, DisplayPort stream encoder, and DisplayPort symbol encoder registers. There are no functions, structs, enums, branches, loops, allocations, includes, or software-owned state in this range.

The reviewed span contains 2,145 `#define` entries: 1,076 shift definitions and 1,069 mask definitions. The mismatch is from chunk boundaries. The range starts with the final two masks for `DSCC2_DSCC_PPS_CONFIG18`, whose shifts and earlier masks are above line 49519, and it ends inside `DP_SYM32_ENC1_DP_SYM32_ENC_SDP_GSP_CONTROL12`, before the rest of that register's masks and following GSP controls.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU Display Core hardware metadata rather than distributed filesystem code.

## Purpose And Hardware Surface

The purpose of this header slice is to describe bit layouts for DCN 3.1.6 display hardware registers. The companion `dcn_3_1_6_offset.h` header supplies register addresses or index selectors; this file supplies the masks and shifts used by AMD display register helpers to pack field writes and decode readbacks.

The hardware surface covered here includes:

- Tail fields for DSC compressor instance 2 (`DSCC2`) and its DSC client interface/top/performance monitor blocks.
- HPO top clock/control and HPO DP stream mapper registers.
- HPO HDMI stream encoder 0 audio formatter (`AFMT5`), data/metadata engine (`DME5`), and video packet generator (`VPG5`) registers.
- HPO DP stream encoder 0 and 1 register families, including audio packet generator (`APG0`, `APG1`), DME (`DME6`, `DME7`), VPG (`VPG6`, `VPG7`), and DP stream encoder clock/input/audio/FIFO controls.
- DP 32-symbol encoder instance 0 (`DP_SYM32_ENC0`) video, MSA, SDP/GSP, audio SDP, metadata packet, CRC, panel replay, and memory-power fields.
- The beginning of DP 32-symbol encoder instance 1 (`DP_SYM32_ENC1`), through the first part of `SDP_GSP_CONTROL12`.

These definitions allow higher-level DCN316 resource, stream encoder, audio, metadata, and diagnostics code to bind one register-list template to concrete generated field names for each hardware instance.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low-bit position for a field in a 16-bit or 32-bit hardware register value.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in that register value.
- `//<REGISTER>` comments group field macros by generated register name.
- `// addressBlock: ...` comments mark the hardware address block that owns following register groups.

Important register families in this range:

- `DSCC2_DSCC_PPS_CONFIG19` through `PPS_CONFIG22` continue the DSC Picture Parameter Set range table for QP ranges 7-14, with min-QP, max-QP, and BPG-offset fields packed in repeated bit groups. The first two lines also complete masks for QP range 6 in `PPS_CONFIG18`.
- `DSCC2_DSCC_MEM_POWER_CONTROL` controls low-power/default/force/disable/state fields for DSC memory and native 4:2:2 memory. `DSCC2_DSCC_*_SQUARED_ERROR_*`, `MAX_ABS_ERROR*`, rate-buffer fullness, rate-control-buffer fullness, and debug-bus rotate registers expose DSC quality/error, buffer, and debug readbacks.
- `DSCCIF2_DSCCIF_CONFIG0` and `CONFIG1` describe DSC client-interface input underflow recovery/interrupt/status, input pixel format, bits per component, double-buffer update-pending, and picture width/height fields.
- `DSC_TOP2_DSC_TOP_CONTROL` and `DSC_DEBUG_CONTROL` expose DSC clock enable, clock-gate disable, debug enable, and test clock mux selection.
- `DC_PERFMON21_*` and `DC_PERFMON22_*` define performance counter event selection, counted-value type, state readback, control/start/stop/clear behavior, current-value interrupt conditions, and high/low counter values for the DSC2 and HPO performance monitor blocks.
- `HPO_TOP_CLOCK_CONTROL` defines per-clock enable, gate-disable, and ready/state fields for HPO DP, HPO HDMI, link symbol, ref, and DP stream clocks. `HPO_TOP_HW_CONTROL` exposes HPO topology/hardware enable state.
- `DP_STREAM_MAPPER_CONTROL0` through `CONTROL3` map logical stream slots to HPO stream encoders.
- `AFMT5_*` covers HDMI audio formatter behavior: VBI/audio packet control, channel enables, DP audio stream ID, HBR overrides, HDMI audio infoframe fields, IEC 60958 channel-status words, audio CRC generation/readback, audio test ramp counters, status bits, FIFO-overflow/audio-enable-change acknowledgements, infoframe source/update, audio source select, and memory-power state.
- `DME5_DME_CONTROL`, `DME6_DME_CONTROL`, and `DME7_DME_CONTROL` expose metadata requestor ID, metadata engine enable, stream type, double-buffer pending/taken/clear/disable, and missed-transmission clear/status fields. Their `DME_MEMORY_CONTROL` registers define DMEM power gating and DME-specific memory power controls.
- `VPG5_*`, `VPG6_*`, and `VPG7_*` describe generic packet access/data, frame-update and immediate-update controls for generic stream packets 0-14, generic packet status, memory power, ISRC packet access/data, and MPEG information registers.
- `DP_STREAM_ENC0_*` and `DP_STREAM_ENC1_*` define stream-encoder clock enables, clock-gate disables, input mux selection, audio mux selection, clock-ramp FIFO threshold/level/clear behavior, FIFO underflow/overflow status and interrupt controls, and spare bits.
- `APG0_*` and `APG1_*` define DP audio packet generator enable, compressed audio mode, double-buffering, packet transmission control, audio CRC test/readback, status, memory-power, and spare fields.
- `DP_SYM32_ENC0_*` defines the first DP symbol encoder instance: encoder enable, HPO stream source select, link/channel selection, video FIFO enable/underflow/status, video MSA double-buffer controls, pixel format, MSA words 0-8, HBLANK minimum symbol width, SDP/GSP transmission controls 0-14, audio SDP, metadata packet control, MSA/VBID/stream/panel-replay control, CRC generation/result/status, memory power, and spare fields.
- `DP_SYM32_ENC1_*` starts the second DP symbol encoder instance with the same control, video FIFO, MSA, pixel format, and GSP transmission-control pattern, but this chunk ends before the full instance-1 register family is present.

## Control Flow

This header has no executable control flow. Runtime sequencing is supplied by AMDGPU Display Core code that includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`, builds register and field tables with generated macros, and then calls register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, or related token-pasting helpers.

A typical use path is:

1. DCN316 resource construction selects a hardware object, such as an HPO DP stream encoder, DP symbol encoder, audio packet generator, VPG, DME, DSC block, or performance monitor.
2. The companion offset header supplies the register address for the selected instance.
3. This shift/mask header supplies the field position and mask.
4. Register helpers pack writes, preserve neighboring fields, decode status, or acknowledge events.
5. Hardware latches configuration, reports status, transmits packets, counts events, gates memory/clocks, or clears sticky status according to the register's hardware semantics.

The macros do not encode ordering. Callers must still sequence DSC setup, HPO clock enable, stream mapping, stream encoder programming, audio packet generator setup, metadata/VPG double-buffer updates, DP symbol encoder enable, CRC tests, interrupt acknowledgements, and memory-power transitions in functional driver code.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO hardware state in the GPU display engine.

Configuration-like fields include DSC QP ranges, DSC memory power controls, DSC input pixel format and dimensions, DSC/HPO/DP clock enables and gate disables, stream-to-encoder mappings, AFMT audio packet/infoframe/channel-status/ramp/source controls, APG audio packet controls, DME metadata engine controls, VPG generic packet controls, DP stream encoder input/audio muxing, symbol encoder source/link selection, pixel format, MSA/VBID/stream/panel-replay controls, SDP/GSP scheduling, and memory-power controls.

Readback/status fields include DSC squared/max error and buffer fullness counters, underflow and double-buffer pending state, performance counter active/current/high/low/count state, HPO clock ready/state bits, AFMT audio FIFO overflow and audio enable/HBR status, APG CRC/status fields, DME double-buffer taken/pending and missed-transmission state, VPG generic packet/ISRC/MPEG status data, DP stream encoder FIFO levels and underflow/overflow status, DP symbol encoder FIFO underflow/status, CRC results/status, GSP transmission pending/deadline missed/double-buffer pending, and memory-power state.

Several names imply write side effects: interrupt acknowledgements, clear bits, double-buffer update/taken clear bits, FIFO status clears, CRC enable/continuous controls, audio FIFO overflow acknowledge, audio-enable-change acknowledge, metadata missed-transmission clear, and memory-power force/disable controls. The generated mask/shift macros do not label read-only, write-one-to-clear, sticky, self-clearing, or power-managed fields; that behavior must be enforced by the driver code and the hardware specification.

## Dependencies And Integration Points

This chunk must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`. The offset header defines the register addresses; this header defines the bit layouts. A missing macro name generally fails compilation, while an incorrect numeric shift or mask can compile and silently program or decode the wrong hardware bits.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which binds DCN316 register metadata for the DMUB service.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes the DCN316 offset and shift/mask headers while constructing display resources, DIO links, and stream encoders.

Functional consumers are mostly indirect through generated register tables. DCN316 resource construction and display objects use these macros to configure DSC, HPO output paths, DP/HDMI stream encoders, audio packet generators, metadata packet paths, video packet generators, performance counters, clock gating, CRC diagnostics, and memory-power controls. The macros in this range are instance-specific; for example `AFMT5`, `DME5`, `VPG5`, `DME6`, `VPG6`, `DP_SYM32_ENC0`, and `DP_SYM32_ENC1` names target different hardware blocks even when their field layouts are repetitive.

## Risks And Maintenance Notes

- The primary risk is generated-header drift from the DCN 3.1.6 register database. Wrong numeric masks or shifts can corrupt DSC PPS programming, clock gating, HPO routing, stream encoder setup, packet scheduling, audio infoframes, metadata transmission, CRC diagnostics, or power-management state without producing a compile error.
- The span starts mid-register. Only the final masks for `DSCC2_DSCC_PPS_CONFIG18` are present here; adjacent chunks own the shifts and earlier masks for QP range 5 and part of range 6.
- The span ends mid-register family. `DP_SYM32_ENC1_DP_SYM32_ENC_SDP_GSP_CONTROL12` is incomplete in this chunk, and later chunks own the remaining masks and following instance-1 SDP/audio/metadata/video/CRC/memory-power fields.
- Many families are repeated by instance. A generator error in one instance may compile because the same field exists for another instance, but runtime failures would appear only on displays or connectors routed through that specific HPO, APG, VPG, DME, or DP symbol encoder instance.
- Dense packet-control fields combine enable, one-shot trigger, double-buffer enable, payload size, start-of-frame reference, line number, pending, and missed-deadline bits. Read-modify-write mistakes can cause missing, duplicated, late, or continuously transmitted secondary data packets.
- Audio fields are protocol-visible. Bad AFMT/APG masks can produce incorrect IEC 60958 channel status, HDMI audio infoframes, HBR state, channel allocation, channel enables, CRC diagnostics, or FIFO acknowledgement behavior.
- Memory and clock power fields can affect display bring-up and suspend/resume. Incorrect force/disable/state masks may leave blocks clock gated, fail to save power, or race with hardware low-power transitions.
- Status/ack/clear fields are easy to misuse because generated macros do not capture side effects. Treating an acknowledge or clear bit as persistent state can drop events; failing to preserve neighboring bits can change unrelated interrupt, FIFO, or double-buffer behavior.

## Test Signals

Useful validation for changes touching this chunk includes:

- Compile AMDGPU Display Core with DCN316 enabled. This catches missing or malformed generated macro names referenced by DCN316 resource, DMUB, stream encoder, DSC, audio, metadata, and diagnostics code.
- Regenerate or mechanically compare `dcn_3_1_6_sh_mask.h` against the authoritative DCN 3.1.6 register database, especially for chunk-boundary registers `DSCC2_DSCC_PPS_CONFIG18` and `DP_SYM32_ENC1_DP_SYM32_ENC_SDP_GSP_CONTROL12`.
- Check that complete register groups in this slice have paired `__SHIFT` and `_MASK` definitions, while allowing the known boundary exceptions at the beginning and end.
- Preprocess representative `REG_GET`, `REG_SET`, `REG_UPDATE`, register-table, and field-table macros to confirm token concatenation resolves to the intended instance-specific symbols such as `AFMT5`, `APG0`, `APG1`, `VPG6`, `DME7`, `DP_STREAM_ENC1`, or `DP_SYM32_ENC0`.
- Runtime DCN316 display tests covering HDMI/DP modeset, HPO stream mapping, DSC-enabled modes, DP stream encoder enable/disable, MST or multi-stream scenarios where available, suspend/resume, and display hotplug.
- Runtime audio tests over HDMI/DP covering PCM playback, channel mapping, multichannel layouts, sample-rate changes, HBR/encoded audio where supported, audio enable/disable, FIFO overflow acknowledgement, and APG/AFMT CRC readback.
- Metadata and packet tests for VPG/DME/DP symbol encoder paths: HDR or other SDP metadata updates, generic packet one-shot and continuous transmission, double-buffer pending/taken transitions, missed-transmission/deadline status, ISRC/MPEG packet fields, and line-number scheduling.
- Register-dump validation before and after programming. Writes should affect only intended masked fields and preserve neighboring bits in dense registers such as GSP controls, AFMT audio packet controls, APG controls, DME controls, VPG frame/immediate update controls, performance monitor controls, memory-power controls, and stream encoder FIFO/status controls.

## Cross-Chunk Notes

Previous chunks own the beginning of DSC instance 2 and the full setup for `DSCC2_DSCC_PPS_CONFIG18` before the final masks visible here. Later chunks continue `DP_SYM32_ENC1` after the partial `SDP_GSP_CONTROL12` definition. The final per-file report should merge adjacent chunk reports before making complete claims about all DCN 3.1.6 DSC or DP symbol encoder instance coverage.
