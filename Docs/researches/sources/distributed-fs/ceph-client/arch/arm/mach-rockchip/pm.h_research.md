# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/pm.h

Purpose: Rockchip PM declarations and RK3288 PMU/SGRF register constants shared by C and assembly-adjacent code.

Important APIs/types/functions: declares `rockchip_slp_cpu_resume()` and `rockchip_suspend_init()` when `CONFIG_PM_SLEEP` is enabled, otherwise provides a stub. Defines RK3288 PMU wake/power/count registers, SGRF fast boot and watchdog gate bits, CPU debug bits, and wakeup enable masks.

Control flow: no runtime flow except the inline stub controlling whether `rockchip.c` calls real suspend setup.

State and persistence: constants address hardware PM registers whose contents persist across low-power entry until restored.

Dependencies and integration points: included by `pm.c`, `rockchip.c`, and resume assembly declarations.

Risks: write-mask bit definitions are easy to misuse; bad constants can prevent resume or leave watchdog/debug gates altered.

Test signals: compile with/without PM_SLEEP, suspend register programming tests, and resume path symbol linkage.
