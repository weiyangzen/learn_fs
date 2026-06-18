<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_types.h

## Purpose
`xe_device_types.h` defines the central top-level Xe driver state containers: `struct xe_device` for the DRM device and `struct xe_file` for per-open-file state. It is the shared type contract used by almost every Xe subsystem.

## Important APIs, types, and functions
`enum xe_wedged_mode` defines recovery policy. `struct xe_device` embeds `struct drm_device`, optional display pointer, device coredump, `info` platform/IP/capability flags, active workaround bitmap, survivability, IRQ/MSI-X state, TTM device, global MMIO mapping, memory managers, SR-IOV PF/VF state, USM ASID/page-fault queues, pinned BO lists, workqueues, tile array, memory-access tracking, PAT tables, D3cold policy, PM notifiers, telemetry/remapper state, HECI/GSC, late bind, OA, PXP, wedged state, async BO free state, PMU, RAS, I2C, SVM timeslices, validation domain, and KUnit hooks. `struct xe_file` stores the owning device, DRM file, VM and exec-queue xarrays plus locks, per-engine-class run ticks, client accounting object, process identity, and kref.

## Control flow and integration points
This header has no functions, but its layout governs initialization, teardown, fdinfo, VM binding, exec queue lookup, PM, SR-IOV, memory management, RAS, and display compatibility. Many helpers in `xe_device.h` and subsystem modules directly dereference these fields.

## State and persistence behavior
Most persistent driver state for a live PCI function is anchored here. Device capability flags remain fixed after probe. xarrays, workqueues, lists, locks, atomics, notifiers, and counters persist until remove. `xe_file` state persists until the DRM file is closed and asynchronous queue destruction has drained.

## Dependencies, risks, and test signals
Dependencies include DRM core/file, TTM, platform/step types, tile, page fault, PMU, SR-IOV, survivability, RAS, OA, validation, and display compatibility shims. Risks are layout coupling, lock-order mistakes, missing initialization of nested locks/lists, stale capability flags, and UAF around per-file xarrays. Test signals include full probe/remove, open/close stress, VM and exec queue creation/destruction, SR-IOV PF/VF tests, fdinfo accounting, runtime PM, suspend/resume, error recovery, and KUnit/debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_types.h -->
