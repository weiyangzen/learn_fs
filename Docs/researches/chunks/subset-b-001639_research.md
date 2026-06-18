# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h lines 2585-5134

## Scope

This chunk is part of the generated AMD DCN 2.0.1 ASIC register offset header. It covers lines 2585-5134 of `dcn_2_0_1_offset.h`, beginning inside the tail of the DPP2 scaler block and ending at the first DIO I2C transaction registers. The slice is constants-only: it exports `#define` macros for memory-mapped display register offsets plus companion `_BASE_IDX` macros, with no C functions, structs, enums, or local runtime control flow.

The chunk contains display pipeline front-end, composition, output, timing, and DDC/I2C register address coverage for DCN 2.0.1. Most macros use the `mm<block>_<register>` naming convention, while each matching `mm..._BASE_IDX` macro selects the register aperture segment used by the display register helper layer.

## Purpose

The purpose of this chunk is to bind symbolic DCN 2.0.1 display register names to exact MMIO offsets. AMDGPU display code uses these offsets, together with the matching `dcn_2_0_1_sh_mask.h` field definitions, to build register tables and to perform typed register reads, writes, updates, polling, and interrupt acknowledgement without scattering literal offsets through functional code.

The visible hardware domains are:

- The tail of DPP2 DSCL register coverage for line-buffer format, line-buffer/scaler/OBUF memory power, and vertical counter state.
- DPP2 color management (`CM2`) registers for input CSC, gamut remap, bias, degamma/blend gamma/output gamma RAM A/B programming, LUT access, legacy palette controls, memory power, and debug data.
- DPP3 top, converter/config, cursor, scaler, and color-management blocks (`DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, `CM3`) with the same front-end display processing themes for pipe 3.
- MPC/MPCC registers for five MPCC instances, global MPC control, output muxing, vupdate-lock routing, denormalization clamps, per-MPCC output gamma, and output CSC matrices.
- OPP/FMT/DPG/OPPBUF/pipe CRC register copies for output pipes 0 and 1, including output formatting, dithering, clamps, 4:2:0/4:2:2 handling, display pattern generation, 3D parameters, pipe enable/control, and CRC capture.
- OPTC/ODM and OTG registers for two timing generators, including horizontal/vertical totals, blanking/sync windows, stereo, snapshots, interrupts, CRC windows, static screen, global sync lock, master update locking, DRR, and DSC start position.
- Miscellaneous display output selection and clock controls (`DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`).
- DIO DDC/I2C controller offsets for arbitration, interrupt control, software/hardware status, DDC1/DDC2 speed/setup, and transaction programming.

## Important API Surface

The exported API is preprocessor register metadata. Each usable register normally appears as a pair:

- `mm<register>`: the register offset inside the selected DCN register address space.
- `mm<register>_BASE_IDX`: the base segment selector consumed by `BASE(...)`, `SRI(...)`, `REG(...)`, and related helper macros.

Representative examples from this chunk include:

- `mmCM2_CM_DGAM_LUT_INDEX`, `mmCM2_CM_DGAM_LUT_DATA`, and `mmCM2_CM_OGAM_LUT_DATA` for pipe 2 DPP transfer-function programming.
- `mmCNVC_CFG3_CNVC_SURFACE_PIXEL_FORMAT`, `mmCNVC_CUR3_CURSOR0_CONTROL`, and `mmDSCL3_SCL_HORZ_FILTER_SCALE_RATIO` for pipe 3 pixel conversion, cursor, and scaling setup.
- `mmMPCC0_MPCC_TOP_SEL` through `mmMPCC4_MPCC_STATUS` for repeated MPCC instance routing, blending, update-lock, power, stall, and status control.
- `mmMPC_CLOCK_CONTROL`, `mmMPC_SOFT_RESET`, `mmMPC_OUT0_MUX`, and `mmMPC_OUT1_DENORM_CONTROL` for global MPC behavior and output routing.
- `mmMPCC_OGAM0_MPCC_OGAM_MODE` through `mmMPCC_OGAM4_MPCC_OGAM_RAMB_REGION_32_33` for per-MPCC output-gamma LUT programming.
- `mmMPC_OUT_CSC_COEF_FORMAT`, `mmMPC_OUT0_CSC_MODE`, and `mmMPC_OUT1_CSC_C33_C34_B` for output color-space conversion.
- `mmFMT0_FMT_BIT_DEPTH_CONTROL`, `mmFMT1_FMT_MAP420_MEMORY_CONTROL`, `mmDPG0_DPG_CONTROL`, and `mmOPP_PIPE_CRC1_OPP_PIPE_CRC_RESULT2` for output formatting, pattern generation, and CRC readback.
- `mmODM0_OPTC_INPUT_GLOBAL_CONTROL` and `mmODM1_OPTC_MEMORY_CONFIG` for output data-merger input control.
- `mmOTG0_OTG_H_TOTAL`, `mmOTG0_OTG_VERTICAL_INTERRUPT0_CONTROL`, `mmOTG1_OTG_MASTER_UPDATE_LOCK`, and `mmOTG1_OTG_DRR_CONTROL` for timing generator programming and synchronization.
- `mmDC_I2C_CONTROL`, `mmDC_I2C_DDC1_SPEED`, and `mmDC_I2C_TRANSACTION1` for display DDC/I2C transactions.

The block inventory in this slice is:

- DPP/CM/scaler: DPP2 DSCL tail, `CM2`, `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, `CM3`.
- MPC: `MPCC0`-`MPCC4`, `MPC`, `MPCC_OGAM0`-`MPCC_OGAM4`, `MPC_OUT_CSC`.
- OPP: `FMT0`, `DPG0`, `OPPBUF0`, `OPP_PIPE0`, `OPP_PIPE_CRC0`, and the same pipe-1 families.
- OPTC: `ODM0`, `ODM1`, `OTG0`, `OTG1`, OPTC misc source/clock controls.
- DIO: common DC I2C controller and DDC1/DDC2 setup/status registers.

## Control Flow

There is no executable control flow in this header chunk. Runtime flow is external and macro-driven:

- DCN 2.0.1 resource construction includes this header and expands register list macros into per-block register tables. For example, DPP, MPC, OPP, OPTC, clock, and IRQ code use symbolic names that paste an instance id into `mm...` and `mm..._BASE_IDX` identifiers.
- Register helper macros combine `BASE(mm..._BASE_IDX)` with `mm...` to produce the final MMIO address. The `SRI(reg_name, block, id)` pattern in the DCN 2.0.1 IRQ service demonstrates this for instance-addressed interrupt registers.
- Functional display code then uses `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, polling helpers, and table initializers with the generated offset and mask/shift headers.
- Hardware sequencing rules are enforced by the consumer code and by DCN hardware, not by this file. The header only supplies the addresses needed to execute sequences such as scaler programming, color LUT loading, MPCC tree updates, OPP enablement, OTG locking, vblank/vline interrupt programming, and DDC transactions.

The implicit ordering contract is significant. Callers must program related register groups in safe order: update locks before multi-register changes, LUT index/data windows in the correct sequence, power controls before depending on memory-backed blocks, OTG timing before master enable, interrupt clears with the right status semantics, and I2C transaction registers while the controller is idle/arbitrated.

## State and Persistence

The file itself has no software state. The constants point to hardware state that persists while the display IP block is powered and until reprogrammed or reset:

- DPP CM, DSCL, CNVC, and cursor registers hold per-pipe conversion, scaling, cursor, gamma, and color-management state.
- MPC and MPCC registers hold compositor topology, OPP routing, blending gains, background color, stall state, vupdate-lock routing, output muxing, and memory-power status.
- MPCC OGAM and DPP CM gamma registers expose indexed LUT/RAM programming windows; index/data/control writes mutate hardware LUT state rather than ordinary software memory.
- OPP/FMT/DPG/CRC registers hold output formatting, bit depth, dither seeds, clamp limits, test pattern, 3D, pipe-control, and CRC capture state.
- OTG/ODM registers hold active timing, blank/sync positions, trigger/manual force state, stereo controls, frame counters, snapshot state, vertical interrupt positions, CRC windows, global sync lock, master update lock, DRR, and DSC start position.
- DIO I2C registers hold controller arbitration, setup/speed, status, interrupt, and transaction descriptors for DDC access.

Bad offsets can therefore persist as hardware misconfiguration: visible corruption, wrong color transforms, scaler artifacts, failed composition, stuck update locks, lost vblank/vline interrupts, broken CRC diagnostics, display timing failure, missed DDC/EDID reads, or power-management dead states until a modeset, block reset, or GPU reset repairs the affected registers.

## Dependencies and Integration Points

This header is tightly coupled to:

- `dcn_2_0_1_sh_mask.h`, which defines the field masks and shifts for the same register names.
- DCN 2.0.1 display files that include it directly: `display/dc/resource/dcn201/dcn201_resource.c`, `display/dc/irq/dcn201/irq_service_dcn201.c`, and `display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c`.
- Register list and helper macros in the AMD display core, including DPP transfer-function lists, MPC/MPCC register tables, OPP/OPTC register tables, IRQ source descriptors, and clock-manager register access.
- SOC15/IP base definitions such as `cyan_skillfish_ip_offset.h`, `soc15_hw_ip.h`, and the `DMU_BASE__INST0_SEG...` style base-address macros that make `_BASE_IDX` meaningful.
- Cross-generation DCN headers. Similar register families exist in DCN 2.0.0, DCN 2.1, DCN 3.x, and later headers, but offsets, instance counts, and register presence can differ. Consumers must include the matching generation header rather than assuming a common address map.

The repeated instance patterns are a major integration contract. `CM2` and `CM3`, `MPCC0`-`MPCC4`, `MPCC_OGAM0`-`MPCC_OGAM4`, `FMT0`/`FMT1`, `DPG0`/`DPG1`, `ODM0`/`ODM1`, and `OTG0`/`OTG1` are expected to align with instance-id macro expansion in display code. A single wrong offset in one instance can affect only that pipe or output path and may not be caught by single-display testing.

## Risks

- Offset/base-index mismatch is the primary risk. `mm...` values are not useful alone; using the wrong `_BASE_IDX` can target a different MMIO aperture even when the symbolic register name is correct.
- Repeated instance drift is easy to introduce. The MPCC, MPCC OGAM, FMT/DPG/OPP, ODM, and OTG blocks are near copies with different base offsets; copy/paste or generation errors can break one pipe while adjacent pipes still work.
- Indexed LUT programming registers are stateful. Wrong CM/OGAM LUT index/data/control offsets can corrupt transfer functions, gamut remap, blending gamma, or output gamma and produce subtle color regressions.
- Update-lock and synchronization registers have cross-block effects. Incorrect MPC vupdate-lock, OTG update-lock, master update, or global sync offsets can cause partial updates, timing glitches, or hangs during modesets and flips.
- Interrupt and CRC registers mix control, mask, status, and readback semantics. Wrong OTG vertical interrupt or CRC offsets can lose vblank/vline events, acknowledge the wrong source, or make diagnostics misleading.
- Power-control and status registers are easy to confuse. DPP DSCL/OBUF, CM memory power, MPCC memory power, OPP clock, and OTG clock controls can leave display sub-blocks gated or incorrectly reported if offsets are wrong.
- DIO I2C offsets affect monitor discovery. Broken DDC speed/setup/transaction/status addresses can prevent EDID reads, HPD-related probing, or AUX/DDC fallback behavior from working reliably.
- This chunk begins and ends mid-file. The DPP2 DSCL block starts before line 2585, and the DIO I2C block continues after line 5134; the merge lane must combine adjacent chunks for a complete file-level map.

## Test Signals

Useful validation signals are mostly compile-time macro expansion plus runtime display behavior:

- AMDGPU/display compilation should catch missing or renamed offset macros in DCN 2.0.1 resource, clock-manager, IRQ, DPP, MPC, OPP, and OPTC table construction.
- Static comparison against the vendor register database and adjacent generated DCN 2.0.1 mask/shift header should confirm every offset has the expected `_BASE_IDX` and matching field definitions.
- Modeset tests should exercise one and two active pipes, pipe 3 DPP use, MPCC composition, OPP0/OPP1 output paths, ODM0/ODM1 routing, OTG0/OTG1 timing, and DSC start-position programming.
- Color tests should cover degamma, blend gamma, output gamma, gamut remap, CSC, denorm clamp, dither, 4:2:0/4:2:2 output handling, and LUT programming on the affected DPP/MPC/OPP paths.
- Synchronization tests should verify vblank, vline, vupdate, frame counters, update locks, global sync lock, DRR, stereo, and master enable behavior on both OTG instances.
- Diagnostic paths should validate DPP/MPC/OPP/OTG CRC controls and readback registers, DPG pattern generation, pixel readback/status registers, and performance/status counters where available.
- Power-management tests should cover suspend/resume, runtime clock/memory gating, repeated modesets, blank/unblank, static-screen handling, and recovery from underflow or stalled MPCC state.
- DDC/I2C tests should confirm EDID reads, DDC1/DDC2 speed/setup programming, arbitration, SW/HW status transitions, interrupt behavior, and transaction sequencing on real connectors.

## Chunk Notes

This is a generated register-offset slice, so its research value is the hardware map and consumer contracts rather than algorithmic behavior. The most important areas for reconciliation are the repeated instance families and the high-impact stateful blocks: color/gamma LUTs, MPCC routing, output formatting, OTG timing/interrupts, update locks, power controls, and DDC/I2C transactions.
