<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pm.c

## Purpose

`xe_pm.c` implements Xe system suspend/resume, runtime suspend/resume, D3cold policy, PM notifiers, runtime PM reference helpers, and lockdep annotations that keep GPU memory management, display, GT, PXP, IRQ, I2C, and firmware flows ordered around power transitions.

## Important APIs and Functions

Public functions include `xe_pm_suspend()`, `xe_pm_resume()`, `xe_pm_init_early()`, `xe_pm_init()`, `xe_pm_fini()`, `xe_pm_runtime_suspend()`, `xe_pm_runtime_resume()`, runtime PM get/put variants, `xe_pm_set_vram_threshold()`, `xe_pm_d3cold_allowed_toggle()`, `xe_pm_block_on_suspend()`, `xe_pm_might_block_on_suspend()`, `xe_rpm_reclaim_safe()`, `xe_pm_assert_unbounded_bridge()`, and `xe_pm_module_init()`. Private helpers handle D3cold capability, runtime PM init/fini, notifier eviction, rebind worker wakeup, callback-task tracking, and lockdep map priming.

## Control Flow and State

System suspend blocks new suspend-sensitive work, suspends PXP, waits late binding, prepares GTs, suspends display, evicts BOs, suspends GTs, IRQ, display late, and I2C. Resume disables GT C6, applies tile workarounds, waits PCODE, restores display early and pinned BOs, resumes I2C/IRQ/GT/display, restores late BOs, resumes PXP, re-registers VF CCS, and reloads late-bind firmware. Runtime suspend marks the callback task, applies lockdep annotations, suspends PXP/display, releases VRAM userfault mmap offsets, evicts BOs only if D3cold is allowed, suspends GTs or runtime-suspends GTs, and suspends IRQ/display-late/I2C. Runtime resume mirrors that path and conditionally restores BOs/firmware only for D3cold. D3cold allowed is recomputed from VRAM usage versus a threshold under `xe->d3cold.lock`.

## Dependencies and Integration Points

This file coordinates PCI PM callbacks, TTM BO eviction/restoration, display PM, GT idle/suspend, IRQ, I2C, PCODE, PXP, late binding firmware, SR-IOV VF CCS, workarounds, runtime PM, Linux suspend notifiers, DMI quirks, and lockdep/reclaim annotations.

## Risks and Test Signals

Ordering bugs can leave hardware inaccessible, display blank, BOs lost, or runtime PM deadlocked. D3cold depends on root-port PME/_PR3, platform quirks, VRAM thresholds, and runtime idle timing. The PM notifier intentionally holds a runtime PM reference across suspend preparation and completion. Tests should cover system suspend/resume success and failure unwinds, D3hot versus D3cold runtime paths, VRAM threshold validation, BMG NUC13RNG threshold quirk, notifier eviction and rebind wakeup, callback-task recursion avoidance, missing outer runtime PM warning, lockdep prime paths, VF RPM disabled behavior, and PM teardown after partial init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pm.c -->
