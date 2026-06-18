# sources/distributed-fs/ceph-client/arch/arm/mach-tegra/sleep-tegra20.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-tegra/sleep-tegra20.S` provides low-level ARM assembly entry code for NVIDIA Tegra ARM platform support. It is part of the board-support layer that bridges generic ARM kernel code to SoC-specific registers, firmware conventions, and Devicetree-described devices.

## Important APIs, Types, and Functions
Important functions and entry points are `tegra20_hotplug_shutdown`, `tegra20_cpu_shutdown`, `tegra20_sleep_core_finish`, `tegra20_tear_down_cpu`, `tegra20_lp1_reset`. Important structs/types referenced or defined are none. File-scope platform state and tables include none. Preprocessor/register symbols defined here include `EMC_CFG`, `EMC_ADR_CFG`, `EMC_NOP`, `EMC_SELF_REF`, `EMC_REQ_CTRL`, `EMC_EMC_STATUS`, `CLK_RESET_CCLK_BURST`, `CLK_RESET_CCLK_DIVIDER`, `CLK_RESET_SCLK_BURST`, `CLK_RESET_SCLK_DIVIDER`, `CLK_RESET_PLLC_BASE`, `CLK_RESET_PLLM_BASE`, `CLK_RESET_PLLP_BASE`, `APB_MISC_XM2CFGCPADCTRL`, `APB_MISC_XM2CFGDPADCTRL`, `APB_MISC_XM2CLKCFGPADCTRL`, `APB_MISC_XM2COMPPADCTRL`, `APB_MISC_XM2VTTGENPADCTRL`, `APB_MISC_XM2CFGCPADCTRL2`, `APB_MISC_XM2CFGDPADCTRL2`, `PLLC_STORE_MASK`, `PLLM_STORE_MASK`, `PLLP_STORE_MASK`. Machine descriptors are none; OF compatible strings visible in the file are none. Headers imported by the file include `linux/linkage.h`, `soc/tegra/flowctrl.h`, `asm/assembler.h`, `asm/proc-fns.h`, `asm/cp15.h`, `asm/cache.h`, `irammap.h`, `reset.h`, `sleep.h`

## Control Flow
Control enters the assembly label(s) `tegra20_hotplug_shutdown`, `tegra20_cpu_shutdown`, `tegra20_sleep_core_finish`, `tegra20_tear_down_cpu`, `tegra20_lp1_reset` from platform SMP, reset, or suspend code. The routines run with constrained CPU state, manipulate CP15/MMU/cache or boot-vector registers as required, then branch back into generic secondary-startup or resume code. Ordering is critical because C runtime services may not be available until after the assembly restores the expected processor context.

## State and Persistence Behavior
State is mostly CPU architectural state and small shared-memory/register contracts: boot vectors, resume addresses, cache/MMU bits, stack or context save areas, and mailbox words populated by C code. None of it is filesystem-persistent, but mistakes survive across suspend or secondary boot until hardware reset.

## Dependencies and Integration Points
Dependencies include `linux/linkage.h`, `soc/tegra/flowctrl.h`, `asm/assembler.h`, `asm/proc-fns.h`, `asm/cp15.h`, `asm/cache.h`, `irammap.h`, `reset.h`, `sleep.h` plus platform integration with Tegra DT machine setup, flow controller/PMC/CLKRST mappings, SMP and CPU hotplug, reset handlers copied to IRAM, LP1/LP2 suspend/resume assembly, irq wake handling, and cpuidle/power-management initialization. Cross-reference scans for visible symbols/compatibles found `sources/distributed-fs/ceph-client/arch/arm/mach-tegra/hotplug.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-tegra/pm-tegra20.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-tegra/pm.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-tegra/sleep-tegra20.S`, `sources/distributed-fs/ceph-client/arch/arm/mach-tegra/sleep.h`. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: IRAM layout overlap, reset-vector programming mistakes, cache/MMU state corruption across suspend, wake IRQ mask loss, SoC-generation register differences, and fragile assembly contracts with C structures. Additional file-specific risks: assembly has limited type checking and is sensitive to exact offsets, cache state, and calling convention; suspend paths can lose wake masks, resume addresses, or controller state.

## Test Signals
tegra_defconfig builds, Tegra20/30/114/124 DT boot, CPU online/offline, suspend/resume or LP2 tests, wake IRQ verification, and objdump/readelf checks that reset/sleep code sections fit expected regions. Assemble with `W=1`, inspect symbol boundaries with `objdump -dr`, and run boot/suspend paths on hardware or faithful emulation because static tests cannot validate CPU mode transitions.
