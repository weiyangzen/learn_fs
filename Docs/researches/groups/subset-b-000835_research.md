# Research: subset-b-000835

Grouped research for SH Linux architecture headers in the Ceph client source tree. Each section preserves the source path and is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/dwarf.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/dwarf.h

## Purpose
Defines SH DWARF unwind opcode, register, CFI, and frame-state constants used when the architecture DWARF unwinder is enabled.

## Important APIs, Types, And Functions
Includes `linux/compiler.h`, `linux/bug.h`, `linux/list.h`, `linux/module.h`. Key macros/constants include `__ASM_SH_DWARF_H`, `DW_OP_addr`, `DW_OP_deref`, `DW_OP_const1u`, `DW_OP_const1s`, `DW_OP_const2u`, `DW_OP_const2s`, `DW_OP_const4u`, `DW_OP_const4s`, `DW_OP_const8u`, `DW_OP_const8s`, `DW_OP_constu`, `DW_OP_consts`, `DW_OP_dup`, `DW_OP_drop`, `DW_OP_over`, `DW_OP_pick`, `DW_OP_swap`, plus 201 more. Structures include `dwarf_cie`, `list_head`, `rb_node`, `dwarf_fde`, `dwarf_frame`, `dwarf_reg`, `module`. Functions or extern declarations include `dwarf_unwind_stack`, `dwarf_free_frame`, `module_dwarf_finalize`, `module_dwarf_cleanup`. Register or hardware-address constants include `DWARF_ARCH_RA_REG`, `DWARF_FRAME_CFA_REG_OFFSET`, `DWARF_FRAME_CFA_REG_EXP`, `DWARF_REG_OFFSET`, `CFI_REGISTER`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
It directly depends on `linux/compiler.h`, `linux/bug.h`, `linux/list.h`, `linux/module.h`. Kconfig-sensitive paths mention `CONFIG_DWARF_UNWINDER`. Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 417 lines, 9899 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/dwarf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/elf.h

## Purpose
Defines the SH ELF ABI contract, relocation numbers, register sets, auxiliary vector hooks, FDPIC/PIC checks, platform initialization, and personality selection.

## Important APIs, Types, And Functions
Includes `linux/utsname.h`, `asm/auxvec.h`, `asm/ptrace.h`, `asm/user.h`. Key macros/constants include `__ASM_SH_ELF_H`, `EF_SH_PIC`, `EF_SH_FDPIC`, `R_SH_NONE`, `R_SH_DIR32`, `R_SH_REL32`, `R_SH_DIR8WPN`, `R_SH_IND12W`, `R_SH_DIR8WPL`, `R_SH_DIR8WPZ`, `R_SH_DIR8BP`, `R_SH_DIR8W`, `R_SH_DIR8L`, `R_SH_SWITCH16`, `R_SH_SWITCH32`, `R_SH_USES`, `R_SH_COUNT`, `R_SH_ALIGN`, plus 58 more. Structures include `user_fpu_struct`, `linux_binprm`. Typedefs include `elf_greg_t`, `elf_gregset_t[ELF_NGREG]`, `elf_fpregset_t`. Functions or extern declarations include `arch_setup_additional_pages`, `vdso_enabled`, `__kernel_vsyscall`, `l2_cache_shape`. Register or hardware-address constants include `CORE_DUMP_USE_REGSET`, `ELF_ET_DYN_BASE`, `ELF_CORE_COPY_REGS(_dest,_regs)`, `VDSO_BASE`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/utsname.h`, `asm/auxvec.h`, `asm/ptrace.h`, `asm/user.h`. Kconfig-sensitive paths mention `CONFIG_VSYSCALL`, `CONFIG_SH_FPU`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 211 lines, 6009 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/entry-macros.S -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/entry-macros.S

## Purpose
Provides low-level SH entry assembly macros for banked registers, IRQ tracing, software interrupt entry, prefetching, and DWARF CFI state.

## Important APIs, Types, And Functions
Key macros/constants include `PREF(x)`. Assembly macros include `.macro	cli`, `.macro	sti`, `.macro	get_current_thread_info, ti, tmp`, `.macro	TRACE_IRQS_ON`, `.macro	TRACE_IRQS_OFF`, `.macro	setup_frame_reg`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_HAS_SR_RB`, `CONFIG_TRACE_IRQFLAGS`, `CONFIG_CPU_SH2A`, `CONFIG_CPU_SH4`, `CONFIG_DWARF_UNWINDER`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 123 lines, 1897 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/entry-macros.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/extable.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/extable.h

## Purpose
Provides the SH architecture hook for the generic Linux `extable` subsystem, mostly by defining small constants or forwarding to generic helpers.

## Important APIs, Types, And Functions
Includes `asm-generic/extable.h`. Key macros/constants include `__ASM_SH_EXTABLE_H`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm-generic/extable.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 7 lines, 135 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/fixmap.h

## Purpose
Defines SH fixed virtual-address slots and fixmap address bounds for per-CPU temporary mappings, boot-time console mappings, and fixed ioremap windows.

## Important APIs, Types, And Functions
Includes `linux/kernel.h`, `linux/threads.h`, `asm/page.h`, `asm-generic/fixmap.h`. Key macros/constants include `_ASM_FIXMAP_H`, `FIX_N_COLOURS`, `FIX_N_IOREMAPS`, `FIXADDR_TOP`, `FIXADDR_SIZE`, `FIXADDR_START`, `FIXMAP_PAGE_NOCACHE`. Enums include `fixed_addresses`. Functions or extern declarations include `__set_fixmap`, `__clear_fixmap`. Register or hardware-address constants include `FIXADDR_TOP`, `FIXADDR_SIZE`, `FIXADDR_START`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `linux/kernel.h`, `linux/threads.h`, `asm/page.h`, `asm-generic/fixmap.h`. Kconfig-sensitive paths mention `CONFIG_IOREMAP_FIXED`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 86 lines, 2543 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/flat.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/flat.h

## Purpose
Defines SH architecture declarations and macros for `flat` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/unaligned.h`. Key macros/constants include `__ASM_SH_FLAT_H`, `FLAT_PLAT_INIT(_r)`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/unaligned.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 33 lines, 865 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/flat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/fpu.h

## Purpose
Defines SH architecture declarations and macros for `fpu` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `asm/ptrace.h`. Key macros/constants include `__ASM_SH_FPU_H`, `save_fpu(tsk)`, `restore_fpu(tsk)`, `release_fpu(regs)`, `grab_fpu(regs)`, `fpu_state_restore(regs)`, `__fpu_state_restore(regs)`. Structures include `task_struct`, `user_regset`. Functions or extern declarations include `float_raise`, `float_rounding_mode`, `save_fpu`, `restore_fpu`, `fpu_state_restore`, `__fpu_state_restore`, `do_fpu_inst`, `init_fpu`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm/ptrace.h`. Kconfig-sensitive paths mention `CONFIG_SH_FPU`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 72 lines, 1707 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/freq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/freq.h

## Purpose
Defines SH architecture declarations and macros for `freq` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `cpu/freq.h`. Key macros/constants include `__ASM_SH_FREQ_H`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `cpu/freq.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 12 lines, 212 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/freq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/ftrace.h

## Purpose
Defines SH low-level debug, unwind, trace, or linkage contracts for `ftrace` support.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_FTRACE_H`, `MCOUNT_INSN_SIZE`, `FTRACE_SYSCALL_MAX`, `MCOUNT_ADDR`, `CALL_ADDR`, `STUB_ADDR`, `GRAPH_ADDR`, `CALLER_ADDR`, `MCOUNT_INSN_OFFSET`, `GRAPH_INSN_OFFSET`, `ftrace_return_address(n)`. Structures include `dyn_arch_ftrace`. Functions or extern declarations include `prepare_ftrace_return`, `mcount`, `return_address`, `arch_ftrace_nmi_enter`, `arch_ftrace_nmi_exit`. Register or hardware-address constants include `MCOUNT_ADDR`, `CALL_ADDR`, `STUB_ADDR`, `GRAPH_ADDR`, `CALLER_ADDR`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_FUNCTION_TRACER`, `CONFIG_DYNAMIC_FTRACE`. Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 58 lines, 1444 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/futex-cas.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/futex-cas.h

## Purpose
Implements SH futex compare-exchange using the `cas.l` instruction plus exception-table fixups.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_FUTEX_CAS_H`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call. Exception-table fixups are present, so faulting loads/stores must branch to the listed recovery labels and return `-EFAULT` or an equivalent safe result. MMU and NOMMU builds take different paths, usually replacing fault-tolerant or page-table behavior with direct stubs. Atomicity is implemented by CPU-specific primitives or by interrupt exclusion, so the selected backend must match the SMP and CPU configuration. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_MMU`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 35 lines, 728 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/futex-cas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/futex-irq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/futex-irq.h

## Purpose
Implements the uniprocessor futex compare-exchange fallback by disabling local interrupts around user get/put.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_FUTEX_IRQ_H`. Register or hardware-address constants include `__ASM_SH_FUTEX_IRQ_H`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call. Atomicity is implemented by CPU-specific primitives or by interrupt exclusion, so the selected backend must match the SMP and CPU configuration.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 25 lines, 482 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/futex-irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/futex-llsc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/futex-llsc.h

## Purpose
Implements SH futex compare-exchange using `movli.l`/`movco.l` load-linked/store-conditional loops and `synco` barriers.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_FUTEX_LLSC_H`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call. Exception-table fixups are present, so faulting loads/stores must branch to the listed recovery labels and return `-EFAULT` or an equivalent safe result. MMU and NOMMU builds take different paths, usually replacing fault-tolerant or page-table behavior with direct stubs. Atomicity is implemented by CPU-specific primitives or by interrupt exclusion, so the selected backend must match the SMP and CPU configuration. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_MMU`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 42 lines, 870 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/futex-llsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/futex.h

## Purpose
Selects the SH futex atomic backend and implements generic futex compare-exchange and in-user atomic operations over `u32` user words.

## Important APIs, Types, And Functions
Includes `linux/futex.h`, `linux/uaccess.h`, `asm/errno.h`, `asm/futex-irq.h`, `asm/futex-cas.h`, `asm/futex-llsc.h`. Key macros/constants include `__ASM_SH_FUTEX_H`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `linux/futex.h`, `linux/uaccess.h`, `asm/errno.h`, `asm/futex-irq.h`, `asm/futex-cas.h`, `asm/futex-llsc.h`. Kconfig-sensitive paths mention `CONFIG_SMP`, `CONFIG_CPU_J2`, `CONFIG_CPU_SH4A`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 72 lines, 1381 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/hardirq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/hardirq.h

## Purpose
Provides the SH architecture hook for the generic Linux `hardirq` subsystem, mostly by defining small constants or forwarding to generic helpers.

## Important APIs, Types, And Functions
Includes `asm-generic/hardirq.h`. Key macros/constants include `__ASM_SH_HARDIRQ_H`, `ack_bad_irq`, `ARCH_WANTS_NMI_IRQSTAT`. Functions or extern declarations include `ack_bad_irq`. Register or hardware-address constants include `ARCH_WANTS_NMI_IRQSTAT`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `asm-generic/hardirq.h`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 11 lines, 267 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/hd64461.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/hd64461.h

## Purpose
Defines board/peripheral constants, platform data, or callbacks for the SH `hd64461` hardware integration.

## Important APIs, Types, And Functions
Includes `asm/io_generic.h`. Key macros/constants include `__ASM_SH_HD64461`, `HD64461_PCC_WINDOW`, `HD64461_IOBASE`, `HD64461_IO_OFFSET(x)`, `HD64461_PCC0_BASE`, `HD64461_PCC0_ATTR`, `HD64461_PCC0_COMM`, `HD64461_PCC0_IO`, `HD64461_PCC1_BASE`, `HD64461_PCC1_ATTR`, `HD64461_PCC1_COMM`, `HD64461_STBCR`, `HD64461_STBCR_CKIO_STBY`, `HD64461_STBCR_SAFECKE_IST`, `HD64461_STBCR_SLCKE_IST`, `HD64461_STBCR_SAFECKE_OST`, `HD64461_STBCR_SLCKE_OST`, `HD64461_STBCR_SMIAST`, plus 147 more. Functions or extern declarations include `hd64461_register_irq_demux`, `hd64461_unregister_irq_demux`. Register or hardware-address constants include `HD64461_PCC0_BASE`, `HD64461_PCC1_BASE`, `HD64461_STBCR`, `HD64461_SYSCR`, `HD64461_SCPUCR`, `HD64461_LCDCCR`, `HD64461_LDHNCR`, `HD64461_GRSCR`, `HD64461_PCC0GCR`, `HD64461_PCC0CSCR`, `HD64461_PCC0SCR`, `HD64461_PCC1GCR`, plus 26 more.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
It directly depends on `asm/io_generic.h`. Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 252 lines, 12075 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/hd64461.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/heartbeat.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/heartbeat.h

## Purpose
Defines board/peripheral constants, platform data, or callbacks for the SH `heartbeat` hardware integration.

## Important APIs, Types, And Functions
Includes `linux/timer.h`. Key macros/constants include `__ASM_SH_HEARTBEAT_H`, `HEARTBEAT_INVERTED`. Structures include `heartbeat_data`, `timer_list`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/timer.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 19 lines, 383 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/heartbeat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/hugetlb.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/hugetlb.h

## Purpose
Provides the SH architecture hook for the generic Linux `hugetlb` subsystem, mostly by defining small constants or forwarding to generic helpers.

## Important APIs, Types, And Functions
Includes `asm/cacheflush.h`, `asm/page.h`, `asm-generic/hugetlb.h`. Key macros/constants include `_ASM_SH_HUGETLB_H`, `__HAVE_ARCH_HUGE_PTEP_CLEAR_FLUSH`, `arch_clear_hugetlb_flags`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `asm/cacheflush.h`, `asm/page.h`, `asm-generic/hugetlb.h`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 23 lines, 554 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/hw_breakpoint.h

## Purpose
Defines SH hardware breakpoint state, UBC registration, perf breakpoint callbacks, and breakpoint-slot accounting.

## Important APIs, Types, And Functions
Includes `uapi/asm/hw_breakpoint.h`, `linux/kdebug.h`, `linux/types.h`. Key macros/constants include `__ASM_SH_HW_BREAKPOINT_H`, `__ARCH_HW_BREAKPOINT_H`, `HBP_NUM`, `hw_breakpoint_slots(type)`. Structures include `arch_hw_breakpoint`, `sh_ubc`, `clk`, `perf_event_attr`, `perf_event`, `task_struct`, `pmu`. Functions or extern declarations include `long`, `arch_install_hw_breakpoint`, `arch_uninstall_hw_breakpoint`, `hw_breakpoint_pmu_read`, `arch_check_bp_in_kernelspace`, `arch_bp_generic_fields`, `hw_breakpoint_arch_parse`, `hw_breakpoint_exceptions_notify`, `arch_fill_perf_breakpoint`, `register_sh_ubc`, `perf_ops_bp`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
It directly depends on `uapi/asm/hw_breakpoint.h`, `linux/kdebug.h`, `linux/types.h`. Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 72 lines, 2040 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/hw_breakpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/hw_irq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/hw_irq.h

## Purpose
Defines SH architecture declarations and macros for `hw_irq` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/init.h`, `linux/sh_intc.h`, `linux/atomic.h`. Key macros/constants include `__ASM_SH_HW_IRQ_H`. Structures include `ipr_data`, `ipr_desc`, `irq_chip`. Functions or extern declarations include `register_ipr_controller`, `irq_err_count`. Register or hardware-address constants include `__ASM_SH_HW_IRQ_H`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `linux/init.h`, `linux/sh_intc.h`, `linux/atomic.h`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 36 lines, 915 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/hw_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/i2c-sh7760.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/i2c-sh7760.h

## Purpose
Defines board/peripheral constants, platform data, or callbacks for the SH `i2c-sh7760` hardware integration.

## Important APIs, Types, And Functions
Key macros/constants include `_I2C_SH7760_H_`, `SH7760_I2C_DEVNAME`, `SH7760_I2C0_MMIO`, `SH7760_I2C0_MMIOEND`, `SH7760_I2C1_MMIO`, `SH7760_I2C1_MMIOEND`. Structures include `sh7760_i2c_platdata`. Register or hardware-address constants include `SH7760_I2C0_MMIO`, `SH7760_I2C0_MMIOEND`, `SH7760_I2C1_MMIO`, `SH7760_I2C1_MMIOEND`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 21 lines, 406 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/i2c-sh7760.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/io.h

## Purpose
Implements SH raw, relaxed, ordered, uncached, string, and port I/O accessors over memory-mapped I/O and the machine vector port base.

## Important APIs, Types, And Functions
Includes `linux/errno.h`, `asm/cache.h`, `asm/addrspace.h`, `asm/machvec.h`, `asm/page.h`, `linux/pgtable.h`, `asm/io_generic.h`, `asm-generic/pci_iomap.h`, `mach/mangle-port.h`, `asm/io_noioport.h`, plus 1 more. Key macros/constants include `__ASM_SH_IO_H`, `__IO_PREFIX`, `__raw_writeb(v,a)`, `__raw_writew(v,a)`, `__raw_writel(v,a)`, `__raw_writeq(v,a)`, `__raw_readb(a)`, `__raw_readw(a)`, `__raw_readl(a)`, `__raw_readq(a)`, `readb_relaxed(c)`, `readw_relaxed(c)`, `readl_relaxed(c)`, `readq_relaxed(c)`, `writeb_relaxed(v,c)`, `writew_relaxed(v,c)`, `writel_relaxed(v,c)`, `writeq_relaxed(v,c)`, plus 53 more. Functions or extern declarations include `__raw_writesl`, `__raw_readsl`, `memcpy_fromio`, `memcpy_toio`, `memset_io`, `valid_phys_addr_range`, `valid_mmap_phys_addr_range`, `ioport_map`, `sh_io_port_base`, `__ioport_map`. Register or hardware-address constants include `ARCH_HAS_VALID_PHYS_ADDR_RANGE`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers. MMU and NOMMU builds take different paths, usually replacing fault-tolerant or page-table behavior with direct stubs.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
It directly depends on `linux/errno.h`, `asm/cache.h`, `asm/addrspace.h`, `asm/machvec.h`, `asm/page.h`, `linux/pgtable.h`, `asm/io_generic.h`, `asm-generic/pci_iomap.h`, `mach/mangle-port.h`, `asm/io_noioport.h`, `asm-generic/io.h`. Kconfig-sensitive paths mention `CONFIG_HAS_IOPORT_MAP`, `CONFIG_GENERIC_IOMAP`, `CONFIG_MMU`. Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 291 lines, 8623 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/io_generic.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/io_generic.h

## Purpose
Provides a SH I/O implementation variant used by `asm/io.h` for generic, no-port, or trapped-I/O configurations.

## Important APIs, Types, And Functions
Key macros/constants include `IO_CONCAT(a,b)`, `_IO_CONCAT(a,b)`. Functions or extern declarations include `IO_CONCAT`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 19 lines, 661 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/io_generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/io_noioport.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/io_noioport.h

## Purpose
Provides a SH I/O implementation variant used by `asm/io.h` for generic, no-port, or trapped-I/O configurations.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_IO_NOIOPORT_H`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 79 lines, 1285 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/io_noioport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/io_trapped.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/io_trapped.h

## Purpose
Provides a SH I/O implementation variant used by `asm/io.h` for generic, no-port, or trapped-I/O configurations.

## Important APIs, Types, And Functions
Includes `linux/list.h`, `linux/ioport.h`, `asm/page.h`. Key macros/constants include `__ASM_SH_IO_TRAPPED_H`, `IO_TRAPPED_MAGIC`, `__ioremap_trapped(offset, size)`, `__ioport_map_trapped(offset, size)`, `register_trapped_io(tiop)`, `handle_trapped_io(tiop, address)`. Structures include `trapped_io`, `resource`, `list_head`. Functions or extern declarations include `register_trapped_io`, `handle_trapped_io`, `trapped_mem`, `trapped_io`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
It directly depends on `linux/list.h`, `linux/ioport.h`, `asm/page.h`. Kconfig-sensitive paths mention `CONFIG_IO_TRAPPED`, `CONFIG_HAS_IOMEM`, `CONFIG_HAS_IOPORT_MAP`. Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 59 lines, 1474 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/io_trapped.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/irq.h

## Purpose
Defines SH architecture declarations and macros for `irq` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/cpumask.h`, `asm/machvec.h`, `asm-generic/irq.h`. Key macros/constants include `__ASM_SH_IRQ_H`, `NO_IRQ_IGNORE`, `irq_demux(irq)`, `irq_ctx_init(cpu)`, `irq_ctx_exit(cpu)`, `irq_lookup(irq)`, `irq_finish(irq)`. Functions or extern declarations include `make_imask_irq`, `init_IRQ`, `migrate_irqs`, `irq_ctx_init`, `irq_ctx_exit`, `irq_lookup`, `irq_finish`. Register or hardware-address constants include `__ASM_SH_IRQ_H`, `NO_IRQ_IGNORE`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `linux/cpumask.h`, `asm/machvec.h`, `asm-generic/irq.h`. Kconfig-sensitive paths mention `CONFIG_IRQSTACKS`, `CONFIG_INTC_BALANCING`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 51 lines, 1185 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/irqflags.h

## Purpose
Implements SH local interrupt flag save, restore, enable, disable, and query helpers around status-register interrupt bits.

## Important APIs, Types, And Functions
Includes `asm-generic/irqflags.h`. Key macros/constants include `__ASM_SH_IRQFLAGS_H`, `ARCH_IRQ_DISABLED`, `ARCH_IRQ_ENABLED`. Register or hardware-address constants include `__ASM_SH_IRQFLAGS_H`, `ARCH_IRQ_DISABLED`, `ARCH_IRQ_ENABLED`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `asm-generic/irqflags.h`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 10 lines, 226 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kdebug.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/kdebug.h

## Purpose
Defines SH low-level debug, unwind, trace, or linkage contracts for `kdebug` support.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_KDEBUG_H`. Enums include `die_val`. Functions or extern declarations include `printk_address`, `dump_mem`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 19 lines, 433 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kexec.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/kexec.h

## Purpose
Declares SH kexec image limits, machine-kexec entry points, crash preparation, and crash register capture hooks.

## Important APIs, Types, And Functions
Includes `asm/ptrace.h`, `asm/string.h`, `linux/kernel.h`. Key macros/constants include `__ASM_SH_KEXEC_H`, `KEXEC_SOURCE_MEMORY_LIMIT`, `KEXEC_DESTINATION_MEMORY_LIMIT`, `KEXEC_CONTROL_MEMORY_LIMIT`, `KEXEC_CONTROL_PAGE_SIZE`, `KEXEC_ARCH`. Structures include `pt_regs`. Functions or extern declarations include `reserve_crashkernel`.

## Control Flow
Control flow is mostly assembler/preprocessor expansion. The file emits instruction sequences, exception-table records, or linker-section metadata that become executable or discoverable at build time. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State is encoded in generated sections, register save areas, and machine instructions rather than allocated here. Correctness depends on section names and offsets staying synchronized with linker and entry code.

## Dependencies And Integration Points
It directly depends on `asm/ptrace.h`, `asm/string.h`, `linux/kernel.h`. Kconfig-sensitive paths mention `CONFIG_KEXEC_CORE`. Integration points are assembler sources, linker script sections, generated offsets, and SH trap/entry code.

## Risks And Edge Cases
Risks are instruction-encoding, branch-delay, section-layout, and register-save mistakes. Small changes can cause boot, trap, or unwind failures that are hard to localize.

## Test Signals
Useful signals are assembler build coverage, objdump inspection of emitted sections, boot/trap smoke tests, unwind verification, and exception-table fixup tests.

Source read size: 72 lines, 2682 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kgdb.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/kgdb.h

## Purpose
Defines SH KGDB register sizing, trap numbers, breakpoint encoding, and register-set layout for remote debugging.

## Important APIs, Types, And Functions
Includes `asm/cacheflush.h`, `asm/ptrace.h`. Key macros/constants include `__ASM_SH_KGDB_H`, `_GP_REGS`, `_EXTRA_REGS`, `GDB_SIZEOF_REG`, `DBG_MAX_REG_NUM`, `NUMREGBYTES`, `BREAK_INSTR_SIZE`, `BUFMAX`, `CACHE_FLUSH_IS_SAFE`, `GDB_ADJUSTS_BREAK_OFFSET`. Enums include `regnames`. Register or hardware-address constants include `_GP_REGS`, `_EXTRA_REGS`, `GDB_SIZEOF_REG`, `DBG_MAX_REG_NUM`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
It directly depends on `asm/cacheflush.h`, `asm/ptrace.h`. Kconfig-sensitive paths mention `CONFIG_SMP`. Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 38 lines, 851 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kprobes.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/kprobes.h

## Purpose
Defines SH kprobe instruction slots, decoded-instruction metadata, breakpoint/restore opcodes, and arch kprobe hooks.

## Important APIs, Types, And Functions
Includes `asm-generic/kprobes.h`, `linux/types.h`, `linux/ptrace.h`. Key macros/constants include `__ASM_SH_KPROBES_H`, `BREAKPOINT_INSTRUCTION`, `MAX_INSN_SIZE`, `MAX_STACK_SIZE`, `MIN_STACK_SIZE(ADDR)`, `flush_insn_slot(p)`, `kretprobe_blacklist_size`, `kprobe_handle_illslot(pc)`. Structures include `kprobe`, `arch_specific_insn`, `prev_kprobe`, `kprobe_ctlblk`. Typedefs include `kprobe_opcode_t`. Functions or extern declarations include `arch_remove_kprobe`, `__kretprobe_trampoline`, `kprobe_fault_handler`, `kprobe_handle_illslot`. Register or hardware-address constants include `MIN_STACK_SIZE(ADDR)`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
It directly depends on `asm-generic/kprobes.h`, `linux/types.h`, `linux/ptrace.h`. Kconfig-sensitive paths mention `CONFIG_KPROBES`. Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 55 lines, 1302 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/linkage.h

## Purpose
Defines SH low-level debug, unwind, trace, or linkage contracts for `linkage` support.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_LINKAGE_H`, `__ALIGN`, `__ALIGN_STR`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 8 lines, 154 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/machvec.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/machvec.h

## Purpose
Defines the SH machine-vector abstraction for board-specific I/O, IRQ, MMIO, memory-init, and heartbeat operations.

## Important APIs, Types, And Functions
Includes `linux/types.h`, `linux/time.h`, `generated/machtypes.h`. Key macros/constants include `_ASM_SH_MACHVEC_H`, `get_system_type()`, `__initmv`. Structures include `sh_machine_vector`. Functions or extern declarations include `sh_mv`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/types.h`, `linux/time.h`, `generated/machtypes.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 36 lines, 699 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/machvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/mmiowb.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/mmiowb.h

## Purpose
Provides the SH architecture hook for the generic Linux `mmiowb` subsystem, mostly by defining small constants or forwarding to generic helpers.

## Important APIs, Types, And Functions
Includes `asm/barrier.h`, `asm-generic/mmiowb.h`. Key macros/constants include `__ASM_SH_MMIOWB_H`, `mmiowb()`. Register or hardware-address constants include `__ASM_SH_MMIOWB_H`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm/barrier.h`, `asm-generic/mmiowb.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 12 lines, 246 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/mmiowb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/mmu.h

## Purpose
Defines SH architecture declarations and macros for `mmu` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/errno.h`, `linux/threads.h`, `asm/page.h`. Key macros/constants include `__MMU_H`, `PMB_PASCR`, `PMB_IRMCR`, `PASCR_SE`, `PMB_ADDR`, `PMB_DATA`, `NR_PMB_ENTRIES`, `PMB_E_MASK`, `PMB_E_SHIFT`, `PMB_PFN_MASK`, `PMB_SZ_16M`, `PMB_SZ_64M`, `PMB_SZ_128M`, `PMB_SZ_512M`, `PMB_SZ_MASK`, `PMB_C`, `PMB_WT`, `PMB_UB`, plus 5 more. Typedefs include `mm_context_id_t[NR_CPUS]`. Functions or extern declarations include `__in_29bit_mode`, `pmb_init`, `pmb_bolt_mapping`, `pmb_unmap`. Register or hardware-address constants include `__MMU_H`, `PMB_PASCR`, `PMB_IRMCR`, `PMB_ADDR`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization. MMU and NOMMU builds take different paths, usually replacing fault-tolerant or page-table behavior with direct stubs.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `linux/errno.h`, `linux/threads.h`, `asm/page.h`. Kconfig-sensitive paths mention `CONFIG_MMU`, `CONFIG_BINFMT_ELF_FDPIC`, `CONFIG_PMB`, `CONFIG_29BIT`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 107 lines, 2233 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/mmu_context.h

## Purpose
Implements SH MMU context allocation, ASID versioning, TTB programming, address-space switching, and MMU enable/disable helpers.

## Important APIs, Types, And Functions
Includes `cpu/mmu_context.h`, `asm/tlbflush.h`, `linux/uaccess.h`, `linux/mm_types.h`, `asm/io.h`, `asm-generic/mm_hooks.h`, `asm/mmu_context_32.h`, `asm-generic/mmu_context.h`, `asm-generic/nommu_context.h`. Key macros/constants include `__ASM_SH_MMU_CONTEXT_H`, `MMU_CONTEXT_ASID_MASK`, `MMU_CONTEXT_VERSION_MASK`, `MMU_CONTEXT_FIRST_VERSION`, `MMU_NO_ASID`, `NO_CONTEXT`, `asid_cache(cpu)`, `cpu_context(cpu, mm)`, `cpu_asid(cpu, mm)`, `MMU_VPN_MASK`, `init_new_context`, `set_asid(asid)`, `get_asid()`, `switch_and_save_asid(asid)`, `set_TTB(pgd)`, `get_TTB()`, `enable_mmu()`, `disable_mmu()`. Structures include `mm_struct`, `task_struct`. Register or hardware-address constants include `__ASM_SH_MMU_CONTEXT_H`, `MMU_CONTEXT_ASID_MASK`, `MMU_CONTEXT_VERSION_MASK`, `MMU_CONTEXT_FIRST_VERSION`, `MMU_NO_ASID`, `MMU_VPN_MASK`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization. MMU and NOMMU builds take different paths, usually replacing fault-tolerant or page-table behavior with direct stubs.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `cpu/mmu_context.h`, `asm/tlbflush.h`, `linux/uaccess.h`, `linux/mm_types.h`, `asm/io.h`, `asm-generic/mm_hooks.h`, `asm/mmu_context_32.h`, `asm-generic/mmu_context.h`, `asm-generic/nommu_context.h`. Kconfig-sensitive paths mention `CONFIG_CPU_HAS_PTEAEX`, `CONFIG_MMU`, `CONFIG_CPU_SH3`, `CONFIG_CPU_SH4`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 178 lines, 4167 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/mmu_context_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/mmu_context_32.h

## Purpose
Provides SH32 helpers for reading and writing the active ASID and translation-table base registers.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_MMU_CONTEXT_32_H`. Register or hardware-address constants include `__ASM_SH_MMU_CONTEXT_32_H`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_HAS_PTEAEX`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 51 lines, 1136 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/mmu_context_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/mmzone.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/mmzone.h

## Purpose
Defines SH architecture declarations and macros for `mmzone` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/numa.h`. Key macros/constants include `__ASM_SH_MMZONE_H`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `linux/numa.h`. Kconfig-sensitive paths mention `CONFIG_NUMA`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 42 lines, 970 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/mmzone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/module.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/module.h

## Purpose
Defines SH module architecture metadata, unwind table storage, and GOT/PLT or FDPIC module state.

## Important APIs, Types, And Functions
Includes `asm-generic/module.h`. Key macros/constants include `_ASM_SH_MODULE_H`. Structures include `mod_arch_specific`, `list_head`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm-generic/module.h`. Kconfig-sensitive paths mention `CONFIG_DWARF_UNWINDER`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 14 lines, 276 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/page.h

## Purpose
Defines SH page geometry, virtual/physical address translation, page flags, clear/copy primitives, and page wrapper types.

## Important APIs, Types, And Functions
Includes `linux/const.h`, `vdso/page.h`, `asm/uncached.h`, `asm-generic/memory_model.h`, `asm-generic/getorder.h`. Key macros/constants include `__ASM_SH_PAGE_H`, `PTE_MASK`, `HPAGE_SHIFT`, `HPAGE_SIZE`, `HPAGE_MASK`, `HUGETLB_PAGE_ORDER`, `clear_page(page)`, `copy_user_page(to, from, vaddr, pg)`, `__HAVE_ARCH_COPY_USER_HIGHPAGE`, `clear_user_highpage`, `pte_val(x)`, `__pte(x)`, `pgd_val(x)`, `pgprot_val(x)`, `__pgd(x)`, `__pgprot(x)`, `pte_pgprot(x)`, `__MEMORY_START`, plus 14 more. Structures include `page`, `vm_area_struct`. Typedefs include `pte_t`, `pgprot_t`, `pgd_t`. Functions or extern declarations include `shm_align_mask`, `min_low_pfn`, `memory_limit`, `copy_page`, `copy_user_highpage`, `clear_user_highpage`. Register or hardware-address constants include `UNCAC_ADDR(addr)`, `CAC_ADDR(addr)`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `linux/const.h`, `vdso/page.h`, `asm/uncached.h`, `asm-generic/memory_model.h`, `asm-generic/getorder.h`. Kconfig-sensitive paths mention `CONFIG_HUGETLB_PAGE_SIZE_64K`, `CONFIG_HUGETLB_PAGE_SIZE_256K`, `CONFIG_HUGETLB_PAGE_SIZE_1MB`, `CONFIG_HUGETLB_PAGE_SIZE_4MB`, `CONFIG_HUGETLB_PAGE_SIZE_64MB`, `CONFIG_HUGETLB_PAGE`, `CONFIG_X2TLB`, `CONFIG_MEMORY_START`, `CONFIG_MEMORY_SIZE`, `CONFIG_PHYSICAL_START`, `CONFIG_PAGE_OFFSET`, `CONFIG_PMB`, `CONFIG_UNCACHED_MAPPING`, `CONFIG_29BIT`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 163 lines, 4711 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/pci.h

## Purpose
Defines SH architecture declarations and macros for `pci` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_PCI_H`, `pcibios_assign_all_busses()`, `HAVE_PCI_MMAP`, `ARCH_GENERIC_PCI_MMAP_RESOURCE`, `PCI_DISABLE_MWI`, `pci_domain_nr(bus)`. Structures include `pci_channel`, `pci_bus`, `pci_ops`, `resource`, `timer_list`. Functions or extern declarations include `pcibios_map_platform_irq`, `pci_config_lock`, `register_pci_controller`, `pcibios_report_status`, `early_read_config_byte`, `early_read_config_word`, `early_read_config_dword`, `early_write_config_byte`, `early_write_config_word`, `early_write_config_dword`, `pcibios_enable_timers`, `pcibios_handle_status_errors`, `pci_is_66mhz_capable`, `PCIBIOS_MIN_MEM`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_PCI`. Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 91 lines, 2844 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/perf_event.h

## Purpose
Provides the SH architecture hook for the generic Linux `perf_event` subsystem, mostly by defining small constants or forwarding to generic helpers.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_PERF_EVENT_H`, `MAX_HWEVENTS`. Structures include `hw_perf_event`, `sh_pmu`. Functions or extern declarations include `register_sh_pmu`, `reserve_pmc_hardware`, `release_pmc_hardware`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 30 lines, 797 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/pgalloc.h

## Purpose
Defines SH architecture declarations and macros for `pgalloc` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/mm.h`, `asm/page.h`, `asm-generic/pgalloc.h`. Key macros/constants include `__ASM_SH_PGALLOC_H`, `__HAVE_ARCH_PMD_ALLOC_ONE`, `__HAVE_ARCH_PMD_FREE`, `__HAVE_ARCH_PGD_FREE`, `__pmd_free_tlb(tlb, pmdp, addr)`, `__pte_free_tlb(tlb, pte, addr)`. Functions or extern declarations include `pgd_alloc`, `pgd_free`, `pud_populate`, `pmd_alloc_one`, `pmd_free`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/mm.h`, `asm/page.h`, `asm-generic/pgalloc.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 38 lines, 1079 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable-2level.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable-2level.h

## Purpose
Defines SH page-table level geometry and index helpers selected by the main page-table header.

## Important APIs, Types, And Functions
Includes `asm-generic/pgtable-nopmd.h`. Key macros/constants include `__ASM_SH_PGTABLE_2LEVEL_H`, `PAGETABLE_LEVELS`, `PTE_MAGNITUDE`, `PTE_SHIFT`, `PTE_BITS`, `PGDIR_SHIFT`, `PTRS_PER_PGD`, `USER_PTRS_PER_PGD`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `asm-generic/pgtable-nopmd.h`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 24 lines, 567 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable-2level.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable-3level.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable-3level.h

## Purpose
Defines SH page-table level geometry and index helpers selected by the main page-table header.

## Important APIs, Types, And Functions
Includes `asm-generic/pgtable-nopud.h`. Key macros/constants include `__ASM_SH_PGTABLE_3LEVEL_H`, `PAGETABLE_LEVELS`, `PTE_MAGNITUDE`, `PGDIR_SHIFT`, `PTRS_PER_PGD`, `USER_PTRS_PER_PGD`, `PMD_SHIFT`, `PMD_SIZE`, `PMD_MASK`, `PTRS_PER_PMD`, `pmd_ERROR(e)`, `pmd_val(x)`, `__pmd(x)`, `pud_page(pud)`, `pud_none(x)`, `pud_present(x)`, `pud_clear(xp)`, `pud_bad(x)`, plus 1 more.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `asm-generic/pgtable-nopud.h`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 59 lines, 1536 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable-3level.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable.h

## Purpose
Connects SH two-level or X2 three-level page-table formats to generic MM, including physical masks, vmalloc bounds, TLB/cache updates, and PTE access checks.

## Important APIs, Types, And Functions
Includes `asm/pgtable-3level.h`, `asm/pgtable-2level.h`, `asm/page.h`, `asm/mmu.h`, `asm/addrspace.h`, `asm/fixmap.h`, `asm/pgtable_32.h`. Key macros/constants include `__ASM_SH_PGTABLE_H`, `NEFF`, `NEFF_SIGN`, `NEFF_MASK`, `NPHYS`, `NPHYS_SIGN`, `NPHYS_MASK`, `PGDIR_SIZE`, `PGDIR_MASK`, `PTRS_PER_PTE`, `PHYS_ADDR_MASK29`, `PHYS_ADDR_MASK32`, `PTE_PHYS_MASK`, `PTE_FLAGS_MASK`, `VMALLOC_START`, `VMALLOC_END`, `pte_pfn(x)`, `update_mmu_cache(vma, addr, ptep)`, plus 3 more. Structures include `vm_area_struct`, `mm_struct`. Functions or extern declarations include `__update_cache`, `__update_tlb`, `paging_init`, `page_table_range_init`. Register or hardware-address constants include `PHYS_ADDR_MASK29`, `PHYS_ADDR_MASK32`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `asm/pgtable-3level.h`, `asm/pgtable-2level.h`, `asm/page.h`, `asm/mmu.h`, `asm/addrspace.h`, `asm/fixmap.h`, `asm/pgtable_32.h`. Kconfig-sensitive paths mention `CONFIG_X2TLB`, `CONFIG_29BIT`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 145 lines, 3745 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable_32.h

## Purpose
Defines SH32 PTE bit layout, page protection templates, cacheability/protection transformations, PTE constructors, and PTE/PMD predicates.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_PGTABLE_32_H`, `_PAGE_WT`, `_PAGE_HW_SHARED`, `_PAGE_DIRTY`, `_PAGE_CACHABLE`, `_PAGE_SZ0`, `_PAGE_RW`, `_PAGE_USER`, `_PAGE_SZ1`, `_PAGE_PRESENT`, `_PAGE_PROTNONE`, `_PAGE_ACCESSED`, `_PAGE_SPECIAL`, `_PAGE_SZ_MASK`, `_PAGE_PR_MASK`, `_PAGE_EXT_ESZ0`, `_PAGE_EXT_ESZ1`, `_PAGE_EXT_ESZ2`, plus 68 more.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization. The same API surface changes behavior across NOMMU, legacy MMU, and X2TLB builds, so Kconfig coverage matters.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_X2TLB`, `CONFIG_CPU_SH3`, `CONFIG_MMU`, `CONFIG_PAGE_SIZE_4KB`, `CONFIG_PAGE_SIZE_8KB`, `CONFIG_PAGE_SIZE_64KB`, `CONFIG_HUGETLB_PAGE_SIZE_64K`, `CONFIG_HUGETLB_PAGE_SIZE_256K`, `CONFIG_HUGETLB_PAGE_SIZE_1MB`, `CONFIG_HUGETLB_PAGE_SIZE_4MB`, `CONFIG_HUGETLB_PAGE_SIZE_64MB`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 482 lines, 16658 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/platform_early.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/platform_early.h

## Purpose
Defines SH architecture declarations and macros for `platform_early` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/types.h`, `linux/platform_device.h`, `linux/pm_runtime.h`, `linux/slab.h`. Key macros/constants include `__PLATFORM_EARLY__`, `EARLY_PLATFORM_ID_UNSET`, `EARLY_PLATFORM_ID_ERROR`, `sh_early_platform_init(class_string, platdrv)`, `sh_early_platform_init_buffer(class_string, platdrv, buf, bufsiz)`. Structures include `sh_early_platform_driver`, `platform_driver`, `list_head`. Functions or extern declarations include `sh_early_platform_driver_register`, `sh_early_platform_add_devices`, `sh_early_platform_driver_register_all`, `sh_early_platform_driver_probe`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/types.h`, `linux/platform_device.h`, `linux/pm_runtime.h`, `linux/slab.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 61 lines, 1849 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/platform_early.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/posix_types.h

## Purpose
Provides the SH architecture hook for the generic Linux `posix_types` subsystem, mostly by defining small constants or forwarding to generic helpers.

## Important APIs, Types, And Functions
Includes `asm/posix_types_32.h`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm/posix_types_32.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 2 lines, 71 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/processor.h

## Purpose
Defines SH CPU/thread state, boot CPU metadata, task sizing, lazy-FPU hooks, user-mode helpers, and processor control declarations.

## Important APIs, Types, And Functions
Includes `asm/cpu-features.h`, `asm/cache.h`, `asm/processor_32.h`. Key macros/constants include `__ASM_SH_PROCESSOR_H`, `boot_cpu_data`, `current_cpu_data`, `raw_current_cpu_data`, `cpu_sleep()`, `cpu_relax()`, `GET_UNALIGN_CTL(tsk, addr)`, `SET_UNALIGN_CTL(tsk, val)`, `SH_THREAD_UAC_NOPRINT`, `SH_THREAD_UAC_SIGBUS`, `SH_THREAD_UAC_MASK`, `MODE_PIN0`, `MODE_PIN1`, `MODE_PIN2`, `MODE_PIN3`, `MODE_PIN4`, `MODE_PIN5`, `MODE_PIN6`, plus 11 more. Structures include `tlb_info`, `sh_cpuinfo`, `cache_info`, `seq_operations`, `task_struct`. Enums include `cpu_type`, `cpu_family`. Functions or extern declarations include `default_idle`, `stop_this_cpu`, `generic_mode_pins`, `test_mode_pin`, `vsyscall_init`, `select_idle_routine`, `fake_swapper_regs`, `cpu_init`, `cpu_probe`, `xstate_size`, `free_thread_xstate`, `task_xstate_cachep`, `get_unalign_ctl`, `set_unalign_ctl`, `mem_init_done`, `cpuinfo_op`, plus 1 more.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `asm/cpu-features.h`, `asm/cache.h`, `asm/processor_32.h`. Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_xxx`, `CONFIG_VSYSCALL`, `CONFIG_CPU_SH2A`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 175 lines, 4319 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/processor_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/processor_32.h

## Purpose
Defines SH32 thread context, trap frame layout helpers, start-thread setup, and architecture-specific register/thread flags.

## Important APIs, Types, And Functions
Includes `linux/compiler.h`, `linux/linkage.h`, `asm/page.h`, `asm/types.h`, `asm/hw_breakpoint.h`. Key macros/constants include `__ASM_SH_PROCESSOR_32_H`, `CCN_PVR`, `CCN_CVR`, `CCN_PRR`, `TASK_SIZE`, `STACK_TOP`, `STACK_TOP_MAX`, `TASK_UNMAPPED_BASE`, `SR_DSP`, `SR_IMASK`, `SR_FD`, `SR_MD`, `SR_USER_MASK`, `INIT_THREAD`, `FPSCR_INIT`, `FPSCR_CAUSE_MASK`, `FPSCR_FLAG_MASK`, `thread_saved_pc(tsk)`, plus 5 more. Structures include `sh_dsp_struct`, `sh_fpu_hard_struct`, `sh_fpu_soft_struct`, `thread_struct`, `perf_event`, `task_struct`, `pt_regs`. Functions or extern declarations include `show_trace`, `show_code`, `start_thread`, `__get_wchan`. Register or hardware-address constants include `TASK_UNMAPPED_BASE`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `linux/compiler.h`, `linux/linkage.h`, `asm/page.h`, `asm/types.h`, `asm/hw_breakpoint.h`. Kconfig-sensitive paths mention `CONFIG_SH_DSP`, `CONFIG_DUMP_CODE`, `CONFIG_CPU_SH2A`, `CONFIG_CPU_SH4`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 203 lines, 4520 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/processor_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/ptrace.h

## Purpose
Defines the SH kernel ptrace register view and maps it to the UAPI ptrace layout for tracing and core-dump users.

## Important APIs, Types, And Functions
Includes `linux/stringify.h`, `linux/stddef.h`, `linux/thread_info.h`, `asm/addrspace.h`, `asm/page.h`, `uapi/asm/ptrace.h`. Key macros/constants include `__ASM_SH_PTRACE_H`, `user_mode(regs)`, `kernel_stack_pointer(_regs)`, `arch_has_single_step()`, `REG_OFFSET_NAME(r)`, `REGS_OFFSET_NAME(num)`, `TREGS_OFFSET_NAME(num)`, `REG_OFFSET_END`, `task_pt_regs(task)`. Structures include `pt_regs_offset`, `perf_event`, `perf_sample_data`. Functions or extern declarations include `regs_query_register_offset`, `regs_query_register_name`, `ptrace_triggered`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/stringify.h`, `linux/stddef.h`, `linux/thread_info.h`, `asm/addrspace.h`, `asm/page.h`, `uapi/asm/ptrace.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 139 lines, 3834 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/ptrace_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/ptrace_32.h

## Purpose
Defines SH architecture declarations and macros for `ptrace_32` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `uapi/asm/ptrace_32.h`. Key macros/constants include `__ASM_SH_PTRACE_32_H`, `MAX_REG_OFFSET`. Register or hardware-address constants include `MAX_REG_OFFSET`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `uapi/asm/ptrace_32.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 14 lines, 307 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/ptrace_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/push-switch.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/push-switch.h

## Purpose
Defines board/peripheral constants, platform data, or callbacks for the SH `push-switch` hardware integration.

## Important APIs, Types, And Functions
Includes `linux/timer.h`, `linux/interrupt.h`, `linux/workqueue.h`, `linux/platform_device.h`. Key macros/constants include `__ASM_SH_PUSH_SWITCH_H`. Structures include `push_switch`, `timer_list`, `work_struct`, `platform_device`, `push_switch_platform_info`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/timer.h`, `linux/interrupt.h`, `linux/workqueue.h`, `linux/platform_device.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 32 lines, 755 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/push-switch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/reboot.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/reboot.h

## Purpose
Defines SH platform hooks for `reboot` memory, power, reset, or timekeeping integration.

## Important APIs, Types, And Functions
Includes `linux/kdebug.h`. Key macros/constants include `__ASM_SH_REBOOT_H`. Structures include `pt_regs`, `machine_ops`. Functions or extern declarations include `native_machine_crash_shutdown`, `machine_ops`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/kdebug.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 22 lines, 472 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/reboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/romimage-macros.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/romimage-macros.h

## Purpose
Defines SH architecture declarations and macros for `romimage-macros` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `__ROMIMAGE_MACRO_H`. Assembly macros include `.macro	LIST comment`, `.macro  ED, addr, data`, `.macro  EW, addr, data`, `.macro  EB, addr, data`, `.macro  WAIT, time`, `.macro  DD, addr, addr2, nr`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 74 lines, 1126 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/romimage-macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/rtc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/rtc.h

## Purpose
Defines SH platform hooks for `rtc` memory, power, reset, or timekeeping integration.

## Important APIs, Types, And Functions
Includes `cpu/rtc.h`. Key macros/constants include `_ASM_RTC_H`, `RTC_CAP_4_DIGIT_YEAR`. Structures include `sh_rtc_platform_info`. Register or hardware-address constants include `_ASM_RTC_H`, `RTC_CAP_4_DIGIT_YEAR`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `cpu/rtc.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 13 lines, 226 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/seccomp.h

## Purpose
Provides the SH architecture hook for the generic Linux `seccomp` subsystem, mostly by defining small constants or forwarding to generic helpers.

## Important APIs, Types, And Functions
Includes `linux/unistd.h`. Key macros/constants include `__NR_seccomp_read`, `__NR_seccomp_write`, `__NR_seccomp_exit`, `__NR_seccomp_sigreturn`, `__SECCOMP_ARCH_LE`, `SECCOMP_ARCH_NATIVE`, `SECCOMP_ARCH_NATIVE_NR`, `SECCOMP_ARCH_NATIVE_NAME`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/unistd.h`. Kconfig-sensitive paths mention `CONFIG_CPU_LITTLE_ENDIAN`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 21 lines, 546 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/sections.h

## Purpose
Defines SH architecture declarations and macros for `sections` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `asm-generic/sections.h`. Key macros/constants include `__ASM_SH_SECTIONS_H`. Functions or extern declarations include `__uncached_end`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm-generic/sections.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 12 lines, 311 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/setup.h

## Purpose
Defines SH architecture declarations and macros for `setup` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `uapi/asm/setup.h`. Key macros/constants include `_SH_SETUP_H`, `PARAM`, `MOUNT_ROOT_RDONLY`, `RAMDISK_FLAGS`, `ORIG_ROOT_DEV`, `LOADER_TYPE`, `INITRD_START`, `INITRD_SIZE`, `COMMAND_LINE`. Functions or extern declarations include `sh_mv_setup`, `check_for_initrd`, `per_cpu_trap_init`, `sh_fdt_init`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `uapi/asm/setup.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 27 lines, 787 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/sfp-machine.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/sfp-machine.h

## Purpose
Defines SH architecture declarations and macros for `sfp-machine` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `_SFP_MACHINE_H`, `__BYTE_ORDER`, `__LITTLE_ENDIAN`, `__BIG_ENDIAN`, `_FP_W_TYPE_SIZE`, `_FP_W_TYPE`, `_FP_WS_TYPE`, `_FP_I_TYPE`, `_FP_MUL_MEAT_S(R,X,Y)`, `_FP_MUL_MEAT_D(R,X,Y)`, `_FP_MUL_MEAT_Q(R,X,Y)`, `_FP_DIV_MEAT_S(R,X,Y)`, `_FP_DIV_MEAT_D(R,X,Y)`, `_FP_DIV_MEAT_Q(R,X,Y)`, `_FP_NANFRAC_S`, `_FP_NANFRAC_D`, `_FP_NANFRAC_Q`, `_FP_NANSIGN_S`, plus 10 more.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 80 lines, 2767 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/sfp-machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/sh7760fb.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/sh7760fb.h

## Purpose
Defines board/peripheral constants, platform data, or callbacks for the SH `sh7760fb` hardware integration.

## Important APIs, Types, And Functions
Key macros/constants include `_ASM_SH_SH7760FB_H`, `SH7760FB_PALETTE_MASK`, `SH7760FB_DMA_MASK`, `LDPR(x)`, `LDICKR`, `LDMTR`, `LDDFR`, `LDDFR_PABD`, `LDDFR_COLOR_MASK`, `LDSMR`, `LDSMR_ROT`, `LDSARU`, `LDSARL`, `LDLAOR`, `LDPALCR`, `LDPALCR_PALS`, `LDPALCR_PALEN`, `LDHCNR`, plus 57 more. Structures include `sh7760fb_platdata`, `fb_videomode`. Register or hardware-address constants include `SH7760FB_DMA_MASK`, `LDPALCR`, `LDMTR_MCNT`, `LDMTR_CL1CNT`, `LDMTR_CL2CNT`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7763`. Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 198 lines, 5740 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/sh7760fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/sh_bios.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/sh_bios.h

## Purpose
Defines board/peripheral constants, platform data, or callbacks for the SH `sh_bios` hardware integration.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_BIOS_H`. Functions or extern declarations include `sh_bios_console_write`, `sh_bios_gdb_detach`, `sh_bios_get_node_addr`, `sh_bios_shutdown`, `sh_bios_vbr_init`, `sh_bios_vbr_reload`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_SH_STANDARD_BIOS`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 28 lines, 743 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/sh_bios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/shmparam.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/shmparam.h

## Purpose
Provides the SH architecture hook for the generic Linux `shmparam` subsystem, mostly by defining small constants or forwarding to generic helpers.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_SHMPARAM_H`, `SHMLBA`, `__ARCH_FORCE_SHMLBA`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 19 lines, 489 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/siu.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/siu.h

## Purpose
Defines board/peripheral constants, platform data, or callbacks for the SH `siu` hardware integration.

## Important APIs, Types, And Functions
Key macros/constants include `ASM_SIU_H`. Structures include `device`, `siu_platform`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 20 lines, 385 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/siu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/smc37c93x.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/smc37c93x.h

## Purpose
Defines board/peripheral constants, platform data, or callbacks for the SH `smc37c93x` hardware integration.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_SMC37C93X_H`, `FDC_PRIMARY_BASE`, `IDE1_PRIMARY_BASE`, `IDE1_SECONDARY_BASE`, `PARPORT_PRIMARY_BASE`, `COM1_PRIMARY_BASE`, `COM2_PRIMARY_BASE`, `RTC_PRIMARY_BASE`, `KBC_PRIMARY_BASE`, `AUXIO_PRIMARY_BASE`, `LDN_FDC`, `LDN_IDE1`, `LDN_IDE2`, `LDN_PARPORT`, `LDN_COM1`, `LDN_COM2`, `LDN_RTC`, `LDN_KBC`, plus 102 more. Structures include `uart_reg`. Register or hardware-address constants include `FDC_PRIMARY_BASE`, `IDE1_PRIMARY_BASE`, `IDE1_SECONDARY_BASE`, `PARPORT_PRIMARY_BASE`, `COM1_PRIMARY_BASE`, `COM2_PRIMARY_BASE`, `RTC_PRIMARY_BASE`, `KBC_PRIMARY_BASE`, `AUXIO_PRIMARY_BASE`, `LDN_RTC`, `CONFIG_PORT`, `INDEX_PORT`, plus 34 more.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_PORT`, `CONFIG_ENTER`, `CONFIG_EXIT`. Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 191 lines, 5700 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/smc37c93x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/smp-ops.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/smp-ops.h

## Purpose
Defines SH architecture declarations and macros for `smp-ops` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_SMP_OPS_H`. Structures include `plat_smp_ops`. Functions or extern declarations include `int`, `mp_ops`, `shx3_smp_ops`, `register_smp_ops`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_SMP`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 53 lines, 1042 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/smp-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/smp.h

## Purpose
Defines SH architecture declarations and macros for `smp` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/bitops.h`, `linux/cpumask.h`, `asm/smp-ops.h`, `linux/atomic.h`, `asm/current.h`, `asm/percpu.h`. Key macros/constants include `__ASM_SH_SMP_H`, `raw_smp_processor_id()`, `cpu_number_map(cpu)`, `cpu_logical_map(cpu)`, `CPU_METHOD_OF_DECLARE(name, _method, _ops)`, `hard_smp_processor_id()`. Structures include `of_cpu_method`, `plat_smp_ops`. Functions or extern declarations include `smp_message_recv`, `arch_send_call_function_single_ipi`, `arch_send_call_function_ipi_mask`, `native_play_dead`, `native_cpu_die`, `native_cpu_disable`, `play_dead_common`, `__cpu_disable`, `mp_ops`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/bitops.h`, `linux/cpumask.h`, `asm/smp-ops.h`, `linux/atomic.h`, `asm/current.h`, `asm/percpu.h`. Kconfig-sensitive paths mention `CONFIG_SMP`, `CONFIG_HOTPLUG_CPU`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 83 lines, 1847 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/sparsemem.h

## Purpose
Defines SH architecture declarations and macros for `sparsemem` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_SPARSEMEM_H`, `SECTION_SIZE_BITS`, `MAX_PHYSMEM_BITS`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 12 lines, 319 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/sparsemem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/spi.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/spi.h

## Purpose
Defines board/peripheral constants, platform data, or callbacks for the SH `spi` hardware integration.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SPI_H__`. Structures include `sh_spi_info`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 14 lines, 265 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/spinlock-cas.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/spinlock-cas.h

## Purpose
Implements SH CAS-based spinlock and rwlock operations for CPU families with compare-and-swap support.

## Important APIs, Types, And Functions
Includes `asm/barrier.h`, `asm/processor.h`. Key macros/constants include `__ASM_SH_SPINLOCK_CAS_H`, `arch_spin_is_locked(x)`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers. Atomicity is implemented by CPU-specific primitives or by interrupt exclusion, so the selected backend must match the SMP and CPU configuration. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
It directly depends on `asm/barrier.h`, `asm/processor.h`. Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 89 lines, 2001 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/spinlock-cas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/spinlock-llsc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/spinlock-llsc.h

## Purpose
Implements SH LL/SC spinlock and rwlock operations with `movli`/`movco`, sleep loops, and explicit synchronization.

## Important APIs, Types, And Functions
Includes `asm/barrier.h`, `asm/processor.h`. Key macros/constants include `__ASM_SH_SPINLOCK_LLSC_H`, `arch_spin_is_locked(x)`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers. Atomicity is implemented by CPU-specific primitives or by interrupt exclusion, so the selected backend must match the SMP and CPU configuration. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
It directly depends on `asm/barrier.h`, `asm/processor.h`. Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 198 lines, 4149 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/spinlock-llsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/spinlock.h

## Purpose
Selects the SH queued/raw spinlock implementation based on SMP and CPU atomic capabilities.

## Important APIs, Types, And Functions
Includes `asm/spinlock-llsc.h`, `asm/spinlock-cas.h`. Key macros/constants include `__ASM_SH_SPINLOCK_H`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
It directly depends on `asm/spinlock-llsc.h`, `asm/spinlock-cas.h`. Kconfig-sensitive paths mention `CONFIG_CPU_SH4A`, `CONFIG_CPU_J2`. Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 19 lines, 438 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/spinlock_types.h

## Purpose
Defines SH architecture declarations and macros for `spinlock_types` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_SPINLOCK_TYPES_H`, `__ARCH_SPIN_LOCK_UNLOCKED`, `RW_LOCK_BIAS`, `__ARCH_RW_LOCK_UNLOCKED`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 22 lines, 469 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/sram.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/sram.h

## Purpose
Defines SH platform hooks for `sram` memory, power, reset, or timekeeping integration.

## Important APIs, Types, And Functions
Includes `linux/spinlock.h`, `linux/genalloc.h`. Key macros/constants include `__ASM_SRAM_H`. Functions or extern declarations include `sram_pool`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/spinlock.h`, `linux/genalloc.h`. Kconfig-sensitive paths mention `CONFIG_HAVE_SRAM_POOL`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 39 lines, 670 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/sram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/stackprotector.h

## Purpose
Defines SH low-level debug, unwind, trace, or linkage contracts for `stackprotector` support.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_STACKPROTECTOR_H`. Functions or extern declarations include `__stack_chk_guard`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 21 lines, 532 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/stacktrace.h

## Purpose
Defines SH low-level debug, unwind, trace, or linkage contracts for `stacktrace` support.

## Important APIs, Types, And Functions
Key macros/constants include `_ASM_SH_STACKTRACE_H`. Structures include `stacktrace_ops`. Functions or extern declarations include `dump_trace`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 21 lines, 528 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/string.h

## Purpose
Defines SH architecture declarations and macros for `string` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `asm/string_32.h`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm/string_32.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 2 lines, 66 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/string_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/string_32.h

## Purpose
Defines SH architecture declarations and macros for `string_32` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_STRING_H`, `__HAVE_ARCH_STRCPY`, `__HAVE_ARCH_STRCMP`, `__HAVE_ARCH_STRNCMP`, `__HAVE_ARCH_MEMSET`, `__HAVE_ARCH_MEMCPY`, `__HAVE_ARCH_MEMMOVE`, `__HAVE_ARCH_MEMCHR`, `__HAVE_ARCH_STRLEN`. Functions or extern declarations include `memset`, `memcpy`, `memmove`, `memchr`, `strlen`.

## Control Flow
Control flow is mostly assembler/preprocessor expansion. The file emits instruction sequences, exception-table records, or linker-section metadata that become executable or discoverable at build time. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State is encoded in generated sections, register save areas, and machine instructions rather than allocated here. Correctness depends on section names and offsets staying synchronized with linker and entry code.

## Dependencies And Integration Points
Integration points are assembler sources, linker script sections, generated offsets, and SH trap/entry code.

## Risks And Edge Cases
Risks are instruction-encoding, branch-delay, section-layout, and register-save mistakes. Small changes can cause boot, trap, or unwind failures that are hard to localize.

## Test Signals
Useful signals are assembler build coverage, objdump inspection of emitted sections, boot/trap smoke tests, unwind verification, and exception-table fixup tests.

Source read size: 102 lines, 2208 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/string_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/suspend.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/suspend.h

## Purpose
Defines SH platform hooks for `suspend` memory, power, reset, or timekeeping integration.

## Important APIs, Types, And Functions
Includes `linux/notifier.h`, `asm/ptrace.h`. Key macros/constants include `_ASM_SH_SUSPEND_H`, `SH_MOBILE_SLEEP_BOARD`, `SH_MOBILE_SLEEP_CPU`, `SH_MOBILE_PRE(x)`, `SH_MOBILE_POST(x)`, `SUSP_SH_SLEEP`, `SUSP_SH_STANDBY`, `SUSP_SH_RSTANDBY`, `SUSP_SH_USTANDBY`, `SUSP_SH_SF`, `SUSP_SH_MMU`, `SUSP_SH_REGS`. Structures include `swsusp_arch_regs`, `pt_regs`, `sh_sleep_regs`, `sh_sleep_data`. Functions or extern declarations include `sh_mobile_call_standby`, `sh_mobile_setup_cpuidle`, `sh_mobile_register_self_refresh`, `sh_mobile_pre_sleep_notifier_list`, `sh_mobile_post_sleep_notifier_list`, `sh_mobile_sleep_supported`. Register or hardware-address constants include `SUSP_SH_REGS`.

## Control Flow
Control flow is mostly assembler/preprocessor expansion. The file emits instruction sequences, exception-table records, or linker-section metadata that become executable or discoverable at build time. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State is encoded in generated sections, register save areas, and machine instructions rather than allocated here. Correctness depends on section names and offsets staying synchronized with linker and entry code.

## Dependencies And Integration Points
It directly depends on `linux/notifier.h`, `asm/ptrace.h`. Kconfig-sensitive paths mention `CONFIG_CPU_IDLE`. Integration points are assembler sources, linker script sections, generated offsets, and SH trap/entry code.

## Risks And Edge Cases
Risks are instruction-encoding, branch-delay, section-layout, and register-save mistakes. Small changes can cause boot, trap, or unwind failures that are hard to localize.

## Test Signals
Useful signals are assembler build coverage, objdump inspection of emitted sections, boot/trap smoke tests, unwind verification, and exception-table fixup tests.

Source read size: 97 lines, 2577 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/suspend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/switch_to.h

## Purpose
Provides SH context-switch declarations or inline assembly used by scheduler task switches.

## Important APIs, Types, And Functions
Includes `asm/switch_to_32.h`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `asm/switch_to_32.h`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 7 lines, 190 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/switch_to_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/switch_to_32.h

## Purpose
Provides SH32 task-switch inline assembly for register save/restore, stack switching, and lazy FPU transfer.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_SWITCH_TO_32_H`, `is_dsp_enabled(tsk)`, `__restore_dsp(tsk)`, `__save_dsp(tsk)`, `switch_to(prev, next, last)`. Structures include `task_struct`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_SH_DSP`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 131 lines, 3631 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/switch_to_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/syscall.h

## Purpose
Declares SH syscall entry, tracing, and wrapper interfaces used by low-level entry code and generic syscall tracing.

## Important APIs, Types, And Functions
Includes `asm/syscall_32.h`. Key macros/constants include `__ASM_SH_SYSCALL_H`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `asm/syscall_32.h`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 9 lines, 201 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/syscall_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/syscall_32.h

## Purpose
Defines SH32 syscall register conventions for tracing, audit architecture reporting, argument extraction, and return-value mutation.

## Important APIs, Types, And Functions
Includes `uapi/linux/audit.h`, `linux/kernel.h`, `linux/sched.h`, `linux/err.h`, `asm/ptrace.h`. Key macros/constants include `__ASM_SH_SYSCALL_32_H`. Structures include `pt_regs`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `uapi/linux/audit.h`, `linux/kernel.h`, `linux/sched.h`, `linux/err.h`, `asm/ptrace.h`. Kconfig-sensitive paths mention `CONFIG_CPU_LITTLE_ENDIAN`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 93 lines, 2257 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/syscall_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/syscalls.h

## Purpose
Declares SH syscall entry, tracing, and wrapper interfaces used by low-level entry code and generic syscall tracing.

## Important APIs, Types, And Functions
Includes `asm/syscalls_32.h`. Key macros/constants include `__ASM_SH_SYSCALLS_H`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `asm/syscalls_32.h`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 15 lines, 532 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/syscalls_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/syscalls_32.h

## Purpose
Declares SH syscall entry, tracing, and wrapper interfaces used by low-level entry code and generic syscall tracing.

## Important APIs, Types, And Functions
Includes `linux/compiler.h`, `linux/linkage.h`, `linux/types.h`. Key macros/constants include `__ASM_SH_SYSCALLS_32_H`. Structures include `pt_regs`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `linux/compiler.h`, `linux/linkage.h`, `linux/types.h`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 27 lines, 979 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/syscalls_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/thread_info.h

## Purpose
Defines SH `thread_info`, low-level task flags, preemption/count layout, and thread-size/alignment contracts used by entry assembly.

## Important APIs, Types, And Functions
Includes `asm/page.h`, `asm/processor.h`. Key macros/constants include `__ASM_SH_THREAD_INFO_H`, `FAULT_CODE_WRITE`, `FAULT_CODE_INITIAL`, `FAULT_CODE_ITLB`, `FAULT_CODE_PROT`, `FAULT_CODE_USER`, `THREAD_SHIFT`, `THREAD_SIZE`, `STACK_WARN`, `INIT_THREAD_INFO(tsk)`, `THREAD_SIZE_ORDER`, `TIF_SYSCALL_TRACE`, `TIF_SIGPENDING`, `TIF_NEED_RESCHED`, `TIF_NOTIFY_SIGNAL`, `TIF_SINGLESTEP`, `TIF_SYSCALL_AUDIT`, `TIF_SECCOMP`, plus 19 more. Structures include `thread_info`, `task_struct`. Functions or extern declarations include `init_thread_xstate`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `asm/page.h`, `asm/processor.h`. Kconfig-sensitive paths mention `CONFIG_4KSTACKS`, `CONFIG_CPU_HAS_SR_RB`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 168 lines, 5077 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/timex.h

## Purpose
Defines SH architecture declarations and macros for `timex` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `asm-generic/timex.h`. Key macros/constants include `__ASM_SH_TIMEX_H`, `CLOCK_TICK_RATE`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm-generic/timex.h`. Kconfig-sensitive paths mention `CONFIG_SH_PCLK_FREQ`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 24 lines, 637 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/tlb.h

## Purpose
Defines SH architecture declarations and macros for `tlb` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/pagemap.h`, `asm-generic/tlb.h`, `linux/swap.h`. Key macros/constants include `__ASM_SH_TLB_H`. Functions or extern declarations include `tlb_wire_entry`, `tlb_unwire_entry`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization. MMU and NOMMU builds take different paths, usually replacing fault-tolerant or page-table behavior with direct stubs.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `linux/pagemap.h`, `asm-generic/tlb.h`, `linux/swap.h`. Kconfig-sensitive paths mention `CONFIG_MMU`, `CONFIG_CPU_SH4`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 33 lines, 740 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/tlbflush.h

## Purpose
Declares SH TLB flush operations and inline/context helpers for range, page, mm, and all-TLB invalidation.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_TLBFLUSH_H`, `flush_tlb_all()`, `flush_tlb_mm(mm)`, `flush_tlb_page(vma, page)`, `flush_tlb_one(asid, page)`, `flush_tlb_range(vma, start, end)`, `flush_tlb_kernel_range(start, end)`. Functions or extern declarations include `local_flush_tlb_all`, `local_flush_tlb_mm`, `local_flush_tlb_range`, `local_flush_tlb_page`, `local_flush_tlb_kernel_range`, `local_flush_tlb_one`, `__flush_tlb_global`, `flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_range`, `flush_tlb_page`, `flush_tlb_kernel_range`, `flush_tlb_one`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_SMP`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 52 lines, 1809 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/topology.h

## Purpose
Provides the SH architecture hook for the generic Linux `topology` subsystem, mostly by defining small constants or forwarding to generic helpers.

## Important APIs, Types, And Functions
Includes `asm-generic/topology.h`. Key macros/constants include `_ASM_SH_TOPOLOGY_H`, `cpu_to_node(cpu)`, `cpumask_of_node(node)`, `pcibus_to_node(bus)`, `cpumask_of_pcibus(bus)`, `mc_capable()`, `topology_core_cpumask(cpu)`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm-generic/topology.h`. Kconfig-sensitive paths mention `CONFIG_NUMA`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 28 lines, 645 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/traps.h

## Purpose
Declares SH trap initialization, exception dispatch, debug handling, die/oops paths, and fault-code helpers.

## Important APIs, Types, And Functions
Includes `linux/compiler.h`, `asm/traps_32.h`. Key macros/constants include `__ASM_SH_TRAPS_H`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `linux/compiler.h`, `asm/traps_32.h`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 18 lines, 424 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/traps_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/traps_32.h

## Purpose
Defines SH architecture declarations and macros for `traps_32` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/types.h`, `asm/mmu.h`. Key macros/constants include `__ASM_SH_TRAPS_32_H`, `lookup_exception_vector()`, `BUILD_TRAP_HANDLER(name)`, `TRAP_HANDLER_DECL`. Structures include `pt_regs`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `linux/types.h`, `asm/mmu.h`. Kconfig-sensitive paths mention `CONFIG_CPU_HAS_SR_RB`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 64 lines, 1458 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/traps_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/types.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/types.h

## Purpose
Provides the SH architecture hook for the generic Linux `types` subsystem, mostly by defining small constants or forwarding to generic helpers.

## Important APIs, Types, And Functions
Includes `asm-generic/int-ll64.h`. Key macros/constants include `__ASM_SH_TYPES_H`. Typedefs include `insn_size_t`, `reg_size_t`.

## Control Flow
Control flow is mostly assembler/preprocessor expansion. The file emits instruction sequences, exception-table records, or linker-section metadata that become executable or discoverable at build time. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State is encoded in generated sections, register save areas, and machine instructions rather than allocated here. Correctness depends on section names and offsets staying synchronized with linker and entry code.

## Dependencies And Integration Points
It directly depends on `asm-generic/int-ll64.h`. Integration points are assembler sources, linker script sections, generated offsets, and SH trap/entry code.

## Risks And Edge Cases
Risks are instruction-encoding, branch-delay, section-layout, and register-save mistakes. Small changes can cause boot, trap, or unwind failures that are hard to localize.

## Test Signals
Useful signals are assembler build coverage, objdump inspection of emitted sections, boot/trap smoke tests, unwind verification, and exception-table fixup tests.

Source read size: 16 lines, 334 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/uaccess.h

## Purpose
Implements SH user-memory access policy and copy helpers, including access-limit checks, address validation, and clear/copy/string entry points.

## Important APIs, Types, And Functions
Includes `asm/extable.h`, `asm-generic/access_ok.h`, `asm/uaccess_32.h`. Key macros/constants include `__ASM_SH_UACCESS_H`, `put_user(x,ptr)`, `get_user(x,ptr)`, `__put_user(x,ptr)`, `__get_user(x,ptr)`, `__m(x)`, `__get_user_nocheck(x,ptr,size)`, `__get_user_check(x,ptr,size)`, `__put_user_nocheck(x,ptr,size)`, `__put_user_check(x,ptr,size)`, `INLINE_COPY_FROM_USER`, `INLINE_COPY_TO_USER`, `clear_user(addr,n)`. Structures include `__large_struct`, `mem_access`. Functions or extern declarations include `long`, `handle_unaligned_access`, `strncpy_from_user`, `strnlen_user`, `set_exception_table_vec`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `asm/extable.h`, `asm-generic/access_ok.h`, `asm/uaccess_32.h`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 133 lines, 4145 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/uaccess_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/uaccess_32.h

## Purpose
Implements SH32 inline `get_user`/`put_user` assembly with exception-table fixups and endian-aware 64-bit user access.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_UACCESS_32_H`, `__get_user_size(x,ptr,size,retval)`, `__get_user_asm(x, addr, err, insn)`, `__get_user_u64(x, addr, err)`, `__put_user_size(x,ptr,size,retval)`, `__put_user_asm(x, addr, err, insn)`, `__put_user_u64(val,addr,retval)`. Functions or extern declarations include `__get_user_unknown`, `__put_user_unknown`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization. Exception-table fixups are present, so faulting loads/stores must branch to the listed recovery labels and return `-EFAULT` or an equivalent safe result. MMU and NOMMU builds take different paths, usually replacing fault-tolerant or page-table behavior with direct stubs. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_MMU`, `CONFIG_CPU_LITTLE_ENDIAN`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 227 lines, 5007 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/uaccess_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/uncached.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/uncached.h

## Purpose
Defines SH platform hooks for `uncached` memory, power, reset, or timekeeping integration.

## Important APIs, Types, And Functions
Includes `linux/bug.h`. Key macros/constants include `__ASM_SH_UNCACHED_H`, `jump_to_uncached()`, `back_to_cached()`, `virt_addr_uncached(kaddr)`, `uncached_init()`, `uncached_resize(size)`. Functions or extern declarations include `cached_to_uncached`, `uncached_size`, `uncached_end`, `virt_addr_uncached`, `uncached_init`, `uncached_resize`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `linux/bug.h`. Kconfig-sensitive paths mention `CONFIG_UNCACHED_MAPPING`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 59 lines, 1372 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/uncached.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/unistd.h

## Purpose
Defines SH architecture declarations and macros for `unistd` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `asm/unistd_32.h`, `uapi/asm/unistd.h`. Key macros/constants include `NR_syscalls`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_OLD_READDIR`, `__ARCH_WANT_OLD_STAT`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_ALARM`, `__ARCH_WANT_SYS_GETHOSTNAME`, `__ARCH_WANT_SYS_IPC`, `__ARCH_WANT_SYS_PAUSE`, `__ARCH_WANT_SYS_SIGNAL`, `__ARCH_WANT_SYS_TIME32`, `__ARCH_WANT_SYS_UTIME32`, `__ARCH_WANT_SYS_WAITPID`, `__ARCH_WANT_SYS_SOCKETCALL`, `__ARCH_WANT_SYS_FADVISE64`, `__ARCH_WANT_SYS_GETPGRP`, `__ARCH_WANT_SYS_NICE`, `__ARCH_WANT_SYS_OLD_GETRLIMIT`, plus 8 more.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm/unistd_32.h`, `uapi/asm/unistd.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 33 lines, 953 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/unwinder.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/unwinder.h

## Purpose
Defines SH low-level debug, unwind, trace, or linkage contracts for `unwinder` support.

## Important APIs, Types, And Functions
Includes `asm/stacktrace.h`. Key macros/constants include `_LINUX_UNWINDER_H`. Structures include `unwinder`, `list_head`. Functions or extern declarations include `unwinder_init`, `unwinder_register`, `unwind_stack`, `stack_reader_dump`, `unwinder_faulted`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
It directly depends on `asm/stacktrace.h`. Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 32 lines, 856 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/unwinder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/user.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/user.h

## Purpose
Defines SH architecture declarations and macros for `user` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `asm/ptrace.h`, `asm/page.h`. Key macros/constants include `__ASM_SH_USER_H`. Structures include `user_fpu_struct`, `user`, `pt_regs`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm/ptrace.h`, `asm/page.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 55 lines, 2244 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/vermagic.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/vermagic.h

## Purpose
Defines SH architecture declarations and macros for `vermagic` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `_ASM_VERMAGIC_H`, `MODULE_PROC_FAMILY`, `MODULE_ARCH_VERMAGIC`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_LITTLE_ENDIAN`, `CONFIG_CPU_SH2`, `CONFIG_CPU_SH3`, `CONFIG_CPU_SH4`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 30 lines, 709 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/vmalloc.h

## Purpose
Defines SH platform hooks for `vmalloc` memory, power, reset, or timekeeping integration.

## Important APIs, Types, And Functions
Key macros/constants include `_ASM_SH_VMALLOC_H`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 4 lines, 84 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/vmlinux.lds.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/vmlinux.lds.h

## Purpose
Defines SH linker-script fragments for trap tables, DWARF unwind tables, exception tables, and architecture sections.

## Important APIs, Types, And Functions
Includes `asm-generic/vmlinux.lds.h`. Key macros/constants include `__ASM_SH_VMLINUX_LDS_H`, `DWARF_EH_FRAME`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm-generic/vmlinux.lds.h`. Kconfig-sensitive paths mention `CONFIG_DWARF_UNWINDER`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 18 lines, 416 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/vmlinux.lds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/watchdog.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/watchdog.h

## Purpose
Defines SH platform hooks for `watchdog` memory, power, reset, or timekeeping integration.

## Important APIs, Types, And Functions
Includes `linux/types.h`, `linux/io.h`, `cpu/watchdog.h`. Key macros/constants include `__ASM_SH_WATCHDOG_H`, `WTCNT_HIGH`, `WTCSR_HIGH`, `WTCSR_CKS2`, `WTCSR_CKS1`, `WTCSR_CKS0`, `WTCNT_R`, `WTCSR_R`, `WTCSR_CKS_32`, `WTCSR_CKS_64`, `WTCSR_CKS_128`, `WTCSR_CKS_256`, `WTCSR_CKS_512`, `WTCSR_CKS_1024`, `WTCSR_CKS_2048`, `WTCSR_CKS_4096`. Register or hardware-address constants include `WTCNT_HIGH`, `WTCSR_HIGH`, `WTCSR_CKS2`, `WTCSR_CKS1`, `WTCSR_CKS0`, `WTCNT_R`, `WTCSR_R`, `WTCSR_CKS_32`, `WTCSR_CKS_64`, `WTCSR_CKS_128`, `WTCSR_CKS_256`, `WTCSR_CKS_512`, plus 3 more.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/types.h`, `linux/io.h`, `cpu/watchdog.h`. Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7785`, `CONFIG_CPU_SUBTYPE_SH7780`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 159 lines, 3981 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/watchdog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/word-at-a-time.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/word-at-a-time.h

## Purpose
Defines SH architecture declarations and macros for `word-at-a-time` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `asm-generic/word-at-a-time.h`, `linux/bitops.h`, `linux/wordpart.h`. Key macros/constants include `__ASM_SH_WORD_AT_A_TIME_H`, `WORD_AT_A_TIME_CONSTANTS`, `zero_bytemask(mask)`. Structures include `word_at_a_time`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm-generic/word-at-a-time.h`, `linux/bitops.h`, `linux/wordpart.h`. Kconfig-sensitive paths mention `CONFIG_CPU_BIG_ENDIAN`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 56 lines, 1375 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/word-at-a-time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/addrspace.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/addrspace.h

## Purpose
Defines CPU-family virtual segment base addresses and physical-area aliases consumed by SH address translation helpers.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH2_ADDRSPACE_H`, `P0SEG`, `P1SEG`, `P2SEG`, `P3SEG`, `P4SEG`. Register or hardware-address constants include `__ASM_CPU_SH2_ADDRSPACE_H`, `P0SEG`, `P1SEG`, `P2SEG`, `P3SEG`, `P4SEG`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 16 lines, 375 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/addrspace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/mmu_context.h

## Purpose
Implements SH MMU context allocation, ASID versioning, TTB programming, address-space switching, and MMU enable/disable helpers.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH2_MMU_CONTEXT_H`. Register or hardware-address constants include `__ASM_CPU_SH2_MMU_CONTEXT_H`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 13 lines, 249 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/pfc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/pfc.h

## Purpose
Declares pin-function-controller registration for CPU-common SH pinmux integration.

## Important APIs, Types, And Functions
Includes `linux/types.h`. Key macros/constants include `__ARCH_SH_CPU_PFC_H__`. Structures include `resource`. Functions or extern declarations include `sh_pfc_register`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
It directly depends on `linux/types.h`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 18 lines, 368 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/pfc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/rtc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/rtc.h

## Purpose
Defines CPU-family RTC register width and capability flags used by the SH RTC driver.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_CPU_SH2_RTC_H`, `rtc_reg_size`, `RTC_BIT_INVERTED`, `RTC_DEF_CAPABILITIES`. Register or hardware-address constants include `__ASM_SH_CPU_SH2_RTC_H`, `RTC_BIT_INVERTED`, `RTC_DEF_CAPABILITIES`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 9 lines, 233 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/sigcontext.h

## Purpose
Defines CPU-family signal context layout exposed to signal delivery and restoration code.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH2_SIGCONTEXT_H`. Structures include `sigcontext`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 18 lines, 385 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/timer.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/timer.h

## Purpose
Provides CPU-common timer header hooks for SH timer integration.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH2_TIMER_H`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 7 lines, 161 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-common/cpu/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2/cpu/cache.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2/cpu/cache.h

## Purpose
Defines CPU-family cacheline sizing, cache-control register addresses, cache mode bits, and cache-array address constants.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH2_CACHE_H`, `L1_CACHE_SHIFT`, `SH_CACHE_VALID`, `SH_CACHE_UPDATED`, `SH_CACHE_COMBINED`, `SH_CACHE_ASSOC`, `SH_CCR`, `CCR_CACHE_CE`, `CCR_CACHE_WT`, `CCR_CACHE_CB`, `CCR_CACHE_CF`, `CACHE_OC_ADDRESS_ARRAY`, `CACHE_OC_DATA_ARRAY`, `CCR_CACHE_ENABLE`, `CCR_CACHE_INVALIDATE`, `CACHE_PHYSADDR_MASK`. Register or hardware-address constants include `SH_CCR`, `CACHE_OC_ADDRESS_ARRAY`, `CACHE_PHYSADDR_MASK`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7619`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 40 lines, 1167 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2/cpu/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2/cpu/freq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2/cpu/freq.h

## Purpose
Defines CPU-family clock/frequency-control register addresses and divisor limits used by clock initialization code.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH2_FREQ_H`, `FREQCR`. Register or hardware-address constants include `FREQCR`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7619`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 15 lines, 284 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2/cpu/freq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2/cpu/watchdog.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2/cpu/watchdog.h

## Purpose
Defines CPU-family watchdog timer registers, reset/status bits, and access helpers for reset-cause handling.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH2_WATCHDOG_H`, `WTCNT`, `WTCSR`, `RSTCSR`, `WTCNT_R`, `RSTCSR_R`, `WTCSR_IOVF`, `WTCSR_WT`, `WTCSR_TME`, `WTCSR_RSTS`, `RSTCSR_RSTS`. Register or hardware-address constants include `WTCNT`, `WTCSR`, `RSTCSR`, `WTCNT_R`, `WTCSR_IOVF`, `WTCSR_WT`, `WTCSR_TME`, `WTCSR_RSTS`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 66 lines, 1631 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2/cpu/watchdog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/addrspace.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/addrspace.h

## Purpose
Defines CPU-family virtual segment base addresses and physical-area aliases consumed by SH address translation helpers.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_CPU_SH2A_ADDRSPACE_H`, `P0SEG`, `P1SEG`, `P2SEG`, `P3SEG`, `P4SEG`. Register or hardware-address constants include `__ASM_SH_CPU_SH2A_ADDRSPACE_H`, `P0SEG`, `P1SEG`, `P2SEG`, `P3SEG`, `P4SEG`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 11 lines, 290 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/addrspace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/cache.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/cache.h

## Purpose
Defines CPU-family cacheline sizing, cache-control register addresses, cache mode bits, and cache-array address constants.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH2A_CACHE_H`, `L1_CACHE_SHIFT`, `SH_CACHE_VALID`, `SH_CACHE_UPDATED`, `SH_CACHE_COMBINED`, `SH_CACHE_ASSOC`, `SH_CCR`, `SH_CCR2`, `CCR_CACHE_CB`, `CCR_CACHE_OCE`, `CCR_CACHE_WT`, `CCR_CACHE_OCI`, `CCR_CACHE_ICE`, `CCR_CACHE_ICI`, `CACHE_IC_ADDRESS_ARRAY`, `CACHE_OC_ADDRESS_ARRAY`, `CCR_CACHE_ENABLE`, `CCR_CACHE_INVALIDATE`, plus 3 more. Register or hardware-address constants include `SH_CCR`, `CACHE_IC_ADDRESS_ARRAY`, `CACHE_OC_ADDRESS_ARRAY`, `CACHE_PHYSADDR_MASK`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 40 lines, 1062 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/freq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/freq.h

## Purpose
Defines CPU-family clock/frequency-control register addresses and divisor limits used by clock initialization code.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH2A_FREQ_H`, `FREQCR`. Register or hardware-address constants include `FREQCR`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 13 lines, 242 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/freq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/rtc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/rtc.h

## Purpose
Defines CPU-family RTC register width and capability flags used by the SH RTC driver.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_CPU_SH2A_RTC_H`, `rtc_reg_size`, `RTC_BIT_INVERTED`, `RTC_DEF_CAPABILITIES`. Register or hardware-address constants include `__ASM_SH_CPU_SH2A_RTC_H`, `RTC_BIT_INVERTED`, `RTC_DEF_CAPABILITIES`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 9 lines, 253 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/sh7203.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/sh7203.h

## Purpose
Defines CPU-subtype IRQ/event, DMA, GPIO, timer, and peripheral enumeration constants for the named SH SoC family.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH7203_H__`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers. Most values are SoC event or peripheral identifiers; consumers typically pass them through `evt2irq()` or platform-resource registration.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 144 lines, 5250 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/sh7203.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/sh7264.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/sh7264.h

## Purpose
Defines CPU-subtype IRQ/event, DMA, GPIO, timer, and peripheral enumeration constants for the named SH SoC family.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH7264_H__`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers. Most values are SoC event or peripheral identifiers; consumers typically pass them through `evt2irq()` or platform-resource registration.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 169 lines, 5259 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/sh7264.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/sh7269.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/sh7269.h

## Purpose
Defines CPU-subtype IRQ/event, DMA, GPIO, timer, and peripheral enumeration constants for the named SH SoC family.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH7269_H__`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers. Most values are SoC event or peripheral identifiers; consumers typically pass them through `evt2irq()` or platform-resource registration.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 213 lines, 7506 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/sh7269.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/watchdog.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/watchdog.h

## Purpose
Defines CPU-family watchdog timer registers, reset/status bits, and access helpers for reset-cause handling.

## Important APIs, Types, And Functions
Includes `cpu-sh2/cpu/watchdog.h`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
It directly depends on `cpu-sh2/cpu/watchdog.h`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 2 lines, 73 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh2a/cpu/watchdog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/adc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/adc.h

## Purpose
Defines SH architecture declarations and macros for `adc` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH3_ADC_H`, `ADDRAH`, `ADDRAL`, `ADDRBH`, `ADDRBL`, `ADDRCH`, `ADDRCL`, `ADDRDH`, `ADDRDL`, `ADCSR`, `ADCSR_ADF`, `ADCSR_ADIE`, `ADCSR_ADST`, `ADCSR_MULTI`, `ADCSR_CKS`, `ADCSR_CH_MASK`, `ADCR`. Register or hardware-address constants include `ADDRAH`, `ADDRAL`, `ADDRBH`, `ADDRBL`, `ADDRCH`, `ADDRCL`, `ADDRDH`, `ADDRDL`, `ADCSR`, `ADCR`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 29 lines, 582 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/adc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/cache.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/cache.h

## Purpose
Defines CPU-family cacheline sizing, cache-control register addresses, cache mode bits, and cache-array address constants.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH3_CACHE_H`, `L1_CACHE_SHIFT`, `SH_CACHE_VALID`, `SH_CACHE_UPDATED`, `SH_CACHE_COMBINED`, `SH_CACHE_ASSOC`, `SH_CCR`, `CCR_CACHE_CE`, `CCR_CACHE_WT`, `CCR_CACHE_CB`, `CCR_CACHE_CF`, `CCR_CACHE_ORA`, `CACHE_OC_ADDRESS_ARRAY`, `CACHE_PHYSADDR_MASK`, `CCR_CACHE_ENABLE`, `CCR_CACHE_INVALIDATE`, `CCR3_REG`, `CCR_CACHE_16KB`, plus 1 more. Register or hardware-address constants include `SH_CCR`, `CACHE_OC_ADDRESS_ARRAY`, `CACHE_PHYSADDR_MASK`, `CCR3_REG`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7705`, `CONFIG_CPU_SUBTYPE_SH7710`, `CONFIG_CPU_SUBTYPE_SH7720`, `CONFIG_CPU_SUBTYPE_SH7721`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 40 lines, 1134 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/dac.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/dac.h

## Purpose
Defines SH architecture declarations and macros for `dac` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/io.h`. Key macros/constants include `__ASM_CPU_SH3_DAC_H`, `DADR0`, `DADR1`, `DACR`, `DACR_DAOE1`, `DACR_DAOE0`, `DACR_DAE`. Register or hardware-address constants include `DACR`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
It directly depends on `linux/io.h`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 44 lines, 832 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/dac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/dma-register.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/dma-register.h

## Purpose
Defines CPU-family DMAC channel-control transfer-size encoding, DMAOR initialization, and transfer-size conversion tables.

## Important APIs, Types, And Functions
Key macros/constants include `CPU_DMA_REGISTER_H`, `CHCR_TS_LOW_MASK`, `CHCR_TS_LOW_SHIFT`, `CHCR_TS_HIGH_MASK`, `CHCR_TS_HIGH_SHIFT`, `DMAOR_INIT`, `TS_SHIFT`, `TS_INDEX2VAL(i)`. Register or hardware-address constants include `CPU_DMA_REGISTER_H`, `DMAOR_INIT`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 38 lines, 855 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/dma-register.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/dma.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/dma.h

## Purpose
Defines CPU-family DMAC base addresses and interrupt event mappings used by the SH DMA engine.

## Important APIs, Types, And Functions
Includes `linux/sh_intc.h`. Key macros/constants include `__ASM_CPU_SH3_DMA_H`, `SH_DMAC_BASE0`, `DMTE0_IRQ`, `DMTE4_IRQ`. Register or hardware-address constants include `__ASM_CPU_SH3_DMA_H`, `SH_DMAC_BASE0`, `DMTE0_IRQ`, `DMTE4_IRQ`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
It directly depends on `linux/sh_intc.h`. Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7720`, `CONFIG_CPU_SUBTYPE_SH7721`, `CONFIG_CPU_SUBTYPE_SH7710`, `CONFIG_CPU_SUBTYPE_SH7712`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 19 lines, 497 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/freq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/freq.h

## Purpose
Defines CPU-family clock/frequency-control register addresses and divisor limits used by clock initialization code.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH3_FREQ_H`, `FRQCR`, `MIN_DIVISOR_NR`, `MAX_DIVISOR_NR`, `FRQCR_CKOEN`, `FRQCR_PLLEN`, `FRQCR_PSTBY`. Register or hardware-address constants include `FRQCR`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7712`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 24 lines, 448 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/freq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/gpio.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/gpio.h

## Purpose
Defines SH architecture declarations and macros for `gpio` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `_CPU_SH3_GPIO_H`, `PORT_PACR`, `PORT_PBCR`, `PORT_PCCR`, `PORT_PDCR`, `PORT_PECR`, `PORT_PFCR`, `PORT_PGCR`, `PORT_PHCR`, `PORT_PJCR`, `PORT_PKCR`, `PORT_PLCR`, `PORT_PMCR`, `PORT_PPCR`, `PORT_PRCR`, `PORT_PSCR`, `PORT_PTCR`, `PORT_PUCR`, plus 23 more. Register or hardware-address constants include `PORT_PACR`, `PORT_PBCR`, `PORT_PCCR`, `PORT_PDCR`, `PORT_PECR`, `PORT_PFCR`, `PORT_PGCR`, `PORT_PHCR`, `PORT_PJCR`, `PORT_PKCR`, `PORT_PLCR`, `PORT_PMCR`, plus 6 more.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7720`, `CONFIG_CPU_SUBTYPE_SH7721`, `CONFIG_CPU_SUBTYPE_SH7709`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 78 lines, 2108 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/mmu_context.h

## Purpose
Implements SH MMU context allocation, ASID versioning, TTB programming, address-space switching, and MMU enable/disable helpers.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH3_MMU_CONTEXT_H`, `MMU_PTEH`, `MMU_PTEL`, `MMU_TTB`, `MMU_TEA`, `MMUCR`, `MMUCR_TI`, `MMU_TLB_ADDRESS_ARRAY`, `MMU_PAGE_ASSOC_BIT`, `MMU_NTLB_ENTRIES`, `MMU_NTLB_WAYS`, `MMU_CONTROL_INIT`, `TRA`, `EXPEVT`, `INTEVT`. Register or hardware-address constants include `__ASM_CPU_SH3_MMU_CONTEXT_H`, `MMU_PTEH`, `MMU_PTEL`, `MMU_TTB`, `MMU_TEA`, `MMUCR`, `MMU_TLB_ADDRESS_ARRAY`, `MMU_PAGE_ASSOC_BIT`, `MMU_NTLB_ENTRIES`, `MMU_NTLB_WAYS`, `MMU_CONTROL_INIT`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7705`, `CONFIG_CPU_SUBTYPE_SH7706`, `CONFIG_CPU_SUBTYPE_SH7707`, `CONFIG_CPU_SUBTYPE_SH7709`, `CONFIG_CPU_SUBTYPE_SH7710`, `CONFIG_CPU_SUBTYPE_SH7712`, `CONFIG_CPU_SUBTYPE_SH7720`, `CONFIG_CPU_SUBTYPE_SH7721`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 42 lines, 1282 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/serial.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/serial.h

## Purpose
Defines SH architecture declarations and macros for `serial` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/serial_sci.h`. Key macros/constants include `__CPU_SH3_SERIAL_H`. Functions or extern declarations include `sh770x_sci_port_ops`, `sh7710_sci_port_ops`, `sh7720_sci_port_ops`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
It directly depends on `linux/serial_sci.h`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 11 lines, 317 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/sh7720.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/sh7720.h

## Purpose
Defines CPU-subtype IRQ/event, DMA, GPIO, timer, and peripheral enumeration constants for the named SH SoC family.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH7720_H__`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers. Most values are SoC event or peripheral identifiers; consumers typically pass them through `evt2irq()` or platform-resource registration.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 175 lines, 4563 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/sh7720.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/watchdog.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/watchdog.h

## Purpose
Defines CPU-family watchdog timer registers, reset/status bits, and access helpers for reset-cause handling.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH3_WATCHDOG_H`, `WTCNT`, `WTCSR`, `WTCSR_TME`, `WTCSR_WT`, `WTCSR_RSTS`, `WTCSR_WOVF`, `WTCSR_IOVF`. Register or hardware-address constants include `WTCNT`, `WTCSR`, `WTCSR_TME`, `WTCSR_WT`, `WTCSR_RSTS`, `WTCSR_WOVF`, `WTCSR_IOVF`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 22 lines, 448 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/watchdog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/addrspace.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/addrspace.h

## Purpose
Defines CPU-family virtual segment base addresses and physical-area aliases consumed by SH address translation helpers.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH4_ADDRSPACE_H`, `P0SEG`, `P1SEG`, `P2SEG`, `P3SEG`, `P4SEG`, `P4SEG_STORE_QUE`, `P4SEG_IC_ADDR`, `P4SEG_IC_DATA`, `P4SEG_ITLB_ADDR`, `P4SEG_ITLB_DATA`, `P4SEG_OC_ADDR`, `P4SEG_OC_DATA`, `P4SEG_TLB_ADDR`, `P4SEG_TLB_DATA`, `P4SEG_REG_BASE`, `PA_AREA0`, `PA_AREA1`, plus 8 more. Register or hardware-address constants include `__ASM_CPU_SH4_ADDRSPACE_H`, `P0SEG`, `P1SEG`, `P2SEG`, `P3SEG`, `P4SEG`, `P4SEG_STORE_QUE`, `P4SEG_IC_ADDR`, `P4SEG_IC_DATA`, `P4SEG_ITLB_ADDR`, `P4SEG_ITLB_DATA`, `P4SEG_OC_ADDR`, plus 4 more.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 41 lines, 1069 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/addrspace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/cache.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/cache.h

## Purpose
Defines CPU-family cacheline sizing, cache-control register addresses, cache mode bits, and cache-array address constants.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH4_CACHE_H`, `L1_CACHE_SHIFT`, `SH_CACHE_VALID`, `SH_CACHE_UPDATED`, `SH_CACHE_COMBINED`, `SH_CACHE_ASSOC`, `SH_CCR`, `CCR_CACHE_OCE`, `CCR_CACHE_WT`, `CCR_CACHE_CB`, `CCR_CACHE_OCI`, `CCR_CACHE_ORA`, `CCR_CACHE_OIX`, `CCR_CACHE_ICE`, `CCR_CACHE_ICI`, `CCR_CACHE_IIX`, `CCR_CACHE_EMODE`, `CCR_CACHE_ENABLE`, plus 4 more. Register or hardware-address constants include `SH_CCR`, `CACHE_IC_ADDRESS_ARRAY`, `CACHE_OC_ADDRESS_ARRAY`, `RAMCR`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SH4A`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 41 lines, 1298 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/dma-register.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/dma-register.h

## Purpose
Defines CPU-family DMAC channel-control transfer-size encoding, DMAOR initialization, and transfer-size conversion tables.

## Important APIs, Types, And Functions
Key macros/constants include `CPU_DMA_REGISTER_H`, `DMAOR_INIT`, `CHCR_TS_LOW_MASK`, `CHCR_TS_LOW_SHIFT`, `CHCR_TS_HIGH_MASK`, `CHCR_TS_HIGH_SHIFT`, `TS_SHIFT`, `TS_INDEX2VAL(i)`. Register or hardware-address constants include `CPU_DMA_REGISTER_H`, `DMAOR_INIT`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SH4A`, `CONFIG_CPU_SUBTYPE_SH7343`, `CONFIG_CPU_SUBTYPE_SH7722`, `CONFIG_CPU_SUBTYPE_SH7723`, `CONFIG_CPU_SUBTYPE_SH7724`, `CONFIG_CPU_SUBTYPE_SH7730`, `CONFIG_CPU_SUBTYPE_SH7786`, `CONFIG_CPU_SUBTYPE_SH7757`, `CONFIG_CPU_SUBTYPE_SH7763`, `CONFIG_CPU_SUBTYPE_SH7780`, `CONFIG_CPU_SUBTYPE_SH7785`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 98 lines, 2507 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/dma-register.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/dma.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/dma.h

## Purpose
Defines CPU-family DMAC base addresses and interrupt event mappings used by the SH DMA engine.

## Important APIs, Types, And Functions
Includes `linux/sh_intc.h`. Key macros/constants include `__ASM_CPU_SH4_DMA_H`, `DMTE0_IRQ`, `DMTE4_IRQ`, `DMTE6_IRQ`, `DMAE0_IRQ`, `SH_DMAC_BASE0`. Register or hardware-address constants include `__ASM_CPU_SH4_DMA_H`, `DMTE0_IRQ`, `DMTE4_IRQ`, `DMTE6_IRQ`, `DMAE0_IRQ`, `SH_DMAC_BASE0`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
It directly depends on `linux/sh_intc.h`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 17 lines, 355 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/fpu.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/fpu.h

## Purpose
Defines SH architecture declarations and macros for `fpu` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `__CPU_SH4_FPU_H`, `FPSCR_ENABLE_MASK`, `FPSCR_FMOV_DOUBLE`, `FPSCR_CAUSE_INEXACT`, `FPSCR_CAUSE_UNDERFLOW`, `FPSCR_CAUSE_OVERFLOW`, `FPSCR_CAUSE_DIVZERO`, `FPSCR_CAUSE_INVALID`, `FPSCR_CAUSE_ERROR`, `FPSCR_DBL_PRECISION`, `FPSCR_ROUNDING_MODE(x)`, `FPSCR_RM_NEAREST`, `FPSCR_RM_ZERO`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 30 lines, 708 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/freq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/freq.h

## Purpose
Defines CPU-family clock/frequency-control register addresses and divisor limits used by clock initialization code.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH4_FREQ_H`, `FRQCR`, `VCLKCR`, `SCLKACR`, `SCLKBCR`, `IrDACLKCR`, `MSTPCR0`, `MSTPCR1`, `MSTPCR2`, `OSCCR`, `PLLCR`, `FRQCRA`, `FRQCRB`, `FCLKACR`, `FCLKBCR`, `FRQCR0`, `FRQCR2`, `FRQMR1`, plus 7 more. Register or hardware-address constants include `FRQCR`, `VCLKCR`, `SCLKACR`, `SCLKBCR`, `IrDACLKCR`, `OSCCR`, `PLLCR`, `FCLKACR`, `FCLKBCR`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7722`, `CONFIG_CPU_SUBTYPE_SH7723`, `CONFIG_CPU_SUBTYPE_SH7343`, `CONFIG_CPU_SUBTYPE_SH7366`, `CONFIG_CPU_SUBTYPE_SH7757`, `CONFIG_CPU_SUBTYPE_SH7763`, `CONFIG_CPU_SUBTYPE_SH7780`, `CONFIG_CPU_SUBTYPE_SH7724`, `CONFIG_CPU_SUBTYPE_SH7734`, `CONFIG_CPU_SUBTYPE_SH7785`, `CONFIG_CPU_SUBTYPE_SH7786`, `CONFIG_CPU_SUBTYPE_SHX3`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 74 lines, 1995 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/freq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/mmu_context.h

## Purpose
Implements SH MMU context allocation, ASID versioning, TTB programming, address-space switching, and MMU enable/disable helpers.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH4_MMU_CONTEXT_H`, `MMU_PTEH`, `MMU_PTEL`, `MMU_TTB`, `MMU_TEA`, `MMU_PTEA`, `MMU_PTEAEX`, `MMUCR`, `MMU_TLB_ENTRY_SHIFT`, `MMU_ITLB_ADDRESS_ARRAY`, `MMU_ITLB_ADDRESS_ARRAY2`, `MMU_ITLB_DATA_ARRAY`, `MMU_ITLB_DATA_ARRAY2`, `MMU_UTLB_ADDRESS_ARRAY`, `MMU_UTLB_ADDRESS_ARRAY2`, `MMU_UTLB_DATA_ARRAY`, `MMU_UTLB_DATA_ARRAY2`, `MMU_PAGE_ASSOC_BIT`, plus 16 more. Register or hardware-address constants include `__ASM_CPU_SH4_MMU_CONTEXT_H`, `MMU_PTEH`, `MMU_PTEL`, `MMU_TTB`, `MMU_TEA`, `MMU_PTEA`, `MMU_PTEAEX`, `MMUCR`, `MMU_TLB_ENTRY_SHIFT`, `MMU_ITLB_ADDRESS_ARRAY`, `MMU_ITLB_ADDRESS_ARRAY2`, `MMU_ITLB_DATA_ARRAY`, plus 8 more.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers. The same API surface changes behavior across NOMMU, legacy MMU, and X2TLB builds, so Kconfig coverage matters.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_MMU`, `CONFIG_32BIT`, `CONFIG_CPU_SUBTYPE_ST40`, `CONFIG_CPU_HAS_PTEAEX`, `CONFIG_X2TLB`, `CONFIG_SH_STORE_QUEUES`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 79 lines, 1919 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/rtc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/rtc.h

## Purpose
Defines CPU-family RTC register width and capability flags used by the SH RTC driver.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_CPU_SH4_RTC_H`, `rtc_reg_size`, `RTC_BIT_INVERTED`, `RTC_DEF_CAPABILITIES`. Register or hardware-address constants include `__ASM_SH_CPU_SH4_RTC_H`, `RTC_BIT_INVERTED`, `RTC_DEF_CAPABILITIES`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7722`, `CONFIG_CPU_SUBTYPE_SH7723`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 14 lines, 407 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7722.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7722.h

## Purpose
Defines CPU-subtype IRQ/event, DMA, GPIO, timer, and peripheral enumeration constants for the named SH SoC family.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH7722_H__`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers. Most values are SoC event or peripheral identifiers; consumers typically pass them through `evt2irq()` or platform-resource registration.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 252 lines, 7295 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7722.h -->
