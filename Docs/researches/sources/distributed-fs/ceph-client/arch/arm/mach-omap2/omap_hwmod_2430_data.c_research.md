# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_2430_data.c

Purpose: Provides OMAP2430-specific hwmod integration data and the `omap2430_hwmod_init()` registration entry point. It describes the OMAP2430 additions and differences relative to common OMAP2 data, especially IVA2, high-speed I2C, USB OTG, extra McBSPs, MMC/SD/SDIO, GPIO5, and McSPI3.

Important descriptors: the file defines an IVA module using the shared IVA class with logic/MMU reset lines, I2C1/I2C2 with 16-bit registers and high-speed clock names, GPIO5 with optional clocks controlled during reset, mailbox, McSPI3, USB HS OTG with rich SYSCONFIG idlemode data and erratum-driven software idle/standby flags, McBSP1-5 with shared optional clocks, MMC1/MMC2 with dbck optional clocks and HSMMC dev attributes, and HDQ1W. OCP links cover USB as both an L3 initiator and an L4 CORE target, L4 CORE access to I2C/MMC/McSPI/McBSP/GPIO5/mailbox/HDQ, L3 access to IVA and GPMC, and L4 WKUP access to watchdog/GPIO1-4.

Control flow: `omap2430_hwmod_init()` initializes the hwmod core and registers `omap2430_hwmod_ocp_ifs`. The array includes common OMAP2 interconnects, DSS, UARTs, timers, crypto, McSPI1/2, and then the 2430-specific peripherals. The core later resolves clock names such as `i2chs*_fck`, `usb_l4_ick`, `mmchs*_ick`, `mcbsp*_ick`, and PRCM IDLEST bits.

State and persistence: descriptor state is static; runtime state is produced by `omap_hwmod.c` after registration. USB HS OTG is configured with `HWMOD_NO_OCP_AUTOIDLE`, `HWMOD_SWSUP_SIDLE`, and `HWMOD_SWSUP_MSTANDBY`, so the core avoids problematic automatic idle/standby behavior. MMC modules carry optional debounce/32k-style clocks during reset. I2C modules select 16-bit MMIO access. IVA reset lines are exposed for driver-controlled hardreset behavior.

Dependencies and integration: includes OMAP24xx PRM/CM bit definitions, common OMAP2 data, HSMMC platform data, I2C reset code, watchdog integration, and the common L3 descriptor. It integrates with legacy `ti,hwmods` DT matching and platform data attributes for HSMMC voltage support.

Risks: comments note I2CHS PRCM enable registers do not follow the usual pattern, so future clock handling changes can break I2C readiness if they rely only on the generic PRCM fields. USB OTG has an erratum (`i479`) requiring OCP autoidle disable and software-supervised idle/standby; changing these flags risks deadlocks or broken idle acknowledgements. MMC optional clocks and dev attributes must match board voltage capabilities. OCP links with `OCP_USER_MPU` only for USB may affect sleep dependency behavior compared with MPU+SDMA peripherals.

Test signals: boot OMAP2430 and check for clock lookup and IDLEST wait warnings for I2C, USB, MMC, McSPI3, McBSPs, and GPIO5. Runtime tests should exercise USB OTG suspend/resume and idle transitions, MMC1 dual-voltage operation, I2C transfers across idle, IVA hardreset control, and DSS/crypto/timer modules inherited from common OMAP2 data.
