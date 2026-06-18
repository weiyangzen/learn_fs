# sources/distributed-fs/ceph-client/include/linux/delayacct.h

Purpose: Defines per-task delay accounting storage and fast-path wrappers for collecting delays caused by block I/O, swapin, reclaim, thrashing, compaction, write-protect copy, and IRQ/softirq time.

Important APIs, types, and functions: Under `CONFIG_TASK_DELAY_ACCT`, `struct task_delay_info` stores starts, min/max/total delays, counts, timestamps of max delays, and a raw spinlock. APIs include task init/exit/free, taskstats export, block-I/O ticks, start/end wrappers for each delay category, and IRQ delay charging. A static key `delayacct_key`, `delayacct_on`, and `delayacct_cache` gate allocation and fast-path overhead.

Control flow: Fork/task init clears inherited delay pointers and allocates accounting state if enabled. Delay sites call start/end wrappers; wrappers first check the static branch and `task->delays` before calling out-of-line accounting functions. Taskstats export copies accumulated values to userspace structures.

State and persistence: State is per-task in memory and freed when the task exits or fork fails. Values are cumulative nanoseconds and counts, with min/max tracking for selected categories. Persistence is only via taskstats snapshots delivered to userspace.

Dependencies and integration points: Depends on taskstats UAPI, scheduler task state, slab cache, jump labels/static keys, raw spinlocks, and memory-management/block-I/O instrumentation sites.

Risks and test signals: Risks include start/end imbalance, static-key overhead regressions, inherited pointer reuse after fork, racey export without locking, and missed accounting when `current->delays` is absent. Test with `CONFIG_TASK_DELAY_ACCT=y/n`, enabling/disabling accounting, taskstats reads, block I/O waits, reclaim/thrashing/compaction paths, fork/exit stress, and IRQ delay charging.
