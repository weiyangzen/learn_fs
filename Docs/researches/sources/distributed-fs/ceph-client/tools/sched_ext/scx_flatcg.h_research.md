# sources/distributed-fs/ceph-client/tools/sched_ext/scx_flatcg.h

Purpose: shared constants, statistic indices, stat names, and cgroup context layout for `scx_flatcg`.

Important APIs/types: defines `FCG_HWEIGHT_ONE` and `FCG_NR_STATS`; `enum fcg_stat_idx` enumerates local/global enqueue, activation/deactivation, hweight cache/update/race/skip, enqueue skip/race, current-cgroup selection outcomes, pick-next-cgroup outcomes, and failure counters. It defines `fcg_stat_names[]` under non-BPF builds. `struct fcg_cgrp_ctx` holds weight, active/runnable counts, child weight sum, hierarchical weight generation/value, task virtual time, cgroup virtual-time delta, and queued flag.

Control flow: none.

State and persistence: `struct fcg_cgrp_ctx` is persisted in BPF cgroup local storage by the BPF scheduler.

Dependencies and integration: included by both BPF and user-space flatcg code. Stat enum order must match user-space stat printing and BPF stat increments.

Risks: changing enum order without updating names breaks monitoring. Struct layout changes affect BPF storage expectations.

Test signals: compile both BPF and user-space users, validate stats names align with incremented indices, and inspect cgroup storage initialization.
