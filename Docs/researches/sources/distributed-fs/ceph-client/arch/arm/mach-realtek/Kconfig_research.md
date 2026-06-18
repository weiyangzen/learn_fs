# sources/distributed-fs/ceph-client/arch/arm/mach-realtek/Kconfig

Purpose: Kconfig entry for Realtek RTD1195 ARM SoC support.

Important APIs/types/functions: `menuconfig ARCH_REALTEK` depends on `ARCH_MULTI_V7` and selects GIC, ARM global timer, global timer sched clock, generic IRQ chip, and reset controller.

Control flow: build-time platform selection only.

State and persistence: none locally; selected timer/IRQ/reset infrastructure affects runtime platform initialization.

Dependencies and integration points: enables `rtd1195.o` through the directory Makefile and supports DT machine matching in `rtd1195.c`.

Risks: broad selections must match SoC hardware; missing reset/timer/GIC dependencies would break early boot.

Test signals: ARM multi-v7 configuration builds and RTD1195 DT boot with timer and IRQ setup.
