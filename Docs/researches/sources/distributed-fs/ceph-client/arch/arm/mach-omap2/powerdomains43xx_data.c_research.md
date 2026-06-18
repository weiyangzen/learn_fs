# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomains43xx_data.c

## Purpose
`powerdomains43xx_data.c` defines AM43xx powerdomains using the OMAP4-style PRCM backend but disables voltage-domain association through a custom callback. It covers GFX, MPU, RTC, WKUP, TAMPER, CEFUSE, and PER.

## Important APIs, Types, and Functions
Descriptors include `gfx_43xx_pwrdm`, `mpu_43xx_pwrdm`, `rtc_43xx_pwrdm`, `wkup_43xx_pwrdm`, `tamper_43xx_pwrdm`, `cefuse_43xx_pwrdm`, and `per_43xx_pwrdm`. The init array is `powerdomains_am43xx[]`. Entry point is `am43xx_powerdomains_init()`, and `am43xx_check_vcvp()` returns 0 for `pwrdm_has_voltdm`.

## Control Flow
Init patches `omap4_pwrdm_operations.pwrdm_has_voltdm`, registers the OMAP4 operations, registers the AM43xx descriptors, then completes powerdomain init.

## State and Persistence Behavior
Descriptors become mutable runtime framework objects. Hardware state is programmed through OMAP4-style PRCM operations; voltage-domain linking is skipped because AM43xx does not use the same VC/VP association.

## Dependencies and Integration Points
It depends on AM43xx PRCM offsets and `omap4_pwrdm_operations`. It integrates with `pm33xx-core.c`, which maps SCU and controls AM43xx suspend behavior.

## Risks
Mutating global `omap4_pwrdm_operations` is intentional but affects subsequent registration in the same boot; ordering must remain AM43xx-specific. PER and MPU memory-bank arrays must align with AM43xx PRM fields.

## Test Signals
Boot AM437x, verify no voltage-domain lookup errors, all seven domains register, SCU/PM suspend paths work, and GFX/PER/MPU transitions are reflected in PM debug counters.
