<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/reset-prcc.h -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/reset-prcc.h

## Purpose

`reset-prcc.h` declares the U8500 PRCC reset-controller state shared between U8500 clock setup and reset implementation.

## Important APIs, Types, And Functions

`struct u8500_prcc_reset` embeds `struct reset_controller_dev`, the physical base addresses for each CLKRST block, and remapped MMIO bases. `u8500_prcc_reset_init()` is the exported initializer.

## Control Flow

The header has no flow. `u8500_of_clk.c` allocates and populates the structure, then passes it to `u8500_prcc_reset_init()` when it sees the reset-controller child node.

## State And Persistence Behavior

The structure owns runtime reset-controller state and MMIO mappings. Hardware reset state remains in PRCC registers.

## Dependencies And Integration Points

It depends on reset-controller and IO types and on `CLKRST_MAX` from `prcc.h`, so includers must include the PRCC topology first.

## Risks And Test Signals

Risks are uninitialized `phy_base` entries if DT resources are missing and stale mappings with no teardown. Build tests catch missing include order; boot tests should register the reset controller and exercise several PRCC reset cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/reset-prcc.h -->
