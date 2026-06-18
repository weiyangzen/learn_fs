<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/Makefile

Purpose: Defines the object composition for the i.MX DCSS DRM module.

Important APIs/types/functions: Builds `imx-dcss.o` from driver, device, block-control, context-loader, DTG, subsampler, DPR, scaler, KMS, CRTC, and plane objects.

Control flow: Kbuild aggregation only.

State and persistence behavior: No runtime state.

Dependencies: Object list must match implemented DCSS submodules and cross-file symbols declared in `dcss-dev.h`/`dcss-kms.h`.

Integration points: Selected by `CONFIG_DRM_IMX_DCSS`.

Risks: Omitting submodule objects causes unresolved symbols or missing hardware programming. Including stale objects can break builds.

Test signals: Build/link success for `CONFIG_DRM_IMX_DCSS=m/y` and module probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/Makefile -->
