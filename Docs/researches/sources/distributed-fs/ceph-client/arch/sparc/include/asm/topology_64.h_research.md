# sources/distributed-fs/ceph-client/arch/sparc/include/asm/topology_64.h

Purpose: SPARC64-specific implementation header for `topology_64.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: types `pci_bus`; functions/helpers `cpu_to_node`, `pcibus_to_node`, `__node_distance`; macros/constants `_ASM_SPARC64_TOPOLOGY_H`, `cpumask_of_node`, `cpumask_of_pcibus`, `node_distance`, `topology_physical_package_id`, `topology_core_id`, `topology_core_cpumask`, `topology_core_cache_cpumask`, `topology_sibling_cpumask`.

Control flow: The file is driven by preprocessor gates such as `_ASM_SPARC64_TOPOLOGY_H`, `CONFIG_NUMA`, `CONFIG_PCI`, `CONFIG_SMP`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, SMP, PCI paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm/mmzone.h`, `asm-generic/topology.h`, `asm/cpudata.h`. Integration points include memory-management, SMP, PCI; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps. Test signals: Build and runtime coverage on sparc64 configurations, especially callers listed in dependencies, are the relevant test signals.
