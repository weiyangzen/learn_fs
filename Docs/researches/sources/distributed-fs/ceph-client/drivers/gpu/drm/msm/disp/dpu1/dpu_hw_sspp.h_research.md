# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_sspp.h

## Purpose
Declares the SSPP pipe abstraction, multirect modes, scaler/pixel-extension support types, software pipe configuration, and operation table used by plane programming.

## Important APIs, types, and functions
- Flags: `DPU_SSPP_FLIP_LR`, `DPU_SSPP_FLIP_UD`, `DPU_SSPP_SOURCE_ROTATED_90`, `DPU_SSPP_ROT_90`, and `DPU_SSPP_SOLID_FILL`.
- Multirect enums define solo, rect0, rect1 and none/parallel/time-multiplex modes.
- `struct dpu_hw_pixel_ext`, `dpu_sw_pipe_cfg`, `dpu_hw_pipe_ts_cfg`, and `dpu_sw_pipe` model per-plane programming.
- `struct dpu_hw_sspp_ops` exposes format, rect, PE, address, CSC, solid fill, multirect, QoS, clock, histogram, scaler, and CDP callbacks.
- Shared helpers declare common implementation entry points and `dpu_hw_setup_rects_impl()`.

## Control flow
The header itself has only inline rectangle programming helper control flow. It computes packed source/destination size and XY register values from DRM rectangles and writes them through `DPU_REG_WRITE`.

## State and persistence
`struct dpu_hw_sspp` stores per-pipe wrapper state: base, register map, UBWC config, index, catalog caps, MDSS version, and ops. Software pipe structs in plane state hold resource assignment and multirect mode until atomic state is replaced.

## Dependencies and integration points
It includes catalog, MDSS, utility, and DPU format definitions. It is shared by SSPP implementations, plane allocation/update logic, debugfs, and resource manager pipe reservations.

## Risks
The ops table is highly feature-dependent. Callers must handle NULL callbacks for unsupported CSC, scaler, CDP, QoS, multirect, or clock force. `DPU_SSPP_MAX_PITCH_SIZE` is enforced by plane checks and must match register field width.

## Test signals
Build coverage catches signature drift. Runtime validation includes atomic state printouts showing `sspp`, multirect mode/index, source/destination rectangles, and correct scanout across all supported formats/modifiers.
