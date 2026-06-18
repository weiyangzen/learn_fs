# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2_7xx.h

Purpose: Defines DRA7xx CM_CORE base, register helper, CM_CORE instance offsets, and clockdomain offsets.

Important APIs/types/functions: Provides `DRA7XX_CM_CORE_BASE`, `DRA7XX_CM_CORE_REGADDR()`, instances for OCP socket, CKGEN, COREAON, CORE, IVA, CAM, DSS, GPU, L3INIT, CUSTEFUSE, and L4PER. Defines CDOFFS for L3MAIN1, IPU2, DMA, EMIF, ATL, L4CFG, L3INSTR, IVA, CAM, DSS, GPU, L3INIT, PCIe, GMAC, CUSTEFUSE, L4PER, L4SEC, L4PER2, and L4PER3.

Control flow: No executable flow. DRA7xx clockdomain descriptors use these offsets.

State and persistence: No software state; hardware register map only.

Dependencies: Used with DRA7xx regbits and OMAP4-style CM backend.

Integration points: Supports DRA7xx CM2/core domain control for interconnect, media, networking, PCIe, and peripheral blocks.

Risks: The CKGEN instance offset differs from simpler OMAP5 layout (`0x0104`), so copy-paste from other families is unsafe. Wrong CDOFFS values can affect only one accelerator path and be hard to diagnose.

Test signals: DRA7xx boot and runtime PM across PCIe, GMAC, ATL, L4PER2/3, GPU, DSS, CAM, and IVA domains.
