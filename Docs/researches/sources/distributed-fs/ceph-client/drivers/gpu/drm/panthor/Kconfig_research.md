# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/Kconfig

`panthor/Kconfig` declares `DRM_PANTHOR`, the tristate build option for the Panthor DRM driver targeting ARM Mali CSF-based Valhall and Immortalis GPUs.

The symbol depends on DRM, ARM or ARM64 or COMPILE_TEST, `!GENERIC_ATOMIC64` for `IOMMU_IO_PGTABLE_LPAE`, and MMU. It selects `DEVFREQ_GOV_SIMPLE_ONDEMAND`, `DRM_EXEC`, `DRM_GEM_SHMEM_HELPER`, `DRM_GPUVM`, `DRM_SCHED`, `IOMMU_IO_PGTABLE_LPAE`, `IOMMU_SUPPORT`, and `PM_DEVFREQ`.

Control flow is build-time only: when enabled, the Makefile links the Panthor composite object. The help text scopes this driver to CSF GPUs and explicitly notes Mali-G68/G78 remain with Panfrost despite being Valhall-family parts.

The file has no runtime state. Its persistent effect is kernel configuration and dependency availability. Integration is with the DRM Kconfig menu and `obj-$(CONFIG_DRM_PANTHOR)` in the Makefile. Risks are missing dependencies or overly broad architecture enablement causing build/runtime failures. Test signals are `=m`, `=y`, ARM, ARM64, and COMPILE_TEST builds, plus config combinations that prove required DRM/IOMMU/devfreq helpers are selected.
