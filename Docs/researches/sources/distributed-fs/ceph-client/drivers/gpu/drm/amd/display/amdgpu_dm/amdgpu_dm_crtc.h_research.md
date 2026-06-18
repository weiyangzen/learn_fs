# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crtc.h

## Purpose
`amdgpu_dm_crtc.h` declares the CRTC-facing Display Manager helpers used by KMS, IRQ, PSR/Replay, and initialization paths.

## Important APIs, Types, And Functions
The header declares panel self-refresh coordination, vblank handling, modeset-required detection, vupdate IRQ control, VRR active checks for IRQ and atomic state paths, vblank enable/disable callbacks, and `amdgpu_dm_crtc_init`. These functions operate on `amdgpu_display_manager`, `amdgpu_crtc`, `dm_crtc_state`, DRM CRTC state, DC stream state, and DRM planes.

## Control Flow
No logic is implemented in the header. It exposes the flow implemented in `amdgpu_dm_crtc.c`: CRTC objects are initialized, atomic checks classify updates and stream validity, vblank callbacks enable/disable hardware IRQs, IRQ handlers report vblank events, and panel self-refresh policy is evaluated when vblank state changes.

## State And Persistence
The header owns no state. Its function signatures show the state being mutated in implementation: CRTC IRQ params, DM display-manager workqueues, DC stream state, `dm_crtc_state` VRR/color fields, and CRTC object lifetime.

## Dependencies And Integration Points
It relies on surrounding includes for AMDGPU/DRM/DC types and is included by files that need CRTC helper calls, including IRQ and PSR/Replay coordination code. It is the local boundary between CRTC implementation and the rest of Display Manager.

## Risks
Signature drift can break broad parts of the display driver because these helpers are shared across modeset, IRQ, and panel-self-refresh code. `amdgpu_dm_crtc_init` names its last parameter `link_index` in the header while the implementation treats it as `crtc_index`, a naming mismatch that can confuse callers even though the type is identical.

## Test Signals
Compile/link coverage for all CRTC users, successful CRTC creation for each display index, vblank callback registration through DRM CRTC funcs, and PSR/Replay/VRR paths invoking the declared helpers are the primary signals.
