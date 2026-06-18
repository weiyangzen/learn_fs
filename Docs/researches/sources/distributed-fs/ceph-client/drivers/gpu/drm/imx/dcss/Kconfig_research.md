<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/Kconfig

Purpose: Defines the build option for the i.MX8MQ Display Controller Subsystem DRM driver.

Important APIs/types/functions: `config DRM_IMX_DCSS` is a tristate option selecting IMX IRQSTEER, DRM client/KMS/display/bridge/GEM DMA helpers, and videomode helpers. It depends on DRM and either ARM64 i.MX or compile-test.

Control flow: Kconfig dependency/select logic only.

State and persistence behavior: No runtime state.

Dependencies: DRM, IRQSTEER, videomode helpers, and i.MX/ARM64 or compile-test build environment.

Integration points: Enables the `imx-dcss` module through the local Makefile.

Risks: Missing dependencies surface as link/build failures or runtime missing IRQ infrastructure. Overbroad selects can pull helper code into unexpected builds.

Test signals: `COMPILE_TEST`, ARM64 i.MX defconfig, module build, and allmodconfig coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/Kconfig -->
