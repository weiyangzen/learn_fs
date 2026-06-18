<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/prcc.h -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/prcc.h

## Purpose

`prcc.h` defines shared PRCC topology constants for U8500 clock and reset code.

## Important APIs, Types, And Functions

`PRCC_NUM_PERIPH_CLUSTERS` is 6 and `PRCC_PERIPHS_PER_CLUSTER` is 32. `enum clkrst_index` maps physical CLKRST blocks 1, 2, 3, 5, and 6 to compact array indices, explicitly skipping missing CLKRST4.

## Control Flow

There is no runtime flow. The constants drive array sizing, two-dimensional ID flattening, and physical-base indexing in `u8500_of_clk.c` and `reset-prcc.c`.

## State And Persistence Behavior

No state is stored. The numbering convention persists as a DT-facing contract because clock and reset specifiers use PRCC number plus bit.

## Dependencies And Integration Points

The header is private to Ux500 PRCC clock/reset code. It integrates the PRCC clock provider with the PRCC reset controller by keeping their cluster numbering consistent.

## Risks And Test Signals

Risks are off-by-one errors around skipped CLKRST4 and arrays sized with `PRCC_NUM_PERIPH_CLUSTERS + 1` versus `CLKRST_MAX`. Test DT references for PRCC 1/2/3/5/6 and rejection of PRCC4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/prcc.h -->
