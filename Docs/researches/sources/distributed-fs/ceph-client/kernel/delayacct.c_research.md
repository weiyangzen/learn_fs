# sources/distributed-fs/ceph-client/kernel/delayacct.c

## Purpose
This file implements per-task delay accounting for CPU scheduler delay, block I/O, swap-in, free-page reclaim, thrashing, compaction, write-protect copy, and IRQ time. It feeds taskstats and exposes a sysctl to enable or disable the static-key guarded accounting path.

## Important APIs, Types, And Functions
Global state includes `delayacct_key`, `delayacct_on`, and `delayacct_cache`. `delayacct_init()` creates the `task_delay_info` cache and initializes `init_task`. `__delayacct_tsk_init()` allocates per-task delay state. `delayacct_add_tsk()` copies accounting into `struct taskstats`. Start/end pairs include block I/O, freepages, thrashing, swapin, compaction, and wpcopy. `__delayacct_irq()` accumulates IRQ delay. `__delayacct_blkio_ticks()` returns block delay in clock ticks.

## Control Flow
Boot option `delayacct` sets `delayacct_on`, then `delayacct_init()` installs the static key according to that setting. The sysctl handler validates admin permission on writes, parses a 0/1 value, and calls `set_delayacct()`. Each end function computes elapsed nanoseconds from `local_clock()`, updates totals/counts/min/max under the task delay raw spinlock, and records wall-clock timestamps when a new max occurs. `delayacct_add_tsk()` snapshots CPU and scheduler stats, then locks `tsk->delays` to merge delay buckets.

## State, Persistence, And Dependencies
All state is per-task memory from `delayacct_cache` plus the global static key. There is no durable persistence. Dependencies include scheduler cputime and sched_info, `taskstats`, sysctl, capabilities, slab cache allocation, raw spinlocks, `local_clock()`, and `ktime_get_real_ts64()`.

## Integration Points
Scheduler, block, reclaim, swap, compaction, memory-management, and IRQ accounting paths call the exported delayacct hooks through `linux/delayacct.h`. Userspace observes results through taskstats and toggles accounting with `/proc/sys/kernel/task_delayacct` when proc sysctl is enabled.

## Risks
Overflow handling zeros totals when additions wrap, so consumers must interpret zero total with nonzero count as overflow. Several CPU scheduler fields are sampled without locking by design. Start/end imbalance can produce bogus delays. Allocation failure for a task leaves `tsk->delays` NULL, and callers must be guarded by the delayacct static key/macros.

## Test Signals
Test boot-time enable, sysctl permission and min/max parsing, taskstats output under I/O wait, swap/reclaim/compaction workloads, nested thrashing state suppression, IRQ delay accounting, and overflow behavior under synthetic large counters.
