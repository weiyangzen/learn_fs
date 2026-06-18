# sources/distributed-fs/ceph-client/drivers/sh/intc/Kconfig

Purpose: configuration for the SuperH interrupt controller framework and optional features.

Important symbols: `SH_INTC` is a bool that selects `IRQ_DOMAIN`. Under it, `INTC_USERIMASK` enables userspace interrupt masking for SH-4A or COMPILE_TEST, `INTC_BALANCING` enables hardware IRQ auto-distribution for SH-X3 SMP, and `INTC_MAPPING_DEBUG` exposes irq-to-controller enum mappings through debugfs.

Control flow: Kconfig gates compilation of optional `userimask.o`, `balancing.o`, and `virq-debugfs.o` through the Makefile. The base INTC framework is built when the architecture selects `SH_INTC`.

State and dependencies: no runtime state here. Dependencies include architecture CPU symbols, SMP, DEBUG_FS, and IRQ_DOMAIN. Risks are allowing options on hardware that lacks support or excluding useful COMPILE_TEST coverage. Test signals are Kconfig dependency resolution, allmodconfig coverage, and expected object selection for each symbol.
