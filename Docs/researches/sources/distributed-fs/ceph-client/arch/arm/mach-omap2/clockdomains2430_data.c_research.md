# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains2430_data.c

Purpose: Provides OMAP243x clockdomain descriptors, including the modem domain, and registers them with OMAP2 clockdomain operations.

Important APIs/types/functions: Defines wake dependency arrays for core, MPU, and MDM, clockdomains for `mpu`, `mdm`, `dsp`, `gfx`, `core_l3`, `core_l4`, and `dss`, `clockdomains_omap243x[]`, and `omap243x_clockdomains_init()`.

Control flow: Initialization registers `omap2_clkdm_operations`, the OMAP243x descriptor array, and completes generic clockdomain setup. Core L3/L4 share the same dependency bit according to file comments, matching OMAP243x hardware limitations.

State and persistence: Static descriptors become runtime clockdomain objects. Dependency arrays store mutable resolved pointers and usecounts after init; actual state is controlled in OMAP2430 PRCM/CM registers.

Dependencies: Uses shared 24xx dependency arrays and `wkup_common_clkdm`, plus 24xx PRM/CM register bit macros. Powerdomain names include `mpu_pwrdm`, `mdm_pwrdm`, `dsp_pwrdm`, `gfx_pwrdm`, and `core_pwrdm`.

Integration points: Used by OMAP2430 early platform initialization. It connects OMAP243x-specific data to generic `clockdomain.c` and OMAP2 CM low-level operations.

Risks: The single dependency bit used for both core L3 and L4 requires care in dependency accounting. Missing or mismatched `mdm_clkdm` dependencies could affect modem wake latency and retention.

Test signals: OMAP2430 boot should resolve MDM, DSP, GFX, MPU, WKUP, core L3/L4 dependencies. Suspend/resume and modem-related wake scenarios are the strongest behavioral checks.
