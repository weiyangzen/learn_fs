<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_5_0_offset.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_5_0_offset.h

## Purpose

`clk_11_5_0_offset.h` is a generated AMDGPU CLK register address header for `clk_clk1_0_SmuClkDec` at base address `0x5c000`. It names CLK1 PLL, bypass, deep-sleep, and current-count registers for a four-clock block. It is structurally close to the CLK 10.0.2 CLK1 map but uses `CLK1_0_CLK1_*` register names, different offsets, and `BASE_IDX` `0`.

## Important APIs, Types, And Macros

There are no functions or types. The exported register constants are:

- `mmCLK1_0_CLK1_CLK_PLL_REQ` for PLL feedback multiplier control.
- `mmCLK1_0_CLK1_CLK0_BYPASS_CNTL` through `mmCLK1_0_CLK1_CLK3_BYPASS_CNTL` for per-clock bypass source/divider selection.
- `mmCLK1_0_CLK1_CLK3_DS_CNTL` and `mmCLK1_0_CLK1_CLK3_ALLOW_DS` for CLK3 deep-sleep divider and allow behavior.
- `mmCLK1_0_CLK1_CLK0_CURRENT_CNT` through `mmCLK1_0_CLK1_CLK3_CURRENT_CNT` for live clock counters.

Every register has `BASE_IDX` `0`, which is part of the register-table contract.

## Control Flow

The header only uses an include guard. Runtime flow is external: AMD display code selects ASIC-specific register tables, reads counters and bypass registers for diagnostics, and may use PLL/deep-sleep registers for clock calculation or low-power control. No polling loops or state transitions are implemented in this file.

## State And Persistence Behavior

The file holds no state. It identifies hardware state in PLL, bypass, deep-sleep, and current-count registers. PLL and bypass fields can affect the active display clock topology until driver/SMU changes or reset. Current counters are readback state, and deep-sleep registers affect whether and how CLK3 can enter lower-power operation.

## Dependencies

Operational dependencies include `clk_11_5_0_sh_mask.h`, AMDGPU MMIO/register-table helpers, and ASIC dispatch that selects CLK 11.5.0 only for matching hardware. Because this is generated metadata, it also depends on consistency with AMD's register database.

## Integration Points

The constants integrate with display clock-manager register structs containing `CLK1_CLK*_CURRENT_CNT`, `CLK1_CLK3_ALLOW_DS`, and `CLK1_CLK*_BYPASS_CNTL` fields. These paths populate debug and SMU log data for display clocks such as DISPCLK, DPPCLK, DPREFCLK, and DCFCLK, and help compute or verify clock sources from PLL and bypass state.

## Risks And Edge Cases

The name pattern is easy to confuse with `clk_10_0_2` because both represent a CLK1 block with four current counters. Offsets and base index differ, so sharing tables across generations is unsafe. `CLK3` is the only deep-sleep-controlled clock in this header; code must not assume CLK0/CLK1/CLK2 have matching allow registers. Hardware sequencing for PLL and bypass updates is not documented here and must come from clock-manager logic or hardware specs.

## Test Signals

Static tests should compare the generated offset table against the register database and build display clock-manager users. Runtime signals include current-count readbacks for each clock, bypass-source decoding, and display idle/suspend tests that confirm CLK3 deep-sleep allowance and counters behave as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_5_0_offset.h -->
