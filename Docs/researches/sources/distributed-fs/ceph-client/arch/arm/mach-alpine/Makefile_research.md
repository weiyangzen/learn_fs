# sources/distributed-fs/ceph-client/arch/arm/mach-alpine/Makefile

Purpose: builds Alpine machine support. `alpine_machine.o` is always built for the platform, while `platsmp.o` and `alpine_cpu_pm.o` are added for SMP.

Control flow is build-time only. Integration depends on Kconfig and the CPU method used by Alpine DT. Risks are leaving CPU PM out of SMP builds, which would break secondary wakeup. Test signals are successful ARCH_ALPINE SMP and non-SMP links.
