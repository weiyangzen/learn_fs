# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm1_7xx.h

Purpose: Defines DRA7xx CM_CORE_AON base, register helper, instance offsets, and clockdomain offsets for always-on and accelerator domains.

Important APIs/types/functions: Provides `DRA7XX_CM_CORE_AON_BASE`, `DRA7XX_CM_CORE_AON_REGADDR()`, instances for OCP socket, CKGEN, MPU, DSP1, IPU, DSP2, EVE1-4, RTC, and VPE, and matching CDOFFS values.

Control flow: No executable flow. DRA7xx clockdomain data uses these macros to populate `cm_inst` and `clkdm_offs`.

State and persistence: No software state; hardware map definitions only.

Dependencies: Used by DRA7xx clockdomain data with OMAP4-style CM backend.

Integration points: Provides CM1 address layout for DRA7xx PM and clockdomain code.

Risks: Accelerator-heavy domains make offset errors costly and potentially device-specific. Generated-file workflow should be preserved for updates.

Test signals: DRA7xx boot plus DSP/IPU/EVE/RTC/VPE runtime PM and suspend/resume validation.
