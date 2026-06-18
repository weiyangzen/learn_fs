# File Research: sources/cow-pools/bcachefs-tools/linux/preempt.c

Defines `preempt_disable()` and `preempt_enable()` as no-ops. The file documents why: userspace percpu storage is genuinely per-thread, so current-thread percpu read-modify-write operations do not need CPU pinning.
