# sources/distributed-fs/ceph-client/kernel/cgroup/cgroup-internal.h

## Purpose

`cgroup-internal.h` is the private interface shared by cgroup core implementation files. It defines internal context structures for cgroup filesystem mounting, per-open-file state, css_set/cgroup association links, migration work state, trace-path helpers, root/subsystem iteration macros, and prototypes for cross-file cgroup core, rstat, namespace, and cgroup v1 functions.

## Important APIs, types, and data

- `TRACE_CGROUP_PATH(type, cgrp, ...)` builds a cgroup path under `trace_cgroup_path_lock` only when the relevant tracepoint static key is enabled, then emits the matching `trace_cgroup_*` event.
- `struct cgroup_fs_context` extends `kernfs_fs_context` with selected root, namespace, root flags, and cgroup v1-only mount options: clone-children, none/all selection, subsystem mask, hierarchy name, and release agent path.
- `cgroup_fc2context()` converts a generic `struct fs_context` to the private cgroup mount context.
- `struct cgroup_file_ctx` holds per-open cgroup file state for namespace context, PSI triggers, v2 task iterators, v1 cached pidlists, and peak-file tracking.
- `struct cgrp_cset_link` models the many-to-many relationship between `struct cgroup` and `struct css_set`.
- `struct cgroup_taskset` and `struct cgroup_mgctx` carry task/cset migration state, including source and destination cset lists, task counts, current iterator positions, preloaded csets, and affected subsystem masks.
- `for_each_root()` and `for_each_subsys()` provide internal iteration over roots and enabled subsystem slots.
- `notify_on_release()`, `get_css_set()`, and `put_css_set()` are inline helpers for common flag/refcount handling.
- Prototypes expose root setup, subsystem rebinding, kernfs live locking, migration, attach, mkdir/rmdir, path formatting, task counting, rstat init/exit, cgroup namespace proc operations, and cgroup v1 entry points.

## Control flow

As a header, it does not run control flow directly, but it shapes several core flows. Mount setup code allocates a `cgroup_fs_context`, parses v1/v2 options into it, then passes it to root setup and kernfs tree creation. Task migration code initializes a `cgroup_mgctx`, preloads source/destination css_sets, validates destination cgroups, migrates tasks, and finishes by dropping preload state. File operations use `cgroup_file_ctx` to keep iterator or pidlist state across seq_file calls.

The trace macro avoids path construction unless tracing is enabled, then serializes access to the global path buffer. `put_css_set()` performs a lockless fast path when the refcount will not reach zero and takes `css_set_lock` only for final destruction.

## State and persistence behavior

The header defines state containers but does not allocate most state. Persistent runtime state lives in cgroup roots, cgroups, css_sets, mount contexts, and open-file contexts owned by implementation files. `trace_cgroup_path` is a global scratch buffer protected by `trace_cgroup_path_lock`. css_set lifetime is refcounted and final release is serialized under `css_set_lock`.

## Dependencies and integration points

This private header depends on public cgroup, kernfs, workqueue, list, refcount, and fs parser APIs. It is included by cgroup core files such as `cgroup.c`, `cgroup-v1.c`, `rstat.c`, and `namespace.c`. It bridges kernfs filesystem operations, cgroup namespace handling, controller subsystem arrays, migration/attach logic, and trace events.

## Risks and edge cases

- Locking contracts are implicit in prototypes and inline helpers. Misusing `put_css_set_locked()`, `cgroup_kn_lock_live()`, or attach locks can introduce lifetime and migration races.
- `TRACE_CGROUP_PATH()` uses a single global buffer; any new trace path user must preserve the spinlock discipline and avoid sleeping while held.
- `for_each_subsys()` iterates all subsystem slots and tolerates null entries through its expression form. Callers must handle absent subsystems.
- Migration structs depend on list-head initialization macros. Stack allocations should use `DEFINE_CGROUP_MGCTX()` or exact initializers.
- v1-only fields live in the common mount context; v2 paths must not accidentally interpret v1 options.

## Test signals

Compile coverage across cgroup v1/v2, namespace, rstat, cpuset, and optional controller configs is the first signal. Runtime stress should cover task migration, concurrent fork/migration, cgroup removal during kernfs file access, tracepoint enable/disable while paths are emitted, css_set final put paths, and mixed v1/v2 mount option parsing.
