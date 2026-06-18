# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_debugfs.c

## Purpose
This file registers Xe debugfs files for device information, workarounds, residencies, forcewake control, wedged-mode control, SVM scheduling knobs, late-binding toggles, page-reclaim testing, fault injection, TTM memory-manager views, tile/GT subtrees, PXP, PSMI, and SR-IOV debug.

## Important APIs, Types, and Functions
The public entry point is `xe_debugfs_register`. Important file operations include `forcewake_all_fops`, `wedged_mode_fops`, `page_reclaim_hw_assist_fops`, `atomic_svm_timeslice_ms_fops`, `min_run_period_lr_ms_fops`, `min_run_period_pf_ms_fops`, and `disable_late_binding_fops`. Static `drm_info_list` entries expose `info`, `sriov_info`, `workarounds`, and Battlemage residency counters.

## Control Flow
Registration adds generic DRM info files, conditionally adds Battlemage telemetry and CSC fault injection, creates writable tuning files, registers TTM manager debugfs nodes, then delegates to tile, GT, PXP, PSMI, and SR-IOV debugfs registration. `forcewake_all` gets runtime PM and all GT forcewake domains on open, then releases them on close. `wedged_mode` validates modes and updates GuC ADS reset policy if changing to/from no-reset hang mode.

## State and Persistence Behavior
Debugfs writes mutate live driver state such as `xe->wedged.mode`, inconsistent reset policy flag, `has_page_reclaim_hw_assist`, SVM timeslice/min-run settings, and `late_bind.disable`. These are runtime settings only and disappear when the device/module is removed.

## Dependencies and Integration Points
It depends on DRM debugfs, Linux fault injection, PM runtime guards, forcewake, PMT telemetry, workarounds, GuC ADS scheduler policy, TTM managers, tile/GT debugfs, PXP, PSMI, and SR-IOV PF/VF debug registration.

## Risks
Debugfs is privileged but can destabilize hardware: forcewake can time out, wedged mode changes reset policy across GTs, and writable tuning knobs can expose racey scheduling behavior. Policy updates across multiple GTs can become inconsistent if a later GT update fails.

## Test Signals
Debugfs smoke tests, forcewake open/close leak checks, wedged mode validation and reset-policy failure injection, Battlemage telemetry reads, TTM manager debugfs presence, SR-IOV PF/VF registration, and runtime PM suspend/resume while files are open are useful signals.
