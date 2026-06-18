# File Research: sources/cow-pools/bcachefs-tools/include/linux/preempt.h

This header declares user-space preemption control hooks `preempt_disable()` and `preempt_enable()`, plus notrace/no-resched aliases. `preemptible()` returns `0`.

`migrate_disable()` and `migrate_enable()` are deliberately no-ops. The comment explains that mapping them to preemption disable would over-serialize transactions and can deadlock. Cleanup guards are defined for `preempt` and `preempt_notrace`.
