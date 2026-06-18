# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 39875-42091

## Purpose

This chunk is a generated AMD DCN 3.5.0 shift/mask register-field slice. It has no executable logic; it publishes C preprocessor constants that describe bit positions and bit masks inside DCN 3.5.0 display, audio, packet, and high-rate DisplayPort registers. Driver code combines these macros with the companion `dcn_3_5_0_offset.h` offsets and AMD display `REG_*` helper macros to read, write, update, or poll individual MMIO fields.

The requested range contains 2,217 `#define` entries: 1,108 `__SHIFT` macros and 1,109 `_MASK` macros. The count is intentionally unbalanced at the artificial chunk boundaries. The first lines are masks for `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0` fields whose shifts are in the previous chunk, and the final lines are shifts for `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` fields whose masks continue in the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, includes, variables, locks, allocations, or runtime branches in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position of a register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or preserve the same field.

Major macro families in this range are:

- `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_*` tail fields: masks and status/count fields for HPO DP DPHY/SYM32 CRC capture, including CRC enable/reset, lane/tap/scheduler source, start/end events, done state, CRC value, and symbol count.
- `DP_STREAM_ENC1`, `DP_STREAM_ENC2`, and `DP_STREAM_ENC3`: HPO DP stream encoder clock enables and clock-on status for `DISPCLK`, `SOCCLK`, `DPSTREAMCLK`, and `SYMCLK32`; pixel/audio input mux selectors; clock-ramp-adjuster FIFO enable/reset/read-start/read-clock/status/error fields; and spare fields.
- `DP_LINK_ENC1`: link encoder clock-control and spare fields for the high-performance output path.
- `APG1`, `APG2`, and `APG3`: Audio Packet Generator reset, enable, DP audio stream ID, ASP channel-count override, debug generator controls, packet source selectors, audio CRC controls/results, audio/HBR/FIFO overflow status, output-active state, memory power state, and spare fields.
- `DME6`, `DME7`, and `DME8`: metadata engine controls and memory power controls, including metadata requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable, missed transmission flags, memory power force/disable/state, and default low-power state.
- `VPG6`, `VPG7`, and `VPG8`: Video Packet Generator generic packet access/data bytes, frame and immediate update bits for generic packets 0-14, generic-packet conflict status/clear, memory power control, ISRC access/data bytes, and MPEG info bytes.
- `DP_DPHY_SYM321_DP_DPHY_SYM32_*`: a complete DPHY/SYM32 instance for HPO DP link behavior, including reset/enable/precoder/mode/lane count, status and update-pending bits, slot allocation table update, per-VC stream source and slot count, per-VC rate `X/Y` controls, test-pattern configuration, PRBS seeds, square-pulse width, custom symbols, error status, symbol override, and CRC controls/status/count.
- `DP_SYM32_ENC1` and `DP_SYM32_ENC2`: nearly complete HPO DP stream encoder field groups for stream instances 1 and 2, covering encoder reset/enable, video pixel format and double-buffering, FIFO reset/enable/status, stream enable/status/VBID fields, panel replay tunneling, SDP stream and CRC enable, audio SDP controls, metadata-packet controls, MSA control/data words 0-8, GSP controls 0-14, video CRC controls/results/status, memory power control, HBlank minimum symbol width, and spare fields.
- `DP_SYM32_ENC3`: beginning of the same HPO DP stream encoder field group for instance 3. This chunk covers encoder control, video FIFO, pixel format, double-buffer controls, MSA data words, HBlank control, and SDP GSP controls 0 through the shifts for control 6. The corresponding masks for the last control-6 fields and the rest of instance 3 continue after line 42091.

The most repetitive structures are the per-instance register blocks. `APG1-3`, `DME6-8`, `VPG6-8`, `DP_STREAM_ENC1-3`, and `DP_SYM32_ENC1-2` repeat identical or near-identical field layouts with instance-specific prefixes, while `DP_SYM32_ENC3` is truncated only because the chunk ends mid-block.

## Control Flow

This header has no runtime control flow. The runtime flow is supplied by the AMDGPU display stack:

1. DCN 3.5/3.5.1 resource code includes the generated offset and shift/mask headers.
2. Register-list macros paste symbolic instance names into generated macro names and initialize per-block register, shift, and mask tables.
3. Resource constructors attach those tables to stream encoders, HPO DP stream encoders, VPGs, APGs, AFMT/audio sub-blocks, and HPO DP link encoders.
4. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and wait/poll helpers to manipulate the fields described here.

Concrete integration found in this tree includes `dcn351_resource.c`, which builds `vpg_regs`, `apg_regs`, `stream_enc_regs`, and `hpo_dp_stream_enc_regs` tables. The HPO DP stream encoder table uses `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(__SHIFT)` and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(_MASK)` from `dcn31_hpo_dp_stream_encoder.h`; VPG and APG tables use `DCN31_VPG_MASK_SH_LIST()` and `DCN31_APG_MASK_SH_LIST()` from the shared DCN31 headers. HPO DP link behavior is similarly tied to generated DPHY/SYM32 fields through the `dcn31_hpo_dp_link_encoder` register macros.

The generated constants do not encode sequencing. Consumers still have to order clock enablement, reset/de-reset, FIFO reset and enable, stream/audio mux programming, packet-buffer updates, metadata double-buffer handoff, CRC capture, DPHY slot/rate updates, and power-gating transitions correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state in DCN 3.5.0 blocks:

- HPO DP stream encoder state: clock gating/status, mux selections, FIFO calibration/status, stream encoder reset/enable, video stream enable/status, pixel format, MSA payloads, HBlank symbol sizing, panel replay flags, SDP/GSP packet scheduling, metadata packet double buffering, audio SDP controls, video CRC capture, and memory power state.
- Audio packet generator state: APG reset/enable, DP audio stream ID, debug audio generation, packet source selection, audio CRC run/result/clear, FIFO overflow status, HBR/audio enable status, output-active status, and APG memory power.
- Video packet generator state: generic packet payload bytes, ISRC and MPEG info payload bytes, per-packet frame/immediate update request bits, conflict status, and memory power.
- Metadata engine state: requestor selection, metadata engine enable, double-buffer pending/taken/clear/disable state, missed transmission flags, and memory power state.
- HPO DP DPHY/SYM32 state: DPHY reset/enable, precoder/mode/lane settings, SAT and rate update-pending status, per-VC slot/rate controls, test-pattern generation, PRBS/custom-symbol controls, symbol override, error flags, CRC configuration/status/count, and link encoder clock/spare fields.

Persistence is hardware-defined. Configuration fields usually last until a modeset, stream teardown, link retraining, power-gating event, suspend/resume restore, driver reset, firmware reprogramming, or ASIC reset. Status, error, interrupt-like, clear, pending, and done fields may be read-only, sticky, write-one-to-clear, self-clearing, or only valid while related display clocks and power domains are enabled. This generated header does not describe access semantics; consuming code and the hardware register specification provide that context.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which defines the matching MMIO register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which creates DCN351 stream encoder, VPG, APG, and HPO DP stream encoder register tables from generated offsets, shifts, and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`, whose mask/shift list names stream encoder fields that are provided by this header for `DP_STREAM_ENC*` and `DP_SYM32_ENC*`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h`, whose VPG/APG field-list macros are satisfied by the generated `VPG*` and `APG*` definitions here.
- HPO DP link encoder code under `display/dc/hpo/dcn31` and `display/dc/hpo/dcn32`, which consumes DPHY/SYM32 control, status, SAT, rate, and test-pattern fields through generated register tables.
- DMUB DCN35 register initialization in `display/dmub/src/dmub_dcn35.c`, which includes the generated DCN 3.5 offset and shift/mask headers for firmware-facing register access tables.

Operationally, these fields integrate with DisplayPort 2.x/HPO stream setup, high-rate link encoder training and diagnostics, audio packet generation, infoframe and generic packet programming, HDR/metadata packet transmission, video CRC validation, panel replay packet controls, and low-power memory control for packet/metadata/encoder blocks.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while updating the wrong MMIO bits. Symptoms may be limited to one encoder, one HPO DP lane/link, one packet slot, or one audio generator instance.
- The generated namespace is highly repetitive. Instance drift in `APG1-3`, `DME6-8`, `VPG6-8`, `DP_STREAM_ENC1-3`, or `DP_SYM32_ENC1-3` may not be caught by tests that only use the first available display or audio path.
- Chunk boundaries are artificial. This chunk starts after some `DP_DPHY_SYM320` shifts and ends before some `DP_SYM32_ENC3` masks, so full-field pairing must be checked across adjacent chunk documents.
- Status and clear fields are side-effect-sensitive. Confusing pending, done, clear, overflow, missed-transmission, conflict, or error bits can lead to stuck packet updates, stale metadata, CRC waits that never complete, interrupt-like storms, or missed diagnostics.
- Stream encoder clock and reset fields are sequencing-sensitive. Incorrect masks around clock enable/status, FIFO reset/done, or encoder reset/done can produce blank HPO DP streams, underflow, hangs during modeset, or resume-only failures.
- Packet scheduling fields affect protocol-visible data. Bad GSP, SDP, metadata, MPEG, ISRC, MSA, VBID, audio SDP, or line-number fields can corrupt infoframes, HDR metadata, audio transport, DSC/compressed stream signaling, or multi-stream packet timing.
- DPHY/SYM32 SAT and rate fields are link-critical. Wrong per-VC slot count, stream source, or rate `X/Y` masks can break multi-stream allocation, high-rate link training, or payload scheduling in ways that only appear under MST, high bandwidth, or multiple HPO streams.
- Memory-power fields are hardware-state dependent. Writes may be ignored or harmful if the block is clock-gated, power-gated, reset, or firmware-owned at the time of access.

## Test Signals

Useful validation combines generated-header consistency with DCN 3.5 hardware behavior:

- Build AMDGPU/DC with DCN 3.5/3.5.1 support enabled. Missing or renamed symbols should fail in token-pasted stream encoder, HPO DP stream encoder, APG, VPG, HPO link encoder, or DMUB register-table construction.
- Mechanically verify shift/mask pairing across the full file, not just this chunk. For this slice, expected boundary exceptions are `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0` masks at the start and `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` shifts at the end.
- Diff this generated range against AMD's authoritative DCN 3.5.0 register database and nearby generated headers such as `dcn_3_5_1_sh_mask.h` where HPO DP and packet block layouts are expected to match.
- Exercise HPO DisplayPort streams across all exposed HPO stream encoder instances, including stream enable/disable, modeset, link retrain, lane-count/link-rate changes, MST payload allocation, high-bandwidth modes, suspend/resume, and display hotplug.
- Validate packet behavior: generic packets, HDR/metadata packets, MPEG/ISRC payloads, MSA values, VBID/compressed-stream flags, GSP frame/immediate update bits, double-buffer pending behavior, and packet line-number scheduling.
- Validate audio paths through APG: DP audio stream ID selection, audio enable/HBR status, channel-count override, CRC capture and clear, FIFO overflow reporting, mute/unmute, and audio behavior across plug/unplug and format changes.
- Validate diagnostics: DPHY error status, SAT/rate update-pending transitions, CRC done/value/count fields, video CRC result/status fields, FIFO reset/done/status/error fields, and generic-packet conflict flags.
- Watch kernel logs and display diagnostics for HPO DP blanking, link-training failure, MST payload errors, audio dropouts, metadata corruption, CRC mismatches, stuck update-pending bits, FIFO errors, packet conflicts, and resume-only regressions.

## Cross-Chunk Notes

The previous chunk owns the start of the `DP_DPHY_SYM320_DP_DPHY_SYM32_CRC_CONFIG0` field definitions, including several shifts whose masks appear at the beginning of this chunk. The next chunk continues `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` masks and the rest of the `DP_SYM32_ENC3` stream encoder block. The final per-file document should merge adjacent chunks before making complete claims about all DCN 3.5.0 HPO DP stream encoder, DPHY/SYM32, VPG, APG, and DME instances.
