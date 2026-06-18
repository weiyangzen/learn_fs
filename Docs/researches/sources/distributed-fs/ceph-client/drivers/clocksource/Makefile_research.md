# sources/distributed-fs/ceph-client/drivers/clocksource/Makefile

Purpose: maps clocksource Kconfig symbols to object files in `drivers/clocksource`.

Important APIs/types/functions: Kbuild entries include infrastructure (`timer-of.o`, `timer-probe.o`, `mmio.o`), legacy devices (`i8253.o`), ARM timers, DesignWare APB timers, Hyper-V, Exynos MCT, Ingenic timers, and numerous SoC-specific timer objects.

Control flow: Kbuild evaluates each `obj-$(CONFIG_...)` assignment and links the selected objects into built-in kernel code or modules as dictated by configuration.

State and persistence: no runtime state; it persists the compile/link graph.

Dependencies and integration points: paired with `Kconfig` symbols and each driver’s `TIMER_OF_DECLARE`, platform driver, or arch initcall entry point.

Risks: missing or stale symbol/object mappings break driver inclusion. Some objects depend on headers and architecture facilities not evident from this file, so compile-test remains important.

Test signals: targeted `make drivers/clocksource/`, broad randconfig builds, and symbol-to-object audits against `Kconfig`.
