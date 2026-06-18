# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains2xxx_3xxx_data.c

Purpose: Holds static clockdomain data shared by OMAP2xxx and OMAP3xxx families, avoiding duplication in SoC-specific files.

Important APIs/types/functions: Defines exported wake dependency arrays `gfx_24xx_wkdeps` and `dsp_24xx_wkdeps`, and exported `wkup_common_clkdm`.

Control flow: OMAP2420 and OMAP2430 data files include `wkup_common_clkdm` in their registration arrays and reference the shared dependency arrays from their static clockdomain descriptors. The generic framework resolves dependency names at `clkdm_complete_init()`.

State and persistence: The arrays are static and long-lived. Their `clkdm` pointers and usecounts are mutated after registration; `wkup_common_clkdm` receives normal runtime fields such as usecount and list node once registered.

Dependencies: Uses `prm2xxx_3xxx.h`, `cm-regbits-24xx.h`, and `clockdomain.h`. Depends on common clockdomain names like `core_l3_clkdm`, `core_l4_clkdm`, `mpu_clkdm`, and `wkup_clkdm`.

Integration points: This is a shared data-provider file for OMAP2-family clockdomain registration. It also exports symbols declared in `clockdomain.h`.

Risks: Because the same arrays are reused by multiple SoC files, future SoC-specific divergence should not be added here unless valid for all users. Name mismatches fail late during dependency resolution.

Test signals: OMAP2420 and OMAP2430 boot logs should not warn about unresolved shared dependencies. Wakeup domain behavior while MPU is active validates the `CLKDM_ACTIVE_WITH_MPU` flag.
