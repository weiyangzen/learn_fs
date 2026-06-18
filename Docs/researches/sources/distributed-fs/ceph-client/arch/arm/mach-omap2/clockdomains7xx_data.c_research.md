# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains7xx_data.c

Purpose: Defines DRA7xx clockdomain topology, including DSP, EVE, IPU, IVA, GPU, display, camera, PCIe, GMAC, and interconnect domains.

Important APIs/types/functions: Provides many wake/sleep dependency arrays for CAM, DMA, DSP1/2, DSS, EVE1-4, GMAC, GPU, IPU1/2, IVA, L3INIT, L4PER2, L4SEC, MPU, PCIe, and VPE. Defines clockdomains for L4PER2/3, MPU0/1/MPU, IVA, COREAON, IPU/IPU1/IPU2, L3INIT, L4SEC, L3MAIN1, VPE, CUSTEFUSE, GMAC, L4CFG, DMA, RTC, PCIe, ATL, L3INSTR, DSS, EMIF, EMU, DSP1/2, CAM, L4PER, GPU, EVE1-4, and WKUPAON. Provides `clockdomains_dra7xx[]` and `dra7xx_clockdomains_init()`.

Control flow: Initialization registers `omap4_clkdm_operations`, registers all DRA7xx domains, and completes generic setup. The OMAP4-style backend writes CLKSTCTRL and STATICDEP fields via CM_CORE_AON/CM_CORE partitions.

State and persistence: Descriptors are static and source generated. Mutable state is in generic `struct clockdomain` fields and DRA7xx CM registers. Dependency arrays resolve to pointers and usecounts after init.

Dependencies: Includes DRA7xx CM1/CM2 headers, DRA7xx regbits, PRCM common headers, and clockdomain APIs. Depends on DRA7xx powerdomain definitions matching the descriptor names.

Integration points: Used by DRA7 platform PM and hwmod/clock operations; its broad accelerator topology is central to low-power behavior on Jacinto/DRA7 devices.

Risks: This is the largest dependency graph in the subset. Generated offsets and STATDEP bits must remain synchronized with hardware data. Missing EVE/DSP/IPU/PCIe/GMAC dependencies may cause wake failures or block retention/off modes.

Test signals: DRA7 boot plus driver activity across display, camera, PCIe, GMAC, IPU, DSP, and EVE blocks. Suspend/resume and runtime PM should verify no unresolved dependency warnings or CM timeouts.
