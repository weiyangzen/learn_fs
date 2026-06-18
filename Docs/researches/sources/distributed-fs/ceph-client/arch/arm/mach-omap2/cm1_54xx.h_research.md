# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm1_54xx.h

Purpose: Defines OMAP54xx CM_CORE_AON base, register helper, always-on CM instances, and clockdomain offsets.

Important APIs/types/functions: Provides `OMAP54XX_CM_CORE_AON_BASE`, `OMAP54XX_CM_CORE_AON_REGADDR()`, instances for OCP socket, CKGEN, MPU, DSP, and ABE, and CDOFFS for MPU, DSP, and ABE.

Control flow: No executable flow; consumed by OMAP54xx static clockdomain data.

State and persistence: No software state. The macros describe persistent hardware register addresses.

Dependencies: Used with OMAP2 L4 IO address mapping and OMAP4-style CM partition access.

Integration points: Enables OMAP5 CM_CORE_AON domain registration and register access.

Risks: Wrong always-on CM offsets can break MPU/DSP/ABE clockdomain management and suspend/resume.

Test signals: OMAP5 boot and runtime PM for MPU, DSP, and ABE domains.
