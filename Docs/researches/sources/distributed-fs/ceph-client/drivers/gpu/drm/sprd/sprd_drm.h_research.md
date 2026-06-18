# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_drm.h

Purpose: shared master declarations for the SPRD DRM module.

Important APIs and types: `struct sprd_drm` embeds the DRM device. The header declares extern platform drivers `sprd_dpu_driver` and `sprd_dsi_driver` so `sprd_drm.c` can register them as one driver set.

Control flow: included by the master, DPU, and DSI sources for shared driver state and logging/atomic headers.

State and persistence: no storage; it defines the top-level DRM container type.

Dependencies and integration: includes DRM atomic and print headers.

Risks: because subdriver symbols are extern declarations, the Makefile must link the matching objects into the same module.

Test signals: module link/build and probe registration.
