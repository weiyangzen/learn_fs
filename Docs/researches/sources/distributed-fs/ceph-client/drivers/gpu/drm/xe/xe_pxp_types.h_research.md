<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_types.h

Purpose: defines PXP state and resource structures shared by the PXP implementation, submit code, and debugfs.

Important types: `enum xe_pxp_status` models lifecycle and error states; `struct xe_pxp_gsc_client_resources` stores GSCCS VM/BO/queue and mapped batch/in/out buffers; `struct xe_pxp` stores device/GT pointers, VCS resources, GSC resources, protected queue list plus spinlock, status mutex, activation/termination completions, key-instance counters, and IRQ workqueue/event state.

State behavior: `key_instance` is the current protected-content generation and `last_suspend_key_instance` helps avoid redundant suspend cleanup. IRQ event flags `PXP_TERMINATION_REQUEST` and `PXP_TERMINATION_COMPLETE` are latched under the device IRQ lock and drained by ordered work.

Risks and test signals: locking rules are split between mutex state, queue spinlock, and IRQ spinlock. Tests should assert list initialization/removal, completion reinitialization, and event flag behavior across concurrent termination and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_types.h -->
