# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2_54xx.h

Purpose: Defines OMAP54xx CM_CORE base, register helper, CM_CORE instance offsets, and clockdomain offsets.

Important APIs/types/functions: Provides `OMAP54XX_CM_CORE_BASE`, `OMAP54XX_CM_CORE_REGADDR()`, instances for OCP socket, CKGEN, COREAON, CORE, IVA, CAM, DSS, GPU, L3INIT, and CUSTEFUSE, plus CDOFFS for L3MAIN1/2, IPU, DMA, EMIF, C2C, L4CFG, L3INSTR, MIPIEXT, L4PER, L4SEC, IVA, CAM, DSS, GPU, L3INIT, and CUSTEFUSE.

Control flow: No executable flow; consumed by OMAP54xx clockdomain data.

State and persistence: No software state.

Dependencies: Used with OMAP4-style partitioned CM access.

Integration points: Provides core CM address layout for OMAP5 clockdomain and PM code.

Risks: Incorrect generated offsets affect major interconnect and multimedia domains. Updates should track hardware database output.

Test signals: OMAP5 boot, module readiness waits, and runtime PM for IPU/DMA/EMIF/C2C/MIPIEXT/L4/L3/IVA/CAM/DSS/GPU/L3INIT.
