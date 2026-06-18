# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_gem.h

Purpose: declares Rocket GEM object state and GEM ioctl entry points.

Important APIs and types: `struct rocket_gem_object` embeds `drm_gem_shmem_object` and stores owner file private data, IOMMU domain, DRM MM node, mapped size, and offset. It declares create/prep/fini ioctl functions and `to_rocket_bo`.

Control flow: `rocket_drv.c` installs `rocket_gem_create_object` in the DRM driver; `rocket_gem.c` uses the container helper to manage BO state.

State and persistence: fields persist per BO until GEM free, while the IOMMU domain ref can outlive the file's base reference through BO ownership.

Dependencies and integration: depends on DRM shmem helpers and `rocket_file_priv` declarations from `rocket_drv.h`.

Risks and test signals: ensure object embedding matches shmem helper expectations, and check that all paths initialize `driver_priv`, `domain`, and `mm` before free can run.
