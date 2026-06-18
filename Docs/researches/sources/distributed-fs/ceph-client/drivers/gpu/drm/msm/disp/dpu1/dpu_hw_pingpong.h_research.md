# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_pingpong.h

## Purpose
Declares the pingpong hardware wrapper and ops for tear-check, autorefresh, dither, and DSC setup.

## Important APIs, types, and functions
- `struct dpu_hw_dither_cfg` carries bit depths, temporal enable, flags, and a 16-entry dither matrix.
- `struct dpu_hw_pingpong_ops` exposes tear-check, external TE, line count, autorefresh disable, dither, and DSC callbacks.
- `struct dpu_hw_pingpong` stores base block, register map, index, caps, optional merge_3d pointer, and ops.
- `to_dpu_hw_pingpong()` and `dpu_hw_pingpong_init()` provide conversion and construction.

## Control flow
The header is declarative. Runtime control is in the implementation and gated by hardware generation through optional ops.

## State and persistence
It defines in-memory wrapper state and configuration structures. Hardware state is held in pingpong registers after ops execute.

## Dependencies and integration points
Includes catalog, MDSS, and utility headers, and forward declares `struct dpu_hw_merge_3d` to associate final composition blocks. Encoder, CRTC, and resource-manager code use the declared object.

## Risks
Several ops can be NULL on newer or older hardware. The dither config does not validate bit-depth bounds in the type system, so implementation-side callers must use supported values.

## Test signals
Build validation covers signatures. Runtime signals include command-mode TE behavior, dither output, DSC programming, and register/debug snapshots for pingpong blocks.
