# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nm.h

## Purpose
This header declares the N/M PLL class and the macros for fractional, SDM, min/max, closest-rate, and simple gated variants.

## Important APIs, Types, And Functions
Important items are `struct ccu_nm`, `SUNXI_CCU_NM_WITH_SDM_GATE_LOCK`, `SUNXI_CCU_NM_WITH_FRAC_GATE_LOCK*`, `SUNXI_CCU_NM_WITH_GATE_LOCK`, and `ccu_nm_ops`.

## Control Flow
No runtime flow exists in the header. Macros create descriptors consumed by `ccu_nm.c`.

## State And Persistence
State includes enable/lock bits, N/M fields, fractional and SDM descriptors, fixed postdivider, min/max rates, and common metadata.

## Dependencies And Integration Points
It depends on common/div/frac/mult/sdm headers. It integrates with audio, video, VE, ISP, and other PLL descriptors.

## Risks
Fractional and SDM modes have exact-rate semantics. Incorrect min/max or feature bits can bypass the intended path and program unstable integer factors.

## Test Signals
Test with audio SDM rates, video fractional rates, normal integer PLL rates, and lock-wait behavior.
