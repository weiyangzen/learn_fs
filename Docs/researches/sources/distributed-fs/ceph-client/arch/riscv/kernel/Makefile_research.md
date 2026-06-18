<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/Makefile

Purpose: Builds the RISC-V architecture kernel objects and applies special compiler flags for low-level entry, patching, vDSO, suspend, and feature code.

Important APIs/types/functions: Defines `obj-y`, `obj-$(CONFIG_*)`, `extra-y`, CFLAGS overrides, syscall table generation, vdso targets, and per-object instrumentation restrictions.

Control flow: Kbuild selects objects based on config, builds generated syscall tables/asm offsets, and compiles sensitive files with instrumentation disabled when required.

State and persistence: No runtime state, but build outputs determine linked kernel behavior.

Dependencies and integration points: Integrates with Kbuild, syscall generation, vDSO/compat vDSO, ftrace, alternatives, KASAN/KCSAN, ACPI, KVM, suspend, and vendor extension objects.

Risks: Wrong object selection or missing no-instrument flags can break early boot, patching with MMU off, or tracing recursion.

Test signals: Config matrix builds for SMP/MMU/ACPI/KVM/VDSO/ftrace/suspend/vendor extensions and boot smoke tests.

Source read size: 130 lines, 3830 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/Makefile -->
