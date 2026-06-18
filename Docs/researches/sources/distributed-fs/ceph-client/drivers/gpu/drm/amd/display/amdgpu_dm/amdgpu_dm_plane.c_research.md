# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.c

### Purpose
`amdgpu_dm_plane.c` implements AMDGPU DM DRM plane support. It advertises plane formats/modifiers, translates DRM framebuffer and plane state into DC plane attributes, pins/unpins scanout buffers, validates scaling and DCC, handles async cursor updates, initializes plane properties, and manages per-plane color-management state.

### Important APIs, Types, And Functions
Exported helpers include `amdgpu_dm_plane_init`, `amdgpu_dm_plane_fill_plane_buffer_attributes`, `amdgpu_dm_plane_fill_dc_scaling_info`, `amdgpu_dm_plane_helper_check_state`, `amdgpu_dm_plane_get_cursor_position`, `amdgpu_dm_plane_handle_cursor_update`, `amdgpu_dm_plane_fill_blending_from_plane_state`, `amdgpu_dm_plane_get_format_info`, and `amdgpu_dm_plane_is_video_format`. Internal logic covers per-family modifier construction for GFX9/GFX10/GFX11/GFX12, DCC validation, framebuffer prepare/cleanup, atomic check/async check/update, panic flush, state duplicate/destroy, format-modifier filtering, and color property handling.

### Control Flow
Plane initialization builds format and modifier lists from DC plane caps and ASIC family, registers a universal DRM plane, attaches zpos, alpha/blend, YUV color, rotation, damage, helper, and color pipeline properties, then resets the state. Atomic check validates viewport/scaling, rejects incompatible plane color pipeline and CRTC degamma use, fills DC scaling info, and calls `dc_validate_plane`. Prepare-fb reserves and pins the BO, allocates GART backing, calls DRM GEM prepare, records the GPU address, references the BO, and fills DC buffer attributes for newly created DC plane states. Cleanup reverses pin/ref state. Async cursor updates swap framebuffer state and program DC cursor attributes/position under `dc_lock`.

### State, Persistence, And Dependencies
State lives in `dm_plane_state` and referenced `dc_plane_state`, DRM plane state fields, framebuffer `amdgpu_framebuffer` address/tiling/TMZ metadata, BO pin counts, color-management blobs, and CRTC cursor dimensions. There is no filesystem persistence. Dependencies include DRM atomic helpers, GEM/TTM reservation and pinning, AMDGPU tiling/modifier macros, DC plane/cursor/scaling/DCC APIs, tracepoints, and optional private color or DRM color pipeline support.

### Integration Points
The file is used by AMDGPU DM device initialization and atomic commit/check paths. It integrates with framebuffer creation, DC resource validation, cursor programming, panic scanout recovery, color management, and userspace-visible DRM plane capabilities. `amdgpu_dm_plane.h` exposes the helpers to the rest of DM.

### Risks
Modifier lists must match both display hardware and render-driver expectations; incorrect DCC/swizzle restrictions can cause corruption or reject valid buffers. BO pin/unpin/ref paths must stay balanced across prepare failures and cleanup. Scaling validation includes hardware-specific workarounds such as rejecting nonzero NV12 source offsets on DCN1. Cursor updates touch live DC state outside a full modeset and require locking. Color blob duplication/destruction must retain and release blobs correctly.

### Test Signals
Run IGT/KMS atomic plane, cursor, async cursor, format/modifier, framebuffer damage, rotation, scaling, writeback/scanout, and panic-flush scenarios across GFX8 through GFX12. Validate NV12/P010 and FP16 formats, DCC and linear buffers, TMZ surfaces, BO pin failure paths, color pipeline properties, and suspend/resume with pinned scanout buffers.
