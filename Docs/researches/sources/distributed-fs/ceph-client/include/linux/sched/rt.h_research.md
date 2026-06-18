# sources/distributed-fs/ceph-client/include/linux/sched/rt.h

Purpose: declares realtime-priority classification helpers, RT mutex scheduler hooks, PI priority adjustment APIs, and RR timeslice constant.

Important APIs and types: `rt_prio()`, `rt_or_dl_prio()`, `rt_task()`, `rt_or_dl_task()`, `rt_or_dl_task_policy()`, `rt_mutex_pre_schedule()`, `rt_mutex_schedule()`, `rt_mutex_post_schedule()`, `rt_mutex_get_top_task()`, `rt_mutex_setprio()`, `rt_mutex_adjust_pi()`, `normalize_rt_tasks()`, and `RR_TIMESLICE` are key.

Control flow: scheduler and locking code classify tasks by current priority or policy, handle PI boosting through RT mutex hooks, and normalize RT tasks when needed. RR tasks use the default timeslice for replenishment.

State and persistence: state lives in task priority/policy fields and RT mutex PI fields. The header itself only declares accessors/hooks.

Dependencies and integration points: integrates scheduler classes with RT mutexes, priority inheritance, and realtime policy management.

Risks and test signals: risks include confusing PI-boosted priority with policy, stale `pi_top_task` locking assumptions, disabled RT_MUTEX stubs hiding bugs, and RR timeslice regressions. Test RT scheduling, RR quantum behavior, PI mutex chains, priority changes, and configs without RT mutexes.
