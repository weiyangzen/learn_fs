# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_idle.c

## Purpose
Implements GT idle/powergating sysfs and helpers for enabling/disabling render/media/GSC power gating and RC6/C6 idle state management.

## Important APIs and Functions
- Public APIs: `xe_gt_idle_init`, `xe_gt_idle_enable_pg`, `xe_gt_idle_disable_pg`, `xe_gt_idle_enable_c6`, `xe_gt_idle_disable_c6`, `xe_gt_idle_pg_print`, and `xe_gt_idle_residency_msec`.
- Sysfs attributes under `gtidle`: `name`, `idle_status`, and `idle_residency_ms`.
- Residency helpers track 32-bit counter wrap and convert raw residency with a 1280 ns multiplier.

## Control Flow
- `xe_gt_idle_init` skips SR-IOV VFs, creates `gtidle`, initializes lock and function pointers, names the GT idle state as render or media, creates sysfs files, and enables powergating.
- `xe_gt_idle_enable_pg` builds `powergate_enable` from available render/media engines, media version, platform exceptions, and workarounds, then writes `POWERGATE_ENABLE` under GT forcewake.
- `xe_gt_idle_pg_print` avoids waking the GT when already C6, otherwise reads live powergate enable/status registers and prints render/media/GSC status plus forcewake domain counters.
- C6 helpers program `RC_IDLE_HYSTERSIS`, `RC_CONTROL`, and `RC_STATE`.

## State and Persistence
`struct xe_gt_idle` stores name, last programmed powergate mask, residency multiplier, extended residency counters, and function pointers into GuC PC. Runtime reads update `prev_residency` and `cur_residency` under a raw spinlock.

## Dependencies and Integration Points
Depends on GT sysfs, GuC PC idle/residency hooks, forcewake, MMIO, runtime PM, engine masks, SR-IOV gating, platform/workaround flags, and GT debugfs powergate printing.

## Risks and Test Signals
- Residency wrap handling assumes queries are frequent enough that a 32-bit counter does not wrap multiple times between reads.
- Powergating is not supported or skipped on PVC and VFs; tests should verify sysfs absence/behavior by platform.
- Workaround `14020316580` masks selected media powergates and should be validated on affected platforms.
