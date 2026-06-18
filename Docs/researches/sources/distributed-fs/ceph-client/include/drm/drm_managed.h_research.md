# sources/distributed-fs/ceph-client/include/drm/drm_managed.h

Purpose: declares DRM-device-managed resource helpers, mirroring devres-style cleanup but tied to the final `drm_dev_put()` lifetime of a `drm_device`.

Important APIs and types: `drmres_release_t` is a cleanup callback receiving the DRM device and resource pointer. `drmm_add_action()` and `drmm_add_action_or_reset()` register reverse-order release actions, the latter immediately running the action on registration failure. `drmm_release_action()` removes and runs matching actions early. Managed allocators include `drmm_kmalloc()`, `drmm_kzalloc()`, `drmm_kmalloc_array()`, `drmm_kcalloc()`, `drmm_kstrdup()`, and `drmm_kfree()`. `drmm_mutex_init()` registers mutex destruction, and `drmm_alloc_ordered_workqueue()` registers ordered workqueue destruction.

Control flow: drivers allocate resources during probe or mode-config init and register cleanup actions against the DRM device. On final DRM device release, actions run in reverse allocation order. The array helpers check multiplication overflow before allocation; the workqueue macro creates the workqueue and registers cleanup atomically from the caller's perspective.

State and persistence behavior: resources persist until manually freed or until the DRM device's last reference is dropped. Cleanup ordering is stack-like, which lets dependent resources be unwound safely.

Dependencies and integration points: uses Linux GFP allocation, overflow helpers, mutexes, workqueues, and `struct drm_device`. It underpins managed variants such as `drmm_mode_config_init()` and modern DRM probe cleanup patterns.

Risks: resources whose lifetime is shorter than the DRM device still need explicit release. `drmm_add_action_or_reset()` callbacks must tolerate being invoked on partial initialization failure. Workqueue cleanup must happen after queued work is quiesced or designed to be destroyed by the release callback.

Test signals: probe failure unwinding, final `drm_dev_put()` cleanup order, overflow rejection in array allocation, early `drmm_kfree()` and action release, mutex lockdep cleanup, and managed workqueue destruction.
