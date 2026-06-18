# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_ccs_mode.c

## Purpose
Implements compute-slice-to-CCS-engine mode programming and sysfs controls for selecting how many compute engines are exposed for available compute slices.

## Important APIs and Functions
- `xe_gt_apply_ccs_mode` applies `gt->ccs_mode` to the `CCS_MODE` register when enabled and not in SR-IOV VF.
- `xe_gt_ccs_mode_sysfs_init` creates `ccs_mode` and `num_cslices` sysfs attributes.
- `ccs_mode_store` validates a requested engine count, ensures no active DRM clients, handles PF lockdown when leaving/returning to default, records user engines, and triggers GT reset.

## Control Flow
`__xe_gt_apply_ccs_mode` starts with all compute slices disabled, iterates available CCS hardware engines, assigns fused-on slices evenly across the requested engine count, builds a user-visible engine mask, writes masked `CCS_MODE`, and logs the configuration.

## State and Persistence
`gt->ccs_mode` is the persistent software selection. Hardware state is reapplied during init and GT restart. User engine accounting is refreshed when the mode changes because exposed compute engines change.

## Dependencies and Integration Points
Depends on GT sysfs, runtime PM, MMIO, SR-IOV PF lockdown helpers, engine masks, and GT reset. Integrated during GT init after early hardware engine init and during `do_gt_restart`.

## Risks and Test Signals
- Invalid mode requests are rejected unless the number of slices is exactly divisible by requested engines.
- Sysfs changes require no open DRM clients; tests should verify `-EBUSY` with active clients and `-EINVAL` for non-divisible modes.
- PF lockdown around default-mode transitions protects active VFs; SR-IOV tests should cover enabled VF rejection.
