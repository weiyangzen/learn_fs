# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm44xx.h

Purpose: Provides common OMAP4+ CM definitions shared by CM1/CM2 layouts and declares OMAP4 CM initialization.

Important APIs/types/functions: Defines `OMAP4_CM_CLKSTCTRL`, `OMAP4_CM_STATICDEP`, and `omap4_cm_init()`.

Control flow: No executable flow. `cminst44xx.c` uses the register offsets for CLKSTCTRL and STATICDEP access.

State and persistence: No software state.

Dependencies: Includes `prcm-common.h` and `cm.h`.

Integration points: Shared by OMAP4, OMAP5, DRA7xx, and AM43xx partitioned CM code.

Risks: These offsets are assumed by all OMAP4-style clockdomain data. Incorrect values would break all CLKSTCTRL and dependency operations.

Test signals: OMAP4-style SoC boot and runtime PM operations.
