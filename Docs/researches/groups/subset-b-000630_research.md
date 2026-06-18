# subset-b-000630 ARC source research

Grouped research report for the exact subset-b-000630 source manifest. Each section preserves the source path in its title and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/pgtable-bits-arcv2.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/pgtable-bits-arcv2.h

ARC page-table bit definitions for software-walked ARC MMUv3/MMUv4 page tables. It maps Linux PTE protection state onto hardware TLB bits such as present, global, cacheable, read, write, execute, accessed, dirty, special, and optional MMUv4 huge-page size. Key APIs are PAGE_U_* protections, PAGE_KERNEL, pgprot_noncached(), pte_write/dirty/young/special(), the PTE_BIT_FUNC-generated mutators, pte_modify(), update_mmu_cache_range(), and swap PTE encode/decode helpers. Control flow is macro-driven by generic MM callers: faults and mprotect update PTEs, then update_mmu_cache_range() pushes them into the software-managed TLB. State persists in PTE values and swap entries; bit 5 is reused as _PAGE_SWP_EXCLUSIVE when the PTE is non-present. Dependencies are linux mm types, asm page/pgprot conventions, transparent hugepage support, and ARC cache/MMU Kconfig. Risks include bit collisions between hardware, software, and swap encodings, missing cacheability for DMA/I/O mappings, and incorrect write/execute implied-read policy. Test signals are page-fault, mprotect, swap, COW, THP, and noncached mmap coverage.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/pgtable-bits-arcv2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/pgtable-levels.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/pgtable-levels.h

Paging-level geometry and folded-level helpers for ARC. It chooses PGDIR/PUD/PMD shifts from CONFIG_PGTABLE_LEVELS, page size, and ARC huge-page options, then defines entry counts, masks, p4d/pud/pmd/pte predicates, setters, pfn conversions, and leaf detection for ARCv2 huge mappings. Control flow is compile-time: generic mm uses folded asm-generic pgtable-nop* headers, while ARC supplies the actual pte/pmd semantics. State is stored as physical page-table addresses plus flag bits in pgd/pud/pmd/pte words; no runtime persistence is owned here. Dependencies include PAGE_SHIFT, PAGE_MASK, virt_to_page(), pfn_to_page(), and _PAGE_HW_SZ from pgtable-bits. Risks are geometry mismatches that can corrupt page-table walks, duplicate pmd_pfn definitions across conditional blocks, and CONFIG_PGTABLE_LEVELS combinations whose folded macros do not match generic expectations. Test signals include boot with 2/3/4 level configs, huge-page mappings, vmalloc/module mappings, and page-table debug warnings via *_ERROR().

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/pgtable-levels.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/pgtable.h

Top-level ARC pgtable include that assembles pgtable-levels, pgtable-bits-arcv2, page, and MMU definitions. It exposes USER_PTRS_PER_PGD, swapper_pg_dir, and HAVE_ARCH_UNMAPPED_AREA for VIPT cache alias-aware mmap placement. Control flow is indirect: generic mm includes this header to obtain the architecture page-table contract and later calls lower-level PTE/TLB helpers declared by the included headers. State consists of the kernel page directory symbol and user virtual-address partitioning via TASK_SIZE and PGDIR_SIZE. Dependencies are processor.h for TASK_SIZE via page/MMU users, ARC software TLB code, and generic mm. Risks are mostly integration risks: wrong USER_PTRS_PER_PGD or unmapped-area policy can cause user/kernel address overlap or cache aliasing. Test signals are boot page-table initialization, mmap layout tests, highmem/vmalloc/module allocations, and alias-sensitive shared mappings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/processor.h

Processor and task-layout definitions for ARC. It defines struct thread_struct with callee register save pointer, fault/breakpoint address, optional DSP and FPU state, task_pt_regs(), stack/register inspection macros, cpu_relax(), start_thread(), __get_wchan(), and the ARC virtual memory layout constants. Control flow integrates with fork/exec/context-switch: process.c fills thread_struct and pt_regs, ctx_sw_asm.S consumes thread_info.ksp, and stack walkers use KSTK/TSK_K_* helpers. State persists per task in thread_struct, thread_info, and the task kernel stack. Dependencies are ptrace, DSP/FPU headers, scheduler task stacks, and CONFIG_ARC_KVADDR_SIZE. Risks include stale assumptions about kernel stack layout, incorrect VMALLOC_START/END sizing, and fault_address overloading for breakpoints. Test signals include fork/exec, kernel threads, stack unwinding, /proc stack views, vmalloc stress, and architecture ptrace regressions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/ptrace.h

Kernel-internal ARC register frame contract. It defines endian-aware ecr_reg and ISA-specific pt_regs layouts for ARCompact and ARCv2, callee_regs, register access helpers, user/kernel mode predicates, syscall/breakpoint tests, restart-state bits, current_pt_regs(), and register-query prototypes. Control flow starts in entry assembly, which saves hardware state into pt_regs; C handlers then inspect ecr/status32/ret/r0-r8 for exceptions, syscalls, signals, ptrace, kprobes, and KGDB. State is transient on the kernel stack, with callee_regs sometimes saved separately and referenced from thread_struct. Dependencies include UAPI ptrace ABI, thread_info stack alignment, status bit definitions, and entry macro offsets. Risks are ABI drift between assembly offsets and C struct layout, endian bitfield mistakes, and incorrect syscall restart bookkeeping. Test signals are syscall tracing, signal delivery, ptrace GETREGSET/SETREGSET, breakpoints, delay-slot exceptions, and kgdb/kprobe register reads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/sections.h

Small section-symbol extension for ARC. It includes asm-generic/sections.h and declares __arc_dccm_base for tightly coupled data memory placement checks. Control flow is compile/link-time: linker scripts define the symbol, setup.c compares it with hardware DCCM build registers during processor setup. State is not mutated here; the symbol represents a linked address. Dependencies are linker-provided sections and CONFIG_ARC_HAS_DCCM sanity checks. Risks are link-script drift or board configuration changes that make the symbol disagree with hardware, which intentionally panics during boot. Test signals include boot on DCCM-enabled and DCCM-disabled configurations and linker map validation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/serial.h

ARC serial early-console support hook. It declares arc_early_base_baud() and defines BASE_BAUD through that helper so 8250/earlycon code can obtain a runtime baud base from early device-tree compatibility rather than a fixed compile-time number. Control flow is devtree.c setting the early baud from the flat DT before serial earlycon consumers query BASE_BAUD. State is the __initdata arc_base_baud value maintained in devtree.c. Dependencies include CONFIG_SERIAL_EARLYCON, DT compatible strings for TB10x/SDP/HSDK/default boards, and 8250 early console expectations. Risks are wrong compatible matching leading to unusable early console or misleading boot diagnostics. Test signals are earlycon boot logs across supported boards and absence of BASE_BAUD compile failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/setup.h

Setup-time declarations and formatting helpers for ARC boot reporting. It exposes COMMAND_LINE_SIZE, id_to_str, root_mountflags/end_mem, setup_processor(), setup_arch_memory(), arc_get_mem_sz(), MMU/cache initialization and reporting hooks, and handle_uboot_args(). Control flow is setup_arch() calling handle_uboot_args(), platform hooks, smp_init_cpus(), setup_processor(), and memory setup. State is global boot configuration: command line, mount flags, machine description, CPU/cache/MMU hardware features, and U-Boot ABI data. Dependencies include UAPI setup.h, Linux init/types, cache/MMU implementations, and setup.c. Risks include command-line truncation, mismatched hardware reporting macros, and missing strict option checks. Test signals include boot logs, /proc/cpuinfo, U-Boot cmdline/DTB handoff, and cache/MMU init on multiple ARC variants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/shmparam.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/shmparam.h

Shared-memory alignment policy for ARC. It sets SHMLBA to 2 * PAGE_SIZE and forces shmat() to honor it, accommodating up to two VIPT cache alias bins. Control flow is generic SysV shared-memory attach logic consulting SHMLBA and __ARCH_FORCE_SHMLBA before mapping. State is purely ABI/configuration; no runtime data is stored. Dependencies are PAGE_SIZE and cache alias behavior. Risks are either too-small alignment causing D-cache aliases for shared mappings or unnecessarily large alignment reducing attach address flexibility. Test signals include SysV shm attach tests, alias-sensitive shared memory workloads, and page-size variants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/smp.h

ARC SMP interface between generic Linux, architecture code, and platform/MCIP drivers. It defines raw_smp_processor_id(), IPI send prototypes, boot hooks, plat_smp_ops, smp_ipi_irq_setup(), and fallback atomic_ops_lock/unlock for cores lacking LLOCK/SCOND. Control flow runs from setup_arch() to smp_init_cpus(), then platform callbacks initialize early SMP hardware, per-CPU IPI IRQs, CPU kick, and IPI clear/send. State includes current_thread_info()->cpu, plat_smp_ops, and optional smp_atomic_ops_lock. Dependencies are CONFIG_SMP, irq hwirq types, spinlock backend, irqflags, and mcip/smp.c implementations. Risks include cyclic-header constraints, broken platform callbacks, and atomic fallback locking that must preserve IRQ state. Test signals are CPU bring-up, smp_call_function, reschedule IPIs, atomic operations on non-LLSC cores, and UP build stubs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/spinlock.h

ARC raw spinlock and rwlock implementation. With CONFIG_ARC_HAS_LLSC it uses llock/scond loops plus full barriers; without LLSC it uses EX-based spinlocks and a nested spinlock/IRQ-disabled scheme for rwlocks. Important APIs are arch_spin_lock/trylock/unlock and arch_read/write_lock/trylock/unlock. Control flow is busy-wait acquisition, atomic exchange/conditional store, and barrier-enforced acquire/release ordering. State persists in arch_spinlock_t.slock and arch_rwlock_t.counter, with optional lock_mutex for non-LLSC rwlocks. Dependencies are barrier semantics, cpu_relax(), local_irq_save/restore, and spinlock_types.h. Risks include writer starvation in rwlocks, missing barriers, EX hardware quirks, and IRQ-state bugs in non-LLSC fallback. Test signals include lockdep, SMP stress, rwlock fairness tests, interrupt-context locking, and atomic fallback users.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/spinlock_types.h

Type and initializer definitions for ARC raw locks. arch_spinlock_t is a volatile integer with unlocked 0 and locked 1. arch_rwlock_t stores a reader counter initialized to 0x01000000 and optionally embeds a mutex spinlock on non-LLSC systems. Control flow is owned by spinlock.h; this file defines the state shape consumed by generic locking. Dependencies are CONFIG_ARC_HAS_LLSC and Linux raw lock initializer conventions. Risks are changing counter constants without updating lock algorithms or static initializers, and volatile assumptions interacting with memory barriers. Test signals are compile coverage for LLSC/non-LLSC/SMP/UP builds and runtime lock stress.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/stacktrace.h

Public stack-unwind entry point for ARC kernel contexts. It declares arc_unwind_core(), which unwinds current, sleeping-task, or interrupt/exception stacks and invokes a callback per frame. Control flow is caller-driven: dump_stack, perf callchains, and debug paths seed it with task/pt_regs or current register values. State is read from task stacks, pt_regs, and frame/unwind metadata; no persistent state is declared here. Dependencies include sched/task state and the implementation in stacktrace/unwind code. Risks include asynchronous unwinding racing with task stack changes, bad pt_regs seeds, and callback misuse. Test signals include dump_stack, perf_callchain_kernel(), sleeping task backtraces, IRQ exception traces, and frame-pointer/DWARF configuration variants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/string.h

Declares ARC-optimized string and memory primitives and advertises them through __HAVE_ARCH_* macros. APIs are memset, memcpy, memzero, memcmp, strchr, strcpy, strcmp, and strlen with __kernel_size_t lengths. Control flow is generic C library/kernel callers resolving to architecture implementations and arcksyms.c exporting them to modules. State is only caller buffers. Dependencies are linux/types and assembly/string implementations elsewhere in the architecture tree. Risks are ABI or overlap semantics mismatches versus generic routines, especially for memcpy/memset used in early boot and modules. Test signals include lib/string tests, boot memory initialization, module loading using exported symbols, and compiler built-in substitution checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/switch_to.h

Task switch wrapper for ARC. It declares __switch_to(prev,next) and defines switch_to() to save/restore optional DSP and FPU state before calling the assembly context switch, then applies a memory barrier. Control flow is scheduler -> switch_to -> dsp_save_restore/fpu_save_restore -> ctx_sw_asm.S __switch_to -> return last task. State transitions include thread.fpu, thread.dsp, thread_info.ksp, and callee-saved kernel registers. Dependencies are sched.h, dsp-impl.h, fpu.h, and ctx_sw_asm.S. Risks are ordering bugs between accelerator state and core register switch, missing barrier effects visible to the scheduler, and config-specific save/restore gaps. Test signals are context-switch stress with FPU/DSP workloads, scheduler tests, SMP migration, and kernel-thread switching.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/syscall.h

Generic syscall tracing/audit helpers for ARC. It exposes sys_call_table and inline helpers for syscall number, rollback, errors, return values, arguments, and audit architecture. Control flow is ptrace/audit/seccomp/trace code using pt_regs: r8 holds the syscall number, r0-r5 are read by walking backward from r0, and orig_r0 supports rollback/restart. State lives in pt_regs during syscall entry/exit. Dependencies are asm/unistd.h, ptrace.h in_syscall(), Linux audit constants, and entry.S trap handling. Risks include argument order assumptions tied to pt_regs layout, returning -1 for non-syscall contexts, and arch ID mismatches for endian/ISA. Test signals are strace, syscall tracepoints, audit records, syscall argument mutation, and restart rollback tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/syscalls.h

ARC-specific syscall prototype header. It declares wrappers for clone/clone3, cacheflush, TLS set/get, and user cmpxchg, then includes asm-generic/syscalls.h. Control flow connects entry.S syscall table dispatch to process.c implementations and assembly wrappers that preserve callee registers around clone. State touched by these calls includes thread_info.thr_ptr, user cache state, and user memory for cmpxchg. Dependencies are linkage/compiler/types headers and generic syscall declarations. Risk signals include the visible typo-like prototype `int sys_cacheflush(uint32_t, uint32_t uint32_t);`, which should be checked against actual build/generated declarations. Test signals are allmodconfig/defconfig build, clone/clone3, TLS ABI tests, cacheflush syscall users, and legacy cmpxchg users.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/thread_info.h

Low-level thread_info layout and TIF flag definitions for ARC. It defines THREAD_SIZE/order, struct thread_info fields needed by assembly, current_thread_info() via stack masking, INIT_THREAD_INFO, and masks for syscall/user-return work. Control flow is entry.S reading flags/preempt_count/ksp/cpu, scheduler updating ksp, and return-to-user handling _TIF_WORK_MASK and _TIF_SYSCALL_WORK. State persists at the base of each task kernel stack. Dependencies include page size, linux/thread_info.h, asm-offsets.c, and assembly macros. Risks are layout changes without offset regeneration, stack size mismatches, and missed TIF bits causing lost reschedule/signal/trace work. Test signals are preemption, signal delivery, syscall tracing, stack overflow checks, SMP raw_smp_processor_id(), and 16K stack builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/timex.h

Minimal ARC timing definitions. It sets CLOCK_TICK_RATE to 80 MHz as a legacy placeholder, includes asm-generic/timex.h, and notes get_cycles() is not implemented with RTSC yet. Control flow is generic timekeeping code including this header for legacy constants. State is none. Dependencies are generic timex and actual clocksource/timer drivers probed elsewhere. Risks are consumers accidentally relying on CLOCK_TICK_RATE despite dynamic clocks, and lack of arch get_cycles optimization. Test signals are timer_probe(), clocksource registration, delay calibration, and warnings from code using CLOCK_TICK_RATE.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/tlb.h

ARC TLB gather glue. It includes linux/pagemap.h and asm-generic/tlb.h without adding custom state. Control flow is generic mmu_gather and page-table teardown using generic implementation, while actual flush primitives are declared in tlbflush.h. Dependencies are generic TLB batching and ARC flush implementations. Risks are hidden if ARC needs stronger ordering than generic tlb gather supplies. Test signals are munmap/mprotect/unmap stress, page-table freeing under memory pressure, and SMP TLB shootdown coverage.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/tlbflush.h

TLB flush API declarations and UP/SMP dispatch for ARC. It declares local_flush_tlb_* functions and maps generic flush_tlb_* to local calls on UP, while SMP builds provide external cross-CPU implementations. THP has local_flush_pmd_tlb_range and flush_pmd_tlb_range variants. Control flow is MM operations invoking flushes after PTE/PMD changes, with SMP variants expected to perform shootdowns. State affected is hardware/software TLB contents, ASIDs, and possibly hugepage entries. Dependencies include linux/mm.h, CONFIG_SMP, CONFIG_TRANSPARENT_HUGEPAGE, and MMU implementation files. Risks include stale TLB entries after permissions or unmap changes, missing PMD huge flushes, and SMP shootdown races. Test signals are mprotect/COW/unmap, THP split/collapse, fork/exec, and cross-CPU memory ordering tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/uaccess.h

ARC user memory access implementation. It supplies inline assembly for scalar __get_user/__put_user sizes 1/2/4/8, raw_copy_from_user(), raw_copy_to_user(), and __clear_user(), then includes asm-generic/uaccess.h. Control flow relies on exception-table fixups: faulting load/store labels branch to .fixup code that returns -EFAULT or residual byte count. The copy routines optimize constant sizes, handle unaligned fallback if hardware lacks unaligned access, and use ARC loop registers. State touched is user/kernel memory and exception table metadata; no persistent data. Dependencies are generic uaccess wrappers, EFAULT, access_ok, ARC instruction encodings, lp_count, and CONFIG_ARC_USE_UNALIGNED_MEM_ACCESS. Risks are high: label/constraint mistakes can corrupt memory or misreport residuals; the constant-copy byte case uses auto-increment addressing and must match intended stride. Test signals are hardened usercopy, fault injection, copy boundary tests, unaligned user buffers, signal frame copy, and compat with exception-table sorting.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/unistd.h

Kernel-facing ARC syscall-number header. It includes UAPI unistd.h, requests legacy stat64/clone/vfork/fork syscall wrappers, and defines NR_syscalls from __NR_syscalls. Control flow is entry.S bounds-checking r8 against NR_syscalls and dispatching sys_call_table. State is compile-time syscall table sizing. Dependencies are generated uapi/asm/unistd_32.h and generic syscall table generation. Risks are table/count mismatch and obsolete __ARCH_WANT_* expectations during syscall cleanup. Test signals are syscall table build, ENOSYS for out-of-range syscalls, clone/vfork/fork ABI tests, and strace syscall numbering.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/unwind.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/unwind.h

ARC DWARF2 unwind interface and fallback stubs. With CONFIG_ARC_DW2_UNWIND it defines arc700_regs, unwind_frame_info, register accessor macros, stack-limit helpers, UNW_REGISTER_INFO, default return-address rule, arc_unwind(), arc_unwind_init(), and module unwind table add/remove. Without DWARF unwinding it stubs the APIs. Control flow is stacktrace/perf/module code registering tables and unwinding frames. State persists in module arch unwinder handles and per-frame register snapshots. Dependencies are scheduler task stacks, pt_regs, THREAD_SIZE, CONFIG_FRAME_POINTER, and module.c finalization. Risks are incomplete arch_unw_* helpers returning empty behavior, bad frame-pointer offsets, and module .eh_frame lifetime bugs. Test signals are kernel stack traces, module load/unload with unwinding, perf callchains, and builds with/without DWARF/frame pointers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/unwind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/vermagic.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/vermagic.h

Module architecture vermagic definition for ARC. It sets MODULE_ARCH_VERMAGIC to `ARC700`, which becomes part of module compatibility strings. Control flow is module build/load comparing vermagic to the running kernel. State is compile-time metadata. Dependencies are Linux module loader and arch Kconfig naming. Risk is that a fixed ARC700 string may be too coarse for ARCv2/HS distinctions if other ABI checks are insufficient. Test signals are insmod/modprobe vermagic rejection/acceptance across ARC ISA configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/vmalloc.h

Empty ARC vmalloc hook header. It supplies the include guard expected by generic code but defines no arch-specific vmalloc behavior. Control flow and state are owned by processor.h VMALLOC_* constants and generic vmalloc. Dependencies are include compatibility. Risks are low, but future arch vmalloc constraints could be missed if added elsewhere. Test signals are vmalloc/module/ioremap allocations and compile coverage.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/Kbuild

UAPI export manifest for ARC asm headers. It marks unistd_32.h as syscall-generated and selects generic ucontext.h. Control flow is header-install and syscall-header generation during kernel build. State is generated/exported userspace header set. Dependencies are scripts/headers_install, syscall-y handling, and generic UAPI ucontext. Risks are missing ABI headers during userspace header export or stale syscall generation. Test signals are `make headers_install`, libc/uapi consumers, and syscall table generation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/bpf_perf_event.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/bpf_perf_event.h

BPF perf event register ABI glue for ARC. It includes asm/ptrace.h and aliases bpf_user_pt_regs_t to user_regs_struct. Control flow is BPF/perf tooling using this type to interpret sampled user registers. State is ABI layout from uapi ptrace.h. Dependencies are stable user_regs_struct fields. Risks are BPF programs assuming pt_regs-like fields that ARC intentionally decouples. Test signals are BPF perf event programs, libbpf register access, and headers_install.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/bpf_perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/byteorder.h

Userspace byte-order selector for ARC. It includes big_endian or little_endian Linux byteorder headers based on __BIG_ENDIAN__. Control flow is compile-time for userspace and kernel UAPI consumers. State is none. Dependencies are compiler endian defines and Linux byteorder UAPI. Risks are toolchains that define endian macros differently, causing ABI misinterpretation. Test signals are headers_install and big/little endian userspace builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/cachectl.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/cachectl.h

Userspace cacheflush flag ABI for ARC. It defines fine-grained flags CF_I_INV, CF_D_FLUSH, CF_D_FLUSH_INV, CF_DEFAULT, and conventional ICACHE/DCACHE/BCACHE aliases. Control flow is sys_cacheflush users passing these flags to kernel cache maintenance. State is syscall argument bits. Dependencies are process/sys cacheflush implementation and Android/uClibc expectations. Risks include flag compatibility with existing binaries and under-specified address/length semantics outside this header. Test signals are cacheflush syscall tests, JIT/self-modifying-code workloads, and Android ABI consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/cachectl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/elf.h

ARC userspace ELF ABI definitions. It defines EF_ARC_OSABI mask/version flags, selects current OSABI by GCC version, and defines elf_greg_t/fpregset, ELF_NGREG, ELF_ARCV2REG, and elf_gregset_t based on UAPI ptrace structs. Control flow is ELF loader/core-dump/ptrace code checking e_flags and sizing regsets. State is userspace-visible ELF metadata. Dependencies are asm/ptrace.h and toolchain ABI versioning. Risks are compiler-version-based EF_ARC_OSABI_CURRENT causing old/new toolchain compatibility failures; process.c enforces this at exec. Test signals are ELF exec, core dumps, gdb regsets, and mixed GCC-version binaries.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/page.h

Userspace page constants for ARC. Kernel builds include vdso/page.h; non-kernel consumers get default 8 KiB PAGE_SHIFT/PAGE_SIZE/PAGE_MASK and PAGE_OFFSET 0x80000000. Control flow is userspace headers providing constants when libc/autoconf is absent. State is ABI constants, not runtime data. Dependencies are linux/const.h and kernel VDSO page definitions. Risks are userspace assuming 8 KiB pages on kernels configured differently; the comment acknowledges ad hoc consumers. Test signals are headers_install, busybox/uClibc builds, VDSO builds, and page-size variant user ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/ptrace.h

Stable ARC userspace register ABI for ptrace, core dumps, sigcontext, and BPF perf. It defines PTRACE_GET_THREAD_AREA, user_regs_struct with scratch/callee/pad/efa/stop_pc fields, and user_regs_arcv2 with r30/r58/r59. Control flow is ptrace.c converting kernel pt_regs/callee_regs to this ABI, signal.c embedding it in sigcontext, and debuggers reading/writing it. State is external ABI and cannot be reshaped; pad fields are preserved. Dependencies are ELF regset sizing and endian-neutral unsigned long layout. Risks are any field reorder/removal breaking GDB/libc/core readers; stop_pc/efa semantics around delay-slot breakpoints are subtle. Test signals are gdbserver, PTRACE_GETREGSET/SETREGSET, signal handlers inspecting ucontext, core dumps, and ARCv2 accumulator registers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/setup.h

Placeholder UAPI setup header. It intentionally exports a non-empty comment so header generation keeps asm/setup.h even though ARC has no userspace setup structures. Control flow is headers_install producing an include file for compatibility. State is none. Dependencies are UAPI install scripts and patch behavior. Risks are low; removal can break includes expecting <asm/setup.h>. Test signals are headers_install and userspace builds including asm/setup.h.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/sigcontext.h

Signal context ABI for ARC. It defines struct sigcontext containing user_regs_struct regs and user_regs_arcv2 v2abi. Control flow is signal.c saving/restoring these fields into ucontext during signal delivery and rt_sigreturn. State is user stack signal frame content. Dependencies are UAPI ptrace register ABI and SA_SIGINFO/ucontext users. Risks are ABI immutability, partial population when SA_SIGINFO is not used, and user tampering during sigreturn; signal.c forces STATUS_U on restore to mitigate kernel-mode returns. Test signals are signal handler ucontext inspection, rt_sigreturn, ARCv2 extra regs, altstack, and core dump compatibility.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/signal.h

ARC signal ABI extension. It defines SA_RESTORER so libc can provide a userland sigreturn stub, avoiding kernel-generated stack trampolines and related TLB/cache maintenance, then includes asm-generic/signal.h. Control flow is signal.c requiring SA_RESTORER when setting up frames and placing the restorer address in blink. State is sigaction flags and handler return path. Dependencies are libc/uClibc behavior and generic signal definitions. Risks are binaries without SA_RESTORER being rejected at signal delivery, and ABI flag collision. Test signals are libc signal tests, rt_sigreturn, signal delivery without/with SA_SIGINFO, and old userspace compatibility.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/swab.h

ARC byte-swap acceleration for userspace/kernel headers. It defines __arch_swab32() using the ARC `swape` instruction and enables 64-bit swaps through 32-bit pieces outside strict ANSI or inside the kernel. Control flow is generic swab macros selecting this arch primitive. State is none beyond input values. Dependencies are compiler inline assembly support and ARC ISA availability. Risks are using `swape` on incompatible cores/toolchains and missing memory clobbers not needed for pure register operations. Test signals are endian conversion selftests, big/little endian builds, and userspace header compilation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/unistd.h

Userspace syscall-number include for ARC. It includes generated asm/unistd_32.h and exports no extra logic. Control flow is libc and userspace builds including syscall numbers, while kernel asm/unistd.h wraps it for NR_syscalls and __ARCH_WANT_* flags. State is generated syscall ABI. Dependencies are syscall table generation. Risks are stale generated unistd_32.h or missing headers_install coverage. Test signals are headers_install, libc syscall wrappers, and strace numbering.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/Makefile

Build manifest for ARC kernel core objects. It selects common objects for boot, setup, IRQ, reset, ptrace, process, device tree, signal, traps, sys, troubleshoot, stacktrace, disasm, and context switching, then conditionally adds ISA-specific entry/intc, modules, SMP, MCIP, DWARF unwind, kprobes, unaligned emulation, KGDB, hostlink, perf, jump labels, and FPU support. Control flow is Kbuild deciding which source files are compiled. State is build composition only. Dependencies are CONFIG_* symbols and vmlinux.lds generation. Risks are duplicate arcksyms in obj-y and obj-$(CONFIG_MODULES) being benign only because Kbuild de-duplicates, and missing object inclusion for feature symbols. Test signals are defconfig/allmodconfig builds across ARCompact/ARCv2/SMP/modules/perf/kprobes/KGDB.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/arc_hostlink.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/arc_hostlink.c

Misc-device pseudo-driver for MetaWare hostlink environments. It allocates a page-aligned 16 KiB __HOSTLINK__ buffer, registers /dev/hostlink, returns the buffer address via ioctl, and maps it noncached through mmap using io_remap_pfn_range(). Control flow is module_init registering the misc device, then userspace ioctl+mmap accessing host communication memory. State is the static buffer and miscdevice registration. Dependencies include CONFIG_ARC_METAWARE_HLINK, miscdevice, uaccess put_user, pgprot_noncached, and mmap VM handling. Risks include returning a virtual address cast to unsigned int as a physical-ish address, weak ioctl command validation, and exposing a shared raw buffer. Test signals are hostlink userspace mmap/ioctl tests, noncached mapping behavior, and build only when MetaWare hostlink is enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/arc_hostlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/arcksyms.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/arcksyms.c

Symbol export file for ARC routines whose implementations live in compiler runtime or assembly/string sources. It exports libgcc helpers for 64-bit shifts, division, compare, floating conversions/arithmetic, and optimized memset/memcpy/memcmp/strchr/strcpy/strcmp/strlen. Control flow is module loader resolving undefined symbols from loadable modules. State is the exported symbol table. Dependencies are compiler code generation patterns, libgcc-compatible symbols linked into the kernel, and arch string implementations. Risks are modules depending on compiler helper symbols that disappear with toolchain changes, and exporting routines with semantics differing from generic expectations. Test signals are module builds using 64-bit arithmetic or string calls, modpost symbol resolution, and insmod runtime.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/arcksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/asm-offsets.c

Generates assembly constants for ARC low-level code. It emits offsets for task_struct, thread_struct, thread_info, mm_struct/mm_context, pt_regs fields, callee-reg size, and pt_regs size. Control flow is Kbuild running this C file to produce asm-offsets.h used by entry/head/context-switch assembly. State is compile-time constants derived from C layouts. Dependencies are struct definitions in sched/mm/thread_info/ptrace and CONFIG_ISA_ARCV2/DSP/ACCL_REGS. Risks are missing offsets for assembly users or layout changes not reflected in macros, causing boot or context-switch corruption. Test signals are successful assembly build, boot into entry paths, context switching, syscall/trap saves, and config matrix builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/ctx_sw_asm.S -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/ctx_sw_asm.S

Hand-written ARC context switch core. __switch_to saves blink/fp and kernel callee-saved registers for prev, stores sp into current thread_info.ksp, updates the current task pointer for the CPU, loads next thread_info.ksp, restores next callee registers/fp/blink, and returns through blink. Control flow is scheduler switch_to() invoking this routine after FPU/DSP save/restore. State transitions are per-task kernel stacks and _current_task/current register cache. Dependencies include asm-offsets.h, entry macros, task/thread_info layouts, and calling convention. Risks are catastrophic if stack layout or offsets drift; unwinder CFI must match pushes/pops. Test signals are scheduler stress, fork/exit, SMP migration, kernel thread switches, lockdep under context switches, and stack unwinding across __switch_to.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/ctx_sw_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/devtree.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/devtree.c

Early flat-device-tree machine selection for ARC. It optionally computes early serial base baud from root compatible strings, iterates machine_desc records, calls early_init_dt_scan(), matches a machine via of_flat_dt_match_machine(), and returns the selected descriptor or halts if none is found. Control flow is handle_uboot_args() passing external or embedded DTB, then setup_arch() using machine_desc hooks. State is __initdata arc_base_baud and selected machine_desc. Dependencies are linker-provided machine descriptor ranges, OF flat-tree APIs, serial.h, and compatible strings. Risks include invalid DTB falling back unexpectedly, no machine match halting boot, and early baud mismatch. Test signals are boot with embedded/external DTB, early console baud, and board compatible coverage.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/devtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/disasm.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/disasm.c

ARC instruction decoder used by unaligned emulation, kprobes, and KGDB. disasm_instr() fetches up to 8 bytes from kernel or user memory, classifies 16/32-bit instructions, handles limm extensions, load/store fields, branches/calls/jumps/loops, delay slots, and unaligned access metadata. get_reg()/set_reg() map architectural register numbers to pt_regs/callee_regs for ARCompact and ARCv2. disasm_next_pc() computes fall-through and branch targets, including delay-slot and zero-overhead-loop behavior. State is per-call disasm_state plus register frames. Dependencies are asm/disasm bitfield macros, copy_from_user, kprobes annotations, pt_regs layout, and callee_regs availability. Risks are decode incompleteness causing wrong single-step targets or bad unaligned emulation; user fetch logic must honor partial-copy faults. Test signals are KGDB single-step, kprobe branch probes, unaligned access emulation, delay-slot branches, limm instructions, and user-fault injection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/disasm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/entry-arcv2.S -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/entry-arcv2.S

ARCv2 low-level vector table and interrupt/exception return implementation. It builds the ARC HS vector table, routes interrupts to handle_interrupt, handles memory errors, misaligned access, TLB protection faults, and includes common entry.S for traps/syscalls. Return code distinguishes interrupt versus exception using AUX_IRQ_ACT, soft-disables IRQs for genirq accounting, handles user-mode return, and works around interrupt returns into delay slots by dropping to exception return. State is pt_regs on the kernel stack, AUX_IRQ_ACT/ICAUSE/status registers, and intr_to_DE_cnt. Dependencies include entry macros, arcregs, irqflags, MMU/page-fault handlers, and arch_do_IRQ. Risks are status/interrupt-active bookkeeping bugs, delay-slot return corruption, and vector numbering mismatches. Test signals are IRQ storms, page faults, misaligned access, syscall traps, preemption on return, and ARCv2 delay-slot exception cases.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/entry-arcv2.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/entry-compact.S -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/entry-compact.S

ARCompact vector table and low-level interrupt/exception handling. It sets 8-byte vector entries, handles optional two-level interrupts, memory bus errors, level 1/level 2 IRQ dispatch, TLB protection faults versus misaligned access, page-fault call wrapper, and includes common entry.S. Return logic chooses exception, L2 IRQ, or L1 IRQ epilogue from status32 active bits and compensates preempt_count when L2 interrupted L1. State includes scratch saved regs, sticky IRQ status, pt_regs, status32, and thread_info.preempt_count. Dependencies are ARC700 ISA macros, irqflags, entry macros, do_page_fault, do_misaligned_access, and arch_do_IRQ. Risks are nested interrupt priority inversion, fake-rtie exception state, and preempt_count imbalance. Test signals are ARCompact boot, level-2 timer IRQs, nested IRQ stress, misaligned access, page faults, and syscall/signal return.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/entry-compact.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/entry.S

Common ARC trap/syscall/return assembly included by ISA-specific entry files. It implements clone wrappers preserving user callee regs, ret_from_fork, instruction/machine/privilege/extension exception C entry calls, syscall tracing, breakpoint traps, normal syscall dispatch, and return-to-user slow paths for reschedule, signals, and notify_resume. State is pt_regs, callee_regs, thread flags, thread.fault_address, syscall return values, and current task state. Dependencies are sys_call_table, ptrace syscall trace hooks, do_signal(), schedule(), do_notify_resume(), entry macros, and ISA-specific restore_regs labels. Risks are syscall argument restoration after tracing, signal coredump callee-reg preservation, machine-check dead-end behavior, and user/kernel return flag tests. Test signals are strace, seccomp/audit tracepoints, fork/clone3, signal delivery, preemption on IRQ return, breakpoint traps, and machine-check/TLB overlap paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/fpu.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/fpu.c

FPU task-state initialization and save/restore. ARCompact uses DEXCL/DADDH instruction sequences to exchange double-precision FPU registers between outgoing and incoming task state without slow aux register stores. ARCv2 initializes FPU control/status for new tasks and saves/restores ARC_REG_FPU_CTRL/STATUS with FWE set. Control flow is switch_to() invoking fpu_save_restore() and start_thread() invoking fpu_init_task(). State persists in thread_struct.fpu. Dependencies are CONFIG_ISA_ARCOMPACT/ARCV2, CONFIG_ARC_FPU_SAVE_RESTORE, asm/fpu register layout, and processor startup sanity checks. Risks include early-clobber constraint errors, stale status bits, and missing save/restore when hardware FPU exists but config is off. Test signals are floating-point context-switch stress, fork/exec of FPU tasks, mixed kernel/user FPU workloads, and hardware-config sanity warnings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/head.S

ARC reset and early CPU startup assembly. CPU_EARLY_SETUP installs the vector base, configures I/D cache enable/invalidate state, handles ARCv2 unaligned-access status, optional loop-buffer disable, HSDK ICCM/DCCM remap, and DSP early init. stext performs SMP master/secondary split, clears BSS, stores U-Boot ABI registers, sets current task and initial stack, then jumps to start_kernel. first_lines_of_secondary sets the secondary idle task/current stack and jumps to start_kernel_secondary. State includes vector-base aux register, cache control registers, uboot_tag/magic/arg, current task per CPU, BSS, and initial stacks. Dependencies are linker symbols, entry macros, asm-offsets, Kconfig, and setup.c. Risks are clobbering boot arguments, wrong cache/unaligned state before C code, and secondary boot races. Test signals are cold boot, SMP secondary bring-up, U-Boot cmdline/DTB handoff, HSDK CCM boot, and cache-disabled configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/intc-arcv2.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/intc-arcv2.c

ARCv2 core interrupt controller driver. Early arc_init_IRQ() configures AUX_IRQ_CTRL autosave fields, reads IRQ_BCR, sets default priorities, disables private lines, and sets status32 priority/IE state. The irq_chip masks/unmasks/enables lines through AUX_IRQ_SELECT/ENABLE/PRIORITY. irqdomain mapping treats core private IRQs as percpu and external IRQs as level IRQs, installs the root domain, and maps IPI/SOFTIRQ lines. State is aux interrupt controller registers and irqdomain mappings. Dependencies are OF irqchip declaration `snps,archs-intc`, asm/irq constants, genirq, and SMP IPI setup. Risks are priority/autosave misconfiguration, masking common interrupts incorrectly, and missing percpu_devid for IPIs/timers. Test signals are boot irqchip_init, timer/perf/IPI IRQs, external device IRQs, SMP request_percpu_irq, and priority-level behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/intc-arcv2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/intc-compact.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/intc-compact.c

ARCompact core interrupt controller support. arc_init_IRQ() optionally marks Timer0 as level-2, resets AUX_IRQ_LEV, and disables IRQ lines. The irqchip uses AUX_IENABLE bit manipulation for mask/unmask, maps root IRQs through a linear domain, and provides a special arch_local_irq_enable() for two-level interrupts that avoids re-enabling the wrong priority while inside hard IRQ context. State is AUX_IRQ_LEV/AUX_IENABLE/status flags and irqdomain mapping. Dependencies are `snps,arc700-intc`, CONFIG_ARC_COMPACT_IRQ_LEVELS, genirq, and entry-compact.S return semantics. Risks include enabling lower-priority interrupts while an L1 context is active, timer priority assumptions, and limited 32-line controller bounds. Test signals are ARCompact timer IRQs, nested level-2 IRQs, spin_unlock_irq inside ISR, root irqdomain creation, and device IRQ request/free.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/intc-compact.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/irq.c

Generic ARC C interrupt entry. init_IRQ() initializes the whole DT irqchip tree, then invokes per-CPU SMP and machine hooks. arch_do_IRQ() is called from assembly with a hardware IRQ number and pt_regs; it enters IRQ context, installs irq_regs, dispatches generic_handle_domain_irq(NULL,hwirq), restores old regs, and exits IRQ context. State is current irq_regs and generic irq accounting. Dependencies are irqchip_init, machine_desc, plat_smp_ops, genirq domains, and assembly vector handlers. Risks are missing default irqdomain, incorrect hwirq from assembly, and irq_enter/exit imbalance. Test signals are boot interrupt initialization, timer interrupts, external IRQ delivery, /proc/interrupts, and IRQ tracing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/jump_label.c

Runtime static-key patching for ARCv2-style 32-bit NOP/branch instructions. It generates a middle-endian NOP, encodes unconditional branch offsets into split bitfields, asserts patched instructions do not cross L1 cache-line boundaries, writes the instruction atomically with WRITE_ONCE, and flushes I-cache. Optional CONFIG_ARC_DBG_JUMP_LABEL runs branch-encoding selftests at early_initcall. State is patched kernel text and static-key jump entries. Dependencies are jump_label.h alignment guarantees, cacheflush, ARC branch encoding, and BUG/pr_err diagnostics. Risks include branch offset overflow, unaligned target/code, cacheline-crossing atomicity failure, and incorrect endian instruction constants. Test signals are static key toggling, ftrace/tracepoint users, CONFIG_ARC_DBG_JUMP_LABEL selftest, and I-cache coherence after patching.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/kgdb.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/kgdb.c

ARC KGDB backend. It converts pt_regs/callee_regs to/from GDB register arrays, supports sleeping-thread register reads, implements software single-step by decoding next PC(s), planting trap instructions, restoring original opcodes, and flushing I-cache, and handles continue/step/detach/kill remote commands. kgdb_trap() adjusts PC for trap_s 3 software breakpoints and invokes kgdb_handle_exception(). State includes global single_step_data with saved opcodes/addresses and armed state. Dependencies are disasm_next_pc(), cacheflush, current->thread.callee_reg, kgdb core, and endian-specific breakpoint bytes. Risks include global single-step state on SMP, wrong branch-target decoding, and failing to restore patched text. Test signals are KGDB break/continue/step over branch/delay-slot instructions, SMP NMI callbacks, and compiled/software breakpoints.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/kgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/kprobes.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/kprobes.c

ARC kprobe/kretprobe implementation. It validates aligned probe addresses, replaces instructions with UNIMP_S traps, restores originals for single-step, decodes next PC and branch targets, plants temporary TRAP_S_2 instructions, manages per-CPU current_kprobe and kprobe_ctlblk state, handles reentrant probes, restores text, processes probe faults, registers a kretprobe trampoline, and notifies DIE_IERR/DIE_TRAP events. State includes patched instruction words, per-CPU kprobe control blocks, and saved temporary trap opcodes. Dependencies are disasm_next_pc(), cacheflush, notifier die events, current callee_regs, and kprobe core. Risks include probing exception code, races while text is temporarily restored, branch/delay-slot handling, and fault recovery gaps. Test signals are kprobe/kretprobe selftests, probes on branch/load/store functions, recursive probes, module probes, and I-cache coherence.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/mcip.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/mcip.c

ARCv2 ARConnect/MCIP and IDU support. SMP code probes MCIP features, sets GFRC/debug halt masks, configures per-CPU IPI/SOFTIRQ IRQs, sends/clears IPIs with coalescing, and publishes plat_smp_ops. IDU code programs common interrupt destination, mode, mask/ack, affinity, type, chained cascade handlers, and OF irqdomain setup. State is protected by mcip_lock and resides in MCIP/IDU aux command/readback registers plus irqdomain/chained-handler data. Dependencies include soc/arc/mcip.h commands, smp.c arch IPI handling, genirq, OF `snps,archs-idu-intc`, and cpu_online_mask. Risks are serialized command races, IPI coalescing assumptions, unsupported polarity/type, affinity masks beyond word 0, and panic when DT requests absent IDU. Test signals are SMP boot/IPIs, smp_call_function, common IRQ affinity changes, edge/level IRQ devices, CPU halt/debug behavior, and MCIP BCR variants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/mcip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/module.c

ARC module relocation and unwind integration. It records section-string data, initializes optional DWARF unwind arch fields, applies RELA relocations R_ARC_32_ME, R_ARC_32, and R_ARC_32_PCREL, registers .eh_frame with the unwinder after relocation, and removes unwind tables at cleanup. arc_write_me() writes middle-endian 32-bit values as two halfwords. State is patched module text/data sections and mod->arch unwind/secstr fields. Dependencies are ELF32 module loader, ARC relocation constants, vmalloc module memory, and unwind.h. Risks include unsupported relocations failing load, middle-endian write mistakes, PC-relative relocation base errors, and unwind table lifetime across init/core module sections. Test signals are loading modules with each relocation type, module stack traces, unload cleanup, and modpost/insmod errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/perf_event.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/perf_event.c

ARC performance counter PMU driver. It maps generic and ARC-specific perf events to hardware condition names discovered from CC_NAME registers, implements cache-event translation, counter allocation per CPU, enable/disable/start/stop/read, sampling-period programming, ARCv2 overflow IRQ handling, dynamic sysfs raw-event attributes, and perf callchains via arc_unwind_core. State includes global arc_pmu, per-CPU used counter masks and active events, PCT/CC aux registers, and sysfs attribute allocations. Dependencies are perf core, platform driver OF matches `snps,arc700-pct`/`snps,archs-pct`, arcregs, stacktrace, percpu IRQs, and endian conversion of condition names. Risks include global PMU singleton assumptions, ffz only checking used_mask[0], unsupported cache mappings, interruptless sampling fallback, and hardware condition-name variability. Test signals are `perf stat`, `perf record` with/without overflow IRQs, raw event sysfs, callchain capture, counter exhaustion, and ARCv2 user/kernel exclude filters.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/perf_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/process.c

ARC process, TLS, idle, clone, and ELF setup. It implements arc_settls/arc_gettls, legacy arc_usr_cmpxchg with user-fault fixup on non-LLSC cores, arch_cpu_idle for ARCv2/ARC700 sleep semantics, copy_thread() stack/register setup for user and kernel threads, start_thread() initial user pt_regs/FPU state, flush_thread(), and elf_check_arch() ABI validation. State touched includes thread_info.thr_ptr, pt_regs, child kernel stack/callee_regs, thread FPU state, status32 Z/U/L bits, and restart/fault state. Dependencies are uaccess, fixup_user_fault, fpu.h, entry ret_from_fork, UAPI ELF flags, and scheduler/task stack layout. Risks include user cmpxchg only safe on UP non-LLSC systems, delicate child stack layout shared with assembly, and strict OSABI rejection. Test signals are TLS syscalls, clone/fork/clone3, kernel threads, idle/resume IRQ behavior, old userspace cmpxchg, ELF exec with ABI flags, and FPU initial state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/ptrace.c

ARC ptrace/regset and syscall tracing implementation. It maps pt_regs offsets by ISA, converts kernel pt_regs/callee_regs to the stable user_regs_struct, accepts writes to mutable registers while ignoring status32/efa/stop_pc/pads, exposes ARCv2 extra regset, handles PTRACE_GET_THREAD_AREA, implements syscall_trace_enter/exit and tracepoints, and provides register name/offset/stack helpers. State is target task pt_regs, thread.callee_reg, thread_info.thr_ptr, and TIF syscall flags. Dependencies are UAPI ptrace/ELF regset sizing, membuf/user_regset helpers, trace/events/syscalls, and entry.S tracing flow. Risks include casting const pt_regs pointers for writes, not allowing status32 updates by ptrace, callee_reg pointer validity only when saved by entry paths, and register table layout drift. Test signals are gdb/strace, PTRACE_GETREGSET/SETREGSET, syscall tracepoints, TLS area ptrace request, core dump notes, and kernel stack register helpers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/reset.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/reset.c

Machine halt/restart/poweroff stubs for ARC. machine_halt() executes `flag 1` to halt; restart and poweroff print or fall through to halt; pm_power_off is exported and initialized NULL. Control flow is reboot/panic/poweroff paths invoking these hooks. State is pm_power_off function pointer. Dependencies are Linux reboot/PM infrastructure and platform-specific overrides that may replace these weak behaviors elsewhere. Risks are restart/poweroff not actually resetting or powering off hardware, leading to hangs in production unless platform handlers are added. Test signals are reboot, halt, poweroff, panic paths, and platform override registration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/setup.c

ARC architecture boot setup and CPU reporting. It handles U-Boot tag/magic/arg validation, external/embedded DTB selection, command-line append, setup_arch(), time_init(), machine init hooks, CPU feature probing/reporting for ARCompact and ARCv2, strict/weak hardware-vs-Kconfig checks, processor setup for IRQ/MMU/cache, /proc/cpuinfo iteration, and CPU topology registration. State includes machine_desc, _current_task[NR_CPUS], intr_to_DE_cnt, uboot_* __initdata, boot_command_line, root_mountflags, and per-CPU topology objects. Dependencies are OF, clocks/timers, cache/MMU setup, MCIP, DSP/FPU checks, linker DCCM symbol, and machine descriptors. Risks include invalid boot args, hardware/Kconfig mismatch panics, boot log buffer truncation, and CPU feature probe assumptions. Test signals are boot on multiple boards, external/embedded DTB paths, mem/cmdline early params, /proc/cpuinfo, topology sysfs, timer clock init, and strict option warnings/panics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/signal.c

ARC signal frame delivery and rt_sigreturn. It defines rt_sigframe with siginfo/ucontext/magic, saves/restores scratch user registers and ARCv2 extras, handles sigmask and altstack, validates user stack alignment/access, restores blocked mask, forces user mode on sigreturn, builds handler frames with r0/r1/r2 args, requires SA_RESTORER and stores restorer in blink, clears delay-slot state, and implements syscall restart rules. State lives on the user signal frame, pt_regs, current blocked signal mask, and restart_block. Dependencies are UAPI sigcontext/ptrace/signal, uaccess, entry return path, resume_user_mode_work, and syscall numbers. Risks include user-tampered frames, SA_RESTORER compatibility, restart PC decrement differing by ISA, and partial ucontext population. Test signals are signal/rt_signal tests, sigaltstack, SA_SIGINFO, syscall restart/no-restart cases, malicious sigreturn frames, delay-slot signal delivery, and ARCv2 extra regs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/smp.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/smp.c

ARC generic SMP boot and IPI layer. It parses possible-cpus from the flat DT or falls back to all NR_CPUS, initializes platform SMP hooks, prepares present CPUs, supports run-on-reset wake_flag boot, starts secondary CPUs through first_lines_of_secondary/start_kernel_secondary, wires active_mm, per-CPU init hooks, online notification, and implements IPI message bits for reschedule, call-function, and stop. IPI sends atomically OR per-CPU ipi_data and elide hardware sends if pending; do_IPI clears platform IRQ state, dequeues bits with xchg, and dispatches generic handlers. State includes plat_smp_ops, secondary_idle_tsk, wake_flag, per-CPU ipi_data and ipi_dev, and optional smp_atomic_ops_lock. Dependencies are DT possible-cpus, mcip/platform IPI callbacks, irqdomain mappings, scheduler, CPU hotplug, and thread_info cpu IDs. Risks include busy-wait wake_flag without timeout for run-on-reset secondaries, per-CPU message bit races if cmpxchg unsupported, one-second CPU-up timeout, and halt-on-stop behavior. Test signals are SMP boot, CPU online masks, reschedule IPIs, smp_call_function_many, CPU stop/reboot, possible-cpus DT variations, and non-LLSC atomic fallback.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/smp.c -->
