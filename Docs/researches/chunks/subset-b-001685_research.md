# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 12950-15501

## Purpose

This chunk is part of AMDGPU's generated DCN 3.0.0 register-offset header. It maps symbolic `mm...` register names to MMIO offsets plus `..._BASE_IDX` values for several display engine blocks. The values are not executable logic; they are compile-time constants consumed by display-core register-list macros so higher-level DCN code can use `REG_SET`, `REG_UPDATE`, `REG_GET`, `SR`, `SRI`, `SRII`, and field-mask helpers without hard-coding addresses.

The covered slice starts in the middle of DSC encoder instance 1 and then covers DSC instances 2-5, DWB0, MPC MPCC instances 0-5, MPC output gamma and output CSC blocks, and the beginning of the MPC RMU shaper table block.

## Register Blocks Covered

- DSC / DSCC:
  - Tail of `DSCC1_DSCC_*`, beginning at `DSCC_PPS_CONFIG12`, through rate-buffer fullness and debug registers.
  - Full repeated blocks for `DSC_TOP2` through `DSC_TOP5`, `DSCCIF2` through `DSCCIF5`, `DSCC2` through `DSCC5`, and per-DSC performance monitors `DC_PERFMON22` through `DC_PERFMON25`.
  - These define PPS packet fields, compression status, interrupt/status registers, memory power control, error counters, and rate-buffer fullness/debug registers for display stream compression.
- DWB0:
  - `DWB_ENABLE_CLK_CTRL`, memory power, frame-capture controls, window/source geometry, CRC controls, output format/denorm controls, MMHUBBUB backpressure counters, host-read and reset controls.
  - `DWBCP` color-processing registers for HDR multiplier, gamut remap matrices, output gamma LUT access, RAMA/RAMB region programming, and debug hooks.
- MPC / MPCC:
  - `MPCC0` through `MPCC5` blending pipes, each with mux, control, status, top/bottom gain, memory power, background color, ALU status, and debug registers.
  - `MPCC_OGAM0` through `MPCC_OGAM5` output-gamma and gamut-remap blocks, including LUT index/data/control, coefficient-format/remap mode, matrix coefficients, RAMA/RAMB piecewise-linear region parameters, offsets, base/slope/end controls, memory power, and debug registers.
- MPC configuration and output:
  - `MPC_MUX`, `MPC_OUT_MUX`, cursor vupdate lock, DWB mux selection, debug/status, and clock-gating configuration.
  - `MPC_OUT0` through `MPC_OUT5` output CSC matrix registers, with A/B coefficient banks for each output.
- MPC RMU:
  - The chunk ends after the start of `dce_dc_mpc_mpc_rmu_dispdec`, covering `MPC_RMU_CONTROL`, `MPC_RMU_MEM_PWR_CTRL`, and early `MPC_RMU0_SHAPER_*` registers through RAMA region programming.

## Important APIs, Types, and Macros

There are no functions or C types defined in this chunk. The important interface is the naming contract:

- `#define mm<block>_<register> <offset>` gives a register offset.
- `#define mm<block>_<register>_BASE_IDX <idx>` selects the register-base segment used by `BASE(...)`.
- Consumers combine the two as `BASE(mm..._BASE_IDX) + mm...`, typically through macros such as `SR(...)`, `SRI(...)`, `SRII(...)`, and DCN-specific variants.
- Field positions and masks are supplied separately by `dcn_3_0_0_sh_mask.h`.

Observed integration points include:

- `display/dc/dsc/dcn20/dcn20_dsc.h` builds DSC register lists with `SRI(DSC_TOP_CONTROL, DSC_TOP, id)`, `SRI(DSCC_PPS_CONFIG*, DSCC, id)`, and `SRI(DSCCIF_CONFIG*, DSCCIF, id)`. `dcn20_dsc.c` then programs PPS, slice geometry, rate-control fields, clock enables, and status reads through `REG_SET_*`, `REG_UPDATE`, and `REG_GET`.
- `display/dc/dwb/dcn30/dcn30_dwb.h` builds the DWB register table from these offsets, and `dcn30_dwb.c` uses them to enable/disable writeback, lock updates, program frame capture, color processing, denorm, CRC, and status reads.
- `display/dc/mpc/dcn30/dcn30_mpc.h` builds MPCC, MPC output, DWB mux, and RMU register tables from this chunk. The MPC code uses the resulting tables for plane composition, blending, output color conversion, output gamma, RMU shaper/3D LUT programming, and memory-power state checks.
- `display/dmub/src/dmub_dcn30.c` and `dmub_dcn302.c` include this offset header for DMUB-facing DCN 3.0 register access.

## Control Flow

The header itself has no runtime control flow. Runtime flow is indirect:

1. DCN 3.0 resource construction expands register-list macros into per-block `uint32_t` register tables.
2. Display algorithms select instances such as DSC2, MPCC4, DWB0, or MPC_OUT3.
3. Register helpers read or write `BASE(base_idx) + offset`.
4. Paired mask/shift definitions isolate fields inside each register.

The repeated instance layout is central to that flow. DSC instance offsets progress by instance base (`0x2e0`, `0x450`, `0x5c0`, `0x730` in this slice for instances 2-5), MPCC blocks are spaced by instance base (`0x0`, `0x80`, `0x100`, ...), MPCC_OGAM blocks are spaced by larger blocks (`0x0`, `0x200`, ...), and MPC_OUT CSC registers are contiguous per output.

## State and Persistence Behavior

All state controlled by these definitions lives in GPU display hardware registers, not in kernel memory owned by this header. Persistence is therefore hardware/register-lifetime state:

- DSC PPS/config/status registers affect active Display Stream Compression programming until reprogrammed, reset, or power-gated.
- DWB update-lock and frame-capture bits gate when writeback changes become active. DWB CRC and backpressure counters expose hardware diagnostic state.
- MPCC control, mux, alpha/gain, background color, and OGAM LUT/region registers define active composition and color pipeline state for each MPCC instance.
- MPC output CSC registers hold output color-space conversion coefficients per output.
- RMU shaper LUT and memory-power registers preserve color-management table state while the relevant memory is powered and valid.

The `_BASE_IDX` values matter because they place the same logical register names into the correct MMIO aperture. A wrong base index can write a valid-looking offset into the wrong hardware block.

## Dependencies

- Paired field metadata from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h`.
- DCN register-access macro framework in AMD display core (`REG_SET`, `REG_UPDATE`, `REG_GET`, `SR`, `SRI`, `SRII`, and related instance helpers).
- Hardware-specific base-address mapping behind `BASE(idx)`.
- Block-level DCN implementations for DSC, DWB, MPC, MPCC, OGAM, and RMU.
- Generated-register naming consistency across offset, mask/shift, and driver register-list headers.

## Risks and Edge Cases

- This chunk begins and ends inside logical blocks: it starts after earlier `DSCC1` PPS registers and ends in the middle of `MPC_RMU0_SHAPER_*`. Any final per-file summary must reconcile adjacent chunks for complete block coverage.
- Offset or base-index drift between `dcn_3_0_0_offset.h` and `dcn_3_0_0_sh_mask.h` can silently corrupt field writes, because the compiler only sees integer constants.
- Instance-copy mistakes are high impact. The repeated DSC, MPCC, OGAM, and MPC_OUT patterns differ mainly by prefix and base address, so a wrong instance macro can program the wrong pipe or compressor.
- Color-management registers are table-oriented and double-buffered/status-sensitive in consumers. Misordered LUT index/data/control writes can produce wrong gamma, gamut, or shaper state even when offsets compile.
- DWB controls include update locks, capture enable, CRC, and backpressure counters. Bugs here may manifest as missed captures, stale writeback frames, or misleading diagnostics.
- Memory-power registers for DSCC, DWB OGAM, MPCC OGAM, and RMU must align with code that waits for or checks power state. Bad offsets can look like timeout, blank output, or color-pipeline failure.

## Test Signals

- Build coverage: compile AMDGPU display code for DCN 3.0 paths to catch missing or renamed macros in DSC, DWB, MPC, and DMUB consumers.
- Register-table sanity: compare generated register tables against expected ASIC register maps, especially repeated instance spacing for `DSCC2-5`, `MPCC0-5`, `MPCC_OGAM0-5`, and `MPC_OUT0-5`.
- Display Stream Compression validation: modes requiring DSC should program PPS registers, enable DSC clocks, and avoid DSCC rate-buffer overflow/underflow interrupt/status bits.
- DWB validation: enable/update/disable writeback paths should toggle `DWB_ENABLE` and `FC_FRAME_CAPTURE_EN`, honor `DWB_UPDATE_LOCK`, produce expected CRC values, and avoid unexpected MMHUBBUB backpressure.
- Composition validation: multi-plane blending, alpha/gain programming, and MPCC mux changes should affect the intended MPCC instance only.
- Color validation: output CSC, MPCC OGAM, DWB OGAM, and RMU shaper programming should be checked with color pipeline tests or CRC/reference-frame comparisons.
- Power-management validation: suspend/resume, display idle, and memory power-gating tests should not lose required LUT/config state or hang while polling memory-power/status fields.
