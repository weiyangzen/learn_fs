# sources/distributed-fs/ceph-client/include/linux/sched/deadline.h

Purpose: provides SCHED_DEADLINE classification helpers and root-domain bandwidth accounting hooks.

Important APIs and types: `dl_prio()`, `dl_task()`, `dl_time_before()`, `dl_add_task_root_domain()`, `dl_clear_root_domain()`, `dl_clear_root_domain_cpu()`, `dl_task_needs_bw_move()`, `dl_bw_visited()`, `dl_server()`, `dl_task_of()`, and `dl_is_implicit()` are the key symbols.

Control flow: scheduler and cpuset affinity paths use these helpers to identify deadline-priority tasks, compare wrapping deadlines, move bandwidth accounting between root domains, and distinguish real tasks from deadline server entities.

State and persistence: state is embedded in `sched_dl_entity` and root-domain bandwidth data elsewhere. The header only classifies and declares accessors.

Dependencies and integration points: depends on `sched.h`, root domains, cpusets, and deadline scheduler internals.

Risks and test signals: risks include confusing policy with PI-boosted priority, incorrect root-domain bandwidth moves during affinity changes, and treating deadline server entities as tasks. Test deadline admission, cpuset moves, affinity shrink/expand, PI boosting, and deadline server configurations.
