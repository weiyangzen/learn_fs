# sources/distributed-fs/ceph-client/arch/arm/mach-sti/board-dt.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-sti/board-dt.c` provides DT machine and board initialization code for STMicroelectronics STi platform support. Its machine descriptor(s) `STM (STi SoC with Flattened Device Tree)` bind DT `compatible` strings to early mapping, IRQ, timer, SMP, restart, and `of_platform_populate` hooks used during ARM boot.

## Important APIs, Types, and Functions
Important functions and entry points are none. Important structs/types referenced or defined are none. File-scope platform state and tables include none. Preprocessor/register symbols defined here include none. Machine descriptors are `STM (STi SoC with Flattened Device Tree)`; OF compatible strings visible in the file are `st,stih407`, `st,stih410`, `st,stih418`. Headers imported by the file include `asm/hardware/cache-l2x0.h`, `asm/mach/arch.h`, `smp.h`

## Control Flow
ARM boot selects the machine descriptor by matching the root DT compatible. The descriptor's callbacks run in order: static IO mapping when present, IRQ/timer setup, optional SMP preparation, board/device population, late init, and restart/poweroff hooks. Device creation is mostly delegated to `of_platform_populate` or `of_platform_default_populate`.

## State and Persistence Behavior
Persistent storage is not used. Runtime state is kept in file-scope mappings, flags, tables, or hardware registers such as no named file-scope state detected. The durable contract is the DT ABI, Kconfig/Kbuild selection, and register programming sequence expected by firmware and the SoC; hardware register contents may persist across warm reset or low-power states even though the kernel does not write files.

## Dependencies and Integration Points
Dependencies include `asm/hardware/cache-l2x0.h`, `asm/mach/arch.h`, `smp.h` plus platform integration with DT-only machine selection, GIC/irqchip setup, SMP secondary boot through syscfg boot registers, PSCI fallback expectations, and OF platform device population. Cross-reference scans for visible symbols/compatibles found `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/stih407-family.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/stih407-pinctrl.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/stih410-b2260.dts`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/stih410-clock.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/stih410.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/stih418-b2199.dts`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/stih418-b2264.dts`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/stih418-clock.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/stih418.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/mach-sti/board-dt.c`, `sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-mux.c`, `sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-pll.c`, `sources/distributed-fs/ceph-client/drivers/clocksource/clksrc_st_lpc.c`, `sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt-platdev.c`. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: missing syscfg phandles, wrong secondary-start address programming, stale compatible strings, and SMP boot regressions when firmware or DT changes the CPU bring-up method. Additional file-specific risks: compatible-string changes can orphan existing board DTBs.

## Test Signals
ARCH_STI builds, DT boot on stih415/stih416/stih407 class boards, secondary CPU online/offline logs, and dtbs_check coverage for `st,syscfg` and CPU enable-method data. Use DT boot smoke tests, earlycon logs, `dtbs_check` for matching board files, and probe logs for devices populated from the machine descriptor.
