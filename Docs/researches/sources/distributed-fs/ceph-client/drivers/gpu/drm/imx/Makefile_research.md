<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/Makefile

Purpose: Routes selected i.MX DRM build options to their subdirectories.

Important APIs/types/functions: Adds `dc/` for `CONFIG_DRM_IMX8_DC`, `dcss/` for `CONFIG_DRM_IMX_DCSS`, `ipuv3/` for `CONFIG_DRM_IMX`, and `lcdc/` for `CONFIG_DRM_IMX_LCDC`.

Control flow: Kbuild object-directory selection only.

State and persistence behavior: No runtime state.

Dependencies: Relies on matching Kconfig symbols and subdirectory Makefiles.

Integration points: Integrated with Linux Kbuild under the DRM driver tree.

Risks: Symbol mismatch causes configured drivers not to build.

Test signals: Kernel build with each config symbol enabled, including allmodconfig/allyesconfig coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/Makefile -->
