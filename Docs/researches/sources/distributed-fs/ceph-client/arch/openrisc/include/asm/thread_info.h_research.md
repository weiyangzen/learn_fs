<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/thread_info.h

## Purpose
Defines OpenRISC low-level thread metadata, stack sizing, thread flags, and current-thread access used by entry assembly and scheduler code.

## Important APIs, Types, And Functions
`THREAD_SIZE_ORDER` is zero and `THREAD_SIZE` is `PAGE_SIZE`. `struct thread_info` holds `task`, `flags`, `cpu`, `preempt_count`, and `ksp`. It declares `current_thread_info_set[NR_CPUS]` and maps thread flags such as `_TIF_SYSCALL_TRACE`, `_TIF_NOTIFY_RESUME`, `_TIF_SIGPENDING`, `_TIF_NEED_RESCHED`, and `_TIF_NOTIFY_SIGNAL`.

## Control Flow
Entry code loads current thread info from `current_thread_info_set`, checks `_TIF_WORK_MASK` before returning to userspace, and uses `ksp` for exception and context-switch stack handling.

## State And Persistence
Per-task `thread_info` persists for task lifetime. `ksp` records the saved kernel stack frame across context switches; `flags` drives syscall tracing, signal delivery, and rescheduling.

## Dependencies And Integration Points
Requires `processor.h`, task layout, and generated asm offsets. Integrated by `entry.S`, `head.S`, `process.c`, `smp.c`, and generic scheduler code.

## Risks
Layout changes must update `asm-offsets.c` consumers. Wrong `THREAD_SIZE` or flag masks break exception entry, stack switching, and userspace return work.

## Test Signals
Context-switch stress, signal delivery, preemption/reschedule tests, SMP boot, and generated asm offset consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/thread_info.h -->
