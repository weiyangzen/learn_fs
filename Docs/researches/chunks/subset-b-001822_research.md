# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 49470-51864

## Scope

This chunk covers a generated DCN 3.1.2 register shift/mask header slice for high-performance DisplayPort output (HPO DP) stream encoder hardware. It contains only preprocessor constants and generated register grouping comments; there are no functions, structs, enums, global storage objects, or executable statements in this slice.

The range is 2,395 lines with 2,139 `#define` entries: 1,072 `__SHIFT` definitions and 1,067 `_MASK` definitions. The count is intentionally uneven because the chunk starts in the middle of `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13` and ends in the middle of `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL8`. It includes 15 complete address-block comments for HPO stream/APG/DME/VPG/SYM32 encoder instances 1 through 3, plus the tail of the previous SYM32 encoder 0 block.

## Purpose

The purpose of this header region is to provide symbolic bit positions and masks for DCN 3.1.2 HPO DP stream encoding, audio packet generation, DisplayPort stream metadata packet generation, and 32-symbol encoder state. AMDGPU display code includes this file together with the matching DCN 3.1.2 offset header so register helper macros can pack, update, and extract MMIO fields without embedding raw bit offsets.

This is a hardware-interface contract rather than algorithmic code. Its important behavior is the exact macro namespace and numeric bit layout expected by DCN31 register tables and register-access helpers.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for the same field.
- Address-block comments, such as `dce_dc_hpo_dp_stream_enc1_dispdec`, group register fields by hardware block.
- Register comments, such as `//DP_SYM32_ENC1_DP_SYM32_ENC_SDP_GSP_CONTROL0`, group the shift/mask pairs for a logical register.

The chunk covers these block families:

- Tail of `DP_SYM32_ENC0`: remaining GSP control 13 fields, full GSP control 14 fields, SDP stream/audio/metadata controls, MSA/VBID/video stream controls, panel replay control, CRC controls/results/status, memory power control, and spare.
- `DP_STREAM_ENC1`, `DP_STREAM_ENC2`, and `DP_STREAM_ENC3`: clock control, pixel/audio input mux control, clock-ramp adjuster FIFO controls, and spare fields.
- `APG1`, `APG2`, and `APG3`: audio packet generator reset/enable, stream ID selection, packet control, audio CRC control/result/status, memory power, and spare fields.
- `DME7`, `DME8`, and `DME9`: data mux engine control, metadata HSI/stereo flags, source select, reset/enable status, reset select, and memory power fields.
- `VPG7`, `VPG8`, and `VPG9`: generic packet indexed data access, GSP frame/immediate update bits for generic packets 0-14, generic conflict status/clear, memory power, ISRC access/data, and MPEG info packet words.
- `DP_SYM32_ENC1` and `DP_SYM32_ENC2`: complete symbol encoder blocks covering reset/enable, pixel-to-symbol FIFO, MSA and pixel-format double buffering, pixel format, MSA data registers, HBLANK minimum symbol width, GSP controls 0-14, SDP stream/audio/metadata controls, MSA/VBID/video stream controls, panel replay, CRC, memory power, and spare fields.
- Beginning of `DP_SYM32_ENC3`: complete control, FIFO, MSA/pixel-format, video MSA data, HBLANK, and GSP controls 0-7, followed by only the shift fields for GSP control 8 at the chunk boundary.

Important repeated field families include:

- Clock and mux controls: stream encoder clock enable/status across `DISPCLK`, `SOCCLK`, `DPSTREAMCLK`, and `SYMCLK32`, plus pixel/audio stream source select fields.
- FIFO and reset controls: FIFO enable/reset/read-start-level/read-clock-source/reset-done/video-active/error fields, plus symbol-encoder and pixel-to-symbol FIFO reset/done/enable fields.
- Video formatting controls: pixel encoding type, uncompressed pixel encoding, component depth, dynamic range, YCbCr coefficient selection, MSA lane data, MSA double buffering, pixel-format double buffering, and HBLANK minimum symbol width.
- Generic secondary-data packet controls: GSP continuous video/idle transmission, one-shot trigger, one-shot position, double buffering, payload size, start-of-frame reference, deadline-missed/pending status, double-buffer pending status, and transmission line number.
- SDP/audio/metadata controls: SDP stream enable, GSP priority, CRC16 enable, audio sample/time/info/change/ISRC packet enablement, audio mute/status, audio sample concatenation limits, metadata packet enable, double buffering, SOF reference, pending status, and line number.
- Video status and validation fields: video stream enable/deferred disable/status, VBID compressed stream flag timing, panel replay tunneling optimization, video CRC enable/continuous mode/results/valid bit.
- Packet generators: VPG generic packet byte lanes, GSP frame and immediate update bits, ISRC continuation/index/data, MPEG info packet fields, and VPG conflict status.
- Power fields: memory low-power default, force, disable, and state for SYM32/VPG/APG/DME-related blocks.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token resolution:

1. DCN31 code includes `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h`.
2. Resource construction macros build per-instance register tables, for example `hpo_dp_stream_encoder_reg_list(1)` resolves `DP_STREAM_ENC1`, `DP_SYM32_ENC1`, APG, and VPG register offsets.
3. Shift/mask table initializers such as `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(__SHIFT)` and `_MASK` use the generated field macros from this header.
4. Runtime register helpers such as `REG_UPDATE`, `REG_GET`, `REG_SET`, `FD_MASK`, and `FD_SHIFT` apply the resolved constants to MMIO reads/writes.

The declaration order mirrors hardware instance order. The chunk finishes encoder 0, then lists stream/APG/DME/VPG/SYM32 blocks for HPO stream encoder 1, repeats the same pattern for encoder 2, and starts the same pattern for encoder 3.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes bit locations for state that lives in DCN 3.1.2 display hardware registers.

Writable fields can program HPO DP clock enablement, mux source selection, FIFO/reset sequencing, pixel format, MSA transmission timing, generic SDP/GSP transmission timing, audio packet behavior, metadata packet delivery, video stream enablement, panel replay optimization, CRC capture, and memory power policy. Read-only or hardware-updated fields can report reset completion, FIFO/video activity/error state, pending or deadline-missed packet transmission, audio mute status, CRC results/validity, VPG generic-packet conflicts, and memory power state.

Persistence is hardware-defined. Programmed control fields generally persist until driver reprogramming, display block reset, suspend/resume restore, or ASIC reset. Status fields may change with stream enable/disable, packet transmission, hotplug modes, clock/power transitions, or CRC capture state. This generated header does not encode access type, reset values, write-one-to-clear semantics, or ordering requirements.

## Dependencies And Integration Points

The matching offset contract is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`. The same 15 HPO DP address blocks for stream encoder instances 1-3 appear there with `reg...` offsets and `_BASE_IDX` values. The offset and shift/mask headers must be generated from the same register database; otherwise register table construction can compile with missing symbols or, worse, program the wrong field bits.

Important source-tree integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` builds four HPO DP stream encoder register tables, initializes `hpo_dp_se_shift` and `hpo_dp_se_mask`, and reports `num_hpo_dp_stream_encoder = 4`.
- The same resource code maps HPO stream instances to VPG/APG blocks: `VPG[6] -> HPO_DP[0]`, `VPG[7] -> HPO_DP[1]`, `VPG[8] -> HPO_DP[2]`, `VPG[9] -> HPO_DP[3]`; `APG[0-3] -> HPO_DP[0-3]`. This chunk covers the generated VPG7-9 and APG1-3 field definitions for instances 1-3.
- `drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` defines the DCN31 HPO stream encoder register and field lists that consume the generated `DP_STREAM_ENC*` and `DP_SYM32_ENC*` shift/mask symbols.
- `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h` consumes APG field symbols through `DCN31_APG_MASK_SH_LIST`; `dcn31_apg.c` uses those fields for reset, enable, audio stream ID, debug channel enablement, and memory power programming.
- `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` consumes VPG field symbols through `DCN31_VPG_MASK_SH_LIST`; the generated VPG7-9 macros in this chunk support HPO instances 1-3 even though field tables are written against instance-0 names and paired with per-instance register offsets.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c` and `drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c` directly include `dcn_3_1_2_sh_mask.h` along with the matching offset header for DMUB and IRQ register infrastructure.

The DME7-9 macros in this chunk are part of the generated HPO stream encoder register map, but direct consumers are less visible in the nearby DCN31 code than APG/VPG/SYM32. Whole-file or cross-file analysis should reconcile whether DME programming is unused, abstracted through other generated tables, or reserved for firmware/hardware flows.

## Risks And Edge Cases

- The chunk boundaries split register definitions. The start lacks the earlier `DP_SYM32_ENC0...GSP_CONTROL13` shift and some mask fields, while the end has only `DP_SYM32_ENC3...GSP_CONTROL8` shift fields and no corresponding masks. The merge lane must combine adjacent chunks before making whole-file completeness claims.
- The blocks are highly repetitive across instances 1-3. A generator drift or copy error that changes only one instance can be hard to spot in review because most lines differ only by instance number.
- The runtime HPO stream encoder field tables use instance-0 field names for common shift/mask values while pairing them with per-instance register offsets. That pattern assumes equivalent field layout across instances; per-instance divergence would require different shift/mask tables.
- Several fields are status or pending bits next to writable control bits, such as reset done, FIFO error, packet transmission pending, double-buffer pending, CRC valid, and memory power state. This header does not prevent accidental writes to status bits.
- Packet timing fields such as `GSP_TRANSMISSION_LINE_NUMBER`, `METADATA_PACKET_TRANSMISSION_LINE_NUMBER`, `VBID_6_COMPRESSEDSTREAM_FLAG_LINE_NUMBER`, and `MSA_TRANSMISSION_LINE_NUMBER` can affect precisely when data is emitted relative to a frame. Wrong shifts or masks may produce intermittent display, audio, metadata, or compliance failures.
- Full-width masks such as VPG generic packet data, ISRC data, MPEG info fields, MSA lane registers, and spare registers use `0xFFFFFFFFL`; consumers should use unsigned 32-bit register values and avoid signed-width assumptions.
- Packed byte and lane fields invite off-by-one errors. VPG generic packet data packs bytes 0-3 into one word, and SYM32 MSA fields carry lane data across full 32-bit registers.
- Memory power controls are present in SYM32, VPG, APG, and DME families. Incorrect force/disable/default state programming can cause reads or writes to appear flaky if the block is clocked or powered down.
- Cross-generation reuse is risky. DCN 3.1.2 names resemble nearby DCN 3.1/3.2 generated headers, but offsets and field layouts must be paired with the exact ASIC generation.

## Test Signals

Useful validation signals are mostly build-time, generated-header consistency, and hardware integration checks:

- Build AMDGPU display code for a DCN31/DCN 3.1.2 configuration to catch missing generated macros in `SRI`, `SE_SF`, `FD_MASK`, `FD_SHIFT`, `REG_GET`, and `REG_UPDATE` expansions.
- Preprocess `dcn31_resource.c`, `dcn31_hpo_dp_stream_encoder.c`, `dcn31_apg.c`, and `dcn31_vpg.c` to confirm the intended per-instance register offsets combine with the common shift/mask field tables.
- Compare this slice against `dcn_3_1_2_offset.h` and verify every register named here has a matching `reg...` offset and base index, especially across `DP_STREAM_ENC1-3`, `APG1-3`, `DME7-9`, `VPG7-9`, and `DP_SYM32_ENC1-3`.
- Validate generated field values against the authoritative AMD register database for DCN 3.1.2, with special attention to high-bit status fields, full-width masks, packet line-number fields, memory-power fields, and repeated GSP control blocks.
- Exercise HPO DP stream creation and destruction on hardware, verifying that all four HPO stream encoder instances can be allocated, mapped to the expected APG/VPG blocks, enabled, disabled, and reset.
- Run DisplayPort 128b/132b or HPO-capable link tests with video stream enable/disable, pixel format changes, MSA programming, metadata packet transmission, panel replay modes, and CRC capture.
- Exercise audio paths through APG programming, checking reset completion, stream ID programming, audio packet generation, mute behavior, audio CRC result/status, and suspend/resume restore.
- Stress generic packet updates through VPG frame-update and immediate-update paths, including conflict status/clear behavior and ISRC/MPEG packet programming.
- Test power-management transitions while repeatedly enabling/disabling streams to catch stale memory-power force/disable settings or missing reinitialization after reset.

## Open Cross-Chunk Questions

- The previous chunk is needed to present `DP_SYM32_ENC0` GSP control 13 as a complete register group.
- The next chunk is needed to complete `DP_SYM32_ENC3` GSP control 8 and the rest of SYM32 encoder 3.
- Whole-file analysis should reconcile DME7-9 generated fields with the actual DCN31 runtime programming path, since APG/VPG/SYM32 consumers are explicit but DME usage is not obvious from the local HPO stream encoder construction path.
- Whole-file analysis should verify that the instance-0 shift/mask table assumption used by DCN31 HPO code remains valid for all generated instances covered here.
