<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu.h -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu.h

## Purpose

`clk-cgu.h` declares the LGM CGU clock data structures, table macros, flags, and regmap bitfield helpers.

## Important APIs, Types, And Functions

It defines runtime structs for mux, divider, dual divider, gate, PLL, and provider state. It defines `lgm_pll_clk_data`, `lgm_clk_ddiv_data`, and `lgm_clk_branch` table formats plus macros `LGM_PLL`, `LGM_DDIV`, `LGM_MUX`, `LGM_DIV`, `LGM_GATE`, `LGM_FIXED`, and `LGM_FIXED_FACTOR`. `lgm_set_clk_val()` and `lgm_get_clk_val()` wrap regmap bitfield updates and reads.

## Control Flow

No standalone flow exists. `clk-lgm.c` expands macros into tables; `clk-cgu.c` and `clk-cgu-pll.c` consume them.

## State And Persistence Behavior

The header defines metadata for register offsets, widths, parent data, flags, and provider arrays. Hardware state remains in CGU registers.

## Dependencies And Integration Points

It depends on regmap and common CCF types expected through includers. It is the internal ABI between LGM table and helper files.

## Risks And Test Signals

Risks are compound-literal parent data lifetime assumptions, bit-width masks with width zero, and warning-only read failure behavior returning zero. Build tests catch macro/API drift; register-level tests should verify every macro row decodes correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu.h -->
