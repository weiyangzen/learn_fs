# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains81xx_data.c

Purpose: Defines TI814x and TI816x clockdomains using the AM33xx-style CM backend and TI81xx-specific CM offsets.

Important APIs/types/functions: Defines common TI81xx ALWON/default/MMU domains and TI816x-specific MPU, GEM, IVAHD0-2, SGX, default L3 medium, Ducati, and PCI domains. Provides separate arrays `clockdomains_ti814x[]` and `clockdomains_ti816x[]`, with init functions `ti814x_clockdomains_init()` and `ti816x_clockdomains_init()`.

Control flow: Each init function registers `am33xx_clkdm_operations`, registers the appropriate SoC-specific array, and completes initialization.

State and persistence: Descriptors store TI81xx CM module offsets in `cm_inst` and clockdomain offsets in `clkdm_offs`. Runtime state is handled through the AM33xx CM register model.

Dependencies: Includes `cm81xx.h`, `cm-regbits-33xx.h`, `prcm-common.h`, and `clockdomain.h`. Requires TI814x/TI816x powerdomain names such as `alwon_pwrdm`, `default_pwrdm`, `active_pwrdm`, `ivahd*_pwrdm`, and `sgx_pwrdm`.

Integration points: Supports DM814/DM816 platform clockdomain registration and reuses the AM33xx operation table for CLKSTCTRL control.

Risks: TI814x and TI816x arrays share several descriptors but differ in included domains; wrong init selection would expose unavailable domains or omit needed ones. Offset reuse such as ALWON L3 medium/Ethernet requires careful hardware validation.

Test signals: DM814/DM816 boot should register the correct array. Ethernet, SATA, Ducati, IVAHD, SGX, and PCI activity are useful domain-specific checks.
