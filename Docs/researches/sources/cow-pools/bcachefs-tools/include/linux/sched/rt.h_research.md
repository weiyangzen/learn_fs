# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/rt.h

Purpose: Real-time scheduler compatibility stub.

Key contents:
- Defines `rt_task()`.

Behavior and design:
- `rt_task()` always returns `0`; user-space bcachefs-tools does not model kernel RT scheduling.
