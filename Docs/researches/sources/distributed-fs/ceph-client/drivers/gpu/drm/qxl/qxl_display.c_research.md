# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_display.c

Purpose: This file implements QXL KMS display support: virtual CRTCs/connectors, client monitor configuration, primary and cursor planes, framebuffer dirty handling, dumb-shadow handling, mode validation, vblank, and monitor config objects.

Important APIs, types, and functions: Public functions include `qxl_display_read_client_monitors_config()`, `qxl_create_monitors_object()`, `qxl_destroy_monitors_object()`, `qxl_modeset_init()`, and `qxl_modeset_fini()`. Internal helpers cover CRC-validated ROM monitor config copying, connector detect/get_modes, `qxl_primary_atomic_update/disable/check()`, cursor creation/update/move/hide, plane prepare/cleanup, CRTC atomic flush/enable/disable, and monitor config sending.

Control flow: Modeset init creates a host-visible monitors config BO, initializes DRM mode config, creates suggested offset properties and the QXL hotplug property, then builds `qxl_num_crtc` CRTC/output pairs and initializes vblank. Client monitor changes are read from ROM with CRC retry, copied into `client_monitors_config`, update connector suggested offsets under modeset lock, and trigger HPD/hotplug. Atomic primary updates create/destroy the primary host surface as needed, apply cursor state, and draw dirty framebuffer regions into QXL commands. Cursor plane changes create QXL cursor BOs or move/hide via cursor releases.

State and persistence: Persistent runtime state includes `monitors_config_bo`, mapped `monitors_config`, `client_monitors_config`, per-CRTC cursor BOs, `dumb_shadow_bo`, `dumb_heads`, primary BO state, connector properties, and vblank events. Host-visible monitor config address is stored in `ram_header->monitors_config`; it is rebuilt on init/resume.

Dependencies and integration points: Uses DRM atomic helpers, simple encoders, virtual connectors, GEM framebuffer helpers, QXL draw/image/cmd/release/object helpers, CRC32, and QXL protocol monitor structures. It is called from `qxl_drv.c` probe/resume/freeze paths and from the IRQ worker on client monitor config interrupts.

Risks: Client monitor config depends on ROM CRC stability and bounded retries. Dumb-shadow aggregation copies multiple dumb heads into one primary surface and must keep offsets coherent. Cursor BO creation pins and maps user BOs and assumes 64x64 ARGB cursor input. Atomic event handling uses vblank timer helpers rather than hardware vblank.

Test signals: Multi-monitor hotplug through SPICE client changes; modes over VRAM size boundaries; atomic page flips with vblank events; cursor image and move tests; dumb buffer scanout on multiple heads; dirtyfb clipping; suspend/resume monitor object recreation.
