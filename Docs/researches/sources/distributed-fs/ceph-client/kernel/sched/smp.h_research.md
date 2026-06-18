<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/smp.h -->
# sources/distributed-fs/ceph-client/kernel/sched/smp.h

## Purpose
`smp.h` is a small scheduler-internal bridge for SMP callback handling. It declares scheduler-facing hooks used by wakeup and generic SMP call-function code while keeping non-SMP builds cheap.

## Important APIs, Types, And Functions
The file declares `sched_ttwu_pending(void *arg)`, which drains pending try-to-wake-up work, and `call_function_single_prep_ipi(int cpu)`, which prepares a target CPU for a single-function IPI. Under `CONFIG_SMP` it declares `flush_smp_call_function_queue`; otherwise it provides an empty inline stub.

## Control Flow
SMP wakeup paths can queue remote wakeups or function callbacks, prepare an IPI, and later run `sched_ttwu_pending` or flush the call-function queue on the destination CPU. Non-SMP builds compile callers against the same names but elide queue flushing.

## State And Persistence
This header defines no storage. State lives in per-CPU wake lists and SMP call-function queues owned by scheduler core and generic SMP code.

## Dependencies And Integration Points
It depends only on `linux/types.h` and scheduler/SMP implementation files. It integrates with try-to-wake-up batching, remote IPI delivery, and generic `smp_call_function_single` queue processing.

## Risks And Edge Cases
The declarations are small, but call ordering is sensitive: pending wakeups must be flushed before a CPU goes idle, offline, or assumes there is no runnable work. The non-SMP stub must not hide code that depends on side effects.

## Test Signals
Signals include SMP wakeup stress, CPU hotplug tests, lockdep around remote wake queues, and build coverage for both `CONFIG_SMP=y` and `CONFIG_SMP=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/smp.h -->
