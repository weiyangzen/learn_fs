# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 5206-7703

## Scope

This chunk is a generated AMD DCN 3.1.6 register-offset header segment. It contains C preprocessor constants only: `reg...` register offsets and matching `reg..._BASE_IDX` segment selectors. There are no functions, structs, enums, or runtime branches in this range. Runtime behavior comes from other AMD display code that includes this header and expands the macros into MMIO register tables.

The range begins in the middle of the DPP1 color-management (`CM1`) block and then covers DPP1 top/perfmon, full DPP2 and DPP3 pixel-processing blocks, MPC/MPCC compositor blocks, MPCC output-gamma blocks, and the beginning of the MPC output CSC block.

## Purpose

The purpose is to bind symbolic DCN316 display-pipeline register names to hardware addresses. DCN display code uses these constants to populate per-IP register-table structs, then `REG_READ`, `REG_SET`, `REG_UPDATE`, and related helpers program display hardware without hard-coding numeric addresses in the functional code.

The `_BASE_IDX` value is as important as the offset value. In DCN316 resource setup, macros such as `SR`, `SRI`, and `SRII` compute an absolute register address as `BASE(reg..._BASE_IDX) + reg...`. For this chunk, DPP-side registers mostly use base segment index `2`, while MPC/MPCC-side registers use base segment index `3`.

## Register Blocks Covered

Visible block map in this chunk:

| Lines | Address block | Base address comment | Register coverage |
| --- | --- | --- | --- |
| 5206-5251 | Tail of DPP1 `CM1` color-management block | inherited from prior chunk | shaper RAMB region tail, secondary CM memory power, 3D LUT access/output offsets, CM debug index/data |
| 5253-5266 | `dce_dc_dpp1_dispdec_dpp_top_dispdec` | `0x5ac` | `DPP_TOP1` control, soft reset, CRC values/control, host read control |
| 5269-5288 | `dce_dc_dpp1_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` | `0x3e3c` | `DC_PERFMON12` counter control/state/value registers |
| 5291-5942 | DPP2 CNVC/CUR/DSCL/CM/DPP top/perfmon blocks | mostly `0xb58`, perfmon `0x43e8` | full DPP2 conversion, cursor, scaler, color-management, top, and perfmon offsets |
| 5983-6672 | DPP3 CNVC/CUR/DSCL/CM/DPP top/perfmon blocks | mostly `0x1104`, perfmon `0x4994` | full DPP3 conversion, cursor, scaler, color-management, top, and perfmon offsets |
| 6675-6800 | `dce_dc_mpc_mpcc0..3_dispdec` | `0x0`, `0x80`, `0x100`, `0x180` | four MPCC composition pipes, including top/bottom selection, OPP selection, alpha/gain/background, memory power, status |
| 6803-6872 | `dce_dc_mpc_mpc_cfg_dispdec` | `0x0` | global MPC clock/reset/CRC/perfmon/host-read/pending/vupdate-lock/DWB mux registers |
| 6875-6894 | `dce_dc_mpc_mpc_dcperfmon_dc_perfmon_dispdec` | `0x1901c` | `DC_PERFMON15` counter control/state/value registers |
| 6897-7614 | `dce_dc_mpc_mpcc_ogam0..3_dispdec` | `0x0`, `0x200`, `0x400`, `0x600` | four MPCC output-gamma blocks with OGAM LUT, RAM A/B region controls, and gamut-remap matrices |
| 7617-7703 | Start of `dce_dc_mpc_mpc_ocsc_dispdec` | `0x0` | MPC output mux/denorm for outputs 0-3 plus output CSC format and CSC matrix registers for outputs 0-1 |

The final `MPC_OUT` block is incomplete in this chunk: it stops at `regMPC_OUT1_CSC_C33_C34_B`. Output 2/3 CSC definitions should be expected in the next chunk.

## Important APIs, Types, And Macros

This file segment exports macros, not callable APIs. The important exported names are the register identifiers consumed by display resource tables:

- `regDPP_TOP1_*`, `regDPP_TOP2_*`, `regDPP_TOP3_*`: DPP top-level control, soft reset, CRC, and host-read registers.
- `regDC_PERFMON12_*`, `regDC_PERFMON13_*`, `regDC_PERFMON14_*`, `regDC_PERFMON15_*`: performance monitor counter controls and values for DPP1/DPP2/DPP3/MPC-related blocks.
- `regCNVC_CFG2_*`, `regCNVC_CFG3_*`: format conversion, floating-point bias/scale, color-key, alpha, pre-CSC, pre-degamma, and pre-realpha registers for DPP instances 2 and 3.
- `regCNVC_CUR2_*`, `regCNVC_CUR3_*`: cursor control/color/floating-point scale-bias registers.
- `regDSCL2_*`, `regDSCL3_*`: scaler coefficient RAM, mode, taps, scale ratios, filter init, overscan, recout, line-buffer, memory power, and output-buffer control registers.
- `regCM2_*`, `regCM3_*`: large color-management blocks, including post-CSC, gamut remap, degamma, regamma, blender gamma, HDR multiplier, shaper LUT/RAM, 3D LUT, memory power, and debug registers.
- `regMPCC0_*` through `regMPCC3_*`: four multi-plane composition cells.
- `regMPC_*`: global MPC clock/reset/CRC/perfmon/pending/update-lock/DWB and output mux/CSC registers.
- `regMPCC_OGAM0_*` through `regMPCC_OGAM3_*`: per-MPCC output gamma and gamut-remap register blocks.

Integration code observed in `display/dc/resource/dcn316/dcn316_resource.c` includes this header together with `dcn_3_1_6_sh_mask.h`. It defines `BASE`, `SR`, `SRI`, `SRII`, and related macros, then uses higher-level register-list macros such as `DPP_REG_LIST_DCN30(id)`, `MPC_REG_LIST_DCN3_0(inst)`, and `MPC_OUT_MUX_REG_LIST_DCN3_0(inst)` to initialize `dcn3_dpp_registers`, `dcn30_mpc_registers`, `dcn20_opp_registers`, and related tables.

`display/dmub/src/dmub_dcn316.c` also includes this offset header. DMUB uses the same `BASE(reg..._BASE_IDX) + reg...` pattern through `REG_OFFSET_EXP()` to fill `dmub_srv_dcn316_regs` for firmware-service register access.

## Control Flow

There is no executable control flow in this chunk. The effective control flow is compile-time macro expansion:

1. A DCN316 source file includes `dcn_3_1_6_offset.h`.
2. The source defines the DCN base-segment constants, for example `DCN_BASE__INST0_SEG2` and `DCN_BASE__INST0_SEG3`.
3. Register-list macros in functional headers expand symbolic names into struct initializers.
4. Each initializer combines `BASE_IDX` with the raw offset to produce an absolute register address.
5. Runtime display code uses the populated structs through common register helpers to read or write MMIO.

This separation lets most display logic share DCN generation code while swapping in ASIC-specific offset and field-mask headers.

## State And Persistence Behavior

The macros themselves hold no state and persist only as compile-time constants. The state they address is hardware state:

- DPP CNVC/DSCL/CM registers configure per-plane pixel conversion, cursor color interpretation, scaling, LUTs, CSC matrices, alpha handling, and memory-power state.
- DPP top and perfmon registers expose control/reset, CRC readback, host-read behavior, and performance counters.
- MPCC registers define composition routing: which DPP feeds the top/bottom of each MPCC, which OPP consumes the result, blending/gain/background controls, update-lock selection, memory power, and status.
- MPC global registers expose compositor clock/reset, CRC, pending status, vertical update lock sets for plane/config/cursor/address state, and DWB muxing.
- MPCC OGAM and MPC output CSC registers persist programmed output color transforms until changed, reset, or power-gated.

The persistence boundary is therefore the display hardware block, not any software object in this header. Incorrect constants can corrupt live hardware programming, but the header itself does not allocate memory or store runtime data.

## Dependencies

Direct dependencies are structural rather than included from this chunk:

- `dcn_3_1_6_sh_mask.h` supplies field masks and shifts for the same symbolic register names.
- DCN316 resource setup defines base segments used by `_BASE_IDX`.
- `reg_helper.h` and display register helper macros consume the resolved register addresses.
- DPP register-list definitions in `display/dc/dpp/dcn30/dcn30_dpp.h` reference many `CNVC`, `CUR`, `DSCL`, `CM`, and `DPP_TOP` names from this chunk.
- MPC register-list definitions in `display/dc/mpc/dcn30/dcn30_mpc.h` reference the `MPCC`, `MPC`, `MPCC_OGAM`, and `MPC_OUT` names from this chunk.
- DMUB DCN316 register setup consumes this same ASIC offset map for firmware service access.

The numeric constants are also implicitly coupled to AMD hardware register specifications and to sibling generated headers for other ASIC versions. Similar symbolic names appear in other DCN offset headers, but some numeric offsets differ by ASIC generation.

## Integration Points

Primary integration points:

- `display/dc/resource/dcn316/dcn316_resource.c`: builds DCN316 register tables for DPP, OPP, MPC, HUBP, HUBBUB, DCCG, AUX, DSC, DWB, and related display components. This chunk directly feeds the DPP and MPC portions visible in that file.
- `display/dc/dpp/dcn30/dcn30_dpp.c` and related DPP headers: functional code programs CM shaper regions, LUTs, CSC coefficients, scaler controls, and DPP top controls through register-table fields backed by this header.
- `display/dc/mpc/dcn10/dcn10_mpc.c`, `dcn20_mpc.c`, and `dcn30_mpc.c`: shared MPC code reads/writes MPCC routing, blending, mux, and status registers. For example, `MPCC_TOP_SEL` is used to attach/detach DPP inputs and to snapshot MPCC state.
- `display/dmub/src/dmub_dcn316.c`: exposes a DCN316-specific register map to DMUB service code.

The chunk is part of a larger single header, so adjacent chunks provide earlier DPP0/DPP1 definitions and later MPC output CSC continuation plus other display blocks. A final per-file report should merge these cross-chunk relationships.

## Risks And Edge Cases

- Generated-address drift: if any offset or `_BASE_IDX` is wrong, the driver will access the wrong MMIO register. Effects range from bad color/scaling to display hangs.
- Segment-index errors are high impact because the offset may look plausible but resolve into the wrong DCN base segment.
- DPP2/DPP3 blocks are repetitive but not interchangeable. Copy/paste or generator mistakes can silently route instance 2 operations to instance 3 addresses or vice versa.
- The chunk starts mid-`CM1` block. Any chunk-level analysis must avoid treating the visible CM1 subset as the full DPP1 color-management register set.
- The chunk ends mid-`MPC_OUT` block. Output 0 and 1 CSC definitions are visible here, but output 2 and 3 CSC definitions are outside this range.
- Color pipeline registers often require coordinated programming order and update locks. This header does not encode those sequencing rules; they live in DPP/MPC functional code.
- Performance monitor and CRC registers are readback/control surfaces. Wrong offsets can create misleading diagnostics even when normal display output appears functional.
- Many registers have paired mask/shift definitions in `dcn_3_1_6_sh_mask.h`; offset names must remain synchronized with those field definitions.

## Test Signals

Useful validation signals for this chunk:

- Build coverage: compile DCN316 display code that includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`; missing or misspelled macros should fail at compile time in resource table initializers.
- Register-table sanity: confirm `dcn316_resource.c` initializes DPP instances 0-3 and MPC/MPCC instances 0-3 without unresolved symbols from `DPP_REG_LIST_DCN30`, `MPC_REG_LIST_DCN3_0`, or `MPC_OUT_MUX_REG_LIST_DCN3_0`.
- Hardware smoke tests: exercise multi-plane composition, scaling, cursor, color management, output CSC, and display wake/reset paths on DCN316 hardware.
- Visual/color tests: verify degamma/regamma, shaper LUT, 3D LUT, gamut remap, HDR multiplier, and output CSC behavior with known test patterns.
- Diagnostic tests: read DPP/MPC CRC and perfmon counters to ensure the register map supports expected debug telemetry.
- Power-management tests: validate `*_MEM_PWR_CTRL` and `*_MEM_PWR_STATUS` behavior across blanking, idle, suspend/resume, and display reconfiguration.

## Chunk-Specific Notes For Merge

This report should be merged with adjacent chunks for the final per-file document. Important cross-chunk boundaries:

- The visible `CM1` definitions are only the tail of DPP1 color management.
- DPP2 and DPP3 appear complete in this range.
- MPCC0-3, MPC global config, DC_PERFMON15, and MPCC_OGAM0-3 appear complete in this range.
- `MPC_OUT` is partial and continues after line 7703.
