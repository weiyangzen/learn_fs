# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains54xx_data.c

Purpose: Defines OMAP54xx clockdomains and wake/sleep dependencies for CM_CORE_AON and CM_CORE based systems.

Important APIs/types/functions: Defines dependencies for C2C, CAM, DMA, DSP, DSS, GPU, IPU, IVA, L3INIT, L4SEC, MIPIEXT, and MPU. Defines domains such as L4SEC, IVA, MIPIEXT, L3MAIN1/2, CUSTEFUSE, IPU, L4CFG, ABE, DSS, DSP, C2C, L4PER, GPU, WKUPAON, MPU0/1/MPU, COREAON, L3INIT, DMA, L3INSTR, EMIF, EMU, and CAM. Provides `clockdomains_omap54xx[]` and `omap54xx_clockdomains_init()`.

Control flow: The init function registers OMAP4-style clockdomain operations, registers the OMAP54xx array, and completes setup. Dependency arrays are used by OMAP4-style static dependency operations.

State and persistence: Static descriptors store PRCM partition IDs and CM instance/offset data from `cm1_54xx.h` and `cm2_54xx.h`. Runtime save/restore uses OMAP4-style CLKSTCTRL context handling where available.

Dependencies: Includes OMAP54xx CM1/CM2 headers, OMAP54xx regbits, PRCM common headers, and clockdomain declarations. Powerdomain names must align with OMAP5 powerdomain data.

Integration points: Feeds the OMAP5 clockdomain framework and PM code with CM_CORE_AON/CM_CORE topology.

Risks: OMAP54xx has many interconnect and accelerator dependencies; missing a dependency can cause peripheral access latency or unsafe domain idling. Generated register macros should be updated via hardware database flow rather than hand edits.

Test signals: OMAP5 boot, accelerator/peripheral activity tests, and suspend/resume should validate dependency graph and CLKSTCTRL behavior for MPU, IPU, DSP, IVA, DSS, GPU, and L3INIT domains.
