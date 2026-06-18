# sources/distributed-fs/ceph-client/include/drm/drm_fbdev_shmem.h

Purpose: Provides the fbdev-emulation probe hook macro for drivers using shmem GEM backing storage.

Important APIs, types, and functions: With `CONFIG_DRM_FBDEV_EMULATION`, declares `drm_fbdev_shmem_driver_fbdev_probe()` and defines `DRM_FBDEV_SHMEM_DRIVER_OPS` to install it as `.fbdev_probe`. Without fbdev emulation, the macro sets `.fbdev_probe = NULL`.

Control flow: Shmem GEM drivers compose this macro into `struct drm_driver`. The fbdev helper calls the probe callback to create the fbdev surface and DRM framebuffer backed by shmem GEM objects.

State and persistence: No state is stored in the header. Runtime state lives in fb helper structures and shmem GEM objects.

Dependencies and integration points: Integrates with DRM fb helper, shmem GEM helpers, driver fbdev callbacks, and Kconfig.

Risks and test signals: Risks include fbdev being unavailable in no-emulation builds, using shmem fbdev paths without CPU mapping support, and damage flushing assumptions for shadow-backed buffers. Test fbdev emulation enabled/disabled builds, fbcon output, mmap/write behavior, hotplug reconfiguration, and shmem object cleanup.
