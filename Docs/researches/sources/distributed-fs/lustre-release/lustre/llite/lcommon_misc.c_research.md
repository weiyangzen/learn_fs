<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/lcommon_misc.c -->
# sources/distributed-fs/lustre-release/lustre/llite/lcommon_misc.c

## Purpose

`lcommon_misc.c` provides common llite/VVP support that does not belong to a specific VFS operation: updating client connect capability state when OSC imports change, initializing MDS layout EA reply sizes from data-target capabilities, and acquiring/releasing whole-file CL group locks.

## Important APIs, Types, And Functions

- `cl_init_ea_size(struct obd_export *md_exp, struct obd_export *dt_exp)`: private helper that queries the data export for maximum and default LOV EA sizes and calls `md_init_ea_size()` on the metadata export.
- `cl_ocd_update(struct obd_device *host, struct obd_device *watched, enum obd_notify_event ev, void *owner)`: OBD notification callback that intersects llite connect flags with OSC import flags and refreshes EA sizing.
- `cl_get_grouplock(struct cl_object *obj, unsigned long gid, int nonblock, struct ll_grouplock *lg)`: creates a `CIT_MISC` CLIO and requests a whole-file `CLM_GROUP` lock with the provided group id.
- `cl_put_grouplock(struct ll_grouplock *lg)`: releases the CL lock, finalizes the CLIO, and drops the CL environment captured by `cl_get_grouplock()`.

## Control Flow

`cl_ocd_update()` is invoked from the OBD observer notification chain. It accepts only set-up, non-stopping OSC devices. For valid OSC updates, it reads the import's negotiated `ocd_connect_flags`, locks `lustre_client_ocd`, intersects the current llite flags with the OSC flags, and refreshes MDS EA buffer sizing if a data export is present. Unexpected notifications are logged and rejected with `-EINVAL`.

`cl_get_grouplock()` obtains a CL environment, creates a VVP CLIO for `CIT_MISC`, and initializes a whole-file lock descriptor spanning `[0, CL_PAGE_EOF]` with mode `CLM_GROUP` and `cld_gid = gid`. It requests the lock with `CEF_MUST` plus optional `CEF_NONBLOCK`. On success, ownership of the CL environment, CLIO, lock, and gid is transferred into `struct ll_grouplock`; on failure everything allocated in the function is released.

`cl_put_grouplock()` assumes a populated `ll_grouplock`, releases the CL lock, finalizes the CLIO, and returns the CL environment.

## State And Persistence Behavior

`cl_ocd_update()` mutates in-memory client capability state and MDS EA-size configuration. It does not persist data itself, but the updated EA sizes affect subsequent MDS RPC buffer sizing. Group locks are distributed runtime locks held in LDLM/CL state; `ll_grouplock` stores the live handles needed for later release.

## Dependencies And Integration Points

The notification path depends on OBD devices/imports, OSC type names, connect flags from `lustre_idl.h`, `lustre_client_ocd`, and metadata/data exports. The group-lock path depends on CLIO, VVP environment helpers, whole-file CL lock descriptors, and the `ll_grouplock` structure used by `file.c` ioctl handlers.

## Risks And Edge Cases

- `cl_ocd_update()` intersects flags (`lco_flags &= flags`), so once a capability is cleared it will not be re-added through this path without broader reinitialization.
- Unexpected OBD notifications are hard failures and noisy; callers must register the callback only for appropriate OSC imports.
- `cl_get_grouplock()` maps positive `cl_io_init()` results to `-EOPNOTSUPP`, meaning released/unavailable layouts cannot hold a group lock.
- Group lock lifetime spans a CL environment. Every successful `cl_get_grouplock()` must be paired with exactly one `cl_put_grouplock()`.
- Nonblocking group locks can fail both on local inode serialization and remote CL lock acquisition; callers need to map `-EAGAIN` appropriately.

## Test Signals

Tests should cover OSC connect-flag changes, EA-size query failures, notification rejection for wrong type/stopping devices, group-lock success, nonblocking conflict failure, released-layout `-EOPNOTSUPP`, remote lock request errors, and double-release/leak detection through `LL_IOC_GROUP_LOCK` and `LL_IOC_GROUP_UNLOCK` integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/lcommon_misc.c -->
