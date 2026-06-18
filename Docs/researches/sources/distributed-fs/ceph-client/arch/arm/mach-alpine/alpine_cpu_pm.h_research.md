# sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_cpu_pm.h

Purpose: declares Alpine CPU PM interfaces `alpine_cpu_pm_init` and `alpine_cpu_wakeup`.

Control flow and state are implemented in `alpine_cpu_pm.c`; this header defines the integration contract consumed by `platsmp.c`. Dependencies are `uint32_t` availability through including C files and `__init` annotation context. Risks are signature drift between the header and implementation. Test signals are compile coverage for SMP Alpine builds.
