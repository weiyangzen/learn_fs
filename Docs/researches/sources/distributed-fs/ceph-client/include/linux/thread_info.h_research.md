<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/thread_info.h -->
# sources/distributed-fs/ceph-client/include/linux/thread_info.h

## Purpose
provides common low-level accessors for `thread_info` flags, syscall-work bits, restart-block setup, stack-frame checks, and architecture task-structure hooks.

## Important APIs, Types, and Functions
The file is 239 lines and exports these visible symbol families: types/enums `syscall_work_bit`; macros/constants `SYSCALL_WORK_SECCOMP`, `SYSCALL_WORK_SYSCALL_TRACEPOINT`, `SYSCALL_WORK_SYSCALL_TRACE`, `SYSCALL_WORK_SYSCALL_EMU`, `SYSCALL_WORK_SYSCALL_AUDIT`, `SYSCALL_WORK_SYSCALL_USER_DISPATCH`, `SYSCALL_WORK_SYSCALL_EXIT_TRAP`, `SYSCALL_WORK_SYSCALL_RSEQ_SLICE`, `TIF_NEED_RESCHED_LAZY`, `_TIF_NEED_RESCHED_LAZY`, `TIF_RSEQ`, `_TIF_RSEQ`, `THREAD_ALIGN`, `THREADINFO_GFP`; function-like macros `current_thread_info`, `arch_set_restart_data`, `set_thread_flag`, `clear_thread_flag`, `update_thread_flag`, `test_and_set_thread_flag`, `test_and_clear_thread_flag`, `test_thread_flag`, `read_thread_flags`, `read_task_thread_flags`, `set_syscall_work`, `test_syscall_work`, `clear_syscall_work`, `set_task_syscall_work`, and 2 more; inline helpers `set_restart_fn`, `set_ti_thread_flag`, `clear_ti_thread_flag`, `update_ti_thread_flag`, `test_and_set_ti_thread_flag`, `test_and_clear_ti_thread_flag`, `test_ti_thread_flag`, `arch_within_stack_frames`, `arch_setup_new_exec`; external prototypes `set_ti_thread_flag`, `clear_ti_thread_flag`, `test_and_set_bit`, `test_and_clear_bit`, `test_bit`, `READ_ONCE`, `arch_test_bit`, `tif_test_bit`, `arch_task_cache_init`, `arch_release_task_struct`, `arch_dup_task_struct`.

## Control Flow
Entry, scheduler, signal, seccomp, audit, tracing, rseq, and preemption code set/test/clear TIF or syscall-work bits through inline wrappers. `tif_need_resched()` is optimized for noinstr paths, and restartable syscalls use `set_restart_fn()`.

## State and Persistence Behavior
State is stored in per-task `thread_info` flags and optional syscall_work fields. CONFIG_THREAD_INFO_IN_TASK maps current_thread_info() onto `current`.

## Dependencies and Integration Points
It depends on arch `asm/thread_info.h`, current task definitions, bitops, restart blocks, and generic-entry configuration. Direct includes are `linux/types.h`, `linux/limits.h`, `linux/bug.h`, `linux/restart_block.h`, `linux/errno.h`, `asm/current.h`, `linux/bitops.h`, `asm/thread_info.h`.

## Risks and Edge Cases
Flag numbering and arch definitions must match entry assembly. Instrumentation in noinstr paths, non-atomic flag use in the wrong context, or mismatched lazy preemption flags can break scheduling and syscall exit handling.

## Test Signals
Build multiple architectures and CONFIG_GENERIC_ENTRY variants, run seccomp/audit/ptrace/rseq tests, exercise preemption/resched flags, and enable objtool/noinstr validation where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/thread_info.h -->
