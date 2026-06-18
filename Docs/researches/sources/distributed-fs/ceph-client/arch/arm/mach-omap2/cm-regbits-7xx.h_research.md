# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-7xx.h

Purpose: Defines DRA7xx static dependency bit shifts for clockdomain relationships.

Important APIs/types/functions: Provides `DRA7XX_*_STATDEP_SHIFT` macros for ATL, CAM, DSP1/2, DSS, EMIF, EVE1-4, GMAC, GPU, IPU/IPU1/IPU2, IVA, L3INIT, L3MAIN1, L4CFG, L4PER/L4PER2/L4PER3, L4SEC, PCIe, VPE, and WKUPAON.

Control flow: No executable flow. DRA7xx clockdomain data assigns these shifts to `dep_bit` fields, and OMAP4-style backend code uses them when manipulating STATICDEP registers.

State and persistence: No software state; hardware field definitions only.

Dependencies: Standalone generated header included by DRA7xx clockdomain data.

Integration points: Supports DRA7xx wake/sleep dependency programming across CPU, accelerator, media, networking, and interconnect domains.

Risks: A wrong shift can silently program the wrong dependency bit. Because DRA7xx has many accelerator domains, errors may surface only in specific device wake or suspend scenarios.

Test signals: DRA7xx runtime PM, suspend/resume, PCIe/GMAC/CAM/DSS/GPU/IPU/DSP/EVE activity tests, and dependency resolution warnings.
