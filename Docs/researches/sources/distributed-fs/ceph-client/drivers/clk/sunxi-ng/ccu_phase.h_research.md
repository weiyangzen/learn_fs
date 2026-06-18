# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_phase.h

## Purpose
This header declares the phase clock descriptor used by sunxi-ng MMC sample/output clocks.

## Important APIs, Types, And Functions
It defines `struct ccu_phase`, `SUNXI_CCU_PHASE`, `hw_to_ccu_phase()`, and `ccu_phase_ops`.

## Control Flow
There is no runtime flow; the macro builds descriptors operated on by `ccu_phase.c`.

## State And Persistence
Descriptor state is shift, width, register offset, and embedded `clk_hw` metadata.

## Dependencies And Integration Points
It depends on CCF and `ccu_common`. Integration is with SoC CCU files that expose MMC phase clocks.

## Risks
Wrong shift/width values can corrupt the main MMC divider or mux fields sharing the same register.

## Test Signals
MMC phase set/get and data-transfer tests validate it.
