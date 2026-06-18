<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/Kconfig

Purpose: Aggregates i.MX DRM display subsystem Kconfig files.

Important APIs/types/functions: Sources `dc/Kconfig`, `dcss/Kconfig`, `ipuv3/Kconfig`, and `lcdc/Kconfig`.

Control flow: Kconfig include flow only.

State and persistence behavior: No runtime state; controls build-time visibility of i.MX DRM options.

Dependencies: Depends on the subdirectory Kconfig files being present and correctly named.

Integration points: Included by the parent DRM Kconfig hierarchy to expose i.MX display drivers.

Risks: Removing or misordering sources can hide drivers from configuration, though ordering here is low risk.

Test signals: `make menuconfig`/`olddefconfig` visibility and build selection for the i.MX subdrivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/Kconfig -->
