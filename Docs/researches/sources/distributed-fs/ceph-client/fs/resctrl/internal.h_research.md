# sources/distributed-fs/ceph-client/fs/resctrl/internal.h

## Purpose
`internal.h` is the private contract for the resctrl filesystem implementation. It defines the in-memory objects shared by `rdtgroup.c`, `ctrlmondata.c`, `monitor.c`, and optional pseudo-lock code, plus function prototypes and configuration-gated pseudo-lock stubs.

## Important APIs, Types, And Functions
`cpumask_any_housekeeping()` selects a CPU from a mask while preferring CPUs not in `nohz_full`, which matters for delayed work and counter reads. `struct rdt_fs_context` extends kernfs mount context with mount flags for L2/L3 CDP, MBA MBps mode, and debug files; `rdt_fc2context()` recovers it from `fs_context`.

Monitoring contracts include `struct mon_evt`, the global `mon_event_all[]`, `for_each_mon_event()`, and `MAX_BINARY_BITS`; `struct mon_data`, stored as kernfs private data for monitor event files; and `struct rmid_read`, the cross-CPU payload used by `mon_event_read()` and `mon_event_count()`.

Group contracts include `enum rdt_group_type`, `enum rdtgrp_mode`, `struct mongroup`, and `struct rdtgroup`. The header also defines `RDT_DELETED`, `RFTYPE_*` flags, `struct rftype`, `struct mbm_state`, and extern globals such as `resctrl_schema_all`, `rdt_all_groups`, `rdtgroup_mutex`, `rdtgroup_default`, `debugfs_resctrl`, and `mba_mbps_default_event`.

The prototypes declare the internal API surface for group locking, `last_cmd_status`, schemata I/O, monitor file show functions, RMID allocation, monitor initialization, delayed work handlers, MBA assignment controls, I/O allocation, CLOSID lookup, CDP peer mapping, and pseudo-lock operations.

## Control Flow
The header itself has no runtime control flow except inline helpers. Its main control role is to keep cross-file call paths explicit: `rdtgroup.c` owns filesystem lifecycle and locks, `ctrlmondata.c` owns control/monitor file operations, `monitor.c` owns RMID and event counting, and `pseudo_lock.c` is compiled in only when `CONFIG_RESCTRL_FS_PSEUDO_LOCK` is enabled.

## State And Persistence
All declared state is in-memory kernel state. `struct rdtgroup` tracks kernfs identity, CLOSID/RMID, CPU assignment, deletion status, type, mode, child monitor groups, MBA MBps event, and pseudo-lock region pointer. `struct mon_data` instances persist while the resctrl filesystem is mounted. `struct rmid_read` is transient per read or counter initialization.

## Dependencies And Integration Points
The header includes `linux/resctrl.h`, kernfs, fs context, and tick/nohz APIs. It binds resctrl filesystem code to architecture-facing functions declared elsewhere by `linux/resctrl.h`, and to kernel subsystems including kernfs, CPU hotplug, cpumasks, delayed work, debugfs, and optional pseudo-lock char-device support.

## Risks
Because this is the shared internal ABI, field semantics must stay synchronized across all implementation files. Misinterpreting `rdtgroup::type`, `mode`, `closid`, or `mon.rmid` changes task/CPU assignment and monitoring behavior. Locking expectations are not encoded in types; many users must already hold `rdtgroup_mutex` and sometimes `cpus_read_lock()`.

## Test Signals
Build coverage should include configurations with allocation only, monitoring only, assignable MBM counters, CDP, MBA MBps, and pseudo-lock enabled/disabled. Runtime tests should verify that all kernfs callbacks referenced by `struct rftype` compile and that pseudo-lock stubs return `-EOPNOTSUPP` or no-op behavior when the feature is disabled.
