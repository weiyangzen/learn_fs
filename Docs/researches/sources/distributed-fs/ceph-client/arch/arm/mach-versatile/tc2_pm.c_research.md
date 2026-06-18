# sources/distributed-fs/ceph-client/arch/arm/mach-versatile/tc2_pm.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-versatile/tc2_pm.c` provides platform power-management code for ARM Integrator, RealView, Versatile, and Versatile Express platform support. It is part of the board-support layer that bridges generic ARM kernel code to SoC-specific registers, firmware conventions, and Devicetree-described devices.

## Important APIs, Types, and Functions
Important functions and entry points are `tc2_pm_cpu_powerup`, `tc2_pm_cluster_powerup`, `tc2_pm_cpu_powerdown_prepare`, `tc2_pm_cluster_powerdown_prepare`, `tc2_pm_cpu_cache_disable`, `tc2_pm_cluster_cache_disable`, `tc2_core_in_reset`, `tc2_pm_wait_for_powerdown`, `tc2_pm_cpu_suspend_prepare`, `tc2_pm_cpu_is_up`, `tc2_pm_cluster_is_up`, `tc2_pm_power_up_setup`, `tc2_pm_init`. Important structs/types referenced or defined are `mcpm_platform_ops`, `device_node`. File-scope platform state and tables include `tc2_pm_power_ops`, `mask`. Preprocessor/register symbols defined here include `RESET_CTRL`, `RESET_A15_NCORERESET`, `RESET_A7_NCORERESET`, `A15_CONF`, `A7_CONF`, `SYS_INFO`, `SPC_BASE`, `TC2_CLUSTERS`, `TC2_MAX_CPUS_PER_CLUSTER`, `POLL_MSEC`, `TIMEOUT_MSEC`. Machine descriptors are none; OF compatible strings visible in the file are none. Headers imported by the file include `linux/delay.h`, `linux/init.h`, `linux/io.h`, `linux/kernel.h`, `linux/of_address.h`, `linux/of_irq.h`, `linux/errno.h`, `linux/irqchip/arm-gic.h`, `asm/mcpm.h`, `asm/proc-fns.h`, `asm/cacheflush.h`, `asm/cputype.h`, `asm/cp15.h`, `linux/arm-cci.h`, `spc.h`

## Control Flow
Power-management flow is entered from suspend, cpuidle, MCPM, or platform late-init hooks. The code maps controller registers, saves state needed across low-power entry, programs wake or reset vectors, disables caches/SCU where needed, and restores hardware state on resume before generic kernel execution continues.

## State and Persistence Behavior
Persistent storage is not used. Runtime state is kept in file-scope mappings, flags, tables, or hardware registers such as `tc2_pm_power_ops`, `mask`. The durable contract is the DT ABI, Kconfig/Kbuild selection, and register programming sequence expected by firmware and the SoC; hardware register contents may persist across warm reset or low-power states even though the kernel does not write files.

## Dependencies and Integration Points
Dependencies include `linux/delay.h`, `linux/init.h`, `linux/io.h`, `linux/kernel.h`, `linux/of_address.h`, `linux/of_irq.h`, `linux/errno.h`, `linux/irqchip/arm-gic.h`, `asm/mcpm.h`, `asm/proc-fns.h`, `asm/cacheflush.h`, `asm/cputype.h`, `asm/cp15.h`, `linux/arm-cci.h`, `spc.h` plus platform integration with ARM reference-platform machine descriptors, syscon/regmap setup, AMBA auxdata, SMP pen-release boot, SPC/MCPM power control, hotplug, sched_clock mapping, and VExpress/TC2 power-management hooks. Cross-reference scans for visible symbols/compatibles found `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/tc2_pm.c`. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: legacy static mapping drift, board-compatible regressions, syscon lookup failures, SMP pen-release races, SPC timeout handling, and fragile big.LITTLE cluster power state transitions. Additional file-specific risks: suspend paths can lose wake masks, resume addresses, or controller state.

## Test Signals
integrator/realview/vexpress builds, QEMU or board DT boot where available, secondary CPU and hotplug tests, SPC debug traces, and Versatile Express TC2 MCPM suspend/hotplug validation. Exercise suspend/resume, wake-source delivery, cpuidle state entry, and lockdep/RCU warnings around low-power transitions.
