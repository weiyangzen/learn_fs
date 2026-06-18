<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/Makefile

Purpose: Main x86 kernel build manifest. It selects core x86 object files, disables instrumentation for fragile entry/boot/debug paths, emits `vmlinux.lds`, and wires feature-specific objects for tracing, paravirt, KVM guest, ACPI, APIC, CPU, FPU, kexec, perf, CET, unwinders, and platform support.

Important APIs/types/functions: Kbuild variables `always-$(KBUILD_BUILTIN)`, `CPPFLAGS_vmlinux.lds`, `CFLAGS_REMOVE_*`, `KASAN_SANITIZE_*`, `KCSAN_SANITIZE`, `KMSAN_SANITIZE_*`, `KCOV_INSTRUMENT_*`, `CFLAGS_head32.o`, `CFLAGS_head64.o`, `CFLAGS_irq.o`, and many `obj-y`/`obj-$(CONFIG_*)` selections such as `head_$(BITS).o`, `setup.o`, `x86_init.o`, `irq.o`, `fpu/`, `cpu/`, `acpi/`, `apic/`, `kvm.o`, `paravirt.o`, `machine_kexec_$(BITS).o`, `ftrace.o`, `shstk.o`, and 64-bit-specific objects.

Control flow: Kbuild evaluates configuration symbols and bitness, removes unsafe instrumentation from selected objects, and compiles/link-orders architecture objects. Runtime control flow is indirect: object inclusion determines which boot, interrupt, tracing, paravirt, CPU, and platform paths exist in the kernel.

State and persistence behavior: No runtime state. Persistent outputs are built objects and linked image sections. Instrumentation exclusions protect early boot, NMI, kexec, and stacktrace state from compiler-added code that would be unsafe in those contexts.

Dependencies and integration points: Integrates with nearly every x86 kernel subsystem: boot entry, traps, IRQs, APIC, ACPI, PCI DMA, timers, FPU, ptrace, SMP, paravirt, KVM guest, kexec/crash dump, tracing, unwinders, modules, KGDB, perf, CET, and CPU/platform directories.

Risks and test signals: Risks include missing objects under configs, unsafe instrumentation causing boot/kexec hangs, wrong 32/64-bit object selection, and link-order regressions. Test broad x86 defconfig/allmodconfig/tinyconfig builds, boot smoke tests, ftrace/KASAN/KMSAN/KCOV configs, kexec, NMI handling, stack unwinding, paravirt/KVM guest boot, and 32-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/Makefile -->
