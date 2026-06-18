# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_color.c

## Purpose
`amdgpu_dm_color.c` translates DRM color-management state into AMD DC color-programming structures. It supports legacy DRM CRTC degamma/CTM/gamma properties, optional AMD private plane/CRTC properties, and the newer DRM plane colorop pipeline, mapping each into DC transfer functions, gamut matrices, shaper/blend LUTs, HDR multipliers, and 3D LUT state.

## Important APIs, Types, And Functions
Public entry points are `amdgpu_dm_init_color_mod`, `amdgpu_dm_create_color_properties` under `AMD_PRIVATE_COLOR`, `amdgpu_dm_verify_lut3d_size`, `amdgpu_dm_verify_lut_sizes`, `amdgpu_dm_check_crtc_color_mgmt`, `amdgpu_dm_update_crtc_color_mgmt`, and `amdgpu_dm_update_plane_color_mgmt`. Key helpers extract DRM LUT blobs, detect linear LUT bypasses, convert DRM LUT formats into `dc_gamma`, convert DRM CTMs into DC `fixed31_32`, select DC predefined transfer functions, and pack DRM 17-cube 3D LUT data into DC tetrahedral arrays.

## Control Flow
CRTC validation checks LUT sizes, computes regamma, and records whether CRTC degamma must later be mapped onto a plane. CRTC update configures stream regamma and gamut remap. Plane update validates 3D LUT support, initializes input transfer bypass, tries AMD private plane degamma, rejects simultaneous plane and CRTC degamma use, maps CRTC degamma to the plane when needed, applies plane CTM, then prefers the DRM colorop pipeline if it can be parsed; otherwise it falls back to AMD private plane properties.

## State And Persistence
The file consumes immutable DRM blob data from atomic state and writes transient DC state into `dc_stream_state` and `dc_plane_state`. It also updates `dm_crtc_state` flags `cm_has_degamma` and `cm_is_degamma_srgb`. It allocates temporary `dc_gamma` objects and releases them after calculating transfer-function parameters.

## Dependencies And Integration Points
It depends on DRM color LUT/CTM/colorop APIs, `amdgpu_dm.h` state definitions, `amdgpu_dm_colorop.h` supported colorop bitmasks, DC color caps, and `modules/color/color_gamma.h` calculation routines. It integrates with CRTC atomic checks, plane atomic programming, DCN color capability reporting, and optional AMD private color-property creation.

## Risks
Color correctness is sensitive to hardware block ordering. Risks include accepting a colorop chain with stale or missing state, rejecting valid userspace because only one pre-blend degamma block exists, loss of CRTC degamma in legacy gamma corner cases, size assumptions for 4096-entry 1D LUTs and 17x17x17 3D LUTs, CTM conversion mistakes, allocation failure from `dc_create_gamma`, and fallback behavior silently using AMD private properties when colorop parsing returns an error.

## Test Signals
Signals include IGT `kms_color` and colorop pipeline tests for CRTC gamma/degamma/CTM, AMD private property tests when compiled, invalid-size rejection for shaper/3D LUT blobs, HDR multiplier and CTM programming checks, DCN2/DCN3 behavior with simultaneous plane and CRTC CTM, 3D LUT enablement only on capable hardware, and visual or CRC-based tests for sRGB/PQ/BT.709/gamma transfer functions.
