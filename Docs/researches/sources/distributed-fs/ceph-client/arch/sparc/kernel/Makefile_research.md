<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/Makefile

Purpose: Maps SPARC kernel configuration symbols to architecture kernel objects and special build flags.

Important APIs and control flow: sets `CPPFLAGS_vmlinux.lds`, always builds the linker script when built-in, removes function-tracer profiling from low-level timing/perf/ftrace objects, and selects boot heads, trap/IRQ/process/signal/setup/time/prom/of-device objects by `$(BITS)`. It conditionally builds SPARC32 platform support, SPARC64 hypervisor/IOMMU/LDOM/VIO/PCI/perf/ADI/NMI objects, SMP and hotplug pieces, early framebuffer, audit/compat audit, modules, kprobes, uprobes, jump labels, and US3 memory controller support.

State, dependencies, and risks: state is build composition and object ordering. Dependencies are Kconfig symbols, generated syscall/linker assets, and low-level assembly names. Risks include unresolved symbols from mismatched config selections, profiling low-level trap/time paths, and missing compat audit objects. Test signals are SPARC32/SPARC64 defconfig and allmodconfig builds, linker-script preprocessing, ftrace-enabled builds, and config combinations for PCI, LDOMS, AUDIT, COMPAT, and US3_MC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/Makefile -->
