# sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/Makefile

Purpose: composes the Apple Display Pipe DRM modules.

Important APIs/types/functions: defines `adpdrm-y := adp_drv.o`, `adpdrm-mipi-y := adp-mipi.o`, and builds both objects under `CONFIG_DRM_ADP`.

Control flow: one Kconfig symbol emits the main DRM/KMS platform driver and a MIPI DSI host/bridge companion; runtime component matching joins them through OF graph data.

State/persistence: build-time state only.

Dependencies/integration: connects `adp_drv.c` and `adp-mipi.c` through Kbuild and `CONFIG_DRM_ADP`.

Risks: both modules are controlled together, so missing device-tree nodes can cause component bind failure; source renames require Makefile updates.

Test signals: build `DRM_ADP=y/m` and boot with matching display-pipe and MIPI nodes.
