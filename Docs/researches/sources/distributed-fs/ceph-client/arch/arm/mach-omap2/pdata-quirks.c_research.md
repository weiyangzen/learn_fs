# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pdata-quirks.c

## Purpose
`pdata-quirks.c` bridges Devicetree boot with legacy OMAP platform data and board-specific quirks. It supplies auxdata, clockdomain hooks, legacy GPIO setup, MMC names, IOMMU callbacks, SmartReflex data, McBSP data, PRM/sysc platform data, and board initialization callbacks that drivers still require.

## Important APIs, Types, and Functions
Key functions include `pdata_quirks_init()`, `pdata_quirks_init_clocks()`, `pdata_quirks_check()`, `omap_pcs_legacy_init()`, `ti_sysc_clkdm_init()`, `ti_sysc_clkdm_deny_idle()`, `ti_sysc_clkdm_allow_idle()`, and hwmod-backed `ti_sysc_enable_module()`, `ti_sysc_idle_module()`, and `ti_sysc_shutdown_module()`. Important data includes `omap_auxdata_lookup[]`, `auxdata_quirks[]`, `pdata_quirks[]`, `ti_sysc_pdata`, `ti_prm_pdata`, `pcs_pdata`, `mmc_pdata[]`, and `omap_sr_pdata[]`.

## Control Flow
Early DT platform init calls `pdata_quirks_init()`. It initializes SDRC for OMAP2420/OMAP3, optional McBSP pdata, runs auxdata quirks based on root compatible strings, populates PRCM/PRM nodes first, then calls `of_platform_populate()` for the full tree with auxdata. Finally it runs board-specific pdata quirks.

## State and Persistence Behavior
The file mutates platform data structures before device creation. It also writes control-module registers for MMC clock routing, pbias voltage, AM35xx EMAC reset/interrupt clearing, and may export GPIO descriptors for legacy board devices. These effects persist for the boot lifetime.

## Dependencies and Integration Points
It depends on OF platform population, GPIO descriptors, clockdomain/hwmod APIs, OMAP control registers, secure calls, hsmmc, IOMMU, SmartReflex, wkup_m3, McBSP, pinctrl-single, `ti-sysc`, and `ti-prm`. It is an integration hub for old board support such as N8x0, N900, Pandora, Compulab SBCs, AM3517 EVM, and OMAP3 EVM.

## Risks
This file can mask missing DT bindings by injecting platform data. Wrong compatible matching, auxdata addresses, or GPIO lookup tables can break board boot, device probe names, PM reset sequencing, or wakeups. Some quirks manipulate hardware directly before normal drivers own it.

## Test Signals
Boot affected boards or QEMU-equivalent configs and verify DT population order, named MMC devices, IOMMU reset callbacks, SmartReflex pdata, McBSP audio, USB hub reset GPIOs, AM35xx EMAC, and `ti-sysc` clockdomain idle hooks. Watch for probe-name regressions from auxdata changes.
