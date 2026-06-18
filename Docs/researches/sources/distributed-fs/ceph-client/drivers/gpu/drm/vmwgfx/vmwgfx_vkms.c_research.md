# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_vkms.c

Purpose: Adds optional virtual vblank and CRC support to vmwgfx screen-target display for DRM timing and pipe CRC tests.

Important APIs/types: `vmw_vkms_init()`, cleanup, vblank enable/disable/timestamp callbacks, CRTC atomic hooks, CRC source functions, `vmw_vkms_set_crc_surface()`, and modeset/vblank lock helpers.

Control flow: Init reads `guestinfo.vmwgfx.vkms_enable`, initializes DRM vblank, and creates an ordered CRC workqueue. Vblank enable starts an hrtimer. The timer advances frame count, calls DRM vblank handling, tries to lock against modeset, and queues CRC work. The worker references the current surface, cleans/synchronizes it, maps the backup BO, computes crc32 per row, and emits CRC entries for pending frames.

State/persistence: Per-DU VKMS state includes timer, period, CRC surface reference, atomic lock, pending frame range, spinlock, and work item. Device state stores enablement and workqueue.

Dependencies/integration: DRM vblank/CRC APIs, KMS DUs, surfaces/resources/BO mapping, guestinfo, hrtimer, workqueue, dma fences, and crc32.

Risks/test signals: Timer vs modeset locking, surface reference races, cleanup with queued work, missing backup BOs, CRC worker backlog, IGT CRC/vblank tests, and guestinfo-disabled fallback.
