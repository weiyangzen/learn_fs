# sources/distributed-fs/ceph-client/include/linux/cgroup-defs.h

## Purpose

`cgroup-defs.h` contains the core cgroup data model: subsystem ids, flags, cgroup roots, per-subsystem state, css sets, recursive statistics state, freezer state, controller file definitions, controller callback tables, and socket cgroup data.

## Important APIs, Types, and Functions

Key types include `cgroup_subsys_state`, `css_set`, `css_rstat_cpu`, `cgroup_rstat_base_cpu`, `cgroup_freezer_state`, `cgroup`, `cgroup_root`, `cftype`, `cgroup_subsys`, `cgroup_file`, `sock_cgroup_data`, and `cgroup_of_peak`. Important constants cover CSS flags, cgroup flags, root flags, cftype flags, attach lock modes, max name sizes, and subsystem enumeration generated from `cgroup_subsys.h`. Inline helpers manage threadgroup change locking and socket cgroup fields.

## Control Flow

The header describes cgroup lifecycle flow rather than implementing it: css allocation/online/offline/free callbacks, task migration attach callbacks, fork/exit callbacks, controller file read/write callbacks, recursive stat propagation, and freezer accounting. Threadgroup change helpers acquire global and optional per-threadgroup read semaphores.

## State and Persistence Behavior

Runtime state is extensive: hierarchy topology, kernfs nodes, task css sets, subsystem states, per-cpu stats, freezer timing, BPF storage, PSI files, pidlists, release-agent work, and socket classification fields. Userspace-visible persistence is the cgroupfs hierarchy while mounted; kernel objects are RCU/refcount managed.

## Dependencies and Integration Points

It depends on lists, IDR, wait queues, RCU, refcounts, percpu refs/rwsems, sched, stats sync, workqueues, BPF cgroup definitions, and PSI. It is included by `cgroup.h` and every controller implementation.

## Risks and Edge Cases

Locking is subtle: fields are variously protected by `cgroup_mutex`, `css_set_lock`, RCU, percpu refs, or subsystem locks. Flexible arrays and embedded root cgroup layout constrain allocation. Controller callbacks must honor online/offline and threaded/default hierarchy rules. Socket fields compile differently by config.

## Test Signals

Run cgroup v1/v2 hierarchy creation/removal, task migration, controller enable/disable, recursive stats flush, freezer operations, BPF attachment, socket classid/prio tests, lockdep, KASAN, and config-matrix builds with controllers disabled.
