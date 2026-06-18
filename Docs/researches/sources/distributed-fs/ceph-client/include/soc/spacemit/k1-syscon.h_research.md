# sources/distributed-fs/ceph-client/include/soc/spacemit/k1-syscon.h

Purpose: defines SpacemiT K1 clock/reset syscon register offsets and PLL lock bits for APBS, MPMU, APBC, APMU, RCPU, RCPU2, and APBC2 domains.

Important APIs/types/functions: macro-only API including `APBS_PLL*_SWCR*`, `MPMU_*`, `POSR_PLL*_LOCK`, many `APBC_*_CLK_RST`, `APMU_*_CLK_RES_CTRL`, `RCPU_*_CLK_RST`, `RCPU2_PWM*_CLK_RST`, and `APBC2_*_CLK_RST` offsets. It includes `ccu.h` for shared CCU auxiliary definitions.

Control flow: clock/reset drivers use the offsets to program gates, resets, muxes, dividers, and PLL controls through regmap. PLL lock bits are polled after PLL changes.

State and persistence: register contents represent persistent clock, reset, and PLL state for K1 functional blocks until reset or reconfiguration.

Dependencies and integration: included by `drivers/clk/spacemit/ccu-k1.c` and `drivers/reset/spacemit/reset-spacemit-k1.c`.

Risks: offset mistakes can gate/reset the wrong peripheral or misread PLL lock. K1 has many similarly named peripherals, so table alignment is important. Test signals include K1 clock tree registration, peripheral probe, reset controller tests, PLL lock polling, and suspend/resume.
