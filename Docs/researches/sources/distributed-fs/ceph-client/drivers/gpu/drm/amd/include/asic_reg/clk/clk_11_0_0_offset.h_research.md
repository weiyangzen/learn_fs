<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_0_offset.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_0_offset.h

## Purpose

`clk_11_0_0_offset.h` is a generated AMDGPU register address header for a compact CLK 11.0.0 block. It names two registers in the `clk_clk3_0_SmuClkDec` address block at base address `0x5c800`: a CLK3 PLL request register and a CLK2 DFS divider-control register. The header gives display clock-manager code symbolic offsets for ASIC-specific clock programming and readback.

## Important APIs, Types, And Macros

The file defines no functions or C types. Its exported constants are:

- `mmCLK3_0_CLK3_CLK_PLL_REQ` with `BASE_IDX` `3`, offset `0x000e`.
- `mmCLK3_0_CLK3_CLK2_DFS_CNTL` with `BASE_IDX` `3`, offset `0x0054`.

The prefix encodes both the clock block instance (`CLK3_0`) and register family (`CLK3`). Consumers use the matching `clk_11_0_0_sh_mask.h` macros to decode feedback multiplier and divider fields.

## Control Flow

Only the `_clk_11_0_0_OFFSET_HEADER` include guard executes at compile time. Runtime code selects this header's register table for compatible ASICs, reads the PLL request register to derive the PLL-programmed clock source, and reads or writes the CLK2 DFS control register to inspect or program the divider. The file itself does not sequence clock changes.

## State And Persistence Behavior

The header contributes compile-time constants only. Hardware state is stored in the PLL request and DFS control registers. PLL and divider values are persistent hardware configuration across normal software reads, but can change through SMU/firmware interaction, display clock-manager updates, power transitions, or reset.

## Dependencies

The file depends on AMDGPU's generated-register naming conventions, the matching shift/mask header, and display clock-manager infrastructure that turns `mm*` names plus `BASE_IDX` into register-table entries. It also depends on correct ASIC matching because the offsets and base index are not self-validating.

## Integration Points

Local display code references CLK3 PLL request fields through `CLK_SRI` and `CLK_SF`-style macros in clock-manager internal headers. These constants support DCN clock-manager paths that need PLL feedback multiplier values or DFS divider values for derived clock reporting and programming.

## Risks And Edge Cases

This header is sparse: it exposes only two registers. Consumers must not assume it covers the full CLK block. The `BASE_IDX` value is `3`, unlike many newer register headers that use base index `0`, so table-generation macros must retain the correct base index. Confusing `CLK3_0_CLK3_CLK2_DFS_CNTL` with similarly named CLK0/CLK1/CLK4 blocks can result in reading the wrong clock domain.

## Test Signals

Build coverage should include the DCN clock-manager variant that uses CLK 11.0.0 metadata. Hardware validation should verify PLL-derived frequency calculations from `CLK3_0_CLK3_CLK_PLL_REQ` and divider extraction from `CLK3_0_CLK3_CLK2_DFS_CNTL`. A generated-header comparison against AMD register metadata is the strongest unit-level signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_0_offset.h -->
