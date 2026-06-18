# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_81xx_data.c

## Purpose
`omap_hwmod_81xx_data.c` describes DM814x/DM816x hardware modules and OCP interconnect links for the legacy OMAP hwmod layer. It maps MPU, L3/L4 buses, UART, watchdog, I2C, ELM, GPIO, GPMC, USB OTG, timers, EMAC/MDIO, SATA, MMC, McSPI, mailbox, and spinbox modules to clockdomains, main clocks, PRCM clock-control offsets, sysconfig layouts, and reset hooks.

## Important APIs, Types, and Functions
The main data types are `struct omap_hwmod`, `struct omap_hwmod_class`, `struct omap_hwmod_class_sysconfig`, `struct omap_hwmod_ocp_if`, `struct omap_hwmod_opt_clk`, and `struct omap_hsmmc_dev_attr`. Entry points are `dm814x_hwmod_init()` and `dm816x_hwmod_init()`, both calling `omap_hwmod_init()` and `omap_hwmod_register_links()`. Important arrays are `dm814x_hwmod_ocp_ifs[]` and `dm816x_hwmod_ocp_ifs[]`.

## Control Flow
Board/SoC init selects the DM814x or DM816x init function. That function initializes hwmod core state, then registers the static OCP link array. Registration pulls in both endpoint hwmods, their class sysconfig metadata, PRCM offsets, module modes, and optional clocks. The hwmod layer later uses this metadata for reset, enable, idle, shutdown, and device instantiation paths.

## State and Persistence Behavior
The file contains static boot-time descriptors, not runtime persistence. Runtime state is held by the hwmod framework, clock framework, PRCM registers, and devices created from DT or auxdata. The descriptor flags matter because they influence whether modules start active, can be idled, have reset status, or skip idlest checks.

## Dependencies and Integration Points
It depends on `omap_hwmod_common_data.h`, `cm81xx.h`, `ti81xx.h`, `wd_timer.h`, and MMC platform data. It integrates with PRCM clockctrl registers, clockdomains such as `alwon_l3s_clkdm`, `default_l3_slow_clkdm`, and `alwon_ethernet_clkdm`, and with drivers consuming hwmod names like `uart1`, `gpio1`, `mmc1`, `davinci_mdio`, and `usb_otg_hs`.

## Risks
The biggest risk is incorrect hardware metadata: a wrong `clkctrl_offs`, `main_clk`, clockdomain, sysconfig offset, reset delay, or shared clock-control assumption can hang boot, break probe, prevent idle, or corrupt wakeup behavior. DM81xx coverage is explicitly incomplete and not generated from the hardware database, so edits require TRM checks and board testing.

## Test Signals
Build with TI81xx/DM814x/DM816x configs and boot on affected boards. Watch for successful registration/probe of UART, MMC, GPIO, GPMC, MDIO/EMAC, SATA, USB, and timers, clean hwmod reset logs, no idlest timeout warnings, and correct suspend/idle behavior. Targeted validation includes enabling/disabling each registered module and checking PRCM clockctrl transitions.
