# sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-io.h

Purpose: This OMAP1 header provides legacy physical-address register access helpers and register base/offset constants for clock, mux, ULPD, DSP, PWL, and control blocks.

Important APIs/types/functions: On ARM it declares `omap_readb/readw/readl` and `omap_writeb/writew/writel`; non-ARM stubs return zero/no-op. It defines constants for module config, ULPD registers, clock generator, DPLL, DSP config, pulse-width light, function mux, pull-down, and pull-up/down select registers.

Control flow: Legacy OMAP1 platform and drivers use these helpers to read/write physical SoC registers directly during early init, clock setup, muxing, and suspend/resume.

State and persistence: Register writes configure clocks, muxing, power, and DSP control until changed or reset.

Dependencies and integration: Integrates with OMAP1 ARM platform code, mux, clock, USB, and board support.

Risks and test signals: Direct physical register access is fragile and bypasses modern abstractions. Test ARM/non-ARM compile paths, early boot, clock setup, mux programming, and suspend/resume register retention.
