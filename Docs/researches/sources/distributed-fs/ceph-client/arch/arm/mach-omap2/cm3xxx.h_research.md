# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm3xxx.h

Purpose: Defines OMAP3 CM address helper, OMAP3-specific CM register offsets, IDLEST value, context function prototypes, and OMAP3 CM init prototype.

Important APIs/types/functions: Provides `OMAP34XX_CM_REGADDR()`, global offsets like `OMAP3430_CM_SYSCONFIG`, `OMAP3430_CM_POLCTRL`, `OMAP3_CM_CLKOUT_CTRL_OFFSET`, OMAP3 PLL/CLKEN/CLKSEL/SLEEPDEP/CLKSTST offsets, `OMAP34XX_CM_IDLEST_VAL`, and prototypes for OMAP3 context save/restore/scratchpad and `omap3xxx_cm_init()`.

Control flow: No executable flow; macros are consumed by `cm3xxx.c` and related clock/PM code.

State and persistence: No software state in header; declares context functions implemented in `cm3xxx.c`.

Dependencies: Includes `prcm-common.h` and shared OMAP2/3 CM definitions.

Integration points: OMAP3 CM backend, PM resume code, and clock initialization.

Risks: Several register offsets alias common offsets with OMAP3-specific meanings. Silicon revision differences are handled elsewhere, so callers must choose appropriate macros.

Test signals: OMAP3 build and resume tests covering CM context and scratchpad handling.
