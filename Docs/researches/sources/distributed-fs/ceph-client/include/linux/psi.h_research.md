# sources/distributed-fs/ceph-client/include/linux/psi.h

Purpose: declares Pressure Stall Information runtime APIs for system and cgroup pressure accounting, display, trigger creation/destruction, polling, and memory-stall annotations.

Important APIs and types: when `CONFIG_PSI` is enabled, `psi_disabled` and `psi_system` expose global state. APIs include `psi_init()`, `psi_memstall_enter()`, `psi_memstall_leave()`, `psi_show()`, `psi_trigger_create()`, `psi_trigger_destroy()`, and `psi_trigger_poll()`. Cgroup helpers include `cgroup_psi()`, `psi_cgroup_alloc()`, `psi_cgroup_free()`, `cgroup_move_task()`, and `psi_cgroup_restart()`. Disabled builds provide no-op init/stall hooks and direct cgroup pointer assignment.

Control flow: scheduler and reclaim paths annotate task pressure; memory reclaim sections call memstall enter/leave; procfs/cgroupfs display calls `psi_show()`; userspace-created triggers are polled through file/kernfs wait queues; cgroup task migration updates PSI group membership.

State and persistence: PSI maintains runtime per-system and per-cgroup pressure counters, averages, triggers, and wait queues. It is diagnostic/accounting state and does not persist across boot.

Dependencies and integration points: depends on jump labels, scheduler task state, cgroups, kernfs/proc seq files, polling, and `psi_types.h`. It integrates resource-pressure accounting with `/proc/pressure/*` and cgroup pressure files.

Risks and test signals: risks include hot-path overhead, incorrect cgroup migration accounting, memstall enter/leave imbalance, trigger lifetime races, and disabled-config semantic drift. Test pressure files, cgroup moves, trigger polling/rate limits, reclaim annotations, and builds with PSI or cgroups disabled.
