# subset-b-000740 Research

Grouped source research for subset B work item `subset-b-000740`. Each source file section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/stackframe.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/stackframe.h

## Purpose

`stackframe.h` defines the assembly macros used by MIPS exception and interrupt entry code to build, save, and restore `pt_regs` stack frames.

## Important APIs, Types, And Functions

Key APIs are assembly macros such as `SAVE_SOME`, `SAVE_ALL`, `RESTORE_SOME`, `RESTORE_ALL`, `SAVE_TEMP`, `SAVE_STATIC`, `SAVE_AT`, `RESTORE_TEMP`, `RESTORE_STATIC`, and `get_saved_sp`/`set_saved_sp`; they encode register save slots, CFI annotations, kernel stack selection, CP0 status/cause capture, and CPU-specific HI/LO or Octeon multiplier handling. Includes: `linux/threads.h`, `asm/asm.h`, `asm/asmmacro.h`, `asm/mipsregs.h`, `asm/asm-offsets.h`, `asm/thread_info.h`. Macros/constants: `_ASM_STACKFRAME_H`, `STATMASK`.

## Control Flow

Entry code expands these macros at trap boundaries: detect whether the trap came from user or kernel mode, switch to the per-CPU kernel stack when needed, allocate `PT_SIZE`, save GPRs, CP0 state, EPC, BADVADDR, and optional scratch state, then later restore status and GPRs before returning through the low-level exception path.

## State And Persistence

State is transient CPU register state stored in the current kernel stack's `pt_regs`; the only persistent architectural state it touches is per-CPU `kernelsp` and CP0 state. There is no filesystem persistence.

## Dependencies And Integration Points

It depends on `asm-offsets.h`, `mipsregs.h`, `thread_info.h`, CPU errata config, EVA handling, SMP CPU-id storage, and entry assembly. It integrates directly with exception handlers, signal delivery, ptrace, unwinding, FPU emulation, and low-level return-to-user code.

## Risks

Risks are catastrophic register corruption, bad `pt_regs` offsets, broken CFI unwinding, incorrect user/kernel stack switching, or CPU-errata workaround regressions.

## Test Signals

Test signals are boot-to-user, syscall/interrupt/fault stress, ptrace and signal tests, oops backtraces, SMP bring-up, EVA builds, Octeon builds, and objdump checks against generated offsets.
Static review signal: this source currently has 496 lines and 11140 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/stackframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/stackprotector.h

## Purpose

`stackprotector.h` provides MIPS GCC stack protector guard initialization.

## Important APIs, Types, And Functions

`boot_init_stack_canary()` seeds `current->stack_canary` from `get_random_canary()` and publishes it to the global `__stack_chk_guard`, which is the symbol GCC expects on MIPS. Macros/constants: `_ASM_STACKPROTECTOR_H`. Functions/prototypes/helpers: `boot_init_stack_canary`, `get_random_canary`.

## Control Flow

The helper is called from non-returning early/thread setup paths and must remain always-inline so the compiler cannot emit protected prologue/epilogue code around canary initialization.

## State And Persistence

The persistent state is the per-task `stack_canary` plus the architecture-wide global `__stack_chk_guard`; MIPS cannot use distinct per-task guards for GCC's global guard model on SMP.

## Dependencies And Integration Points

It integrates with `CONFIG_STACKPROTECTOR`, task setup, random canary generation, and compiler-emitted `__stack_chk_fail` checks.

## Risks

Risks are predictable canaries, calling from a returning protected function, and SMP-wide guard reuse.

## Test Signals

Test signals are stack-protector boot builds, forced stack-smash tests, and inspection that early init paths call the helper before protected code returns.
Static review signal: this source currently has 35 lines and 1022 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/stacktrace.h

## Purpose

`stacktrace.h` declares MIPS stack unwind interfaces and provides `prepare_frametrace()` for synthesizing a `pt_regs` snapshot of the current register file.

## Important APIs, Types, And Functions

Important APIs are `unwind_stack()`, `unwind_stack_by_address()`, `raw_show_trace`, and `prepare_frametrace()`; helper macros stringify MIPS load/store mnemonics to save registers through inline assembly. Includes: `asm/ptrace.h`, `asm/asm.h`, `linux/stringify.h`. Macros/constants: `_ASM_STACKTRACE_H`, `raw_show_trace`, `STR_PTR_LA`, `STR_LONG_S`, `STR_LONG_L`, `STR_LONGSIZE`, `STORE_ONE_REG`. Types/enums/unions: `task_struct`, `pt_regs`. Functions/prototypes/helpers: `unwind_stack`, `unwind_stack_by_address`, `prepare_frametrace`.

## Control Flow

When KALLSYMS is available the unwind functions are implemented elsewhere; otherwise they degrade to raw trace behavior. `prepare_frametrace()` stores the current PC and registers into caller-supplied `pt_regs`.

## State And Persistence

State is only the caller-owned register snapshot; no persistent kernel state is modified.

## Dependencies And Integration Points

It integrates with oops reporting, stack dump code, kallsyms-aware unwinding, raw backtraces, and architecture register layout.

## Risks

Risks are wrong register slot arithmetic, clobbering `$1`, misleading traces without KALLSYMS, and 32/64-bit load-store mismatch.

## Test Signals

Test signals are `show_stack()`, oops dumps, panic traces, and kallsyms-off builds.
Static review signal: this source currently has 90 lines and 2199 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/string.h

## Purpose

`string.h` selects MIPS architecture implementations for the core memory routines.

## Important APIs, Types, And Functions

The API is `__HAVE_ARCH_MEMSET`, `__HAVE_ARCH_MEMCPY`, `__HAVE_ARCH_MEMMOVE` plus prototypes for `memset()`, `memcpy()`, and `memmove()`. Macros/constants: `_ASM_STRING_H`, `__HAVE_ARCH_MEMSET`, `__HAVE_ARCH_MEMCPY`, `__HAVE_ARCH_MEMMOVE`. Functions/prototypes/helpers: `memset`, `memcpy`, `memmove`.

## Control Flow

There is no local control flow; generic string callers bind to MIPS implementations compiled elsewhere.

## State And Persistence

No state is persisted here; runtime behavior is in the selected assembly/C string routines.

## Dependencies And Integration Points

It integrates with libc-like kernel string operations, optimized MIPS memory copy code, and generic string fallback selection.

## Risks

Risks are ABI/prototype mismatch or selecting broken optimized routines.

## Test Signals

Test signals are lib/string tests, boot memory initialization, KASAN/KMSAN builds where available, and unaligned/overlap copy cases.
Static review signal: this source currently has 23 lines and 692 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/switch_to.h

## Purpose

`switch_to.h` defines MIPS scheduler context-switch orchestration around the low-level `resume()` assembly routine.

## Important APIs, Types, And Functions

Key APIs are `switch_to()`, `resume()`, LL/SC clearing helpers, FPU-affinity cleanup, `__sanitize_fcr31()`, DSP/COP2 save-restore hooks, userlocal register reload, and watch-register restoration. Includes: `asm/cpu-features.h`, `asm/watch.h`, `asm/dsp.h`, `asm/cop2.h`, `asm/fpu.h`. Macros/constants: `_ASM_SWITCH_TO_H`, `__mips_mt_fpaff_switch_to`, `__clear_r5_hw_ll_bit`, `__clear_software_ll_bit`, `__sanitize_fcr31`, `switch_to`. Types/enums/unions: `task_struct`, `thread_info`. Functions/prototypes/helpers: `resume`, `task_thread_info`, `clear_ti_thread_flag`, `write_c0_lladdr`, `mask_fcr31_x`, `force_fcr31_sig`, `__mips_mt_fpaff_switch_to`, `lose_fpu_inatomic`, `__sanitize_fcr31`, `__save_dsp`, `__restore_dsp`, `read_c0_status`, `set_c0_status`, `cop2_save`, `cop2_restore`, `write_c0_status`, `__clear_r5_hw_ll_bit`, `__clear_software_ll_bit`, `__restore_watch`.

## Control Flow

On a context switch the macro handles FPU ownership, optional FPU-affinity mask relaxation, pending FCSR exception signaling, DSP and COP2 state save/restore, hardware and software LL-bit clearing, user TLS reload through CP0 UserLocal, hardware watchpoint restoration, then calls `resume(prev,next,next_ti)`.

## State And Persistence

State includes per-task FPU/DSP/COP2/watch/TLS fields, global software LL state (`ll_bit`, `ll_task`), CP0 UserLocal, and scheduler-visible CPU masks. No filesystem persistence exists.

## Dependencies And Integration Points

It depends on CPU feature detection, `watch.h`, DSP/COP2/FPU helpers, `thread_info`, task register state, and scheduler switch semantics.

## Risks

Risks include leaked FPU/COP2/DSP state between tasks, incorrect LL/SC semantics after context switch, spurious or missed FP exceptions, lost TLS, and watchpoint misprogramming.

## Test Signals

Test signals are context-switch stress, FP/DSP/MSA workloads, ptrace watchpoints, MIPS MT FPU affinity tests, and LL/SC atomic stress.
Static review signal: this source currently has 143 lines and 4455 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sync.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sync.h

## Purpose

`sync.h` centralizes MIPS `sync` instruction types, reasons, and assembly emission macros for memory ordering.

## Important APIs, Types, And Functions

Important APIs are `__SYNC_full`, `__SYNC_rmb`, `__SYNC_wmb`, `__SYNC_ginv`, reason bits such as `__SYNC_weak_ordering`, and emitters `__SYNC()`/`__SYNC_ELSE()`. Macros/constants: `__MIPS_ASM_SYNC_H__`, `__SYNC_none`, `__SYNC_full`, `__SYNC_aq`, `__SYNC_rl`, `__SYNC_mb`, `__SYNC_rmb`, `__SYNC_wmb`, `__SYNC_ginv`, `__SYNC_always`, `__SYNC_weak_ordering`, `__SYNC_weak_llsc`, `__SYNC_loongson3_war`, `__SYNC_rpt`, `____SYNC`, `___SYNC`, `__SYNC`, `__SYNC_ELSE`. Functions/prototypes/helpers: `__SYNC_rpt`.

## Control Flow

The macros expand in C inline asm or assembly files to conditionally emit the correct `sync` subtype, including Octeon double-WMB behavior and Loongson3 LL/SC errata barriers.

## State And Persistence

No kernel state is stored; state is hardware memory-ordering effects and instruction stream selection.

## Dependencies And Integration Points

It integrates with barriers, atomics, LL/SC loops, cache/TLB global invalidation, and CPU errata workarounds.

## Risks

Risks are under-barriering SMP/device interactions, over-barriering performance regressions, or bad assembler-time expression behavior.

## Test Signals

Test signals are LKMM/atomic litmus tests, locktorture, DMA ordering tests, Octeon and Loongson builds, and objdump validation of emitted syncs.
Static review signal: this source currently has 210 lines and 7824 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/syscall.h

## Purpose

`syscall.h` implements the MIPS `asm-generic/syscall.h` accessors for syscall tracing, audit, seccomp, ptrace, and restart logic.

## Important APIs, Types, And Functions

Important helpers include `mips_syscall_is_indirect()`, `syscall_get_nr()`, `syscall_set_nr()`, `mips_syscall_update_nr()`, argument get/set helpers, return/error accessors, `syscall_get_arguments()`, `syscall_set_arguments()`, and `syscall_get_arch()`. Includes: `linux/compiler.h`, `uapi/linux/audit.h`, `linux/elf-em.h`, `linux/kernel.h`, `linux/sched.h`, `linux/uaccess.h`, `asm/ptrace.h`, `asm/unistd.h`. Macros/constants: `__ASM_MIPS_SYSCALL_H`, `__NR_syscall`. Types/enums/unions: `task_struct`, `pt_regs`. Functions/prototypes/helpers: `mips_syscall_is_indirect`, `syscall_get_nr`, `syscall_set_nr`, `mips_syscall_update_nr`, `mips_get_syscall_arg`, `mips_set_syscall_arg`, `syscall_get_error`, `syscall_get_return_value`, `syscall_rollback`, `syscall_set_return_value`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_arch`.

## Control Flow

The accessors read and update syscall number/arguments in `pt_regs` and `thread_info->syscall`, including O32 indirect `syscall()` handling where the real syscall number moves from `v0` to `a0` and 32-bit arguments may live in `regs->args`.

## State And Persistence

State is per-task syscall number in `thread_info`, `pt_regs` argument/return registers, and audit architecture flags; no persistent storage is used.

## Dependencies And Integration Points

It integrates with syscall entry/exit assembly, seccomp, audit, tracepoints, ptrace, compat ABIs, and syscall tables for O32/N32/N64.

## Risks

Risks are ABI-specific argument corruption, incorrect indirect syscall rewriting, wrong audit arch for endian/N32/N64, and broken seccomp/ptrace replay.

## Test Signals

Test signals are syscall tracing tests, seccomp user-notify/filter tests, audit arch checks, O32/N32/N64 compat syscall suites, and strace comparisons.
Static review signal: this source currently has 188 lines and 4588 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/syscalls.h

## Purpose

`syscalls.h` declares MIPS-specific syscall entry points and compat syscall shims.

## Important APIs, Types, And Functions

The APIs include signal-return trampolines, `sysm_pipe()`, MIPS MT affinity syscalls, O32/N32 signal returns, and 32-bit argument-splitting wrappers for fallocate, fadvise, readahead, and sync_file_range. Includes: `linux/linkage.h`, `linux/compat.h`. Macros/constants: `_ASM_MIPS_SYSCALLS_H`. Functions/prototypes/helpers: `sys_sigreturn`, `sys_rt_sigreturn`, `sysm_pipe`, `mipsmt_sys_sched_setaffinity`, `mipsmt_sys_sched_getaffinity`, `sys32_fallocate`, `sys32_fadvise64_64`, `sys32_readahead`, `sys32_sync_file_range`, `sys32_rt_sigreturn`, `sys32_sigreturn`, `sys32_sigsuspend`, `sysn32_rt_sigreturn`.

## Control Flow

There is no local flow; syscall tables reference these prototypes and implementations elsewhere marshal ABI-specific register/stack arguments into generic kernel operations.

## State And Persistence

State is syscall-callsite state in `pt_regs` and user memory passed through `__user` pointers.

## Dependencies And Integration Points

It integrates with generated syscall tables, signal delivery, compat code, scheduler affinity, and large-file syscall wrappers.

## Risks

Risks are prototype/table mismatches, wrong 64-bit argument pairing on 32-bit ABIs, and signal-frame compatibility breaks.

## Test Signals

Test signals are syscall table builds, LTP syscall coverage, signal return tests, and 32-bit userspace compatibility.
Static review signal: this source currently has 34 lines and 1313 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/thread_info.h

## Purpose

`thread_info.h` defines low-level MIPS `thread_info`, stack sizing, thread flags, and fast current-thread access conventions.

## Important APIs, Types, And Functions

Important APIs are `struct thread_info`, `INIT_THREAD_INFO`, `current_thread_info()`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `STACK_WARN`, `TIF_*` and `_TIF_*` masks, syscall work masks, and SMP CPUID CP0 register constants. Includes: `asm/processor.h`. Macros/constants: `_ASM_THREAD_INFO_H`, `INIT_THREAD_INFO`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `THREAD_MASK`, `STACK_WARN`, `TIF_SIGPENDING`, `TIF_NEED_RESCHED`, `TIF_SYSCALL_AUDIT`, `TIF_SECCOMP`, `TIF_NOTIFY_RESUME`, `TIF_UPROBE`, `TIF_NOTIFY_SIGNAL`, `TIF_RESTORE_SIGMASK`, `TIF_USEDFPU`, `TIF_MEMDIE`, `TIF_NOHZ`, `TIF_FIXADE`, `TIF_LOGADE`, `TIF_32BIT_REGS`, `TIF_32BIT_ADDR`, `TIF_FPUBOUND`, `TIF_LOAD_WATCH`, `TIF_SYSCALL_TRACEPOINT`, `TIF_32BIT_FPREGS`, `TIF_HYBRID_FPREGS`, `TIF_USEDMSA`, `TIF_MSA_CTX_LIVE`, `TIF_SYSCALL_TRACE`, `_TIF_SYSCALL_TRACE`, `_TIF_SIGPENDING`, `_TIF_NEED_RESCHED`, `_TIF_SYSCALL_AUDIT`, `_TIF_SECCOMP`, and 26 more. Types/enums/unions: `should`, `shares`, `thread_info`, `task_struct`, `pt_regs`. Functions/prototypes/helpers: `current_thread_info`, `__asm__`.

## Control Flow

Entry assembly and C code find `thread_info` through `$28/$gp`, track preemption, pending work, syscall number, TLS, CPU, and saved regs, and use TIF masks to decide syscall-entry, syscall-exit, and return-to-user work.

## State And Persistence

State persists for each task on its kernel stack/supervisor stack area; flags and syscall fields change across scheduling, signal, syscall, FPU, watchpoint, and OOM paths.

## Dependencies And Integration Points

It integrates with exception entry, scheduler, syscall tracing, FPU/MSA state, watchpoints, CPU hotplug, VDSO build constraints, and generated assembly offsets.

## Risks

Risks are changing structure layout without regenerating offsets, flag-bit collisions, wrong stack size for page size/ABI, and `$gp` clobbering.

## Test Signals

Test signals are all MIPS builds, syscall/signal stress, preempt/debug builds, stack overflow warnings, and VDSO link checks.
Static review signal: this source currently has 198 lines and 6755 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/time.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/time.h

## Purpose

`time.h` defines MIPS timekeeping, clocksource, clockevent, and cycle-counter interfaces.

## Important APIs, Types, And Functions

The APIs include platform time init, R4K clockevent/clocksource initialization, CP0 compare/perf interrupt discovery, cycle reads, entropy reads, and timer frequency variables. Includes: `linux/rtc.h`, `linux/spinlock.h`, `linux/clockchips.h`, `linux/clocksource.h`. Macros/constants: `_ASM_TIME_H`. Types/enums/unions: `clock_event_device`. Functions/prototypes/helpers: `plat_time_init`, `get_c0_perfcount_int`, `get_c0_compare_int`, `r4k_clockevent_init`, `mips_clockevent_init`, `init_r4k_clocksource`, `init_mips_clocksource`, `clockevent_set_clock`, `clockevents_calc_mult_shift`.

## Control Flow

Boot/platform time code initializes board clocks, discovers compare/perf IRQs, registers clockevents and clocksources, and cycle readers fetch CP0 count when supported.

## State And Persistence

State is clock frequency, clocksource/event registration, CP0 Count/Compare hardware, and RTC lock-protected state.

## Dependencies And Integration Points

It integrates with generic timekeeping, clockevents, perf IRQ handling, platform `plat_time_init()`, R4K timer code, and random entropy hooks.

## Risks

Risks are wrong timer frequency, unusable counters on specific PRIDs, lost timer interrupts, and unstable entropy/cycles on suspended or virtualized systems.

## Test Signals

Test signals are boot clocksource selection, timer interrupt cadence, timekeeping selftests, perf interrupt tests, suspend/resume, and NTP/clock drift observation.
Static review signal: this source currently has 74 lines and 1624 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/timex.h

## Purpose

`timex.h` defines MIPS timekeeping, clocksource, clockevent, and cycle-counter interfaces.

## Important APIs, Types, And Functions

The APIs include platform time init, R4K clockevent/clocksource initialization, CP0 compare/perf interrupt discovery, cycle reads, entropy reads, and timer frequency variables. Includes: `linux/compiler.h`, `asm/cpu.h`, `asm/cpu-features.h`, `asm/mipsregs.h`, `asm/cpu-type.h`. Macros/constants: `_ASM_TIMEX_H`, `CLOCK_TICK_RATE`, `get_cycles`, `random_get_entropy`. Types/enums/unions: `cycles_t`. Functions/prototypes/helpers: `can_use_mips_counter`, `get_cycles`, `random_get_entropy`, `read_c0_count`.

## Control Flow

Boot/platform time code initializes board clocks, discovers compare/perf IRQs, registers clockevents and clocksources, and cycle readers fetch CP0 count when supported.

## State And Persistence

State is clock frequency, clocksource/event registration, CP0 Count/Compare hardware, and RTC lock-protected state.

## Dependencies And Integration Points

It integrates with generic timekeeping, clockevents, perf IRQ handling, platform `plat_time_init()`, R4K timer code, and random entropy hooks.

## Risks

Risks are wrong timer frequency, unusable counters on specific PRIDs, lost timer interrupts, and unstable entropy/cycles on suspended or virtualized systems.

## Test Signals

Test signals are boot clocksource selection, timer interrupt cadence, timekeeping selftests, perf interrupt tests, suspend/resume, and NTP/clock drift observation.
Static review signal: this source currently has 103 lines and 2938 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/tlb.h

## Purpose

`tlb.h` declares MIPS TLB management helpers and constants.

## Important APIs, Types, And Functions

The API covers local and SMP TLB flush prototypes, wired-entry helpers, debug dump hooks, runtime TLB handler generation, or unique EntryHi construction depending on the file. Includes: `asm/cpu-features.h`, `asm/mipsregs.h`, `asm-generic/tlb.h`. Macros/constants: `__ASM_TLB_H`, `_UNIQUE_ENTRYHI`, `UNIQUE_ENTRYHI`, `UNIQUE_GUEST_ENTRYHI`. Functions/prototypes/helpers: `num_wired_entries`, `read_c0_wired`.

## Control Flow

Callers flush all, mm, range, kernel-range, page, or single virtual-address TLB entries; TLB exception code may build refill handlers dynamically and wired-entry code reserves fixed TLB slots.

## State And Persistence

State is hardware TLB contents, wired-entry count, MM context IDs, generated handler code, and debug output; no filesystem persistence exists.

## Dependencies And Integration Points

It integrates with `mmu_context`, page fault handling, VM unmap/mprotect, SMP shootdowns, KVM/guest mappings where applicable, and low-level exception vectors.

## Risks

Risks are stale translations, missing SMP shootdowns, wrong wired count, TLB refill handler encoding errors, and debug-only code using unsafe register state.

## Test Signals

Test signals are mmap/munmap/mprotect stress, fork/exec, SMP TLB shootdown tests, highmem/cache alias cases, and boot on CPUs with varied TLB sizes.
Static review signal: this source currently has 27 lines and 613 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbdebug.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbdebug.h

## Purpose

`tlbdebug.h` declares MIPS TLB management helpers and constants.

## Important APIs, Types, And Functions

The API covers local and SMP TLB flush prototypes, wired-entry helpers, debug dump hooks, runtime TLB handler generation, or unique EntryHi construction depending on the file. Macros/constants: `__ASM_TLBDEBUG_H`. Functions/prototypes/helpers: `dump_tlb_regs`, `dump_tlb_all`.

## Control Flow

Callers flush all, mm, range, kernel-range, page, or single virtual-address TLB entries; TLB exception code may build refill handlers dynamically and wired-entry code reserves fixed TLB slots.

## State And Persistence

State is hardware TLB contents, wired-entry count, MM context IDs, generated handler code, and debug output; no filesystem persistence exists.

## Dependencies And Integration Points

It integrates with `mmu_context`, page fault handling, VM unmap/mprotect, SMP shootdowns, KVM/guest mappings where applicable, and low-level exception vectors.

## Risks

Risks are stale translations, missing SMP shootdowns, wrong wired count, TLB refill handler encoding errors, and debug-only code using unsafe register state.

## Test Signals

Test signals are mmap/munmap/mprotect stress, fork/exec, SMP TLB shootdown tests, highmem/cache alias cases, and boot on CPUs with varied TLB sizes.
Static review signal: this source currently has 18 lines and 403 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbex.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbex.h

## Purpose

`tlbex.h` declares MIPS TLB management helpers and constants.

## Important APIs, Types, And Functions

The API covers local and SMP TLB flush prototypes, wired-entry helpers, debug dump hooks, runtime TLB handler generation, or unique EntryHi construction depending on the file. Includes: `asm/uasm.h`. Macros/constants: `__ASM_TLBEX_H`. Types/enums/unions: `tlb_write_entry`, `uasm_label`, `uasm_reloc`. Functions/prototypes/helpers: `build_get_pmde64`, `build_get_pgde32`, `build_get_ptep`, `build_update_entries`, `build_tlb_write_entry`, `build_tlb_refill_handler`, `handle_tlbl`, `handle_tlbs`, `handle_tlbm`.

## Control Flow

Callers flush all, mm, range, kernel-range, page, or single virtual-address TLB entries; TLB exception code may build refill handlers dynamically and wired-entry code reserves fixed TLB slots.

## State And Persistence

State is hardware TLB contents, wired-entry count, MM context IDs, generated handler code, and debug output; no filesystem persistence exists.

## Dependencies And Integration Points

It integrates with `mmu_context`, page fault handling, VM unmap/mprotect, SMP shootdowns, KVM/guest mappings where applicable, and low-level exception vectors.

## Risks

Risks are stale translations, missing SMP shootdowns, wrong wired count, TLB refill handler encoding errors, and debug-only code using unsafe register state.

## Test Signals

Test signals are mmap/munmap/mprotect stress, fork/exec, SMP TLB shootdown tests, highmem/cache alias cases, and boot on CPUs with varied TLB sizes.
Static review signal: this source currently has 38 lines and 1014 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbflush.h

## Purpose

`tlbflush.h` declares MIPS TLB management helpers and constants.

## Important APIs, Types, And Functions

The API covers local and SMP TLB flush prototypes, wired-entry helpers, debug dump hooks, runtime TLB handler generation, or unique EntryHi construction depending on the file. Includes: `linux/mm.h`, `asm/mmu_context.h`. Macros/constants: `__ASM_TLBFLUSH_H`, `flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_range`, `flush_tlb_kernel_range`, `flush_tlb_page`, `flush_tlb_one`. Types/enums/unions: `vm_area_struct`, `mm_struct`. Functions/prototypes/helpers: `local_flush_tlb_all`, `local_flush_tlb_range`, `local_flush_tlb_kernel_range`, `local_flush_tlb_page`, `local_flush_tlb_one`, `flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_range`, `flush_tlb_kernel_range`, `flush_tlb_page`, `flush_tlb_one`.

## Control Flow

Callers flush all, mm, range, kernel-range, page, or single virtual-address TLB entries; TLB exception code may build refill handlers dynamically and wired-entry code reserves fixed TLB slots.

## State And Persistence

State is hardware TLB contents, wired-entry count, MM context IDs, generated handler code, and debug output; no filesystem persistence exists.

## Dependencies And Integration Points

It integrates with `mmu_context`, page fault handling, VM unmap/mprotect, SMP shootdowns, KVM/guest mappings where applicable, and low-level exception vectors.

## Risks

Risks are stale translations, missing SMP shootdowns, wrong wired count, TLB refill handler encoding errors, and debug-only code using unsafe register state.

## Test Signals

Test signals are mmap/munmap/mprotect stress, fork/exec, SMP TLB shootdown tests, highmem/cache alias cases, and boot on CPUs with varied TLB sizes.
Static review signal: this source currently has 50 lines and 1683 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbmisc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbmisc.h

## Purpose

`tlbmisc.h` declares MIPS TLB management helpers and constants.

## Important APIs, Types, And Functions

The API covers local and SMP TLB flush prototypes, wired-entry helpers, debug dump hooks, runtime TLB handler generation, or unique EntryHi construction depending on the file. Macros/constants: `__ASM_TLBMISC_H`. Functions/prototypes/helpers: `add_wired_entry`.

## Control Flow

Callers flush all, mm, range, kernel-range, page, or single virtual-address TLB entries; TLB exception code may build refill handlers dynamically and wired-entry code reserves fixed TLB slots.

## State And Persistence

State is hardware TLB contents, wired-entry count, MM context IDs, generated handler code, and debug output; no filesystem persistence exists.

## Dependencies And Integration Points

It integrates with `mmu_context`, page fault handling, VM unmap/mprotect, SMP shootdowns, KVM/guest mappings where applicable, and low-level exception vectors.

## Risks

Risks are stale translations, missing SMP shootdowns, wrong wired count, TLB refill handler encoding errors, and debug-only code using unsafe register state.

## Test Signals

Test signals are mmap/munmap/mprotect stress, fork/exec, SMP TLB shootdown tests, highmem/cache alias cases, and boot on CPUs with varied TLB sizes.
Static review signal: this source currently has 12 lines and 320 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbmisc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/topology.h

## Purpose

`topology.h` maps generic topology queries to MIPS `cpu_data`, sibling/core cpumasks, package/core IDs, and the primary-thread mask.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `topology.h`, `linux/smp.h`. Macros/constants: `__ASM_TOPOLOGY_H`, `topology_physical_package_id`, `topology_core_id`, `topology_core_cpumask`, `topology_sibling_cpumask`, `cpu_primary_thread_mask`. Types/enums/unions: `cpumask`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with scheduler topology, hotplug, and SMP sibling management.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 25 lines and 754 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/traps.h

## Purpose

`traps.h` declares MIPS trap, exception, NMI, EJTAG, bus-error, cache-error, and page-fault entry points plus board hook pointers.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Macros/constants: `_ASM_TRAPS_H`, `MIPS_BE_DISCARD`, `MIPS_BE_FIXUP`, `MIPS_BE_FATAL`, `VECTORSPACING`, `nmi_notifier`. Types/enums/unions: `pt_regs`, `notifier_block`. Functions/prototypes/helpers: `mips_set_be_handler`, `register_nmi_notifier`, `reserve_exception_space`, `do_ade`, `do_be`, `do_ov`, `do_fpe`, `do_bp`, `do_tr`, `do_ri`, `do_cpu`, `do_msa_fpe`, `do_msa`, `do_mdmx`, `do_watch`, `do_mcheck`, `do_mt`, `do_dsp`, `do_reserved`, `do_ftlb`, `do_gsexc`, `do_daddi_ov`, `do_page_fault`, `cache_parity_error`, `ejtag_exception_handler`, `nmi_exception_handler`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with exception vector setup, notifier chains, fault handling, and board firmware hooks.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 69 lines and 2443 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/boards.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/boards.h

## Purpose

`boards.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. This file is intentionally small and exposes only its include guard or build-list role.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 6 lines and 125 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/boards.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/dmac.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/dmac.h

## Purpose

`dmac.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Includes: `linux/dmaengine.h`. Macros/constants: `__ASM_TXX9_DMAC_H`, `TXX9_DMA_MAX_NR_CHANNELS`. Types/enums/unions: `txx9dmac_platform_data`, `txx9dmac_chan_platform_data`, `platform_device`, `txx9dmac_slave`. Functions/prototypes/helpers: `txx9_dmac_init`.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 49 lines and 1170 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/dmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/generic.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/generic.h

## Purpose

`generic.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Includes: `linux/init.h`, `linux/ioport.h`. Macros/constants: `__ASM_TXX9_GENERIC_H`, `TXX9_CE`, `TXX9_IMCLK`. Types/enums/unions: `resource`, `uart_port`, `pci_dev`, `txx9_board_vec`, `physmap_flash_data`. Functions/prototypes/helpers: `txx9_reg_res_init`, `early_serial_txx9_setup`, `txx9_wdt_init`, `txx9_wdt_now`, `txx9_spi_init`, `txx9_ethaddr_init`, `txx9_sio_init`, `txx9_sio_putchar_init`, `txx9_physmap_flash_init`, `__fls8`, `txx9_iocled_init`, `txx9_7segled_init`, `txx9_7segled_putc`, `txx9_aclc_init`, `txx9_sramc_init`, `prom_getenv`.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 99 lines and 2800 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/pci.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/pci.h

## Purpose

`pci.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Includes: `linux/pci.h`. Macros/constants: `__ASM_TXX9_PCI_H`, `TXX9_PCI_OPT_PICMG`, `TXX9_PCI_OPT_CLK_33`, `TXX9_PCI_OPT_CLK_66`, `TXX9_PCI_OPT_CLK_MASK`, `TXX9_PCI_OPT_CLK_AUTO`. Types/enums/unions: `pci_controller`, `txx9_pci_err_action`. Functions/prototypes/helpers: `txx9_alloc_pci_controller`, `txx9_pci66_check`, `txx9_pcibios_setup`.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 40 lines and 1147 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/rbtx4927.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/rbtx4927.h

## Purpose

`rbtx4927.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Includes: `asm/txx9/tx4927.h`. Macros/constants: `__ASM_TXX9_RBTX4927_H`, `RBTX4927_PCIMEM`, `RBTX4927_PCIMEM_SIZE`, `RBTX4927_PCIIO`, `RBTX4927_PCIIO_SIZE`, `RBTX4927_LED_ADDR`, `RBTX4927_IMASK_ADDR`, `RBTX4927_IMSTAT_ADDR`, `RBTX4927_SOFTINT_ADDR`, `RBTX4927_SOFTRESET_ADDR`, `RBTX4927_SOFTRESETLOCK_ADDR`, `RBTX4927_PCIRESET_ADDR`, `RBTX4927_BRAMRTC_BASE`, `RBTX4927_ETHER_BASE`, `RBTX4927_ETHER_ADDR`, `rbtx4927_imask_addr`, `rbtx4927_imstat_addr`, `rbtx4927_softint_addr`, `rbtx4927_softreset_addr`, `rbtx4927_softresetlock_addr`, `rbtx4927_pcireset_addr`, `RBTX4927_INTB_PCID`, `RBTX4927_INTB_PCIC`, `RBTX4927_INTB_PCIB`, `RBTX4927_INTB_PCIA`, `RBTX4927_INTF_PCID`, `RBTX4927_INTF_PCIC`, `RBTX4927_INTF_PCIB`, `RBTX4927_INTF_PCIA`, `RBTX4927_NR_IRQ_IOC`, `RBTX4927_IRQ_IOC`, `RBTX4927_IRQ_IOC_PCID`, `RBTX4927_IRQ_IOC_PCIC`, `RBTX4927_IRQ_IOC_PCIB`, and 5 more. Types/enums/unions: `pci_dev`. Functions/prototypes/helpers: `rbtx4927_prom_init`, `rbtx4927_irq_setup`, `rbtx4927_pci_map_irq`.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 93 lines and 3914 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/rbtx4927.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/smsc_fdc37m81x.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/smsc_fdc37m81x.h

## Purpose

`smsc_fdc37m81x.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Macros/constants: `_SMSC_FDC37M81X_H_`, `SMSC_FDC37M81X_CONFIG_INDEX`, `SMSC_FDC37M81X_CONFIG_DATA`, `SMSC_FDC37M81X_CONF`, `SMSC_FDC37M81X_INDEX`, `SMSC_FDC37M81X_DNUM`, `SMSC_FDC37M81X_DID`, `SMSC_FDC37M81X_DREV`, `SMSC_FDC37M81X_PCNT`, `SMSC_FDC37M81X_PMGT`, `SMSC_FDC37M81X_OSC`, `SMSC_FDC37M81X_CONFPA0`, `SMSC_FDC37M81X_CONFPA1`, `SMSC_FDC37M81X_TEST4`, `SMSC_FDC37M81X_TEST5`, `SMSC_FDC37M81X_TEST1`, `SMSC_FDC37M81X_TEST2`, `SMSC_FDC37M81X_TEST3`, `SMSC_FDC37M81X_FDD`, `SMSC_FDC37M81X_PARALLEL`, `SMSC_FDC37M81X_SERIAL1`, `SMSC_FDC37M81X_SERIAL2`, `SMSC_FDC37M81X_KBD`, `SMSC_FDC37M81X_AUXIO`, `SMSC_FDC37M81X_NONE`, `SMSC_FDC37M81X_ACTIVE`, `SMSC_FDC37M81X_BASEADDR0`, `SMSC_FDC37M81X_BASEADDR1`, `SMSC_FDC37M81X_INT`, `SMSC_FDC37M81X_INT2`, `SMSC_FDC37M81X_LDCR_F0`, `SMSC_FDC37M81X_CONFIG_ENTER`, `SMSC_FDC37M81X_CONFIG_EXIT`, `SMSC_FDC37M81X_CHIP_ID`. Functions/prototypes/helpers: `smsc_fdc37m81x_init`, `smsc_fdc37m81x_config_beg`, `smsc_fdc37m81x_config_end`, `smsc_fdc37m81x_config_set`, `smsc_fdc37m81x_config_get`.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 69 lines and 2142 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/smsc_fdc37m81x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/tx4927.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/tx4927.h

## Purpose

`tx4927.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Includes: `linux/types.h`, `linux/io.h`, `asm/txx9irq.h`, `asm/txx9/tx4927pcic.h`. Macros/constants: `__ASM_TXX9_TX4927_H`, `TX4927_REG_BASE`, `TX4927_REG_SIZE`, `TX4927_SDRAMC_REG`, `TX4927_EBUSC_REG`, `TX4927_DMA_REG`, `TX4927_PCIC_REG`, `TX4927_CCFG_REG`, `TX4927_IRC_REG`, `TX4927_NR_TMR`, `TX4927_TMR_REG`, `TX4927_NR_SIO`, `TX4927_SIO_REG`, `TX4927_PIO_REG`, `TX4927_ACLC_REG`, `TX4927_IR_ECCERR`, `TX4927_IR_WTOERR`, `TX4927_NUM_IR_INT`, `TX4927_IR_INT`, `TX4927_NUM_IR_SIO`, `TX4927_IR_SIO`, `TX4927_NUM_IR_DMA`, `TX4927_IR_DMA`, `TX4927_IR_PIO`, `TX4927_IR_PDMAC`, `TX4927_IR_PCIC`, `TX4927_NUM_IR_TMR`, `TX4927_IR_TMR`, `TX4927_IR_PCIERR`, `TX4927_IR_PCIPME`, `TX4927_IR_ACLC`, `TX4927_IR_ACLCPME`, `TX4927_NUM_IR`, `TX4927_IRC_INT`, and 92 more. Types/enums/unions: `tx4927_sdramc_reg`, `tx4927_ebusc_reg`, `tx4927_ccfg_reg`, `tx4927_pcic_reg`, `txx9_pio_reg`. Functions/prototypes/helpers: `txx9_clear64`, `txx9_set64`, `tx4927_ccfg_clear`, `tx4927_ccfg_set`, `tx4927_ccfg_change`, `tx4927_get_mem_size`, `tx4927_wdt_init`, `tx4927_setup`, `tx4927_time_init`, `tx4927_sio_init`, `tx4927_report_pciclk`, `tx4927_pciclk66_setup`, `tx4927_setup_pcierr_irq`, `tx4927_irq_init`, `tx4927_mtd_init`, `tx4927_dmac_init`, `tx4927_aclc_init`, `local_irq_save`, `local_irq_restore`.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 274 lines and 9261 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/tx4927.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/tx4927pcic.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/tx4927pcic.h

## Purpose

`tx4927pcic.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Includes: `linux/pci.h`, `linux/irqreturn.h`. Macros/constants: `__ASM_TXX9_TX4927PCIC_H`, `TX4927_PCIC_G2PSTATUS_ALL`, `TX4927_PCIC_G2PSTATUS_TTOE`, `TX4927_PCIC_G2PSTATUS_RTOE`, `TX4927_PCIC_PCISTATUS_ALL`, `TX4927_PCIC_PBACFG_FIXPA`, `TX4927_PCIC_PBACFG_RPBA`, `TX4927_PCIC_PBACFG_PBAEN`, `TX4927_PCIC_PBACFG_BMCEN`, `TX4927_PCIC_PBASTATUS_ALL`, `TX4927_PCIC_PBASTATUS_BM`, `TX4927_PCIC_G2PMnGBASE_BSDIS`, `TX4927_PCIC_G2PMnGBASE_ECHG`, `TX4927_PCIC_G2PIOGBASE_BSDIS`, `TX4927_PCIC_G2PIOGBASE_ECHG`, `TX4927_PCIC_PCICSTATUS_ALL`, `TX4927_PCIC_PCICSTATUS_PME`, `TX4927_PCIC_PCICSTATUS_TLB`, `TX4927_PCIC_PCICSTATUS_NIB`, `TX4927_PCIC_PCICSTATUS_ZIB`, `TX4927_PCIC_PCICSTATUS_PERR`, `TX4927_PCIC_PCICSTATUS_SERR`, `TX4927_PCIC_PCICSTATUS_GBE`, `TX4927_PCIC_PCICSTATUS_IWB`, `TX4927_PCIC_PCICSTATUS_E2PDONE`, `TX4927_PCIC_PCICCFG_GBWC_MASK`, `TX4927_PCIC_PCICCFG_HRST`, `TX4927_PCIC_PCICCFG_SRST`, `TX4927_PCIC_PCICCFG_IRBER`, `TX4927_PCIC_PCICCFG_G2PMEN`, `TX4927_PCIC_PCICCFG_G2PM0EN`, `TX4927_PCIC_PCICCFG_G2PM1EN`, `TX4927_PCIC_PCICCFG_G2PM2EN`, `TX4927_PCIC_PCICCFG_G2PIOEN`, and 50 more. Types/enums/unions: `tx4927_pcic_reg`, `pci_controller`. Functions/prototypes/helpers: `tx4927_pcic_setup`, `tx4927_report_pcic_status`, `tx4927_dump_pcic_settings`, `get_tx4927_pcicptr`, `tx4927_pcibios_setup`, `tx4927_pcierr_interrupt`.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 204 lines and 6534 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/tx4927pcic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/tx4938.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/tx4938.h

## Purpose

`tx4938.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Includes: `asm/txx9/tx4927.h`. Macros/constants: `__ASM_TXX9_TX4938_H`, `TX4938_REG_BASE`, `TX4938_REG_SIZE`, `TX4938_NDFMC_REG`, `TX4938_SRAMC_REG`, `TX4938_PCIC1_REG`, `TX4938_SDRAMC_REG`, `TX4938_EBUSC_REG`, `TX4938_DMA_REG`, `TX4938_PCIC_REG`, `TX4938_CCFG_REG`, `TX4938_NR_TMR`, `TX4938_TMR_REG`, `TX4938_NR_SIO`, `TX4938_SIO_REG`, `TX4938_PIO_REG`, `TX4938_IRC_REG`, `TX4938_ACLC_REG`, `TX4938_SPI_REG`, `TX4938_IR_ECCERR`, `TX4938_IR_WTOERR`, `TX4938_NUM_IR_INT`, `TX4938_IR_INT`, `TX4938_NUM_IR_SIO`, `TX4938_IR_SIO`, `TX4938_NUM_IR_DMA`, `TX4938_IR_DMA`, `TX4938_IR_PIO`, `TX4938_IR_PDMAC`, `TX4938_IR_PCIC`, `TX4938_NUM_IR_TMR`, `TX4938_IR_TMR`, `TX4938_IR_NDFMC`, `TX4938_IR_PCIERR`, and 167 more. Types/enums/unions: `tx4938_sramc_reg`, `tx4938_ccfg_reg`, `tx4927_pcic_reg`, `txx9_pio_reg`, `pci_dev`, `tx4938ide_platform_info`. Functions/prototypes/helpers: `tx4938_wdt_init`, `tx4938_setup`, `tx4938_time_init`, `tx4938_sio_init`, `tx4938_spi_init`, `tx4938_ethaddr_init`, `tx4938_report_pciclk`, `tx4938_report_pci1clk`, `tx4938_pciclk66_setup`, `tx4938_pcic1_map_irq`, `tx4938_setup_pcierr_irq`, `tx4938_irq_init`, `tx4938_mtd_init`, `tx4938_ndfmc_init`, `tx4938_ata_init`, `tx4938_dmac_init`, `tx4938_aclc_init`, `tx4938_sramc_init`.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 313 lines and 10991 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/tx4938.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9irq.h

## Purpose

`txx9irq.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Includes: `irq.h`. Macros/constants: `__ASM_TXX9IRQ_H`, `TXX9_IRQ_BASE`, `TXx9_MAX_IR`. Functions/prototypes/helpers: `txx9_irq_init`, `txx9_irq`, `txx9_irq_set_pri`.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 31 lines and 682 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9pio.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9pio.h

## Purpose

`txx9pio.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Includes: `linux/types.h`. Macros/constants: `__ASM_TXX9PIO_H`. Types/enums/unions: `txx9_pio_reg`. Functions/prototypes/helpers: `txx9_gpio_init`.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 30 lines and 592 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9pio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9tmr.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9tmr.h

## Purpose

`txx9tmr.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Includes: `linux/types.h`. Macros/constants: `__ASM_TXX9TMR_H`, `TXx9_TMTCR_TCE`, `TXx9_TMTCR_CCDE`, `TXx9_TMTCR_CRE`, `TXx9_TMTCR_ECES`, `TXx9_TMTCR_CCS`, `TXx9_TMTCR_TMODE_MASK`, `TXx9_TMTCR_TMODE_ITVL`, `TXx9_TMTCR_TMODE_PGEN`, `TXx9_TMTCR_TMODE_WDOG`, `TXx9_TMTISR_TPIBS`, `TXx9_TMTISR_TPIAS`, `TXx9_TMTISR_TIIS`, `TXx9_TMITMR_TIIE`, `TXx9_TMITMR_TZCE`, `TXx9_TMWTMR_TWIE`, `TXx9_TMWTMR_WDIS`, `TXx9_TMWTMR_TWC`, `TXX9_TIMER_BITS`. Types/enums/unions: `txx9_tmr_reg`. Functions/prototypes/helpers: `txx9_clocksource_init`, `txx9_clockevent_init`, `txx9_tmr_init`.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 64 lines and 1560 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9tmr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/types.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/types.h

## Purpose

`types.h` selects MIPS type behavior by including the generic integer type definitions.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `asm-generic/int-ll64.h`. Macros/constants: `_ASM_TYPES_H`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with architecture UAPI/kernel type consistency.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 17 lines and 459 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/uaccess.h

## Purpose

`uaccess.h` implements MIPS user-memory access primitives and raw copy/string helpers.

## Important APIs, Types, And Functions

Important APIs are `put_user()`, `get_user()`, `__put_user()`, `__get_user()`, `raw_copy_from_user()`, `raw_copy_to_user()`, `clear_user()`, `strncpy_from_user()`, `strnlen_user()`, kernel nofault helpers, and exception-table-backed load/store assembly macros. Includes: `linux/kernel.h`, `linux/string.h`, `asm/asm-eva.h`, `asm/extable.h`, `asm-generic/access_ok.h`. Macros/constants: `_ASM_UACCESS_H`, `__UA_LIMIT`, `TASK_SIZE_MAX`, `__UA_ADDR`, `__UA_LA`, `__UA_ADDU`, `__UA_t0`, `__UA_t1`, `put_user`, `get_user`, `__put_user`, `__get_user`, `__m`, `__GET_DW`, `__get_data_asm`, `__get_data_asm_ll32`, `__get_kernel_nofault`, `__PUT_DW`, `__put_data_asm`, `__put_data_asm_ll32`, `__put_kernel_nofault`, `__MODULE_JAL`, `DADDI_SCRATCH`, `INLINE_COPY_FROM_USER`, `INLINE_COPY_TO_USER`, `bzero_clobbers`, `clear_user`. Types/enums/unions: `__large_struct`. Functions/prototypes/helpers: `__raw_copy_from_user`, `__raw_copy_to_user`, `raw_copy_from_user`, `raw_copy_to_user`, `__bzero`, `__clear_user`, `__strncpy_from_user_asm`, `strncpy_from_user`, `__strnlen_user_asm`, `strnlen_user`, `might_fault`, `__chk_user_ptr`, `__put_data_asm`, `__PUT_DW`, `BUILD_BUG`, `__asm__`.

## Control Flow

The macros check `access_ok()` for public helpers, execute EVA or normal user load/store instructions, and install `__ex_table` fixups that set `-EFAULT`, zero destinations where required, or return uncopied byte counts. Bulk copy jumps into assembly routines with ABI-fixed argument registers.

## State And Persistence

State is caller buffers, user memory, exception-table metadata, and residual counts/errors; no long-lived state is stored.

## Dependencies And Integration Points

It depends on `asm-eva.h`, `extable.h`, generic `access_ok`, module long-call handling, DADDI/EVA prefetch workarounds, and copy-user assembly implementations.

## Risks

Risks are security-critical: missing bounds checks, bad exception fixups, wrong register clobbers, data leaks on fault, residual-count errors, and module call range issues.

## Test Signals

Test signals are LTP uaccess/syscall tests, fault-injection into user copies, hardened usercopy, KASAN where available, 32/64-bit and EVA builds, and copy/string boundary tests.
Static review signal: this source currently has 565 lines and 15028 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/uasm.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/uasm.h

## Purpose

`uasm.h` declares the MIPS micro-assembler used to build runtime-generated instruction streams, especially TLB refill/fault handlers.

## Important APIs, Types, And Functions

The API is the large set of `uasm_i*` instruction emitters, label/relocation structs, `UASM_i_*` ABI-width aliases, safe 64-bit shift/rotate helpers, label builders, relocation movers, and labeled branch helpers. Includes: `linux/types.h`, `linux/export.h`. Macros/constants: `__ASM_UASM_H`, `UASM_EXPORT_SYMBOL`, `Ip_u1u2u3`, `Ip_u2u1u3`, `Ip_u3u2u1`, `Ip_u3u1u2`, `Ip_u1u2s3`, `Ip_u2s3u1`, `Ip_s3s1s2`, `Ip_u2u1s3`, `Ip_u2u1msbu3`, `Ip_u1u2`, `Ip_u2u1`, `Ip_u1s2`, `Ip_u1`, `Ip_0`, `UASM_L_LA`, `UASM_i_ADDIU`, `UASM_i_ADDU`, `UASM_i_LL`, `UASM_i_LW`, `UASM_i_LWX`, `UASM_i_MFC0`, `UASM_i_MTC0`, `UASM_i_ROTR`, `UASM_i_SC`, `UASM_i_SLL`, `UASM_i_SRA`, `UASM_i_SRL`, `UASM_i_SRL_SAFE`, `UASM_i_SUBU`, `UASM_i_SW`, `uasm_i_b`, `uasm_i_beqz`, and 8 more. Types/enums/unions: `uasm_label`, `uasm_reloc`. Functions/prototypes/helpers: `uasm_build_label`, `uasm_in_compat_space_p`, `uasm_rel_hi`, `uasm_rel_lo`, `UASM_i_LA_mostly`, `UASM_i_LA`, `uasm_i_drotr_safe`, `uasm_i_dsll_safe`, `uasm_i_dsrl_safe`, `uasm_i_dsra_safe`, `uasm_r_mips_pc16`, `uasm_resolve_relocs`, `uasm_move_relocs`, `uasm_move_labels`, `uasm_copy_handler`, `uasm_insn_has_bdelay`, `uasm_il_b`, `uasm_il_bbit0`, `uasm_il_bbit1`, `uasm_il_beq`, `uasm_il_beqz`, `uasm_il_beqzl`, `uasm_il_bgezl`, `uasm_il_bgez`, `uasm_il_bltz`, `uasm_il_bne`, `uasm_il_bnez`, `Ip_u2u1s3`, `Ip_u3u1u2`, `Ip_u2u1u3`, and 19 more.

## Control Flow

Callers append encoded instructions to a `u32 **buf`, place labels, record relocations, then resolve or copy handlers into final executable memory.

## State And Persistence

State is caller-owned instruction buffers plus label/relocation arrays; no global persistence except optional exported symbols when `CONFIG_EXPORT_UASM` is enabled.

## Dependencies And Integration Points

It integrates with TLB exception generation, CPU feature-dependent code emission, module exports, and instruction encoding definitions.

## Risks

Risks are bad instruction encoding, unresolved relocations, branch-delay-slot mistakes, 32/64-bit alias mismatch, or generating code unsupported by the target ISA.

## Test Signals

Test signals are boot TLB refill paths, objdump of generated handlers, QEMU/hardware boots across CPU revisions, and runtime TLB miss stress.
Static review signal: this source currently has 329 lines and 9664 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/uasm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/unaligned-emul.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/unaligned-emul.h

## Purpose

`unaligned-emul.h` provides byte-wise load/store macros for software emulation of unaligned MIPS memory accesses.

## Important APIs, Types, And Functions

Important APIs are `LoadHWU`, `LoadHWUE`, `LoadWU`, `LoadWUE`, `LoadHW`, `LoadHWE`, `LoadW`, `LoadWE`, `LoadDW`, `StoreHW`, `StoreHWE`, `StoreW`, `StoreWE`, and `StoreDW`; variants distinguish signed/unsigned, kernel/user access, word/doubleword, and endian order. Includes: `asm/asm.h`. Macros/constants: `_ASM_MIPS_UNALIGNED_EMUL_H`, `_LoadHW`, `_LoadW`, `_LoadHWU`, `_LoadWU`, `_LoadDW`, `_StoreHW`, `_StoreW`, `_StoreDW`, `LoadHWU`, `LoadHWUE`, `LoadWU`, `LoadWUE`, `LoadHW`, `LoadHWE`, `LoadW`, `LoadWE`, `LoadDW`, `StoreHW`, `StoreHWE`, `StoreW`, `StoreWE`, `StoreDW`.

## Control Flow

The macros build values one byte at a time using inline assembly, with exception-table fixups that set `-EFAULT` for user or kernel fault handling, then store back bytes in endian-correct order.

## State And Persistence

State is only the target memory value and result/error variable supplied by the caller.

## Dependencies And Integration Points

It integrates with address-error exception handling, `TIF_FIXADE`/`TIF_LOGADE`, user access helpers, endian macros, and FPU/instruction emulation paths that need safe unaligned reads.

## Risks

Risks are endian inversion, sign-extension errors, partial stores on fault, missing exception fixups, and 64-bit value corruption on 32-bit builds.

## Test Signals

Test signals are unaligned access emulation tests, big/little endian builds, user fault injection, and address-error signal behavior.
Static review signal: this source currently has 780 lines and 26856 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/unaligned-emul.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/unistd.h

## Purpose

`unistd.h` selects MIPS syscall-number ranges and generic syscall feature wants for O32, N32, and N64 ABIs.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `uapi/asm/unistd.h`, `asm/unistd_nr_n32.h`, `asm/unistd_nr_n64.h`, `asm/unistd_nr_o32.h`. Macros/constants: `_ASM_UNISTD_H`, `__NR_N32_Linux`, `__NR_64_Linux`, `__NR_O32_Linux`, `NR_syscalls`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_OLD_READDIR`, `__ARCH_WANT_SYS_ALARM`, `__ARCH_WANT_SYS_GETHOSTNAME`, `__ARCH_WANT_SYS_IPC`, `__ARCH_WANT_SYS_PAUSE`, `__ARCH_WANT_SYS_UTIME`, `__ARCH_WANT_SYS_UTIME32`, `__ARCH_WANT_SYS_WAITPID`, `__ARCH_WANT_SYS_SOCKETCALL`, `__ARCH_WANT_SYS_GETPGRP`, `__ARCH_WANT_SYS_NICE`, `__ARCH_WANT_SYS_OLD_UNAME`, `__ARCH_WANT_SYS_OLDUMOUNT`, `__ARCH_WANT_SYS_SIGPENDING`, `__ARCH_WANT_SYS_SIGPROCMASK`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_TIME32`, `__ARCH_WANT_COMPAT_STAT`, `__ARCH_WANT_SYS_FORK`, `__ARCH_WANT_SYS_CLONE`, `__IGNORE_fadvise64_64`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with generated syscall tables and generic syscall wrappers.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 68 lines and 1872 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/unroll.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/unroll.h

## Purpose

`unroll.h` provides a compile-time loop-unrolling macro for performance-critical paths such as string routines.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Macros/constants: `__ASM_UNROLL_H__`, `unroll`. Functions/prototypes/helpers: `bad_unroll`, `__compiletime_error`, `fn`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with optimized C loops and compiler-version portability.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 76 lines and 2860 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/unroll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/uprobes.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/uprobes.h

## Purpose

`uprobes.h` defines MIPS uprobes instruction storage, break opcodes, XOL slot size, and per-task uprobe state.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `linux/notifier.h`, `linux/types.h`, `asm/break.h`, `asm/inst.h`. Macros/constants: `__ASM_UPROBES_H`, `MAX_UINSN_BYTES`, `UPROBE_XOL_SLOT_BYTES`, `UPROBE_BRK_UPROBE`, `UPROBE_BRK_UPROBE_XOL`, `UPROBE_SWBP_INSN`, `UPROBE_SWBP_INSN_SIZE`. Types/enums/unions: `mips_instruction`, `arch_uprobe`, `arch_uprobe_task`, `uprobe_opcode_t`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with uprobes breakpoint insertion, branch-delay-slot handling, and trap return.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 46 lines and 1141 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/uprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso.h

## Purpose

`vdso.h` describes MIPS VDSO image metadata used by the kernel when mapping user VDSO pages and signal trampolines.

## Important APIs, Types, And Functions

Important API is `struct mips_vdso_image` plus `vdso_image`, `vdso_image_o32`, and `vdso_image_n32` declarations. Includes: `linux/mm_types.h`, `vdso/datapage.h`, `asm/barrier.h`. Macros/constants: `__ASM_VDSO_H`. Types/enums/unions: `mips_vdso_image`, `vm_special_mapping`.

## Control Flow

Runtime flow is in VDSO setup code: select the ABI-specific image, map its page-aligned data via `vm_special_mapping`, and use stored offsets for sigreturn trampolines.

## State And Persistence

Persistent state is static image metadata and runtime mapping descriptors; no filesystem state is involved.

## Dependencies And Integration Points

It integrates with exec, mmap special mappings, signal delivery, ABI selection, and generated VDSO artifacts.

## Risks

Risks are wrong ABI image selection, stale trampoline offsets, or non-page-aligned image sizes.

## Test Signals

Test signals are VDSO mapping inspection, signal return tests, O32/N32/N64 userspace, and `readelf`/symbol-offset validation.
Static review signal: this source currently has 54 lines and 1387 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/clocksource.h

## Purpose

`clocksource.h` provides MIPS VDSO architecture glue for generic VDSO code.

## Important APIs, Types, And Functions

The API consists of VDSO clock modes, data-page address helpers, processor relax behavior, or generic vsyscall inclusion points. Macros/constants: `__ASM_VDSOCLOCKSOURCE_H`, `VDSO_ARCH_CLOCKMODES`.

## Control Flow

Runtime flow occurs when VDSO userspace code reads the data page, mapped clocksource pages, or falls through to generic VDSO helpers; this header controls architecture-specific inline fragments.

## State And Persistence

State is VDSO data-page contents, optional GIC mapping, and CPU/hardware counter visibility.

## Dependencies And Integration Points

It integrates with generic VDSO timekeeping, MIPS VDSO link constraints, clocksource drivers, and userspace ABI mapping.

## Risks

Risks are illegal relocations in VDSO code, wrong page arithmetic, missing spin-loop barriers on affected CPUs, or unsupported clock mode exposure.

## Test Signals

Test signals are VDSO selftests, readelf relocation checks, clock_gettime monotonicity, and Loongson/GIC/R4K clocksource coverage.
Static review signal: this source currently has 10 lines and 225 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/gettimeofday.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/gettimeofday.h

## Purpose

`gettimeofday.h` implements MIPS VDSO time fallback syscalls and architecture counter readers for generic VDSO time code.

## Important APIs, Types, And Functions

Important APIs are `gettimeofday_fallback()`, `clock_gettime_fallback()`, `clock_getres_fallback()`, 32-bit time fallbacks, `read_r4k_count()`, `read_gic_count()`, `__arch_get_hw_counter()`, `mips_vdso_hres_capable()`, and `__arch_get_vdso_u_time_data()`. Includes: `asm/vdso/vdso.h`, `asm/clocksource.h`, `asm/unistd.h`, `asm/vdso.h`. Macros/constants: `__ASM_VDSO_GETTIMEOFDAY_H`, `VDSO_HAS_CLOCK_GETRES`, `VDSO_SYSCALL_CLOBBERS`, `__arch_vdso_hres_capable`, `__arch_get_vdso_u_time_data`. Types/enums/unions: `__kernel_old_timeval`, `timezone`, `__kernel_timespec`, `old_timespec32`, `vdso_time_data`. Functions/prototypes/helpers: `gettimeofday_fallback`, `clock_gettime_fallback`, `clock_getres_fallback`, `clock_gettime32_fallback`, `clock_getres32_fallback`, `mips_vdso_hres_capable`, `asm`, `get_gic`, `__raw_readl`, `read_r4k_count`, `read_gic_count`, `IS_ENABLED`, `get_vdso_time_data`.

## Control Flow

Fast paths read R4K `rdhwr` count or the GIC counter using stable hi/lo/hi reads. Unsupported or racing modes return 0 so generic VDSO code retries/falls back. Fallbacks invoke raw `syscall` with MIPS register conventions and translate the `a3` error flag.

## State And Persistence

State read includes VDSO data pages, optional mapped GIC counter page, hardware counters, and user output buffers.

## Dependencies And Integration Points

It integrates with generic `vdso/gettimeofday`, clocksource mode selection, syscall numbers, ABI64 versus time64 syscall selection, and MIPS clobber rules for HI/LO before ISA r6.

## Risks

Risks are wrong syscall number per ABI, missing clobbers, torn GIC counter reads, unsupported clock modes, and VDSO relocation/GOT use.

## Test Signals

Test signals are VDSO time selftests, 32-bit time64 tests, clocksource switching, strace fallback comparisons, and monotonicity checks.
Static review signal: this source currently has 221 lines and 5388 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/gettimeofday.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/processor.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/processor.h

## Purpose

`processor.h` provides MIPS VDSO architecture glue for generic VDSO code.

## Important APIs, Types, And Functions

The API consists of VDSO clock modes, data-page address helpers, processor relax behavior, or generic vsyscall inclusion points. Macros/constants: `__ASM_VDSO_PROCESSOR_H`, `cpu_relax`.

## Control Flow

Runtime flow occurs when VDSO userspace code reads the data page, mapped clocksource pages, or falls through to generic VDSO helpers; this header controls architecture-specific inline fragments.

## State And Persistence

State is VDSO data-page contents, optional GIC mapping, and CPU/hardware counter visibility.

## Dependencies And Integration Points

It integrates with generic VDSO timekeeping, MIPS VDSO link constraints, clocksource drivers, and userspace ABI mapping.

## Risks

Risks are illegal relocations in VDSO code, wrong page arithmetic, missing spin-loop barriers on affected CPUs, or unsupported clock mode exposure.

## Test Signals

Test signals are VDSO selftests, readelf relocation checks, clock_gettime monotonicity, and Loongson/GIC/R4K clocksource coverage.
Static review signal: this source currently has 28 lines and 747 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/vdso.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/vdso.h

## Purpose

`vdso.h` describes MIPS VDSO image metadata used by the kernel when mapping user VDSO pages and signal trampolines.

## Important APIs, Types, And Functions

Important API is `struct mips_vdso_image` plus `vdso_image`, `vdso_image_o32`, and `vdso_image_n32` declarations. Includes: `asm/sgidefs.h`, `vdso/page.h`, `asm/asm.h`, `asm/vdso.h`. Macros/constants: `__ASM_VDSO_VDSO_H`, `__VDSO_PAGES`. Types/enums/unions: `vdso_time_data`.

## Control Flow

Runtime flow is in VDSO setup code: select the ABI-specific image, map its page-aligned data via `vm_special_mapping`, and use stored offsets for sigreturn trampolines.

## State And Persistence

Persistent state is static image metadata and runtime mapping descriptors; no filesystem state is involved.

## Dependencies And Integration Points

It integrates with exec, mmap special mappings, signal delivery, ABI selection, and generated VDSO artifacts.

## Risks

Risks are wrong ABI image selection, stale trampoline offsets, or non-page-aligned image sizes.

## Test Signals

Test signals are VDSO mapping inspection, signal return tests, O32/N32/N64 userspace, and `readelf`/symbol-offset validation.
Static review signal: this source currently has 78 lines and 1795 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/vsyscall.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/vsyscall.h

## Purpose

`vsyscall.h` provides MIPS VDSO architecture glue for generic VDSO code.

## Important APIs, Types, And Functions

The API consists of VDSO clock modes, data-page address helpers, processor relax behavior, or generic vsyscall inclusion points. Includes: `asm/page.h`, `vdso/datapage.h`, `asm-generic/vdso/vsyscall.h`. Macros/constants: `__ASM_VDSO_VSYSCALL_H`.

## Control Flow

Runtime flow occurs when VDSO userspace code reads the data page, mapped clocksource pages, or falls through to generic VDSO helpers; this header controls architecture-specific inline fragments.

## State And Persistence

State is VDSO data-page contents, optional GIC mapping, and CPU/hardware counter visibility.

## Dependencies And Integration Points

It integrates with generic VDSO timekeeping, MIPS VDSO link constraints, clocksource drivers, and userspace ABI mapping.

## Risks

Risks are illegal relocations in VDSO code, wrong page arithmetic, missing spin-loop barriers on affected CPUs, or unsupported clock mode exposure.

## Test Signals

Test signals are VDSO selftests, readelf relocation checks, clock_gettime monotonicity, and Loongson/GIC/R4K clocksource coverage.
Static review signal: this source currently has 17 lines and 356 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vermagic.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/vermagic.h

## Purpose

`vermagic.h` builds MIPS module vermagic CPU-family and 32/64-bit tags.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Macros/constants: `_ASM_VERMAGIC_H`, `MODULE_PROC_FAMILY`, `MODULE_KERNEL_TYPE`, `MODULE_ARCH_VERMAGIC`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with module loader compatibility checks.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 67 lines and 2108 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vga.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/vga.h

## Purpose

`vga.h` maps VGA memory and endian-correct text-console buffer operations on MIPS.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `linux/string.h`, `asm/addrspace.h`, `asm/byteorder.h`. Macros/constants: `_ASM_VGA_H`, `VGA_MAP_MEM`, `vga_readb`, `vga_writeb`, `VT_BUF_HAVE_RW`, `VT_BUF_HAVE_MEMSETW`. Functions/prototypes/helpers: `scr_writew`, `scr_memsetw`, `cpu_to_le16`, `le16_to_cpu`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with VGA/MDA text console and legacy framebuffer paths.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 53 lines and 1142 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/video.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/video.h

## Purpose

`video.h` provides framebuffer pgprot and 64-bit raw framebuffer read/write helpers before including generic video helpers.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `asm/page.h`, `asm-generic/video.h`. Macros/constants: `_ASM_VIDEO_H_`, `pgprot_framebuffer`, `fb_readq`, `fb_writeq`. Functions/prototypes/helpers: `fb_writeq`, `pgprot_noncached`, `__raw_readq`, `__raw_writeq`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with framebuffer mmap and IO helpers.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 39 lines and 875 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/vmalloc.h

## Purpose

`vmalloc.h` is an empty MIPS vmalloc override header that defers behavior to generic code.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Macros/constants: `_ASM_MIPS_VMALLOC_H`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with vmalloc include plumbing.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 5 lines and 90 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vpe.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/vpe.h

## Purpose

`vpe.h` declares MIPS MT VPE loader state, thread-context state, control lists, file operations, notifications, memory allocation, and run/stop APIs.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `linux/init.h`, `linux/list.h`, `linux/smp.h`, `linux/spinlock.h`. Macros/constants: `_ASM_VPE_H`, `VPE_MODULE_NAME`, `VPE_MODULE_MINOR`, `P_SIZE`, `MAX_VPES`. Types/enums/unions: `vpe_state`, `tc_state`, `vpe`, `list_head`, `tc`, `vpe_notifications`, `vpe_control`, `file_operations`. Functions/prototypes/helpers: `aprp_cpu_index`, `vpe_notify`, `get_vpe`, `get_tc`, `alloc_vpe`, `alloc_tc`, `release_vpe`, `release_progmem`, `vpe_run`, `cleanup_tc`, `vpe_module_init`, `vpe_start`, `vpe_stop`, `vpe_free`, `vpe_get_shared`, `alloc_progmem`, `vpe_module_exit`, `vpe_alloc`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with VPE loader device, MIPS MT secondary execution, and module lifecycle.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 131 lines and 2783 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/vpe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/watch.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/watch.h

## Purpose

`watch.h` declares hardware watchpoint probing/install/clear helpers and `__restore_watch()` context-switch integration.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `linux/bitops.h`, `asm/mipsregs.h`. Macros/constants: `_ASM_WATCH_H`, `__restore_watch`. Types/enums/unions: `task_struct`, `cpuinfo_mips`. Functions/prototypes/helpers: `mips_install_watch_registers`, `mips_read_watch_registers`, `mips_clear_watch_registers`, `mips_probe_watch_registers`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with ptrace watchpoints and context switching.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 33 lines and 827 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/watch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/wbflush.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/wbflush.h

## Purpose

`wbflush.h` selects write-buffer flush behavior using a platform `__wbflush` hook or `fast_iob()` fallback.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Macros/constants: `_ASM_WBFLUSH_H`, `wbflush`, `wbflush_setup`. Functions/prototypes/helpers: `wbflush_setup`, `__sync`, `__wbflush`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with I/O ordering and platform setup.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 35 lines and 694 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/wbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/xtalk/xtalk.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/xtalk/xtalk.h

## Purpose

`xtalk.h` is a MIPS architecture support header.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Macros/constants: `_ASM_XTALK_XTALK_H`, `XWIDGET_NONE`, `XWIDGET_PART_NUM_NONE`, `XWIDGET_REV_NUM_NONE`, `XWIDGET_MFG_NUM_NONE`, `XIO_NOWHERE`, `XIO_ADDR_BITS`, `XIO_PORT_BITS`, `XIO_PORT_SHIFT`, `XIO_PACKED`, `XIO_ADDR`, `XIO_PORT`, `XIO_PACK`. Types/enums/unions: `xtalk_piomap_s`, `xwidgetnum_t`, `xwidget_part_num_t`, `xwidget_rev_num_t`, `xwidget_mfg_num_t`, `xtalk_piomap_t`.

## Control Flow

Control flow is implemented by files that include this header; this file contributes compile-time contracts, inline helpers, constants, or prototypes.

## State And Persistence

State is architecture or subsystem state owned by callers; no filesystem persistence is introduced here.

## Dependencies And Integration Points

It integrates with the MIPS architecture tree and generic kernel subsystem named by its declarations.

## Risks

Risks are build regressions, low-level ABI drift, and hardware-specific behavior changes.

## Test Signals

Test signals are MIPS builds, headers-install where applicable, and subsystem runtime coverage.
Static review signal: this source currently has 53 lines and 1531 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/xtalk/xtalk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/xtalk/xwidget.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/xtalk/xwidget.h

## Purpose

`xwidget.h` is a MIPS architecture support header.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `linux/types.h`, `asm/xtalk/xtalk.h`. Macros/constants: `_ASM_XTALK_XWIDGET_H`, `WIDGET_ID`, `WIDGET_STATUS`, `WIDGET_ERR_UPPER_ADDR`, `WIDGET_ERR_LOWER_ADDR`, `WIDGET_CONTROL`, `WIDGET_REQ_TIMEOUT`, `WIDGET_INTDEST_UPPER_ADDR`, `WIDGET_INTDEST_LOWER_ADDR`, `WIDGET_ERR_CMD_WORD`, `WIDGET_LLP_CFG`, `WIDGET_TFLUSH`, `WIDGET_REV_NUM`, `WIDGET_PART_NUM`, `WIDGET_MFG_NUM`, `WIDGET_REV_NUM_SHFT`, `WIDGET_PART_NUM_SHFT`, `WIDGET_MFG_NUM_SHFT`, `XWIDGET_PART_NUM`, `XWIDGET_REV_NUM`, `XWIDGET_MFG_NUM`, `WIDGET_LLP_REC_CNT`, `WIDGET_LLP_TX_CNT`, `WIDGET_PENDING`, `WIDGET_ERR_UPPER_ADDR_ONLY`, `WIDGET_F_BAD_PKT`, `WIDGET_LLP_XBAR_CRD`, `WIDGET_LLP_XBAR_CRD_SHFT`, `WIDGET_CLR_RLLP_CNT`, `WIDGET_CLR_TLLP_CNT`, `WIDGET_SYS_END`, `WIDGET_MAX_TRANS`, `WIDGET_WIDGET_ID`, `WIDGET_INT_VECTOR`, and 45 more. Types/enums/unions: `widget_ident`, `widget_cfg`, `xwidget_info_s`, `xwidget_hwid_s`, `widgetreg_t`, `xwidget_info_t`.

## Control Flow

Control flow is implemented by files that include this header; this file contributes compile-time contracts, inline helpers, constants, or prototypes.

## State And Persistence

State is architecture or subsystem state owned by callers; no filesystem persistence is introduced here.

## Dependencies And Integration Points

It integrates with the MIPS architecture tree and generic kernel subsystem named by its declarations.

## Risks

Risks are build regressions, low-level ABI drift, and hardware-specific behavior changes.

## Test Signals

Test signals are MIPS builds, headers-install where applicable, and subsystem runtime coverage.
Static review signal: this source currently has 280 lines and 7680 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/xtalk/xwidget.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/yamon-dt.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/yamon-dt.h

## Purpose

`yamon-dt.h` declares helpers that append YAMON bootloader command line, memory regions, and serial configuration into an FDT.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `linux/types.h`. Macros/constants: `__MIPS_ASM_YAMON_DT_H__`. Types/enums/unions: `yamon_mem_region`. Functions/prototypes/helpers: `yamon_dt_append_cmdline`, `yamon_dt_append_memory`, `yamon_dt_serial_config`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with MIPS bootloader-to-device-tree handoff.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 61 lines and 1717 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/yamon-dt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/Kbuild

## Purpose

`Kbuild` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Header-install entries: `generated-y += unistd_n32.h`, `generated-y += unistd_n64.h`, `generated-y += unistd_o32.h`, `generic-y += kvm_para.h`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 7 lines and 144 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/auxvec.h

## Purpose

`auxvec.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Macros/constants: `__ASM_AUXVEC_H`, `AT_SYSINFO_EHDR`, `AT_VECTOR_SIZE_ARCH`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 21 lines and 616 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/bitfield.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/bitfield.h

## Purpose

`bitfield.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Macros/constants: `__UAPI_ASM_BITFIELD_H`, `__BITFIELD_FIELD`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 31 lines and 766 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/bitfield.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/bitsperlong.h

## Purpose

`bitsperlong.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm-generic/bitsperlong.h`. Macros/constants: `__ASM_MIPS_BITSPERLONG_H`, `__BITS_PER_LONG`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 10 lines and 244 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/break.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/break.h

## Purpose

`break.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Macros/constants: `__UAPI_ASM_BREAK_H`, `BRK_USERBP`, `BRK_SSTEPBP`, `BRK_OVERFLOW`, `BRK_DIVZERO`, `BRK_RANGE`, `BRK_BUG`, `BRK_UPROBE`, `BRK_UPROBE_XOL`, `BRK_MEMU`, `BRK_KPROBE_BP`, `BRK_KPROBE_SSTEPBP`, `BRK_MULOVF`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 33 lines and 1321 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/break.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/byteorder.h

## Purpose

`byteorder.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `linux/byteorder/big_endian.h`, `linux/byteorder/little_endian.h`. Macros/constants: `_ASM_BYTEORDER_H`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 21 lines and 580 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/cachectl.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/cachectl.h

## Purpose

`cachectl.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Macros/constants: `_ASM_CACHECTL`, `ICACHE`, `DCACHE`, `BCACHE`, `CACHEABLE`, `UNCACHEABLE`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 28 lines and 800 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/cachectl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/errno.h

## Purpose

`errno.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm-generic/errno-base.h`. Macros/constants: `_UAPI_ASM_ERRNO_H`, `ENOMSG`, `EIDRM`, `ECHRNG`, `EL2NSYNC`, `EL3HLT`, `EL3RST`, `ELNRNG`, `EUNATCH`, `ENOCSI`, `EL2HLT`, `EDEADLK`, `ENOLCK`, `EBADE`, `EBADR`, `EXFULL`, `ENOANO`, `EBADRQC`, `EBADSLT`, `EDEADLOCK`, `EBFONT`, `ENOSTR`, `ENODATA`, `ETIME`, `ENOSR`, `ENONET`, `ENOPKG`, `EREMOTE`, `ENOLINK`, `EADV`, `ESRMNT`, `ECOMM`, `EPROTO`, `EDOTDOT`, and 70 more.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 133 lines and 5900 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/fcntl.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/fcntl.h

## Purpose

`fcntl.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm/sgidefs.h`, `asm-generic/fcntl.h`. Macros/constants: `_UAPI_ASM_FCNTL_H`, `O_APPEND`, `O_DSYNC`, `O_NONBLOCK`, `O_CREAT`, `O_TRUNC`, `O_EXCL`, `O_NOCTTY`, `FASYNC`, `O_LARGEFILE`, `__O_SYNC`, `O_SYNC`, `O_DIRECT`, `F_GETLK`, `F_SETLK`, `F_SETLKW`, `F_SETOWN`, `F_GETOWN`, `F_GETLK64`, `F_SETLK64`, `F_SETLKW64`, `__ARCH_FLOCK_EXTRA_SYSID`, `__ARCH_FLOCK_PAD`. Types/enums/unions: `flock64`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 61 lines and 2028 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/hwcap.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/hwcap.h

## Purpose

`hwcap.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Macros/constants: `_UAPI_ASM_HWCAP_H`, `HWCAP_MIPS_R6`, `HWCAP_MIPS_MSA`, `HWCAP_MIPS_CRC32`, `HWCAP_MIPS_MIPS16`, `HWCAP_MIPS_MDMX`, `HWCAP_MIPS_MIPS3D`, `HWCAP_MIPS_SMARTMIPS`, `HWCAP_MIPS_DSP`, `HWCAP_MIPS_DSP2`, `HWCAP_MIPS_DSP3`, `HWCAP_MIPS_MIPS16E2`, `HWCAP_LOONGSON_MMI`, `HWCAP_LOONGSON_EXT`, `HWCAP_LOONGSON_EXT2`, `HWCAP_LOONGSON_CPUCFG`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 23 lines and 715 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/hwcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/inst.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/inst.h

## Purpose

`inst.h` exposes MIPS instruction opcode enumerations and endian-aware bitfield overlays for instruction decoding in UAPI-visible tooling.

## Important APIs, Types, And Functions

Important APIs are opcode enums for classic MIPS, microMIPS, MIPS16e, MSA, DSP, COP0/COP1, Loongson, Octeon, and MXU encodings; format structs such as `j_format`, `i_format`, `r_format`, `c0r_format`, `msa_mi10_format`, microMIPS formats, and unions `mips_instruction`/`mips16e_instruction`. Includes: `asm/bitfield.h`. Macros/constants: `_UAPI_ASM_INST_H`, `MM_NOP16`. Types/enums/unions: `major_op`, `spec_op`, `spec2_op`, `spec3_op`, `mult_op`, `multu_op`, `div_op`, `divu_op`, `dmult_op`, `dmultu_op`, `ddiv_op`, `ddivu_op`, `rt_op`, `cop_op`, `bcop_op`, `cop0_coi_func`, `cop0_com_func`, `cop1_fmt`, `cop1_sdw_func`, `cop1x_func`, `mad_func`, `ptw_func`, `lx_func`, `mxu_func`, `lx_ingenic_func`, `bshfl_func`, and 76 more.

## Control Flow

There is no runtime flow locally; consumers overlay instruction words with endian-correct bitfields to decode or inspect opcodes.

## State And Persistence

State is user/kernel memory containing instruction words; no persistent state is modified.

## Dependencies And Integration Points

It integrates with uprobes, kprobes, instruction emulation, disassembly helpers, ptrace tooling, and user programs including kernel UAPI headers.

## Risks

Risks are UAPI ABI breakage, endian field-order mistakes, incorrect opcode values, and tooling misdecode across ISA revisions.

## Test Signals

Test signals are instruction decoder tests, kprobe/uprobe branch handling, microMIPS/MIPS16e coverage, and headers-install UAPI compilation.
Static review signal: this source currently has 1175 lines and 29923 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/inst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ioctl.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ioctl.h

## Purpose

`ioctl.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm-generic/ioctl.h`. Macros/constants: `__ASM_IOCTL_H`, `_IOC_SIZEBITS`, `_IOC_DIRBITS`, `_IOC_NONE`, `_IOC_READ`, `_IOC_WRITE`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 29 lines and 781 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ioctls.h

## Purpose

`ioctls.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm/ioctl.h`. Macros/constants: `__ASM_IOCTLS_H`, `TCGETA`, `TCSETA`, `TCSETAW`, `TCSETAF`, `TCSBRK`, `TCXONC`, `TCFLSH`, `TCGETS`, `TCSETS`, `TCSETSW`, `TCSETSF`, `TIOCEXCL`, `TIOCNXCL`, `TIOCOUTQ`, `TIOCSTI`, `TIOCMGET`, `TIOCMBIS`, `TIOCMBIC`, `TIOCMSET`, `TIOCPKT`, `TIOCPKT_DATA`, `TIOCPKT_FLUSHREAD`, `TIOCPKT_FLUSHWRITE`, `TIOCPKT_STOP`, `TIOCPKT_START`, `TIOCPKT_NOSTOP`, `TIOCPKT_DOSTOP`, `TIOCPKT_IOCTL`, `TIOCSWINSZ`, `TIOCGWINSZ`, `TIOCNOTTY`, `TIOCSETD`, `TIOCGETD`, and 53 more. Types/enums/unions: `winsize`, `termios`, `termios2`, `serial_rs485`, `serial_iso7816`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 120 lines and 4830 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/kvm.h

## Purpose

`kvm.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `linux/types.h`. Macros/constants: `__LINUX_KVM_MIPS_H`, `KVM_COALESCED_MMIO_PAGE_OFFSET`, `KVM_REG_MIPS_GP`, `KVM_REG_MIPS_CP0`, `KVM_REG_MIPS_KVM`, `KVM_REG_MIPS_FPU`, `KVM_REG_MIPS_R0`, `KVM_REG_MIPS_R1`, `KVM_REG_MIPS_R2`, `KVM_REG_MIPS_R3`, `KVM_REG_MIPS_R4`, `KVM_REG_MIPS_R5`, `KVM_REG_MIPS_R6`, `KVM_REG_MIPS_R7`, `KVM_REG_MIPS_R8`, `KVM_REG_MIPS_R9`, `KVM_REG_MIPS_R10`, `KVM_REG_MIPS_R11`, `KVM_REG_MIPS_R12`, `KVM_REG_MIPS_R13`, `KVM_REG_MIPS_R14`, `KVM_REG_MIPS_R15`, `KVM_REG_MIPS_R16`, `KVM_REG_MIPS_R17`, `KVM_REG_MIPS_R18`, `KVM_REG_MIPS_R19`, `KVM_REG_MIPS_R20`, `KVM_REG_MIPS_R21`, `KVM_REG_MIPS_R22`, `KVM_REG_MIPS_R23`, `KVM_REG_MIPS_R24`, `KVM_REG_MIPS_R25`, `KVM_REG_MIPS_R26`, `KVM_REG_MIPS_R27`, and 23 more. Types/enums/unions: `kvm_regs`, `kvm_fpu`, `kvm_debug_exit_arch`, `kvm_guest_debug_arch`, `kvm_sync_regs`, `kvm_sregs`, `kvm_mips_interrupt`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 226 lines and 7690 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/mman.h

## Purpose

`mman.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Macros/constants: `_ASM_MMAN_H`, `PROT_NONE`, `PROT_READ`, `PROT_WRITE`, `PROT_EXEC`, `PROT_SEM`, `PROT_GROWSDOWN`, `PROT_GROWSUP`, `MAP_TYPE`, `MAP_FIXED`, `MAP_RENAME`, `MAP_AUTOGROW`, `MAP_LOCAL`, `MAP_AUTORSRV`, `MAP_NORESERVE`, `MAP_ANONYMOUS`, `MAP_GROWSDOWN`, `MAP_DENYWRITE`, `MAP_EXECUTABLE`, `MAP_LOCKED`, `MAP_POPULATE`, `MAP_NONBLOCK`, `MAP_STACK`, `MAP_HUGETLB`, `MAP_FIXED_NOREPLACE`, `MS_ASYNC`, `MS_INVALIDATE`, `MS_SYNC`, `MCL_CURRENT`, `MCL_FUTURE`, `MCL_ONFAULT`, `MLOCK_ONFAULT`, `MADV_NORMAL`, `MADV_RANDOM`, and 28 more.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 120 lines and 4824 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/msgbuf.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/msgbuf.h

## Purpose

`msgbuf.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm/ipcbuf.h`. Macros/constants: `_ASM_MSGBUF_H`. Types/enums/unions: `msqid64_ds`, `ipc64_perm`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 69 lines and 2327 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/msgbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/param.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/param.h

## Purpose

`param.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm-generic/param.h`. Macros/constants: `_ASM_PARAM_H`, `EXEC_PAGESIZE`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 18 lines and 476 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/perf_regs.h

## Purpose

`perf_regs.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Macros/constants: `_ASM_MIPS_PERF_REGS_H`. Types/enums/unions: `perf_event_mips_regs`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 41 lines and 864 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/poll.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/poll.h

## Purpose

`poll.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm-generic/poll.h`. Macros/constants: `__ASM_POLL_H`, `POLLWRNORM`, `POLLWRBAND`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 11 lines and 217 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/poll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/posix_types.h

## Purpose

`posix_types.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm/sgidefs.h`, `asm-generic/posix_types.h`. Macros/constants: `_ASM_POSIX_TYPES_H`, `__kernel_daddr_t`. Types/enums/unions: `__kernel_daddr_t`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 27 lines and 757 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ptrace.h

## Purpose

`ptrace.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `linux/types.h`. Macros/constants: `_UAPI_ASM_PTRACE_H`, `FPR_BASE`, `PC`, `CAUSE`, `BADVADDR`, `MMHI`, `MMLO`, `FPC_CSR`, `FPC_EIR`, `DSP_BASE`, `DSP_CONTROL`, `ACX`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, `PTRACE_GETFPREGS`, `PTRACE_SETFPREGS`, `PTRACE_OLDSETOPTIONS`, `PTRACE_GET_THREAD_AREA`, `PTRACE_SET_THREAD_AREA`, `PTRACE_PEEKTEXT_3264`, `PTRACE_PEEKDATA_3264`, `PTRACE_POKETEXT_3264`, `PTRACE_POKEDATA_3264`, `PTRACE_GET_THREAD_AREA_3264`, `PTRACE_GET_WATCH_REGS`, `PTRACE_SET_WATCH_REGS`. Types/enums/unions: `defines`, `user_pt_regs`, `pt_regs`, `pt_watch_style`, `mips32_watch_regs`, `mips64_watch_regs`, `pt_watch_regs`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 110 lines and 2802 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/reg.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/reg.h

## Purpose

`reg.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Macros/constants: `__UAPI_ASM_MIPS_REG_H`, `MIPS32_EF_R0`, `MIPS32_EF_R1`, `MIPS32_EF_R2`, `MIPS32_EF_R3`, `MIPS32_EF_R4`, `MIPS32_EF_R5`, `MIPS32_EF_R6`, `MIPS32_EF_R7`, `MIPS32_EF_R8`, `MIPS32_EF_R9`, `MIPS32_EF_R10`, `MIPS32_EF_R11`, `MIPS32_EF_R12`, `MIPS32_EF_R13`, `MIPS32_EF_R14`, `MIPS32_EF_R15`, `MIPS32_EF_R16`, `MIPS32_EF_R17`, `MIPS32_EF_R18`, `MIPS32_EF_R19`, `MIPS32_EF_R20`, `MIPS32_EF_R21`, `MIPS32_EF_R22`, `MIPS32_EF_R23`, `MIPS32_EF_R24`, `MIPS32_EF_R25`, `MIPS32_EF_R26`, `MIPS32_EF_R27`, `MIPS32_EF_R28`, `MIPS32_EF_R29`, `MIPS32_EF_R30`, `MIPS32_EF_R31`, `MIPS32_EF_LO`, and 86 more.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 208 lines and 5426 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/resource.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/resource.h

## Purpose

`resource.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm-generic/resource.h`. Macros/constants: `_ASM_RESOURCE_H`, `RLIMIT_NOFILE`, `RLIMIT_AS`, `RLIMIT_RSS`, `RLIMIT_NPROC`, `RLIMIT_MEMLOCK`, `RLIM_INFINITY`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 37 lines and 1067 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sembuf.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sembuf.h

## Purpose

`sembuf.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm/ipcbuf.h`. Macros/constants: `_ASM_SEMBUF_H`. Types/enums/unions: `semid64_ds`, `ipc64_perm`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 37 lines and 1079 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sembuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/setup.h

## Purpose

`setup.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Macros/constants: `_UAPI_MIPS_SETUP_H`, `COMMAND_LINE_SIZE`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 9 lines and 183 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sgidefs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sgidefs.h

## Purpose

`sgidefs.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Macros/constants: `__ASM_SGIDEFS_H`, `_MIPS_ISA_MIPS1`, `_MIPS_ISA_MIPS2`, `_MIPS_ISA_MIPS3`, `_MIPS_ISA_MIPS4`, `_MIPS_ISA_MIPS5`, `_MIPS_ISA_MIPS32`, `_MIPS_ISA_MIPS64`, `_MIPS_SIM_ABI32`, `_MIPS_SIM_NABI32`, `_MIPS_SIM_ABI64`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 38 lines and 1054 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sgidefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/shmbuf.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/shmbuf.h

## Purpose

`shmbuf.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm/ipcbuf.h`, `asm/posix_types.h`. Macros/constants: `_ASM_SHMBUF_H`. Types/enums/unions: `shmid64_ds`, `ipc64_perm`, `shminfo64`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 62 lines and 1937 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/shmbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sigcontext.h

## Purpose

`sigcontext.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `linux/types.h`, `asm/sgidefs.h`. Macros/constants: `_UAPI_ASM_SIGCONTEXT_H`, `USED_FP`, `USED_FR1`, `USED_HYBRID_FPRS`, `USED_EXTCONTEXT`. Types/enums/unions: `extcontext`, `definition`, `sigcontext`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 91 lines and 2564 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sigcontext.h -->
