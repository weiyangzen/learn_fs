# sources/distributed-fs/ceph-client/kernel/cgroup/debug.c

## Purpose

`debug.c` implements an unstable cgroup debug controller for inspecting cgroup core internals. It is intended for diagnostics rather than stable user ABI.

## Important APIs, Types, and Functions

The controller registers `debug_cgrp_subsys`. It allocates a bare `struct cgroup_subsys_state` in `debug_css_alloc()` and frees it in `debug_css_free()`. Read handlers include `debug_taskcount_read()`, `current_css_set_read()`, `current_css_set_refcount_read()`, `current_css_set_cg_links_read()`, `cgroup_css_links_read()`, `cgroup_subsys_states_read()`, `cgroup_masks_read()`, and `releasable_read()`. `enable_debug_cgroup()` enables v2 debug files implicitly when the `cgroup_debug` boot parameter is used.

## Control Flow and State

The file is mostly read-only. Debug cgroup files walk `css_set`, `cgrp_cset_link`, task lists, subsystem state arrays, and cgroup masks while holding either `css_set_lock` or a live kernfs/cgroup lock. v1 exposes names such as `cgroup_css_links`, `cgroup_subsys_states`, and `cgroup_masks`; v2 uses shorter names such as `css_links`, `csses`, and `masks`.

## Dependencies and Integration Points

It depends tightly on cgroup core internals from `cgroup-internal.h`, including `css_set_lock`, `task_css_set()`, `cgroup_kn_lock_live()`, `cgroup_task_count()`, css ids, threaded css sets, cgroup masks, and population/release state.

## Risks and Edge Cases

The output exposes kernel addresses with `%pK`, so pointer visibility follows kernel pointer-printing policy. Reads can be expensive on large cgroup/task graphs and are intentionally unstable. `WARN_ON(count != cset->nr_tasks)` can surface internal accounting mismatches. Because this is diagnostic code, users must not depend on file names or formats as ABI.

## Test Signals

Test with `cgroup_debug` enabled and disabled; read all legacy and v2 files; create threaded cgroups and migrating tasks; verify task-count and css-set refcount displays; and check that removing cgroups makes live-lock checks return `-ENODEV` rather than stale data.
