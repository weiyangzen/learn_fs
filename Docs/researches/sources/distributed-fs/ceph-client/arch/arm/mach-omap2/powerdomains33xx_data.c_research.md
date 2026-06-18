# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains33xx_data.c

## Purpose
`powerdomains33xx_data.c` defines AM33xx powerdomain descriptors and registers them with the AM33xx PRM backend. It covers GFX, RTC, WKUP, PER, MPU, and CEFUSE domains with AM33xx-specific register offsets and bit masks.

## Important APIs, Types, and Functions
Descriptors include `gfx_33xx_pwrdm`, `rtc_33xx_pwrdm`, `wkup_33xx_pwrdm`, `per_33xx_pwrdm`, `mpu_33xx_pwrdm`, and `cefuse_33xx_pwrdm`. The init array is `powerdomains_am33xx[]`; entry point is `am33xx_powerdomains_init()`.

## Control Flow
Init registers `am33xx_pwrdm_operations`, registers all AM33xx domains, and completes initialization. Later `pm33xx-core.c` looks up several domains and controls GFX/CEFUSE during suspend setup.

## State and Persistence Behavior
Descriptors contain both generic state capabilities and AM33xx-specific register masks for control/status fields. After registration, mutable runtime state is stored in each descriptor object.

## Dependencies and Integration Points
It depends on `prm33xx.h`, `prm-regbits-33xx.h`, `prcm-common.h`, and AM33xx powerdomain operation callbacks. It integrates with AM33xx PM, cpuidle, and suspend firmware paths.

## Risks
AM33xx uses explicit `pwrstctrl_offs`, `pwrstst_offs`, and masks per memory bank; mask mistakes directly break state programming. PER and MPU have multiple memory banks and low-power state-change flags, increasing risk.

## Test Signals
Boot AM335x, verify all domains register, CEFUSE can be powered off on GP devices, GFX and PER domains transition during suspend, and debugfs counters match expected states after deepsleep/standby.
