
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pll.h

## Purpose
Declares the AMDGPU PLL helper API used by display code. It is intentionally small and exposes only divider computation and PPLL sharing queries.

## Important APIs, Types, and Functions
The header declares `amdgpu_pll_compute`, `amdgpu_pll_get_use_mask`, `amdgpu_pll_get_shared_dp_ppll`, and `amdgpu_pll_get_shared_nondp_ppll`. Inputs include `struct amdgpu_device`, `struct amdgpu_pll`, requested frequency, output divider pointers, and `struct drm_crtc`.

## Control Flow
Callers include this header when preparing display mode programming. They compute divider outputs before register programming or query sharing helpers before assigning a PPLL ID to a CRTC.

## State and Persistence Behavior
No state is defined here. It relies on externally owned DRM CRTC and AMDGPU PLL/device structures.

## Dependencies and Integration Points
Requires the including translation unit to know `struct amdgpu_device`, `struct amdgpu_pll`, `struct drm_crtc`, and `u32`. It integrates with ATOMBIOS/display mode-setting code.

## Risks and Test Signals
The API is pointer-output heavy, so callers must pass valid storage for every output. Test signals are compile coverage from display code and runtime mode-setting paths that verify the returned dividers and sharing decisions.
