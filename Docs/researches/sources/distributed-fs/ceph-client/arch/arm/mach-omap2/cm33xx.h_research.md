# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm33xx.h

Purpose: Defines AM33xx CM base address, register address helper, CM instance offsets, selected CLKSTCTRL/CLKCTRL register offsets, and the AM33xx CM init prototype.

Important APIs/types/functions: Provides `AM33XX_CM_BASE`, `AM33XX_CM_REGADDR()`, instances for PER, WKUP, DPLL, MPU, DEVICE, RTC, GFX, and CEFUSE, plus offsets for L4LS, L3S, L4FW, L3, EMIF, L4HS, OCPWP, PRUSS, CPSW, LCDC, 24MHz, WKUP, L3 AON, L4 WKUP AON, GFX, RTC, and CEFUSE registers.

Control flow: No executable flow; macros feed static data and AM33xx CM backend register calculations.

State and persistence: No software state; hardware address map only.

Dependencies: Includes `cm.h`, `cm-regbits-33xx.h`, and `prcm-common.h`.

Integration points: Used by `cm33xx.c` and `clockdomains33xx_data.c`.

Risks: The file only lists selected registers needed by this code. Adding new domains/modules requires matching offsets from hardware data.

Test signals: AM33xx compile and boot, especially peripherals mapped through the listed offsets.
