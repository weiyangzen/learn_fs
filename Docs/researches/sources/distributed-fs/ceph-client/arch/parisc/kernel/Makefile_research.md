<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/Makefile

Source read size: 54 lines, 1818 bytes.

Purpose: builds the PA-RISC kernel object set and optional architecture features. Important targets/variables: `always-$(KBUILD_BUILTIN) := vmlinux.lds`, core `obj-y` list for boot, cache, traps, time, irq, syscall, entry, firmware, hardware, drivers, alternatives, signal, unwind, patching and TOC; conditional objects for SMP, PA11 DMA, PCI, modules, 64-bit compat, stacktrace, audit, perf, topology, ftrace, jump labels, KGDB, kprobes, kexec, and vDSO subdirectories. Control flow: Kbuild includes or excludes objects based on config, and removes ftrace profiling from low-level files. State and persistence: build configuration determines linked kernel contents. Dependencies and integration points: architecture Kconfig, vDSO Makefiles, low-level assembly, and linker script generation. Risks: profiling low-level entry/cache/patch/unwind code can break tracing recursion; missing conditional objects produce unresolved symbols only in specific configs. Test signals: allmodconfig/defconfig builds for 32-bit and 64-bit, ftrace/perf/kexec/kprobes configs, and vDSO build validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/Makefile -->
