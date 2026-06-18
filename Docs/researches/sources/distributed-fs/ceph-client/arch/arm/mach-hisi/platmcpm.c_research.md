<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-hisi/platmcpm.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-hisi/platmcpm.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-hisi/platmcpm.c` belongs to HiSilicon ARM platform and SMP support in the Ceph-client kernel source snapshot. It coordinates SMP secondary CPU bring-up, hotplug, multi-cluster power management, and coherency transitions.

### Important APIs, Types, And Functions
Notable functions/entry points: `hip04_cluster_is_down`, `hip04_set_snoop_filter`, `hip04_boot_secondary`, `hip04_cpu_die`, `hip04_cpu_kill`, `hip04_cpu_table_init`, `hip04_smp_init`, `out`, `err`, `err_table`, `err_fabric`, `err_sysctrl`, `err_reloc`. Types: structs `device_node`, `resource`, enums none. Important macros/register names include `CORE_RESET_BIT(x)`, `NEON_RESET_BIT(x)`, `CORE_DEBUG_RESET_BIT(x)`, `CLUSTER_L2_RESET_BIT`, `CLUSTER_DEBUG_RESET_BIT`, `CORE_RESET_STATUS(x)`, `NEON_RESET_STATUS(x)`, `CORE_DEBUG_RESET_STATUS(x)`, `CLUSTER_L2_RESET_STATUS`, `CLUSTER_DEBUG_RESET_STATUS`, `CORE_WFI_STATUS(x)`, `CORE_WFE_STATUS(x)`, `CORE_DEBUG_ACK(x)`, `SC_CPU_RESET_REQ(x)`, `SC_CPU_RESET_DREQ(x)`, `SC_CPU_RESET_STATUS(x)`, `FAB_SF_MODE`, `FAB_SF_INVLD`, `FB_SF_INVLD_START`, `HIP04_MAX_CLUSTERS`, `HIP04_MAX_CPUS_PER_CLUSTER`, `POLL_MSEC`, `TIMEOUT_MSEC`.

### Control Flow
SMP/hotplug paths compute logical-to-physical CPU or cluster IDs, program reset/power bits, synchronize with locks/cache maintenance, and release or park secondary CPUs.

### State, Persistence, And Dependencies
Dependencies include `linux/init.h`, `linux/smp.h`, `linux/delay.h`, `linux/io.h`, `linux/memblock.h`, `linux/of_address.h`, `asm/cputype.h`, `asm/cp15.h`, `asm/cacheflush.h`, `asm/smp.h`, `asm/smp_plat.h`, `core.h`. Local/static state or exported register data includes `static void __iomem *sysctrl, *fabric`, `static int hip04_cpu_table[HIP04_MAX_CLUSTERS][HIP04_MAX_CPUS_PER_CLUSTER]`, `static u32 fabric_phys_addr`, `static u32 hip04_boot_method[4]`, `int i`, `unsigned long data`, `unsigned int mpidr, cpu, cluster`, `void __iomem *sys_dreq, *sys_status`, `bool last_man`, `unsigned int data, tries, count`, `static const struct smp_operations hip04_smp_ops __initconst = {`, `struct device_node *np, *np_sctl, *np_fab`, and 3 more. Compatible strings or firmware/device-tree identifiers observed: `hisilicon,hip04-bootwrapper`, `hisilicon,sysctrl`, `hisilicon,hip04-fabric`. State is kernel-resident and hardware-backed: MMIO registers, interrupt masks, reset vectors, wakeup masks, clock/regulator settings, and cached CPU revision variables survive only as long as the running kernel unless the underlying PMU/SRAM/firmware register preserves them across suspend.

### Integration Points
Integration points are ARM SMP, hotplug, and MCPM, legacy platform devices such as LED, RTC, timer, and ISA DMA. Callers should treat `hip04_cluster_is_down`, `hip04_set_snoop_filter`, `hip04_boot_secondary`, `hip04_cpu_die`, `hip04_cpu_kill`, `hip04_cpu_table_init`, `hip04_smp_init`, `out` as platform hooks rather than generic APIs when those symbols are visible.

### Risks
Primary risks include MMIO or port-I/O ordering, missing barriers, and incorrect register bit definitions, interrupt masking/wakeup regressions, resume failures, lost wakeups, and low-power state mismatches, CPU bring-up/hotplug races and coherency/cache maintenance bugs, missing devicetree nodes or leaked mappings/references on error paths.

### Test Signals
Useful test signals include ARM build coverage for the relevant CONFIG symbols, devicetree boot logs showing compatible match and platform device population, interrupt storm, mask/unmask, and wake-capable IRQ tests, secondary CPU online/offline hotplug loops under load, GPIO/LED state readback on target hardware. Source reading signal: 346 lines; 12 includes; 13 function/entry points; 23 macro/defines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-hisi/platmcpm.c -->
