# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi.h

Purpose: This header is the central public contract for MSM DSI core, manager, host, and PHY integration.

Important APIs and types: It defines DSI ids (`DSI_0`, `DSI_1`, `DSI_MAX`), PHY use cases for standalone/master/slave, `struct msm_dsi`, shared PHY timing and clock request structs, manager functions, host functions, and PHY driver/control functions. Host declarations cover command transfer, power, IRQ, mode, DSC checks, registration, clocks, TX buffers, snapshots, and test patterns.

Control flow and state: `struct msm_dsi` is the per-controller object shared across driver, manager, host, PHY, and KMS. The manager uses ids and PHY use cases for bonded configuration. Host functions take `mipi_dsi_host *`, allowing MIPI DSI core callbacks to use MSM-specific implementation through `container_of`.

Dependencies and integration: It includes platform/OF and DRM bridge/CRTC/MIPI DSI headers plus MSM display snapshot support. It is included by `dsi.c`, `dsi_manager.c`, `dsi_host.c`, `dsi_cfg.c`, and PHY code.

Risks and test signals: The header exposes a wide internal surface, so signature or state changes can affect multiple layers. Compile coverage is essential; runtime signals include host registration, panel attach/detach, command transfers, PHY enable/disable, bonded DSI, DSC/wide-bus, and mode validation.
