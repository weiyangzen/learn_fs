# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-common.h

## Purpose
This header defines the shared data model and bitfield helpers used by all CV18xx clock classes. It is the common substrate for gates, dividers, muxes, audio clocks, and PLLs.

## Important APIs, Types, And Functions
`struct cv1800_clk_common` embeds `struct clk_hw`, an MMIO base, a shared spinlock pointer, and feature flags. `struct cv1800_clk_regbit` describes a single bit; `struct cv1800_clk_regfield` describes a multi-bit field with an optional initial value and divider flags. `CV1800_CLK_COMMON`, `CV1800_CLK_BIT`, and `CV1800_CLK_REG` initialize those structures.

Inline-like macros `cv1800_clk_regfield_genmask()`, `cv1800_clk_regfield_get()`, `cv1800_clk_regfield_set()`, and `_CV1800_SET_FIELD()` implement field packing and extraction. The header declares `cv1800_clk_setbit()`, `cv1800_clk_clearbit()`, `cv1800_clk_checkbit()`, and `cv1800_clk_wait_for_lock()`.

## Control Flow
No executable flow exists beyond macros. The initialization macro uses `CLK_HW_INIT_PARENTS_DATA()` so all CV18xx classes use firmware/clk_hw parent-data arrays consistently.

## State And Persistence
The common struct is embedded in each static clock object. At probe time, the top-level driver sets its `base` and `lock`; after that, CCF callbacks use those pointers to access persistent hardware registers.

## Dependencies And Integration Points
The header depends on CCF, compiler helpers, and bitfield macros. It is included by both `clk-cv18xx-ip.*` and `clk-cv18xx-pll.*`, and indirectly by the top-level CV1800 clock table.

## Risks
Field macros assume valid widths and shifts; invalid descriptors can generate undefined or unintended masks. `initval` carries special semantics in divider code, so table authors must distinguish fixed dividers, hardware default dividers, and writable dividers carefully.

## Test Signals
Static analysis should catch impossible shifts/widths when constants are visible. Runtime tests should verify descriptor initialization for representative gate, divider, mux, and PLL clocks after `cv1800_clk_init_ctrl()` sets base/lock.
