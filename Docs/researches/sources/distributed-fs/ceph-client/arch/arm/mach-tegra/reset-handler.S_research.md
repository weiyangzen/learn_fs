# sources/distributed-fs/ceph-client/arch/arm/mach-tegra/reset-handler.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-tegra/reset-handler.S` provides low-level ARM assembly entry code for NVIDIA Tegra ARM platform support. It is part of the board-support layer that bridges generic ARM kernel code to SoC-specific registers, firmware conventions, and Devicetree-described devices.

## Important APIs, Types, and Functions
Important functions and entry points are `tegra_resume`, `tegra_resume_trusted_foundations`, `__tegra_cpu_reset_handler_start`, `__tegra_cpu_reset_handler`, `__tegra_cpu_reset_handler_end`. Important structs/types referenced or defined are none. File-scope platform state and tables include none. Preprocessor/register symbols defined here include `PMC_SCRATCH41`. Machine descriptors are none; OF compatible strings visible in the file are none. Headers imported by the file include `linux/init.h`, `linux/linkage.h`, `soc/tegra/flowctrl.h`, `soc/tegra/fuse.h`, `asm/assembler.h`, `asm/asm-offsets.h`, `asm/cache.h`, `iomap.h`, `reset.h`, `sleep.h`

## Control Flow
Control enters the assembly label(s) `tegra_resume`, `tegra_resume_trusted_foundations`, `__tegra_cpu_reset_handler_start`, `__tegra_cpu_reset_handler`, `__tegra_cpu_reset_handler_end` from platform SMP, reset, or suspend code. The routines run with constrained CPU state, manipulate CP15/MMU/cache or boot-vector registers as required, then branch back into generic secondary-startup or resume code. Ordering is critical because C runtime services may not be available until after the assembly restores the expected processor context.

## State and Persistence Behavior
State is mostly CPU architectural state and small shared-memory/register contracts: boot vectors, resume addresses, cache/MMU bits, stack or context save areas, and mailbox words populated by C code. None of it is filesystem-persistent, but mistakes survive across suspend or secondary boot until hardware reset.

## Dependencies and Integration Points
Dependencies include `linux/init.h`, `linux/linkage.h`, `soc/tegra/flowctrl.h`, `soc/tegra/fuse.h`, `asm/assembler.h`, `asm/asm-offsets.h`, `asm/cache.h`, `iomap.h`, `reset.h`, `sleep.h` plus platform integration with Tegra DT machine setup, flow controller/PMC/CLKRST mappings, SMP and CPU hotplug, reset handlers copied to IRAM, LP1/LP2 suspend/resume assembly, irq wake handling, and cpuidle/power-management initialization. Cross-reference scans for visible symbols/compatibles found `sources/distributed-fs/ceph-client/arch/arm/mach-tegra/reset-handler.S`, `sources/distributed-fs/ceph-client/arch/arm/mach-tegra/reset.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-tegra/reset.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-tegra/sleep-tegra20.S`, `sources/distributed-fs/ceph-client/arch/arm/mach-tegra/sleep-tegra30.S`, `sources/distributed-fs/ceph-client/arch/arm/mach-tegra/sleep.h`, `sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-tegra.c`, `sources/distributed-fs/ceph-client/drivers/soc/tegra/pmc.c`. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: IRAM layout overlap, reset-vector programming mistakes, cache/MMU state corruption across suspend, wake IRQ mask loss, SoC-generation register differences, and fragile assembly contracts with C structures. Additional file-specific risks: assembly has limited type checking and is sensitive to exact offsets, cache state, and calling convention.

## Test Signals
tegra_defconfig builds, Tegra20/30/114/124 DT boot, CPU online/offline, suspend/resume or LP2 tests, wake IRQ verification, and objdump/readelf checks that reset/sleep code sections fit expected regions. Assemble with `W=1`, inspect symbol boundaries with `objdump -dr`, and run boot/suspend paths on hardware or faithful emulation because static tests cannot validate CPU mode transitions.
