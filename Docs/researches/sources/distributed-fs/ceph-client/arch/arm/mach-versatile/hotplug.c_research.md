# sources/distributed-fs/ceph-client/arch/arm/mach-versatile/hotplug.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-versatile/hotplug.c` provides SMP and CPU hotplug platform code for ARM Integrator, RealView, Versatile, and Versatile Express platform support. It is part of the board-support layer that bridges generic ARM kernel code to SoC-specific registers, firmware conventions, and Devicetree-described devices.

## Important APIs, Types, and Functions
Important functions and entry points are `versatile_immitation_enter_lowpower`, `versatile_immitation_leave_lowpower`, `versatile_immitation_do_lowpower`, `versatile_immitation_cpu_die`. Important structs/types referenced or defined are none. File-scope platform state and tables include `spurious`. Preprocessor/register symbols defined here include none. Machine descriptors are none; OF compatible strings visible in the file are none. Headers imported by the file include `linux/kernel.h`, `linux/errno.h`, `linux/smp.h`, `asm/smp_plat.h`, `asm/cp15.h`, `platsmp.h`

## Control Flow
Runtime flow starts when generic ARM SMP code calls this platform's `smp_operations`: initialize possible CPUs, prepare shared boot vectors or release registers, request a secondary CPU start, then synchronize with a pen-release or completion path. Hotplug paths reverse the sequence by quiescing caches, programming power/reset control, and waiting for the dying CPU or cluster to report a safe state.

## State and Persistence Behavior
Persistent storage is not used. Runtime state is kept in file-scope mappings, flags, tables, or hardware registers such as `spurious`. The durable contract is the DT ABI, Kconfig/Kbuild selection, and register programming sequence expected by firmware and the SoC; hardware register contents may persist across warm reset or low-power states even though the kernel does not write files.

## Dependencies and Integration Points
Dependencies include `linux/kernel.h`, `linux/errno.h`, `linux/smp.h`, `asm/smp_plat.h`, `asm/cp15.h`, `platsmp.h` plus platform integration with ARM reference-platform machine descriptors, syscon/regmap setup, AMBA auxdata, SMP pen-release boot, SPC/MCPM power control, hotplug, sched_clock mapping, and VExpress/TC2 power-management hooks. Cross-reference scans for visible symbols/compatibles found `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/hotplug.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/platsmp-realview.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/platsmp-vexpress.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/platsmp.h`. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: legacy static mapping drift, board-compatible regressions, syscon lookup failures, SMP pen-release races, SPC timeout handling, and fragile big.LITTLE cluster power state transitions. Additional file-specific risks: CPU bring-up and hotplug bugs can deadlock boot or leave caches incoherent.

## Test Signals
integrator/realview/vexpress builds, QEMU or board DT boot where available, secondary CPU and hotplug tests, SPC debug traces, and Versatile Express TC2 MCPM suspend/hotplug validation. Exercise `/sys/devices/system/cpu/cpu*/online`, parallel hotplug loops, and dmesg checks for secondary boot timeouts or cache/RCU warnings.
