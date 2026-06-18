# sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/Makefile

Purpose: build rules for BCM1480/BCM1x80 SoC support.

Important APIs and control flow: always builds `setup.o`, `irq.o`, and `time.o`; adds `smp.o` when `CONFIG_SMP` is enabled.

State, persistence, and integration: no runtime state; this selects SoC identification, interrupt routing, timer setup, and optional SMP operations. Dependencies include BCM1x80 Kconfig and common CFE support. Risks are no SMP secondary support if `smp.o` is omitted for SMP hardware. Test signals are expected object inclusion and symbols such as `bcm1480_smp_ops`.
