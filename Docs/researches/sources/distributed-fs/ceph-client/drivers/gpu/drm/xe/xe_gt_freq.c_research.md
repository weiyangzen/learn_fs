# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_freq.c

## Purpose
Exposes GT frequency management through per-GT sysfs attributes backed by GuC SLPC/PC frequency controls.

## Important APIs and Functions
- `xe_gt_freq_init` creates `freq0` under the GT sysfs directory, installs attributes, registers cleanup, and initializes throttle reporting.
- Read-only attributes: `act_freq`, `cur_freq`, `rpn_freq`, `rpa_freq`, `rpe_freq`, and `rp0_freq`.
- Read-write attributes: `min_freq`, `max_freq`, and `power_profile`.
- Helper accessors translate sysfs kobjects back to `struct xe_guc_pc` and `struct xe_device`.

## Control Flow and State
Initialization is skipped when `xe->info.skip_guc_pc` is true. Attribute reads/writes take runtime PM where live GuC PC access is needed, call the corresponding `xe_guc_pc_*` function, and return sysfs-formatted values. Cleanup removes files and drops the kobject.

## Dependencies and Integration Points
Depends on GT sysfs, GuC PC, throttle sysfs/support, runtime PM, and DRM managed cleanup. Called from `xe_gt_init` after idle/sysfs and before all-forcewake hardware init.

## Risks and Test Signals
- Min/max writes propagate GuC PC validation errors directly; sysfs tests should cover invalid frequency ranges and suspended-device reads.
- `power_profile_show` relies on GuC PC writing a NUL-terminated string into the buffer.
- Presence/absence of `freq0` should match `skip_guc_pc`.
