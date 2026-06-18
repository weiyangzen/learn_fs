# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mmc_timing.c

## Purpose
`ccu_mmc_timing.c` exposes a small platform API for switching supported MMC clocks between old and new timing modes.

## Important APIs, Types, And Functions
Important APIs are `sunxi_ccu_set_mmc_timing_mode()` and `sunxi_ccu_get_mmc_timing_mode()`, exported GPL symbols for MMC-related consumers.

## Control Flow
Both functions get the underlying `clk_hw`, convert to `ccu_common`, require `CCU_FEATURE_MMC_TIMING_SWITCH`, and then set or read `CCU_MMC_NEW_TIMING_MODE` in the clock register. The setter writes under the CCU spinlock.

## State And Persistence
The only state is the hardware timing-mode bit. No persistence exists across boot.

## Dependencies And Integration Points
It depends on Linux CCF internals, `linux/clk/sunxi-ng.h`, MMIO, and `ccu_common`. It integrates with MMC host drivers that need timing-mode control on newer Allwinner SoCs.

## Risks
Calling it on unsupported clocks returns `-ENOTSUPP`; consumers must handle that. The mode affects effective MMC clock rates and is coordinated with `ccu_mp_mmc_ops`, so inconsistent use can break card tuning.

## Test Signals
Test through MMC timing mode changes, card enumeration in legacy/high-speed modes, and clk-summary rates with old/new timing selected.
