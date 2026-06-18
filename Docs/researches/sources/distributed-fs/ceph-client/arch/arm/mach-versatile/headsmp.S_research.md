# sources/distributed-fs/ceph-client/arch/arm/mach-versatile/headsmp.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-versatile/headsmp.S` provides low-level ARM assembly entry code for ARM Integrator, RealView, Versatile, and Versatile Express platform support. It is part of the board-support layer that bridges generic ARM kernel code to SoC-specific registers, firmware conventions, and Devicetree-described devices.

## Important APIs, Types, and Functions
Important functions and entry points are `versatile_secondary_startup`. Important structs/types referenced or defined are none. File-scope platform state and tables include none. Preprocessor/register symbols defined here include none. Machine descriptors are none; OF compatible strings visible in the file are none. Headers imported by the file include `linux/linkage.h`, `linux/init.h`, `asm/assembler.h`

## Control Flow
Control enters the assembly label(s) `versatile_secondary_startup` from platform SMP, reset, or suspend code. The routines run with constrained CPU state, manipulate CP15/MMU/cache or boot-vector registers as required, then branch back into generic secondary-startup or resume code. Ordering is critical because C runtime services may not be available until after the assembly restores the expected processor context.

## State and Persistence Behavior
State is mostly CPU architectural state and small shared-memory/register contracts: boot vectors, resume addresses, cache/MMU bits, stack or context save areas, and mailbox words populated by C code. None of it is filesystem-persistent, but mistakes survive across suspend or secondary boot until hardware reset.

## Dependencies and Integration Points
Dependencies include `linux/linkage.h`, `linux/init.h`, `asm/assembler.h` plus platform integration with ARM reference-platform machine descriptors, syscon/regmap setup, AMBA auxdata, SMP pen-release boot, SPC/MCPM power control, hotplug, sched_clock mapping, and VExpress/TC2 power-management hooks. Cross-reference scans for visible symbols/compatibles found `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/headsmp.S`, `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/platsmp-realview.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/platsmp-vexpress.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-versatile/platsmp.h`. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: legacy static mapping drift, board-compatible regressions, syscon lookup failures, SMP pen-release races, SPC timeout handling, and fragile big.LITTLE cluster power state transitions. Additional file-specific risks: assembly has limited type checking and is sensitive to exact offsets, cache state, and calling convention; CPU bring-up and hotplug bugs can deadlock boot or leave caches incoherent.

## Test Signals
integrator/realview/vexpress builds, QEMU or board DT boot where available, secondary CPU and hotplug tests, SPC debug traces, and Versatile Express TC2 MCPM suspend/hotplug validation. Assemble with `W=1`, inspect symbol boundaries with `objdump -dr`, and run boot/suspend paths on hardware or faithful emulation because static tests cannot validate CPU mode transitions.
