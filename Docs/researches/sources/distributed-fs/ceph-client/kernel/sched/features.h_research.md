# sources/distributed-fs/ceph-client/kernel/sched/features.h

## Purpose
Defines the scheduler feature switches consumed by the core scheduler through the `SCHED_FEAT(name, default)` macro expansion pattern. The file is intentionally macro-only: includers choose whether each entry becomes an enum value, static key, debugfs setting, or generated table entry.

## APIs, Control Flow, and State
The exported surface is the ordered list of feature names and defaults. Important flags include EEVDF/CFS placement controls (`PLACE_LAG`, `PLACE_DEADLINE_INITIAL`, `PLACE_REL_DEADLINE`, `RUN_TO_PARITY`, `PREEMPT_SHORT`, `DELAY_DEQUEUE`, `DELAY_ZERO`), wakeup and locality controls (`NEXT_BUDDY`, `PICK_BUDDY`, `CACHE_HOT_BUDDY`, `WAKEUP_PREEMPTION`), high-resolution tick controls (`HRTICK`, `HRTICK_DL`), remote wakeup queuing (`TTWU_QUEUE`), scheduling-domain scan heuristics (`SIS_UTIL`, `WA_IDLE`, `WA_WEIGHT`, `WA_BIAS`, `NI_RANDOM`, `NI_RATE`), utilization estimation (`UTIL_EST`), RT behavior (`RT_PUSH_IPI`, `RT_RUNTIME_SHARE`), and debug/warning switches. There is no runtime control flow in this header; control flow arises wherever `sched_feat()` gates behavior. Persistent state is external, normally in scheduler feature static keys and the sched debugfs interface when enabled.

## Dependencies and Integration Points
The file depends on scheduler build configuration symbols such as `CONFIG_HRTIMER_REARM_DEFERRED`, `CONFIG_PREEMPT_RT`, and `HAVE_RT_PUSH_IPI`. It integrates with fair scheduling, deadline hrticks, RT push/pull balancing, topology-aware balancing, wakeup placement, PELT/util-est accounting, and scheduler debugging. The order and names are part of the scheduler's internal feature registry, so changes have broad scheduler impact even though this file contains no functions.

## Risks and Test Signals
Risk centers on accidentally changing default scheduler policy, enabling a feature under an incompatible config, or removing a feature still referenced by `sched_feat()`. Good signals are scheduler selftests, boot-time scheduler debugfs inspection, latency and wakeup-preemption benchmarks, RT migration tests, CFS fairness/regression runs, and config matrix builds with and without `PREEMPT_RT`, hrtick support, and RT push IPI support.
