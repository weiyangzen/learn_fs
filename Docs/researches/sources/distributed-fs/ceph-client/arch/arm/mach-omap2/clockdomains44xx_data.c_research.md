# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains44xx_data.c

Purpose: Defines OMAP44xx clockdomain topology, static dependency relationships, and the OMAP44xx clockdomain init sequence.

Important APIs/types/functions: Provides wake/sleep dependency arrays for D2D, Ducati, ISS, IVAHD, L3 DMA, DSS, GFX, L3INIT, L4 secure, MPU, and Tesla. Defines clockdomains for CEFUSE, L4 CFG, Tesla, GFX, IVAHD, L4 secure/per, ABE, L3 instr/init/emif/dma/DSS, D2D, MPU0/MPU1/MPU, L4 AO/WKUP, Ducati, L3_1/L3_2, ISS, and EMU. Provides `clockdomains_omap44xx[]` and `omap44xx_clockdomains_init()`.

Control flow: `omap44xx_clockdomains_init()` registers `omap4_clkdm_operations`, registers the OMAP44xx descriptor array, and completes initialization. Static dependency arrays are resolved into `OMAP4_CM_STATICDEP` bit operations by the backend.

State and persistence: Domain descriptors carry OMAP4 PRCM partition, CM instance, clockdomain offset, dependency bit, flags, and optional dependency arrays. Runtime context stores CLKSTCTRL state through `omap4_clkdm_save_context()`.

Dependencies: Includes OMAP4 CM1/CM2, CM regbits, PRCM partition headers, and clockdomain declarations. Depends on powerdomain data for MPU, ABE, core, IVAHD, CAM, DSS, GFX, L3INIT, L4PER, CEFUSE, and wakeup domains.

Integration points: Used by OMAP4 platform initialization and OMAP4 PM/hwmod code. Integrates with `cminst44xx.c` for partitioned register reads/writes and static dependency manipulation.

Risks: Static dependency bit mappings must match hardware `STATDEP` fields. The large dependency graph is sensitive to missing names and can affect wake latency or prevent low-power entry. Partitioned register access will BUG on invalid base setup.

Test signals: OMAP44xx boot should register all domains and resolve dependencies. Device tests for Ducati, DSS, GFX, IVAHD, L3INIT USB, and suspend/resume exercise the topology.
