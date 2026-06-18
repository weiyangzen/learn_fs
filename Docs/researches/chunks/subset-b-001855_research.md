# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h

Chunk: `subset-b-001855`
Covered source range: lines 54013-56454 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h`

## Purpose

This chunk is a generated AMD DCN 3.1.4 register field mask header section. It contains C preprocessor constants for bit shifts and masks in display hardware registers; it is not executable logic and does not define functions, structs, or storage.

The covered range spans three major display areas:

- the tail of `DP_DPHY_SYM321` CRC fields for a 32-symbol DisplayPort DPHY block;
- HPO DisplayPort stream encoder instance 2 and instance 3 support blocks, including `DP_STREAM_ENC`, APG audio packet generator, DME metadata engine, VPG video packet generator, and `DP_SYM32_ENC` video/symbol encoder fields;
- MPC/MPCC composition fields for MPCC instances 0 through 3 and the beginning of MPCC output-gamma (`MPCC_OGAM0`) programming for LUT, gamut/gamma mode, RAM A region descriptors, and the start of RAM B region descriptors.

The chunk starts mid-register: `DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_CONFIG0` begins before line 54013, and this range starts at its field definitions. It ends mid-register-family: `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_14_15` is only partially present at line 56454, with the remaining mask fields and later MPCC OGAM registers in the next chunk. The final per-file merge should preserve both boundary splits.

## Important APIs, Types, And Macros

There are no runtime APIs, types, or functions in this range. The public interface is the generated macro contract:

- `<REGISTER>__<FIELD>__SHIFT` is the bit position used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` is the 32-bit field mask used by register helpers.
- Companion address macros live in `dcn_3_1_4_offset.h` as `reg<REGISTER>` or related base-index definitions; this header supplies only field layout.

Important macro families in this chunk include:

- `DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_*`: DPHY symbol CRC enable/reset, source selection, scheduler selection, start/end event selection, symbol count, CRC done/status, CRC value, and counted-symbol reporting.
- `DP_STREAM_ENC2_*` and `DP_STREAM_ENC3_*`: HPO DP stream encoder clock enable/source status, pixel stream mux, audio stream mux, clock-ramp FIFO enable/reset/status/error, FIFO calibration and override levels, and spare bits.
- `APG2_*` and `APG3_*`: audio packet generator reset, enable, DP audio stream ID, ASP channel-count override, debug audio generation, packet source selection, audio CRC control/result, audio/HBR/FIFO overflow status, output active state, memory power control, and spare bits.
- `DME7_*` and `DME8_*`: metadata engine requestor ID, enable, stream type, double-buffer pending/taken status, clear bits, double-buffer disable, missed-transmission latch/clear, and metadata-engine memory power state.
- `VPG7_*` and `VPG8_*`: generic packet data access and indexed byte payloads, frame/immediate generic stream packet update controls, generic status, memory power control, ISRC packet access/data, and MPEG infoframe payload fields.
- `DP_SYM32_ENC2_*` and `DP_SYM32_ENC3_*`: symbol encoder enable/reset/status, video FIFO enable/reset/watermark/error, MSA and pixel-format double buffering, pixel encoding and component depth, MSA lane bytes, hblank minimum symbol width, generic stream packet controls, SDP/audio/metadata packet controls, MSA/VBID/stream control, panel replay controls, video CRC control/result/status, memory power control, and spare bits.
- `MPCC0_*` through `MPCC3_*`: top and bottom MPC input selection, OPP ID, alpha/multiplied-alpha/pre-multiplied-alpha mode, background color, shared memory power, MPCC status, update-lock selection, stereo/mode fields, and gain controls for top/bottom and inside/outside alpha.
- `MPCC_OGAM0_*`: output gamma mode/select/PWL disable/current status, LUT index/data/indexing control, RAM A and RAM B start/end/slope/base/offset fields per B/G/R channel, and paired region descriptors for regions 0-33 in RAM A and regions 0-15 at the end of this chunk.

## Control Flow

This header chunk has no internal control flow. All behavior occurs in code that includes this header and uses the generated constants to build register tables.

The runtime pattern is:

1. DCN314 display resource or block code includes `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`.
2. Register-list macros select the instance addresses from the offset header.
3. Mask/shift list macros select the field constants from this header.
4. Block constructors store register addresses, shifts, and masks in per-block structures.
5. Display code later calls `REG_SET`, `REG_UPDATE`, `REG_GET`, or related helper macros, which use these masks and shifts to perform read/modify/write or polling operations.

Concrete integration points in this source tree:

- `display/dc/resource/dcn314/dcn314_resource.c` includes this header and builds DCN314 resource tables. Its HPO stream encoder tables use `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(__SHIFT/_MASK)`, so the `DP_STREAM_ENC*` and `DP_SYM32_ENC*` fields in this chunk become the HPO stream encoder's register-field metadata.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` defines the shared HPO DP stream encoder field list. It maps fields such as `DP_STREAM_ENC_CLOCK_EN`, `FIFO_RESET`, `FIFO_RESET_DONE`, `DP_SYM32_ENC_ENABLE`, pixel-format fields, MSA double-buffer fields, stream enable/status, SDP enable, audio enables, video CRC fields, and hblank symbol width to the generated masks and shifts.
- `display/dc/resource/dcn314/dcn314_resource.c` maps HPO stream encoders to sub-blocks: VPG register blocks 6-9 map to HPO DP instances 0-3, and APG register blocks 0-3 map to HPO DP instances 0-3. In this chunk, instance 2 uses `VPG7`/`APG2`, and instance 3 uses `VPG8`/`APG3`.
- `display/dc/mpc/dcn10/dcn10_mpc.h`, `display/dc/mpc/dcn30/dcn30_mpc.h`, `display/dc/mpc/dcn32/dcn32_mpc.h`, and related resource headers consume the MPCC fields. The `MPCC0..3` fields form per-MPCC composition metadata, while `MPCC_OGAM0` fields support MPCC output gamma and gamut-remap programming.
- `display/dc/resource/dcn32/dcn32_resource.h` shows the MPC register-list pattern used by later DCN resource code: MPCC registers and MPCC OGAM LUT/RAM A/RAM B region registers are collected through `SRII(..., MPCC_OGAM, inst)` entries and then paired with these generated mask/shift constants.
- `display/dmub/src/dmub_dcn314.c` includes the DCN314 offset and mask headers for DMUB service register definitions. This chunk is part of the same ASIC-specific register namespace available to DMUB-facing code, although the fields in this range are primarily display datapath and HPO/MPC fields.

## State And Persistence Behavior

The header itself is stateless. It performs no I/O, owns no memory, and has no persistence beyond compiled constants in driver objects.

The hardware fields described by these macros are persistent register state in display blocks until changed by driver writes, firmware writes, power gating, display block reset, ASIC reset, suspend/resume restore, or link/stream reprogramming. Important state categories include:

- HPO DP stream routing and clocks: `DP_STREAM_ENC_CLOCK_EN`, clock-on-source status bits, pixel/audio stream mux fields, and FIFO enable/reset/status fields.
- HPO video-symbol encoding: `DP_SYM32_ENC_ENABLE`, reset/done bits, FIFO enable/reset/error, pixel format, MSA lane data, VBID compressed-stream flag behavior, stream enable/status, panel replay markers, and video CRC status.
- Packet generation: APG audio packet enable/reset/CRC/status, VPG generic packet payload/index/update state, ISRC/MPEG packet data, SDP generic-stream controls, SDP audio controls, metadata packet enable, and DME double-buffer handoff/missed-transmission status.
- Memory power controls: APG, DME, VPG, DP SYM32 encoder, MPCC, and MPCC OGAM memory power force/disable/state/default-low-power fields.
- Composition pipeline state: MPCC top/bottom input selection, OPP routing, alpha/multiply/pre-multiply controls, stereo/mode controls, update-lock selection, background color, gain factors, and status.
- Output gamma state: MPCC OGAM mode, selected LUT RAM, LUT index/data programming state, RAM A/B per-channel start/end/base/slope/offset values, and region LUT offsets/segment counts.

Several fields are status or latch/clear style, for example APG audio FIFO overflow clear, DME double-buffer taken clear, metadata transmission missed clear, CRC done clear/status fields, FIFO reset done, and stream/FIFO status fields. The macros do not encode access type or ordering requirements; those are enforced by hardware documentation and by the existing register helper sequences in HPO, VPG/APG, stream encoder, and MPC code.

## Dependencies And Integration Points

Direct dependencies are minimal:

- the C preprocessor;
- the matching DCN 3.1.4 offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`;
- AMD display register helper conventions (`REG_SET`, `REG_UPDATE`, `REG_GET`, `FD`, `FN`, `SF`, `SE_SF`, `SRI`, `SRII`, and related macros) that assemble register addresses with masks and shifts.

Functional dependencies are the display blocks represented by the register names:

- DCN314 resource construction decides how many stream encoders, HPO stream encoders, HPO link encoders, MPCCs, and MPCC OGAM/LUT resources exist.
- HPO DP stream encoder code depends on these constants to program the stream encoder, symbol encoder, MSA, VBID, generic packet, audio packet, metadata packet, and CRC fields.
- APG/VPG/DME helper objects depend on the APG, VPG, and DME masks for audio packet, generic packet, metadata, and memory-power controls.
- MPC/MPCC code depends on the MPCC and MPCC OGAM fields for plane composition, blending, update locking, output gamma programming, and debug state capture.
- DC debug and diagnostic paths can read MPCC OGAM state; `dc.h` includes debug arrays for `mpcc_ogam_mode`, `mpcc_ogam_select`, and `mpcc_ogam_pwl_disable`, which correspond to fields in `MPCC_OGAM0_MPCC_OGAM_CONTROL`.

This chunk is also tightly coupled to generated ASIC naming. Instance numbering matters: `DP_STREAM_ENC2` pairs with `DP_SYM32_ENC2`, `APG2`, `DME7`, and `VPG7`; `DP_STREAM_ENC3` pairs with `DP_SYM32_ENC3`, `APG3`, `DME8`, and `VPG8`. Callers should not infer a simple one-to-one APG/DME/VPG numeric suffix from the HPO stream encoder suffix without checking the resource mapping.

## Risks And Edge Cases

The largest risk is silent field-layout drift. If a mask or shift is wrong, the driver still compiles, but read/modify/write helpers can program the wrong bits in display hardware. High-impact examples in this chunk include stream enable/reset, FIFO reset/status, packet enables, memory power state, MPCC source selection, MPCC alpha modes, and MPCC OGAM LUT/region programming.

Boundary splits are easy to mishandle during automated analysis. This chunk starts without the `//DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_CONFIG0` comment and without any preceding macros for that register. It ends after only the `__SHIFT` fields and first mask for `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_14_15`; its remaining mask fields and later RAM B regions are outside this chunk.

Instance mismatches are another risk. HPO DP stream encoder instance 2 uses APG2 but DME7/VPG7, and instance 3 uses APG3 but DME8/VPG8. Register table generation must preserve these mappings or HPO streams may send packets, metadata, audio, or video over the wrong sub-block.

Status and clear bits need access-type discipline. Fields such as APG FIFO overflow clear, DME double-buffer/missed-transmission clear, CRC done clear, reset done, and FIFO error/status fields are not ordinary persistent configuration values. Treating all fields as plain read/write fields can lose events, fail to clear latches, or race with hardware state changes.

MPCC OGAM programming spans many related registers. LUT mode/select, LUT index/data, RAM A/B channel start/end/slope/base/offset, and region descriptors need coherent update ordering. Partial writes or bank-selection mistakes can produce visible color errors, stale gamma curves, or debug readbacks that disagree with intended state.

Generated macro consumers often use compile-time field-list expansion. Renaming a macro, changing the generated suffix, or moving a field between address blocks will break table initialization for DCN314 resource code or, worse, compile if a same-named field from a different instance is accidentally selected.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing rather than unit-level:

- Build coverage for DCN314 display code with `dcn314_resource.c`, `irq_service_dcn314.c`, `dmub_dcn314.c`, HPO stream encoder code, APG/VPG/DME code, and MPC/MPCC code enabled. This catches missing or renamed generated macros.
- Static checks comparing `dcn_3_1_4_sh_mask.h` against the matching `dcn_3_1_4_offset.h` and against adjacent generated ASIC versions for expected field names and instance counts.
- HPO DP functional tests that enable HPO stream encoders 2 and 3, verify stream mux selection, reset/done sequencing, FIFO reset/enable, stream enable/status, MSA programming, VBID compressed-stream flags, and hblank symbol width.
- DP packet tests for VPG/APG/DME behavior: generic SDP insertion, metadata packet enable/double-buffer handoff, audio packet enable/mute/CRC, ISRC/MPEG infoframe writes, and APG/VPG memory power transitions.
- CRC diagnostics: symbol CRC and video CRC enable/reset/result/status paths should report stable values for known test patterns and clear/reset cleanly across stream disable/enable.
- MPC/MPCC composition tests with multiple planes: top/bottom selection, alpha and pre-multiplied-alpha modes, update-lock selection, background color, and gain programming should produce expected blending output.
- MPCC OGAM tests: program LUT RAM A/B, switch selected bank, verify PWL enable/disable, read back LUT index/data and region descriptors, and compare output color/gamma against expected ramp behavior.
- Suspend/resume and power-gating tests for APG, DME, VPG, DP SYM32, MPCC, and MPCC OGAM memory power state restoration.

## Notes For Final Merge

This chunk should be merged with adjacent chunks for the same header before producing a final per-file report. The previous chunk owns the beginning of the `DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_CONFIG0` block; the next chunk owns the rest of `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_14_15`, later RAM B region descriptors, and subsequent MPCC OGAM/gamut-remap fields. The final file-level report should describe the whole header as generated DCN314 register-field metadata, not as independent handwritten driver logic.
