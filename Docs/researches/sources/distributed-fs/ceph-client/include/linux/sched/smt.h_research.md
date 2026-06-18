# sources/distributed-fs/ceph-client/include/linux/sched/smt.h

Purpose: declares SMT scheduler activation state and architecture SMT update hook.

Important APIs and types: `sched_smt_present`, `sched_smt_active()`, and `arch_smt_update()` are the exported symbols.

Control flow: scheduler/topology code checks a static key to determine whether SMT scheduling behavior is active; architecture code can notify updates when SMT availability changes.

State and persistence: SMT presence is runtime static-key state, derived from CPU topology and hotplug/control policy.

Dependencies and integration points: depends on static keys and `CONFIG_SCHED_SMT`. Integrates scheduler topology and architecture SMT control.

Risks and test signals: risks include stale static-key state after SMT hotplug/control changes and disabled-config assumptions. Test SMT on/off toggles, CPU hotplug, sched-domain rebuilds, and non-SMT builds.
