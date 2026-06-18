# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2_44xx.h

Purpose: Defines OMAP44xx CM2 base, register helper, CM2 instance offsets, and core/peripheral clockdomain offsets.

Important APIs/types/functions: Provides `OMAP4430_CM2_BASE`, `OMAP44XX_CM2_REGADDR()`, instances for OCP socket, CKGEN, ALWAYS_ON, CORE, IVAHD, CAM, DSS, GFX, L3INIT, L4PER, and CEFUSE, plus CDOFFS for ALWON, L3, Ducati, SDMA, MEMIF, D2D, L4CFG, L3INSTR, IVAHD, CAM, DSS, GFX, L3INIT, L4PER, L4SEC, and CEFUSE.

Control flow: No executable flow. Used as register-coordinate input to OMAP44xx clockdomain descriptors.

State and persistence: No software state; hardware address constants only.

Dependencies: Used with PRCM partition IDs and OMAP4 CM instance backend.

Integration points: Central to OMAP44xx CM2 domain control for core and peripheral domains.

Risks: CM2 covers many high-use peripherals; wrong offsets can cause broad device failures or register aborts.

Test signals: OMAP44xx boot and runtime PM for core interconnect, Ducati, IVAHD, DSS, GFX, L3INIT, L4PER, and CEFUSE.
