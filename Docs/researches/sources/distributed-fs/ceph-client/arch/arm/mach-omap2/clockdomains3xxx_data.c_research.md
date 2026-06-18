# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains3xxx_data.c

Purpose: Provides OMAP3/AM35x clockdomain descriptors, wake dependencies, sleep dependencies, auto-dependency data, and SoC-revision-specific registration sets.

Important APIs/types/functions: Defines dependency arrays for SGX/GFX, PER, USBHOST, MPU, IVA2, CAM, DSS, NEON, and sleepdeps for DSS/PER/USBHOST/CAM/GFX. Defines clockdomains including MPU, NEON, IVA2, GFX/SGX, D2D, CORE L3/L4, DSS, CAM, USBHOST, PER, EMU, and DPLL domains. Provides `clockdomains_common[]`, `clockdomains_omap3430[]`, ES1/ES2+ variants, `clockdomains_am35x[]`, and `omap3xxx_clockdomains_init()`.

Control flow: Initialization registers `omap3_clkdm_operations`, registers common domains, conditionally registers OMAP3430 or AM35x-specific domain sets based on `soc_is_omap3430()` and `soc_is_am35xx()`, registers OMAP3 autodeps, and completes init.

State and persistence: Dependency arrays are resolved at runtime and their usecounts are adjusted by generic autodep and dependency APIs. OMAP3 CM registers hold CLKSTCTRL, wake, and sleep dependency state; broader CM context is saved by `cm3xxx.c`.

Dependencies: Uses `soc.h`, OMAP3 PRM/CM module definitions, `cm-regbits-34xx.h`, and `clockdomain.h`. Powerdomain names cover `mpu_pwrdm`, `neon_pwrdm`, `iva2_pwrdm`, `sgx_pwrdm`, `core_pwrdm`, `dss_pwrdm`, `cam_pwrdm`, `usbhost_pwrdm`, `per_pwrdm`, `emu_pwrdm`, and DPLL domains.

Integration points: This is the main OMAP3 clockdomain topology used by OMAP3 PM, clock, and hwmod code. It couples with `omap3_clkdm_operations` for sleepdep manipulation and deprecated autodeps needed by OMAP3 clock gating.

Risks: Many SoC revision conditionals mean an incorrect `soc_is_*` result can register the wrong SGX/GFX/USBHOST domain layout. Autodeps are deprecated and energy-costly but still required. `CLKDM_MISSING_IDLE_REPORTING` flags are critical for EMU-like domains to avoid unsafe powerdomain idling.

Test signals: OMAP3430 ES1, ES2+, and AM35x builds/boots should each register the expected variant domains. Suspend/resume, SGX/DSS/USBHOST activity, and DPLL idle behavior are important validation signals.
