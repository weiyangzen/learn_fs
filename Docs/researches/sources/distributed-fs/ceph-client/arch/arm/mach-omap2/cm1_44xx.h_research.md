# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm1_44xx.h

Purpose: Defines OMAP44xx CM1 base, register address helper, CM1 instance offsets, and clockdomain offsets.

Important APIs/types/functions: Macros include `OMAP4430_CM1_BASE`, `OMAP44XX_CM1_REGADDR()`, CM1 instances for OCP socket, CKGEN, MPU, TESLA, and ABE, plus CDOFFS for MPU, TESLA, and ABE clockdomains.

Control flow: No executable flow. Static clockdomain data uses instance and CDOFFS macros; OMAP4 register code combines them with partition bases.

State and persistence: No software state; hardware address definitions only.

Dependencies: Uses `OMAP2_L4_IO_ADDRESS` from included platform address infrastructure through users.

Integration points: Used by OMAP44xx clockdomain data and OMAP4 CM instance backend.

Risks: Generated comments note naming alignment issues. Wrong base/offset values make partitioned CM access hit incorrect registers.

Test signals: OMAP44xx boot, ABE/Tesla/MPU clockdomain transitions, and no OMAP4 CM BUG_ON during register access.
