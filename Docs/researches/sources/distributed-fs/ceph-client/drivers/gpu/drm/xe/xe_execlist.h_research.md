<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist.h

## Purpose
`xe_execlist.h` declares the legacy execlist backend interface and a lock assertion helper.

## Important APIs, types, and functions
The header includes execlist types, declares `xe_execlist_init()`, `xe_execlist_port_create()`, and `xe_execlist_port_destroy()`, and defines `xe_execlist_port_assert_held(port)` as a lockdep assertion on the port spinlock.

## Control flow and integration points
There is no control flow beyond the lock assertion macro. GT initialization uses `xe_execlist_init()` when GuC submission is disabled; hardware engine setup/teardown uses port create/destroy.

## State and persistence behavior
The header owns no state. The implementation allocates per-engine ports and per-queue execlist backend state.

## Dependencies, risks, and test signals
Dependencies are execlist type definitions, GT/device declarations, and lockdep. Risks are callers invoking port internals without holding the lock or failing to skip execlist init when GuC is enabled. Test signals are force-execlist builds, backend init on GuC-disabled platforms, and lockdep coverage for active-list manipulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_execlist.h -->
