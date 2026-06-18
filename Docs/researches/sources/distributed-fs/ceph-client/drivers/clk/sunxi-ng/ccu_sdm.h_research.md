# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_sdm.h

## Purpose
This header defines sigma-delta modulation table entries and descriptor state for sunxi-ng PLLs.

## Important APIs, Types, And Functions
Important types are `struct ccu_sdm_setting` and `struct ccu_sdm_internal`; `_SUNXI_CCU_SDM()` fills the descriptor and helper prototypes declare the runtime API.

## Control Flow
There is no runtime flow in the header. It stores static table data consumed by `ccu_sdm.c`.

## State And Persistence
Descriptor state includes supported rates, raw vendor pattern words, M/N factors, optional PLL enable bit, tuning enable bit, and tuning register offset.

## Dependencies And Integration Points
It depends on CCF and `ccu_common`; integration is through `ccu_nm` descriptors using `CCU_FEATURE_SIGMA_DELTA_MOD`.

## Risks
The comments document unknown hardware pattern semantics. Treat pattern words as hardware-calibrated constants, not values to recompute casually.

## Test Signals
Audio exact-rate tests validate descriptor entries.
