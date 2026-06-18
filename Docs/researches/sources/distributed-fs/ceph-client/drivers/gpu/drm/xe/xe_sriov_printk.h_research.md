<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_printk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_printk.h

## Purpose

`xe_sriov_printk.h` provides SR-IOV-aware logging macros that prepend PF/VF context to normal Xe driver messages.

## Important APIs, Types, and Functions

`xe_sriov_printk_prefix()` returns `PF: `, `VF: `, or an empty prefix from `xe->sriov.__mode`. Macros `xe_sriov_err`, `warn`, `notice`, `info`, and `dbg` wrap the corresponding Xe logging macros. `xe_sriov_dbg_verbose` compiles to debug logging only under `CONFIG_DRM_XE_DEBUG_SRIOV`; otherwise it type-checks the device pointer.

## Control Flow

Call sites use these macros exactly like normal Xe logging. The prefix is evaluated at log time from the device mode and merged into the format string.

## State and Persistence Behavior

There is no owned state. Output depends on persistent `xe->sriov.__mode`.

## Dependencies and Integration Points

It depends on `xe_printk.h` and is used throughout PF/VF SR-IOV provisioning, service, migration, and diagnostics.

## Risks and Test Signals

The macros assume a valid `struct xe_device *`. Format-string tests and compile coverage under both verbose-debug enabled and disabled configurations should catch type or variadic macro regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_printk.h -->
