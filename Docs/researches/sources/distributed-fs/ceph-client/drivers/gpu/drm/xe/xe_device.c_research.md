# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device.c

## Purpose
This file implements the top-level Xe DRM device and file lifecycle. It defines DRM ioctls/fops, per-open file state, special mmap behavior, device allocation/destruction, early and full probe sequencing, remove/shutdown paths, cache flush helpers, snapshot printing, wedged-device handling, and ASID-to-VM lookup.

## Important APIs, Types, and Functions
Major entry points include `xe_device_create`, `xe_device_probe_early`, `xe_device_probe`, `xe_device_remove`, `xe_device_shutdown`, `xe_file_get`, `xe_file_put`, `xe_is_xe_file`, `xe_device_wmb`, `xe_device_l2_flush`, `xe_device_td_flush`, `xe_device_ccs_bytes`, `xe_device_snapshot_print`, `xe_device_declare_wedged`, `xe_device_validate_wedged_mode`, `xe_wedged_mode_to_string`, and `xe_device_asid_to_vm`. Static structures include the DRM ioctl table, `xe_driver_fops`, and the `drm_driver`.

## Control Flow
Open allocates `xe_file`, client accounting, VM and exec-queue xarrays, and process identity. Close kills exec queues, removes them from HW engine groups, closes VMs, and drops the file ref under runtime PM. Ioctls reject wedged devices and acquire runtime PM before dispatch. Mmap handles a DGFX PCI barrier special offset or falls back to GEM mmap.

Device creation removes conflicting apertures, allocates `xe_device`, initializes TTM with `xe_ttm_funcs`, creates BO/shrinker/pagemap infrastructure, IRQ state, validation state, ASID tracking, pinned BO lists, workqueues, and PMT locking. Early probe initializes workarounds, early MMIO, SR-IOV mode, pcode, survivability mode, LMEM readiness, wedged mode, and VRAM region allocation. Full probe initializes PAT, SR-IOV, DMA masks, tiles, GTs, GGTT, FLR cleanup, flat CCS, VRAM, TTM managers, display, IRQ, pagefaults, devcoredump, NVM, remapper, HECI, late bind, OA, PXP, PSMI, DRM registration, sysfs/debugfs/hwmon/I2C/VSEC/SR-IOV late hooks, and sanitize cleanup.

## State and Persistence Behavior
The file initializes long-lived device state: TTM device, workqueues, shrinkers, `xe->info`, ASID xarray, pinned BO state, runtime wedged flags/methods, PM/runtime fields, and per-file VM/queue xarrays. Wedging is terminal until external recovery; it blocks ioctls and emits DRM wedged events. Remove unplugs DRM and evicts/purges BOs; shutdown tears down display/IRQ/GTs and may trigger driver FLR.

## Dependencies and Integration Points
It is the integration hub for aperture, DRM core, GEM/TTM, display, IRQ, GGTT, GT, GuC, pagefault, VM madvise, BO eviction, PM, PXP, PSMI, OA/PMU, sysfs/debugfs/hwmon, SR-IOV, survivability, workarounds, NVM, HECI, VSEC, and PCI probe/remove code.

## Risks
Probe ordering is fragile: display must own the first allocation after TTM managers, FLR cleanup is registered only after certain init steps, and many later subsystems assume tiles/GTs/VRAM are ready. Runtime PM must wrap ioctls, faults, debugfs, and memory access correctly. Wedged-mode changes affect recovery semantics and reset policy. Remove/shutdown must prevent new users while preserving exported BO data as intended.

## Test Signals
PCI probe/remove fault injection, runtime PM ioctl/mmap tests, open/close leak checks, ASID allocation wrap tests under debug config, suspend/shutdown FLR behavior, wedged uevent tests, debugfs/sysfs registration, display-first allocation assertions, SR-IOV PF/VF probe modes, and cache-flush helper tests are strong signals.
