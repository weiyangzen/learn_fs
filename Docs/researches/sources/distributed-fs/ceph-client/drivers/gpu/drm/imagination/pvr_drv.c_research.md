# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_drv.c

Purpose: provides the main PowerVR DRM platform driver, file lifecycle, ioctl dispatch, device query helpers, user-object copy helpers, probe/remove paths, and module metadata.

Important APIs/functions: ioctl handlers cover BO creation/mmap-offset, device queries, VM context create/destroy, VM map/unmap, context create/destroy, free-list/HWRT dataset create/destroy, and job submission. `pvr_get_uobj()`, `pvr_set_uobj()`, `pvr_get_uobj_array()`, and `pvr_set_uobj_array()` implement size/stride-compatible UAPI copying. `pvr_drm_driver_open()` allocates `pvr_file` and xarrays; `pvr_drm_driver_postclose()` destroys contexts, free lists, HWRT datasets, and VM contexts. `pvr_probe()` allocates the DRM device, initializes power domains, reset semaphore, context/queue/runtime-PM/watchdog/device state, registers DRM, and initializes ID xarrays. `pvr_remove()` reverses that.

Control flow and state: most ioctls enter `drm_dev_enter()` and validate padding/flags before touching device state. Device queries support size-probe calls with null pointers and copy filtered GPU/runtime/quirk/enhancement/heap/static-area data. File state owns per-open handles. Probe sets autosuspend, watchdog, and runtime PM before `pvr_device_init()`.

Dependencies and integration: ties together DRM core, GEM shmem, PowerVR GEM/VM/context/free-list/HWRT/job/queue/power/device modules, OF platform matching, runtime PM, debugfs, and firmware declarations.

Risks: UAPI copy helpers must preserve forward/backward compatibility and zero extended output. `pvr_set_uobj_array()` appears to advance user/source pointers inconsistently in the strided branch, so array-output compatibility paths deserve focused testing. Probe initializes `free_list_ids`/`job_ids` after DRM registration, so early users must not access them before that point.

Test signals: ioctl validation tests for padding, flags, short structs, strided arrays, invalid handles, VM bounds, and job submission; probe/remove and file open/close leak tests; module firmware availability checks.
