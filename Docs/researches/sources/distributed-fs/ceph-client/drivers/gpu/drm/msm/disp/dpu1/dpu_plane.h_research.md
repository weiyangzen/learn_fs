# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_plane.h

## Purpose
Declares DPU plane state extensions and public plane APIs used by KMS, CRTC, encoder, and debugfs code.

## Important APIs, types, and functions
- `struct dpu_plane_state` extends `drm_plane_state` with DPU software pipes, pipe configs, blend stage, QoS remap flag, pending flag, bandwidth/clock estimates, dirtyfb flag, and framebuffer layout.
- `to_dpu_plane_state()` converts DRM state to DPU state.
- Declares `dpu_plane_flush()`, `dpu_plane_set_error()`, `dpu_plane_init()`, `dpu_plane_init_virtual()`, `dpu_plane_color_fill()`, `dpu_plane_danger_signal_ctrl()`, and `dpu_assign_plane_resources()`.

## Control flow
The header contains no runtime control flow except the debugfs stub for `dpu_plane_danger_signal_ctrl()` when debugfs is disabled.

## State and persistence
`dpu_plane_state` is duplicated and swapped through DRM atomic state. It persists per committed plane state and carries resource assignments until the next atomic transaction.

## Dependencies and integration points
Includes DRM CRTC, DPU KMS, MDSS, and SSPP headers. KMS creates planes with these APIs; CRTC/encoder commit code uses flush/error/color-fill/resource assignment paths.

## Risks
`PIPES_PER_PLANE` controls array sizes and must match splitter/resource assignment assumptions. Callers must not treat `pipe[].sspp` as valid until resource assignment has completed.

## Test signals
Atomic state dumps, successful plane allocation, resource assignment for virtual/fixed planes, and flush behavior across visible/disabled states validate this header contract.
