# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_drv.h

Purpose: shares Rocket driver-private per-file and IOMMU domain structures across GEM and job code.

Important APIs and types: defines `struct rocket_iommu_domain` with an IOMMU domain and kref, and `struct rocket_file_priv` with `rocket_device`, domain, `drm_mm`, `mm_lock`, and DRM scheduler entity. Declares `rocket_pm_ops`, `rocket_iommu_domain_get`, and `rocket_iommu_domain_put`.

Control flow: open initializes `rocket_file_priv`; GEM creation uses its domain and allocator; job submission takes domain references; close drops everything after jobs are destroyed.

State and persistence: per-file state persists for a DRM fd. IOMMU domains are refcounted across BOs and jobs.

Dependencies and integration: includes DRM MM and scheduler helpers plus `rocket_device.h`.

Risks and test signals: validate kref balance between file, BOs, and jobs; check `drm_mm` teardown only after BO cleanup; compile-check PM ops export users.
