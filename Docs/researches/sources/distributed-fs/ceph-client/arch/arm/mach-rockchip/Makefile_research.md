# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/Makefile

Purpose: object selection for Rockchip ARM machine support.

Important APIs/types/functions: forces `platsmp.o` to compile as ARMv7-A, builds `rockchip.o` under `CONFIG_ARCH_ROCKCHIP`, `pm.o sleep.o` under `CONFIG_PM_SLEEP`, and `headsmp.o platsmp.o` under `CONFIG_SMP`.

Control flow: make-time object inclusion only.

State and persistence: none.

Dependencies and integration points: links machine descriptor, suspend resume assembly, and SMP trampoline based on kernel config.

Risks: `platsmp.o` architecture flags must remain compatible with the assembly/register usage. PM sleep symbols are absent if `CONFIG_PM_SLEEP` is off, so callers use stubs.

Test signals: build matrix for Rockchip with SMP and PM_SLEEP combinations.
