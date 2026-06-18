# sources/distributed-fs/ceph-client/net/core/netclassid_cgroup.c

## Purpose

`netclassid_cgroup.c` implements the legacy `net_cls` cgroup subsystem, which associates a 32-bit classid with tasks and propagates that classid into sockets for traffic classification.

## Important APIs, Types, And Functions

The main state type is `struct cgroup_cls_state`, reached from `struct cgroup_subsys_state` by `css_cls_state()`. Exported `task_cls_state()` retrieves a task's classid cgroup state under the appropriate RCU/BH/trace locking context. Cgroup callbacks are `cgrp_css_alloc()`, `cgrp_css_online()`, `cgrp_css_free()`, and `cgrp_attach()`. The control file callbacks are `read_classid()` and `write_classid()`.

Socket propagation is handled by `update_classid_task()` and `update_classid_sock()`, which iterate a thread-group leader's file descriptors and call `sock_cgroup_set_classid()` for socket files.

## Control Flow

When a cgroup CSS is allocated, the file creates zeroed `cgroup_cls_state`. When brought online, it inherits the parent's classid if present. When tasks attach to a cgroup, `cgrp_attach()` updates sockets for each task in the taskset. When users write `classid`, `write_classid()` stores the new value in the CSS and iterates all tasks in that CSS to update currently open sockets.

`update_classid_task()` only processes thread-group leaders to avoid duplicate file-table traversal for multithreaded processes. It locks the task, iterates file descriptors in batches of 1000, unlocks and reschedules between batches to avoid long stalls, then resumes from the returned descriptor index.

## State And Persistence Behavior

The classid is stored per cgroup in memory and inherited by child cgroups at online time. Existing sockets are updated on attach and classid write; new sockets are expected to pick up the current cgroup classid through socket cgroup data initialization elsewhere. No state persists beyond cgroup lifetime.

## Dependencies And Integration Points

This file integrates with the cgroup subsystem, task CSS lookup, file descriptor tables, socket file detection, and `net/cls_cgroup.h` socket cgroup data. It defines `net_cls_cgrp_subsys` with a legacy cftype named `classid`.

## Risks

The main risk is consistency versus latency when updating many open descriptors. The batching avoids holding `file_lock` too long but means concurrent socket creation may race; the comment notes new sockets should already receive the new classid. Only processing thread-group leaders assumes shared file tables in threaded tasks. Locking context for `task_cls_state()` must match cgroup RCU expectations.

## Test Signals

Tests should cover reading/writing `net_cls.classid`, child inheritance, task migration between cgroups, updating existing sockets, creating sockets during classid changes, large descriptor tables, and classification behavior in qdisc/classifier paths that consume socket classid.
