# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-24xx.h

Purpose: Defines OMAP24xx Clock Management bit masks and shifts used by OMAP2 CM code and static clockdomain data.

Important APIs/types/functions: Provides masks/shifts for OMAP24xx autostate, functional clock enable/status fields, APLL/DPLL autoidle fields, core clock source, and CLKSTCTRL automatic mode values `OMAP24XX_CLKSTCTRL_DISABLE_AUTO` and `OMAP24XX_CLKSTCTRL_ENABLE_AUTO`.

Control flow: This header has no executable flow. Its macros are consumed by `cm2xxx.c`, `cm2xxx.h`, and OMAP2420/2430 clockdomain data to compose register reads/writes and dependency bits.

State and persistence: No software state. It describes persistent hardware register bit positions in the OMAP24xx CM block.

Dependencies: Standalone guarded header; included by OMAP2-specific CM and clockdomain files.

Integration points: Supports DPLL/APLL autoidle control, module status polling, DSS/UART/MMC/McSPI retention gating checks, and OMAP24xx CLKSTCTRL hardware-supervision toggling.

Risks: Bit definitions are hardware contracts; incorrect masks can break clock enable status, retention decisions, and PLL autoidle. Some macros are SoC-specific to OMAP2420 or OMAP2430 and should not be used interchangeably.

Test signals: OMAP2420/2430 compile coverage and runtime checks for DPLL autoidle, module readiness, MPU retention allowed logic, and clockdomain auto mode.
