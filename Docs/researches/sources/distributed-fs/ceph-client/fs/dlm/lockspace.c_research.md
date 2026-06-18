# sources/distributed-fs/ceph-client/fs/dlm/lockspace.c

## Purpose
`lockspace.c` owns DLM lockspace lifecycle. It creates and destroys `struct dlm_ls`, exposes lockspace sysfs attributes, coordinates userland `dlm_controld` join/leave handshakes through kobject uevents, starts/stops communication and recovery threads, registers per-lockspace devices/debugfs files, and releases all per-lockspace memory.

## Important APIs and Functions
- Module lifecycle: `dlm_lockspace_init()` creates the `dlm` kset; `dlm_lockspace_exit()` unregisters it.
- Lookup/refcount APIs: `dlm_find_lockspace_global()`, `dlm_find_lockspace_local()`, `dlm_find_lockspace_device()`, and `dlm_put_lockspace()`.
- Creation APIs: `dlm_new_lockspace()` for kernel/filesystem users and `dlm_new_user_lockspace()` for userspace lockspaces, both funneled through `__dlm_new_lockspace()` and `new_lockspace()`.
- Release APIs: `dlm_release_lockspace()` and private `release_lockspace()`.
- Emergency control: `dlm_stop_lockspaces()` stops running lockspaces when userland control disappears.
- Sysfs attribute handlers: `control`, `event_done`, `id`, `nodir`, `recover_status`, and `recover_nodeid`.
- Cleanup helpers: `free_lockspace()`, `remove_lockspace()`, `lockspace_busy()`, `lkb_idr_free()`, and `rhash_free_rsb()`.

## Control Flow
Initialization sets up a global lockspace list guarded by `lslist_lock`, a create/release mutex `ls_lock`, and a kset with uevent operations. Creating the first lockspace starts midcomms. `new_lockspace()` validates names/LVB length/cluster compatibility, reuses an existing lockspace unless `DLM_LSFL_NEWEXCL` forbids it, allocates `struct dlm_ls`, initializes every embedded list/lock/table/timer/waitqueue, starts callback and recovery threads, waits for recoverd to hold the initial recovery lock, adds the kobject, emits an online uevent, waits for userland to configure membership and start recovery, waits for recovery completion, then creates debugfs files.

Releasing checks whether the lockspace is busy according to the requested release mode, removes the create reference or decrements shared create count, deregisters the device, optionally emits an offline uevent, stops recoverd, shuts down scan timer/callbacks/midcomms as needed, removes the lockspace from the global list, deletes debugfs files, drops the kobject, destroys recovery/request/membership state, queues delayed memory freeing, and drops the module reference.

Sysfs `control` calls `dlm_ls_stop()` or `dlm_ls_start()` after taking a lockspace reference. `event_done` stores the userland result and wakes the join/leave waiter. `nodir` can set `LSFL_NODIR`; `id` sets the global lockspace id used in wire headers.

## State and Persistence Behavior
Global state consists of `ls_count`, `ls_lock`, `lslist`, `lslist_lock`, and `dlm_kset`. Per-lockspace state is allocated dynamically and lives until release plus delayed `free_lockspace()` work. There is no disk persistence. Membership and recovery state are rebuilt on each join/recovery cycle from userland configuration and peer communication. `ls_create_count` tracks shared open/create references separately from `ls_count`, which protects active users of an `ls` pointer.

## Dependencies and Integration Points
`lockspace.c` depends on module refs, kobjects/sysfs/uevents, midcomms, recoverd, member/config management, request queue cleanup, user daemon availability, callback workqueues, debugfs creation, lock scanning, and device registration. It is the bridge between in-kernel DLM users, userspace `dlm_controld`, and the lower lock/recovery/message layers.

## Risks
- Creation has many initialized resources with many error labels; unwind order must match initialization order exactly.
- Join/release waits depend on userland writing `event_done`. A missing or wedged control daemon blocks progress unless higher-level handling stops lockspaces.
- `lockspace_busy()` checks the LKB xarray rather than RSB table because AST-pending locks may already be detached from resources; release behavior can surprise callers expecting only granted locks to matter.
- Shared create references (`ls_create_count`) and active pointer refs (`ls_count`) are separate; bugs in either can leak lockspaces or free them while still reachable.
- The first/last lockspace controls global midcomms startup/shutdown, making races around `ls_count` particularly sensitive.

## Test Signals
- Create/release tests should cover first lockspace, additional shared lockspace, `DLM_LSFL_NEWEXCL`, invalid names, invalid LVB lengths, cluster mismatch, and user daemon absence.
- Sysfs tests should verify `control`, `event_done`, `id`, `nodir`, and recovery status/node fields.
- Failure-injection tests should target allocation or thread-start failures in `new_lockspace()` and verify no kobjects, xarrays, rhashtables, timers, or module refs leak.
- Release tests should cover `DLM_RELEASE_NO_LOCKS`, `DLM_RELEASE_UNUSED`, `DLM_RELEASE_FORCE`, `DLM_RELEASE_NO_EVENT`, and `DLM_RELEASE_RECOVER`.
- Integration tests should confirm debugfs files and misc devices are created after successful recovery and removed during release.
