## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_drm_drv.c

### Purpose

`mtk_drm_drv.c` is the main MediaTek DRM/KMS driver. It defines SoC display paths, registers all MediaTek display sub-drivers, builds component matches from hardcoded data or OF graphs, coordinates one or more MMSYS/VDOSYS instances into a DRM device, initializes mode config, creates CRTCs, sets DMA allocation device, registers DRM, and handles system suspend/resume and shutdown.

### Important APIs, types, and functions

Important data includes path arrays for MT2701, MT7623, MT2712, MT8167, MT8173, MT8183, MT8186, MT8188, MT8192, and MT8195, plus `struct mtk_mmsys_driver_data` instances that define path lengths, connector routes, mmsys IDs, multi-MMSYS counts, shadow-register support, and width/height limits.

Core functions are `mtk_drm_kms_init()`, `mtk_drm_kms_deinit()`, `mtk_drm_bind()`, `mtk_drm_unbind()`, `mtk_drm_of_get_ddp_ep_cid()`, `mtk_drm_of_ddp_path_build_one()`, `mtk_drm_of_ddp_path_build()`, `mtk_drm_probe()`, `mtk_drm_remove()`, `mtk_drm_shutdown()`, and PM callbacks. The DRM driver uses GEM DMA helpers and a custom `fb_create` that rejects multi-plane framebuffers.

### Control flow

Module init registers all component platform drivers and the main DRM platform driver. Probe identifies the parent MMSYS compatible, copies path data when OF graph paths are present, optionally builds paths by walking graph endpoints, allocates the cross-MMSYS private pointer array, creates an OVL adaptor pseudo-device if the path needs one, scans sibling display nodes for known DDP components, stores component nodes, initializes DDP component descriptors, finds the matching mutex node, enables PM, and registers a component master.

Master bind finds the mutex platform device, marks this DRM node bound, waits until all required MMSYS instances are bound, allocates the DRM device once on the master, points all MMSYS private structures to it, initializes KMS, removes conflicting firmware apertures, registers DRM, and starts DRM clients. KMS init initializes mode config, binds all components for every MMSYS instance, creates CRTCs in main/ext/third order, sets cursor size, chooses the first CRTC OVL DMA device for GEM allocation, sets max segment size, initializes vblank and polling, and resets mode config.

### State and persistence behavior

`struct mtk_drm_private` persists per mediatek-drm platform device and stores the DRM device pointer, bound/master flags, mutex/mmsys devices, component nodes, component descriptors, SoC data, suspend atomic state pointer, mailbox index, and all-MMSYS private array. DRM device state persists registered CRTCs, connectors, planes, vblank, GEM DMA settings, and mode config. System suspend uses `drm_mode_config_helper_suspend()` only from the DRM master, and complete resumes through DRM helpers.

### Dependencies

The driver depends on Linux component, OF graph, platform, PM runtime, DMA mapping, aperture removal, and DRM core/atomic/GEM/DMA/fbdev/vblank helpers. It depends on all MediaTek component drivers declared in `mtk_drm_drv.h`, on `mtk_crtc_create()`, `mtk_crtc_dma_dev_get()`, `mtk_ddp_comp_init()`, and OVL adaptor graph detection.

### Integration points

This file is the central integration point for the entire MediaTek DRM stack. It registers sub-drivers, maps DT compatibles to DDP component types, builds display pipelines, creates pseudo OVL adaptor devices, coordinates multiple VDOSYS devices for MT8188/MT8195, binds encoders/connectors through component drivers, and exposes the final DRM device to userspace.

### Risks

Multi-MMSYS bind ordering is subtle: non-master binds can return success without registering DRM until all instances are present. `mtk_drm_get_all_drm_priv()` indexes `all_drm_priv` by path type and assumes all expected instances can be found. Graph path building treats the final output component specially and suppresses duplicate OVL adaptor entries; malformed graphs can fail late. `mtk_drm_kms_deinit()` unbinds only `drm->dev`, whereas init bound all MMSYS devices, so multi-device cleanup depends on surrounding paths and should be reviewed if changed. Only single-plane framebuffer creation is allowed.

### Test signals

Signals include boot and DRM registration on each compatible, graph-built and hardcoded path systems, multi-MMSYS MT8188/MT8195 bringup, CRTC creation order, connector route selection, OVL adaptor pseudo-device creation, fbdev/client setup, PRIME import with contiguous IOVA, vblank init, suspend/resume, shutdown, and failure injection around missing mutex/component nodes.
