# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_rc.c

## Purpose
Implements GuC Render C-state control, specifically enabling or disabling GuC ownership of RC6 in coordination with host GT idle logic.

## Important APIs, Types, And Functions
Exports `xe_guc_rc_init`, `xe_guc_rc_enable`, and `xe_guc_rc_disable`. Internal `guc_action_setup_gucrc` sends `GUC_ACTION_HOST2GUC_SETUP_PC_GUCRC` with either host or firmware control. `xe_guc_rc_fini_hw` disables GuC RC on managed teardown.

## Control Flow
Init asserts UC is enabled and registers hardware finalization. Enable takes GT forcewake and fails if forcewake cannot be acquired. PVC disables GuC RC and returns success. If GuC PC is skipped, it enables host C6 and does not send SLPC RC mode messages. Otherwise it requests firmware control. Disable requests host control when GuC PC is active and non-PVC, then disables host C6 through `xe_gt_idle_disable_c6`.

## State And Persistence
This file owns no dedicated struct fields; state is firmware RC mode plus host idle state. The managed action persists until device teardown and skips work on wedged devices.

## Dependencies And Integration Points
Depends on SLPC RC action ABI, GuC CT, forcewake, device wedge checks, GuC PC skip/platform flags, and `xe_gt_idle`. It is separate from `xe_guc_pc.c` but uses SLPC H2G calls for mode override.

## Risks And Test Signals
Enable/disable semantics vary by platform and `skip_guc_pc`. CT failures are logged unless caused by wedged cancellation. Test signals include RC6 residency changes, host C6 enable/disable behavior when PC is skipped, and teardown without warnings.
