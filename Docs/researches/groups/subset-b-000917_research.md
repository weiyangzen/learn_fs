# subset-b-000917 research

Grouped research report for the requested Xtensa architecture files. Each file section preserves the source path in its title and is wrapped in the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pgtable.h

Purpose: defines Xtensa's two-level Linux page-table contract, folded through `asm-generic/pgtable-nopmd.h`, including PGD/PTE sizing, vmalloc/TLBTEMP ranges, hardware/software PTE bit layout, page protection presets, and swap-PTE encoding. Important APIs include `paging_init`, `swapper_pg_dir`, `pte_none`, `pte_present`, `pte_clear`, `pte_write`, `pte_dirty`, `pte_young`, `pte_modify`, `update_pte`, `set_pte`, `ptep_test_and_clear_young`, `ptep_get_and_clear`, `ptep_set_wrprotect`, `update_mmu_cache_range`, and `update_mmu_tlb_range`. Assembly consumers use `_PGD_INDEX`, `_PTE_INDEX`, `_PGD_OFFSET`, and `_PTE_OFFSET`.

Control flow is macro/inline driven: MM paths set/clear PTE bits, optionally write back PTE cache lines on aliasing writeback caches, and encode swap type/offset/exclusive state into invalid PTE formats. State is persistent in task `mm->pgd`, PTE pages, swap entries, TLB-visible attributes, and `swapper_pg_dir`. Dependencies include `asm/page.h`, `asm/kmem_layout.h`, cache geometry, Xtensa hardware version, and MMU configuration. Integration points are Linux MM, `entry.S` fast TLB/store handlers, cache aliasing code, swap, and page-fault handling. Risks are PTE bit layout regressions, older hardware valid/execute semantics, cache aliasing writeback omissions, wrong `PAGE_NONE` present tests, and swap bit overlap. Test signals include MMU boot, page fault/store fault tests, swap/COW, vmalloc and cache-alias stress, and builds for old/new Xtensa hardware versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/platform.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/platform.h

Purpose: declares platform hooks used by the Xtensa port during boot, setup, idle, clock calibration, and reset. Important APIs are `platform_init(bp_tag_t *)`, `platform_setup(char **)`, `platform_idle(void)`, `platform_calibrate_ccount(void)`, and noreturn `cpu_reset(void)`.

Control flow is supplied by platform code or weak defaults in `kernel/platform.c`: early boot calls `platform_init` before MMU initialization, `setup_arch` calls `platform_setup`, idle calls `platform_idle`, optional ccount calibration calls `platform_calibrate_ccount`, and reset paths call `cpu_reset`. State is not stored in the header, but hooks consume boot parameter tags and may mutate global platform/device state, command line data, or clock state. Dependencies include `linux/types.h` and `asm/bootparam.h`. Integration points are bootloader tag parsing, arch setup, idle loop, time initialization, and machine restart. Risks are missing platform overrides causing no-op setup or fallback 10 MHz clock calibration, and reset implementations needing MMU/cache-safe transitions. Test signals include boot logs, idle behavior, calibrated `ccount_freq`, platform device availability, and reset/restart tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/processor.h

Purpose: defines Xtensa process/CPU ABI constants, task address limits, interrupt levels, exception pseudo-causes, register-window helpers, `thread_struct`, user PS setup, `start_thread`, kernel stack accessors, and special-register accessors. Important definitions include `TASK_SIZE`, `STACK_TOP`, `EXCCAUSE_MAPPED_NMI`, `EXCCAUSE_MAPPED_DEBUG`, `VALID_DOUBLE_EXCEPTION_ADDRESS`, `LOCKLEVEL`, `TOPLEVEL`, `XTENSA_FAKE_NMI`, `MAKE_RA_FOR_CALL`, `MAKE_PC_FROM_RA`, `SPILL_SLOT*`, `USER_PS_VALUE`, `INIT_THREAD`, `KSTK_EIP`, `KSTK_ESP`, `xtensa_set_sr`, `xtensa_get_sr`, `xtensa_xsr`, and optional `set_er`/`get_er`.

Control flow is mostly inline/macro: `start_thread` rebuilds `pt_regs` for a new user program while preserving current register-file contents and syscall metadata. Persistent state includes `thread_struct.ra/sp`, optional ptrace breakpoint arrays, user register state in `pt_regs`, and special registers. Dependencies are `asm/core.h`, `asm/ptrace.h`, `asm/regs.h`, boot params, ABI selection, and XCHAL configuration. Integration points include scheduler context switch, exec, syscall/exception assembly, perf, hardware breakpoints, and PMU external registers. Risks are ABI mismatches between windowed and call0 builds, wrong task size breaking call-range assumptions, and special-register access ordering. Test signals include exec/fork tests, backtraces, ptrace register tests, SMP/fake-NMI builds, and both ABI build variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/ptrace.h

Purpose: defines kernel exception-frame layout and register access helpers for Xtensa ptrace, syscall, and exception handling. The central type is `struct pt_regs`, containing PC/PS/DEPC, exception cause/address, debug cause, window metadata, syscall number, special loop/SAR/threadptr registers, optional Xtensa registers, and the address-register file. Important APIs/macros are `NO_SYSCALL`, `task_pt_regs`, `user_mode`, `instruction_pointer`, `return_pointer`, `profile_pc`, `user_stack_pointer`, `regs_return_value`, `do_syscall_trace_enter`, and `do_syscall_trace_leave`; assembly sees `PT_REGS_OFFSET`.

Control flow is data-layout focused: assembly saves into this frame, C exception/syscall/ptrace code reads and mutates it, and return paths restore state from it. Persistent state lives on each task's kernel stack, with exact offsets generated by `asm-offsets.c`. Dependencies include `asm/kmem_layout.h`, UAPI ptrace definitions, coprocessor state, core configuration, and stack layout. Integration points are `entry.S`, `ptrace.c`, signal setup/return, core dumps, perf callchains, and syscall tracing. Risks are offset drift, register-window rotation mistakes, hiding PS.EXCM from user views, and profile PC accuracy under locks. Test signals include ptrace GET/SETREGS, signal delivery/return, syscall tracing, stack unwinding, and exception stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/regs.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/regs.h

Purpose: centralizes Xtensa special register numbers and bitfield constants for exception causes, processor status, debug break controls, and debug cause decoding. Important constants include `SREG_*` register bases, `EXCCAUSE_*` enumerations, `PS_*` masks/shifts, `DBREAKC_*` masks, and `DEBUGCAUSE_*` masks/bits.

Control flow is absent; this file is a shared ABI between C and assembly. State described by the constants is hardware state in PS, EXCCAUSE, DEBUGCAUSE, IBREAK/DBREAK, EPC/EPS/EXCSAVE, CCOMPARE, and related registers. Dependencies are minimal, but consumers rely on Xtensa ISA and configured register counts. Integration points include low-level exception entry, debug exception handling, hardware breakpoints, PMU, time, boot code, and trap dispatch. Risks are incorrect bit definitions causing unrecoverable exception handling, missed debug/watchpoint events, or wrong interrupt masking. Test signals include build coverage across hardware variants, hardware breakpoint tests, exception cause routing, timer interrupts, and debug single-step/watchpoint validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/seccomp.h

Purpose: wires Xtensa into generic seccomp by declaring the native audit architecture, syscall count, and human-readable name. Important definitions are `SECCOMP_ARCH_NATIVE`, `SECCOMP_ARCH_NATIVE_NR`, and `SECCOMP_ARCH_NATIVE_NAME`, plus inclusion of `asm-generic/seccomp.h`.

Control flow is generic: seccomp and audit code compare syscall metadata against these constants when filtering. State is not stored here; runtime state lives in task seccomp filters and audit records. Dependencies include `AUDIT_ARCH_XTENSA` and `NR_syscalls`. Integration points are `ptrace.c` syscall entry, `secure_computing()`, audit, BPF seccomp filters, and libc sandboxing. Risks are audit architecture mismatch or syscall-count drift leading to bad filter behavior. Test signals include seccomp filter selftests, audit syscall records, invalid syscall filtering, and syscall table count consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/sections.h

Purpose: extends generic section symbols with Xtensa vector, exception, secondary reset, and XIP section boundaries. Important declarations include `_WindowVectors_text_start/end`, `_DebugInterruptVector_text_start/end`, `_KernelExceptionVector_text_start/end`, `_UserExceptionVector_text_start/end`, `_DoubleExceptionVector_text_start/end`, `_exception_text_start/end`, interrupt-level vector section boundaries, `_SecondaryResetVector_text_start/end`, and XIP section bounds.

Control flow is absent; the file exposes linker-script symbols to C. State is linker-defined address ranges for exception vectors and XIP text/data. Dependencies include `asm-generic/sections.h` and configuration options for vector placement, secondary reset vectors, and XIP. Integration points are linker script, vector relocation/mapping, boot, cache/TLB setup, and module or diagnostics code needing section bounds. Risks are config-gated symbol mismatches with `vmlinux.lds.S` or stale declarations after vector layout changes. Test signals include link success for vector/XIP/SMP configs, boot vector execution, section boundary checks, and objdump/map-file inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/serial.h

Purpose: delegates Xtensa serial-port configuration to platform-specific `platform/serial.h`, supporting 8250-style serial setup without hardcoding board details in the architecture header.

Control flow is none; it is an include bridge. State is determined by platform serial definitions such as base addresses, IRQs, or baud settings provided elsewhere. Dependencies are the platform header path and serial driver expectations. Integration points are early console, 8250/legacy serial drivers, board platform code, and boot parameter serial tags. Risks are missing or incompatible platform serial definitions, which can break console availability or serial IRQ mapping. Test signals include early printk/console output, 8250 driver probe logs, serial loopback, and platform build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/shmparam.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/shmparam.h

Purpose: defines shared-memory low boundary alignment `SHMLBA` for Xtensa, choosing the larger of `PAGE_SIZE` and `DCACHE_WAY_SIZE` to avoid cache aliasing for System V shared memory.

Control flow is compile-time only. State affected is userspace shared-memory mapping placement and alignment as enforced by generic IPC/MM code. Dependencies are page size and data-cache geometry. Integration points include `arch_get_unmapped_area`, SysV shared memory attachment, cache alias avoidance, and mmap alignment. Risks are aliasing corruption if `SHMLBA` is too small for a cache configuration, and ABI-visible behavior if changed. Test signals include SysV shm attach tests, mmap alignment checks, cache-alias stress on large-way caches, and noMMU/MMU build validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/signal.h

Purpose: connects kernel Xtensa signal handling to UAPI signal definitions and advertises `__ARCH_HAS_SA_RESTORER`. It includes `uapi/asm/signal.h` and, for C kernel code, `asm/sigcontext.h`.

Control flow is delegated to `kernel/signal.c`; this header defines compile-time contracts for signal frames and restorer support. State is user-visible signal masks, action layout, and sigcontext data. Dependencies include UAPI signal ABI and sigcontext layout. Integration points are signal delivery/return, libc signal trampolines, ptrace signal stops, and `rt_sigreturn`. Risks are ABI breakage if restorer or sigcontext expectations change. Test signals include signal handler execution, alternate signal stack, rt_sigreturn, strace signal decoding, and libc compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/smp.h

Purpose: declares Xtensa SMP per-CPU identity, secondary CPU startup state, IPI helpers, and hotplug hooks. Important APIs/macros include `raw_smp_processor_id`, `cpu_logical_map`, `struct start_info`, `start_info`, `arch_send_call_function_ipi_mask`, `arch_send_call_function_single_ipi`, `secondary_start_kernel`, `smp_init_cpus`, `secondary_init_irq`, `ipi_init`, `show_ipi_list`, and hotplug `__cpu_die`, `__cpu_disable`, `cpu_die`, `cpu_restart`.

Control flow is implemented in `kernel/smp.c` and `head.S`/`mxhead.S`; this header is the public arch interface to generic SMP code. State includes per-thread `cpu`, secondary stack start info, CPU masks, and hotplug liveness. Dependencies include `CONFIG_SMP`, `thread_info`, cpumasks, and seq output. Integration points are scheduler, IPI broadcast, CPU bringup, interrupt display, and hotplug. Risks include wrong CPU identity before thread_info setup, stale start state, and IPI/hotplug races. Test signals include SMP boot, CPU hotplug, IPI counters in `/proc/interrupts`, reschedule/call-function IPIs, and cross-CPU TLB/cache flushes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/spinlock.h

Purpose: selects generic queued spinlock and queued rwlock implementations for Xtensa and defines `smp_mb__after_spinlock()` as a full SMP memory barrier.

Control flow is in included qspinlock/qrwlock code; this header supplies the arch barrier hook. State is lock word state managed by generic locking primitives. Dependencies include `asm/barrier.h`, `asm/qspinlock.h`, and `asm/qrwlock.h`. Integration points are all kernel spinlock/rwlock users, scheduler and interrupt synchronization, and SMP memory ordering. Risks center on insufficient barrier semantics after lock acquisition or mismatched atomic implementation support. Test signals include locktorture, SMP stress, lockdep, atomic/queued lock build coverage, and memory-order litmus-style failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/spinlock_types.h

Purpose: exposes queued spinlock and queued rwlock type definitions for Xtensa while preventing direct inclusion outside Linux lock headers. Important contents are the inclusion guard check and includes of `asm-generic/qspinlock_types.h` and `asm-generic/qrwlock_types.h`.

Control flow is compile-time include validation only. State layout is the ABI of raw spinlock/rwlock objects embedded throughout the kernel. Dependencies are Linux lock header inclusion order and generic queued lock type definitions. Integration points are all raw/spin/rw lock declarations, lockdep, and generic locking code. Risks are direct inclusion errors, type-size mismatches if generic lock config changes, and ABI/layout assumptions in assembly or percpu structures. Test signals are allmodconfig-style builds, lock type compile checks, and locktorture on SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/stackprotector.h

Purpose: provides GCC stack protector support for Xtensa via global `__stack_chk_guard` and boot-time canary initialization. Important API is `boot_init_stack_canary()`, which calls `get_random_canary()`, stores it in `current->stack_canary`, and copies it to `__stack_chk_guard`.

Control flow is early boot/init only and must be inlined in non-returning initialization contexts. Persistent state is the global canary plus per-task `stack_canary`; the comment notes SMP cannot use a different compiler canary per task because Xtensa GCC expects a global symbol. Dependencies include `current`, task canary fields, and random canary generation. Integration points are compiler-emitted stack protector checks, `process.c` exported guard, and context switch stack protector refresh for non-SMP. Risks are weak canary uniqueness on SMP and ordering before protected code runs. Test signals include stack protector enabled builds, deliberate stack-smash tests, boot entropy checks, and symbol export/module linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/stacktrace.h

Purpose: declares Xtensa stack-walking primitives and a minimal `struct stackframe` with `pc` and `sp`. Important APIs are `stack_pointer`, `walk_stackframe`, `xtensa_backtrace_kernel`, and `xtensa_backtrace_user`.

Control flow is implemented in `kernel/stacktrace.c`: callers seed a stack pointer or pt_regs, and callback-driven walkers report frames. State is task stack content and saved thread stack pointer. Dependencies include scheduler/task structures and Xtensa return-address encoding. Integration points are perf callchains, `return_address`, oops stack dumps, tracing, and scheduler diagnostics. Risks are invalid SP boundaries, register-window ABI return-address reconstruction, user memory faults while walking user stacks, and stale `thread.sp` for running tasks. Test signals include perf callchains, oops stack output, `save_stack_trace`, sleeping task `wchan`, and user/kernel backtrace tests for both ABIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/string.h

Purpose: supplies Xtensa-specific inline implementations or declarations for common string/memory operations. It defines inline `strcpy`, `strncpy`, `strcmp`, and `strncmp`, declares `memset`, `__memset`, `memcpy`, `__memcpy`, `memmove`, and `__memmove`, and redirects memops to non-instrumented versions under KASAN for non-instrumented files.

Control flow is tight inline assembly loops for byte loads/stores and comparisons; memory block functions live in arch library code. Persistent state is only caller memory. Dependencies include Xtensa load/store instructions, `size_t`, `uintptr_t`, KASAN, and FORTIFY interaction. Integration points are the whole kernel C library layer, uaccess clear/copy helpers, boot code, and sanitizer instrumentation. Risks include missing NUL padding semantics in `strncpy`, inline asm constraints/memory clobbers, KASAN/FORTIFY bypass mistakes, and unaligned or inaccessible pointers. Test signals include lib/string selftests, KASAN builds, boot smoke, memmove overlap tests, and compiler warning checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/switch_to.h

Purpose: declares the low-level context switch routine `_switch_to(void *last, void *next)` and maps the generic `switch_to(prev, next, last)` macro to it.

Control flow is a simple macro wrapper; actual state save/restore is in `kernel/entry.S`. Persistent state touched by the implementation includes `thread_struct.ra/sp`, kernel stack pointer in `exc_table`, coprocessor enable state, optional user Xtensa registers, stack canary, and PS interrupt state. Dependencies include scheduler calling conventions and ABI-specific `_switch_to`. Integration points are the scheduler, task fork setup, register-window spilling, coprocessor lazy context switching, and stack protector. Risks are type-erased `void *` misuse, ABI register preservation errors, and switch return value assumptions. Test signals include scheduler stress, fork/exec tests, preemption, SMP task migration, and coprocessor state preservation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/syscall.h

Purpose: provides generic syscall inspection and mutation helpers for Xtensa. Important APIs are `syscall_get_arch`, `sys_call_table`, `syscall_get_nr`, `syscall_set_nr`, `syscall_rollback`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`, `syscall_get_arguments`, `syscall_set_arguments`, and Xtensa syscall prototypes `xtensa_rt_sigreturn`, `xtensa_shmat`, and `xtensa_fadvise64_64`.

Control flow maps syscall number and arguments to fields in `pt_regs`; Xtensa uses return register `areg[2]` and argument registers `{6,3,4,5,8,9}`. State is the syscall number and register frame saved by `entry.S`. Dependencies include `linux/err.h`, `asm/ptrace.h`, audit arch definitions, and syscall table generation. Integration points are tracing, audit, seccomp, ptrace, syscall dispatch in `entry.S`, and signal return. Risks are wrong argument register mapping, failure to distinguish error from valid high unsigned returns through `IS_ERR_VALUE`, and syscall table count drift. Test signals include strace/seccomp/audit selftests, syscall fuzzing, fadvise/shmat ABI tests, and ptrace syscall modification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/sysmem.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/sysmem.h

Purpose: declares architecture memory initialization entry points `bootmem_init()` and `zones_init()`.

Control flow is implemented elsewhere in setup/mm code: early boot discovers/reserves memory, then initializes zones for the Linux page allocator. State includes memblock reservations, PFN ranges, zone layouts, and boot memory allocator metadata. Dependencies include `linux/memblock.h`. Integration points are `setup_arch`, boot parameter memory tags, device tree memory discovery, and the page allocator. Risks are mismatched prototypes with implementation, bad memory ranges causing allocator corruption, and missed reserved regions. Test signals include boot memblock logs, `/proc/zoneinfo`, memory hotplug or sparsemem build coverage where applicable, and boot with multiple memory regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/sysmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/thread_info.h

Purpose: defines low-level per-thread state used directly by Xtensa assembly, including `struct thread_info`, current-thread lookup, thread flags, and stack size constants. Important fields are `task`, `flags`, `status`, `cpu`, `preempt_count`, optional `atomctl8`, optional `ps_woe_fix_addr`, `cpenable`, `cp_owner_cpu`, optional coprocessor save areas, and `xtregs_user`. Important APIs/macros are `INIT_THREAD_INFO`, `current_thread_info`, `GET_THREAD_INFO`, `_TIF_WORK_MASK`, `THREAD_SIZE`, and `THREAD_SIZE_ORDER`.

Control flow is macro/inline: current thread is computed by masking stack pointer low bits, and assembly uses generated offsets to read flags and CPU/coprocessor state. Persistent state is per-task low-level execution state at the base of the kernel stack. Dependencies include `asm/kmem_layout.h`, `asm/processor.h`, coprocessor types, and generated offsets. Integration points are `entry.S`, scheduler, syscall return work loop, coprocessor lazy switching, SMP CPU identity, and user ABI probing. Risks are layout drift without offset regeneration, cacheline-size assumptions, stack masking errors, and lost `_TIF_WORK_MASK` bits. Test signals include context switch, syscall tracing/seccomp, signal delivery, coprocessor state tests, and SMP/preemption stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/timex.h

Purpose: selects a usable Xtensa hardware timer interrupt and provides accessors for cycle counter and compare register. Important definitions are `LINUX_TIMER`, `LINUX_TIMER_INT`, `ccount_freq`, `local_timer_setup`, `get_ccount`, `set_ccount`, `get_linux_timer`, and `set_linux_timer`.

Control flow is compile-time timer selection based on available timers and interrupt levels; inline accessors read/write special registers. Persistent state is hardware `ccount`, selected `ccompare`, and global `ccount_freq`. Dependencies include `asm/processor.h`, `SREG_CCOMPARE`, XCHAL timer configuration, and generic timex. Integration points are `kernel/time.c`, clocksource/clockevent setup, scheduler clock, delay calibration, SMP local timer setup, and platform clock calibration. Risks include selecting an interrupt above exception level, wrong frequency calibration causing time drift, and special-register writes affecting active timers. Test signals include boot timekeeping, timer interrupts, `clocksource` selection, delay calibration logs, SMP timer setup, and sleep/timeout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/tlb.h

Purpose: connects Xtensa to generic TLB gather/free logic and declares debug sanity checking. Important definition is `__pte_free_tlb(tlb, pte, address)` mapped to `pte_free((tlb)->mm, pte)`, plus `check_tlb_sanity()`.

Control flow is generic MMU teardown through `asm-generic/tlb.h`; Xtensa customizes PTE page freeing. State is page-table memory and TLB state managed elsewhere. Dependencies include `asm/cache.h`, `asm/page.h`, and generic TLB APIs. Integration points are memory unmap, page-table teardown, `entry.S` debug TLB sanity checks under `CONFIG_DEBUG_TLB_SANITY`, and architecture MM. Risks are freeing PTE pages without needed cache/TLB synchronization and debug sanity build drift. Test signals include mmap/munmap stress, exit teardown, TLB debug builds, and MMU fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/tlbflush.h

Purpose: declares local/SMP TLB flush APIs and implements inline Xtensa TLB probe, invalidate, config, and read/write helpers. Important APIs include `local_flush_tlb_all/mm/page/range/kernel_range`, SMP `flush_tlb_*` wrappers, `itlb_probe`, `dtlb_probe`, `invalidate_itlb_entry`, `invalidate_dtlb_entry`, no-isync invalidators, `set_itlbcfg_register`, `set_dtlbcfg_register`, `set_ptevaddr_register`, `read_ptevaddr_register`, `write_dtlb_entry`, `write_itlb_entry`, `invalidate_page_directory`, `invalidate_itlb_mapping`, `invalidate_dtlb_mapping`, and diagnostic `read_*tlb_*`.

Control flow is inline special-register/TLB instruction sequences with required `isync`/`dsync`. SMP builds route public flushes to cross-CPU implementations; UP maps directly to local flushes. State is hardware ITLB/DTLB entries, TLB config registers, page-directory wired ways, and PTE virtual address register. Dependencies include `asm/processor.h`, PTE types, MM structures, and SMP support. Integration points include MMU faults, page-table updates, cache aliasing code, SMP TLB shootdown, and debug diagnostics. Risks are missing synchronization after invalidates, wrong hit-bit constants, stale page-directory wired entries, and use of diagnostic non-ISA instructions. Test signals include TLB shootdown stress, page protection changes, vmalloc faults, SMP munmap, and debug TLB dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/traps.h

Purpose: defines Xtensa exception dispatch data structures, handler types, fast handler declarations, trap initialization helpers, register spill helper, and debug exception save layout. Central types are `xtensa_exception_handler`, `struct exc_table`, and `struct debug_table`. Important APIs are `trap_set_handler`, fast handler declarations, `kernel_exception`, `user_exception`, `system_call`, `do_IRQ`, `do_page_fault`, `do_unhandled`, `early_trap_init`, `secondary_trap_init`, `spill_registers`, and `debug_exception`.

Control flow centers on `exc_table`, pointed to by `EXCSAVE1`, containing kernel stack pointer, double-exception/fixup slots, optional coprocessor owners, fast user/kernel handlers, and default C handlers. `early_trap_init` installs minimal handlers before full trap setup. Persistent state is per-CPU exception table and debug save table. Dependencies include `pt_regs`, exception cause count, coprocessor support, and generated offsets. Integration points are vectors, `entry.S`, `traps.c`, MMU boot, coprocessor lazy switching, debug/watchpoints, and secondary CPU init. Risks are handler-table corruption, stale fixup handlers, wrong stack pointer during early faults, and register-window spill failures. Test signals include early boot with MMU faults, exception routing, debug watchpoints, secondary CPU startup, and panic/oops paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/uaccess.h

Purpose: implements Xtensa user memory access primitives for scalar get/put, raw copy, clear, and user string helpers. Important APIs/macros are `put_user`, `get_user`, `__put_user`, `__get_user`, `__put_user_check/nocheck/size`, `__get_user_check/nocheck/size`, `__put_user_asm`, `__get_user_asm`, alignment checks, `__xtensa_copy_user`, `raw_copy_from_user`, `raw_copy_to_user`, `__xtensa_clear_user`, `clear_user`, `__clear_user`, `strncpy_from_user`, and `strnlen_user`.

Control flow first validates ranges with `access_ok` for checked variants, rejects unaligned scalar access before issuing faultable load/store asm, and uses exception-table fixups to convert faults to `-EFAULT`. 8-byte transfers fall back to copy helpers. Persistent state is caller buffers and exception-table metadata; no global state is stored. Dependencies include `asm/extable.h`, generic access_ok, `__ex_table`, `__memset`, user-copy assembly, and errno. Integration points are syscalls, ptrace, signal frames, futexes, and any kernel-to-user transfer. Risks include label/fixup mismatch, unaligned double-fault kernel panic, incorrect residual count for clear/copy, and access_ok granularity only checking one byte for strings. Test signals include usercopy selftests, fault injection, unaligned pointer tests, signal/ptrace copy failures, and KASAN/usercopy hardening.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/unistd.h

Purpose: selects syscall compatibility wants and includes the Xtensa UAPI syscall numbers. Important definitions include `__ARCH_WANT_SYS_CLONE`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_UTIME32`, `__ARCH_WANT_SYS_GETPGRP`, and `NR_syscalls`.

Control flow is compile-time syscall table generation and generic syscall availability selection. State is the generated syscall ABI exposed through `sys_call_table` and UAPI headers. Dependencies include `uapi/asm/unistd.h` and generated `unistd_32.h`. Integration points are syscall table generation, `entry.S` dispatch, libc ABI, seccomp syscall count, and trace/audit. Risks are stale `NR_syscalls`, unintended legacy syscall exposure, and mismatch with generated headers. Test signals include syscall table build, strace syscall numbers, seccomp bounds checks, and legacy stat/utime/clone syscall tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/vectors.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/vectors.h

Purpose: computes kernel and exception vector virtual addresses for Xtensa, including MMU V3 remapping and optional configurable vector base. Important definitions include `KERNELOFFSET`, `RESET_VECTOR1_VADDR`, `VECBASE_VADDR`, `VECTOR_VADDR`, and addresses for user, kernel, double exception, window, interrupt-level, and debug vectors.

Control flow is compile-time address selection based on MMU, PTP MMU, spanning-way, kernel virtual address, and vector-base capability. Persistent state is linker/boot mapping expectations rather than runtime variables. Dependencies include `asm/core.h`, `asm/kmem_layout.h`, XCHAL vector constants, and Kconfig. Integration points are vector assembly, linker script, boot MMU initialization, secondary reset vector, and exception dispatch. Risks include wrong vector address under VECBASE or MMU V3, a likely typo mapping `INTLEVEL7_VECTOR_VADDR` to the level 6 constant in the non-VECBASE branch, and stale XCHAL undef behavior. Test signals include boot on VECBASE/non-VECBASE cores, interrupt/debug exception entry, map-file validation, and vector relocation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/vectors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/vermagic.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/vermagic.h

Purpose: contributes Xtensa core identity to module version magic. Important definition is `MODULE_ARCH_VERMAGIC`, built as `xtensa-<XCHAL_CORE_ID> ` through `linux/stringify.h` and `variant/core.h`.

Control flow is module build/load metadata generation. State is embedded in module `.modinfo` and compared by the module loader. Dependencies are configured variant core ID and Linux vermagic assembly. Integration points are out-of-tree module compatibility, kernel module loader, and variant-specific builds. Risks are modules built for one Xtensa core loading on incompatible hardware if vermagic is wrong, or unnecessary load rejection if core IDs differ despite compatibility. Test signals include module build/load, `modinfo vermagic`, variant rebuilds, and negative tests with mismatched modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/vmalloc.h

Purpose: placeholder architecture vmalloc header for Xtensa. It only provides an include guard and no custom declarations.

Control flow and persistent state are absent; generic vmalloc behavior applies. Dependencies are only include ordering expectations from generic Linux headers. Integration points are generic vmalloc, ioremap/vmap users, and architecture headers that include `asm/vmalloc.h` conditionally. Risks are low, but future Xtensa vmalloc customization must preserve source-tree include contracts. Test signals include build coverage for vmalloc users, module/vmalloc allocation smoke tests, and include self-sufficiency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/Kbuild

Purpose: controls exported UAPI header generation for Xtensa. It marks `unistd_32.h` as generated and reuses generic `ucontext.h`.

Control flow is Kbuild header-install/generation logic rather than runtime execution. State is generated syscall header output and installed UAPI header set. Dependencies include architecture syscall tables and generic UAPI infrastructure. Integration points are `make headers_install`, libc header consumption, syscall table generation, and UAPI packaging. Risks are missing generated headers or accidentally exporting incompatible local headers. Test signals include `headers_install`, generated `unistd_32.h` presence, libc/toolchain builds, and UAPI header diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/auxvec.h

Purpose: reserved Xtensa UAPI auxiliary-vector header with only an include guard and no architecture-specific AT_* entries.

Control flow and persistent state are absent. Generic ELF auxiliary vector handling provides the effective runtime behavior. Dependencies are only UAPI include order. Integration points are ELF loader, libc startup code, and exported kernel headers. Risks are low; adding future auxvec constants would be ABI-visible. Test signals include headers install, libc build, ELF exec smoke tests, and auxv inspection showing only generic entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/byteorder.h

Purpose: selects UAPI byteorder definitions for little-endian or big-endian Xtensa. It includes `linux/byteorder/little_endian.h` when `__XTENSA_EL__` is defined, `linux/byteorder/big_endian.h` when `__XTENSA_EB__` is defined, and errors otherwise.

Control flow is preprocessor selection. State is not runtime state, but it defines ABI interpretation for multi-byte values in UAPI structs and ioctl payloads. Dependencies are compiler-provided Xtensa endian macros. Integration points include exported headers, SysV IPC struct time-field ordering, networking, filesystems, and userspace builds. Risks are toolchain macro mismatch or unsupported bi-endian build paths. Test signals include big/little endian builds, headers_install, userspace compile tests, and ABI layout checks for endian-sensitive structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ioctls.h

Purpose: defines Xtensa UAPI ioctl numbers for file, terminal, pty, modem, serial, and termios operations. Important constants include `FIOCLEX`, `FIONBIO`, `FIONREAD`, `TCGETS/TCSETS*`, `TCGETA/TCSETA*`, `TIOCSWINSZ/TIOCGWINSZ`, modem bits `TIOCM_*`, pty controls, RS485/ISO7816 controls, and serial diagnostics.

Control flow is ABI constant lookup by drivers and userspace. Persistent state affected at runtime is device/tty state managed by generic tty and serial subsystems. Dependencies include `asm/ioctl.h`, type sizes for `pid_t`, `loff_t`, and tty structs. Integration points are libc ioctl wrappers, terminal emulators, serial drivers, ptys, and strace decoding. Risks are ABI-number incompatibility, hardcoded legacy values with structure-size assumptions, and divergence from generic tty ioctl expectations. Test signals include tty/pty selftests, serial ioctl tests, termios tools, strace number decoding, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ipcbuf.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ipcbuf.h

Purpose: defines the Xtensa UAPI `struct ipc64_perm` used in System V IPC objects. Fields include key, uid/gid/cuid/cgid, mode, sequence, and two padding words.

Control flow is none; generic IPC syscalls copy this structure across the user/kernel boundary. Persistent state is IPC permission metadata in kernel IPC objects and userspace ABI buffers. Dependencies include `linux/posix_types.h`. Integration points are message queues, semaphores, shared memory, libc IPC APIs, and compat ABI layout. Risks are padding/field-size ABI regressions and mismatch with IPC object structures. Test signals include SysV IPC tests, structure size/offset checks, big/little endian builds, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ipcbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/mman.h

Purpose: defines Xtensa UAPI memory-management protection and mapping constants. Important definitions include `PROT_*`, `MAP_TYPE`, `MAP_FIXED`, legacy non-Linux flags, Linux `MAP_*`, `MS_*`, `MCL_*`, `MLOCK_ONFAULT`, `MADV_*` including guard and collapse flags, `MAP_FILE`, and pkey disable masks.

Control flow is userspace/kernel ABI constant interpretation in mmap, mprotect, msync, mlock, madvise, and pkey paths. Persistent state affected is VMA flags, page protections, locked memory state, and memory advice state. Dependencies are generic MM syscalls and architecture protection support in `pgtable.h`. Integration points include libc, ELF loader, memory allocators, SysV shm mapping, and tests. Risks include ABI constant collisions, unsupported execute/write protection nuance, and stale additions relative to generic MM. Test signals include mmap/mprotect/msync/mlock/madvise selftests, userspace header compile checks, and protection fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/msgbuf.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/msgbuf.h

Purpose: defines Xtensa UAPI `struct msqid64_ds` for System V message queues, including permission data, split high/low timestamp fields ordered by endianness, byte/message counts, queue size limit, last sender/receiver PIDs, and padding.

Control flow is none; generic IPC message queue syscalls copy this layout to/from userspace. Persistent state represented is kernel message-queue metadata. Dependencies include `asm/ipcbuf.h` and endian macros. Integration points are libc `msgctl`, checkpoint/restore tools, strace, and SysV IPC tests. Risks include endian-specific timestamp layout regressions, 32-bit time extension handling, and padding ABI stability. Test signals include msgget/msgsnd/msgrcv/msgctl tests, structure offset checks for both endian modes, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/msgbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/poll.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/poll.h

Purpose: defines Xtensa-specific poll event aliases before including generic poll definitions. Important constants are `POLLWRNORM` as `POLLOUT`, `POLLWRBAND`, and `POLLREMOVE`.

Control flow is ABI event-bit interpretation in poll/select/epoll users. Persistent state is readiness bitmasks produced by file operations and consumed by userspace. Dependencies include `asm-generic/poll.h`. Integration points are libc poll APIs, epoll, drivers, and strace. Risks are event bit collision with generic definitions or userspace relying on architecture-specific values. Test signals include poll/epoll selftests, headers_install, and driver readiness behavior tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/poll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/posix_types.h

Purpose: defines Xtensa UAPI kernel POSIX base types before deferring to generic definitions. Important typedefs are `__kernel_ipc_pid_t`, `__kernel_size_t`, `__kernel_ssize_t`, `__kernel_ptrdiff_t`, `__kernel_old_uid_t`, `__kernel_old_gid_t`, and `__kernel_old_dev_t`.

Control flow is none; it is exported ABI type definition. Persistent state impacted is binary layout of UAPI structures using these typedefs. Dependencies include `asm-generic/posix_types.h` and non-GCC userspace compatibility concerns. Integration points are libc, SysV IPC, stat/signal/ioctl layouts, and headers_install. Risks are type-size ABI breakage, namespace pollution, and compiler compatibility. Test signals include userspace header compile tests, ABI size/offset checks, libc builds, and IPC/stat structure validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ptrace.h

Purpose: defines UAPI ptrace register numbers, ptrace request numbers, FDPIC selector constants, and `struct user_pt_regs`. Important constants include `REG_A_BASE`, `REG_AR_BASE`, `REG_PC`, `REG_PS`, `REG_WB`, `REG_WS`, `REG_LBEG`, `REG_LEND`, `REG_LCOUNT`, `REG_SAR`, `SYSCALL_NR`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, `PTRACE_GETXTREGS`, `PTRACE_SETXTREGS`, `PTRACE_GETHBPREGS`, `PTRACE_SETHBPREGS`, and `PTRACE_GETFDPIC`.

Control flow is implemented in `kernel/ptrace.c`, which maps this ABI to internal `pt_regs` and TIE/coprocessor state. Persistent state is debugger-visible task register state. Dependencies include `linux/types.h` and Xtensa register-window architecture. Integration points are strace, gdb, core dump regsets, hardware breakpoints, syscall tracing, and FDPIC loaders. Risks include ABI structure size/offset regressions, windowbase/windowstart rotation mistakes, and reserved field misuse. Test signals include ptrace GET/SETREGS/GETXTREGS, gdb single-step, hardware breakpoint ptrace operations, strace syscall number reads, and core dump register notes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sembuf.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sembuf.h

Purpose: defines Xtensa UAPI `struct semid64_ds` for System V semaphores, including permissions, endian-ordered split operation/change timestamps, semaphore count, and padding.

Control flow is generic SysV semaphore syscall copying. Persistent state represented is semaphore-set metadata in kernel IPC state and userspace buffers. Dependencies include `asm/byteorder.h` and `asm/ipcbuf.h`. Integration points are libc `semctl`, IPC tools, checkpoint/restore, and strace. Risks are endian timestamp ordering, padding ABI stability, and 32-bit time handling. Test signals include semget/semop/semctl selftests, structure offset validation, big/little endian builds, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sembuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/setup.h

Purpose: exports Xtensa setup constant `COMMAND_LINE_SIZE`, set to 256.

Control flow is none; it bounds boot command-line buffers and UAPI expectations. Persistent state affected is boot command-line storage and parsing length in setup code. Dependencies are consumers that include UAPI setup headers. Integration points include bootloader parameter parsing, `setup_arch`, proc/cmdline exposure, and userspace headers. Risks are truncation of long command lines and ABI-visible change if size is altered. Test signals include boot with long command line, setup parser behavior, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/shmbuf.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/shmbuf.h

Purpose: defines Xtensa UAPI shared-memory metadata structures `struct shmid64_ds` and `struct shminfo64`. `shmid64_ds` contains permissions, segment size, attach/detach/change timestamps with high words, creator/last PIDs, attach count, and padding; `shminfo64` contains shm limits and padding.

Control flow is generic SysV shm syscall copying. Persistent state represented is shared memory segment metadata and system limits. Dependencies include `asm/ipcbuf.h` and `asm/posix_types.h`. Integration points are `shmctl`, `shmat`, libc IPC APIs, cache-aligned shared memory mapping, and CRIU-like tools. Risks include historically wrong-side padding for big-endian Xtensa, size_t width assumptions, and timestamp ABI stability. Test signals include shmget/shmat/shmctl tests, endian structure offset checks, headers_install, and shared-memory alignment/cache stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/shmbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sigcontext.h

Purpose: defines the user-visible Xtensa signal context saved in signal frames. Fields include `sc_pc`, `sc_ps`, loop registers, `sc_sar`, accumulator low/high placeholders, 16 address registers, and `sc_xtregs` pointer.

Control flow is used by signal delivery and `rt_sigreturn` to save and restore user execution state. Persistent state is the signal frame placed on the user stack. Dependencies include signal frame code, Xtensa register ABI, and optional Xtensa extension register storage. Integration points are libc signal handlers, debuggers inspecting signal frames, ptrace, and core dumps. Risks are ABI layout changes, incomplete register preservation for extended/TIE state, and invalid user-stack pointers. Test signals include signal handler/return tests, altstack, nested signals, gdb signal frame unwinding, and ABI size/offset checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/signal.h

Purpose: defines Xtensa UAPI signal numbers, signal-set layout, action/restorer ABI, realtime bounds, stack sizes, and `stack_t`. Important constants include `_NSIG`, `_NSIG_BPW`, `_NSIG_WORDS`, traditional signal numbers 1-31, `SIGRTMIN`, `SIGRTMAX`, `SA_RESTORER`, `MINSIGSTKSZ`, and `SIGSTKSZ`.

Control flow is in generic signal/syscall code and architecture signal frame code. Persistent state includes user signal masks, sigaction tables, altstack state, and signal frames. Dependencies include `linux/types.h`, generic signal defs, and `__kernel_size_t`. Integration points are libc, `sigaction`, `rt_sigprocmask`, signal delivery/return, strace, and debuggers. Risks are ABI incompatibility with libc, signal number mismatches, insufficient signal stack size for extended registers, and restorer handling. Test signals include signal selftests, realtime signals, altstack/nested handlers, libc compatibility, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sockios.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sockios.h

Purpose: defines Xtensa socket ioctl numbers for ownership, out-of-band mark checks, process group control, and old timestamp ioctls. Important constants are `FIOGETOWN`, `FIOSETOWN`, `SIOCATMARK`, `SIOCSPGRP`, `SIOCGPGRP`, `SIOCGSTAMP_OLD`, and `SIOCGSTAMPNS_OLD`.

Control flow is ioctl command dispatch in socket/file layers. Persistent state affected includes socket owner, process group, and timestamp copyout behavior. Dependencies include `asm/ioctl.h`, `pid_t`, and socket timestamp compatibility code. Integration points are libc socket APIs, networking stack, legacy applications, and strace. Risks are ABI-number mismatch or old timestamp layout compatibility bugs. Test signals include socket ioctl tests, `SIOCATMARK` behavior, timestamp ioctl compatibility, headers_install, and strace decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sockios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/stat.h

Purpose: defines Xtensa UAPI `struct stat` and `struct stat64` layouts and sets `STAT_HAVE_NSEC`. Fields cover device/inode, mode/link count, uid/gid, rdev, size, block size/count, atime/mtime/ctime with nanoseconds, and padding.

Control flow is syscall copyout/copyin through stat-family syscalls. Persistent state represented is filesystem inode metadata in user ABI buffers. Dependencies include kernel syscall wants in `asm/unistd.h` and generic VFS stat conversion. Integration points are libc `stat`, old/new/stat64 syscalls, filesystems, tar/core utilities, and strace. Risks are structure layout ABI stability, 32-bit time range constraints, and inconsistency between `stat` and `stat64`. Test signals include stat syscall tests, large file tests, nanosecond timestamp checks, structure offset validation, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/swab.h

Purpose: provides Xtensa inline byte-swap primitives for UAPI/headers. Important APIs are `__arch_swab32` and `__arch_swab16`, with `__SWAB_64_THRU_32__` indicating 64-bit swaps can compose from 32-bit swaps.

Control flow is inline assembly using Xtensa shift/align instructions. Persistent state is none beyond returned values. Dependencies include `linux/types.h`, compiler inline asm behavior, and Xtensa ISA support. Integration points are endian conversion helpers, networking/filesystems/userspace headers, and compiler inlining. Risks include compiler differences for 16-bit return masking, incorrect asm constraints, and use on non-Xtensa toolchains. Test signals include byteorder unit tests, big/little endian builds, userspace header compile tests, and compiler comparison for generated code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/types.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/types.h

Purpose: defines Xtensa UAPI integer type inclusion and unsigned-long literal helpers. It includes `asm-generic/int-ll64.h` and provides `__XTENSA_UL` and `__XTENSA_UL_CONST` variants for assembler vs C.

Control flow is preprocessor-only. State is ABI type sizing and constant expression typing in exported headers. Dependencies include generic int-ll64 type definitions and assembler/C compilation contexts. Integration points are all UAPI headers needing fixed-width integer types or Xtensa unsigned long constants, including page/MM constants. Risks are literal suffix misuse in assembler, type-size ABI mismatches, and empty non-assembler extension block suggesting future expansion points. Test signals include headers_install, C and assembler preprocessing, userspace compile tests, and ABI type-size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/unistd.h

Purpose: includes generated 32-bit Xtensa syscall numbers and defines Xtensa-specific `sysxtensa` operation numbers. Important definitions are `__ARCH_WANT_SYS_OLDUMOUNT`, `SYS_XTENSA_RESERVED`, `SYS_XTENSA_ATOMIC_SET`, `SYS_XTENSA_ATOMIC_EXG_ADD`, `SYS_XTENSA_ATOMIC_ADD`, `SYS_XTENSA_ATOMIC_CMP_SWP`, and `SYS_XTENSA_COUNT`.

Control flow is executed in `entry.S` fast syscall handling when `__NR_xtensa` is invoked; operation number in `a6` selects atomic user memory operations using pointer/value registers. Persistent state affected is user memory targeted by atomic operations. Dependencies include generated `asm/unistd_32.h`, uaccess/fault handling, and syscall table generation. Integration points are libc/syscall wrappers, legacy Xtensa atomic ABI, seccomp, strace, and fast syscall path. Risks are atomicity/fault semantics, operation number ABI stability, and mismatch between header and fast handler. Test signals include generated syscall header checks, `sysxtensa` atomic operation tests, invalid op tests, user fault tests, and strace/seccomp decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/Makefile

Purpose: controls Xtensa kernel object composition and custom linker-script preprocessing. It always builds core objects such as `head.o`, `align.o`, `coprocessor.o`, `entry.o`, `irq.o`, `platform.o`, `process.o`, `ptrace.o`, `setup.o`, `signal.o`, `stacktrace.o`, `syscall.o`, `time.o`, `traps.o`, and `vectors.o`, with config-gated objects for MMU DMA, PCI, modules, ftrace, SMP, secondary reset vector, perf, hardware breakpoints, S32C1I selftest, jump labels, and hibernation.

Control flow is Kbuild-driven. The notable custom rule preprocesses `vmlinux.lds.S` and runs sed substitutions so Xtensa `.literal` sections are grouped before matching `.text` sections, satisfying L32R's limited relative range. Persistent state is build artifacts and generated `vmlinux.lds`. Dependencies include Kbuild variables, CPP, sed, linker script layout, and Xtensa literal constraints. Integration points are kernel image linking, conditional feature objects, and module/perf/SMP support. Risks are sed expression fragility, missing object for enabled feature, and literal/text separation causing link/runtime failures. Test signals include full kernel builds across config matrix, linker map inspection, and booting images with large text/literal placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/align.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/align.S

Purpose: implements fast handlers for unaligned and load/store exceptions, including instruction decoding, endian-aware data assembly, optional user MMU access checks, emulated loads/stores, loop register adjustment, and fixup fallback. Important entry points are `fast_load_store`, `fast_unaligned`, and `fast_unaligned_fixup`; helper labels include `.Lsave_and_load_instruction`, `.Lload_table`, `.Lstore_table`, `.Linvalid_instruction`, and `.Lexit`.

Control flow saves scratch registers in `pt_regs`, fetches the faulting instruction from EPC1, decodes narrow and regular load/store opcodes, reconstructs data across aligned words, writes the destination register slot or stores a masked value back to memory, advances PC, adjusts loop count if needed, clears `EXC_TABLE_FIXUP`, and returns with `rfe`. Invalid or faulting cases restore state and jump to user/kernel default exception paths; fixup restores after double exceptions. State includes `pt_regs`, SAR, EPC1, LCOUNT/LBEG/LEND, `EXC_TABLE_FIXUP`, and user/kernel memory. Dependencies include assembler access_ok, page/MMU config, endian macros, exception offsets, and Xtensa density/window features. Integration points are trap dispatch table, `uaccess`, page fault handling, and load-store emulation configs. Risks are instruction decoder gaps, table register mapping errors for a1 comments marked "fishy", user access double faults, and loop/single-step PC accounting. Test signals include unaligned load/store tests, MMU fault injection during emulation, endian builds, density instruction tests, and single-step/loop instruction cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/align.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/asm-offsets.c

Purpose: generates assembler constants for C structure offsets and sizes consumed by Xtensa assembly. It emits offsets for `struct pt_regs`, `task_struct`, `thread_info`, `mm_struct`, `page`, clone flags, debug/exception tables, and hibernation `pbe` fields.

Control flow is build-time: `main()` calls `DEFINE`/`OFFSET` macros from `linux/kbuild.h`, and generated output becomes `asm-offsets.h`. Persistent state is generated headers, not runtime data. Dependencies include `asm/processor.h`, `asm/coprocessor.h`, Linux task/mm/ptrace/suspend/uaccess headers, and config-gated fields. Integration points are `entry.S`, `align.S`, `coprocessor.S`, `head.S`, hibernation assembly, and trap/debug table access. Risks are missing offsets for fields used by assembly, typo `TI_STSTUS` preserving a generated symbol spelling, config mismatch, and structure layout changes without rebuild. Test signals include clean builds for feature matrix, assembler compile success, runtime exception/context switch correctness, and hibernation build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/coprocessor.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/coprocessor.S

Purpose: implements lazy coprocessor context switching for Xtensa configurations with coprocessors. Important symbols include generated save/load stubs for CP0-CP7, `.Lcp_regs_jump_table`, `fast_coprocessor`, and `coprocessor_flush`.

Control flow in `fast_coprocessor` handles disabled-coprocessor exceptions: it checks whether a task's coprocessor state is live on another CPU, falls back to C exception handling when cross-CPU flush is needed, saves scratch registers, enables the requested CP bit, finds the prior owner in per-CPU `exc_table`, records the new owner and owner CPU, saves previous owner state if present, loads current task state, then restores registers and returns. `coprocessor_flush` explicitly saves one coprocessor by table lookup. Persistent state includes `thread_info.cpenable`, `cp_owner_cpu`, per-task `xtregs_cp`, and per-CPU `exc_table.coprocessor_owner`. Dependencies include XCHAL coprocessor macros, offsets, SMP memory barriers, and `cpenable`. Integration points are `process.c` flush/release APIs, ptrace TIE regsets, context switch, trap dispatch, and hibernation. Risks are SMP ownership races, missing `memw` ordering, table offset mismatch, and unsupported coprocessor count/layout. Test signals include coprocessor-using userspace across task switches and CPU migration, ptrace XTREGS, exec/exit flush, and SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/coprocessor.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/entry.S

Purpose: core Xtensa low-level runtime assembly for exceptions, syscall entry/exit, fast faults, context switch, fork returns, debug exceptions, register-window spill, and hibernation suspend/resume. Important entry points include `user_exception`, `kernel_exception`, `common_exception_return`, `debug_exception`, `unrecoverable_exception`, `fast_alloca`, `fast_illegal_instruction_user`, `fast_syscall_user`, `fast_syscall_xtensa`, `fast_syscall_spill_registers`, `fast_second_level_miss`, `fast_store_prohibited`, `system_call`, `_switch_to`, `ret_from_fork`, `ret_from_kernel_thread`, `swsusp_arch_suspend`, and `swsusp_arch_resume`.

Control flow saves user or kernel register-window state into `pt_regs`, records special registers and exception cause, masks interrupts appropriately, dispatches via `exc_table.default_handler`, then loops over thread flags for reschedule, signals, notify-resume, trace/audit/seccomp, preemption, context tracking, debug-breakpoint restoration, and optional TLB sanity before restoring state and returning with `rfe`/`rfde`. Fast paths handle sysxtensa atomics, register spills, second-level TLB misses by installing page-directory translations, writable PTE faults by setting dirty/accessed/hw-write bits, and alloca/window exceptions. `_switch_to` saves previous thread RA/SP, user Xtensa regs, stack canary, CPENABLE, exclusive monitor state, spills windows, updates exception kernel stack, restores next state, and returns. Persistent state includes `pt_regs`, thread flags, `thread_struct`, `thread_info`, `exc_table`, TLB entries, PTEs, debug registers, and hibernation saved registers/page copies. Dependencies are generated offsets, Xtensa ABI/window config, `pgtable.h`, `tlbflush.h`, syscall table, trap/debug tables, coprocessor state, and scheduler helpers. Integration points cover nearly all arch runtime: traps, MMU, scheduler, ptrace/audit/seccomp/tracing, signals, perf/hw breakpoints, hibernation, and SMP. Risks are severe: register save/restore asymmetry, stale fixup handlers, double-exception handling, wrong syscall argument mapping, TLB/PTE synchronization, memory ordering for CPENABLE, leaking user registers, and ABI-specific frame bugs. Test signals include boot, syscall/ptrace/seccomp/audit tests, signal return, fork/kernel threads, preemption/SMP stress, page fault/COW/store faults, TLB miss stress, debug watchpoints, hibernation, and windowed/call0 ABI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/head.S

Purpose: Xtensa primary boot entry and early CPU initialization. Important symbols are `_start`, `_SetupOCD`, `_SetupMMU`, `_startup`, optional `cpu_restart`, `start_info`, and `swapper_pg_dir`.

Control flow preserves boot parameters in `excsave1`, initializes register windows and PS, optionally initializes MMU inside vmlinux, jumps to `_startup`, sets `vecbase`, clears debug/timer/coprocessor state, invalidates caches and initializes cache attributes, sets initial stack and PS, handles primary vs secondary CPU path, copies relocated data sections, clears BSS, flushes/invalidate caches, passes boot params to `init_arch`, and calls `start_kernel`. SMP secondary path waits for `cpu_start_ccount`, sets CCOUNT, and calls `secondary_start_kernel`. Hotplug `cpu_restart` flushes caches, coordinates with `cpu_start_id`, then restarts startup. Persistent state includes boot params, special registers, caches, BSS/data, `start_info`, and `swapper_pg_dir`. Dependencies include cache/MMU macros, linker symbols, XCHAL config, SMP MX registers, and kernel stack layout. Integration points are reset vector, linker script, setup, SMP bringup, MMU/cache init, and page-table bootstrap. Risks are literal placement, cache coherency before executing relocated code, boot param remapping, incorrect initial PS/window state, and SMP handoff races. Test signals include boot on MMU/noMMU/XIP/SMP variants, BSS/data integrity, early console, secondary CPU startup, and hotplug restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/hibernate.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/hibernate.c

Purpose: supplies minimal Xtensa hibernation helpers. Important APIs are `pfn_is_nosave`, `save_processor_state`, and `restore_processor_state`.

Control flow: `pfn_is_nosave` compares a PFN against `__nosave_begin`/`__nosave_end`; `save_processor_state` asserts only one CPU is online and flushes/releases local coprocessors when present; `restore_processor_state` is empty because assembly handles register restore. Persistent state is hibernation nosave range and coprocessor memory save areas. Dependencies include Linux suspend types, MM helpers, `__nosave_*` section symbols, and coprocessor support. Integration points are swsusp core, `entry.S` hibernation assembly, CPU hotplug/offline requirements, and coprocessor lazy state. Risks are incomplete processor-state restoration, failing to quiesce SMP, and lost live coprocessor state. Test signals include hibernate/resume, nosave range validation, coprocessor workload across hibernation, and WARN_ON for multi-CPU suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/hibernate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/hw_breakpoint.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/hw_breakpoint.c

Purpose: implements Xtensa hardware instruction breakpoints and data watchpoints through perf/hw_breakpoint. Important APIs include `hw_breakpoint_slots`, `arch_check_bp_in_kernelspace`, `hw_breakpoint_arch_parse`, `hw_breakpoint_exceptions_notify`, `arch_install_hw_breakpoint`, `arch_uninstall_hw_breakpoint`, `hw_breakpoint_pmu_read`, `flush_ptrace_hw_breakpoint`, `clear_ptrace_hw_breakpoint`, `restore_dbreak`, and `check_hw_breakpoint`.

Control flow parses perf attributes into Xtensa breakpoint type/length/address, allocates per-CPU IBREAK/DBREAK slots, writes special registers, disables/uninstalls slots, flushes ptrace-owned events on exec/exit, restores disabled data breakpoints after kernel-side hits, and handles debug exceptions by matching `DEBUGCAUSE` bits and reporting perf breakpoint events. Persistent state includes per-CPU `bp_on_reg`/`wp_on_reg`, task `thread.ptrace_bp/wp`, special IBREAK/DBREAK registers, and `TIF_DB_DISABLED`. Dependencies include configured breakpoint counts, `asm/regs.h`, `processor.h`, perf events, and ptrace. Integration points are `ptrace.c`, `entry.S` debug exception path, perf hw_breakpoint core, and scheduler return-to-user work. Risks are limited hardcoded switch support for at most two break/watch registers, kernel watchpoint recursion, address/length alignment, and per-CPU slot lifetime. Test signals include perf breakpoint tests, ptrace hardware breakpoint tests, user/kernel watchpoint hits, CPU migration, and invalid length/alignment cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/hw_breakpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/irq.c

Purpose: handles Xtensa interrupt dispatch, IRQ domain translation/mapping, interrupt display, legacy/OF IRQ controller initialization, external IRQ numbering, and hotplug IRQ migration. Important APIs are `do_IRQ`, `arch_show_interrupts`, `xtensa_irq_domain_xlate`, `xtensa_irq_map`, `xtensa_map_ext_irq`, `xtensa_get_ext_irq_no`, `init_IRQ`, and `migrate_irqs`.

Control flow sends hardware IRQs to `generic_handle_domain_irq`, reports SMP IPI and fake-NMI counters, translates device-tree interrupt specs, assigns generic handlers based on XCHAL interrupt type masks, initializes either OF irqchips or legacy PIC/MX controllers, initializes IPIs under SMP, and moves IRQ affinities off offline CPUs. Persistent state includes irq domains, irq descriptors, per-CPU NMI counts, affinity masks, and controller state. Dependencies include irqchip drivers, XCHAL masks, OF, SMP/IPI code, and `asm/traps.h`. Integration points are exception entry interrupt path, generic IRQ subsystem, device tree, `/proc/interrupts`, SMP hotplug, and timer/profiling interrupts. Risks include bad type mapping, invalid external IRQ translation, stack overflow under IRQ, and affinity migration races. Test signals include interrupt boot/probe, `/proc/interrupts`, device IRQs, timer IRQ, SMP IPI counters, and CPU hotplug with active IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/jump_label.c

Purpose: implements Xtensa static key/jump label patching. Important functions are `arch_jump_label_transform`, `patch_text`, `patch_text_stop_machine`, and `local_patch_text`; constants encode endian-specific jump and NOP instructions.

Control flow computes relative jump displacement, verifies it fits the 128 KiB Xtensa jump range, encodes either a J instruction or NOP, and patches text. SMP uses `stop_machine_cpuslocked`; the last arriving CPU patches and flushes local icache while other CPUs wait and invalidate their icaches. UP disables local interrupts around the patch. Persistent state is executable kernel text and per-patch atomic synchronization. Dependencies include `linux/jump_label.h`, stop_machine, cacheflush, CPU hotplug locking, and endianness. Integration points are static branches, tracepoints, scheduler/static key users, and text patching. Risks are out-of-range jumps, endian encoding errors, icache coherency, and patching while CPUs execute target text. Test signals include jump label selftests, static branch toggling under SMP load, ftrace/static key users, and big/little endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/mcount.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/mcount.S

Purpose: provides Xtensa ftrace `_mcount` and `ftrace_stub`. It checks `ftrace_trace_function`, returns if it points to the stub, otherwise computes caller and parent IPs and calls the active tracer.

Control flow differs by ABI. Windowed ABI uses `abi_entry_default`, reconstructs IPs from return-address encodings relative to stack pointer, subtracts `MCOUNT_INSN_SIZE`, and calls through `callx4`. Call0 ABI preserves caller argument and callee-saved registers on a local frame, passes adjusted caller IP, calls the tracer with `callx0`, then restores registers. Persistent state is none except ftrace global function pointer and caller stack/register state. Dependencies include `asm/asmmacro.h`, `asm/ftrace.h`, ABI macros, and ftrace core. Integration points are function tracer, dynamic tracing, profiling, and module instrumentation. Risks are register clobbering, wrong callsite IP reconstruction, ABI-specific frame size mistakes, and recursion if stub checks fail. Test signals include function graph/function tracer enablement, both ABI builds, module tracing, and tracer stress under interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/mcount.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/module.c

Purpose: applies Xtensa ELF relocations for loadable modules. Important functions are `decode_calln_opcode`, `decode_l32r_opcode`, and `apply_relocate_add`.

Control flow iterates relocation entries, computes symbol plus addend, and handles no-op/diff/asm-expand relocations, absolute `R_XTENSA_32`/PLT relocations, and `R_XTENSA_SLOT0_OP` for calln and L32R instruction fields with endian-specific byte patching and range validation. FLIX and ALT slot relocations, unknown relocations, and out-of-range operands fail with `-ENOEXEC`. Persistent state is patched module text/data in memory. Dependencies include ELF relocation constants, module loader, endianness, and Xtensa instruction encoding. Integration points are kernel module loading, vermagic, exported symbols, and instruction literal/call range constraints. Risks include silently ignoring unexpected SLOT0 opcodes due to assembler relaxation assumptions, range failures for far calls/literals, unaligned patch writes, and endian bugs. Test signals include loading modules with calls/literals, relocation failure tests, big/little endian builds, and modpost/objdump verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/mxhead.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/mxhead.S

Purpose: provides the secondary reset vector for Xtensa MX/SMP configurations. Important symbol is `_SecondaryResetVector`, with local setup labels `_SetupOCD` and `_SetupMMU`.

Control flow jumps from the secondary reset vector to OCD/window/PS setup, optionally initializes the MMU inside vmlinux, sets boot parameter register `a2` to NULL, loads `_startup`, and jumps there. Persistent state initialized includes window registers, PS interrupt level, MMU mappings, and secondary boot register arguments. Dependencies include cache/MMU initialization macros, MX registers, XCHAL window support, and `_startup` from `head.S`. Integration points are SMP secondary CPU bringup, reset-vector linker sections, and platform/MX boot hardware. Risks are vector placement, inconsistent setup relative to primary `_start`, missing MMU initialization, and literal-range constraints in reset-vector text. Test signals include SMP boot with `CONFIG_SECONDARY_RESET_VECTOR`, secondary CPU online, vector map inspection, and CPU hotplug restart paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/mxhead.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/pci-dma.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/pci-dma.c

Purpose: implements Xtensa DMA cache maintenance and coherent mapping helpers for MMU systems. Important functions are `do_cache_op`, `arch_sync_dma_for_cpu`, `arch_sync_dma_for_device`, `arch_dma_prep_coherent`, and `arch_dma_set_uncached`.

Control flow maps a physical DMA range to virtual addresses, using direct mapping for normal pages and `kmap_atomic` for highmem pages, then invokes cache invalidate or flush callbacks by DMA direction. CPU sync invalidates for bidirectional/from-device; device sync flushes writeback caches for bidirectional/to-device; coherent prep invalidates; MMU uncached conversion offsets from cached to bypass KSEG. Persistent state affected is data cache content and virtual address mapping used for coherent DMA. Dependencies include DMA map ops, highmem, cacheflush, page/phys mapping, and Xtensa KSEG layout. Integration points are PCI/device DMA mapping, coherent allocations, cache alias handling, and platform noMMU overrides. Risks are highmem page iteration/off-by-offset bugs, missing writeback flush, wrong uncached address translation, and `DMA_NONE` BUG. Test signals include DMA API debug, PCI device IO, highmem DMA tests, bidirectional buffer coherency, and cache writeback configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/pci-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/pci.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/pci.c

Purpose: provides Xtensa PCI resource alignment, bus fixup, and IO BAR mmap support. Important functions are `pcibios_align_resource`, `pcibios_fixup_bus`, and `pci_iobar_pfn`.

Control flow aligns IO resources to avoid low-10-bit aliasing with ISA-like devices, delegates memory resource alignment to generic PCI logic, reads bridge bases for subordinate buses, and adjusts VMA page offset for `/proc/bus/pci` IO BAR mappings using controller IO space offsets. Persistent state affected includes PCI resource assignments, bridge windows, and mmap VMA offsets. Dependencies include `asm/pci-bridge.h`, PCI core, resource flags, and platform controller data. Integration points are PCI enumeration, resource allocation, procfs PCI mmap, and device drivers. Risks are IO resource overlarge warnings without hard failure, bad controller `sysdata`, offset arithmetic errors, and legacy IO mirroring assumptions. Test signals include PCI enumeration/resource logs, devices behind bridges, procfs BAR mmap, and resource alignment inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/perf_event.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/perf_event.c

Purpose: implements Xtensa PMU support for perf hardware, cache, and raw events plus perf callchains. Important APIs include `xtensa_pmu_cache_event`, PMU register read/write helpers, `xtensa_perf_event_update`, `xtensa_perf_event_set_period`, `xtensa_pmu_enable/disable`, `xtensa_pmu_event_init`, `xtensa_pmu_start/stop/add/del/read`, `perf_callchain_kernel`, `perf_callchain_user`, `perf_event_print_debug`, `xtensa_pmu_irq_handler`, `xtensa_pmu_setup`, and `xtensa_pmu_init`.

Control flow maps perf configs to PMCTRL bitfields, allocates per-CPU counters, writes negative periods for overflow sampling, enables/disables PMG, updates software counts from hardware deltas, handles overflow IRQs by clearing PMSTAT and calling `perf_event_overflow`, initializes counters on CPU hotplug, and registers the PMU early. Persistent state includes per-CPU event arrays/used masks, hardware PM registers, perf event counts, and IRQ mapping. Dependencies include external register access, profiling interrupt, stacktrace callbacks, perf core, IRQ domain, and XCHAL counter count/version. Integration points are perf stat/record, scheduler perf context, fake NMI vs IRQ handling, and callchain unwinding. Risks include unsupported event mappings, raw config validation gaps, counter overflow period math, CPU hotplug cleanup, and fake-NMI IRQ ownership. Test signals include `perf stat`, sampling `perf record`, cache event validation, PMU overflow IRQs, CPU hotplug, and callchain tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/perf_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/platform.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/platform.c

Purpose: supplies weak default implementations for platform hooks declared in `asm/platform.h`. Important functions are weak `platform_init`, `platform_setup`, `platform_idle`, and optional `platform_calibrate_ccount`.

Control flow is intentionally minimal: init/setup defaults do nothing, idle executes `waiti 0` then returns to arch idle code, and fallback clock calibration logs an error and assumes 10 MHz when `CONFIG_XTENSA_CALIBRATE_CCOUNT` is enabled. Persistent state affected only by calibration fallback, which writes `ccount_freq`. Dependencies include `linux/printk.h`, units, `asm/timex.h`, and platform override linkage. Integration points are boot setup, idle loop, time initialization, and board code. Risks are silent missing platform setup, incorrect fallback timer frequency, and idle behavior unsuitable for some platforms. Test signals include boot logs for calibration fallback, idle/resume behavior, platform override symbol checks, and timekeeping accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/process.c

Purpose: implements Xtensa process/thread lifecycle, coprocessor state management, idle behavior, fork setup, and wait-channel lookup. Important APIs include `local_coprocessors_flush_release_all`, `coprocessor_release_all`, `coprocessor_flush_all`, `coprocessor_flush_release_all`, `arch_cpu_idle`, `exit_thread`, `flush_thread`, `arch_dup_task_struct`, `copy_thread`, and `__get_wchan`; it also exports `pm_power_off` and optional `__stack_chk_guard`.

Control flow flushes/releases live coprocessor state via local callbacks or SMP calls to owner CPU, idles through platform code, releases state on exit/exec, duplicates task structs after flushing source coprocessors, and builds child kernel stack/register frames for user clones or kernel threads. `copy_thread` handles CLONE_VM register-window hazards by resetting child window metadata and, for vfork-like same-stack cases, spilling caller stack pointer. Persistent state includes task `thread.ra/sp`, pt_regs child frame, thread_info coprocessor fields, TLS threadptr, ptrace breakpoints, and stack canary globals. Dependencies include scheduler, ptrace, hw breakpoints, coprocessors, ABI mode, uaccess, and `entry.S` fork return labels. Integration points are fork/clone/vfork, exec, scheduler switch, idle loop, ptrace, and coprocessor lazy switching. Risks are register-window stack corruption, SMP coprocessor memory ordering, TLS setup, breakpoint inheritance, and wchan stack bounds. Test signals include fork/clone/vfork/kthread tests, exec flushing, TLS tests, ptrace breakpoint inheritance, coprocessor migration, and scheduler wait-channel output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/ptrace.c

Purpose: implements Xtensa ptrace regsets, legacy ptrace requests, hardware breakpoint ptrace access, and syscall tracing hooks. Important functions are `gpr_get`, `gpr_set`, `tie_get`, `tie_set`, `task_user_regset_view`, `user_enable_single_step`, `user_disable_single_step`, `ptrace_disable`, `ptrace_getregs/setregs`, `ptrace_getxregs/setxregs`, `ptrace_peekusr`, `ptrace_pokeusr`, hardware breakpoint helpers, `arch_ptrace`, `do_syscall_trace_enter`, and `do_syscall_trace_leave`.

Control flow rotates internal register windows into user-visible order for GPR reads, validates and writes PC/PS/window state on set, flushes coprocessors before exposing or replacing TIE/coprocessor state, maps legacy PEEK/POKE register numbers, creates/modifies ptrace hardware breakpoints through perf, dispatches arch-specific ptrace requests, and handles syscall entry/exit tracing with seccomp, tracepoints, audit, single-step, and `NO_SYSCALL`. Persistent state includes task `pt_regs`, thread_info TIE/coprocessor save areas, task thread breakpoint arrays, TIF flags, and syscall return register. Dependencies include regset API, uaccess, perf/hw_breakpoint, seccomp/audit/security, tracepoints, ELF definitions, and Xtensa ptrace UAPI. Integration points are gdb/strace, core dumps, syscall tracing, signal stops, hardware breakpoints, and coprocessor state. Risks include register-window mask reconstruction, user-provided invalid PS/window state, large XTREGS allocation failures, breakpoint control-word validation, and syscall cancellation semantics. Test signals include gdb/strace, PTRACE_GET/SETREGS/GETXTREGS, syscall trace/seccomp/audit tests, hardware breakpoints, and core dump regset validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/s32c1i_selftest.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/s32c1i_selftest.c

Purpose: early self-test for Xtensa `S32C1I` atomic compare-and-swap support. Important functions are `probed_compare_swap`, `do_probed_exception`, and `check_s32c1i`.

Control flow for capable cores installs temporary trap handlers for load/store error causes, probes a non-storing compare-swap and a storing compare-swap while recording exception PC/cause, validates return value and memory behavior, panics on inconsistent or unsupported exception behavior, restores original handlers, and runs as an `early_initcall`. For cores without `XCHAL_HAVE_S32C1I`, it warns that atomic CAS support is absent. Persistent state includes initdata probe word, probe PC, exception cause, and temporarily replaced trap handlers. Dependencies include `asm/traps.h`, `scompare1`, exception cause constants, and early trap setup. Integration points are atomic/cmpxchg correctness, bringup diagnostics, and trap handler replacement. Risks are panic during boot on cores where S32C1I traps, incomplete handler restoration if panic occurs, and early exception handling fragility. Test signals include boot logs, successful early initcall, intentional unsupported-core warning, and atomic operation stress after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/s32c1i_selftest.c -->
