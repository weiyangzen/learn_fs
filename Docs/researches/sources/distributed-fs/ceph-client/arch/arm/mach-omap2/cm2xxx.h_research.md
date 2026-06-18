# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2xxx.h

Purpose: Declares OMAP2xxx CM address macros, OMAP2-specific register offsets, IDLEST polarity value, and public OMAP2 CM helpers.

Important APIs/types/functions: Provides `OMAP2420_CM_REGADDR()`, `OMAP2430_CM_REGADDR()`, offsets for `OMAP24XX_CM_FCLKEN2`, `OMAP24XX_CM_ICLKEN4`, `OMAP24XX_CM_AUTOIDLE4`, `OMAP24XX_CM_IDLEST4`, `OMAP24XX_CM_IDLEST_VAL`, and prototypes for OMAP2 DPLL/clock/retention/divider helpers plus `omap2xxx_cm_init()`.

Control flow: No executable flow beyond macro expansion and inline inclusion from shared `cm2xxx_3xxx.h`.

State and persistence: No software state; maps hardware offsets and declares functions implemented in `cm2xxx.c`.

Dependencies: Includes `prcm-common.h` and shared OMAP2/3 CM definitions.

Integration points: Used by OMAP2 CM backend, clock code, and PM code that needs OMAP2-specific CM helpers.

Risks: Address macros must be used with the correct OMAP2420 vs OMAP2430 base. `OMAP24XX_CM_IDLEST_VAL` differs from OMAP3 and is important for readiness logic.

Test signals: OMAP2 builds and runtime CM IDLEST polling, DPLL autoidle, and divider programming.
