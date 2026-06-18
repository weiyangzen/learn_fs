# sources/distributed-fs/ceph-client/arch/arm/mach-imx/mxc.h

Purpose: Shared private i.MX architecture helper header for CPU type tests, low-level read/write aliases, DDR type constant, and cross-file hooks.

Important APIs/types/functions: Defines `IMX_DDR_TYPE_LPDDR2`, inline `cpu_is_imx6*()` and `cpu_is_imx7d()` helpers, `struct cpu_op`, `tzic_enable_wake()`, external `get_cpu_op`, and `imx_readl/readw/writel/writew` aliases.

Control flow: No standalone runtime flow. The inline CPU tests compare `__mxc_cpu_type`; one helper is gated by `CONFIG_SOC_IMX6SL` to fold to false when unsupported.

State and persistence: No owned persistence. It exposes global CPU identification state from `soc/imx/cpu.h` and declares global hooks used by PM/frequency code.

Dependencies and integration points: Must be included through the guarded i.MX hardware header. Used by PM, IRQ, reset, and platform code that needs relaxed MMIO helpers or CPU-family branching.

Risks: The direct-include guard prevents misuse, but any stale `__mxc_cpu_type` classification changes PM register programming. Relaxed accessors need explicit ordering where hardware requires it.

Test signals: Compile coverage across i.MX6 variants; runtime validation comes from suspend, cpuidle, SMP boot, and TZIC wake behavior on the relevant SoCs.
