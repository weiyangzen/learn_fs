# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt.c

## Purpose
Implements core Xe GT allocation, initialization, hardware setup, reset/restart, suspend/resume, runtime PM, default LRC capture, user engine accounting, and wedged handling.

## Important APIs and Functions
- Lifecycle: `xe_gt_alloc`, `xe_gt_init_early`, `xe_gt_init`, `xe_gt_mmio_init`, `xe_gt_sanitize`, `xe_gt_suspend_prepare`, `xe_gt_suspend`, `xe_gt_resume`, `xe_gt_runtime_suspend`, `xe_gt_runtime_resume`, and `xe_gt_shutdown`.
- Reset: `xe_gt_reset_async`, inline `xe_gt_reset`/`xe_gt_wait_for_reset` from the header, `gt_reset_worker`, `do_gt_reset`, and `do_gt_restart`.
- Engine lookup/accounting: `xe_gt_record_user_engines`, `xe_gt_hw_engine`, `xe_gt_any_hw_engine_by_reset_domain`, and `xe_gt_any_hw_engine`.
- Context state: `xe_gt_record_default_lrcs`, `emit_wa_job`, `emit_nop_job`, and `emit_job_sync`.
- Workarounds/features: host L2 VRAM enable/disable, compression 1W coherence enable, `wa_14026539277`, and `xe_gt_sanitize_freq`.

## Control Flow
- Allocation sets `gt->tile` and chooses an ordered workqueue, sharing the primary GT workqueue for certain SR-IOV VF media GTs.
- Early init initializes PF/VF SR-IOV data, register save/restore state, workarounds/tunings, forcewake, TLB invalidation, MOCS, MMIO, uC noalloc state, stats, MCR early state, and PAT.
- Main init registers devm cleanup, sysfs, forcewake-protected uC/topology/MCR/engine/sysfs/CCS setup, idle/frequency sysfs, all-forcewake hardware setup, uC load, default CCS mode, SR-IOV PF hardware setup, user engine accounting, EU stall, and VF late init.
- Reset worker sanitizes submission, takes all forcewake, stops PF/VF/uC/pagefault/TLB state, applies GSC reset workaround around GDRST, restarts hardware/uC/SR-IOV state, restores frequency, and releases the runtime PM reference.
- Suspend/runtime suspend disable submission/uC and powergating-related hardware state; resume/runtime resume reinitializes hardware state and uC.

## State and Persistence
- Persistent GT state includes workqueues, reset work, forcewake, MMIO accessor, MCR steering, register save/restore, default LRC images, engine masks, user engine counts, frequency/idle sysfs kobjects, and SR-IOV data.
- Reset loses hardware programming and GuC/PF pushed configuration, so `do_gt_restart` reapplies PAT, MCR defaults, register SR, WOPCM, engine rings, uC, LMEM translation, SR-IOV PF HW, MOCS, engine SR, CCS mode, and GuC start.
- `xe_gt_sanitize_freq` restores GuC PC-stashed frequencies once GSC is loaded, absent, or in error for a specific workaround.

## Dependencies and Integration Points
Central integration point for most Xe subsystems: forcewake, MMIO, GuC/HuC/GSC uC, GGTT, LMEM LMTT, migration, MCR, MOCS, PAT, TLB invalidation, pagefaults, sysfs/debugfs, SR-IOV PF/VF, GT topology, ring ops, workarounds, and scheduling jobs.

## Risks and Edge Cases
- Init ordering is fragile: many operations require specific forcewake domains, MMIO adjustment for media GTs, or uC availability.
- Reset failure wedges the device; partial restart must not leave forcewake or runtime PM refs leaked.
- Default LRC capture submits real jobs on every engine and can fail if workarounds or engine state are invalid.
- SR-IOV PF/VF paths diverge significantly, with VF reset delegated and PF restart queued asynchronously after GT restart.

## Test Signals
- Probe/init tests should cover main and media GTs, SR-IOV PF/VF modes, DGFX/integrated memory, and CCS-capable compute configurations.
- Reset fault injection via `gt_reset_failure` should exercise wedge paths and PM ref cleanup.
- Suspend/resume and runtime PM tests should verify uC reload, powergating, host L2 VRAM workaround, and frequency restoration.
