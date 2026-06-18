# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/Makefile

Purpose: Build rules for Cadence DRM bridge drivers.

Important APIs/types/functions: Builds `cdns-dsi.o` when `CONFIG_DRM_CDNS_DSI` is enabled, with `cdns-dsi-core.o` always included and `cdns-dsi-j721e.o` included when `CONFIG_DRM_CDNS_DSI_J721E` is enabled. Builds `cdns-mhdp8546.o` when `CONFIG_DRM_CDNS_MHDP8546` is enabled, with core and HDCP objects always included and J721E wrapper object conditional on `CONFIG_DRM_CDNS_MHDP8546_J721E`.

Control flow: Kbuild combines per-driver composite objects according to Kconfig symbols. There is no runtime control flow.

State and persistence: No runtime state. Persistent effect is the object list included in a kernel build.

Dependencies and integration: Directly mirrors `cadence/Kconfig` symbols and integrates Cadence DSI and MHDP8546 source files into the DRM bridge build.

Risks: Object-list drift from Kconfig or source-file renames causes build failures. Composite object naming must match module expectations.

Test signals: Build each parent as built-in and module, toggle J721E child symbols, and run clean incremental builds to catch stale object dependencies.
