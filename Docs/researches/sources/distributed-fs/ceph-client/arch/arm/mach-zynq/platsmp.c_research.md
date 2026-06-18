# sources/distributed-fs/ceph-client/arch/arm/mach-zynq/platsmp.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-zynq/platsmp.c` provides SMP and CPU hotplug platform code for Xilinx Zynq-7000 platform support. It is part of the board-support layer that bridges generic ARM kernel code to SoC-specific registers, firmware conventions, and Devicetree-described devices.

## Important APIs, Types, and Functions
Important functions and entry points are `zynq_cpun_start`, `zynq_boot_secondary`, `zynq_smp_init_cpus`, `zynq_smp_prepare_cpus`, `zynq_secondary_init`, `zynq_cpu_kill`, `zynq_cpu_die`. Important structs/types referenced or defined are `task_struct`, `smp_operations`. File-scope platform state and tables include `ncores`, `trampoline_code_size`, `phy_cpuid`, `trampoline_size`, `i`. Preprocessor/register symbols defined here include none. Machine descriptors are none; OF compatible strings visible in the file are none. Headers imported by the file include `linux/export.h`, `linux/jiffies.h`, `linux/init.h`, `linux/io.h`, `asm/cacheflush.h`, `asm/smp_plat.h`, `asm/smp_scu.h`, `linux/irqchip/arm-gic.h`, `common.h`

## Control Flow
Runtime flow starts when generic ARM SMP code calls this platform's `smp_operations`: initialize possible CPUs, prepare shared boot vectors or release registers, request a secondary CPU start, then synchronize with a pen-release or completion path. Hotplug paths reverse the sequence by quiescing caches, programming power/reset control, and waiting for the dying CPU or cluster to report a safe state.

## State and Persistence Behavior
Persistent storage is not used. Runtime state is kept in file-scope mappings, flags, tables, or hardware registers such as `ncores`, `trampoline_code_size`, `phy_cpuid`, `trampoline_size`, `i`. The durable contract is the DT ABI, Kconfig/Kbuild selection, and register programming sequence expected by firmware and the SoC; hardware register contents may persist across warm reset or low-power states even though the kernel does not write files.

## Dependencies and Integration Points
Dependencies include `linux/export.h`, `linux/jiffies.h`, `linux/init.h`, `linux/io.h`, `asm/cacheflush.h`, `asm/smp_plat.h`, `asm/smp_scu.h`, `linux/irqchip/arm-gic.h`, `common.h` plus platform integration with Zynq DT machine setup, SLCR syscon/regmap access, SCU mapping, SMP trampoline copying, CPU start/stop state, restart notifier, cpuidle registration, and DDR self-refresh suspend setup. Cross-reference scans for visible symbols/compatibles found `sources/distributed-fs/ceph-client/arch/arm/mach-zynq/common.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-zynq/platsmp.c`. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: SLCR unlock/write ordering errors, trampoline address or cache-flush mistakes, stale CPU state bits across hotplug, wrong OCM/DDR controller discovery, and suspend support depending on unavailable PM services. Additional file-specific risks: CPU bring-up and hotplug bugs can deadlock boot or leave caches incoherent.

## Test Signals
ARCH_ZYNQ builds, Zynq DT boot, CPU1 online/offline/hotplug, restart behavior, cpuidle registration, suspend entry when enabled, and SLCR syscon compatible validation. Exercise `/sys/devices/system/cpu/cpu*/online`, parallel hotplug loops, and dmesg checks for secondary boot timeouts or cache/RCU warnings.
