# `sources/distributed-fs/ceph-client/kernel/cgroup/cpuset-internal.h`

## Purpose

`cpuset-internal.h` is the private shared header for the cpuset controller implementation. It defines the central `struct cpuset`, shared enums for flags and cgroup file types, helpers for converting between css/task/cpuset objects, traversal macros over online cpuset children and descendants, and the internal API boundary between common cpuset code and the legacy v1-specific implementation in `cpuset-v1.c`.

The header is not a standalone module; it is the contract used by `cpuset.c` and `cpuset-v1.c` to keep cgroup css state, CPU masks, memory-node masks, partition state, deadline accounting, and legacy knobs consistent.

## Important APIs, Types, and Globals

- `struct fmeter` stores the legacy memory-pressure low-pass filter state: pending count, current value, timestamp, and spinlock.
- `enum prs_errcode` enumerates partition-root validation failures such as invalid CPUs, invalid parent, not exclusive, no CPUs, hotplug, empty CPU set, housekeeping violation, access failure, and remote partition errors.
- `cpuset_flagbits_t` defines bits stored in `struct cpuset::flags`: CPU/memory exclusivity, memory hardwall, memory migration, scheduler load balancing, page spread, and slab spread.
- `cpuset_filetype_t` assigns identifiers for all cpuset files handled by shared or v1 code, including CPU/mem lists, effective masks, partition files, exclusivity flags, scheduler relax level, memory pressure, and spread flags.
- `struct cpuset` embeds `struct cgroup_subsys_state css` and contains configured masks (`cpus_allowed`, `mems_allowed`), effective masks, default-hierarchy exclusive CPU masks, old memory mask, attach tracking, partition state, remote partition flag, SCHED_DEADLINE migration accounting, partition file handle, and v1-only fields.
- `top_cpuset` is declared as the root cpuset object, defined in `cpuset.c`.
- Inline accessors: `css_cs()`, `task_cs()`, `parent_cs()`, `is_cpuset_online()`, and flag tests like `is_cpu_exclusive()`, `is_memory_migrate()`, `is_spread_page()`.
- Iteration helpers: `cpuset_for_each_child()` and `cpuset_for_each_descendant_pre()` wrap css iterators and filter to online cpusets under RCU.
- Common cpuset API declarations include `rebuild_sched_domains_locked()`, callback lock helpers, task CPU/memory mask update helpers, `cpuset_update_flag()`, `cpuset_write_resmask()`, `cpuset_common_seq_show()`, and full lock/unlock helpers.
- Under `CONFIG_CPUSETS_V1`, v1 APIs and `cpuset1_files[]` are declared. Without v1 support, static inline no-op or success stubs preserve common code call sites.

## Control Flow and State Model

The core state model distinguishes configured and effective masks. In cgroup v2/default hierarchy, `cpuset.cpus` and `cpuset.mems` are user-configured and are not automatically constrained by the parent. Effective masks are the masks actually applied to tasks, derived from configured masks and ancestors, inheriting parent masks if intersection becomes empty. In legacy hierarchy, configured masks and effective masks are always the same.

Default hierarchy partitioning adds `exclusive_cpus` and `effective_xcpus`. `exclusive_cpus` is user-requested capacity that can be granted to a partition root or descendants; `effective_xcpus` is the granted set after ancestor and sibling constraints. For a valid partition root, `effective_cpus` comes from `effective_xcpus` minus CPUs handed to subpartitions, not necessarily from `cpus_allowed`.

`old_mems_allowed` records the previous memory-node set used for migration when `cpuset.mems` changes. `attach_in_progress` keeps a cpuset considered populated between `can_attach` and `attach`, avoiding transitions to empty CPU/memory masks while a task is entering. Deadline fields track attached and migrating SCHED_DEADLINE tasks and reserved bandwidth during cpuset attachment.

The v1-only block adds `fmeter`, `relax_domain_level`, and a union-find node used by legacy sched-domain generation. This keeps legacy memory pressure and custom load-balancing domain behavior out of builds without `CONFIG_CPUSETS_V1`.

## Dependencies and Integration Points

- Includes cgroup core definitions, CPU and cpumask APIs, cpuset public APIs, spinlocks, union-find, and scheduler isolation/housekeeping definitions.
- Relies on cgroup css helpers such as `task_css()`, `css_is_online()`, `css_is_dying()`, `css_for_each_child()`, `css_for_each_descendant_pre()`, and `css_rightmost_descendant()`.
- Common code in `cpuset.c` implements the declared shared functions and uses the v1 stubs/hooks to compile the same logic with or without legacy support.
- `cpuset-v1.c` implements the v1 declarations, including legacy file table registration through `cpuset1_files[]`.
- Scheduler integration runs through sched-domain rebuild declarations, load balance flags, relax-domain level, housekeeping CPU masks, and SCHED_DEADLINE accounting fields.
- Memory management integration uses nodemasks, old memory masks, memory migration, hardwall/exclusive flags, and page/slab spread flags.

## Risks and Edge Cases

- The configured/effective mask distinction differs sharply between v1 and v2. Code that assumes `cpus_allowed == effective_cpus` is only valid for legacy mode or selected top-level cases.
- `attach_in_progress` is part of population semantics; ignoring it can permit an invalid empty cpuset while a task is being attached.
- Online traversal macros require RCU read locking and filter through `is_cpuset_online()`. Missing RCU coverage risks seeing dying css state.
- Partition state is partly not lock-protected (`prs_err` is explicitly called out), so readers must tolerate transient status.
- The v1 stubs deliberately return success/no-op when `CONFIG_CPUSETS_V1` is off. Callers must not depend on v1 side effects in non-v1 builds.
- The union-find node is embedded in `struct cpuset`, so sched-domain generation must not run concurrently in a way that reuses the same nodes without the cpuset lock.

## Test Signals

- Build with and without `CONFIG_CPUSETS_V1` to verify the stub boundary and v1 field use.
- Validate cpuset v2 mask inheritance, empty configured masks, parent hotplug propagation, and partition-root transitions.
- Validate legacy mode keeps configured/effective masks identical and exposes v1-only files.
- Exercise task attach while changing cpuset masks to ensure `attach_in_progress` prevents invalid empty transitions.
- Exercise RCU traversal under concurrent cpuset creation/removal with lockdep and KASAN/KCSAN.
- Cover SCHED_DEADLINE attach/migration accounting and sched-domain rebuild triggers.
