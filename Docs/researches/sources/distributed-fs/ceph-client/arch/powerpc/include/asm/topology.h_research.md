<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/topology.h

Purpose: Declares PowerPC NUMA, CPU, cache, and PCI topology helpers.

Important APIs/types/functions: node/cpu masks, `pcibus_to_node()`, `node_distance()`, associativity update hooks, sibling/core/cache masks, SMT controls, and topology update declarations. Source-visible declarations include: #define _ASM_POWERPC_TOPOLOGY_H; struct device;; struct device_node;; struct drmem_lmb;; #define RECLAIM_DISTANCE 10; #define cpumask_of_node(node) ((node) == -1 ? \; struct pci_bus;; extern int pcibus_to_node(struct pci_bus *bus);.

Control flow: firmware/OF topology is parsed into node and CPU masks used by scheduler, memory allocator, and PCI placement. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: NUMA node, CPU mask, and distance data persist globally and per CPU. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/mmzone.h>, #include <asm-generic/topology.h>, #include <asm/cputable.h>, #include <asm/smp.h>, #include <linux/cpu_smt.h>, #include <linux/cpumask.h>, #include <asm/cputhreads.h>. Integrated with scheduler domains, NUMA memory policy, PCI locality, CPU hotplug, and device-tree associativity.

Risks: bad topology maps degrade scheduling and can allocate memory on the wrong NUMA node. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 181 lines, 4449 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/topology.h -->
