<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/Makefile

Purpose: Defines the object list for the i.MX8 DC DRM module.

Important APIs/types/functions: Builds `imx8-dc-drm.o` from DC sub-block implementations: constframe, CRTC, display engine, driver, extdst, framegen, fetchlayer, fetchunit, fetchwarp, interrupt controller, KMS, layerblend, pixel engine, plane, and timing controller.

Control flow: Kbuild aggregation only.

State and persistence behavior: No runtime state.

Dependencies: Must stay synchronized with exported `struct platform_driver` objects and cross-file symbols declared in `dc-drv.h`, `dc-de.h`, `dc-fu.h`, and `dc-pe.h`.

Integration points: Selected by `CONFIG_DRM_IMX8_DC`.

Risks: Omitting an object can leave platform drivers or helper functions undefined; adding dead objects can create unused-driver build issues.

Test signals: Link success for `CONFIG_DRM_IMX8_DC=m/y` and module load probing all subdrivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/Makefile -->
