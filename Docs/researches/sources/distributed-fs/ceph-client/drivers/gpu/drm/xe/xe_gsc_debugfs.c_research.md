# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_debugfs.c

## Purpose
Registers a per-GSC debugfs file that prints GSC firmware and HECI status information.

## Important APIs and Functions
- `xe_gsc_debugfs_register` creates the `gsc_info` drm debugfs info file under the supplied parent.
- `gsc_info` gets a runtime PM reference, creates a `drm_printer`, and delegates to `xe_gsc_print_info`.
- Local helpers translate a `drm_info_node` back to the `struct xe_gsc`, `struct xe_gt`, and `struct xe_device`.

## Control Flow and State
The registration allocates a device-managed copy of the static info list, stores `gsc` in each entry's data pointer, then calls `drm_debugfs_create_files`. No persistent state is owned here beyond the debugfs metadata managed by DRM/devres.

## Dependencies and Integration Points
Depends on DRM debugfs helpers, runtime PM guard macros, and `xe_gsc_print_info`. It is normally called from uC debugfs registration under the GT debugfs tree.

## Risks and Test Signals
- Allocation failure silently skips the debugfs file, which is acceptable for diagnostics but can hide probe issues.
- Reading `gsc_info` should not fail on a suspended device because it takes runtime PM before printing.
