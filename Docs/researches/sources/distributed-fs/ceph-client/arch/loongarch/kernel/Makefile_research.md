<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/Makefile

Purpose: defines the LoongArch architecture kernel object build graph.
Important APIs and types: selects core objects such as head, entry, traps, irq, process, setup, time, CPU probe, module, signal, ptrace, vdso, alternatives, ftrace, kprobes, uprobes, KVM/paravirt, suspend, EFI, ACPI, kexec, KGDB, and debug helpers according to config.
Control flow: Kbuild uses the object lists to compile/link the architecture kernel and optional feature objects.
State and persistence: no runtime state, but object inclusion determines which initcalls and handlers exist in the kernel image.
Dependencies and integration: integrates with architecture configuration symbols, linker scripts, vDSO builds, and generic kernel subsystems.
Risks and test signals: missing object entries cause link failures or runtime absent handlers. Signals include defconfig/allmodconfig builds across EFI/ACPI/SMP/KGDB/FTRACE/KEXEC/KVM options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/Makefile -->
