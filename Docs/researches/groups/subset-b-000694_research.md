# subset-b-000694 Research

Grouped research for Hexagon low-level UAPI/kernel/lib/mm support and LoongArch build/config/asm headers. Each section is wrapped with deterministic file markers so the reconciliation lane can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/registers.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/registers.h

## Purpose

`registers.h` defines the user-visible Hexagon trap register frame ABI. It models `struct hvm_event_record` and `struct pt_regs`, names the GPR, loop, predicate, HVME, syscall, and restart fields saved on exception entry, and supplies accessor macros such as `pt_elr`, `pt_cause`, `pt_badva`, `pt_psp`, `pt_set_singlestep`, `pt_set_kmode`, and `pt_set_usermode`. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The important API is the exact field layout consumed by signal delivery, ptrace, KGDB, traps, syscall restart, and assembly entry/exit code. The macros hide the HVME subrecord layout and encode the difference between kernel and user return state. Concrete declarations observed in the file: Macros: `_ASM_REGISTERS_H`, `pt_elr`, `pt_set_elr`, `pt_cause`, `user_mode`, `ints_enabled`, `pt_psp`, `pt_badva`, `pt_set_singlestep`, `pt_clr_singlestep`, `pt_set_rte_sp`, `pt_set_kmode`, `pt_set_usermode`. Types referenced or declared: `hvm_event_record`, `pt_regs`.

## Control Flow, State, And Persistence

There is no executable flow; state is the saved register image placed on the kernel stack by `vm_entry.S` and then inspected or rewritten by C handlers before `restore_pt_regs` returns to user or kernel context.

## Dependencies And Integration Points

It integrates with `asm/ptrace.h`, `kernel/signal.c`, `kernel/traps.c`, `kernel/process.c`, `kernel/kgdb.c`, `kernel/ptrace.c`, and generated asm offsets. Layout changes must stay synchronized with assembly offsets and the UAPI signal/ptrace ABI.

## Risks And Test Signals

Risks are ABI breakage, incorrect user/kernel mode detection, bad single-step state, or mismatched stack pointer restoration. Test signals are Hexagon build coverage, ptrace register get/set, signal round trips, syscall restart tests, KGDB register dumps, and boot through exception entry/exit paths.
 A local static signal for this file is that it has 230 lines and 4623 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/setup.h

## Purpose

`setup.h` is the Hexagon UAPI setup header. It only includes `asm-generic/setup.h`, so it delegates boot-parameter user ABI definitions to the generic Linux header. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The public API is the include guard plus the generic setup definitions pulled into the Hexagon UAPI namespace. Concrete declarations observed in the file: Includes: `asm-generic/setup.h`. Macros: `_UAPI_ASM_HEXAGON_SETUP_H`.

## Control Flow, State, And Persistence

There is no runtime control flow or persistent state; the file participates only in preprocessing UAPI consumers.

## Dependencies And Integration Points

It integrates with exported UAPI headers and userspace/kernel code that includes `<asm/setup.h>` on Hexagon.

## Risks And Test Signals

Risks are limited to accidental divergence from the generic header or include-guard breakage. Test signals are UAPI header install checks and allmodconfig/header selftests for Hexagon.
 A local static signal for this file is that it has 26 lines and 928 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/sigcontext.h

## Purpose

`sigcontext.h` defines the Hexagon `struct sigcontext` UAPI wrapper around `struct user_regs_struct`. It is the register payload embedded in `ucontext` for `rt_sigreturn`. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The key type is `sigcontext.sc_regs`; it is populated in `setup_sigcontext` and consumed by `restore_sigcontext`. Concrete declarations observed in the file: Includes: `asm/user.h`. Macros: `_ASM_SIGCONTEXT_H`. Types referenced or declared: `sigcontext`, `user_regs_struct`.

## Control Flow, State, And Persistence

No local runtime logic exists. The persistent contract is the userspace signal frame layout, which must remain stable across kernel versions.

## Dependencies And Integration Points

It depends on `asm/user.h` and integrates with `kernel/signal.c`, libc signal trampolines, debuggers, and unwinding code.

## Risks And Test Signals

Risks are irreversible UAPI layout drift or incomplete register restore. Test signals are signal-handler ABI tests, `rt_sigreturn`, unwinder behavior, and ptrace/signal register comparisons.
 A local static signal for this file is that it has 35 lines and 1167 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/swab.h

## Purpose

`swab.h` declares Hexagon byte-swap policy for UAPI by defining `__SWAB_64_THRU_32__`, causing generic helpers to implement 64-bit swaps through 32-bit operations. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The API is the macro selection itself; no functions or types are declared here. Concrete declarations observed in the file: Macros: `_ASM_SWAB_H`, `__SWAB_64_THRU_32__`.

## Control Flow, State, And Persistence

There is no runtime flow. The selected generic implementation is compiled wherever UAPI byte-swap helpers are used.

## Dependencies And Integration Points

It integrates with Linux byteorder/swab headers and any UAPI consumer building for Hexagon.

## Risks And Test Signals

Risks are incorrect endian helper selection or accidental removal of the 64-through-32 path. Test signals are header compile tests and checksum/byteorder tests on 64-bit values.
 A local static signal for this file is that it has 26 lines and 897 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/unistd.h

## Purpose

`unistd.h` provides Hexagon syscall-number UAPI glue. It includes generated `asm/unistd_32.h` and aliases `__NR_sync_file_range2` to syscall number 84 for the architecture-specific syscall table. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The public API is the syscall number namespace consumed by libc, seccomp, ptrace, and kernel syscall dispatch. Concrete declarations observed in the file: Includes: `asm/unistd_32.h`. Macros: `__NR_sync_file_range2`.

## Control Flow, State, And Persistence

No executable flow exists in the header; at runtime the numbers are consumed by `do_trap0` and `sys_call_table` dispatch.

## Dependencies And Integration Points

It integrates with generated syscall headers, `kernel/syscalltab.c`, `kernel/signal.c` restart handling, and userspace syscall wrappers.

## Risks And Test Signals

Risks are syscall-number ABI drift and mismatch between UAPI numbers and `sys_call_table`. Test signals are syscall table generation, strace/seccomp syscall-number checks, and runtime syscall smoke tests.
 A local static signal for this file is that it has 34 lines and 1231 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/user.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/user.h

## Purpose

`user.h` defines Hexagon `struct user_regs_struct`, the UAPI register layout exposed to ptrace, core dumps, and signal context. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The type lists 32 GPRs plus loop registers, modifiers, predicate/user status, GP/UGP, optional CS registers, PC, cause, and bad virtual address. Concrete declarations observed in the file: Macros: `HEXAGON_ASM_USER_H`. Types referenced or declared: `user_regs_struct`.

## Control Flow, State, And Persistence

There is no local control flow. State is persisted transiently in ptrace/core/signal ABI objects and must mirror the kernel `pt_regs` save set.

## Dependencies And Integration Points

It integrates with `sigcontext.h`, `ptrace.c` regsets, KGDB register mapping, ELF core note generation, and userspace debuggers.

## Risks And Test Signals

Risks are field ordering changes, incomplete architecture-version guards, and mismatch with ptrace offsets. Test signals are GDB register display, core-dump note validation, signal context restore, and UAPI header compile checks.
 A local static signal for this file is that it has 66 lines and 1370 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/Makefile

## Purpose

`Makefile` selects the Hexagon kernel objects that form boot, trap, syscall, signal, process, timer, VM, SMP, KGDB, module, DMA, and stacktrace support. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The build API is the `obj-y` and `obj-$(CONFIG_...)` object list; it controls whether files such as `smp.o`, `kgdb.o`, `module.o`, `dma.o`, and `stacktrace.o` are linked. Concrete declarations observed in the file: Build/script rules: `always-$(KBUILD_BUILTIN) := vmlinux.lds`, `obj-y += head.o`, `obj-$(CONFIG_SMP) += smp.o`, `obj-y += setup.o irq_cpu.o traps.o syscalltab.o signal.o time.o`, `obj-y += process.o trampoline.o reset.o ptrace.o vdso.o`, `obj-$(CONFIG_KGDB)    += kgdb.o`, `obj-$(CONFIG_MODULES) += module.o hexagon_ksyms.o`, `obj-y += vm_entry.o vm_events.o vm_switch.o vm_ops.o vm_init_segtable.o`, `obj-y += vm_vectors.o`, `obj-$(CONFIG_HAS_DMA) += dma.o`, `obj-$(CONFIG_STACKTRACE) += stacktrace.o`.

## Control Flow, State, And Persistence

Build-time only; Kbuild resolves config-dependent object inclusion before link.

## Dependencies And Integration Points

It integrates with `arch/hexagon/Makefile`, generated `vmlinux.lds`, and all Hexagon kernel subsystems.

## Risks And Test Signals

Risks are omitting mandatory boot/VM objects or linking optional objects under the wrong config. Test signals are Hexagon defconfig/allmodconfig links and boot to `start_kernel`.
 A local static signal for this file is that it has 20 lines and 552 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/asm-offsets.c

## Purpose

`asm-offsets.c` emits assembly offsets for Hexagon low-level code. It uses `DEFINE` from `linux/kbuild.h` to publish `pt_regs`, `thread_info`, and `hexagon_switch_stack` field offsets. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The generated constants are consumed by exception entry, context switch, linker, and VM assembly. Concrete declarations observed in the file: Includes: `linux/compat.h`, `linux/types.h`, `linux/sched.h`, `linux/interrupt.h`, `linux/kbuild.h`, `asm/ptrace.h`, `asm/processor.h`. Macros: `COMPILE_OFFSETS`. Types referenced or declared: `pt_regs`, `hexagon_switch_stack`. Functions/syscalls: `main`.

## Control Flow, State, And Persistence

Build-time C is compiled by the offsets generator; no runtime object is linked.

## Dependencies And Integration Points

It integrates with `include/generated/asm-offsets.h`, `vm_entry.S`, `vm_switch.S`, `head.S`, and `vmlinux.lds.S`.

## Risks And Test Signals

Risks are stale offsets after C structure layout changes. Test signals are successful assembly, objdump sanity around save/restore code, and boot through fork/syscall/interrupt paths.
 A local static signal for this file is that it has 93 lines and 3144 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/dma.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/dma.c

## Purpose

`dma.c` initializes Hexagon coherent DMA reservations by assigning `dma_direct_set_offset` from `memblock_start_of_DRAM()` to `__phys_offset` and registering `hexagon_dma_init` through `arch_initcall`. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The key API is `hexagon_dma_init`, which establishes direct-DMA address translation for the architecture. Concrete declarations observed in the file: Includes: `linux/dma-map-ops.h`, `linux/memblock.h`, `asm/page.h`. Types referenced or declared: `dma_data_direction`. Functions/syscalls: `arch_sync_dma_for_device`, `hexagon_dma_init`.

## Control Flow, State, And Persistence

It runs once during initcall processing after memblock setup; it does not allocate persistent state beyond DMA mapping metadata.

## Dependencies And Integration Points

It depends on memblock, DMA direct map ops, `asm/page.h`, and the physical offset exported by MM initialization.

## Risks And Test Signals

Risks are incorrect DMA offset for nonzero physical bases or coherent pool assumptions. Test signals are DMA-capable device probe, DMA API debug, and coherent allocation tests.
 A local static signal for this file is that it has 45 lines and 1046 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/head.S

## Purpose

`head.S` contains the Hexagon boot head code that transitions from reset/loader entry into the kernel virtual mapping and C startup path. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important entry labels and constants set provisional mappings, establish stack/MMU state, and branch into the generic kernel initialization sequence. Concrete declarations observed in the file: Includes: `linux/linkage.h`, `linux/init.h`, `asm/asm-offsets.h`, `asm/mem-layout.h`, `asm/vm_mmu.h`, `asm/page.h`, `asm/hexagon_vm.h`. Macros: `SEGTABLE_ENTRIES`, `PTE_BITS`. Types referenced or declared: `and`. Assembly entry labels: `stext`, `external_cmdline_buffer`, `__head_s_vaddr_target`.

## Control Flow, State, And Persistence

Control flow is early boot only: create or use initial segment-table mappings, switch execution into the linked virtual address space, and prepare for `start_kernel`.

## Dependencies And Integration Points

It depends on mem-layout, VM MMU, page, and generated offset headers, and integrates with `vm_init_segtable.S` and `vmlinux.lds.S`.

## Risks And Test Signals

Risks are fatal early-boot address, mapping, or stack mistakes. Test signals are QEMU/board early console, objdump address checks, and boot past `setup_arch`.
 A local static signal for this file is that it has 219 lines and 5466 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/hexagon_ksyms.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/hexagon_ksyms.c

## Purpose

`hexagon_ksyms.c` exports Hexagon architecture helper symbols for loadable modules, including user-copy routines, VM interrupt helpers, memory routines, and VM/MM globals. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The API is the `EXPORT_SYMBOL` set used by modules that need architecture-provided low-level helpers. Concrete declarations observed in the file: Includes: `linux/dma-mapping.h`, `asm/hexagon_vm.h`, `asm/io.h`, `linux/uaccess.h`. Macros: `DECLARE_EXPORT`. Exported symbols: `__clear_user_hexagon`, `raw_copy_from_user`, `raw_copy_to_user`, `__vmgetie`, `__vmsetie`, `__vmyield`, `memcpy`, `memset`, `__phys_offset`, `_dflt_cache_att`, `name`.

## Control Flow, State, And Persistence

There is no runtime control flow except module symbol resolution by the kernel module loader.

## Dependencies And Integration Points

It integrates with `module.c`, `uaccess` assembly, VM helper assembly, and generic module loading.

## Risks And Test Signals

Risks are missing exports causing module link failures or over-exporting fragile internals. Test signals are `CONFIG_MODULES` builds and loading modules that use memcpy, memset, uaccess, and DMA helpers.
 A local static signal for this file is that it has 39 lines and 1056 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/hexagon_ksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/irq_cpu.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/irq_cpu.c

## Purpose

`irq_cpu.c` implements the Hexagon CPU interrupt chip, with mask, unmask, EOI, wake, and `init_IRQ` logic over HVM interrupt operations. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The important callbacks are `mask_irq_num`, `unmask_irq`, `eoi_irq`, `set_wake`, and the `irq_chip` registered for CPU interrupts. Concrete declarations observed in the file: Includes: `linux/interrupt.h`, `asm/irq.h`, `asm/hexagon_vm.h`. Types referenced or declared: `irq_data`, `irq_chip`. Functions/syscalls: `mask_irq`, `mask_irq_num`, `unmask_irq`, `eoi_irq`, `set_wake`, `init_IRQ`.

## Control Flow, State, And Persistence

Interrupt setup initializes the IRQ chip, while runtime IRQ flow masks/unmasks/posts EOI through `__vmintop_*` operations.

## Dependencies And Integration Points

It depends on generic IRQ core and `asm/hexagon_vm.h`; it integrates with `vm_events.c`, SMP IPIs, and timer IRQs.

## Risks And Test Signals

Risks are wrong interrupt numbers, missing EOI, or unsafe wake semantics. Test signals are timer interrupts, IPIs, device IRQ delivery, and `/proc/interrupts` progression.
 A local static signal for this file is that it has 78 lines and 2180 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/irq_cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/kgdb.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/kgdb.c

## Purpose

`kgdb.c` maps Hexagon registers into GDB remote protocol state and handles KGDB exception notification. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `dbg_set_reg`, `kgdb_arch_set_pc`, `sleeping_thread_to_gdb_regs`, `kgdb_arch_handle_exception`, `kgdb_notify`, `kgdb_arch_init`, and `kgdb_arch_exit`. Concrete declarations observed in the file: Includes: `linux/irq.h`, `linux/sched.h`, `linux/sched/task_stack.h`, `linux/kdebug.h`, `linux/kgdb.h`. Macros: `GDB_SIZEOF_REG`. Types referenced or declared: `dbg_reg_def_t`, `pt_regs`, `kgdb_arch`, `task_struct`, `die_args`, `notifier_block`. Functions/syscalls: `dbg_set_reg`, `kgdb_arch_set_pc`, `sleeping_thread_to_gdb_regs`, `kgdb_arch_handle_exception`, `__kgdb_notify`, `kgdb_notify`, `kgdb_arch_init`, `kgdb_arch_exit`.

## Control Flow, State, And Persistence

On debug traps KGDB copies live or sleeping thread register state, optionally updates PC, and returns control according to KGDB core decisions.

## Dependencies And Integration Points

It integrates with `traps.c` debug handling, `pt_regs`, scheduler task stacks, and `linux/kgdb.h`.

## Risks And Test Signals

Risks are incorrect register numbering, broken PC updates, and bad sleeping-thread stack decoding. Test signals are KGDB breakpoint, single-step, register read/write, and detach/resume tests.
 A local static signal for this file is that it has 215 lines and 7045 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/kgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/module.c

## Purpose

`module.c` implements Hexagon module relocation handling for ELF RELA records. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The main API is `apply_relocate_add`, which applies supported relocation types while loading a module. Concrete declarations observed in the file: Includes: `asm/module.h`, `linux/elf.h`, `linux/module.h`, `linux/moduleloader.h`, `linux/vmalloc.h`. Macros: `DEBUGP`. Types referenced or declared: `module`. Functions/syscalls: `module_frob_arch_sections`, `apply_relocate_add`.

## Control Flow, State, And Persistence

Runtime flow is module-load time only: iterate relocation entries, locate target section/symbol, patch text/data, and reject unsupported relocations.

## Dependencies And Integration Points

It integrates with Linux moduleloader, ELF relocation definitions, vmalloc module memory, and exported Hexagon symbols.

## Risks And Test Signals

Risks are unsupported relocation types, overflow, or bad instruction patching. Test signals are loading representative modules, `modpost`, and relocation-error negative tests.
 A local static signal for this file is that it has 150 lines and 4095 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/process.c

## Purpose

`process.c` implements Hexagon process and thread lifecycle hooks: userspace launch, idle, fork setup, wait-channel walking, and return-to-user pending work. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `start_thread`, `arch_cpu_idle`, `copy_thread`, `flush_thread`, `__get_wchan`, and `do_work_pending`. Concrete declarations observed in the file: Includes: `linux/cpu.h`, `linux/sched.h`, `linux/sched/debug.h`, `linux/sched/task.h`, `linux/sched/task_stack.h`, `linux/types.h`, `linux/module.h`, `linux/tick.h`, `linux/uaccess.h`, `linux/slab.h`, `linux/resume_user_mode.h`. Types referenced or declared: `pt_regs`, `task_struct`, `kernel_clone_args`, `thread_info`, `hexagon_switch_stack`. Functions/syscalls: `start_thread`, `arch_cpu_idle`, `copy_thread`, `flush_thread`, `do_work_pending`.

## Control Flow, State, And Persistence

Control flow covers ELF exec register reset, idle `__vmwait`, child kernel/user stack construction, scheduler wait-channel frame walking, and return-from-event handling of reschedule, signals, and notify-resume work.

## Dependencies And Integration Points

It depends on `pt_regs`, `thread_info`, scheduler/task APIs, Hexagon VM wait, and `ret_from_fork` from assembly.

## Risks And Test Signals

Risks are wrong child stack layout, TLS restore bugs, syscall restart interaction, and missed pending work. Test signals are fork/clone/TLS tests, kernel thread startup, scheduler traces, signal delivery, and idle tick behavior.
 A local static signal for this file is that it has 184 lines and 4777 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/ptrace.c

## Purpose

`ptrace.c` implements Hexagon ptrace register access and syscall tracing hooks. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `genregs_get`, `genregs_set`, `user_enable_single_step`, `user_disable_single_step`, `ptrace_disable`, and `arch_ptrace`. Concrete declarations observed in the file: Includes: `linux/kernel.h`, `linux/sched.h`, `linux/sched/task_stack.h`, `linux/mm.h`, `linux/smp.h`, `linux/errno.h`, `linux/ptrace.h`, `linux/regset.h`, `linux/user.h`, `linux/elf.h`, `asm/user.h`. Macros: `INEXT`. Types referenced or declared: `task_struct`, `user_regset`, `membuf`, `pt_regs`, `user_regs_struct`, `hexagon_regset`, `user_regset_view`. Functions/syscalls: `user_enable_single_step`, `user_disable_single_step`, `genregs_get`, `genregs_set`, `ptrace_disable`, `arch_ptrace`.

## Control Flow, State, And Persistence

Ptrace regset flow copies fields between `pt_regs` and `user_regs_struct`, toggles single-step in HVME state, and delegates generic requests to `ptrace_request`.

## Dependencies And Integration Points

It integrates with `registers.h`, ELF regsets, signal/core-dump ABI, and `traps.c` syscall/debug reporting.

## Risks And Test Signals

Risks are register offset mismatch, bad single-step masking, and syscall trace regressions. Test signals are strace, GDB register set/get, single-step, and core-dump register validation.
 A local static signal for this file is that it has 174 lines and 4594 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/reset.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/reset.c

## Purpose

`reset.c` provides Hexagon machine halt, poweroff, and restart hooks using the virtual machine stop primitive. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The public hooks are `machine_halt`, `machine_power_off`, `machine_restart`, and exported `pm_power_off`. Concrete declarations observed in the file: Includes: `linux/reboot.h`, `linux/smp.h`, `asm/hexagon_vm.h`. Functions/syscalls: `machine_power_off`, `machine_halt`. Exported symbols: `pm_power_off`.

## Control Flow, State, And Persistence

Runtime flow is direct: halt/poweroff/restart call `__vmstop`, with SMP stop available through generic shutdown paths.

## Dependencies And Integration Points

It integrates with reboot core, PM poweroff, SMP stop, and `asm/hexagon_vm.h`.

## Risks And Test Signals

Risks are restart behaving like halt or missing platform-specific reset. Test signals are reboot, halt, and poweroff command smoke tests under VM or hardware.
 A local static signal for this file is that it has 26 lines and 393 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/setup.c

## Purpose

`setup.c` implements Hexagon architecture setup, CPU info reporting, bootmem sizing handoff, console behavior, and device-tree memory discovery. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important APIs include `setup_arch`, `calibrate_delay`, and `/proc/cpuinfo` seq operations. Concrete declarations observed in the file: Includes: `linux/init.h`, `linux/delay.h`, `linux/memblock.h`, `linux/mmzone.h`, `linux/mm.h`, `linux/seq_file.h`, `linux/console.h`, `linux/of_fdt.h`, `asm/io.h`, `asm/sections.h`, `asm/setup.h`, `asm/processor.h`, `asm/hexagon_vm.h`, `asm/vm_mmu.h`, `asm/time.h`. Types referenced or declared: `seq_file`, `seq_operations`. Functions/syscalls: `calibrate_delay`, `setup_arch`, `c_stop`.

## Control Flow, State, And Persistence

Boot flow parses the flattened DT, sets command line and root device assumptions, initializes memory, reserves initrd if present, and registers CPU info reporting.

## Dependencies And Integration Points

It depends on memblock, OF FDT, sections, processor, MM setup, and generic proc/seq infrastructure.

## Risks And Test Signals

Risks are wrong memory discovery, command-line handling, or early reservation conflicts. Test signals are boot logs, `/proc/cpuinfo`, initrd boot, and DT memory-node validation.
 A local static signal for this file is that it has 138 lines and 3118 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/signal.c

## Purpose

`signal.c` implements Hexagon real-time signal frame creation, signal-context save/restore, syscall restart handling, and `rt_sigreturn`. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `setup_sigcontext`, `restore_sigcontext`, `setup_rt_frame`, `do_signal`, and `SYSCALL_DEFINE0(rt_sigreturn)`. Concrete declarations observed in the file: Includes: `linux/linkage.h`, `linux/syscalls.h`, `linux/sched/task_stack.h`, `asm/registers.h`, `asm/thread_info.h`, `asm/unistd.h`, `linux/uaccess.h`, `asm/ucontext.h`, `asm/cacheflush.h`, `asm/signal.h`, `asm/vdso.h`. Types referenced or declared: `rt_sigframe`, `siginfo`, `ucontext`, `ksignal`, `pt_regs`, `sigcontext`, `hexagon_vdso`. Functions/syscalls: `setup_sigcontext`, `restore_sigcontext`, `setup_rt_frame`, `handle_signal`, `do_signal`, `rt_sigreturn`.

## Control Flow, State, And Persistence

Control flow runs on return to user mode: choose a signal, build `rt_sigframe` on the user or alt stack, redirect PC to the handler and LR to the VDSO trampoline, then restore context on `rt_sigreturn`.

## Dependencies And Integration Points

It integrates with `registers.h`, `ucontext`, `vdso.c`, syscall restart numbers, and uaccess helpers.

## Risks And Test Signals

Risks are corrupt user frames, incorrect PC/SP restore, signal mask loss, and syscall restart loops. Test signals are Linux signal selftests, altstack, sigreturn, interrupted syscall restart, and unwinder checks.
 A local static signal for this file is that it has 257 lines and 6708 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/smp.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/smp.c

## Purpose

`smp.c` implements Hexagon SMP bring-up and IPI delivery. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs include `send_ipi`, `handle_ipi`, `start_secondary`, `__cpu_up`, `smp_prepare_cpus`, `arch_smp_send_reschedule`, and call-function IPI helpers. Concrete declarations observed in the file: Includes: `linux/err.h`, `linux/errno.h`, `linux/kernel.h`, `linux/init.h`, `linux/interrupt.h`, `linux/module.h`, `linux/percpu.h`, `linux/sched/mm.h`, `linux/smp.h`, `linux/spinlock.h`, `linux/cpu.h`, `linux/mm_types.h`, `asm/time.h`, `asm/hexagon_vm.h`. Macros: `BASE_IPI_IRQ`. Types referenced or declared: `ipi_data`, `cpumask`, `ipi_message_type`, `task_struct`, `thread_info`. Functions/syscalls: `__handle_ipi`, `smp_vm_unmask_irq`, `handle_ipi`, `send_ipi`, `start_secondary`, `__cpu_up`, `smp_cpus_done`, `arch_smp_send_reschedule`, `smp_send_stop`, `arch_send_call_function_single_ipi`, `arch_send_call_function_ipi_mask`, `smp_start_cpus`.

## Control Flow, State, And Persistence

Boot CPU marks possible/present CPUs, starts secondary CPUs with `__vmstart`, installs per-CPU IPI IRQs, and runtime IPI handling drains per-CPU bitmaps for timer, call-function, stop, and reschedule messages.

## Dependencies And Integration Points

It depends on generic SMP/cpumask APIs, scheduler IPIs, timer broadcast, and HVM interrupt posting.

## Risks And Test Signals

Risks are IPI races, wrong BASE_IPI_IRQ mapping, secondary stack/thread-info corruption, and CPU stop hangs. Test signals are SMP boot, CPU hotplug, reschedule/call-function stress, and timer IPI behavior.
 A local static signal for this file is that it has 246 lines and 4983 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/stacktrace.c

## Purpose

`stacktrace.c` implements the Hexagon stacktrace collector by walking frame pointers from the task stack. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The exported API is `save_stack_trace`. Concrete declarations observed in the file: Includes: `linux/sched.h`, `linux/sched/task_stack.h`, `linux/stacktrace.h`, `linux/thread_info.h`, `linux/module.h`. Types referenced or declared: `stackframe`, `stack_trace`. Functions/syscalls: `save_stack_trace`. Exported symbols: `save_stack_trace`.

## Control Flow, State, And Persistence

Runtime flow starts from current or target task frame pointer, validates stack bounds, saves return PCs, and stops on corrupt/out-of-bounds frames.

## Dependencies And Integration Points

It integrates with scheduler task stacks, `thread_info`, generic stacktrace users, and module export machinery.

## Risks And Test Signals

Risks are bad frame-pointer assumptions and out-of-bounds stack reads. Test signals are `CONFIG_STACKTRACE`, lockdep/tracing stack dumps, and forced stacktrace collection.
 A local static signal for this file is that it has 53 lines and 1133 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/syscalltab.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/syscalltab.c

## Purpose

`syscalltab.c` builds the Hexagon syscall dispatch table from generated syscall metadata. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The main object is `sys_call_table[__NR_syscalls]`; macros map generic syscall names and Hexagon-specific aliases such as `sys_sync_file_range`. Concrete declarations observed in the file: Includes: `linux/syscalls.h`, `linux/signal.h`, `linux/unistd.h`, `asm/syscall.h`, `asm/syscall_table_32.h`. Macros: `__SYSCALL`, `__SYSCALL_WITH_COMPAT`, `sys_mmap2`, `sys_fadvise64_64`, `sys_sync_file_range`. Functions/syscalls: `hexagon_fadvise64_64`.

## Control Flow, State, And Persistence

No active control flow exists here; `traps.c` indexes the table after validating the syscall number.

## Dependencies And Integration Points

It integrates with generated `asm/syscall_table_32.h`, `unistd.h`, syscall wrappers, and ptrace/seccomp paths.

## Risks And Test Signals

Risks are table size drift or wrong aliasing. Test signals are syscall smoke tests, strace syscall names, and generated-table build checks.
 A local static signal for this file is that it has 31 lines and 785 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/syscalltab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/time.c

## Purpose

`time.c` implements Hexagon clocksource, clockevent, per-CPU clock device setup, timer interrupt handling, and busy-wait delay loops. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `time_init`, `setup_percpu_clockdev`, `timer_interrupt`, `ipi_timer`, `__delay`, and `__udelay`. Concrete declarations observed in the file: Includes: `linux/init.h`, `linux/clockchips.h`, `linux/clocksource.h`, `linux/interrupt.h`, `linux/err.h`, `linux/platform_device.h`, `linux/ioport.h`, `linux/of.h`, `linux/of_address.h`, `linux/of_irq.h`, `linux/module.h`, `asm/delay.h`, `asm/hexagon_vm.h`, `asm/time.h`. Macros: `TIMER_ENABLE`, `RTOS_TIMER_INT`, `RTOS_TIMER_REGS_ADDR`. Types referenced or declared: `resource`, `platform_device`, `adsp_hw_timer_struct`, `clocksource`, `clock_event_device`, `cpumask`. Functions/syscalls: `timer_get_cycles`, `set_next_event`, `broadcast`, `setup_percpu_clockdev`, `ipi_timer`, `timer_interrupt`, `time_init_deferred`, `time_init`, `__delay`, `__udelay`. Exported symbols: `__delay`, `__udelay`.

## Control Flow, State, And Persistence

Boot maps timer registers, registers a clocksource and per-CPU clockevent; runtime timer interrupts acknowledge hardware, run event handlers, and broadcast per-CPU events through IPIs when needed.

## Dependencies And Integration Points

It depends on OF address/IRQ parsing, clocksource/clockevent core, platform resources, and Hexagon VM interrupt operations.

## Risks And Test Signals

Risks are broken timer frequency, missed acknowledges, delay calibration errors, and SMP broadcast failures. Test signals are scheduler tick, high-resolution timers, `udelay` calibration, and clocksource watchdog.
 A local static signal for this file is that it has 234 lines and 6027 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/trampoline.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/trampoline.S

## Purpose

`trampoline.S` contains the small Hexagon signal trampoline template used for userspace frame/unwind compatibility. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The important label is `__rt_sigtramp_template`, which issues the `rt_sigreturn` syscall sequence expected by signal frame consumers. Concrete declarations observed in the file: Includes: `asm/unistd.h`. Assembly entry labels: `__rt_sigtramp_template`.

## Control Flow, State, And Persistence

It is copied or referenced as signal trampoline code; normal signal delivery now uses the VDSO trampoline while retaining magic compatibility values.

## Dependencies And Integration Points

It integrates with `signal.c`, `vdso.c`, and `unistd.h` syscall numbering.

## Risks And Test Signals

Risks are mismatched trampoline instructions or syscall number drift. Test signals are signal unwinding and `rt_sigreturn` execution tests.
 A local static signal for this file is that it has 23 lines and 585 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/trampoline.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/traps.c

## Purpose

`traps.c` implements Hexagon exception, syscall trap, debug trap, oops, and stack display handling. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `show_stack`, `die`, `die_if_kernel`, `do_genex`, `do_trap0`, `do_machcheck`, and `do_debug_exception`. Concrete declarations observed in the file: Includes: `linux/init.h`, `linux/sched/signal.h`, `linux/sched/debug.h`, `linux/sched/task_stack.h`, `linux/module.h`, `linux/kallsyms.h`, `linux/kdebug.h`, `linux/syscalls.h`, `linux/signal.h`, `linux/ptrace.h`, `asm/traps.h`, `asm/vm_fault.h`, `asm/syscall.h`, `asm/registers.h`, `asm/unistd.h`, `asm/sections.h`, `linux/kgdb.h`. Macros: `TRAP_SYSCALL`, `TRAP_DEBUG`. Types referenced or declared: `task_struct`, `hexagon_switch_stack`, `thread_info`, `pt_regs`. Functions/syscalls: `is_valid_bugaddr`, `do_show_stack`, `show_stack`, `die`, `die_if_kernel`, `misaligned_instruction`, `misaligned_data_load`, `misaligned_data_store`, `illegal_instruction`, `precise_bus_error`, `cache_error`, `do_genex`, `do_trap0`, `do_machcheck`, `do_debug_exception`.

## Control Flow, State, And Persistence

General exceptions dispatch by `pt_cause` into page-fault or fatal signal paths. `do_trap0` handles syscall trap #1 by enabling interrupts, saving syscall metadata, indexing `sys_call_table`, and running ptrace entry/exit hooks; debug traps signal userspace or enter KGDB.

## Dependencies And Integration Points

It integrates with `vm_entry.S`, `vm_fault.c`, syscall table, ptrace, KGDB, kallsyms, and scheduler stacks.

## Risks And Test Signals

Risks are fatal misdecode of causes, syscall restart breakage, missing ptrace hooks, or unsafe oops locking. Test signals are page-fault tests, illegal instruction/sigill, strace, KGDB breakpoints, and panic/oops stack traces.
 A local static signal for this file is that it has 433 lines and 10139 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vdso.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vdso.c

## Purpose

`vdso.c` initializes and maps the Hexagon VDSO into new user address spaces. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `vdso_init` and `arch_setup_additional_pages`; state lives in `struct hexagon_vdso` and a `vm_special_mapping`. Concrete declarations observed in the file: Includes: `linux/err.h`, `linux/mm.h`, `linux/vmalloc.h`, `linux/binfmts.h`, `asm/elf.h`, `asm/vdso.h`. Types referenced or declared: `page`, `hexagon_vdso`, `linux_binprm`, `vm_area_struct`, `mm_struct`, `vm_special_mapping`. Functions/syscalls: `vdso_init`, `arch_setup_additional_pages`.

## Control Flow, State, And Persistence

Boot/init flow allocates page pointers for the VDSO image. Exec/mmap flow maps the VDSO near the user stack under `mmap_write_lock` and records the base in `mm->context.vdso`.

## Dependencies And Integration Points

It integrates with ELF binfmt, `signal.c` trampoline selection, `asm/vdso.h`, and mm special mappings.

## Risks And Test Signals

Risks are VDSO page-count mistakes, bad special mapping permissions, and signal trampoline pointer loss. Test signals are VDSO presence in `/proc/self/maps`, signal handler return, and exec/mmap stress.
 A local static signal for this file is that it has 96 lines and 2127 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_entry.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_entry.S

## Purpose

`vm_entry.S` contains Hexagon virtual-machine event entry and return assembly for interrupts, traps, machine checks, debug, and fork return. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important macros are `save_pt_regs`, `restore_pt_regs`, and `vm_event_entry`; labels include `event_dispatch`, `restore_all`, `_K_enter_genex`, `_K_enter_interrupt`, `_K_enter_trap0`, and `ret_from_fork`. Concrete declarations observed in the file: Includes: `asm/asm-offsets.h`, `asm/mem-layout.h`, `asm/hexagon_vm.h`, `asm/thread_info.h`. Macros: `save_pt_regs`, `restore_pt_regs`, `vm_event_entry`. Assembly entry labels: `event_dispatch`, `check_work_pending`, `restore_all`, `_K_enter_genex`, `_K_enter_interrupt`, `_K_enter_trap0`, `_K_enter_machcheck`, `_K_enter_debug`, `ret_from_fork`.

## Control Flow, State, And Persistence

Control flow saves the interrupted register set, dispatches to C handlers, checks thread work flags on return to user mode, restores registers, and resumes through the HVM return path.

## Dependencies And Integration Points

It depends on generated offsets, thread-info flags, C handlers in `traps.c`/`vm_events.c`, and `process.c` pending-work logic.

## Risks And Test Signals

Risks are register corruption, wrong stack layout, lost interrupt state, and return-to-user work omissions. Test signals are boot, syscall, interrupt, signal, fork, and preemption stress.
 A local static signal for this file is that it has 381 lines and 10198 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_events.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_events.c

## Purpose

`vm_events.c` bridges VM interrupt events into generic Linux IRQ handling. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The key API is `arch_do_IRQ`, called from assembly event entry with a populated `pt_regs`. Concrete declarations observed in the file: Includes: `linux/kernel.h`, `linux/sched/debug.h`, `asm/registers.h`, `linux/irq.h`, `linux/hardirq.h`. Types referenced or declared: `pt_regs`. Functions/syscalls: `show_regs`, `arch_do_IRQ`.

## Control Flow, State, And Persistence

Runtime flow enters IRQ context, decodes the IRQ cause, invokes generic IRQ handling, and exits IRQ context for return processing.

## Dependencies And Integration Points

It integrates with `irq_cpu.c`, `vm_entry.S`, generic IRQ core, and hardirq accounting.

## Risks And Test Signals

Risks are wrong IRQ decode, missing irq_enter/exit pairing, or failure under nested interrupts. Test signals are timer/device interrupts and IRQ accounting traces.
 A local static signal for this file is that it has 86 lines and 2449 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_init_segtable.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_init_segtable.S

## Purpose

`vm_init_segtable.S` defines and initializes the early Hexagon segment and device page tables. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important labels include `swapper_pg_dir`, `_K_init_segtable`, `_K_io_map`, `_K_init_devicetable`, and `UART_PTE_ENTRY`; macros create big-page, IO, and L2 pointer entries. Concrete declarations observed in the file: Includes: `asm/vm_mmu.h`. Macros: `BKP`, `BKPG_IO`, `FOURK_IO`, `L2_PTR`, `X`. Assembly entry labels: `swapper_pg_dir`, `UART_PTE_ENTRY`, `_K_init_segtable`, `_K_io_map`, `_K_init_devicetable`, `_K_io_kmap`.

## Control Flow, State, And Persistence

Control flow/data setup creates boot-time identity/virtual mappings, kernel text/data mappings, IO windows, and the initial device table consumed by early boot and MM initialization.

## Dependencies And Integration Points

It integrates with `head.S`, `mm/init.c`, HVM PTE definitions, and the linker script.

## Risks And Test Signals

Risks are invalid early mappings, wrong cache attributes, or device-window overlap. Test signals are early console, memory sizing logs, and boot through paging initialization.
 A local static signal for this file is that it has 430 lines and 12163 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_init_segtable.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_ops.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_ops.S

## Purpose

`vm_ops.S` provides assembly wrappers for Hexagon VM operations such as interrupt enable, wait/yield, cache/TLB, and VM control primitives. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The file's symbols are low-level ABI helpers referenced from C and exported for modules where needed. Concrete declarations observed in the file: Includes: `linux/linkage.h`, `asm/hexagon_vm.h`. Assembly entry labels: `__vmrte`, `__vmsetvec`, `__vmsetie`, `__vmgetie`, `__vmintop`, `__vmclrmap`, `__vmnewmap`, `__vmcache`, `__vmgettime`, `__vmsettime`, `__vmwait`, `__vmyield`, `__vmstart`, `__vmstop`, `__vmvpid`, `__vmsetregs`, `__vmgetregs`.

## Control Flow, State, And Persistence

Control flow is direct wrapper execution: move arguments into expected registers, execute HVM instructions, return status/results.

## Dependencies And Integration Points

It integrates with `hexagon_ksyms.c`, IRQ, timer, cache, SMP, and reset code.

## Risks And Test Signals

Risks are wrong calling convention or clobber set around privileged VM operations. Test signals are boot, interrupt enable/disable, cache/TLB flush, idle wait, and SMP stop paths.
 A local static signal for this file is that it has 90 lines and 1647 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_ops.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_switch.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_switch.S

## Purpose

`vm_switch.S` implements Hexagon context switching between tasks. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The key entry is `__switch_to`, which saves/restores callee-saved registers and task `thread.switch_sp` state. Concrete declarations observed in the file: Includes: `asm/asm-offsets.h`. Types referenced or declared: `task_struct`, `size`. Assembly entry labels: `__switch_to`.

## Control Flow, State, And Persistence

Scheduler runtime flow stores the old task switch stack, loads the next task stack, restores saved registers, and returns into the next task's context or `ret_from_fork`.

## Dependencies And Integration Points

It depends on generated `thread_struct`/switch-stack offsets and integrates with `copy_thread` in `process.c`.

## Risks And Test Signals

Risks are task register corruption, wrong stack pointer restore, and fork return failures. Test signals are scheduler stress, fork/exec loops, and context-switch tracing.
 A local static signal for this file is that it has 83 lines and 2389 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_switch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_vectors.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_vectors.S

## Purpose

`vm_vectors.S` defines provisional and real Hexagon VM event vectors. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important labels include `_K_provisional_vec` and `_K_VM_event_vector`, which point VM events at the architecture entry stubs. Concrete declarations observed in the file: Includes: `asm/hexagon_vm.h`. Assembly entry labels: `_K_provisional_vec`, `_K_VM_event_vector`.

## Control Flow, State, And Persistence

Boot flow starts with provisional vectoring and later installs the real vector table used for exceptions, interrupts, trap0, machine check, and debug entry.

## Dependencies And Integration Points

It integrates with HVM vector registers, `head.S`, and `vm_entry.S`.

## Risks And Test Signals

Risks are wrong vector ordering or early exception jumps to unmapped code. Test signals are early boot exceptions, timer IRQ entry, syscall trap, and debug trap tests.
 A local static signal for this file is that it has 36 lines and 628 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_vectors.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vmlinux.lds.S

## Purpose

`vmlinux.lds.S` is the Hexagon architecture linker script for the kernel image. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

It defines image layout, section placement, alignment, init sections, per-CPU data, exception tables, and architecture-specific symbols consumed by boot/MM code. Concrete declarations observed in the file: Includes: `asm-generic/vmlinux.lds.h`, `asm/asm-offsets.h`, `asm/mem-layout.h`, `asm/cache.h`, `asm/thread_info.h`. Macros: `PAGE_SIZE`. Assembly entry labels: `stext`.

## Control Flow, State, And Persistence

Build-time only: the linker script lays out the final `vmlinux`; runtime code uses symbols such as text/data boundaries and initial stack/table locations.

## Dependencies And Integration Points

It integrates with generic linker macros, `head.S`, `mm/init.c`, and generated offsets.

## Risks And Test Signals

Risks are section misalignment, discarded required metadata, or address mismatch with early mappings. Test signals are successful link, `readelf -S`, boot, module exception-table behavior, and init memory freeing.
 A local static signal for this file is that it has 71 lines and 1350 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/hexagon/lib/Makefile

## Purpose

`Makefile` selects Hexagon architecture library objects for arithmetic, memory, and checksum helpers. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The build API is the `lib-y`/object list for `memcpy`, `memset`, division/modulo helpers, and checksum code. Concrete declarations observed in the file: Build/script rules: `obj-y = checksum.o memcpy.o memset.o memcpy_likely_aligned.o \`.

## Control Flow, State, And Persistence

Build-time only; the selected objects are linked into the kernel library archive.

## Dependencies And Integration Points

It integrates with compiler helper resolution, generic lib, and module symbol exports.

## Risks And Test Signals

Risks are missing compiler runtime helpers or optimized memory routines. Test signals are full Hexagon link, lib/string tests, checksum tests, and boot.
 A local static signal for this file is that it has 7 lines and 202 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/checksum.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/lib/checksum.c

## Purpose

`checksum.c` implements Hexagon IP checksum helpers, including TCP/UDP pseudo-header folding and the core buffer checksum routine. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `csum_tcpudp_magic`, `csum_tcpudp_nofold`, and `do_csum`, with vector-style carry/select helper macros. Concrete declarations observed in the file: Includes: `linux/module.h`, `linux/string.h`, `asm/byteorder.h`, `net/checksum.h`, `linux/uaccess.h`, `asm/intrinsics.h`. Macros: `SIGN`, `CARRY`, `SELECT`, `VR_NEGATE`, `VR_CARRY`, `VR_SELECT`. Exported symbols: `csum_tcpudp_nofold`.

## Control Flow, State, And Persistence

Runtime flow walks aligned and unaligned buffer pieces, accumulates 16-bit sums, folds carries, and returns network checksum values.

## Dependencies And Integration Points

It integrates with the networking stack, `net/checksum.h`, byteorder helpers, and uaccess-safe checksum users.

## Risks And Test Signals

Risks are endian/carry mistakes, odd-length buffer handling bugs, and unaligned access assumptions. Test signals are network checksum selftests, ping/TCP/UDP traffic, and checksum comparison with generic implementation.
 A local static signal for this file is that it has 179 lines and 4708 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/checksum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/divsi3.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/lib/divsi3.S

## Purpose

`divsi3.S` provides the signed 32-bit division compiler helper for Hexagon. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The exported ABI symbol is the division routine expected by GCC when hardware or compiler lowering requires `__divsi3`-style support. Concrete declarations observed in the file: Includes: `linux/linkage.h`. Assembly entry labels: `__hexagon_divsi3`.

## Control Flow, State, And Persistence

Runtime flow normalizes signs, performs unsigned division, then reapplies the result sign.

## Dependencies And Integration Points

It integrates with compiler-generated calls from kernel C code and the Hexagon library archive.

## Risks And Test Signals

Risks are divide-by-zero behavior mismatch and signed overflow edge cases. Test signals are arithmetic helper unit tests and full kernel link without unresolved helpers.
 A local static signal for this file is that it has 68 lines and 1671 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/divsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/memcpy.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/lib/memcpy.S

## Purpose

`memcpy.S` implements the optimized Hexagon `memcpy` routine with alignment prologue, wide transfer kernel, and epilogue handling. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The public ABI is `memcpy`, using register aliases for source, destination, length, predicates, and wide data buffers. Concrete declarations observed in the file: Macros: `ptr_out`, `ptr_in`, `len`, `data70`, `dataF8`, `ldata0`, `ldata1`, `data1`, `data0`, `ifbyte`, `ifhword`, `ifword`, `noprolog`, `nokernel`, `noepilog`, `align`, `kernel1`, `dalign`, `star3`, `rest`, `back`, `epilog`, `inc`, `kernel`, and 13 more. Assembly entry labels: `memcpy`, `.Lskip64`, `.Lnoprolog32`, `.Ldword_loop_prolog`, `.Lkernel`, `.Loword_loop_25to31`, `.Lodd_alignment`, `.Loword_loop_00to24`, `.Lepilog`, `.Ldword_loop_epilog`, `.Lepilog60`, `.Lbytes23orless`, `.Lbyte_copy`, `.Ldwordaligned`, `.Ldword_copy`, `.Lmemcpy_return`.

## Control Flow, State, And Persistence

Runtime flow aligns the destination/source relationship, handles small/prologue bytes, copies large blocks in 32-byte chunks, and finishes with word/half/byte epilogues.

## Dependencies And Integration Points

It integrates with core kernel memory operations and module exports through `hexagon_ksyms.c`.

## Risks And Test Signals

Risks are overlap assumptions, unaligned faults, tail corruption, and clobber/calling-convention bugs. Test signals are lib/string tests, KASAN-free boot, module use of memcpy, and randomized copy verification.
 A local static signal for this file is that it has 530 lines and 15374 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/memcpy_likely_aligned.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/lib/memcpy_likely_aligned.S

## Purpose

`memcpy_likely_aligned.S` is a thin aligned-copy wrapper/entry path that forwards likely aligned copies into the main Hexagon `memcpy` implementation. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Its ABI is the alternate copy entry/label used by callers that can assume favorable alignment. Concrete declarations observed in the file: Includes: `linux/linkage.h`. Assembly entry labels: `__hexagon_memcpy_likely_aligned_min32bytes_mult8bytes`, `.Lmemcpy_call`.

## Control Flow, State, And Persistence

Runtime flow performs minimal setup then branches/calls into the shared copy implementation.

## Dependencies And Integration Points

It integrates with the Hexagon library Makefile and memory-copy users.

## Risks And Test Signals

Risks are divergence from `memcpy` semantics or bad branch target linkage. Test signals are lib/string aligned-copy cases and final link.
 A local static signal for this file is that it has 57 lines and 1586 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/memcpy_likely_aligned.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/memset.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/lib/memset.S

## Purpose

`memset.S` implements optimized Hexagon `memset` with byte/half/word alignment handling and wide fill loops. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The public ABI is `memset`. Concrete declarations observed in the file: Assembly entry labels: `.L47`, `.L3`, `.L8`, `.L10`, `.L12`, `.L17`, `.L46`, `.L14`, `.L44`, `.L28`, `.L33`, `.L35`, `.L1`, `.L18`, `.L45`.

## Control Flow, State, And Persistence

Runtime flow handles leading unaligned bytes, constructs repeated fill words/doublewords, runs a wide loop, then stores the trailing word/half/byte pieces.

## Dependencies And Integration Points

It integrates with kernel initialization, allocator clearing, and module exports.

## Risks And Test Signals

Risks are incorrect fill byte replication, tail overwrite, and alignment faults. Test signals are lib/string memset tests, boot memory clearing, and randomized memset verification.
 A local static signal for this file is that it has 303 lines and 4659 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/modsi3.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/lib/modsi3.S

## Purpose

`modsi3.S` provides the signed 32-bit modulo compiler helper. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The ABI symbol implements signed remainder for compiler-generated calls. Concrete declarations observed in the file: Includes: `linux/linkage.h`. Assembly entry labels: `__hexagon_modsi3`.

## Control Flow, State, And Persistence

Runtime flow derives sign, uses division/remainder mechanics, and returns a signed remainder matching C semantics.

## Dependencies And Integration Points

It integrates with compiler runtime helper resolution.

## Risks And Test Signals

Risks are negative dividend/divisor edge cases. Test signals are arithmetic selftests and compiler-helper linkage.
 A local static signal for this file is that it has 47 lines and 1066 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/modsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/udivsi3.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/lib/udivsi3.S

## Purpose

`udivsi3.S` provides the unsigned 32-bit division compiler helper. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The ABI symbol implements unsigned quotient calculation. Concrete declarations observed in the file: Includes: `linux/linkage.h`. Assembly entry labels: `__hexagon_udivsi3`.

## Control Flow, State, And Persistence

Runtime flow is a compact bit/loop division routine returning the quotient in the ABI return register.

## Dependencies And Integration Points

It integrates with compiler-generated unsigned division calls.

## Risks And Test Signals

Risks are zero divisor and high-bit divisor edge cases. Test signals are arithmetic helper tests and kernel link.
 A local static signal for this file is that it has 39 lines and 938 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/udivsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/umodsi3.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/lib/umodsi3.S

## Purpose

`umodsi3.S` provides the unsigned 32-bit modulo compiler helper. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The ABI symbol implements unsigned remainder calculation. Concrete declarations observed in the file: Includes: `linux/linkage.h`. Assembly entry labels: `__hexagon_umodsi3`.

## Control Flow, State, And Persistence

Runtime flow mirrors unsigned division but returns the remainder.

## Dependencies And Integration Points

It integrates with compiler-generated modulo calls.

## Risks And Test Signals

Risks are high-bit/zero divisor edge cases. Test signals are arithmetic selftests and unresolved-symbol checks.
 A local static signal for this file is that it has 37 lines and 848 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/lib/umodsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/hexagon/mm/Makefile

## Purpose

`Makefile` selects Hexagon MM implementation objects for initialization, uaccess, faults, cache management, user-copy assembly, and TLB flushing. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The build API is the `obj-y` list for `init.o`, `uaccess.o`, `vm_fault.o`, `cache.o`, `copy_to_user.o`, `copy_from_user.o`, and `vm_tlb.o`. Concrete declarations observed in the file: Build/script rules: `obj-y := init.o uaccess.o vm_fault.o cache.o`, `obj-y += copy_to_user.o copy_from_user.o vm_tlb.o`.

## Control Flow, State, And Persistence

Build-time only; these objects become the architecture MM support library.

## Dependencies And Integration Points

It integrates with the Hexagon kernel Makefile and generic MM hooks.

## Risks And Test Signals

Risks are missing mandatory MM objects. Test signals are Hexagon link and boot into userspace.
 A local static signal for this file is that it has 8 lines and 191 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/cache.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/mm/cache.c

## Purpose

`cache.c` implements Hexagon cache maintenance hooks for I-cache/D-cache synchronization and user-page copy flushing. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `flush_icache_range`, `hexagon_clean_dcache_range`, `hexagon_inv_dcache_range`, `flush_cache_all_hexagon`, and `copy_to_user_page`. Concrete declarations observed in the file: Includes: `linux/mm.h`, `asm/cacheflush.h`, `asm/hexagon_vm.h`. Macros: `spanlines`. Types referenced or declared: `vm_area_struct`, `page`. Functions/syscalls: `flush_dcache_range`, `flush_icache_range`, `hexagon_clean_dcache_range`, `hexagon_inv_dcache_range`, `flush_cache_all_hexagon`, `copy_to_user_page`. Exported symbols: `flush_icache_range`.

## Control Flow, State, And Persistence

Runtime flow rounds ranges to cache-line spans and invokes HVM cache operations; user-page copy copies data then synchronizes instruction/data cache for executable mappings.

## Dependencies And Integration Points

It integrates with generic cacheflush APIs, VM cache attributes, module export, and userspace text modification paths.

## Risks And Test Signals

Risks are missed line endpoints, stale I-cache after code copy, and excessive global flushes. Test signals are self-modifying/JIT code tests, module load, ptrace poke text, and cacheflush build coverage.
 A local static signal for this file is that it has 127 lines and 2400 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/copy_from_user.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/mm/copy_from_user.S

## Purpose

`copy_from_user.S` instantiates the Hexagon user-copy template for reads from userspace into kernel memory. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

It defines `FUNCNAME` as `raw_copy_from_user` and supplies exception labels that return the uncopied byte count. Concrete declarations observed in the file: Includes: `copy_user_template.S`. Macros: `src_sav`, `dst_sav`, `src_dst_sav`, `d_dbuf`, `w_dbuf`, `dst`, `src`, `bytes`, `loopcount`, `FUNCNAME`.

## Control Flow, State, And Persistence

Runtime flow copies 8/4/2/1-byte chunks using the shared template; exception fixups adjust `r2` for remaining bytes.

## Dependencies And Integration Points

It integrates with `copy_user_template.S`, exception tables, uaccess core, and exported user-copy symbols.

## Risks And Test Signals

Risks are bad residual counts, missing exception entries, and kernel faults on invalid userspace pointers. Test signals are uaccess selftests, `copy_from_user` fault injection, and syscall argument copying.
 A local static signal for this file is that it has 102 lines and 1687 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/copy_from_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/copy_to_user.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/mm/copy_to_user.S

## Purpose

`copy_to_user.S` instantiates the Hexagon user-copy template for writes from kernel memory to userspace. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

It defines `FUNCNAME` as `raw_copy_to_user` and write-side exception fixup labels. Concrete declarations observed in the file: Includes: `copy_user_template.S`. Macros: `src_sav`, `dst_sav`, `src_dst_sav`, `d_dbuf`, `w_dbuf`, `dst`, `src`, `bytes`, `loopcount`, `FUNCNAME`.

## Control Flow, State, And Persistence

Runtime flow mirrors `copy_from_user` but faults are based on user destination writes; fixups compute remaining bytes.

## Dependencies And Integration Points

It integrates with `copy_user_template.S`, exception tables, and generic uaccess APIs.

## Risks And Test Signals

Risks are partial-copy accounting errors and unsafe writes after faults. Test signals are uaccess selftests, signal frame copyout, and invalid-pointer syscall tests.
 A local static signal for this file is that it has 80 lines and 1551 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/copy_to_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/copy_user_template.S -->
# sources/distributed-fs/ceph-client/arch/hexagon/mm/copy_user_template.S

## Purpose

`copy_user_template.S` is the shared assembly body for Hexagon raw user-copy routines. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The including file defines register aliases and `FUNCNAME`; template labels implement aligned and unaligned 8/4/2/1-byte loops with extable-visible fault sites. Concrete declarations observed in the file: Assembly entry labels: `FUNCNAME`, `.Loop8`, `.Loop_not_aligned_8`, `.Loop4`, `.Loop_not_aligned_4`, `.Loop2`, `.Loop_not_aligned`, `.Loop1`, `.Lsmall`, `.Ldone`, `.Lalign`.

## Control Flow, State, And Persistence

Runtime flow prefers 8-byte transfers, falls back through smaller chunks for alignment/tail, and returns the uncopied byte count after fixup.

## Dependencies And Integration Points

It integrates with `copy_from_user.S`, `copy_to_user.S`, `uaccess.c`, and architecture exception-table handling.

## Risks And Test Signals

Risks are template changes breaking both copy directions or exception label numbering. Test signals are fault-injection uaccess tests and randomized partial-copy tests.
 A local static signal for this file is that it has 173 lines and 2667 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/copy_user_template.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/mm/init.c

## Purpose

`init.c` implements Hexagon memory initialization, boot memory sizing, DMA reservation, initial segment-table pruning, cache/page protection defaults, and zone limits. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs and state include `bootmem_lastpg`, `__phys_offset`, `_dflt_cache_att`, `sync_icache_dcache`, `arch_zone_limits_init`, `setup_arch_memory`, `hexagon_coherent_pool_size`, and `protection_map`. Concrete declarations observed in the file: Includes: `linux/init.h`, `linux/mm.h`, `linux/memblock.h`, `asm/atomic.h`, `linux/highmem.h`, `asm/tlb.h`, `asm/sections.h`, `asm/setup.h`, `asm/vm_mmu.h`. Macros: `bootmem_startpg`, `DMA_RESERVE`, `DMA_CHUNKSIZE`, `DMA_RESERVED_BYTES`. Types referenced or declared: `page`. Functions/syscalls: `sync_icache_dcache`, `arch_zone_limits_init`, `paging_init`, `early_mem`, `setup_arch_memory`.

## Control Flow, State, And Persistence

Boot flow parses `mem=`, adds/reserves memblock ranges, reserves the coherent DMA top-of-RAM pool, trims early segment-table entries past physical memory, initializes paging, and exposes page protection mapping.

## Dependencies And Integration Points

It integrates with `setup.c`, `vm_init_segtable.S`, memblock, generic MM, DMA setup, and cache synchronization.

## Risks And Test Signals

Risks are off-by-one PFNs, reserving too much/little DMA memory, invalidating required mappings, and wrong page protections. Test signals are boot memory logs, memblock debug, DMA coherent allocation, page-fault tests, and mmap permission tests.
 A local static signal for this file is that it has 245 lines and 7545 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/uaccess.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/mm/uaccess.c

## Purpose

`uaccess.c` provides Hexagon uaccess helper logic beyond the assembly raw-copy routines. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The file implements user memory clearing/copy support paths used by generic uaccess wrappers. Concrete declarations observed in the file: Includes: `linux/types.h`, `linux/uaccess.h`, `linux/pgtable.h`.

## Control Flow, State, And Persistence

Runtime flow walks user pages/ranges and relies on access checks and exception fixups for invalid addresses.

## Dependencies And Integration Points

It integrates with `linux/uaccess.h`, raw copy assembly, and page-table helpers.

## Risks And Test Signals

Risks are bad residual counts, page-boundary mistakes, and missing fault handling. Test signals are uaccess selftests, invalid pointer syscalls, and signal frame copy tests.
 A local static signal for this file is that it has 38 lines and 999 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/uaccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/vm_fault.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/mm/vm_fault.c

## Purpose

`vm_fault.c` implements Hexagon page-fault handling for execute, load, and store protection faults. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `read_protection_fault`, `write_protection_fault`, `execute_protection_fault`, and internal `do_page_fault`. Concrete declarations observed in the file: Includes: `asm/traps.h`, `asm/vm_fault.h`, `linux/uaccess.h`, `linux/mm.h`, `linux/sched/signal.h`, `linux/signal.h`, `linux/extable.h`, `linux/hardirq.h`, `linux/perf_event.h`. Macros: `FLT_IFETCH`, `FLT_LOAD`, `FLT_STORE`. Types referenced or declared: `pt_regs`, `vm_area_struct`, `mm_struct`, `exception_table_entry`. Functions/syscalls: `do_page_fault`, `read_protection_fault`, `write_protection_fault`, `execute_protection_fault`.

## Control Flow, State, And Persistence

Runtime flow rejects faults in interrupt/no-mm context, enables IRQs, finds/locks the VMA, checks access rights, calls `handle_mm_fault`, handles retry/OOM/SIGBUS/SIGSEGV, and uses exception-table fixups for kernel faults.

## Dependencies And Integration Points

It integrates with `traps.c`, generic MM fault machinery, perf page-fault events, uaccess exception tables, and signal delivery.

## Risks And Test Signals

Risks are mmap-lock leaks, wrong access-right classification, failure to fix up kernel uaccess faults, and signal-code mismatch. Test signals are page-fault selftests, COW/mmap stress, invalid user access, and kernel uaccess fault injection.
 A local static signal for this file is that it has 178 lines and 3856 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/vm_fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/vm_tlb.c -->
# sources/distributed-fs/ceph-client/arch/hexagon/mm/vm_tlb.c

## Purpose

`vm_tlb.c` implements Hexagon TLB flush hooks. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `flush_tlb_one`, `tlb_flush_all`, `flush_tlb_mm`, `flush_tlb_page`, and `flush_tlb_kernel_range`. Concrete declarations observed in the file: Includes: `linux/mm.h`, `linux/sched.h`, `asm/page.h`, `asm/hexagon_vm.h`, `asm/tlbflush.h`. Types referenced or declared: `vm_area_struct`, `mm_struct`. Functions/syscalls: `flush_tlb_range`, `flush_tlb_one`, `tlb_flush_all`, `flush_tlb_mm`, `flush_tlb_page`, `flush_tlb_kernel_range`.

## Control Flow, State, And Persistence

Runtime flow issues HVM TLB/cache operations for single addresses, processes, pages, and kernel ranges; broader operations may degrade to full TLB flushes.

## Dependencies And Integration Points

It integrates with generic MMU gather, context switching, page-table updates, and HVM VM ops.

## Risks And Test Signals

Risks are stale translations, overbroad expensive flushes, and SMP shootdown gaps. Test signals are mmap/munmap/mprotect stress, fork/exec, page migration, and TLB debug instrumentation.
 A local static signal for this file is that it has 83 lines and 2250 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/mm/vm_tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/Kbuild -->
# sources/distributed-fs/ceph-client/arch/loongarch/Kbuild

## Purpose

`Kbuild` is the top-level LoongArch Kbuild dispatcher. It descends into kernel, mm, net, vdso, optional KVM, and boot subdirectories. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The API is the object/subdir routing via `obj-y`, `obj-$(subst m,y,$(CONFIG_KVM))`, and `subdir-`. Concrete declarations observed in the file: Build/script rules: `obj-y += kernel/`, `obj-y += mm/`, `obj-y += net/`, `obj-y += vdso/`, `obj-$(subst m,y,$(CONFIG_KVM)) += kvm/`, `subdir- += boot`.

## Control Flow, State, And Persistence

Build-time only; it determines which architecture directories are visited during `vmlinux` and boot-image builds.

## Dependencies And Integration Points

It integrates with the global Linux Kbuild recursion and all LoongArch architecture subtrees.

## Risks And Test Signals

Risks are missing architecture subdirectories or incorrect optional KVM inclusion. Test signals are LoongArch defconfig/allmodconfig builds and `make arch/loongarch/...` target coverage.
 A local static signal for this file is that it has 10 lines and 131 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/Kconfig -->
# sources/distributed-fs/ceph-client/arch/loongarch/Kconfig

## Purpose

`Kconfig` defines the main LoongArch architecture configuration surface: 32/64-bit selection, CPU subtype, paging levels, toolchain capability probes, ACPI/EFI/PCI/NUMA/SMP/MMU support, unwinders, module support, and many generic-kernel feature selects. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The public API is the Kconfig symbol set consumed by the build system and source `#ifdef`s, including `LOONGARCH`, `32BIT`, `64BIT`, `MACH_LOONGSON32`, `MACH_LOONGSON64`, paging-level symbols, toolchain probes, errata, and feature toggles. Concrete declarations observed in the file: Kconfig symbols: `LOONGARCH`, `32BIT`, `64BIT`, `32BIT_REDUCED`, `32BIT_STANDARD`, `GENERIC_BUG`, `GENERIC_BUG_RELATIVE_POINTERS`, `GENERIC_CALIBRATE_DELAY`, `GENERIC_CSUM`, `GENERIC_HWEIGHT`, `L1_CACHE_SHIFT`, `LOCKDEP_SUPPORT`, `STACKTRACE_SUPPORT`, `MACH_LOONGSON32`, `MACH_LOONGSON64`, `FIX_EARLYCON_MEM`, `PGTABLE_2LEVEL`, `PGTABLE_3LEVEL`, `PGTABLE_4LEVEL`, `PGTABLE_LEVELS`, `SCHED_OMIT_FRAME_POINTER`, `AS_HAS_EXPLICIT_RELOCS`, `AS_HAS_FCSR_CLASS`, `AS_HAS_THIN_ADD_SUB`, `AS_HAS_LSX_EXTENSION`, `AS_HAS_LASX_EXTENSION`, `AS_HAS_LBT_EXTENSION`, `AS_HAS_LVZ_EXTENSION`, `AS_HAS_SCQ_EXTENSION`, `CC_HAS_ANNOTATE_TABLEJUMP`, and 56 more. Build/script rules: `def_bool $(rustc-option,-Cllvm-args=--loongarch-annotate-tablejump)`, `(Note: power management support will enable this option`, `You can override this setting via writecombine=on/off boot parameter.`.

## Control Flow, State, And Persistence

Kconfig flow is dependency resolution, defaults, `select` propagation, and user choices. It persists in `.config` and generated autoconf headers that steer compilation.

## Dependencies And Integration Points

It integrates with generic kernel Kconfig menus, LoongArch Makefile flag selection, ACPI/EFI/PCI/SMP/MM subsystems, objtool/ORC support, and platform defconfigs.

## Risks And Test Signals

Risks are invalid selects, impossible dependencies, broken 32-bit/64-bit combinations, and enabling features without source/toolchain support. Test signals are `olddefconfig`, randconfig, 32-bit and 64-bit defconfig builds, toolchain-probe coverage, and boot smoke tests.
 A local static signal for this file is that it has 823 lines and 24225 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/Makefile -->
# sources/distributed-fs/ceph-client/arch/loongarch/Makefile

## Purpose

`Makefile` is the top-level LoongArch architecture Makefile. It selects default defconfig, image names, cross-compile prefixes, ABI/toolchain flags, relocation policy, objtool/Rust flags, load address, VDSO preparation, libraries, drivers, install, and help targets. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The build API is the set of Kbuild variables and targets such as `KBUILD_DEFCONFIG`, `KBUILD_IMAGE`, `cflags-y`, `ld-emul`, `KBUILD_AFLAGS`, `KBUILD_CFLAGS`, `KBUILD_RUSTFLAGS`, `load-y`, `vdso_prepare`, `vmlinux.elf`, `vmlinux.efi`, and `install`. Concrete declarations observed in the file: Build/script rules: `boot	:= arch/loongarch/boot`, `KBUILD_DEFCONFIG := loongson32_defconfig`, `KBUILD_DEFCONFIG := loongson64_defconfig`, `KBUILD_DTBS      := dtbs`, `image-name-y			:= vmlinux`, `image-name-$(CONFIG_EFI_ZBOOT)	:= vmlinuz`, `KBUILD_IMAGE	:= $(boot)/vmlinux.elf`, `KBUILD_IMAGE	:= $(boot)/$(image-name-y).efi`, `32bit-tool-archpref	= loongarch32`, `64bit-tool-archpref	= loongarch64`, `32bit-bfd		= elf32-loongarch`, `64bit-bfd		= elf64-loongarch`, `32bit-emul		= elf32loongarch`, `64bit-emul		= elf64loongarch`, `CC_FLAGS_FPU		:= -mfpu=64`, `CC_FLAGS_NO_FPU		:= -msoft-float`, `orc_hash_h := arch/$(SRCARCH)/include/generated/asm/orc_hash.h`, `orc_hash_sh := $(srctree)/scripts/orc_hash.sh`, and 75 more.

## Control Flow, State, And Persistence

Build flow resolves 32-bit versus 64-bit toolchain mode, probes compiler/assembler options, prepares ORC/VDSO generated headers, selects EFI or ELF image generation, and delegates boot image creation to `arch/loongarch/boot`.

## Dependencies And Integration Points

It integrates with Kconfig feature probes, scripts/orc_hash.sh, objtool, Rust target settings, EFI stub libraries, VDSO build, and platform install scripts.

## Risks And Test Signals

Risks are toolchain option incompatibility, wrong ABI/load address, broken relocatable/EFI image flags, or VDSO generation failures. Test signals are 32-bit/64-bit defconfig builds, `make Image` equivalents, EFI zboot builds, objtool-enabled builds, and cross-compile prefix detection.
 A local static signal for this file is that it has 232 lines and 7932 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/loongarch/boot/Makefile

## Purpose

`Makefile` builds LoongArch boot images from `vmlinux`, including stripped `vmlinux.elf`, EFI images, and EFI zboot payload metadata. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important build variables include `OBJCOPYFLAGS_vmlinux.efi`, `EFI_ZBOOT_PAYLOAD`, `EFI_ZBOOT_BFD_TARGET`, and image targets `vmlinux.elf`/`vmlinux.efi`. Concrete declarations observed in the file: Build/script rules: `drop-sections := .comment .note .options .note.gnu.build-id`, `strip-flags   := $(addprefix --remove-section=,$(drop-sections)) -S`, `OBJCOPYFLAGS_vmlinux.efi := -O binary $(strip-flags)`, `quiet_cmd_strip = STRIP	  $@`, `cmd_strip = $(STRIP) -s -o $@ $<`, `targets := vmlinux.elf`, `$(obj)/vmlinux.elf: vmlinux FORCE`, `targets += vmlinux.efi`, `$(obj)/vmlinux.efi: vmlinux FORCE`, `EFI_ZBOOT_PAYLOAD      := vmlinux.efi`, `EFI_ZBOOT_BFD_TARGET   := elf32-loongarch`, `EFI_ZBOOT_MACH_TYPE    := LOONGARCH32`, `EFI_ZBOOT_BFD_TARGET   := elf64-loongarch`, `EFI_ZBOOT_MACH_TYPE    := LOONGARCH64`.

## Control Flow, State, And Persistence

Build flow invokes objcopy with section removal for boot images and selects 32-bit or 64-bit EFI zboot metadata from configuration.

## Dependencies And Integration Points

It integrates with the top-level LoongArch Makefile, EFI stub/zboot infrastructure, and kernel install targets.

## Risks And Test Signals

Risks are wrong BFD target, stripping required sections, or mismatched EFI machine type. Test signals are `make vmlinux.elf`, `make vmlinux.efi`, zboot builds, and `file/readelf` image inspection.
 A local static signal for this file is that it has 33 lines and 818 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/boot/dts/Makefile -->
# sources/distributed-fs/ceph-client/arch/loongarch/boot/dts/Makefile

## Purpose

`Makefile` is the LoongArch boot devicetree Makefile. In this snapshot it is a placeholder with SPDX metadata and no DTB targets. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

There are no local build targets; the file preserves the directory hook for future board DTBs. Concrete declarations observed in the file: Build/script rules: `dtb-y = loongson-2k0500-ref.dtb loongson-2k1000-ref.dtb loongson-2k2000-ref.dtb`.

## Control Flow, State, And Persistence

Build-time only; it is reached from the boot build when DTB targets exist.

## Dependencies And Integration Points

It integrates with `KBUILD_DTBS := dtbs` in the architecture Makefile and the boot subtree.

## Risks And Test Signals

Risks are silent absence of expected DTB targets for DT-based boards. Test signals are `make ARCH=loongarch dtbs` and manifest checks for supported boards.
 A local static signal for this file is that it has 4 lines and 121 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/boot/dts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/boot/install.sh -->
# sources/distributed-fs/ceph-client/arch/loongarch/boot/install.sh

## Purpose

`install.sh` is the LoongArch kernel install helper invoked by `make install` when no external installkernel handler overrides it. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Its script API takes kernel version, kernel image, System.map, and install path arguments, then copies or delegates installation using the distribution/user install hook conventions. Concrete declarations observed in the file: Build/script rules: `base=vmlinux`, `base=vmlinuz`.

## Control Flow, State, And Persistence

Runtime flow validates arguments and paths, finds an install command if available, and installs image/map artifacts under the requested install directory.

## Dependencies And Integration Points

It integrates with the architecture Makefile `install` target, `/sbin/installkernel`, user `~/bin/installkernel`, and bootloader packaging scripts.

## Risks And Test Signals

Risks are wrong default install path, missing executable checks, or overwriting boot artifacts. Test signals are dry-run/staged `INSTALL_PATH` installs and packaging CI.
 A local static signal for this file is that it has 57 lines and 1244 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/boot/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/loongarch/crypto/Kconfig

## Purpose

`Kconfig` is the LoongArch crypto Kconfig include point. In this snapshot it contains only SPDX/comment structure and no selectable crypto accelerators. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

There are no local config symbols; its API is the placeholder menu integration for future LoongArch crypto options. Concrete declarations observed in the file: The file exports only a small static interface and has no local declarations beyond its include guard or build stanza.

## Control Flow, State, And Persistence

Build-time only; Kconfig parses it when architecture crypto support is visited.

## Dependencies And Integration Points

It integrates with `arch/loongarch/crypto/Makefile` and the global crypto Kconfig tree.

## Risks And Test Signals

Risks are currently low, mainly accidental removal of a needed include point. Test signals are Kconfig parse and LoongArch allnoconfig/allmodconfig.
 A local static signal for this file is that it has 6 lines and 109 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/loongarch/crypto/Makefile

## Purpose

`Makefile` is the LoongArch crypto object Makefile. In this snapshot it contains no objects, matching the empty crypto Kconfig. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

There are no local object targets; it is a placeholder for future accelerated crypto code. Concrete declarations observed in the file: The file exports only a small static interface and has no local declarations beyond its include guard or build stanza.

## Control Flow, State, And Persistence

Build-time only and currently a no-op.

## Dependencies And Integration Points

It integrates with `drivers-y += arch/loongarch/crypto/` in the architecture Makefile.

## Risks And Test Signals

Risks are low unless crypto objects are added without Kconfig wiring. Test signals are LoongArch allmodconfig and crypto build target traversal.
 A local static signal for this file is that it has 5 lines and 79 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/Kbuild

## Purpose

`Kbuild` is the top-level LoongArch Kbuild dispatcher. It descends into kernel, mm, net, vdso, optional KVM, and boot subdirectories. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The API is the object/subdir routing via `obj-y`, `obj-$(subst m,y,$(CONFIG_KVM))`, and `subdir-`. Concrete declarations observed in the file: Build/script rules: `syscall-y += syscall_table_32.h`, `syscall-y += syscall_table_64.h`, `generated-y += orc_hash.h`, `generic-y += mcs_spinlock.h`, `generic-y += parport.h`, `generic-y += early_ioremap.h`, `generic-y += qrwlock.h`, `generic-y += user.h`, `generic-y += ioctl.h`, `generic-y += mmzone.h`, `generic-y += statfs.h`, `generic-y += text-patching.h`.

## Control Flow, State, And Persistence

Build-time only; it determines which architecture directories are visited during `vmlinux` and boot-image builds.

## Dependencies And Integration Points

It integrates with the global Linux Kbuild recursion and all LoongArch architecture subtrees.

## Risks And Test Signals

Risks are missing architecture subdirectories or incorrect optional KVM inclusion. Test signals are LoongArch defconfig/allmodconfig builds and `make arch/loongarch/...` target coverage.
 A local static signal for this file is that it has 15 lines and 343 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/acenv.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/acenv.h

## Purpose

`acenv.h` provides LoongArch ACPICA environment definitions, currently marking ACPI misalignment as unsupported. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The API is `ACPI_MISALIGNMENT_NOT_SUPPORTED` under the include guard. Concrete declarations observed in the file: Macros: `_ASM_LOONGARCH_ACENV_H`, `ACPI_MISALIGNMENT_NOT_SUPPORTED`.

## Control Flow, State, And Persistence

No runtime flow; it changes ACPICA compile-time assumptions.

## Dependencies And Integration Points

It integrates with ACPICA and architecture ACPI code.

## Risks And Test Signals

Risks are ACPICA making unaligned accesses on cores that trap. Test signals are ACPI table parsing on LoongArch and compiler header checks.
 A local static signal for this file is that it has 18 lines and 482 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/acenv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/acpi.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/acpi.h

## Purpose

`acpi.h` declares LoongArch ACPI integration helpers and constants for MADT CPU discovery, wakeup address handling, and ACPI table upgrade limits. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important APIs include `disable_acpi`, `acpi_has_cpu_in_madt`, `acpi_get_wakeup_address`, `acpi_os_ioremap`, `MAX_CORE_PIC`, and `struct acpi_madt_core_pic` references. Concrete declarations observed in the file: Includes: `asm/smp.h`, `asm/suspend.h`. Macros: `_ASM_LOONGARCH_ACPI_H`, `acpi_os_ioremap`, `MAX_CORE_PIC`, `ACPI_TABLE_UPGRADE_MAX_PHYS`. Types referenced or declared: `list_head`, `acpi_madt_core_pic`. Functions/syscalls: `disable_acpi`, `acpi_has_cpu_in_madt`, `acpi_get_wakeup_address`.

## Control Flow, State, And Persistence

Runtime flow is elsewhere; this header supplies prototypes and constants used during ACPI boot, CPU enumeration, suspend, and ioremap.

## Dependencies And Integration Points

It integrates with SMP, suspend, ACPI MADT parsing, and generic ACPI OS services.

## Risks And Test Signals

Risks are CPU discovery mismatch, wake address errors, and incorrect table-upgrade physical limits. Test signals are ACPI boot logs, CPU enumeration, suspend/resume, and MADT parsing tests.
 A local static signal for this file is that it has 59 lines and 1293 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/addrspace.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/addrspace.h

## Purpose

`addrspace.h` defines LoongArch virtual/physical address-space translation constants and helpers for direct mapped windows, cached/uncached aliases, physical masks, fixed addresses, and `PAGE_OFFSET`. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs include `PHYS_OFFSET`, `IO_BASE`, `CACHE_BASE`, `UNCACHE_BASE`, `TO_PHYS`, `TO_CACHE`, `TO_UNCACHE`, `PAGE_OFFSET`, `FIXADDR_TOP`, and CAC address helpers. Concrete declarations observed in the file: Includes: `linux/const.h`, `linux/sizes.h`, `asm/loongarch.h`. Macros: `_ASM_ADDRSPACE_H`, `PHYS_OFFSET`, `IO_BASE`, `CACHE_BASE`, `UNCACHE_BASE`, `WRITECOMBINE_BASE`, `DMW_PABITS`, `TO_PHYS_MASK`, `HIGHMEM_START`, `TO_PHYS`, `TO_CACHE`, `TO_UNCACHE`, `PAGE_OFFSET`, `FIXADDR_TOP`, `_ATYPE_`, `_ATYPE32_`, `_ATYPE64_`, `_CONST64_`, `_ACAST32_`, `_ACAST64_`, `UVRANGE`, `KPRANGE0`, `KPRANGE1`, `KVRANGE`, and 10 more.

## Control Flow, State, And Persistence

No local runtime flow; the macros are compiled into MM, IO, boot, and drivers to translate addresses.

## Dependencies And Integration Points

It integrates with CSR direct mapping windows, page-table setup, ioremap, highmem, and low-level boot code.

## Risks And Test Signals

Risks are wrong physical mask width, cached/uncached alias confusion, and 32/64-bit address truncation. Test signals are boot memory map logs, ioremap tests, DMA/IO access, and sparse address checks.
 A local static signal for this file is that it has 149 lines and 3288 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/addrspace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/alternative-asm.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/alternative-asm.h

## Purpose

`alternative-asm.h` defines assembly macros for LoongArch runtime instruction alternatives. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The API emits original and replacement instruction regions plus `.altinstructions` metadata for one or two feature alternatives. Concrete declarations observed in the file: Includes: `asm/asm.h`. Macros: `_ASM_ALTERNATIVE_ASM_H`, `old_len`, `new_len1`, `new_len2`, `alt_max_short`. Types referenced or declared: `alt_instr`.

## Control Flow, State, And Persistence

Runtime patching is performed by alternative code elsewhere; this header contributes annotated sections during assembly.

## Dependencies And Integration Points

It integrates with CPU feature detection, `alternative.h`, linker sections, and boot-time patching.

## Risks And Test Signals

Risks are length mismatches, bad section metadata, and patching the wrong instruction stream. Test signals are objdump of `.altinstructions`, boot on CPUs with/without features, and alternative patch debug logs.
 A local static signal for this file is that it has 83 lines and 2088 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/alternative-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/alternative.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/alternative.h

## Purpose

`alternative.h` provides C inline-assembly macros and `struct alt_instr` metadata for LoongArch alternatives. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important APIs are `ALTERNATIVE`, `ALTERNATIVE_2`, `alternative`, `alternative_2`, `ALTINSTR_ENTRY`, and `struct alt_instr`. Concrete declarations observed in the file: Includes: `linux/types.h`, `linux/stddef.h`, `linux/stringify.h`, `asm/asm.h`. Macros: `_ASM_ALTERNATIVE_H`, `b_replacement`, `e_replacement`, `alt_end_marker`, `alt_slen`, `alt_total_slen`, `alt_rlen`, `__OLDINSTR`, `OLDINSTR`, `alt_max_short`, `OLDINSTR_2`, `ALTINSTR_ENTRY`, `ALTINSTR_REPLACEMENT`, `ALTERNATIVE`, `ALTERNATIVE_2`, `alternative`, `alternative_2`. Types referenced or declared: `alt_instr`.

## Control Flow, State, And Persistence

Compile-time macros emit old instructions, replacement instructions, and metadata; boot/runtime alternative patching later selects code based on CPU feature bits.

## Dependencies And Integration Points

It integrates with CPU feature handling, linker sections, and low-level asm helpers.

## Risks And Test Signals

Risks are instruction length mismatch, bad feature selection, and clobbered inline-asm constraints. Test signals are alternative selftests, objdump, and feature-specific boot coverage.
 A local static signal for this file is that it has 112 lines and 3859 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/alternative.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm-extable.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm-extable.h

## Purpose

`asm-extable.h` defines LoongArch assembly exception-table encodings and helpers for normal fixups, uaccess err/zero fixups, and BPF fixups. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important APIs include `EX_TYPE_*`, `__ASM_EXTABLE_RAW`, `_ASM_EXTABLE`, `_ASM_EXTABLE_UACCESS_ERR_ZERO`, and packed `EX_DATA_REG` fields. Concrete declarations observed in the file: Includes: `linux/bits.h`, `linux/stringify.h`, `asm/gpr-num.h`. Macros: `__ASM_ASM_EXTABLE_H`, `EX_TYPE_NONE`, `EX_TYPE_FIXUP`, `EX_TYPE_UACCESS_ERR_ZERO`, `EX_TYPE_BPF`, `__ASM_EXTABLE_RAW`, `_ASM_EXTABLE`, `EX_DATA_REG_ERR_SHIFT`, `EX_DATA_REG_ERR`, `EX_DATA_REG_ZERO_SHIFT`, `EX_DATA_REG_ZERO`, `EX_DATA_REG`, `_ASM_EXTABLE_UACCESS_ERR_ZERO`, `_ASM_EXTABLE_UACCESS_ERR`.

## Control Flow, State, And Persistence

No direct runtime flow; macros emit exception-table records consumed by the exception fixup engine during faults.

## Dependencies And Integration Points

It integrates with uaccess assembly, BPF JIT/exception paths, linker exception-table sorting, and fault handlers.

## Risks And Test Signals

Risks are wrong relative/absolute encoding, invalid register packing, and broken uaccess residual/error handling. Test signals are uaccess fault tests, BPF probe tests, and exception-table objdump inspection.
 A local static signal for this file is that it has 66 lines and 1717 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm-extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm-offsets.h

## Purpose

`asm-offsets.h` wraps the generated LoongArch `asm-offsets.h` header. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Its API is whatever constants are generated from architecture offset code. Concrete declarations observed in the file: Includes: `generated/asm-offsets.h`.

## Control Flow, State, And Persistence

No runtime flow; it provides assembly-safe numeric offsets at build time.

## Dependencies And Integration Points

It integrates with assembly files that need C-structure offsets.

## Risks And Test Signals

Risks are stale generation or include-path breakage. Test signals are successful assembly and generated-header dependency checks.
 A local static signal for this file is that it has 6 lines and 148 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm-prototypes.h

## Purpose

`asm-prototypes.h` declares prototypes needed by LoongArch assembly and modversion tooling, including uaccess, FPU, LBT, MMU context, page, ftrace, and generic asm prototypes. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The API is the included prototype set and forward declarations for task, register, KVM, and FPU types. Concrete declarations observed in the file: Includes: `linux/uaccess.h`, `asm/fpu.h`, `asm/lbt.h`, `asm/mmu_context.h`, `asm/page.h`, `asm/ftrace.h`, `asm-generic/asm-prototypes.h`. Types referenced or declared: `task_struct`, `pt_regs`, `kvm_run`, `kvm_vcpu`, `loongarch_fpu`.

## Control Flow, State, And Persistence

Build-time only; it ensures symbol CRC/prototype visibility for assembly-callable routines.

## Dependencies And Integration Points

It integrates with modversions, ftrace, KVM, FPU/LBT code, and asm-generic prototypes.

## Risks And Test Signals

Risks are missing prototypes causing modversion drift or build warnings. Test signals are `CONFIG_MODVERSIONS`, modules build, and W=1 compile checks.
 A local static signal for this file is that it has 43 lines and 1207 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm.h

## Purpose

`asm.h` defines LoongArch assembly portability macros for register sizes, load/store mnemonics, stack alignment, symbol annotations, relocation/address loading, and prefetch helpers. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs include `SZREG`, `REG_L`, `REG_S`, `LONG_L`, `PTR_L`, `FEXPORT`, `LEAF`, `NESTED`, `END`, `la_abs`, `la_pcrel`, and related relocation macros. Concrete declarations observed in the file: Macros: `__ASM_ASM_H`, `PREF`, `PREFX`, `STACK_ALIGN`, `SZREG`, `REG_L`, `REG_S`, `REG_ADD`, `REG_SUB`, `INT_ADD`, `INT_ADDI`, `INT_SUB`, `INT_L`, `INT_S`, `INT_SLLI`, `INT_SLLV`, `INT_SRLI`, `INT_SRLV`, `INT_SRAI`, `INT_SRAV`, `LONG_ADD`, `LONG_ADDI`, `LONG_ALSL`, `LONG_BSTRINS`, and 43 more.

## Control Flow, State, And Persistence

No runtime flow; macros expand into assembly instructions and ELF symbol metadata.

## Dependencies And Integration Points

It integrates with almost every LoongArch assembly source, linker behavior, and toolchain relocation support.

## Risks And Test Signals

Risks are 32/64-bit mnemonic mismatch, bad symbol alignment, and relocation-mode incompatibility. Test signals are full assembly build, objdump symbol checks, and 32/64-bit defconfig builds.
 A local static signal for this file is that it has 239 lines and 4894 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asmmacro.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asmmacro.h

## Purpose

`asmmacro.h` defines higher-level LoongArch assembly macros for saving/restoring registers, FPU/LSX/LASX state, interrupt state, per-CPU access, TLB operations, and stack/task helpers. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The API is the macro collection included by exception entry, context switch, FPU, and VM assembly. Concrete declarations observed in the file: Includes: `linux/sizes.h`, `asm/asm-offsets.h`, `asm/regdef.h`, `asm/fpregdef.h`, `asm/loongarch.h`. Macros: `_ASM_ASMMACRO_H`, `TASK_STRUCT_OFFSET`.

## Control Flow, State, And Persistence

Runtime flow is generated at macro expansion sites; this header shapes how low-level paths preserve architectural state.

## Dependencies And Integration Points

It integrates with generated offsets, register definitions, LoongArch CSR definitions, FPU/vector code, and exception entry.

## Risks And Test Signals

Risks are register corruption, wrong offset use, broken 32/64-bit state handling, and vector-state save bugs. Test signals are boot, context-switch stress, signal/FPU tests, vector extension tests, and objdump review.
 A local static signal for this file is that it has 682 lines and 24914 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asmmacro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/atomic-amo.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/atomic-amo.h

## Purpose

`atomic-amo.h` implements LoongArch atomic operations using AMO instructions. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Macros generate `arch_atomic_*` add/sub/and/or/xor operations, return variants, fetch variants, and relaxed/acquire/release/full-barrier forms. Concrete declarations observed in the file: Includes: `linux/types.h`, `asm/barrier.h`, `asm/cmpxchg.h`. Macros: `_ASM_ATOMIC_AMO_H`, `ATOMIC_OP`, `ATOMIC_OP_RETURN`, `ATOMIC_FETCH_OP`, `ATOMIC_OPS`, `arch_atomic_add_return`, `arch_atomic_add_return_acquire`, `arch_atomic_add_return_release`, `arch_atomic_add_return_relaxed`, `arch_atomic_sub_return`, `arch_atomic_sub_return_acquire`, `arch_atomic_sub_return_release`, `arch_atomic_sub_return_relaxed`, `arch_atomic_fetch_add`, `arch_atomic_fetch_add_acquire`, `arch_atomic_fetch_add_release`, `arch_atomic_fetch_add_relaxed`, `arch_atomic_fetch_sub`, `arch_atomic_fetch_sub_acquire`, `arch_atomic_fetch_sub_release`, `arch_atomic_fetch_sub_relaxed`, `arch_atomic_fetch_and`, `arch_atomic_fetch_and_acquire`, `arch_atomic_fetch_and_release`, and 41 more.

## Control Flow, State, And Persistence

Runtime flow is a single AMO-based read-modify-write sequence with optional barriers selected by the generated variant.

## Dependencies And Integration Points

It integrates with `atomic.h`, barrier primitives, cmpxchg support, locking, refcounts, and generic atomic APIs.

## Risks And Test Signals

Risks are missing memory ordering, incorrect old/new return values, and CPU support assumptions. Test signals are atomic selftests, lock/refcount stress, KCSAN, and SMP boot.
 A local static signal for this file is that it has 207 lines and 7349 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/atomic-amo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/atomic-llsc.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/atomic-llsc.h

## Purpose

`atomic-llsc.h` implements LoongArch atomic operations using load-linked/store-conditional loops. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Macros generate `arch_atomic_*` add/sub and bitwise operations with retry loops and relaxed variants. Concrete declarations observed in the file: Includes: `linux/types.h`, `asm/barrier.h`, `asm/cmpxchg.h`. Macros: `_ASM_ATOMIC_LLSC_H`, `ATOMIC_OP`, `ATOMIC_OP_RETURN`, `ATOMIC_FETCH_OP`, `ATOMIC_OPS`, `arch_atomic_add_return_relaxed`, `arch_atomic_sub_return_relaxed`, `arch_atomic_fetch_add_relaxed`, `arch_atomic_fetch_sub_relaxed`, `arch_atomic_fetch_and_relaxed`, `arch_atomic_fetch_or_relaxed`, `arch_atomic_fetch_xor_relaxed`.

## Control Flow, State, And Persistence

Runtime flow loads the old value, computes a new value, attempts store-conditional, and retries until success; higher-level ordering is supplied through barriers/wrappers.

## Dependencies And Integration Points

It integrates with `atomic.h` as the fallback/alternative to AMO instructions.

## Risks And Test Signals

Risks are livelock under contention, missing clobbers, and ordering mismatch. Test signals are atomic torture tests, lock stress, and SMP contention benchmarks.
 A local static signal for this file is that it has 101 lines and 2964 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/atomic-llsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/atomic.h

## Purpose

`atomic.h` selects and completes LoongArch atomic APIs, providing basic read/set, AMO/LLSC includes, and specialized 32/64-bit helpers such as `sub_if_positive` and `fetch_add_unless`. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important APIs include `ATOMIC_INIT`, `arch_atomic_read`, `arch_atomic_set`, `arch_atomic_sub_if_positive`, `arch_atomic64_fetch_add_unless`, and `arch_atomic64_sub_if_positive`. Concrete declarations observed in the file: Includes: `linux/types.h`, `asm/barrier.h`, `asm/cmpxchg.h`, `asm/atomic-amo.h`, `asm/atomic-llsc.h`, `asm-generic/atomic64.h`. Macros: `_ASM_ATOMIC_H`, `__LL`, `__SC`, `__AMADD`, `__AMOR`, `__AMAND_DB`, `__AMOR_DB`, `__AMXOR_DB`, `ATOMIC_INIT`, `arch_atomic_read`, `arch_atomic_set`, `arch_atomic_fetch_add_unless`, `arch_atomic_dec_if_positive`, `ATOMIC64_INIT`, `arch_atomic64_read`, `arch_atomic64_set`, `arch_atomic64_fetch_add_unless`, `arch_atomic64_dec_if_positive`. Functions/syscalls: `arch_atomic_fetch_add_unless`, `arch_atomic_sub_if_positive`, `arch_atomic64_fetch_add_unless`, `arch_atomic64_sub_if_positive`.

## Control Flow, State, And Persistence

Runtime flow depends on AMO or LLSC generated primitives plus custom loops for conditional operations.

## Dependencies And Integration Points

It integrates with generic atomic64 fallback on 32-bit, barriers, cmpxchg, locking, refcounting, and scheduler counters.

## Risks And Test Signals

Risks are memory ordering holes, 32/64-bit helper divergence, and conditional atomic races. Test signals are atomic selftests, refcount tests, locktorture, and 32-bit/64-bit builds.
 A local static signal for this file is that it has 175 lines and 3910 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/barrier.h

## Purpose

`barrier.h` defines LoongArch memory-ordering primitives using `dbar` hints and maps them to Linux barrier APIs. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs include `DBAR`, `c_sync`, `o_sync`, `ldacq_mb`, `strel_mb`, `mb`, `rmb`, `wmb`, `__smp_mb`, `__smp_store_release`, and `__smp_load_acquire` integrations. Concrete declarations observed in the file: Includes: `asm-generic/barrier.h`. Macros: `__ASM_BARRIER_H`, `DBAR`, `crwrw`, `cr_r_`, `c_w_w`, `orwrw`, `or_r_`, `o_w_w`, `orw_w`, `or_rw`, `c_sync`, `c_rsync`, `c_wsync`, `o_sync`, `o_rsync`, `o_wsync`, `ldacq_mb`, `strel_mb`, `mb`, `rmb`, `wmb`, `iob`, `wbflush`, `__smp_mb`, and 9 more. Functions/syscalls: `array_index_mask_nospec`.

## Control Flow, State, And Persistence

Runtime flow is insertion of hardware ordering instructions around memory operations; no state is stored.

## Dependencies And Integration Points

It integrates with atomics, spinlocks, device IO, SMP synchronization, and asm-generic barrier fallbacks.

## Risks And Test Signals

Risks are under-barriering device or SMP interactions and performance regressions from over-barriering. Test signals are LKMM litmus tests, locktorture, DMA/IO ordering tests, and SMP stress.
 A local static signal for this file is that it has 140 lines and 3352 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/barrier.h -->
