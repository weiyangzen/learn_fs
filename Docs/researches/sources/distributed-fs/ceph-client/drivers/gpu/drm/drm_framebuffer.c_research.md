# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_framebuffer.c

## Purpose
`drm_framebuffer.c` implements DRM framebuffer object validation, ioctl handling, per-file ownership, lookup, lifetime management, removal from active scanout, dirty forwarding, and debugfs reporting. It is the core path behind ADDFB, ADDFB2, RMFB, CLOSEFB, GETFB, GETFB2, and DIRTYFB.

## Important APIs, Types, And Functions
Major functions include `drm_framebuffer_check_src_coords()`, `drm_mode_addfb()`, `drm_mode_addfb2()`, `drm_internal_framebuffer_create()`, `drm_mode_rmfb()`, `drm_mode_closefb_ioctl()`, `drm_mode_getfb()`, `drm_mode_getfb2_ioctl()`, `drm_mode_dirtyfb_ioctl()`, `drm_fb_release()`, `drm_framebuffer_init()`, `drm_framebuffer_lookup()`, `drm_framebuffer_unregister_private()`, `drm_framebuffer_cleanup()`, `drm_framebuffer_remove()`, and `drm_framebuffer_print_info()`. Important types include `struct drm_framebuffer`, `struct drm_mode_fb_cmd2`, `struct drm_format_info`, `struct drm_file`, and `struct drm_mode_rmfb_work`.

## Control Flow
ADDFB translates legacy bpp/depth to FourCC and delegates to ADDFB2. ADDFB2 validates mode-setting support, dimensions, flags, modifiers, format metadata, per-plane handles, pitches, offsets, and modifier consistency before calling the driver `fb_create` callback; the new framebuffer id is added to the calling file's framebuffer list. RMFB and file release remove framebuffers from the file list, then either drop the final reference or schedule removal from active usage. GETFB/GETFB2 return metadata and only create GEM handles for current DRM master or CAP_SYS_ADMIN callers. DIRTYFB copies clip rectangles from userspace and forwards them to `fb->funcs->dirty`.

## State, Persistence, And Dependencies
Framebuffer state persists as a mode object with a kref, idr registration, `dev->mode_config.fb_list`, per-file `fbs` ownership, GEM object pointers, handle-ref internal flags, immutable format/size/pitch/offset/modifier metadata, and allocator command name. Dependencies include DRM mode object registration, GEM handle accounting, DRM format metadata, atomic and legacy modeset APIs, user copy helpers, debugfs, and driver framebuffer callbacks.

## Integration Points
Userspace KMS APIs create and manage framebuffer ids through these ioctls. Drivers provide `mode_config.funcs->fb_create` and framebuffer funcs for destroy, dirty, and optional handle creation. Plane and CRTC state refer to framebuffer objects; removal must clear those references through atomic or legacy modeset paths. `drm_file_free()` calls `drm_fb_release()` to reap per-file framebuffers on close.

## Risks
Framebuffer lifetime is delicate because the lookup idr holds a weak reference while planes, CRTCs, file lists, and userspace handles hold strong or implied references. Removal can require modeset locks and can hit `-EDEADLK`, so atomic removal retries with a modeset acquire context and may retry by disabling CRTCs if simply clearing planes is invalid. GETFB handle disclosure is intentionally restricted for security. Validation must reject malformed unused planes when modifiers are enabled while tolerating old userspace that did not zero unused fields before modifier support.

## Test Signals
High-value tests cover ADDFB and ADDFB2 validation failures, planar formats with repeated GEM objects, modifier flag consistency, big-endian ADDFB2 restrictions, GETFB/GETFB2 privilege behavior and handle cleanup on partial failure, DIRTYFB clip copying and annotate-copy constraints, RMFB while framebuffer is active on atomic and legacy devices, file close reaping, private framebuffer unregister/cleanup, and debugfs framebuffer output.
