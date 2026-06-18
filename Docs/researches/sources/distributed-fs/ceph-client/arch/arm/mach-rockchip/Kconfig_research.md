# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/Kconfig

Purpose: Kconfig entry for Rockchip RK2928/RK3xxx ARMv7 SoCs.

Important APIs/types/functions: `ARCH_ROCKCHIP` depends on `ARCH_MULTI_V7` and selects pinctrl, reset controller, AMBA, GIC, L2X0, gpiolib, architected timer, SCU/TWD when SMP, DW APB timer, regulators, Rockchip timer, global timer sched clock, DMA zone for LPAE, and PM.

Control flow: build-time dependency selection; enables machine, PM, and SMP objects through Makefile.

State and persistence: none locally, but selected subsystems define early boot, interrupt, timer, pin, and suspend behavior.

Dependencies and integration points: targets DT-based Rockchip boards and supports `rockchip.c`, `platsmp.c`, and PM sleep code.

Risks: forced `PM` selection means suspend code is expected for this platform. Legacy ARM32 Rockchip support relies on many common subsystems being present.

Test signals: multi-v7 builds, DT boot for supported compatibles, SMP on A9/non-A9 variants, and suspend config builds.
