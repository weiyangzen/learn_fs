# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/cputime.h

Provides `task_cputime_adjusted()` stub, setting user and system CPU time outputs to zero. This preserves call-site compatibility without implementing per-task CPU accounting.
