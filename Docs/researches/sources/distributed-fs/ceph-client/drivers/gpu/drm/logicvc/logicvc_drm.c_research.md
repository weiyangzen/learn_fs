# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_drm.c

Purpose: platform-driver core for LogiCVC. It owns probe/remove/shutdown, DRM driver registration, regmap setup, reserved memory handling, clocks, IRQ handling, device-tree config parsing, and top-level component initialization.

Important APIs/types/functions: `logicvc_drm_probe`, `logicvc_drm_remove`, `logicvc_drm_shutdown`, `logicvc_drm_irq_handler`, `logicvc_drm_gem_dma_dumb_create`, `logicvc_drm_config_parse`, `logicvc_clocks_prepare/unprepare`, and caps matching.

Control flow: probe initializes reserved memory, obtains parent syscon regmap or maps MMIO and creates regmap, requests IRQ, allocates `logicvc_drm`, matches IP version, prepares clocks, parses DT config and layers count, initializes DRM mode config, layers, CRTC, interface, KMS mode config, registers the DRM device, and starts client setup. Remove unregisters, performs atomic shutdown, finalizes mode polling, disables clocks, and releases reserved memory.

State and persistence: `struct logicvc_drm` stores caps, parsed config, regmap, reserved memory base, clocks, layer list, CRTC, and interface. Hardware registers persist until shutdown or next modeset.

Dependencies and integration points: platform OF matching for `xylon,logicvc-*`, Linux reserved memory, syscon/regmap MMIO, clocks, DRM GEM DMA/fbdev helpers, and local layer/CRTC/interface/mode/OF helpers.

Risks and test signals: error unwinding must disable clocks and release reserved memory. Parent syscon fallback must handle both shared and direct register mappings. Test probe deferral for panels/bridges, missing clocks/IRQ/layers, dumb buffer pitch, IRQ vblank delivery, and remove/shutdown.
