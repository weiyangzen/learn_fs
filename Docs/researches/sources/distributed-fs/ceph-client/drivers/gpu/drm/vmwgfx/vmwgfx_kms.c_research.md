# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_kms.c

## Purpose
`vmwgfx_kms.c` provides the common KMS/display-mode infrastructure for vmwgfx display units. It implements atomic state helpers, framebuffer creation for BO-backed and surface-backed scanout, topology validation and layout updates, present/readback dispatch, dirty/plane update helpers, suspend/resume, mode enumeration, and `vmw_user_object` utilities shared by display paths.

## Important APIs, Types, and Functions
- Display-unit helpers include `vmw_du_init()`, `vmw_du_cleanup()`, plane/crtc/connector duplicate/reset/destroy functions, `vmw_du_primary_plane_atomic_check()`, and `vmw_du_crtc_atomic_check()`.
- Framebuffer paths are `vmw_kms_new_framebuffer_surface()`, `vmw_kms_new_framebuffer_bo()`, `vmw_kms_new_framebuffer()`, and `vmw_kms_fb_create()`.
- Mode/configuration paths include `vmw_kms_check_display_memory()`, `vmw_kms_check_implicit()`, `vmw_kms_check_topology()`, `vmw_kms_atomic_check_modeset()`, `vmw_kms_init()`, and `vmw_kms_close()`.
- Present/readback helpers are `vmw_kms_present()`, `vmw_kms_readback()`, `vmw_kms_helper_dirty()`, `vmw_kms_helper_validation_finish()`, and `vmw_du_helper_plane_update()`.
- Layout and connector helpers include `vmw_du_update_layout()`, `vmw_kms_update_layout_ioctl()`, `vmw_du_connector_detect()`, `vmw_connector_mode_valid()`, and `vmw_connector_get_modes()`.
- `vmw_user_object_*()` helpers abstract whether a display object is a raw BO or a surface with guest-memory backing.

## Control Flow
KMS init configures DRM mode limits, framebuffer creation, atomic check/commit callbacks, suggested-offset and hotplug properties, then tries screen-target, screen-object, and legacy display init in order. Framebuffer creation looks up a userspace object, validates dimensions/format/modifier, creates either a surface or BO framebuffer, attaches dirty tracking, and drops lookup references. Atomic checking validates plane scaling, primary presence, connector masks, implicit display-unit constraints, topology memory, screen-target per-output limits, and bounding-box memory. Present/readback dispatch by active display unit to STDU or SOU helpers and flushes SVGA commands after present.

## State and Persistence Behavior
The file manages in-memory DRM mode_config state, display-unit preferred layout (`pref_width`, `pref_height`, `pref_active`, `gui_x`, `gui_y`), connector properties/status, framebuffer references, BO dirty trackers, surface dirty/coherent flags, suspend atomic state, and temporary validation contexts/fences for dirty updates. Layout changes are runtime state announced through DRM hotplug events; no filesystem persistence exists.

## Dependencies and Integration Points
It depends on DRM atomic/modeset helpers, damage helpers, framebuffer helpers, vmwgfx STDU/SOU/LDU backends, BO/resource validation, surface dirty tracking, `vmwgfx_execbuf.c` fence helpers, SVGA registers, `vmwgfx_vkms` CRC work, and user object lookup from vmwgfx resource/BO layers.

## Risks
Topology validation must prevent integer overflow and memory overcommit while still matching virtual hardware limits. Surface framebuffers require scanout metadata and one-level 2D dimensions. Dirty tracking coherence between BOs and surfaces is subtle. Plane update FIFO-size callbacks must not under-reserve; the helper commits zero bytes if calculated submit size exceeds reservation. Suspend/resume depends on a saved atomic state and warns if resume is called without suspend. User-object helpers must maintain correct references across BO-backed dumb surfaces and surface-backed framebuffers.

## Test Signals
Exercise KMS init fallback order, framebuffer creation with invalid handles/formats/modifiers/sizes, surface scanout metadata rejection, atomic modesets with implicit units and topology bounds, layout ioctl overflow and memory-limit failures, STDU/SOU present/readback, dirtyfb damage clipping, plane update command-size accounting, suspend/resume/lost-device paths, and connector mode enumeration under different max width/height limits.
