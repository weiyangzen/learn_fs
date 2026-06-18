# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h lines 10396-12981

## Scope

This chunk is a generated DCN 3.1.4 register-offset header segment for AMDGPU display hardware. It contains only preprocessor constants: `reg...` names map logical display block registers to MMIO register offsets, and companion `..._BASE_IDX` constants select the register base index used by AMD's register access macros. There are no C functions, structs, or executable control-flow statements in the chunk; the behavior comes from how display code includes these constants into register tables.

The slice starts in the middle of the `dce_dc_dio_dp3_dispdec` register block at `regDP3_DP_DPHY_SYM2` and ends in the `dce_dc_hpo_dp_sym32_enc2_dispdec` block at `regDP_SYM32_ENC2_DP_SYM32_ENC_VID_MSA5`. It therefore covers the end of legacy DP3, legacy DIG4/DP4 stream output, DCIO/UNIPHY lanes, power sequencing, DSC/writeback support, HVM, and the first two full HPO DP stream/link encoder instances plus the beginning of HPO stream encoder 2.

## Purpose

The header provides the DCN314 address map consumed by display core resource construction. `dcn314_resource.c` includes `dcn/dcn_3_1_4_offset.h` alongside mask/shift headers and uses macros such as `SRI`, `SR`, and `SRII` to populate per-instance register structures. For this chunk, the main consumers are:

- legacy DIO stream encoder setup through `SE_DCN314_REG_LIST(id)` in `display/dc/dio/dcn314/dcn314_dio_stream_encoder.h`;
- VPG and AFMT/APG packet/audio helpers through `VPG_DCN3_REG_LIST`, `AFMT_DCN31_REG_LIST`, and `APG_DCN31_REG_LIST`;
- HPO DP stream encoders through `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` in `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`;
- HPO DP link encoders through `DCN3_1_HPO_DP_LINK_ENC_REG_LIST(id)` in `display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h`;
- DCN314 resource arrays such as `stream_enc_regs[]`, `vpg_regs[]`, `afmt_regs[]`, `apg_regs[]`, `hpo_dp_stream_enc_regs[]`, and `hpo_dp_link_enc_regs[]`.

## Register Groups In This Chunk

The chunk has these address-block regions:

- continuation of `dce_dc_dio_dp3_dispdec`: DP3 DPHY symbols, 8b/10b, PRBS/scrambler/CRC, fast training, secondary-data packet controls, audio M/N readback, MSE/SST/MST allocation timing, MSA timing/colorimetry, DSC, GSP8-GSP11, metadata transmission, ALPM, and AUX-less ALPM registers.
- `dce_dc_dio_dig4_vpg_vpg_dispdec` at base `0x164a0`: `VPG4_*` generic packet access/data/update/status, memory power, ISRC, and MPEG info registers.
- `dce_dc_dio_dig4_afmt_afmt_dispdec` at base `0x164cc`: `AFMT4_*` audio, VBI/infoframe, 60958 channel status, CRC, ramp, generic packet, and memory power registers.
- `dce_dc_dio_dig4_dme_dme_dispdec` at base `0x16524`: `DME4_DME_CONTROL` and `DME4_DME_MEMORY_CONTROL` metadata-engine controls.
- `dce_dc_dio_dig4_dispdec` at base `0x1000`: `DIG4_*` stream-encoder registers for HDMI packet generation, audio ACR, front-end control, FIFO, TMDS, clocks, CRC, stereo sync, and format conversion.
- `dce_dc_dio_dp4_dispdec` at base `0x1000`: `DP4_*` legacy DisplayPort link/video/secondary-data registers mirroring the DP3-style set for DIO instance 4.
- DCIO/DCIO chip and `UNIPHY1` through `UNIPHY4`: clock, power, PLL, training, DPCS, RDPCS, PHY control, test/debug, and data-swap/order registers for physical output lanes.
- `PWRSEQ0` and `PWRSEQ1`: backlight/LVTMA control, panel timing, GPIO, reference divider, reset, and debug/status registers.
- DSC0 through DSC3: DSC top, DSC CIF, DSCC encoder controls, PPS words, rate control, flatness, native 4:2:0/4:2:2, clock-gate, debug, and per-DSC perfmon registers.
- `WB0`: display writeback controls, scaling/tap/filter registers, writeback line/frame state, pixel format, interrupt/status, and writeback perfmon.
- `DCHVM`: HVM power control/status and debug.
- HPO stream encoder instances 0 and 1: `DP_STREAM_ENC*`, `APG*`, `DME5/6`, `VPG5/6`, `DP_SYM32_ENC0/1`, `DP_LINK_ENC0/1`, and `DP_DPHY_SYM320/321` blocks.
- HPO stream encoder instance 2 prefix: `DP_STREAM_ENC2`, `APG2`, `DME7`, `VPG7`, and `DP_SYM32_ENC2` through `VID_MSA5`.

All defines in this range use `_BASE_IDX 2`, except this chunk begins after earlier header regions that can use other base indices. That matters because the same logical register name may exist across ASIC headers with different base index or offset values.

## Important APIs, Types, And Macro Contracts

There are no local API functions, but the constants are part of a macro ABI used by display code:

- `reg<block><instance>_<register>`: symbolic MMIO offset. Examples in this chunk include `regDP3_DP_SEC_CNTL`, `regDIG4_HDMI_CONTROL`, `regVPG4_VPG_GENERIC_PACKET_DATA`, `regDP_STREAM_ENC1_DP_STREAM_ENC_CLOCK_CONTROL`, and `regDP_DPHY_SYM321_DP_DPHY_SYM32_TP_CONFIG`.
- `reg<...>_BASE_IDX`: register base selector consumed with the offset by low-level AMDGPU register macros.
- `SRI(name, block, id)`: used by resource macros to expand to instance-specific `reg<block><id>_<name>` plus base-index symbols.
- `SR(name)` and `SRII(name, block, id)`: related macros used for non-instance and double-indexed register arrays.
- `struct dcn10_stream_enc_registers`, `struct dcn30_vpg_registers`, `struct dcn31_afmt_registers`, `struct dcn31_apg_registers`, `struct dcn31_hpo_dp_stream_encoder_registers`, and `struct dcn31_hpo_dp_link_encoder_registers`: resource-side containers populated from these constants.

The chunk's legacy DIO symbols map to fields used by `SE_DCN314_REG_LIST(id)`, including HDMI controls, DP MSA, DP secondary-data packet controls, metadata transmission, DME control, FIFO, and DIG front-end control. The HPO symbols map to fields used by `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` and `DCN3_1_HPO_DP_LINK_ENC_REG_LIST(id)`, including stream clock/input/audio controls, SYM32 video MSA/format/FIFO/SDP/audio/CRC controls, link clock controls, DPHY status, test-pattern, PRBS seed, SAT and VC rate registers.

## Control Flow And Runtime Use

This header has compile-time substitution only. Runtime flow is indirect:

1. DCN314 resource construction includes this offset header and the matching shift/mask headers.
2. Resource macros instantiate static register arrays. For example, `stream_enc_regs[]` uses `SE_DCN314_REG_LIST(id)` for legacy stream encoders 0-4; `hpo_dp_stream_enc_regs[]` uses `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` for HPO stream encoders 0-3; `hpo_dp_link_enc_regs[]` uses `DCN3_1_HPO_DP_LINK_ENC_REG_LIST(id)` for HPO link encoders 0-1.
3. Construct functions attach the selected per-instance register table to hardware objects such as stream encoders, VPG/APG/AFMT helpers, or HPO link encoders.
4. Operational code uses `REG_READ`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and related macros against logical field names. Those macros dereference the pre-populated register offset and apply the paired mask/shift definitions.

The practical control flow covered by this chunk includes HDMI setup, DP secondary-data packet enablement, DP audio timestamp/M/N programming, DSC stream setup, VPG generic packet updates, APG audio packet generator enable/disable, HPO stream enable/reset/status polling, HPO DPHY training/test-pattern programming, and HPO MST/SST slot allocation updates.

## State And Persistence Behavior

The constants themselves have no mutable state and persist only as compiled-in register addresses. They define access points for hardware state held in display registers:

- DP/DIG stream state: pixel format, MSA timing, video M/N, VBID, stream enable/status, FIFO reset/enable, HDMI deep-color/scrambling/packet generation, audio ACR, and secondary-data packet enable bits.
- Packet metadata state: VPG/AFMT/APG generic packet RAM/data windows, frame-update and immediate-update latches, conflict/status bits, ISRC/MPEG/audio info state, and metadata-engine controls.
- Link/PHY state: UNIPHY clock/power/training controls, RDPCS/DPCS state, HPO link clock enable, DPHY reset/enable/status, lane count, mode, PRBS/test-pattern seeds, symbol override, CRC counters, SAT allocation, and VC rate updates.
- Panel and compression state: PWRSEQ backlight/panel timing/reset and DSC PPS/rate/flatness/clock-gate/debug/perfmon registers.
- Writeback state: WB enable/path, scaling filter/taps, line/frame counters, status and perfmon state.

Because these offsets address hardware registers, incorrect values can persist until the display engine is reprogrammed, reset, power-cycled, or overwritten by later driver operations. The generated header is not responsible for saving/restoring state; state ownership is in the display resource and hardware-sequencing layers.

## Dependencies And Integration Points

Direct dependencies are generated companion headers for the same ASIC family, especially `dcn_3_1_4_sh_mask.h`, and the core register-access macros used throughout AMD display code. The offset names must match field-definition prefixes in mask/shift headers and the register list macros in DC source headers.

Important integration points:

- `display/dc/resource/dcn314/dcn314_resource.c`: builds the static register tables for stream encoders, link encoders, VPG, AFMT, APG, HPO stream encoders, and HPO link encoders.
- `display/dc/dio/dcn314/dcn314_dio_stream_encoder.h` and `.c`: consume `DIG4_*`, `DP4_*`, DME, HDMI, and DP SEC/MSA offsets via `SE_DCN314_REG_LIST` and perform HDMI/DP stream programming.
- `display/dc/dio/dcn31/dcn31_dio_link_encoder.c` and shared DCN link-encoder code: use `DP_LINK_CNTL`, UNIPHY, DPCS, and RDPCS registers for link training and PHY control.
- `display/dc/dcn30/dcn30_vpg.h`, `display/dc/dcn31/dcn31_vpg.h`, and VPG implementation: use `VPG4`, `VPG5`, `VPG6`, and `VPG7` offsets for generic info-packet programming.
- `display/dc/dcn31/dcn31_apg.h`: consumes `APG0-APG2` offsets for HPO audio packet generator reset, enable, stream ID, debug audio channels, and memory-power controls.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` and HPO stream encoder implementation: use `DP_STREAM_ENC*` and `DP_SYM32_ENC*` offsets for UHBR/HPO stream setup.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` and implementation: use `DP_LINK_ENC*` and `DP_DPHY_SYM32*` offsets for HPO link setup, training patterns, SAT/VC rate programming, and status polling.
- `display/dmub/src/dmub_dcn314.c` and `display/dc/irq/dcn314/irq_service_dcn314.c`: include the same offset header for DMUB and interrupt register access, though this exact slice is mostly display-output block offsets.

## Risks And Edge Cases

- Offset/header mismatch: These generated constants must be paired with the DCN314 mask/shift header. Reusing a DCN315/DCN320/DCN36 offset header with DCN314 resource tables can silently point register writes at the wrong MMIO locations.
- Instance mapping mistakes: The chunk includes both legacy DIO instances (`DIG4`, `DP4`, `VPG4`, `AFMT4`, `DME4`) and HPO instances (`DP_STREAM_ENC0-2`, `VPG5-7`, `DME5-7`). Resource comments in `dcn314_resource.c` note that VPG/AFMT/DME blocks are mapped to DIO block instances; off-by-one mapping errors can send info packets or metadata to the wrong stream.
- Partial chunk boundary: The chunk starts after the beginning of `DP3` and ends before completing `DP_SYM32_ENC2`; merge/reconciliation must combine adjacent chunks to get the full per-file register map.
- Duplicate logical registers: Some register names appear twice in macro lists, such as metadata transmission and HDMI metadata packet control in DCN314 stream encoder lists. Generated offsets must remain stable so duplicate logical consumers resolve consistently.
- Hardware side effects: Registers in this chunk include reset, enable, training, memory-power, CRC, status-clear, and update-pending controls. Bad offsets can cause visible display loss, audio loss, link training failure, panel backlight issues, metadata packet corruption, DSC corruption, or writes into reserved hardware.
- Base-index sensitivity: This slice consistently uses base index `2`, but other ASIC generations can have identical logical names with different offsets or base indices. Tests should catch both offset and base-index regressions.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware smoke tests rather than unit tests:

- Build coverage: compile AMDGPU display code for DCN314 with this header included, ensuring all `SRI`/`SE_SF` references resolve and register structures initialize cleanly.
- Register-table sanity: inspect generated/compiled `dcn314_resource.c` register arrays for expected offsets, especially `DIG4`, `DP4`, `VPG4`, `AFMT4`, `DME4`, `DP_STREAM_ENC0-2`, `DP_LINK_ENC0-1`, and `DP_DPHY_SYM320/321`.
- Display bring-up: attach HDMI and DP sinks on DCN314 hardware and verify stream enable, link training completion, correct pixel format/deep color, no blanking artifacts, and stable hotplug/retrain behavior.
- Packet/audio behavior: verify HDMI audio, DP audio, infoframes, HDR/metadata packets, ISRC/MPEG packets, and VPG/APG generic packet update paths; failures often indicate bad AFMT/VPG/APG/DME/DIG offsets.
- MST/HPO behavior: test DisplayPort MST and HPO-capable links, checking SAT/VC allocation updates, stream-to-link mapping, UHBR/HBR training patterns, and HPO stream/link enable/reset status.
- DSC and writeback: enable DSC output paths and display writeback where supported, watching for corruption, underflow, CRC mismatch, or perfmon/status anomalies.
- Power sequencing: panel/backlight and power-gating tests should watch PWRSEQ, DSC clock-gate, APG/VPG memory-power, and UNIPHY power-state side effects.

## Research Notes

This is a generated hardware contract rather than hand-written logic. The substantive behavior is in consumers that turn these offset macros into typed register tables and then into MMIO operations. The most important maintenance invariant is name alignment across three layers: offset macro names in this file, mask/shift field names in the paired generated headers, and register-list entries in DC resource/helper headers.
