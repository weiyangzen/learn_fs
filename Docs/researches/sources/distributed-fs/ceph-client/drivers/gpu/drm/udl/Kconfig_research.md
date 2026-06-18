<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/Kconfig

Purpose: Defines the `DRM_UDL` option for USB DisplayLink KMS adapters.

Important APIs/types/functions: The tristate depends on `DRM`, `USB`, `USB_ARCH_HAS_HCD`, and `MMU`; it selects `DRM_CLIENT_SELECTION`, `DRM_GEM_SHMEM_HELPER`, and `DRM_KMS_HELPER`.

Control flow: Enables building the `udl` module/driver.

State and persistence: Build-time metadata only.

Dependencies and integration points: Captures the driver's reliance on USB host support, MMU, shmem GEM, KMS helpers, and client setup.

Risks and test signals: Build matrix should include module and built-in variants, USB-enabled configs, and `COMPILE_TEST`-style coverage where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/Kconfig -->
