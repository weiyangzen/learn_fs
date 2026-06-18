# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_drm_drv.c

Purpose: master DRM platform driver for Kirin display. It coordinates OF graph/component binding, allocates the DRM device, initializes mode config, private CRTC/plane hardware data, vblank, polling, DRM registration, and cleanup.

Important APIs/functions: `kirin_drm_platform_probe()` finds the remote graph node and registers a component master. `kirin_drm_bind()` allocates and registers the DRM device. `kirin_drm_kms_init()` initializes mode config, private display controller objects, binds subdrivers, initializes vblank, resets state, and starts polling. `kirin_drm_private_init()` allocates `kirin_drm_private`, hardware context, planes, and CRTC.

Control flow: platform probe creates component match for the downstream device. Component bind gets `kirin_drm_data` from OF match, allocates DRM, initializes KMS, registers DRM, and starts clients. Unbind unregisters DRM, shuts down atomics, cleans private data, unbinds components, and drops the device.

State and persistence: `struct kirin_drm_private` contains one CRTC, up to two planes, and `hw_ctx`. DRM state lives in mode config and object state. No persistent storage.

Dependencies and integration points: depends on component framework, OF graph, DRM OF helpers, GEM DMA, vblank, and ADE driver data. DSI is expected as a component through graph matching.

Risks: `dev->mode_config.max_height` is assigned `driver_data->config_max_width` instead of `config_max_height` in this tree. `kirin_drm_crtc_init()` calls `of_node_put(port)` before assigning `crtc->port = port`, which is suspicious for node lifetime. Cleanup assumes `dev_private` is set and driver data cleanup is safe.

Test signals: OF graph probe, component bind/unbind order, DRM registration, mode config dimensions, vblank init, shutdown path, and DSI bridge attachment.
