# sources/distributed-fs/ceph-client/arch/arm/mach-versatile/realview.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-versatile/realview.c` provides DT machine and board initialization code for ARM Integrator, RealView, Versatile, and Versatile Express platform support. Its machine descriptor(s) `REALVIEW_DT (ARM RealView Machine (Device Tree Support))` bind DT `compatible` strings to early mapping, IRQ, timer, SMP, restart, and `of_platform_populate` hooks used during ARM boot.

## Important APIs, Types, and Functions
Important functions and entry points are none. Important structs/types referenced or defined are none. File-scope platform state and tables include none. Preprocessor/register symbols defined here include none. Machine descriptors are `REALVIEW_DT (ARM RealView Machine (Device Tree Support))`; OF compatible strings visible in the file are `arm,realview-eb`, `arm,realview-pb1176`, `arm,realview-pba8`, `arm,realview-pbx`. Headers imported by the file include `asm/mach/arch.h`

## Control Flow
ARM boot selects the machine descriptor by matching the root DT compatible. The descriptor's callbacks run in order: static IO mapping when present, IRQ/timer setup, optional SMP preparation, board/device population, late init, and restart/poweroff hooks. Device creation is mostly delegated to `of_platform_populate` or `of_platform_default_populate`.

## State and Persistence Behavior
Persistent storage is not used. Runtime state is kept in file-scope mappings, flags, tables, or hardware registers such as no named file-scope state detected. The durable contract is the DT ABI, Kconfig/Kbuild selection, and register programming sequence expected by firmware and the SoC; hardware register contents may persist across warm reset or low-power states even though the kernel does not write files.

## Dependencies and Integration Points
Dependencies include `asm/mach/arch.h` plus platform integration with ARM reference-platform machine descriptors, syscon/regmap setup, AMBA auxdata, SMP pen-release boot, SPC/MCPM power control, hotplug, sched_clock mapping, and VExpress/TC2 power-management hooks. Cross-reference scans for visible symbols/compatibles found `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/arm-realview-eb-11mp-ctrevb.dts`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/arm-realview-eb-mp.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/arm-realview-eb.dts`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/arm-realview-eb.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/arm-realview-pb1176.dts`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/arm-realview-pba8.dts`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/arm-realview-pbx.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/platsmp-realview.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/realview.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_versatile.c`, `sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-realview.c`, `sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.c`, `sources/distributed-fs/ceph-client/drivers/power/reset/arm-versatile-reboot.c`, `sources/distributed-fs/ceph-client/drivers/soc/versatile/soc-realview.c`. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: legacy static mapping drift, board-compatible regressions, syscon lookup failures, SMP pen-release races, SPC timeout handling, and fragile big.LITTLE cluster power state transitions. Additional file-specific risks: compatible-string changes can orphan existing board DTBs.

## Test Signals
integrator/realview/vexpress builds, QEMU or board DT boot where available, secondary CPU and hotplug tests, SPC debug traces, and Versatile Express TC2 MCPM suspend/hotplug validation. Use DT boot smoke tests, earlycon logs, `dtbs_check` for matching board files, and probe logs for devices populated from the machine descriptor.
