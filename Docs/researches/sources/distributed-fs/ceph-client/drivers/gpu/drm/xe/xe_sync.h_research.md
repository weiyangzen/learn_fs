<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync.h

## Purpose

`xe_sync.h` declares the Xe sync-entry API used by execution, VM bind, and wait paths.

## Important APIs, Types, and Functions

It defines parse flags for exec mode, long-running mode, and user-fence disallowance. It declares parse, dependency add, signal, wait, cleanup, input-fence aggregation, user-fence reference helpers, and `xe_sync_is_ufence()`.

## Control Flow

Ioctl handlers parse user sync entries, add dependencies to jobs, signal output syncs with the resulting fence, and clean entries after use. User-fence consumers can take references and poll signaled status.

## State and Persistence Behavior

The header exposes operations over `struct xe_sync_entry`, whose reference-owned members are released by cleanup.

## Dependencies and Integration Points

It includes sync types and forward declares DRM/Xe types. Integration points include exec ioctl, VM bind ioctl, scheduler jobs, and user fence wait/status paths.

## Risks and Test Signals

All parsed entries must eventually be cleaned. Tests should verify every parse success path has matching cleanup and that LR mode flags reject unsupported signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync.h -->
