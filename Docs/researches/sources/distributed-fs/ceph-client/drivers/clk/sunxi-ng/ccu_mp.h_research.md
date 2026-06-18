# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mp.h

## Purpose
This header declares the M/P clock class used for many Allwinner module clocks, including the special MMC variant.

## Important APIs, Types, And Functions
Important items are `struct ccu_mp`, `SUNXI_CCU_MP_WITH_MUX_GATE*`, data/hardware parent variants, dual-divider variants, `SUNXI_CCU_MP_MMC_WITH_MUX_GATE`, `hw_to_ccu_mp()`, `ccu_mp_ops`, and `ccu_mp_mmc_ops`.

## Control Flow
It has no runtime flow; macros construct descriptors that `ccu_mp.c` operates on.

## State And Persistence
Descriptor state includes enable bit, M and P divider descriptors, mux metadata, optional fixed postdivider, and common feature flags.

## Dependencies And Integration Points
Dependencies are CCF, bitops, common/div/mult/mux headers. Integration is with MMC, SPI, NAND, IR, peripheral module clocks, and SoC CCU tables.

## Risks
Misusing dual-divider vs shift-style P changes the formula. MMC descriptors require `CLK_GET_RATE_NOCACHE` because timing mode changes the effective output outside normal CCF caching.

## Test Signals
Build and hardware tests for MMC, SPI, NAND, and other MP clocks validate macro correctness.
