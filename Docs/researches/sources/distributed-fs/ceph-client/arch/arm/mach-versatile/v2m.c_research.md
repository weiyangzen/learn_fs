# sources/distributed-fs/ceph-client/arch/arm/mach-versatile/v2m.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-versatile/v2m.c` provides DT machine and board initialization code for ARM Integrator, RealView, Versatile, and Versatile Express platform support. Its machine descriptor(s) `VEXPRESS_DT (ARM-Versatile Express)` bind DT `compatible` strings to early mapping, IRQ, timer, SMP, restart, and `of_platform_populate` hooks used during ARM boot.

## Important APIs, Types, and Functions
Important functions and entry points are `vexpress_flags_set`. Important structs/types referenced or defined are `device_node`. File-scope platform state and tables include none. Preprocessor/register symbols defined here include `SYS_FLAGSSET`, `SYS_FLAGSCLR`. Machine descriptors are `VEXPRESS_DT (ARM-Versatile Express)`; OF compatible strings visible in the file are `arm,vexpress`, `arm,vexpress-sysreg`. Headers imported by the file include `linux/of.h`, `linux/of_address.h`, `asm/mach/arch.h`, `vexpress.h`

## Control Flow
ARM boot selects the machine descriptor by matching the root DT compatible. The descriptor's callbacks run in order: static IO mapping when present, IRQ/timer setup, optional SMP preparation, board/device population, late init, and restart/poweroff hooks. Device creation is mostly delegated to `of_platform_populate` or `of_platform_default_populate`.

## State and Persistence Behavior
Persistent storage is not used. Runtime state is kept in file-scope mappings, flags, tables, or hardware registers such as no named file-scope state detected. The durable contract is the DT ABI, Kconfig/Kbuild selection, and register programming sequence expected by firmware and the SoC; hardware register contents may persist across warm reset or low-power states even though the kernel does not write files.

## Dependencies and Integration Points
Dependencies include `linux/of.h`, `linux/of_address.h`, `asm/mach/arch.h`, `vexpress.h` plus platform integration with ARM reference-platform machine descriptors, syscon/regmap setup, AMBA auxdata, SMP pen-release boot, SPC/MCPM power control, hotplug, sched_clock mapping, and VExpress/TC2 power-management hooks. Cross-reference scans for visible symbols/compatibles found `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/vexpress-v2m-rs1.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/vexpress-v2m.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/vexpress-v2p-ca15-tc1.dts`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/vexpress-v2p-ca15_a7.dts`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/vexpress-v2p-ca5s.dts`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/vexpress-v2p-ca9.dts`, `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/platsmp-vexpress.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/tc2_pm.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/v2m.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/vexpress.h`, `sources/distributed-fs/ceph-client/drivers/bus/vexpress-config.c`, `sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-vexpress-osc.c`, `sources/distributed-fs/ceph-client/drivers/clocksource/timer-versatile.c`, `sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt-platdev.c`. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: legacy static mapping drift, board-compatible regressions, syscon lookup failures, SMP pen-release races, SPC timeout handling, and fragile big.LITTLE cluster power state transitions. Additional file-specific risks: compatible-string changes can orphan existing board DTBs.

## Test Signals
integrator/realview/vexpress builds, QEMU or board DT boot where available, secondary CPU and hotplug tests, SPC debug traces, and Versatile Express TC2 MCPM suspend/hotplug validation. Use DT boot smoke tests, earlycon logs, `dtbs_check` for matching board files, and probe logs for devices populated from the machine descriptor.
