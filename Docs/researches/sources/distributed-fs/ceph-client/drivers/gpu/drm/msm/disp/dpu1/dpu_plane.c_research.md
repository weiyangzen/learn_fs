# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_plane.c

## Purpose
Implements DPU DRM plane objects and atomic plane behavior: framebuffer preparation, validation, virtual/real SSPP resource assignment, wide-plane splitting, multirect sharing, scaler/CSC/QoS/VBIF programming, color fill/error fill, format modifier support, state management, and plane creation.

## Important APIs, types, and functions
- Public entry points: `dpu_plane_init()`, `dpu_plane_init_virtual()`, `dpu_assign_plane_resources()`, `dpu_plane_flush()`, `dpu_plane_set_error()`, and debugfs-only `dpu_plane_danger_signal_ctrl()`.
- Atomic validation: `dpu_plane_atomic_check()`, `dpu_plane_atomic_check_nosspp()`, `dpu_plane_atomic_check_pipe()`, and `dpu_plane_split()`.
- Resource assignment: `dpu_plane_virtual_assign_resources()`, `dpu_plane_assign_resources()`, `dpu_plane_assign_resource_in_stage()`, `dpu_plane_try_multirect_parallel()`, and `dpu_plane_try_multirect_shared()`.
- Programming: `dpu_plane_sspp_atomic_update()`, `dpu_plane_sspp_update_pipe()`, `_dpu_plane_setup_scaler()`, `_dpu_plane_set_qos_lut()`, `_dpu_plane_set_ot_limit()`, `_dpu_plane_set_qos_remap()`, and `dpu_plane_flush_csc()`.
- DRM hooks: plane funcs, helper funcs, reset/duplicate/destroy/print state, and format-modifier validation.

## Control flow
Atomic check first runs generic DRM plane checks with DPU scale limits, computes stage from zpos, validates framebuffer dimensions/pitches, populates layout, and marks QoS remap for modesets. Visible planes force CRTC `planes_changed` if geometry or format changes. Later resource assignment splits a plane against mixer halves/stages and max SSPP width or core clock. In virtual-plane mode it reserves SSPPs dynamically and can share adjacent single-pipe planes through multirect parallel/time-mux. In fixed-plane mode it uses the plane's catalog SSPP and can only split through multirect on that pipe.

Atomic update marks the DPU plane state pending, determines real-time client type, populates buffer addresses, then programs every active software pipe: source address, rects, scaler/pixel extension, multirect, format/rotation/flip, CDP, QoS LUT, VBIF OT limit, and QoS remap. Flush then applies error/color-fill override or CSC just before CRTC flush timing and clears pending. Disable clears multirect state for secondary pipes so shared SSPPs can return to solo mode.

## State and persistence
`struct dpu_plane` stores DRM plane, fixed pipe ID or `SSPP_NONE` for virtual planes, color-fill flag/data, error flag, real-time pipe classification, and catalog pointer. `struct dpu_plane_state` stores assigned pipes, per-pipe configs, stage, pending flag, QoS flags, bandwidth/clock calculations, dirtyfb need, and framebuffer layout. Hardware state persists in SSPP/VBIF registers until a later atomic update/disable or reset.

## Dependencies and integration points
Integrates with DRM atomic helpers, DRM damage/fb helpers, MSM framebuffer prepare/cleanup and format layout/address helpers, DPU resource manager, CRTC client type/mixer count, VBIF policy, SSPP ops, utility CSC matrices, tracepoints, and KMS catalog/perf data.

## Risks
This file is high risk because it translates user-visible DRM plane state into hardware resource allocation and MMIO programming. Wide-plane splitting, rotation, multirect sharing with adjacent z-order planes, UBWC tile constraints, YUV alignment/CSC requirements, and QoS/OT programming can all cause underruns or visual corruption if slightly wrong. `crtc_state` must be valid for visible planes. Virtual planes use a broad advertised format set and rely on assignment-time hardware capability checks.

## Test signals
Validation should cover primary/overlay/cursor planes, virtual and fixed-plane modes, zpos ordering, alpha/blend modes, linear and QCOM compressed modifiers, YUV alignment rejection, inline rotation, scaling limits, max linewidth splitting, dual-DSI/quad-pipe topologies, multirect sharing, color fill/error fill, dirtyfb handling, bandwidth/clock accounting, and debug atomic state prints showing pipe assignments.
