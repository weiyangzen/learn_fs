# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_kms.c

Purpose: initializes the DRM device, GEM/fbdev helpers, mode configuration, IRQ handler, atomic check/commit tail, and KMS attach/detach/shutdown lifecycle.

Important APIs/types/functions: `komeda_kms_attach()`, `komeda_kms_detach()`, `komeda_kms_shutdown()`, `komeda_gem_dma_dumb_create()`, KMS IRQ handler, `komeda_kms_check()`, and commit-tail helpers. Defines `komeda_kms_driver` with GEM DMA ops and atomic modesetting.

Control flow: attach allocates managed DRM device, stores `mdev`, initializes mode config, adds private objects, planes, vblank, CRTCs, writeback connectors, requests IRQ, initializes polling, and registers DRM. Atomic check performs modeset checks, adds affected planes, normalizes zpos, then helper plane checks. Commit tail disables modesets, commits active planes, enables modesets, waits for Komeda flip-done flushes, waits DRM flip completion, and cleans planes.

State and persistence: `komeda_kms_dev` embeds `drm_device` and stores CRTCs. Normalized z-order is written into plane states per commit. IRQ registration and DRM device registration persist until detach.

Dependencies/integration: DRM atomic/GEM DMA/fbdev/vblank/probe helpers, Komeda framebuffer, CRTC/plane/private/writeback setup, and chip IRQ event decoding.

Risks: custom `komeda_kms_atomic_commit_hw_done()` waits every active CRTC, so one stuck pipe can delay all commits. Zpos uniqueness is stricter than generic DRM. Cleanup must handle partial attach failures. Test signals: IGT atomic, zpos conflict tests, dumb buffer pitch alignment, IRQ handling, vblank init, attach failure injection, and hot-unplug/remove.
