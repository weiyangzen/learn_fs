<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/smp.h

Purpose: Declares PowerPC SMP topology, CPU bring-up, IPI, NMI, and CPU mask helpers.

Important APIs/types/functions: boot CPU IDs, `struct smp_ops_t`, CPU maps, IPI message enums, kick/offline hooks, NMI helpers, and topology mask accessors. Source-visible declarations include: #define _ASM_POWERPC_SMP_H; extern int boot_cpuid;; extern int boot_cpu_hwid; /* PPC64 only */; extern int boot_core_hwid;; extern int spinning_secondaries;; extern u32 *cpu_to_phys_id;; extern bool coregroup_enabled;; extern int cpu_to_chip_id(int cpu);.

Control flow: platform code fills `smp_ops`, boot code releases secondary CPUs, and runtime code sends IPIs or queries sibling/core masks. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: global CPU maps, boot CPU IDs, and per-CPU topology masks persist after discovery. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/threads.h>, #include <linux/cpumask.h>, #include <linux/kernel.h>, #include <linux/irqreturn.h>, #include <asm/paca.h>, #include <asm/percpu.h>. Integrated with scheduler topology, hotplug, interrupt controller code, KVM, and platform CPU bring-up.

Risks: CPU numbering versus hardware IDs is subtle, and hotplug/IPI ordering bugs can hang secondary CPUs. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 272 lines, 7179 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/smp.h -->
