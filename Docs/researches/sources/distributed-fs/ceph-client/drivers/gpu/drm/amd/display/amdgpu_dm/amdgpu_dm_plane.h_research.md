# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.h

### Purpose
`amdgpu_dm_plane.h` declares the AMDGPU DM plane helper API used by connector/CRTC/atomic code to initialize planes, validate state, convert buffer/scaling attributes, update cursors, inspect formats, and derive blending state.

### Important APIs, Types, And Functions
The header exposes `amdgpu_dm_plane_init`, `amdgpu_dm_plane_fill_plane_buffer_attributes`, `amdgpu_dm_plane_fill_dc_scaling_info`, `amdgpu_dm_plane_helper_check_state`, `amdgpu_dm_plane_get_cursor_position`, `amdgpu_dm_plane_handle_cursor_update`, `amdgpu_dm_plane_get_format_info`, `amdgpu_dm_plane_fill_blending_from_plane_state`, and `amdgpu_dm_plane_is_video_format`.

### Control Flow
The header has no runtime control flow. It defines the call contract between DRM atomic paths and DC plane conversion/programming code implemented in `amdgpu_dm_plane.c`.

### State, Persistence, And Dependencies
No state is stored in the header. Function signatures pass DRM plane/framebuffer state, AMDGPU framebuffers, DC tiling/size/DCC/address/scaling structures, and DC plane caps. It includes `dc.h` for DC structure definitions and relies on AMDGPU/DRM types being visible to consumers.

### Integration Points
Consumers include atomic check/commit logic, cursor code, framebuffer state conversion, and plane initialization paths elsewhere in AMDGPU DM. The declarations are part of the source-level interface between DM and the DC library.

### Risks
Signature changes ripple through atomic commit code. The buffer-attribute helper has many out-parameters, so mismatched initialization or caller assumptions can create stale DC plane state.

### Test Signals
Build all AMDGPU DM configurations and run KMS atomic plane/cursor/modifier tests that call through these helpers.
