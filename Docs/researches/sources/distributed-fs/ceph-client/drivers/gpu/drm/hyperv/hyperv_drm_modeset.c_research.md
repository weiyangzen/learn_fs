# sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm_modeset.c

Purpose: implements KMS objects for Hyper-V synthetic video: virtual connector, primary shadow plane, CRTC, encoder, mode config, VRAM blitting, dirty rectangle notifications, and panic scanout support.

Important APIs/functions: `hyperv_mode_config_init()` initializes DRM mode config and one pipe. Plane update iterates damage clips, copies shadow framebuffer data into `hv->vram`, and calls `hyperv_update_dirt()`. CRTC enable hides the host pointer and sends a situation update. Connector mode enumeration creates no-EDID modes up to host-provided maximum and sets preferred mode.

Control flow: top-level probe calls mode config init after VRAM and host resolution setup. Atomic plane check validates no scaling and framebuffer size fits VRAM. Atomic update blits damaged rectangles. CRTC enable sends active mode details and enables vblank. Dirty notifications tell the host which rectangles changed.

State and persistence: KMS state lives in DRM atomic state. The scanout backing is Hyper-V VRAM at `hv->vram`; guest shadow buffers come from GEM shmem. Host display state is updated by VMBus messages.

Dependencies and integration points: depends on DRM shmem shadow plane helpers, format helpers, damage helpers, vblank timer functions, panic helpers, and Hyper-V protocol calls.

Risks: only `DRM_FORMAT_XRGB8888` and linear modifiers are exposed. Plane check uses full framebuffer height for size; mode validity uses pitch derived from width and depth if no fb. `hyperv_plane_atomic_update()` ignores return values from blit and dirty update. Dirty notifications are skipped if host feature flag says not needed.

Test signals: mode enumeration with host preferred resolution, framebuffer size rejection, damage-only updates, full-screen updates, host visible refresh, panic flush, vblank timer behavior, and suspend/resume modeset restore.
