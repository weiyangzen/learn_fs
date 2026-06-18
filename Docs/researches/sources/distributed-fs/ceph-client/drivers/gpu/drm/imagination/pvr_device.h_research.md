# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device.h

Purpose: defines core PowerVR device/file structures, feature/quirk access macros, register accessors, UAPI padding validation, and device lifecycle declarations.

Important APIs/types: `struct pvr_gpu_id`, `struct pvr_fw_version`, `struct pvr_device_data`, and large `struct pvr_device` wrap DRM device state, hardware identity, firmware state, clocks, power domains, reset/pwrseq, IRQ, FWCCB/KCCB, kernel VM, queues, watchdog, context/free-list/job xarrays, reset semaphore, scheduler workqueue, and safety-event flag. `struct pvr_file` stores per-open xarrays and context list. Macros expose features/quirks/enhancements, convert between DRM/PVR types, pack BVNC, read/write/poll control registers, and validate union padding.

Control flow and state: this header defines the persistent state shared across the driver. `reset_sem` protects firmware command paths from reset/lost-device races. KCCB state includes return slots, reserved slots, waiters, and fence context. Per-file state owns user handles for contexts, free lists, HWRT datasets, and VM contexts.

Dependencies and integration: includes DRM device/file/mm headers, Linux IO/polling/locks/workqueue/xarray, CCB, firmware, stream, and device-info headers.

Risks: structure fields are cross-module contracts. Register accessors assume `pvr_dev->regs` is mapped and powered. `PVR_FEATURE_VALUE()` silently leaves output untouched when absent and returns `-EINVAL`; callers must initialize defaults.

Test signals: full-driver builds, probe/runtime paths using register access, UAPI validation tests for union padding, and reset/job tests exercising `reset_sem` semantics.
