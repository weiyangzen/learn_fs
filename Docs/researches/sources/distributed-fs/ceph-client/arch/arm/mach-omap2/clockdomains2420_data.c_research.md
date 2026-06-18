# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains2420_data.c

Purpose: Provides OMAP242x-specific static clockdomain descriptors and wake dependency data, then registers them with the generic clockdomain framework.

Important APIs/types/functions: Defines `mpu_2420_wkdeps`, `core_2420_wkdeps`, and clockdomains for `mpu`, `iva1`, `dsp`, `gfx`, `core_l3`, `core_l4`, and `dss`, plus the `clockdomains_omap242x[]` array and `omap242x_clockdomains_init()`.

Control flow: `omap242x_clockdomains_init()` registers `omap2_clkdm_operations`, registers the OMAP242x clockdomain array, and calls `clkdm_complete_init()`. The common `wkup_common_clkdm` comes from `clockdomains2xxx_3xxx_data.c`.

State and persistence: The descriptors are static `__initdata` inputs to boot-time registration; runtime state is stored in the registered `struct clockdomain` objects and OMAP24xx CM registers. Wake dependencies are resolved by name at completion time.

Dependencies: Includes `soc.h`, `clockdomain.h`, PRM module definitions, and 24xx CM register bit definitions. The descriptors depend on matching powerdomain names such as `mpu_pwrdm`, `dsp_pwrdm`, `gfx_pwrdm`, and `core_pwrdm`.

Integration points: Feeds the generic clockdomain framework for OMAP2420 systems and uses the OMAP2 CM backend from `cm2xxx.c` for CLKSTCTRL and wake dependency operations.

Risks: Static dependency names must exactly match registered clockdomain names. Several domains have hardware-supervised-only flags, so incorrect flags can block software sleep/wakeup. The OMAP2420 IVA/DSP split relies on hardware-specific dependency bits.

Test signals: OMAP2420 boot should show successful registration, dependency resolution, and no missing powerdomain errors. Functional clock gating, MPU retention checks, and wake from DSP/GFX/core activity exercise the table.
