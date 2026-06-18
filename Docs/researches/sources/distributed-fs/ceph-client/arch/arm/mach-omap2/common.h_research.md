# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common.h

Purpose: Aggregates common OMAP2+ machine declarations, configuration-dependent stubs, early/late init hooks, PM hooks, restart hooks, MMIO mapping hooks, low-level SMP/CPU idle helpers, and the `omap_test_timeout()` polling macro.

Important APIs/types/functions: Declares PM init functions, L2 cache helpers, SoC early/late init functions, restart functions, barrier reservation/init, map_io functions, GIC helpers, SCU/L2/SAR/MPUSS helpers, SMP ops, low-power CPU entry functions, auxdata/PCS legacy hooks, SDRC init, `omap_reserve()`, DSS reset, clock init, and IOMMU powerdomain constraints. Defines `OMAP_INTC_START`, `OMAP_L2C_AUX_CTRL`, and `omap_test_timeout()`.

Control flow: Header only. Many declarations are selected by Kconfig with inline no-op fallbacks, allowing common call sites to compile across SoCs. `omap_test_timeout()` expands into a microsecond polling loop used by CM backends.

State and persistence: No direct state, but declares many platform state providers and low-power entry functions. The timeout macro is stack-local at call sites.

Dependencies: Linux IRQ, delay, I2C, TWL, reboot, OMAP INTC, ARM cache/proc headers, and local I2C/platform declarations.

Integration points: Broad OMAP2+ platform integration header used across init, PM, SMP, cache, device, clock, and reset code. In this subset, CM backends depend on `omap_test_timeout()`.

Risks: Because it exposes many conditional no-op stubs, build success does not guarantee runtime feature availability. Timeout polling is busy-wait based and depends on correct timeout values and `udelay()`.

Test signals: Multi-SoC build matrix, boot through early/late init, restart, suspend/resume, SMP bringup, and CM wait loops.
