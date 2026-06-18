<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_drv.h

Purpose: Central V3D internal header defining core device/file/BO/job/fence/perfmon/stat structures, register access macros, queue enums helpers, wait helpers, and cross-module prototypes.

Important APIs/types/functions: Defines `V3D_MAX_QUEUES`, `v3d_queue_to_string()`, `struct v3d_stats`, `v3d_queue_state`, `v3d_perfmon`, generation enum, IRQ enum, `struct v3d_dev`, `v3d_file_priv`, `v3d_bo`, `v3d_fence`, base job and specialized bin/render/TFU/CSD/CPU jobs, query metadata, submit extension state, `wait_for()` helper, `nsecs_to_jiffies_timeout()`, and prototypes for all V3D modules.

Control flow: Other compilation units share these definitions to coordinate scheduler jobs, IRQ signaling, MMU mapping, perfmon activation, BO lifetime, reset, and ioctls.

State and persistence: Describes nearly all V3D runtime state: register mappings, page table, scratch page, DRM MM, work item, queues, active jobs, locks, stats, perfmons, and global reset counter.

Dependencies and integration points: Includes DRM GEM shmem, DRM scheduler, Linux locks/workqueue, performance counter descriptors, and V3D UAPI.

Risks and test signals: Struct layout and locking contracts are high blast-radius. Risks include queue enum mismatch, timeout overflow, stale prototypes, and active-job lifetime bugs. Test signals are full-driver build, lockdep under job submission/reset, fdinfo stats, and KASAN/KCSAN during open/close/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_drv.h -->
