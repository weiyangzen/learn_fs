# subset-b-000696 research

Grouped research report for the requested LoongArch Ceph-client kernel architecture files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgtable-bits.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgtable-bits.h

Purpose: defines the LoongArch software and hardware page-table bit layout used by the MMU, generic memory management, swap encoding, huge pages, and protection macros.
Important APIs and types: exports `_PAGE_*` bit constants for valid, dirty, present, write, global, huge, protnone, special, non-readable, non-executable, accessed, modified, present-invalid, and swap-exclusive state. It also defines cacheability encodings such as `_CACHE_CC`, `_CACHE_SUC`, `_CACHE_WUC`, `_CACHE_UC`, page protection presets like `PAGE_KERNEL`, `PAGE_SHARED`, `PAGE_READONLY`, `PAGE_NONE`, and `__P*`/`__S*` protection tables.
Control flow: there is no runtime flow; the header is consumed at compile time by `pgtable.h`, TLB code, KVM MMU helpers, and architecture memory setup. The conditional layout differs for 32-bit versus 64-bit and for `CONFIG_ARCH_HAS_PTE_SPECIAL`.
State and persistence: the bit definitions are the persistent in-memory ABI of LoongArch PTEs and PMDs. Any mismatch changes how page tables encode permissions, dirty/accessed status, swap entries, and huge-page global bits.
Dependencies and integration: depends on `asm/loongarch.h` cache constants and feeds Linux generic MM APIs through pgprot and pte helpers. It also aligns with hardware CSR/TLB semantics and user-visible behavior such as NX and write protection.
Risks and test signals: risky changes include overlapping bits, stale `_PAGE_CHG_MASK`, or incorrect cacheability flags. Build coverage, boot under page-fault stress, mmap/mprotect/swap tests, THP tests, and KVM page-table tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgtable-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgtable.h

Purpose: implements LoongArch page-table geometry and PTE/PMD/PUD/P4D helper operations for Linux MM.
Important APIs and types: defines `PGDIR_SHIFT`, `PMD_SHIFT`, `PUD_SHIFT`, `PTRS_PER_*`, `VMALLOC_*`, `MODULES_*`, `vmemmap`, invalid page-table sentinel arrays, folded-level helpers, `pfn_pte`, `pte_pfn`, `pmd_pfn`, swap conversion macros, protection mutators such as `pte_mkdirty`, `pte_wrprotect`, `pte_modify`, THP helpers such as `pmd_trans_huge`, and MMU cache update hooks.
Control flow: most paths are inline transforms. Empty upper-level entries point at invalid tables rather than zero; `pmd_present` special-cases huge mappings; `set_pte` writes atomically and emits an SMP barrier for global mappings; `update_mmu_cache_range` iterates pages and calls `__update_tlb`.
State and persistence: page table entries persist memory permissions, PFNs, huge-page status, swap type/offset, exclusive swap state, and global bits. Clearing a PTE preserves `_PAGE_GLOBAL` while dropping other state.
Dependencies and integration: includes generic folded page-table headers based on `CONFIG_PGTABLE_LEVELS`, `asm/pgtable-bits.h`, sparsemem/fixmap definitions, and Linux MM types. It integrates with TLB refill/update code, vmalloc/module layout, KASAN/KFENCE placement, swap, THP, and highmem.
Risks and test signals: address-space layout math depends on `cpu_vabits`, `vm_map_base`, vmemmap size, and KASAN/KFENCE options. Bad invalid-table handling or swap bit layout breaks faults and reclaim. Signals include boot, `mm` selftests, swap stress, THP, KASAN/KFENCE builds, and TLB shootdown regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/prefetch.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/prefetch.h

Purpose: exposes LoongArch cache prefetch helpers to generic code.
Important APIs and types: defines `ARCH_HAS_PREFETCH`, `prefetch`, `prefetchw`, `PREFETCH_STRIDE`, and `prefetch_range`, mapping C calls to LoongArch `preld` hints.
Control flow: `prefetch_range` advances by `PREFETCH_STRIDE` and emits read prefetches for each cache-line-sized step. The single-address helpers are inline assembly with memory operands but no persistent state.
State and persistence: no state is stored; behavior only influences cache residency and timing.
Dependencies and integration: depends on LoongArch prefetch instruction encodings and is consumed by generic kernel hot paths that use architecture prefetch hooks.
Risks and test signals: wrong hint values or addressing constraints can hurt performance or assembler compatibility. Signals are build coverage on supported compilers, memcpy/page-cache benchmarks, and absence of faults when prefetching valid kernel addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/prefetch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/processor.h

Purpose: defines LoongArch task CPU state, architecture thread layout, task-size limits, CPU idle hooks, and process/thread helpers.
Important APIs and types: provides `struct thread_struct` with saved callee registers, CSR/FPU/LBT state, hardware breakpoint arrays, and address-limit state; declares `cpu_probe`, `start_thread`, `release_thread`, `arch_dup_task_struct`, `copy_thread`, `get_wchan`, `__KSTK_TOS`, and idle helpers.
Control flow: generic scheduler and fork code use this header to create, copy, and restore task CPU context. Debug, ptrace, FPU, and hardware breakpoint code read and update fields in `thread_struct`.
State and persistence: the structure persists per-task register state across context switches, lazy FPU/vector state, user TLS, and per-task debug resources. Constants such as `TASK_SIZE`, `STACK_TOP`, and `STACK_TOP_MAX` define user address-space bounds.
Dependencies and integration: integrates with `asm/ptrace.h`, `asm/fpu.h`, `asm/page.h`, `asm/hw_breakpoint.h`, generic scheduler, ELF core dump code, and syscall entry/return paths.
Risks and test signals: layout changes must stay synchronized with assembly offsets and switch code. Signals include fork/exec, ptrace, coredump, lazy FPU/vector, hardware breakpoint, and stack unwinding tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/ptrace.h

Purpose: supplies the kernel-internal LoongArch register frame definition and helpers for exception, syscall, and ptrace paths.
Important APIs and types: defines `struct pt_regs`, `user_mode`, `regs_return_value`, `instruction_pointer`, `profile_pc`, `current_pt_regs`, syscall argument accessors, and register classification macros. It includes CSR fields such as ERA, BADVADDR, CRMD, PRMD, EUEN, ECFG, and ESTAT.
Control flow: assembly entry code saves registers into `pt_regs`; C exception, signal, ptrace, KGDB, ftrace, and syscall code consume and mutate the frame. Helpers distinguish user versus kernel mode and expose the syscall return value in the ABI register.
State and persistence: `pt_regs` is the transient but critical trap-frame state stored on the kernel stack while handling exceptions, interrupts, syscalls, and signal delivery.
Dependencies and integration: aligned with UAPI ptrace register numbering, `asm/asm-offsets.h`, `stackframe.h`, syscall code, signal frame setup, and debugger paths.
Risks and test signals: changing ordering or semantics breaks assembly offsets, coredumps, ptrace, seccomp, and signal restore. Signals include `ptrace` selftests, syscall tracing, signal tests, KGDB, and unwinder coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/qspinlock.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/qspinlock.h

Purpose: customizes queued spinlock behavior for LoongArch and selects architecture paravirtualization hooks when available.
Important APIs and types: includes generic qspinlock definitions, architecture atomic/cmpxchg primitives, and paravirt qspinlock support under the relevant configuration. It exposes the spinlock operations expected by generic locking code.
Control flow: locking flow is delegated to the generic queued spinlock implementation, with LoongArch atomic operations providing acquisition/release ordering and optional PV substitutions.
State and persistence: spinlock state lives in `qspinlock` words owned by callers; this header does not hold global state.
Dependencies and integration: integrates with `asm/cmpxchg.h`, `asm-generic/qspinlock.h`, `asm/paravirt.h`, scheduler/preemption locking, and SMP memory ordering.
Risks and test signals: atomic ordering mistakes show up as deadlocks or data races under SMP. Signals include locktorture, qspinlock selftests, KCSAN/lockdep, and virtualized guest spinlock benchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/qspinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/regdef.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/regdef.h

Purpose: names LoongArch general-purpose registers for assembly sources using ABI-friendly aliases.
Important APIs and types: maps `$r0` through `$r31` to aliases such as `zero`, `ra`, `tp`, `sp`, argument registers, temporaries, saved registers, and `u0`/`fp` according to LoongArch conventions.
Control flow: no runtime flow; assembly files include it so entry, exception, context-switch, and FPU code can use stable symbolic names.
State and persistence: no stored state, but the names define how assembly preserves and interprets calling-convention registers.
Dependencies and integration: used heavily by `entry.S`, `head.S`, `genex.S`, `fpu.S`, `stackframe.h`, and other low-level assembly.
Risks and test signals: a wrong alias corrupts calling convention globally. Signals are assembler build success, boot, syscall entry, context switch, and exception tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/regdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/seccomp.h

Purpose: maps LoongArch syscall architecture identifiers into the generic seccomp/audit ABI.
Important APIs and types: defines `SECCOMP_ARCH_NATIVE` and compatibility constants for 32-bit/64-bit LoongArch when enabled.
Control flow: seccomp and audit code use these constants while evaluating filters against syscall events. There is no local runtime logic.
State and persistence: no state; constants become part of userspace filter ABI expectations.
Dependencies and integration: depends on `linux/audit.h` architecture tags and `asm/unistd.h` syscall-number selection.
Risks and test signals: wrong audit arch values cause filters to match the wrong ABI or reject valid syscalls. Signals include seccomp selftests, audit syscall tests, and compat syscall tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/serial.h

Purpose: supplies LoongArch serial-port defaults to generic 8250/serial code.
Important APIs and types: defines `BASE_BAUD` and includes generic serial support.
Control flow: no runtime control flow; serial drivers consume constants during console/port setup.
State and persistence: no state, but baud-rate defaults influence early console and legacy serial configuration.
Dependencies and integration: integrates with `serial_core`, 8250 drivers, ACPI SPCR parsing, and early console fallback.
Risks and test signals: wrong baud assumptions affect console readability. Signals are earlycon boot logs and serial console regression testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/set_memory.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/set_memory.h

Purpose: declares architecture hooks for changing kernel linear/text mapping attributes.
Important APIs and types: declares `set_memory_x`, `set_memory_nx`, `set_memory_ro`, `set_memory_rw`, and `set_memory_rox` style helpers depending on config.
Control flow: callers such as instruction patching switch pages writable, copy code, then restore executable/read-only permissions.
State and persistence: changes persist in kernel page tables and require cache/TLB coherency handled by implementation files.
Dependencies and integration: integrates with generic `set_memory` APIs, module loading, ftrace/static-call patching, and `inst.c` text modification.
Risks and test signals: wrong permissions can leave text writable or non-executable. Signals include module load/unload, ftrace, live patching, strict RWX checks, and boot warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/set_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/setup.h

Purpose: declares LoongArch early boot parameters and setup-time globals.
Important APIs and types: exposes firmware argument variables, command-line pointers, CPU address-bit globals (`cpu_pabits`, `cpu_vabits`), memory limits, `early_memblock`, `loongarch_parse_*` setup helpers, and boot CPU configuration hooks.
Control flow: early assembly stores firmware arguments; setup code parses them and populates boot configuration before normal memory management and CPU probing.
State and persistence: globals persist early firmware-provided command line, memory layout, and CPU address-size decisions used later by MM and platform code.
Dependencies and integration: shared by `head.S`, environment parsing, CPU probe, memblock setup, EFI/FDT/ACPI paths, and `pgtable.h` layout.
Risks and test signals: wrong setup state breaks boot before diagnostics are rich. Signals include EFI and FDT boot, command-line parsing, memblock reservations, and multiple page-size/address-bit configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/sigframe.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/sigframe.h

Purpose: defines the LoongArch runtime signal frame layout used by signal delivery and `rt_sigreturn`.
Important APIs and types: declares `struct rt_sigframe` containing siginfo, ucontext, and trampoline space.
Control flow: signal setup writes this frame on the user stack; `rt_sigreturn` reads it to restore user register and extended context state.
State and persistence: the frame is user-visible ABI state during signal handlers and must remain layout-compatible.
Dependencies and integration: integrates with `kernel/signal.c`, UAPI `sigcontext.h`, `ucontext.h`, vdso signal return, FPU/LSX/LASX/LBT extended context handling, and user stacks.
Risks and test signals: layout drift breaks signal handlers, debuggers, and libcs. Signals include signal ABI tests, sigaltstack, vector-state signal restore, and ptrace over signal frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/smp.h

Purpose: declares LoongArch SMP CPU mapping, boot, IPI, and hotplug interfaces.
Important APIs and types: exposes logical/physical CPU maps, `cpu_logical_map`, `cpu_number_map`, `loongson_send_ipi_*`, `show_ipi_list`, `start_secondary`, `smp_prepare_*`, `smp_send_stop`, and boot data for secondary CPUs.
Control flow: boot code maps physical CPU IDs from ACPI/FDT, starts secondaries with stack/thread info, and uses IPI helpers for reschedule, call-function, and stop events.
State and persistence: CPU maps and boot data persist per-system CPU topology and handoff state for secondary startup.
Dependencies and integration: integrates with ACPI MADT parsing, topology, irqchip/IPI controllers, scheduler SMP code, CPU hotplug, and `head.S` `smpboot_entry`.
Risks and test signals: CPU ID map corruption causes wrong IPI targets or hotplug failures. Signals include SMP boot, CPU online/offline, scheduler IPIs, kexec crash stop, and topology tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/sparsemem.h

Purpose: provides LoongArch sparsemem/vmemmap sizing and section layout constants.
Important APIs and types: defines `SECTION_SIZE_BITS`, `MAX_PHYSMEM_BITS`, and related memory-model constants with 32-bit/64-bit and NUMA considerations.
Control flow: no runtime flow; generic memory-model code uses these constants to size sections and vmemmap.
State and persistence: constants shape physical memory section indexing and vmemmap placement for the life of the kernel.
Dependencies and integration: consumed by `pgtable.h`, memblock, sparsemem, NUMA, memory hotplug, and vmemmap initialization.
Risks and test signals: too-small limits lose memory; too-large section geometry wastes metadata or breaks PFN math. Signals include high-memory boot, NUMA boot, memory hotplug, and sparsemem build variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/sparsemem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/spinlock.h

Purpose: selects LoongArch spinlock implementation by including queued spinlock support.
Important APIs and types: includes `asm/qspinlock.h` and generic queued read-write locks as required by the kernel locking API.
Control flow: runtime locking behavior is implemented by included generic and architecture atomic code.
State and persistence: lock state is caller-owned; this file only wires type/operation selection.
Dependencies and integration: integrates with SMP atomic primitives, lockdep, scheduler, interrupt paths, and paravirtualized locking when enabled.
Risks and test signals: inclusion/order errors break low-level locking builds. Signals include allmodconfig, locktorture, lockdep, and SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/spinlock_types.h

Purpose: selects the concrete spinlock type definitions for LoongArch.
Important APIs and types: includes `asm-generic/qspinlock_types.h` and read-write lock type definitions expected by generic locking code.
Control flow: no runtime flow; compile-time type selection only.
State and persistence: defines in-memory lock word layout through included type headers.
Dependencies and integration: must match `spinlock.h`, qspinlock code, and architecture atomic operations.
Risks and test signals: type/layout mismatch breaks locking ABI for static initializers and debug code. Signals include compile coverage, lockdep, and locktorture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stackframe.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stackframe.h

Purpose: defines LoongArch assembly macros for saving, restoring, and returning from exception/syscall frames.
Important APIs and types: macros include `SAVE_ALL`, `RESTORE_ALL_AND_RET`, `RESTORE_STATIC`, `RESTORE_SOME`, `RESTORE_SP_AND_RET`, `BACKUP_T0T1`, CFI helpers, and stack/thread pointer setup helpers.
Control flow: entry assembly uses these macros to build `pt_regs`, switch to kernel stacks, preserve callee/caller registers, restore CSR state, and return through `ertn` or equivalent sequences.
State and persistence: macros materialize transient trap state on the kernel stack and restore user/kernel register state after handlers finish.
Dependencies and integration: tied to `pt_regs`, `asm-offsets.c`, `thread_info.h`, `entry.S`, `genex.S`, KGDB/ftrace unwinding, and objtool unwind hints.
Risks and test signals: offset or CFI mistakes cause silent register corruption or bad unwinds. Signals include boot, syscall/interrupt storm tests, signal delivery, lockdep unwinds, KGDB, and objtool/build warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stackframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stackprotector.h

Purpose: initializes stack canaries for LoongArch kernel stack protector support.
Important APIs and types: provides `boot_init_stack_canary` and task canary handling using random data mixed with time/cycle state as available.
Control flow: early boot and fork/task setup call the helper before stack-protected C code relies on `__stack_chk_guard` or per-task canaries.
State and persistence: writes the stack canary value used to detect stack smashing for the boot/current task.
Dependencies and integration: integrates with compiler stack protector instrumentation, scheduler task state, random initialization, and per-task/thread info.
Risks and test signals: predictable or uninitialized canaries reduce hardening; wrong storage breaks compiler-generated checks. Signals include stack protector builds, boot, fork stress, and intentional stack-smash test modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stacktrace.h

Purpose: declares LoongArch stacktrace helpers and stack-frame validation interfaces.
Important APIs and types: defines frame record structures/helpers and declares `arch_stack_walk`, `arch_stack_walk_reliable`, and user stack-walk helpers through generic stacktrace integration.
Control flow: unwinder code walks frames from `pt_regs` or task stacks and feeds return addresses to generic consumers.
State and persistence: no persistent state; it interprets stack contents and saved frame pointers.
Dependencies and integration: consumed by `kernel/stacktrace.c`, `unwind.h`, ftrace, livepatch reliable-stack checks, perf, lockdep, and panic backtraces.
Risks and test signals: weak validation can emit bogus traces or mark unreliable stacks reliable. Signals include unwinder selftests, livepatch reliable-stack checks, NMI/panic backtraces, and user stack walking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/string.h

Purpose: declares/selects optimized LoongArch string and memory routines.
Important APIs and types: wires architecture implementations of functions such as `memcpy`, `memmove`, `memset`, `strlen`, and related helpers when configured, falling back to generic routines otherwise.
Control flow: callers use normal C library-like APIs; the header controls whether architecture assembly/C implementations are visible.
State and persistence: no persistent state; routines modify caller buffers only.
Dependencies and integration: integrated with generic lib/string code, boot code, uaccess-adjacent memory copies, and compiler builtins.
Risks and test signals: wrong prototypes or overlap semantics cause broad memory corruption. Signals include lib/string selftests, KASAN/KMSAN, boot, and filesystem/network copy stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/suspend.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/suspend.h

Purpose: declares low-level LoongArch suspend/resume entry points and saved-state hooks.
Important APIs and types: exposes `loongarch_suspend_enter`/ACPI suspend glue when power management is configured.
Control flow: PM core calls architecture suspend code, which saves CPU state, enters firmware/ACPI low-power flow, then resumes through low-level restore paths.
State and persistence: state is saved in CPU/firmware-specific areas across suspend; this header only declares the interface.
Dependencies and integration: integrates with ACPI suspend, CPU context save/restore, IRQ/clock state, and platform firmware.
Risks and test signals: missing declarations or wrong prototypes break suspend builds; implementation mistakes show as resume crashes. Signals include suspend/resume cycles, CPU hotplug around suspend, and ACPI sleep-state tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/suspend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/switch_to.h

Purpose: declares LoongArch task-switch helpers and lazy FPU/vector context management hooks.
Important APIs and types: exposes `__switch_to`, `resume`, and macros/helpers to save or restore FPU, LSX, LASX, LBT, and hardware breakpoint state during context switches.
Control flow: scheduler calls the assembly/C switch path; lazy state helpers decide whether current task vector/FPU state needs saving and next task state needs restoring or enabling.
State and persistence: per-task `thread_struct` fields persist callee-saved registers and optional accelerator/debug state across scheduling.
Dependencies and integration: depends on processor/thread layout, FPU/LBT headers, hardware breakpoints, and `kernel/switch.S` plus `asm-offsets.c`.
Risks and test signals: stale lazy state leaks register contents across tasks or corrupts computation. Signals include context-switch stress, FPU/vector tests, ptrace over switched tasks, and hardware breakpoint switch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/syscall.h

Purpose: provides LoongArch syscall introspection and mutation helpers for tracing, seccomp, audit, and ptrace.
Important APIs and types: implements `syscall_get_nr`, `syscall_rollback`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`, `syscall_get_arguments`, and syscall argument storage conventions.
Control flow: syscall entry saves arguments in `pt_regs`; tracing/seccomp code uses these helpers before and after `do_syscall` to inspect, modify, or roll back calls.
State and persistence: operates on transient `pt_regs` state, especially syscall number, argument registers, return register, and original first argument.
Dependencies and integration: aligns with `entry.S`, `ptrace.h`, `unistd.h`, audit/seccomp, ftrace/perf syscall tracing, and signal restart handling.
Risks and test signals: ABI register mistakes break tracing or syscall restarts. Signals include `strace`, ptrace syscall tests, seccomp user notification, audit, and syscall restart tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/thread_info.h

Purpose: defines LoongArch low-level thread info layout, stack sizing, and TIF flags.
Important APIs and types: provides `struct thread_info`, `THREAD_SIZE`, `_THREAD_MASK`, `INIT_THREAD_INFO`, and flags such as `TIF_SYSCALL_TRACE`, `TIF_SIGPENDING`, `TIF_NEED_RESCHED`, `TIF_NOTIFY_SIGNAL`, `TIF_SINGLESTEP`, and watch/debug-related flags.
Control flow: entry/return assembly tests TIF flags to decide whether to deliver signals, reschedule, notify tracing/seccomp, or manage debug state.
State and persistence: thread flags and CPU/preempt fields persist in per-task low-level state and are frequently read from assembly.
Dependencies and integration: tied to kernel stack layout, `stackframe.h`, scheduler, signal code, ptrace, syscall work, hardware breakpoints, and assembly offsets.
Risks and test signals: flag-number drift or stack-size mistakes break return-to-user work and stack masking. Signals include scheduler stress, signal/syscall tracing, single-step, and stack overflow detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/time.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/time.h

Purpose: declares LoongArch timer, clockevent, and clocksource setup interfaces.
Important APIs and types: exposes timer init helpers, frequency variables, constant clock event names, and per-CPU timer setup hooks.
Control flow: boot and CPU bring-up initialize the constant counter/timer and register clocksource/clockevent devices; scheduler tick and high-resolution timers then use them.
State and persistence: clock frequency and timer configuration persist globally/per-CPU for timekeeping and scheduling.
Dependencies and integration: integrates with CSR timer registers, `timex.h`, clockevents, clocksource, SMP CPU bring-up, vDSO time data, and ACPI/FDT frequency discovery.
Risks and test signals: wrong frequency or interrupt setup skews time or stalls scheduling. Signals include boot timekeeping, `clocksource` watchdog, hrtimer tests, suspend/resume, and vDSO clock tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/timex.h

Purpose: provides LoongArch cycle-counter access and `get_cycles` support.
Important APIs and types: defines `CLOCK_TICK_RATE`, `cycles_t`, `get_cycles`, `random_get_entropy`, and CSR-based stable counter reads.
Control flow: inline helpers read LoongArch counter registers and return monotonically increasing cycle values to generic time/random/perf users.
State and persistence: no writable state here; it reads hardware counter state.
Dependencies and integration: used by timekeeping, scheduler clock, random entropy, profiling, and vDSO gettimeofday code.
Risks and test signals: counter width/order issues cause time regressions or unstable entropy inputs. Signals include clocksource validation, scheduler-clock monotonicity, and vDSO time tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/tlb.h

Purpose: defines LoongArch TLB batching, refill, and MMU gather integration.
Important APIs and types: declares TLB handler symbols, `tlb_init`, `setup_tlb_handler`, `local_flush_tlb_*`, huge TLB helpers, and generic `tlb_gather_mmu` integration macros.
Control flow: memory unmap paths batch page-table freeing and TLB invalidations; architecture flush functions invalidate local or remote TLB entries according to range/mm scope.
State and persistence: TLB state lives in hardware and per-mm ASID/context data; this header defines how generic MM requests invalidation.
Dependencies and integration: integrates with `tlbflush.h`, page-table definitions, ASID allocation, exception refill assembly, huge pages, and SMP shootdown.
Risks and test signals: stale TLBs cause memory corruption/security bugs; over-flushing hurts performance. Signals include mmap/munmap stress, fork/exit, THP, KVM, ASID wrap, and SMP shootdown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/tlbflush.h

Purpose: declares LoongArch TLB flush interfaces used by MM, vmalloc, and SMP code.
Important APIs and types: exposes `local_flush_tlb_all`, `local_flush_tlb_mm`, `local_flush_tlb_range`, `local_flush_tlb_kernel_range`, `flush_tlb_*` wrappers, and page/hugepage flush helpers.
Control flow: local helpers perform CSR/TLB invalidations; SMP wrappers choose local versus remote invalidation depending on CPU masks and mm activity.
State and persistence: flushes mutate hardware TLB state and synchronize it with page-table changes.
Dependencies and integration: depends on `mmu_context`, CPU masks, page-table bits, and generic MM invalidation hooks.
Risks and test signals: missed flushes expose stale permissions or mappings. Signals include mprotect, munmap, fork/exec, vmalloc module mapping, THP split/collapse, and SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/topology.h

Purpose: exposes LoongArch CPU topology, NUMA, and cache/topology integration to generic scheduler code.
Important APIs and types: maps topology fields from `cpu_data`, defines node/cpu helpers, and includes generic topology fallbacks.
Control flow: ACPI PPTT or platform discovery populates `cpu_data` topology; scheduler and sysfs read the values through this header.
State and persistence: per-CPU core/package/node identifiers persist in CPU topology structures.
Dependencies and integration: integrates with ACPI topology parsing, NUMA setup, cacheinfo, scheduler domains, cpufreq, and sysfs topology files.
Risks and test signals: wrong topology degrades scheduling or misrepresents cache sharing. Signals include `/sys/devices/system/cpu` topology, scheduler domain dumps, NUMA boot, and cacheinfo validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/types.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/types.h

Purpose: provides architecture type selections and includes generic Linux type definitions for LoongArch.
Important APIs and types: defines LoongArch-specific DMA/physical address typedef availability through generic headers and architecture config.
Control flow: no runtime flow; compile-time type contract only.
State and persistence: type widths shape ABI and in-memory structures.
Dependencies and integration: consumed by kernel and UAPI headers that require exact integer and address widths.
Risks and test signals: type-width mistakes cause ABI or DMA address truncation. Signals are allmodconfig builds and sparse/compile checks across 32-bit and 64-bit variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/uaccess.h

Purpose: implements LoongArch user memory access primitives, address-limit checks, and exception-table guarded copy helpers.
Important APIs and types: provides `access_ok`, `__get_user`, `__put_user`, raw copy helpers, clear-user, `unsafe_get_user`, `unsafe_put_user`, and masked user access support around `__ua_limit` on 64-bit.
Control flow: accessors validate user ranges, emit inline load/store assembly with fixups, and return `-EFAULT` on exception. Bulk copy functions are delegated to architecture routines and generic wrappers.
State and persistence: no independent state, but it reads the process address limit and may zero or partially copy caller-provided buffers on faults.
Dependencies and integration: central to syscalls, signal frame copy, ptrace, filesystem/network I/O, BPF, and Spectre-v1 user pointer mitigation.
Risks and test signals: range-check or fixup errors are security critical. Signals include `lib/test_user_copy`, LKDTM usercopy, signal/ptrace tests, KASAN, and fault-injection around bad user pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unistd.h

Purpose: selects LoongArch syscall table metadata for kernel builds.
Important APIs and types: defines `__ARCH_WANT_*` feature macros and includes UAPI syscall numbers.
Control flow: syscall dispatch and table generation use these constants at build time; no runtime flow lives here.
State and persistence: syscall-number ABI is persistent user/kernel contract.
Dependencies and integration: integrates with `include/uapi/asm/unistd.h`, syscall table generation, audit/seccomp, and libc headers.
Risks and test signals: wrong selection breaks syscall availability. Signals include syscall ABI builds, `strace`, libc tests, and seccomp/audit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unwind.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unwind.h

Purpose: defines LoongArch unwinder state and interfaces for kernel stack walking.
Important APIs and types: declares `struct unwind_state`, `unwind_start`, `unwind_next_frame`, `unwind_get_return_address`, `unwind_done`, and default frame handling helpers.
Control flow: stacktrace and debugging code initialize state from task/regs, repeatedly call `unwind_next_frame`, and consume return addresses until `unwind_done`.
State and persistence: unwinder state is transient and tracks stack pointer, frame pointer, program counter, task, and reliability flags during a walk.
Dependencies and integration: used by `stacktrace.c`, `unwind_guess.c`, ftrace, livepatch, panic backtraces, and objtool/unwind hints.
Risks and test signals: invalid frame validation can read outside stacks or hide unreliable traces. Signals include stacktrace tests, panic backtraces, reliable-stack livepatch checks, and ftrace recursion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unwind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unwind_hints.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unwind_hints.h

Purpose: supplies assembly unwind hint macros for LoongArch entry and low-level code.
Important APIs and types: defines macros such as `UNWIND_HINT_UNDEFINED`, `UNWIND_HINT_REGS`, and `UNWIND_HINT_END_OF_STACK`, with objtool/CFI-aware behavior where configured.
Control flow: assembly code emits hints at entry, exception, idle, and return sites so unwinder tools can understand non-standard frames.
State and persistence: no runtime state, but emitted metadata persists in object/debug sections.
Dependencies and integration: used by `entry.S`, `head.S`, `genex.S`, FPU/idle assembly, objtool, stacktrace, and ORC/CFI-like validation flows.
Risks and test signals: bad hints produce unreliable stack traces or build-time validation failures. Signals include objtool warnings, stack unwinding through exceptions, and livepatch reliable-stack checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unwind_hints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/uprobes.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/uprobes.h

Purpose: declares LoongArch uprobes breakpoint instruction, XOL slot handling, and architecture-specific uprobe state.
Important APIs and types: defines `UPROBE_SWBP_INSN`, `UPROBE_SWBP_INSN_SIZE`, `struct arch_uprobe`, and helpers for return probes and single-step/breakpoint handling.
Control flow: uprobes patches user instructions with breakpoints, executes displaced instructions out of line, then redirects control back through arch handlers.
State and persistence: `arch_uprobe` stores copied instruction words and fixup metadata associated with a probed site.
Dependencies and integration: integrates with `kernel/uprobes.c`, LoongArch instruction decoder/generator, break exception handling, ptrace, and perf uprobes.
Risks and test signals: wrong instruction emulation or XOL return handling corrupts user execution. Signals include perf probe/uprobe tests, uprobes selftests, branch instruction probes, and signal interaction tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/uprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso.h

Purpose: declares LoongArch vDSO image and mapping interfaces.
Important APIs and types: exposes vDSO symbol/page data, `vdso_init`, `arch_setup_additional_pages`, and constants for mapping vvar/vdso pages into userspace.
Control flow: exec/mmap setup maps the vDSO into new processes; time/signal code references vDSO entry points and data pages.
State and persistence: vDSO image pages and per-mm mappings persist for process lifetime; vvar data is updated by timekeeping.
Dependencies and integration: integrates with ELF auxvec `AT_SYSINFO_EHDR`, signal return, gettimeofday vDSO, time namespaces, and mm mapping code.
Risks and test signals: mapping or symbol errors break libc fast paths. Signals include `vdso_test`, clock_gettime/gettimeofday tests, signal return, ASLR, and auxvec validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/arch_data.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/arch_data.h

Purpose: defines LoongArch architecture-specific data embedded in vDSO/vvar pages.
Important APIs and types: provides `struct arch_vdso_data` fields used by vDSO time routines, notably counter/timer configuration and clocksource mode data.
Control flow: kernel timekeeping updates vvar data; vDSO userspace routines read it without syscalls.
State and persistence: fields persist in read-only/shared vvar mappings visible to user processes.
Dependencies and integration: used by generic vDSO data structures, `gettimeofday.h`, timer/clocksource code, and libc clock fast paths.
Risks and test signals: ABI/layout changes break existing vDSO code. Signals include vDSO clock tests, compat with libc, and time namespace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/arch_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/clocksource.h

Purpose: selects LoongArch vDSO clocksource mode definitions.
Important APIs and types: includes generic vDSO clocksource definitions and maps architecture mode constants.
Control flow: no local runtime flow; vDSO time code switches behavior based on clocksource mode.
State and persistence: mode fields are stored in vDSO data and read from userspace.
Dependencies and integration: integrates with LoongArch counter reads, generic vDSO timekeeping, and clocksource registration.
Risks and test signals: wrong mode selection sends userspace down invalid time paths. Signals include vDSO clocksource tests and clocksource watchdog behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/getrandom.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/getrandom.h

Purpose: supplies LoongArch hooks for vDSO getrandom support.
Important APIs and types: defines architecture eligibility and includes generic vDSO getrandom support when configured.
Control flow: userspace vDSO getrandom uses shared random-state pages where supported, falling back to syscalls when unavailable.
State and persistence: random state lives in kernel-managed vvar/getrandom pages, not in this header.
Dependencies and integration: integrates with generic vDSO getrandom code, random subsystem, mm vDSO mapping, and libc wrappers.
Risks and test signals: ABI or feature mismatches can produce weak randomness or syscall fallback failures. Signals include getrandom selftests and vDSO mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/getrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/gettimeofday.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/gettimeofday.h

Purpose: implements LoongArch vDSO time read helpers for `clock_gettime`, `gettimeofday`, and related fast paths.
Important APIs and types: provides inline cycle reads from architecture counters, `__arch_get_hw_counter`, clocksource validation hooks, and namespace/time-data access helpers expected by generic vDSO code.
Control flow: userspace vDSO code reads stable vvar data, samples the hardware counter, computes nanoseconds, and falls back to syscalls on invalid modes or sequence changes.
State and persistence: reads vvar/vDSO data and hardware counters; no writable state in the header.
Dependencies and integration: depends on `timex.h`, vDSO data layout, clocksource mode definitions, and generic vDSO time algorithms.
Risks and test signals: counter ordering or width errors create time regressions in userspace. Signals include vDSO clock tests, time namespace tests, clocksource switching, and libc fast-path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/gettimeofday.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/processor.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/processor.h

Purpose: provides processor relaxation primitives for vDSO/user-visible spin loops.
Important APIs and types: defines `cpu_relax` or equivalent pause/barrier behavior for vDSO code.
Control flow: tight userspace loops call the inline helper to reduce contention while polling vvar sequence counters.
State and persistence: no state; it emits CPU hint instructions or compiler barriers.
Dependencies and integration: consumed by generic vDSO seqlock/time code.
Risks and test signals: missing barriers can cause bad polling behavior; unsupported instructions break old CPUs. Signals are vDSO build and time fast-path stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/vdso.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/vdso.h

Purpose: defines LoongArch vDSO architecture glue for generic vDSO headers.
Important APIs and types: provides vDSO page, symbol, and data access conventions used by architecture and generic code.
Control flow: build and runtime mapping code use these definitions to expose the vDSO image to processes.
State and persistence: describes persistent vDSO image/data placement but does not own mutable state.
Dependencies and integration: integrates with ELF aux vectors, `vdso.h`, time vDSO, signal return, and mm additional-page setup.
Risks and test signals: symbol/page alignment mistakes break userspace vDSO discovery. Signals include auxvec inspection, vDSO selftests, and libc clock/signal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/vsyscall.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/vsyscall.h

Purpose: provides kernel-side vDSO/vsyscall update hooks for LoongArch.
Important APIs and types: defines functions/macros used by timekeeping to update vDSO data, often mapping architecture-specific data into generic `vdso_data` accessors.
Control flow: timekeeping update paths call the helpers when clock data changes; userspace later observes the values in vvar pages.
State and persistence: updates persistent shared vDSO data structures.
Dependencies and integration: integrates with generic timekeeping, vDSO data, clocksource code, and namespace-aware vvar mappings.
Risks and test signals: stale or incorrectly updated data causes userspace time errors. Signals include vDSO time tests, clocksource changes, suspend/resume, and time namespace tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vermagic.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vermagic.h

Purpose: adds LoongArch-specific feature strings to module version magic.
Important APIs and types: defines `MODULE_PROC_FAMILY`, page-size/module ABI fragments, and final vermagic suffixes based on CPU/configuration.
Control flow: module build embeds these strings; module loader compares them when loading modules.
State and persistence: vermagic becomes persistent metadata in built kernel modules.
Dependencies and integration: integrates with module loader ABI checks, CPU family/page-size configuration, and kernel build system.
Risks and test signals: missing ABI-affecting flags can allow incompatible modules; excessive flags reject valid modules. Signals include module load tests across page-size/config variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/video.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/video.h

Purpose: provides LoongArch video/framebuffer memory helpers and platform defaults.
Important APIs and types: declares `screen_info` handling and architecture helpers for framebuffer physical/virtual mapping where needed.
Control flow: sysfb/simplefb/EFI BGRT and console drivers consult these helpers during early graphics setup.
State and persistence: framebuffer descriptors and primary display data persist after EFI/firmware discovery.
Dependencies and integration: integrates with EFI primary display parsing, sysfb, fbdev/simpledrm, and boot console code.
Risks and test signals: wrong memory attributes or addresses break early display. Signals include EFI framebuffer boot, simpledrm handoff, and console display tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vmalloc.h

Purpose: supplies LoongArch vmalloc hooks through generic definitions.
Important APIs and types: includes generic vmalloc behavior without additional architecture-specific helpers.
Control flow: runtime vmalloc behavior is implemented by generic MM and page-table code.
State and persistence: vmalloc mappings persist in kernel page tables; this file has no state.
Dependencies and integration: depends on `pgtable.h` address-space layout and generic vmalloc.
Risks and test signals: minimal local risk; signals include vmalloc stress, module loading, ioremap, and KASAN vmalloc coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/Kbuild

Purpose: controls which LoongArch UAPI asm headers are generated or exported to userspace.
Important APIs and types: lists generic-y/generated-y header mappings for the UAPI install step.
Control flow: Kbuild consumes this during `headers_install`; there is no runtime path.
State and persistence: installed header set becomes userspace ABI distribution state.
Dependencies and integration: integrates with kernel UAPI header installation, libc header generation, and syscall-number generation.
Risks and test signals: missing headers break userspace builds; exporting wrong generated headers causes ABI drift. Signals include `make headers_check` and libc/toolchain header builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/auxvec.h

Purpose: defines LoongArch ELF auxiliary-vector architecture entries.
Important APIs and types: defines `AT_SYSINFO_EHDR` for vDSO discovery and `AT_VECTOR_SIZE_ARCH` sizing.
Control flow: ELF loader populates auxvec for new processes; libc reads it to locate the vDSO.
State and persistence: auxvec entries are per-process ABI data visible to userspace.
Dependencies and integration: integrates with ELF exec, vDSO mapping, dynamic loaders, and libc clock/signal fast paths.
Risks and test signals: wrong constants break vDSO discovery. Signals include auxvec inspection, libc startup, and vDSO tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/bpf_perf_event.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/bpf_perf_event.h

Purpose: defines the register type BPF programs see for LoongArch perf events.
Important APIs and types: typedefs `bpf_user_pt_regs_t` to `struct user_pt_regs`.
Control flow: BPF helper/verifier paths use this type when exposing perf-event register context to programs.
State and persistence: no state; this is UAPI type binding.
Dependencies and integration: depends on UAPI `ptrace.h`, perf events, eBPF tracing, and libbpf-generated skeletons.
Risks and test signals: wrong context type breaks BPF programs reading registers. Signals include BPF selftests for kprobe/perf-event contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/bpf_perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/break.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/break.h

Purpose: defines LoongArch `break` instruction immediate values reserved for kernel/user debug semantics.
Important APIs and types: constants include `BRK_DEFAULT`, `BRK_BUG`, `BRK_KDB`, user breakpoint and single-step IDs, arithmetic trap IDs, kprobe, and uprobe break values.
Control flow: exception handlers decode break immediates and route to BUG, KGDB, kprobe, uprobe, debugger, or fault handling.
State and persistence: constants are part of userspace/debugger ABI for break instruction interpretation.
Dependencies and integration: used by KGDB, kprobes, uprobes, BUG handling, ptrace/debuggers, and instruction generation.
Risks and test signals: value collisions route traps to the wrong subsystem. Signals include kprobe/uprobe/KGDB tests, BUG traps, and debugger breakpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/break.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/byteorder.h

Purpose: declares LoongArch UAPI byte order.
Important APIs and types: includes little-endian byteorder definitions.
Control flow: compile-time only; userspace and kernel headers use it for endian conversions.
State and persistence: fixes ABI endian assumptions for structures shared with userspace.
Dependencies and integration: consumed by libc, kernel UAPI structures, networking/filesystem tools, and BPF headers.
Risks and test signals: wrong endian selection corrupts ABI interpretation. Signals include headers_check and userspace cross-builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/hwcap.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/hwcap.h

Purpose: defines LoongArch hardware capability bits advertised to userspace.
Important APIs and types: `HWCAP_LOONGARCH_*` bits cover CPUCFG, LAM, UAL, FPU, LSX, LASX, CRC32, complex/crypto instructions, LVZ, binary translation extensions, PTW, LSPW, SCQ, and LAM_BH.
Control flow: CPU probe sets matching bits in `elf_hwcap`; ELF exec exposes them through auxvec for libc and applications.
State and persistence: HWCAP bits are user ABI and must remain stable once assigned.
Dependencies and integration: tied to `cpu-probe.c`, ELF auxvec, libc feature detection, JITs, crypto libraries, and vector code dispatch.
Risks and test signals: advertising unsupported features causes illegal instructions; hiding features reduces performance. Signals include CPU feature probes, auxvec checks, vector/FPU tests, and userspace dispatch validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/hwcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/kvm.h

Purpose: defines the LoongArch userspace KVM ABI.
Important APIs and types: declares `struct kvm_regs`, `struct kvm_fpu`, KVM register ID ranges for GPR/CSR/KVM/FPSIMD/CPUCFG/LBT, VM and VCPU feature attributes, IRQ line support, coalesced MMIO/dirty-log offsets, and debug flags.
Control flow: QEMU/VMMs use ioctls with these structures and register IDs to create VMs, configure VCPU state, inject IRQs, and control features.
State and persistence: structure layout and register IDs are stable userspace ABI for VM state migration and tooling.
Dependencies and integration: integrates with arch KVM implementation, LoongArch CSR/CPUCFG definitions, userspace VMMs, and migration formats.
Risks and test signals: ABI changes break VMM compatibility or live migration. Signals include KVM selftests, QEMU boot, register get/set round trips, and VM migration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/kvm_para.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/kvm_para.h

Purpose: defines LoongArch KVM paravirtual CPUCFG leaves and feature bits.
Important APIs and types: provides `CPUCFG_KVM_BASE`, signature/feature leaves, `KVM_SIGNATURE`, and feature IDs for PV IPI, steal time, preempt, virtual EXTIOI, and user hypercalls.
Control flow: guests query CPUCFG leaves to discover KVM paravirtual features and enable optimized paths.
State and persistence: feature numbering is guest ABI.
Dependencies and integration: used by guest kernel paravirt code, KVM host emulation, and userspace VMM CPU model exposure.
Risks and test signals: mismatched feature IDs cause guest/host negotiation failures. Signals include KVM guest boot, paravirt IPI/steal-time tests, and CPUCFG ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/kvm_para.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/perf_regs.h

Purpose: enumerates LoongArch register IDs exposed in perf sample register masks.
Important APIs and types: defines `enum perf_event_loongarch_regs` for GPRs, original argument, PC, BADVADDR, and max register count.
Control flow: perf records selected register values in samples; userspace perf tooling decodes by these enum IDs.
State and persistence: enum ordering is perf UAPI.
Dependencies and integration: tied to `pt_regs`, perf callchain/sampling, BPF perf-event contexts, and tooling decoders.
Risks and test signals: enum drift breaks perf data interpretation. Signals include perf record/report with register sampling and BPF perf tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/ptrace.h

Purpose: defines LoongArch userspace ptrace register sets and watchpoint state.
Important APIs and types: includes `struct user_pt_regs`, `user_fp_state`, `user_lsx_state`, `user_lasx_state`, `user_lbt_state`, `user_watch_state`, `user_watch_state_v2`, register index constants, and `PTRACE_SYSEMU` requests.
Control flow: ptrace, core dump, signal tooling, debuggers, and BPF use these structures to inspect and modify task state.
State and persistence: structures are UAPI ABI and affect core files, debuggers, and checkpoint/restore.
Dependencies and integration: kernel ptrace code, KGDB/GDB register mapping, perf/BPF, hardware breakpoints, and signal contexts must stay consistent.
Risks and test signals: layout changes break debuggers and CRIU. Signals include ptrace selftests, GDB register access, hardware watchpoint tests, and core dump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/reg.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/reg.h

Purpose: defines numeric offsets for LoongArch ELF/core general register sets.
Important APIs and types: `LOONGARCH_EF_R0` through `LOONGARCH_EF_R31`, `LOONGARCH_EF_ORIG_A0`, CSR ERA/BADV/CRMD/PRMD/EUEN/ECFG/ESTAT indexes, and `LOONGARCH_EF_SIZE`.
Control flow: core dump, ptrace, and debugger code use indexes to map saved register arrays.
State and persistence: register numbering and size are ABI for ELF notes and tooling.
Dependencies and integration: tied to UAPI ptrace, GDB, perf, core dump generation, and signal/debug register conventions.
Risks and test signals: index drift corrupts debugger/core register display. Signals include core dump inspection, GDB, ptrace tests, and perf register sampling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/setup.h

Purpose: defines LoongArch userspace-visible setup constants.
Important APIs and types: sets `COMMAND_LINE_SIZE` to 4096.
Control flow: boot and tooling use this compile-time size for command-line buffers.
State and persistence: constant is ABI-adjacent for boot interfaces and tools.
Dependencies and integration: used by boot protocol, procfs command-line exposure, and userspace header consumers.
Risks and test signals: mismatched sizes truncate or overread command lines. Signals include boot with long command lines and headers_check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/sigcontext.h

Purpose: defines LoongArch signal context ABI, including optional extended contexts.
Important APIs and types: declares `struct sigcontext`, `struct sctx_info`, `fpu_context`, `lsx_context`, `lasx_context`, and `lbt_context`, plus magic numbers, alignment constants, and flags such as `SC_USED_FP` and address-error flags.
Control flow: signal delivery writes these records; `rt_sigreturn` parses magic/alignment-linked contexts and restores CPU/FPU/vector/LBT state.
State and persistence: user stack signal frames are ABI state visible to signal handlers, debuggers, and libcs.
Dependencies and integration: must match kernel signal code, FPU/LSX/LASX/LBT save/restore, UAPI `ucontext.h`, and ptrace register formats.
Risks and test signals: ABI drift breaks signal restore or vector-state preservation. Signals include signal selftests, sigaltstack, vector/LBT signal tests, and GDB signal handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/signal.h

Purpose: defines LoongArch signal stack sizing and imports generic signal ABI definitions.
Important APIs and types: sets `MINSIGSTKSZ` to 4096 and `SIGSTKSZ` to 16384 before including `asm-generic/signal.h`.
Control flow: userspace libraries use these constants for alternate signal stack sizing; kernel signal code enforces stack layout indirectly.
State and persistence: constants are userspace ABI expectations.
Dependencies and integration: tied to signal frame size, extended FPU/vector contexts, libc, and sigaltstack.
Risks and test signals: undersized values cause signal delivery failures with large contexts. Signals include sigaltstack tests with LSX/LASX/LBT state and libc header checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/ucontext.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/ucontext.h

Purpose: defines LoongArch `ucontext_t` ABI for signal handlers and user context APIs.
Important APIs and types: declares `struct ucontext` with flags, link pointer, stack, sigmask, sigcontext, and extension-space fields.
Control flow: signal delivery fills the structure; user handlers and `rt_sigreturn` consume it to inspect or restore context.
State and persistence: stored on user stacks as ABI-visible signal context state.
Dependencies and integration: aligns with `sigcontext.h`, signal frame setup, libc `ucontext_t`, and debugger expectations.
Risks and test signals: layout mismatch breaks signal handling and context switching libraries. Signals include signal ABI tests, `getcontext` consumers where present, and GDB signal unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/unistd.h

Purpose: selects generated LoongArch syscall-number headers for userspace.
Important APIs and types: includes `bitsperlong.h` and either 32-bit or 64-bit generated syscall numbers.
Control flow: compile-time inclusion by libc, seccomp tools, and kernel syscall tables.
State and persistence: syscall numbers are stable UAPI.
Dependencies and integration: generated from syscall tables and consumed by libc, audit, seccomp, strace, and kernel syscall dispatch.
Risks and test signals: wrong generated header selection breaks every syscall user. Signals include headers_install, libc builds, syscall smoke tests, and strace decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/Makefile

Purpose: defines the LoongArch architecture kernel object build graph.
Important APIs and types: selects core objects such as head, entry, traps, irq, process, setup, time, CPU probe, module, signal, ptrace, vdso, alternatives, ftrace, kprobes, uprobes, KVM/paravirt, suspend, EFI, ACPI, kexec, KGDB, and debug helpers according to config.
Control flow: Kbuild uses the object lists to compile/link the architecture kernel and optional feature objects.
State and persistence: no runtime state, but object inclusion determines which initcalls and handlers exist in the kernel image.
Dependencies and integration: integrates with architecture configuration symbols, linker scripts, vDSO builds, and generic kernel subsystems.
Risks and test signals: missing object entries cause link failures or runtime absent handlers. Signals include defconfig/allmodconfig builds across EFI/ACPI/SMP/KGDB/FTRACE/KEXEC/KVM options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/access-helper.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/access-helper.h

Purpose: provides small helpers for exception-safe instruction/address fetching from user or kernel context.
Important APIs and types: defines `__get_inst` and `__get_addr`, choosing `get_user` for user addresses and direct/kernel nofault access for kernel addresses.
Control flow: exception emulation code passes a user flag; helpers fetch the instruction or address and report fault status.
State and persistence: no persistent state; outputs are copied into caller variables.
Dependencies and integration: used by unaligned access and instruction emulation paths, depends on `linux/uaccess.h`.
Risks and test signals: wrong user/kernel selection can fault in atomic context or bypass access checks. Signals include unaligned access tests and fault injection with invalid user addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/access-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/acpi.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/acpi.c

Purpose: implements LoongArch ACPI boot-table parsing, CPU discovery, NUMA affinity, hotplug mapping, and architecture ACPI memory mapping.
Important APIs and types: defines `acpi_disabled`, `acpi_noirq`, `acpi_pci_disabled`, `acpi_strict`, `num_processors`, `disabled_cpus`, `acpi_core_pic`, `__acpi_map_table`, `acpi_os_ioremap`, MADT parsers, `parse_acpi_topology`, `acpi_boot_table_init`, SRAT affinity handlers, `arch_reserve_mem_area`, CPU hotplug map/unmap, and `acpi_get_cpu_uid`.
Control flow: early boot initializes ACPI tables, records boot CPU ID, parses MADT in two passes for enabled/disabled CPUs, parses EIO PIC masters, optionally parses SPCR/BGRT, and falls back to FDT earlycon if ACPI is disabled or table init fails. NUMA callbacks map proximity domains to CPU IDs; hotplug updates present masks and node mappings.
State and persistence: stores CPU presence/possible maps, physical/logical CPU maps, MADT core PIC entries, topology/core IDs, NUMA mappings, processor counts, and ACPI suspend low-level hook.
Dependencies and integration: depends on ACPI core, memblock/early ioremap, serial SPCR, EFI BGRT, irqdomain, Loongson sysconf, NUMA helpers, SMP CPU maps, and CPU hotplug.
Risks and test signals: BIOS table quirks directly affect CPU enumeration and topology. Signals include ACPI boot, FDT fallback, CPU hotplug, NUMA SRAT/PPTT validation, early console, BGRT/sysfb, and suspend builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/alternative.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/alternative.c

Purpose: applies LoongArch runtime instruction alternatives selected by CPU feature availability.
Important APIs and types: implements alternative patching over `alt_instr` records, feature matching, instruction copy/patch helpers, and init-time/application entry points.
Control flow: during boot/module setup, the code scans alternative sections, checks CPU feature bits, copies replacement instruction sequences when enabled, and flushes instruction caches after patching.
State and persistence: text modifications persist in kernel/module instruction memory for the life of the loaded image.
Dependencies and integration: integrates with `asm/alternative.h`, CPU feature probing, `inst.c` text patching, module loading, cache flush, stop_machine or patch locks, and SMP text synchronization.
Risks and test signals: bad length/range checks or cache flushing can execute stale or invalid instructions. Signals include boot on CPUs with/without features, module load with alternatives, ftrace/static key interaction, and objdump verification of patched sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/alternative.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/asm-offsets.c

Purpose: emits C-verified structure offsets for LoongArch assembly code.
Important APIs and types: uses `DEFINE`/`OFFSET` macros for `pt_regs`, `thread_info`, `thread_struct`, CPU boot data, FPU/vector state, sigcontext, and other low-level structures.
Control flow: built during kernel compilation to generate `asm-offsets.h`; no runtime code is linked.
State and persistence: generated constants persist in build artifacts and keep assembly synchronized with C layout.
Dependencies and integration: consumed by `entry.S`, `stackframe.h`, `switch.S`, `fpu.S`, signal code, suspend, and low-level boot paths.
Risks and test signals: missing offsets cause assembly to read/write wrong fields. Signals are build success and runtime tests for syscall entry, context switch, signal restore, FPU save/restore, and suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/cacheinfo.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/cacheinfo.c

Purpose: populates Linux cacheinfo structures from LoongArch CPU cache descriptors.
Important APIs and types: implements `init_cache_level`, `populate_cache_leaves`, `cache_cpumap_setup`, and cache-sharing comparison helpers.
Control flow: CPU/cache sysfs setup calls `init_cache_level`, then `populate_cache_leaves` fills each cache leaf from `cpu_data[cpu].cache_leaves`; sharing maps are built by comparing cache leaves across online CPUs.
State and persistence: per-CPU cacheinfo leaves and shared CPU masks persist for sysfs and scheduler/topology consumers.
Dependencies and integration: depends on `linux/cacheinfo.h`, topology, `cpu-info.h`, and boot-populated cache descriptors.
Risks and test signals: wrong shared maps mislead scheduler and userspace. Signals include `/sys/devices/system/cpu/cpu*/cache`, hotplug cacheinfo refresh, and topology tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/cacheinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/cpu-probe.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/cpu-probe.c

Purpose: probes LoongArch CPU capabilities, address sizes, TLB geometry, FPU masks, hardware watchpoint counts, and ELF hardware capabilities.
Important APIs and types: defines/export `elf_hwcap`, `vm_map_base`, `__ua_limit`, CPU name/family arrays, `cpu_probe`, `cpu_probe_common`, `cpu_probe_addrbits`, `cpu_probe_loongson`, SIMD boot parameter handling, and spectre mitigation reporting.
Control flow: boot/CPU bring-up reads CPUCFG and CSR registers, sets ISA/options/HWCAP bits, configures ASID masks, TLB sizes, timer bits, KSave masks, watchpoint availability, vendor/core names, address-space base, and user-access limit. An early `simd=` parameter can cap LSX/LASX exposure before final arch init.
State and persistence: populates `cpu_data`, `elf_hwcap`, CPU family/name strings, `vm_map_base`, `__elf_platform`, `__ua_limit`, and per-CPU feature masks.
Dependencies and integration: feeds ELF auxvec, `pgtable.h` layout, uaccess, TLB code, FPU/vector code, hardware breakpoints, Loongson IOCSR features, and sysfs vulnerability reporting.
Risks and test signals: over-advertised features cause illegal instructions; address-bit mistakes break kernel/user layout. Signals include boot logs, auxvec HWCAP checks, vector/FPU tests, TLB/page-table stress, and different CPUCFG configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/cpu-probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/crash_dump.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/crash_dump.c

Purpose: provides LoongArch crash dump memory copy support.
Important APIs and types: implements crash-dump copy helpers that map old memory and copy into kernel/user I/O vectors.
Control flow: kdump/vmcore code calls into this file to read physical memory from the crashed kernel using ioremap-style mappings and copy_to_iter semantics.
State and persistence: no long-lived local state; it reads crash memory and writes caller buffers.
Dependencies and integration: depends on `linux/crash_dump.h`, `io.h`, and `uio.h`; integrates with `/proc/vmcore` and kdump tooling.
Risks and test signals: address translation or copy faults break crash dump capture. Signals include kdump boot, vmcore read, makedumpfile, and sparse memory crash ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/crash_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/dma.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/dma.c

Purpose: supplies LoongArch DMA initialization and cache-coherency policy hooks.
Important APIs and types: implements architecture DMA setup/init hooks and coherent DMA decision helpers.
Control flow: device and platform initialization call DMA setup paths to configure masks/coherency and hand off to generic DMA mapping code.
State and persistence: device DMA attributes persist in device structures; no major local global state.
Dependencies and integration: integrates with OF/ACPI device enumeration, generic DMA mapping, cache maintenance, and IOMMU/SWIOTLB policy.
Risks and test signals: wrong coherency assumptions corrupt I/O buffers. Signals include storage/network DMA tests, IOMMU/SWIOTLB boot, and non-coherent device validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/efi-header.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/efi-header.S

Purpose: defines the PE/COFF EFI header emitted for EFI-stub bootable LoongArch kernels.
Important APIs and types: assembly macros lay out DOS, PE, optional header, section table, machine type, image base, subsystem, and relocation/header fields.
Control flow: included by `head.S` when `CONFIG_EFI_STUB` is enabled; firmware reads the header before jumping to the kernel entry.
State and persistence: header bytes persist in the kernel image and are part of the boot protocol.
Dependencies and integration: tied to EFI stub, linker symbols, image size symbols, and firmware loaders.
Risks and test signals: incorrect offsets or machine values prevent EFI boot. Signals include EFI boot on firmware, PE header inspection, secure boot tooling, and relocatable kernel tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/efi-header.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/efi.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/efi.c

Purpose: initializes LoongArch EFI runtime/table support and primary display information.
Important APIs and types: implements `efi_fdt_pointer`, `efi_runtime_init`, `efi_poweroff_required`, `efi_init`, `init_primary_display`, and exports `sysfb_primary_display`; tracks EFI config table addresses including boot memmap, FDT, and display table.
Control flow: early EFI init maps the system table, discovers config tables, initializes runtime services if available, parses primary display/sysfb information, and records FDT pointer for later boot flow.
State and persistence: stores EFI table addresses, runtime availability, and framebuffer/display metadata for sysfb/simpledrm.
Dependencies and integration: depends on EFI core, early ioremap, memblock, ACPI/BGRT/sysfb, Loongson platform data, reboot/poweroff, and uaccess for table copying.
Risks and test signals: bad table mapping or display parsing can break boot services handoff or framebuffer. Signals include EFI boot, runtime service calls, sysfb/simpledrm display, BGRT, and kexec EFI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/elf.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/elf.c

Purpose: provides LoongArch ELF core-dump and personality helpers.
Important APIs and types: implements architecture ELF register dumping or `arch_setup_additional_pages` adjacent hooks depending on configuration.
Control flow: ELF loader/core-dump code calls arch helpers to report register sets and architecture details.
State and persistence: affects core-file notes and ELF process metadata.
Dependencies and integration: integrates with `pt_regs`, UAPI reg/ptrace definitions, `elf_hwcap`, vDSO auxvec, and binfmt_elf.
Risks and test signals: wrong register notes break debuggers. Signals include core dump/GDB validation, ELF auxvec checks, and compat personality tests where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/elf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/entry.S

Purpose: implements LoongArch syscall entry and fork return assembly paths.
Important APIs and types: defines `handle_syscall`, `ret_from_fork_asm`, and `ret_from_kernel_thread_asm`, using `SAVE_STATIC`, `RESTORE_*`, `STACKLEAK_ERASE`, and unwind hints.
Control flow: `handle_syscall` switches from user to kernel stack using per-CPU saved stack, saves user registers and CSRs into `pt_regs`, enables KGDB watch handling if configured, sets thread pointer state, calls `do_syscall`, erases stack-leak region, and restores state back to user. Fork return paths call C helpers and restore saved frames.
State and persistence: builds transient syscall `pt_regs` on the kernel stack and updates saved return state.
Dependencies and integration: depends on `stackframe.h`, `thread_info.h`, `asm-offsets.h`, `ptrace.h`, `do_syscall`, stackleak, KGDB, and scheduler fork code.
Risks and test signals: register save/restore mistakes break all syscalls and fork. Signals include syscall ABI tests, fork/clone, strace/seccomp, signal restart, and stack unwinding through syscall frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/env.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/env.c

Purpose: parses LoongArch firmware environment and boot arguments into kernel setup state.
Important APIs and types: handles firmware argument variables, boot command line extraction, initrd/memmap/environment parsing, and Loongson boot parameter structures.
Control flow: early setup code reads `fw_arg*` values saved by `head.S`, identifies boot protocol style, copies command-line data, and discovers memory/initrd/platform descriptors.
State and persistence: populates global command line, firmware environment pointers, initrd bounds, and Loongson system configuration used later by ACPI/FDT and memory setup.
Dependencies and integration: integrates with `setup.h`, `bootinfo.h`, memblock, EFI/FDT fallback, Loongson platform config, and early printk/console paths.
Risks and test signals: malformed firmware data can corrupt early memory setup or lose command-line options. Signals include boot across firmware revisions, initrd boot, long command lines, and FDT/EFI fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/env.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/fpu.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/fpu.S

Purpose: implements low-level save, restore, initialize, and signal-copy routines for LoongArch FPU, LSX, and LASX register state.
Important APIs and types: exports `_save_fp`, `_save_lsx`, `_save_lasx`, `_restore_lsx_upper`, `_restore_lasx_upper`, and defines `_restore_fp`, `_restore_lsx`, `_restore_lasx`, `_init_fpu`, `_init_lsx_upper`, `_init_lasx_upper`, plus exception-table guarded `sc_save_*`/`sc_restore_*` macros for signal contexts.
Control flow: context switch, signal, ptrace, and debug paths call assembly routines to move FPU/vector registers to/from `thread_struct` or user signal context buffers. Exception table entries route faulting user-context loads/stores to a common fault return.
State and persistence: persists floating-point control/status, FCC flags, 32 FPRs, LSX 128-bit vector state, and LASX 256-bit vector state in task structures and signal frames.
Dependencies and integration: depends on asm offsets, FPU/vector register definitions, exception tables, signal context layout, lazy FPU enable, and CPU feature config.
Risks and test signals: offset/register-order mistakes leak or corrupt FPU/vector state. Signals include FPU math tests, LSX/LASX context-switch stress, signal save/restore, ptrace register access, and fault injection on signal frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/fpu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/ftrace.c

Purpose: provides LoongArch ftrace call-site support for function tracing.
Important APIs and types: implements architecture ftrace preparation, return address adjustment, and callsite validation hooks used by generic ftrace.
Control flow: ftrace core consults arch hooks when enabling tracing and when interpreting callsites/return addresses.
State and persistence: tracing state is maintained by ftrace core; this file supplies architecture glue.
Dependencies and integration: integrates with `inst.c` instruction generation/patching, module sections, dynamic ftrace, function graph tracing, and unwind metadata.
Risks and test signals: bad callsite interpretation can patch wrong text. Signals include ftrace selftests, function graph tracing, module tracing, and live ftrace enable/disable stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/ftrace_dyn.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/ftrace_dyn.c

Purpose: implements dynamic ftrace text patching for LoongArch.
Important APIs and types: provides `ftrace_make_call`, `ftrace_make_nop`, `ftrace_update_ftrace_func`, and helpers to generate branch/NOP sequences and validate patched instructions.
Control flow: ftrace core asks the arch code to replace callsite instructions with calls to ftrace trampoline or NOPs; patching uses LoongArch instruction helpers and cache flushes.
State and persistence: modifies kernel/module text while tracing is enabled or disabled.
Dependencies and integration: depends on `inst.c`, ftrace core, module relocation sections, stop_machine/text patching, and instruction cache coherency.
Risks and test signals: branch range or patch atomicity failures can crash executing CPUs. Signals include dynamic ftrace selftests, module ftrace, graph tracer, concurrent enable/disable, and objdump checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/ftrace_dyn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/genex.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/genex.S

Purpose: defines general LoongArch exception vectors and exception handler stubs.
Important APIs and types: implements `__arch_cpu_idle`, `handle_vint`, `except_vec_cex`, `handle_ade`, `handle_ale`, `handle_bce`, `handle_bp`, `handle_fpe`, `handle_fpu`, `handle_lsx`, `handle_lasx`, `handle_lbt`, `handle_ri`, `handle_watch`, `handle_reserved`, and `handle_sys`.
Control flow: vector stubs save state with `SAVE_ALL`, prepare BADV/FCSR arguments when needed, call C `do_*` handlers, then restore all registers. `handle_vint` handles the idle interrupt window specially so an interrupt between enabling IRQs and `idle` does not re-enter idle.
State and persistence: creates transient `pt_regs` frames and emits unwind hint metadata for exception frames.
Dependencies and integration: depends on `stackframe.h`, `thread_info.h`, CSR definitions, C trap handlers, idle code, KGDB/kprobe break handling, and interrupt dispatch.
Risks and test signals: wrong save/restore or idle-window handling causes interrupt loss or register corruption. Signals include interrupt storm tests, exception/fault tests, idle/reschedule behavior, KGDB/kprobe/uprobe breakpoints, and unwinder validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/genex.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/head.S

Purpose: contains the LoongArch kernel entry point and secondary CPU boot entry.
Important APIs and types: defines EFI header embedding under `CONFIG_EFI_STUB`, `kernel_entry`, image size symbols, and `smpboot_entry`.
Control flow: primary entry sets up translation/direct-map windows, switches to virtual addressing, clears BSS, saves firmware arguments, initializes percpu base and boot stack, optionally relocates/KASLR-adjusts the kernel, runs early KASAN, and calls `start_kernel`. Secondary entry performs minimal MMU/window setup, loads stack/thread info from `cpuboot_data`, and calls `start_secondary`.
State and persistence: initializes global BSS, firmware argument globals, initial stack pointer, saved SP, percpu base, and relocation-adjusted execution state.
Dependencies and integration: tied to linker symbols, EFI header, relocation code, KASAN early init, SMP boot data, `stackframe.h`, and platform firmware ABI.
Risks and test signals: early entry bugs prevent boot. Signals include EFI/non-EFI boot, relocatable/KASLR builds, SMP secondary bring-up, 4K page-size IMPCTL handling, and KASAN boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/hw_breakpoint.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/hw_breakpoint.c

Purpose: implements LoongArch hardware breakpoint/watchpoint support for perf, ptrace, and KGDB.
Important APIs and types: defines per-CPU breakpoint/watchpoint slot arrays, `hw_breakpoint_slots`, CSR read/write switch helpers, `arch_install_hw_breakpoint`, `arch_uninstall_hw_breakpoint`, `arch_check_bp_in_kernelspace`, `arch_bp_generic_fields`, `hw_breakpoint_arch_parse`, `breakpoint_handler`, `watchpoint_handler`, `hw_breakpoint_thread_switch`, and `flush_ptrace_hw_breakpoint`.
Control flow: perf events are parsed into arch breakpoint descriptors, assigned to per-CPU slots, written to FWP/MWP CSR register groups, and enabled via CRMD/PRMD bits. Exception handlers scan pending status bits, emit `perf_bp_event`, clear status, and disable or restore breakpoint registers around traps/thread switches.
State and persistence: per-CPU slot arrays track installed perf events; thread fields track ptrace break/watch events; hardware CSR watch registers hold address/mask/control/ASID state.
Dependencies and integration: depends on `asm/hw_breakpoint.h`, perf/hw_breakpoint core, ptrace thread state, kprobes `NOKPROBE`, CPU probe watch counts, CSR helpers, and KGDB hardware breakpoint callbacks.
Risks and test signals: slot accounting, privilege bits, and single-step interactions are fragile. Signals include perf hardware breakpoint tests, ptrace watchpoints, KGDB hardware breakpoints, CPU hotplug, and kprobe recursion safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/hw_breakpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/idle.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/idle.c

Purpose: exposes the LoongArch CPU idle routine to generic idle code.
Important APIs and types: calls the assembly `__arch_cpu_idle` implementation through architecture idle hooks.
Control flow: scheduler idle loop invokes the arch idle function; assembly enables interrupts and executes the LoongArch idle instruction with a protected interrupt window.
State and persistence: no long-lived state; CPU enters and leaves low-power idle state.
Dependencies and integration: integrates with `genex.S` idle interrupt handling, scheduler idle loop, IRQ state, and CPU power management.
Risks and test signals: incorrect interrupt enable ordering can miss reschedules. Signals include idle/reschedule stress, timer interrupts, cpuidle tracing, and suspend-adjacent tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/image-vars.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/image-vars.h

Purpose: maps kernel image symbols for the EFI stub and compressed/relocatable image interfaces.
Important APIs and types: declares symbol aliases for image size, file size, and entry/load addresses used by EFI or relocation code.
Control flow: included by low-level image/header code at build time; no runtime logic.
State and persistence: symbols become part of linked image metadata.
Dependencies and integration: tied to linker script symbols, `head.S`, EFI stub, and boot loaders.
Risks and test signals: wrong symbol exposure breaks boot image headers. Signals include EFI boot, objdump/readelf image checks, and relocatable boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/image-vars.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/inst.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/inst.c

Purpose: implements LoongArch instruction simulation, safe text patching, and instruction generation helpers.
Important APIs and types: provides `simu_pc`, `simu_branch`, `insns_not_supported`, `insns_need_simulation`, `arch_simulate_insn`, `larch_insn_read`, `larch_insn_write`, `larch_insn_patch_text`, `larch_insn_text_copy`, and generators for NOP, branch, break, OR/move, LU12I/LU32I/LU52I, BEQ/BNE, and JIRL.
Control flow: emulation updates `pt_regs` PC/registers for PC-relative and branch instructions; patching validates alignment, writes with nofault copies under a raw spinlock, flushes icache, or uses `stop_machine_cpuslocked` after temporarily making pages writable and restoring ROX permissions.
State and persistence: text patching persistently modifies kernel/module code; simulation mutates transient exception register frames.
Dependencies and integration: used by kprobes/uprobes, ftrace, alternatives, jump labels, KGDB single-step, module patching, cache flush, and memory permission changes.
Risks and test signals: branch range errors, stale icache, or RWX restoration failures can crash the kernel. Signals include ftrace/kprobe/uprobe/jump-label selftests, module patching, strict RWX checks, and instruction emulator tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/inst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/irq.c

Purpose: implements LoongArch interrupt initialization and interrupt dispatch glue.
Important APIs and types: provides IRQ initialization, `do_vint`, `arch_show_interrupts`, `init_IRQ`, and architecture interrupt accounting hooks.
Control flow: exception vector `handle_vint` calls `do_vint` with `pt_regs`; the C path decodes pending interrupt state, dispatches to irqdomains/chained handlers, and returns through common restore code.
State and persistence: interrupt controller mappings, per-CPU interrupt state, and IRQ statistics persist in generic IRQ structures.
Dependencies and integration: integrates with ACPI/FDT irqchip discovery, Loongson interrupt controllers, generic IRQ core, SMP IPIs, and `/proc/interrupts` reporting.
Risks and test signals: wrong vector dispatch loses interrupts or loops. Signals include timer/IPI/device interrupt tests, `/proc/interrupts`, irqdomain validation, and SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/jump_label.c

Purpose: implements LoongArch static key/jump label text patching.
Important APIs and types: provides `arch_jump_label_transform` and instruction selection for NOP versus branch forms.
Control flow: jump-label core requests transformations when static keys toggle; the arch code generates a branch or NOP and patches kernel text.
State and persistence: modifies text at static branch sites until toggled again.
Dependencies and integration: depends on `inst.c`, static key core, text patching, icache flush, and branch reach limits.
Risks and test signals: wrong patch target or range causes bad control flow. Signals include jump_label selftests, tracepoints/static keys, module static keys, and concurrent toggling stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kdebugfs.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/kdebugfs.c

Purpose: exposes LoongArch kernel debug information through debugfs.
Important APIs and types: creates debugfs files for architecture state such as CPU registers/features, page tables, or platform data depending on config.
Control flow: initcall creates debugfs entries and read callbacks format current architecture state for userspace inspection.
State and persistence: debugfs dentries persist while mounted; output reflects live kernel state.
Dependencies and integration: integrates with debugfs, CPU feature data, memory/debug helpers, and architecture diagnostics.
Risks and test signals: debugfs callbacks must avoid unsafe access and respect config availability. Signals include debugfs mount/read tests and lockdep while reading entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kdebugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kexec_efi.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/kexec_efi.c

Purpose: prepares EFI-specific metadata for kexec on LoongArch.
Important APIs and types: implements helpers to pass EFI system table, memory map, and boot parameters to a kexec target kernel.
Control flow: kexec file load/build code invokes EFI helpers to construct the target boot parameter block and preserve runtime information.
State and persistence: generated handoff metadata persists until the new kernel boots.
Dependencies and integration: depends on EFI table parsing, kexec image loading, memblock/memory map data, and LoongArch boot protocol.
Risks and test signals: incomplete EFI handoff breaks second-kernel EFI/runtime behavior. Signals include kexec boot from EFI, kdump under EFI, and runtime service checks after kexec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kexec_efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kexec_elf.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/kexec_elf.c

Purpose: handles ELF image loading details for LoongArch kexec.
Important APIs and types: implements architecture ELF kexec probe/load helpers, segment placement, and entry/boot argument preparation.
Control flow: kexec file loader validates the ELF image, maps/load segments, prepares control data, and records the target entry point.
State and persistence: kexec image metadata and loaded segments persist until reboot into the new kernel.
Dependencies and integration: integrates with generic kexec_file, ELF parser, crash kernel, EFI handoff, and low-level relocation/reboot code.
Risks and test signals: segment placement or entry mistakes fail kexec or crash kernels. Signals include normal kexec, kdump, signed image loading where enabled, and memory-range validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kexec_elf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kfpu.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/kfpu.c

Purpose: provides kernel-mode FPU/vector usage helpers for LoongArch.
Important APIs and types: implements save/restore wrappers that allow kernel code to borrow FPU/LSX/LASX state safely, along with begin/end style APIs.
Control flow: callers disable preemption or otherwise guard ownership, save current task FPU state if needed, enable FPU/vector units, perform work, then restore previous state and permissions.
State and persistence: temporarily stores task FPU/vector state and updates ownership/lazy flags.
Dependencies and integration: depends on low-level `fpu.S` routines, CPU feature bits, scheduler/preemption, and crypto/math code that uses kernel FPU.
Risks and test signals: incorrect nesting or preemption handling corrupts userspace FPU state. Signals include crypto selftests using vector code, preemption stress, FPU signal tests, and KCSAN/lockdep around kernel FPU regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kfpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kgdb.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/kgdb.c

Purpose: implements LoongArch KGDB register access, breakpoints, single-step emulation, exception notification, and hardware breakpoint integration.
Important APIs and types: defines `dbg_reg_def`, `dbg_get_reg`, `dbg_set_reg`, `sleeping_thread_to_gdb_regs`, `kgdb_arch_set_pc`, `arch_kgdb_breakpoint`, `kgdb_breakpoint_handler`, `kgdb_arch_handle_exception`, `arch_kgdb_ops`, `kgdb_arch_init`, `kgdb_arch_late`, and `kgdb_arch_exit`; maintains `kgdb_watch_activated`, `stepped_opcode`, `stepped_address`, and `breakinfo[]`.
Control flow: die notifications route kernel traps into KGDB; remote commands update PC, continue, detach, kill, or single-step. Single-step computes the next PC for LoongArch branch forms, plants a temporary break instruction, flushes icache, and restores the original opcode after the trap. Hardware breakpoint commands reserve wide perf breakpoints per CPU, install/uninstall arch breakpoints, and disable/correct them while KGDB owns control.
State and persistence: KGDB stores temporary patched instruction state, per-slot hardware breakpoint attributes/per-CPU perf events, and debugger-visible register mappings. It saves/restores current task FPU state when accessing FP registers.
Dependencies and integration: depends on KGDB core, die notifiers, perf hardware breakpoints, LoongArch instruction decoder, FPU helpers, cache flush, SMP, ptrace/register ABI, and break immediate `BRK_KDB`.
Risks and test signals: single-step branch decoding and text patch restoration are high risk; hardware breakpoints share scarce resources with perf/ptrace. Signals include KGDB over serial, software and hardware breakpoints, single-step over branches, FPU register read/write in GDB, SMP KGDB callbacks, and detach/continue paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kgdb.c -->
