# sources/distributed-fs/ceph-client/drivers/sh/intc/Makefile

Purpose: Kbuild object list for the SuperH INTC framework.

Important build rules: base objects are `access.o`, `chip.o`, `core.o`, `handle.o`, `irqdomain.o`, and `virq.o`. Optional objects are `balancing.o` for `CONFIG_INTC_BALANCING`, `userimask.o` for `CONFIG_INTC_USERIMASK`, and `virq-debugfs.o` for `CONFIG_INTC_MAPPING_DEBUG`.

Control flow: the base objects collectively implement register access, handle encoding, irq-chip operations, controller registration, irqdomain setup, and virtual subgroup IRQs. Optional objects extend hooks compiled into the base through stubs in `internals.h`.

State and dependencies: no runtime state in the Makefile. Dependencies are the Kconfig symbols and internal symbol references between objects. Risks include missing an optional object when stubs are not sufficient and link failures if feature guards diverge. Test signals are link success for every symbol combination and boot tests for base INTC with optional features enabled/disabled.
