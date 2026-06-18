# sources/distributed-fs/ceph-client/kernel/cgroup/legacy_freezer.c

## Purpose

`legacy_freezer.c` implements the cgroup v1 freezer controller with `freezer.state`, `freezer.self_freezing`, and `freezer.parent_freezing` files. It is described as imperfect and points users toward the cgroup v2 freezer.

## Important APIs, Types, and Functions

The controller state is `struct freezer` with state bits `CGROUP_FREEZER_ONLINE`, `CGROUP_FREEZING_SELF`, `CGROUP_FREEZING_PARENT`, and `CGROUP_FROZEN`. Public integration includes `cgroup1_freezing()` and `freezer_cgrp_subsys`. Main handlers include `freezer_css_alloc()`, `freezer_css_online()`, `freezer_css_offline()`, `freezer_attach()`, `freezer_fork()`, `freezer_read()`, `freezer_write()`, and `freezer_change_state()`.

## Control Flow and State

Writing `FROZEN` or `THAWED` to `freezer.state` calls `freezer_change_state()`, which walks descendants in preorder under `freezer_mutex` and CPU read lock. The target cgroup receives or loses `CGROUP_FREEZING_SELF`; descendants inherit `CGROUP_FREEZING_PARENT` from their parents. Freezing calls `freeze_task()` for all tasks; thawing calls `__thaw_task()` once no freezing bits remain. Reads perform a bottom-up pass with `update_if_frozen()` so cgroups lazily transition from `FREEZING` to `FROZEN` once all children and tasks are frozen.

## Dependencies and Integration Points

It depends on cgroup v1 css lifecycle, `freezer_active` static branch, CPU hotplug read locking, task freezer APIs, task iteration, RCU, and cgroup task migration/fork hooks.

## Risks and Edge Cases

Task migration can temporarily make task state disagree with freezer state; `freezer_attach()` compensates and clears ancestor `FROZEN` bits when needed. State transitions are lazy and read-driven. The root cgroup is non-freezable. The code increments/decrements the `freezer_active` static branch as freezing state appears or disappears, so missed transitions would affect scheduler freezer checks globally.

## Test Signals

Tests should cover writing `FROZEN`/`THAWED`, inherited freezing through nested cgroups, task attach into frozen and thawed cgroups, fork inside a frozen cgroup, bottom-up `freezer.state` reads, static-branch enable/disable balance, and legacy-only file visibility.
