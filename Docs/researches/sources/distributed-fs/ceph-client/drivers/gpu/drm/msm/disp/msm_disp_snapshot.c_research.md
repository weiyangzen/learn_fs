# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/msm_disp_snapshot.c

Purpose: Provides asynchronous display devcoredump capture infrastructure for MSM KMS failures.

Important APIs/functions: `msm_disp_snapshot_init()` initializes `kms->dump_mutex`, creates a kthread worker named `disp_snapshot`, and initializes work. `msm_disp_snapshot_state()` queues snapshot work for a DRM device. `msm_disp_snapshot_state_sync()` allocates `struct msm_disp_state`, initializes it, and captures state while caller holds `dump_mutex`. `_msm_disp_snapshot_work()` serializes capture, optionally prints to console, and publishes the dump through `dev_coredumpm()`. `msm_disp_snapshot_destroy()` tears down the worker and mutex.

Control flow: Fault or debug callers queue `dump_work`. The worker locks `dump_mutex`, captures state through utility code, unlocks, and hands ownership to devcoredump with `disp_devcoredump_read()` and `msm_disp_state_free()` callbacks. The read callback prints the captured state through a DRM coredump printer.

State and persistence: Captured state is an allocated `struct msm_disp_state` containing register blocks and duplicated atomic state. It persists only until devcoredump consumption or replacement. Worker/mutex state lives in `struct msm_kms`.

Dependencies/integration: Depends on DRM printer/coredump helpers, Linux kthread workers, devcoredump, MSM KMS dump fields, and snapshot utility functions.

Risks and test signals: `msm_disp_snapshot_init()` logs worker creation failure but still returns 0, so later queueing must tolerate error pointers/null. The sync function warns if mutex is not held. Test manual snapshot trigger, devcoredump read/free, repeated dumps while one is pending, worker destruction during driver removal, and builds with coredump disabled.
