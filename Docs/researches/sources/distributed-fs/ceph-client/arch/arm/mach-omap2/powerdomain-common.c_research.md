# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomain-common.c

## Purpose
`powerdomain-common.c` provides shared helpers for mapping powerdomain memory-bank indexes to OMAP3/OMAP4 register masks. It abstracts common memory on-state, retention-state, and status bitfields used by arch-specific `pwrdm_ops`.

## Important APIs, Types, and Functions
The exported functions are `omap2_pwrdm_get_mem_bank_onstate_mask()`, `omap2_pwrdm_get_mem_bank_retst_mask()`, and `omap2_pwrdm_get_mem_bank_stst_mask()`. They accept a bank index 0-4 and return register masks such as `OMAP_MEM0_ONSTATE_MASK`, `OMAP_MEM4_RETSTATE_MASK`, or warn on invalid indexes.

## Control Flow
Each helper is a switch over the bank number. Invalid banks trigger `WARN_ON(1)` and return `-EEXIST` cast through `u32`. OMAP powerdomain operation implementations call these helpers while programming or reading memory-bank state fields.

## State and Persistence Behavior
There is no stored state. The returned masks control persistent hardware register reads/writes in callers.

## Dependencies and Integration Points
It depends on PM, CM, and PRM register-bit headers. It integrates with OMAP2/3/4 powerdomain operation backends that implement the generic `pwrdm_ops` interface.

## Risks
Bank-to-mask mapping is global and low-level. Wrong masks can cause the framework to program one memory bank while believing it programmed another, leading to retention/off failures or context loss.

## Test Signals
Build OMAP3/4 PM. Exercise powerdomains with 1-5 memory banks and verify memory on/retention states through debugfs counters, PRM registers, and suspend/resume stability. Invalid bank warnings should never occur in normal operation.
