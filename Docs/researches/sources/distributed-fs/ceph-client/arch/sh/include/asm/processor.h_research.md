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
