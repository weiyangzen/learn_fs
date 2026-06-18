# sources/distributed-fs/ceph-client/drivers/clk/sprd/pll.h

## Purpose
Declares PLL data structures, factor indexes, and constructor macros for Spreadtrum PLL clocks.

## Important APIs, Types, And Functions
`struct reg_cfg` stores pending register value/mask pairs. `struct clk_bit_field` maps factor shift and width. The PLL factor enum covers lock, div mode, modulation, SDM, reference input, ibias, N/NINT/KINT, prediv, and postdiv. `struct sprd_pll` stores register count, ibias table, factor table, delay, fractional constants, FVCO behavior, and common clock data. Macros include `SPRD_PLL_WITH_ITABLE_K_FVCO`, `SPRD_PLL_WITH_ITABLE_1K`, `SPRD_PLL_FW_NAME`, and `SPRD_PLL_HW`.

## Control Flow
No direct runtime flow. Macro expansion initializes static PLL objects that use `sprd_pll_ops`; runtime interpretation happens in `pll.c`.

## State And Persistence
The structure stores static PLL formula metadata and common register location. Hardware registers store the live PLL configuration.

## Dependencies And Integration Points
Includes `common.h` and is consumed by SC9860/SC9863A SoC files. Fixed-factor clocks often derive from these PLL `clk_hw` objects.

## Risks And Edge Cases
Factor table indexes must align exactly with the enum. `regs_num` controls bounds for register access and allocation, so an incorrect value can hide fields or trigger warnings. Ibias table element zero is a count, which is easy to misuse.

## Test Signals
Compile-time macro coverage, rate recalc/set-rate validation for each PLL descriptor, and comparing exposed fixed-factor child rates against expected PLL outputs.
