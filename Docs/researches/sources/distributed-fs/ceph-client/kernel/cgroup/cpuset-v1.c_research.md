# `sources/distributed-fs/ceph-client/kernel/cgroup/cpuset-v1.c`

## Purpose

`cpuset-v1.c` implements legacy cgroup v1 cpuset behavior that is not shared with the default hierarchy. It provides v1-only memory pressure accounting, deprecated legacy file read/write handlers, legacy validation rules, hotplug evacuation of empty cpusets, clone-children inheritance, custom scheduler-domain generation, `/proc/<pid>/cpuset`, and the `cpuset1_files[]` cftype table consumed by the cpuset subsystem's legacy cftypes.

The file is compiled only when `CONFIG_CPUSETS_V1` is enabled and is explicitly separated from common cpuset code so modern v2 behavior can avoid legacy API and semantic baggage.

## Important APIs and Functions

- `struct cpuset_remove_tasks_struct` carries asynchronous work for moving tasks out of an empty legacy cpuset after hotplug.
- Frequency-meter helpers `fmeter_init()`, `fmeter_update()`, `fmeter_markevent()`, and `fmeter_getrate()` implement a scaled integer IIR low-pass filter for legacy `memory_pressure`.
- `cpuset_memory_pressure_enabled` globally gates memory-pressure event collection. `__cpuset_memory_pressure_bump()` marks a reclaim event on the current task's cpuset.
- `update_relax_domain_level()` validates and applies `sched_relax_domain_level`, rebuilding sched domains when needed.
- `cpuset_write_s64()` and `cpuset_read_s64()` handle signed legacy files, currently `sched_relax_domain_level`.
- `cpuset1_update_task_spread_flags()` and `cpuset1_update_tasks_flags()` apply legacy page/slab spread flags to tasks.
- `cpuset1_hotplug_update_tasks()` updates masks on CPU/memory hotplug and schedules asynchronous migration when a cpuset becomes empty.
- `cpuset1_validate_change()` enforces v1 subset and non-empty-populated constraints.
- `cpuset1_cpus_excl_conflict()` checks sibling CPU exclusivity conflicts.
- Optional `proc_cpuset_show()` renders `/proc/<pid>/cpuset`.
- `cpuset_read_u64()` and `cpuset_write_u64()` implement legacy boolean/stat files such as `cpu_exclusive`, `mem_exclusive`, `mem_hardwall`, `sched_load_balance`, `memory_migrate`, `memory_pressure_enabled`, and spread flags.
- `cpuset1_init()` initializes v1 fields, and `cpuset1_online_css()` inherits spread flags or clones parent masks when `CGRP_CPUSET_CLONE_CHILDREN` is set.
- `cpuset1_generate_sched_domains()` builds scheduler load-balancing domains from legacy load-balanced cpusets, using union-find to merge overlapping CPU masks.
- `cpuset1_files[]` declares the legacy cpuset cgroup files: `cpus`, `mems`, effective masks, exclusivity flags, scheduler knobs, memory migration/pressure, spread flags, and root-only `memory_pressure_enabled`.

## Control Flow and Behavior

Memory pressure starts with the global `cpuset_memory_pressure_enabled` knob. When enabled, reclaim paths call `__cpuset_memory_pressure_bump()`, which RCU-locks, finds `task_cs(current)`, and increments that cpuset's `fmeter`. Reads of `memory_pressure` call `fmeter_getrate()`, which updates elapsed ticks, decays the previous value by `FM_COEF`, folds in pending events, and returns a scaled recent rate.

Legacy file writes route through cgroup cftype operations. Boolean writes use `cpuset_write_u64()`, which takes `cpuset_full_lock()`, rejects offline cpusets, dispatches to `cpuset_update_flag()` for most flags, and emits one-time deprecation messages for obsolete v1 knobs. `memory_pressure_enabled` is root-only and directly updates the global gate. Signed writes use `cpuset_write_s64()` for `sched_relax_domain_level`; a value change can trigger `rebuild_sched_domains_locked()` when the cpuset has CPUs and load balancing is enabled.

Hotplug updates in `cpuset1_hotplug_update_tasks()` copy new CPU/memory masks into both configured and effective masks under the callback lock, then updates existing task CPU and memory masks if the cpuset remains non-empty. If CPUs or memory nodes become empty and the cgroup has populated css_sets, the code takes a live css ref and schedules `cpuset_migrate_tasks_workfn()`. The worker finds the nearest ancestor with non-empty CPU and memory masks and calls `cgroup_transfer_tasks()` to evacuate tasks asynchronously, avoiding a full cgroup migration from inside the hotplug update path.

Validation in `cpuset1_validate_change()` is legacy-specific: children must remain subsets of the trial cpuset, the trial cpuset must remain a subset of its parent, and populated cpusets cannot transition from non-empty CPU or memory masks to empty masks. The helper `is_cpuset_subset()` includes CPU and memory masks plus exclusivity flag constraints.

When a new legacy cpuset css comes online, `cpuset1_online_css()` inherits parent spread flags. If the cgroup has `CGRP_CPUSET_CLONE_CHILDREN`, it refuses to clone when siblings have CPU or memory exclusivity; otherwise it copies the parent's CPU and memory masks into both configured and effective masks under the callback lock.

Legacy sched-domain generation has a fast path: if `top_cpuset` is load-balanced, return one domain covering top effective CPUs intersected with housekeeping CPUs and aggregate relax-domain attributes over the tree. Otherwise, it walks descendants under RCU, collects relevant load-balanced cpusets, initializes their embedded union-find nodes, merges overlapping effective CPU masks, allocates one sched-domain mask per disjoint merged set, intersects with `housekeeping_cpumask(HK_TYPE_DOMAIN)`, and computes per-domain relax attributes from descendant load-balanced cpusets. Allocation failure falls back to the scheduler default-domain behavior by returning `ndoms = 1` with `domains == NULL`.

## State and Persistence Behavior

Per-cpuset legacy state lives in v1-only fields of `struct cpuset`: `fmeter`, `relax_domain_level`, and the union-find node. The memory pressure enable flag is global, not per hierarchy. File values are persistent kernel state while the cpuset css exists and are exposed through kernfs files created from `cpuset1_files[]`.

Hotplug mask updates mutate both configured and effective masks because legacy semantics do not separate them. Empty legacy cpusets are not allowed to keep tasks; task evacuation is deferred to a workqueue while a css reference keeps the cpuset alive. Spread flags are stored as bits in the shared `flags` field but only have v1 task flag side effects when the cpuset subsystem is not on the default hierarchy.

Scheduler-domain generation temporarily mutates each collected cpuset's embedded union-find node. That state is scratch space protected by the cpuset lock and should not be treated as persistent topology.

## Dependencies and Integration Points

- Includes `cgroup-internal.h` and `cpuset-internal.h`, using cgroup migration helpers, css/task iteration, path helpers, and cpuset shared locks.
- Relies on common cpuset code for `cpuset_update_flag()`, `cpuset_write_resmask()`, `cpuset_common_seq_show()`, task CPU/memory updates, callback locks, full locks, `top_cpuset`, and sched-domain rebuild entry points.
- Interacts with scheduler topology through `alloc_sched_domains()`, `struct sched_domain_attr`, `SD_ATTR_INIT`, `partition_sched_domains()` expectations, `sched_domain_level_max`, load-balance flags, and housekeeping CPU masks.
- Interacts with `/proc` through `proc_cpuset_show()` under `CONFIG_PROC_PID_CPUSET`.
- Uses cgroup core task migration (`cgroup_transfer_tasks()`), css references (`css_tryget_online()`, `css_put()`), and cgroup path rendering with namespace awareness.
- Uses task spread flag helpers for legacy page and slab spreading.

## Risks and Edge Cases

- `__cpuset_memory_pressure_bump()` assumes the current task has a valid cpuset under RCU; incorrect call sites outside task context would be unsafe.
- The frequency meter uses intentionally bounded integer arithmetic. Changes to scale, max tick, or max count can overflow or alter legacy ABI-visible values.
- Hotplug evacuation is asynchronous. Failures in `cgroup_transfer_tasks()` are logged but not retried here, so tests should cover failure handling and ensure css refs are always dropped.
- `cpuset1_hotplug_update_tasks()` skips direct task mask updates when the cpuset becomes empty because tasks should move to an ancestor. If evacuation fails, tasks may temporarily remain in an empty cpuset.
- `cpuset1_online_css()` clone-children behavior silently returns without cloning when siblings are exclusive. This is historical API behavior and can surprise callers expecting inheritance.
- `cpuset1_generate_sched_domains()` uses embedded union-find nodes and RCU traversal while depending on external cpuset lock serialization. Concurrent generation without the lock would corrupt scratch state.
- Deprecated v1 files still trigger real side effects; deprecation messages should not be confused with no-op behavior.
- The v1 file table uses unprefixed legacy names when mounted through the `cpuset` compatibility filesystem because cgroup core sets `CGRP_ROOT_NOPREFIX`.

## Test Signals

- Read/write every file in `cpuset1_files[]`, including invalid booleans, invalid `sched_relax_domain_level`, max write lengths for CPU/node lists, and root-only `memory_pressure_enabled`.
- Enable memory pressure, trigger direct reclaim in a cpuset, and verify `memory_pressure` decays over time and saturates safely under high event rates.
- CPU and memory hotplug tests where legacy cpusets lose CPUs/nodes, including populated cpusets that must evacuate tasks to the nearest non-empty ancestor.
- Validate v1 subset rules: child masks must stay within parent masks, populated cpusets cannot become empty, and exclusive siblings cannot overlap.
- Test clone-children inheritance with and without exclusive siblings.
- Exercise `memory_spread_page` and `memory_spread_slab` writes and confirm task flags update for existing and newly attached tasks in legacy mode.
- Generate sched domains for top-load-balanced, disjoint load-balanced, overlapping load-balanced, empty CPU, and housekeeping-excluded CPU cases.
- Verify `/proc/<pid>/cpuset` path output with cgroup namespaces and long paths when `CONFIG_PROC_PID_CPUSET` is enabled.
