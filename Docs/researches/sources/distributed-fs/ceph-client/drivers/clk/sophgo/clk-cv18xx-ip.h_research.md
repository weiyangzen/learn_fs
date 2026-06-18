# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-ip.h

## Purpose
This header defines all non-PLL CV18xx clock object layouts and declaration macros. It lets the top-level clock table declare many gates/dividers/muxes compactly while binding each object to the correct `clk_ops`.

## Important APIs, Types, And Functions
Clock structs are `cv1800_clk_gate`, `cv1800_clk_div`, `cv1800_clk_bypass_div`, `cv1800_clk_mux`, `cv1800_clk_bypass_mux`, `cv1800_clk_mmux`, and `cv1800_clk_audio`. Declaration macros include `CV1800_GATE`, `CV1800_DIV`, `CV1800_BYPASS_DIV`, `CV1800_FIXED_DIV`, `CV1800_BYPASS_FIXED_DIV`, `CV1800_MUX`, `CV1800_BYPASS_MUX`, `CV1800_MMUX`, and `CV1800_ACLK`.

The header exports the operation tables implemented in `clk-cv18xx-ip.c`.

## Control Flow
No runtime flow exists in the header. The macros initialize embedded `cv1800_clk_common` records with `CLK_HW_INIT_PARENTS_DATA()` and attach class-specific descriptors for gate, divider, mux, bypass, selector, and audio fields.

## State And Persistence
Each macro expands to a static object whose descriptors are later completed with MMIO base and lock in the top-level probe. The descriptors encode how persistent hardware registers are manipulated by CCF callbacks.

## Dependencies And Integration Points
It depends on the common CV18xx header and on CCF types. The macro names are used extensively by `clk-cv1800.c`, so changes here affect all CV1800/CV1810/SG2000 clock definitions.

## Risks
The macros hide many positional arguments; swapping a register, shift, width, or init value is easy and hard to detect in review. The fixed-divider macro uses width 0 and initval as a sentinel, so helper code must continue to preserve that convention.

## Test Signals
Build-time coverage verifies macro expansion. Runtime validation should map each macro family to at least one clock in `clk_summary` and test rate/parent/gate behavior for that instance.
