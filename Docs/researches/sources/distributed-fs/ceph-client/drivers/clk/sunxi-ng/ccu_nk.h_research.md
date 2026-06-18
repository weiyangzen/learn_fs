# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nk.h

## Purpose
This header declares the N*K PLL clock class.

## Important APIs, Types, And Functions
It defines `struct ccu_nk`, `SUNXI_CCU_NK_WITH_GATE_LOCK_POSTDIV`, `hw_to_ccu_nk()`, and `ccu_nk_ops`.

## Control Flow
There is no runtime flow; the macro creates static descriptors for `ccu_nk.c`.

## State And Persistence
Descriptor state includes enable and lock bits, N/K multiplier fields, fixed postdivider, and common metadata.

## Dependencies And Integration Points
Dependencies are CCF, common/div/mult headers. Integration is with peripheral PLL descriptors in SoC CCU files.

## Risks
Postdivider and offset fields are easy to misencode, which changes every child clock rate.

## Test Signals
PLL rate-change tests and lock-wait behavior validate this header.
