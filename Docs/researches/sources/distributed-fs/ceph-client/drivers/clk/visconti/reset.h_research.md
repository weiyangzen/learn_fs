<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/reset.h -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/reset.h

## Purpose

`reset.h` declares the Visconti reset-controller table and runtime structures.

## Important APIs, Types, And Functions

`struct visconti_reset_data` stores assert/deassert offsets and reset bit index. `struct visconti_reset` embeds `reset_controller_dev`, regmap, reset table, and lock. It declares `visconti_reset_ops` and `visconti_register_reset_controller()`.

## Control Flow

No flow exists. SoC files provide reset tables and call the registration helper.

## State And Persistence Behavior

The runtime struct describes the reset controller state; actual reset assertion persists in hardware registers.

## Dependencies And Integration Points

It depends on Linux reset-controller types and is included by both clock and reset common files.

## Risks And Test Signals

Risks include table IDs being used as direct array indices and no explicit bounds fields in each data row. Build tests catch prototype drift; runtime tests should cover every binding reset ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/reset.h -->
