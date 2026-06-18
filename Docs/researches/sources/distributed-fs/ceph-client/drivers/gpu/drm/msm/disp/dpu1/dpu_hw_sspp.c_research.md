# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_sspp.c

## Purpose
Implements pre-v13 Source Surface Processing Pipe hardware operations for scanout format, rectangles, source addresses, multirect, pixel extension, scaling, CSC, solid fill, QoS, CDP, and clock force control.

## Important APIs, types, and functions
- `dpu_hw_sspp_init()` creates the hardware pipe and chooses v13 or legacy ops.
- Format path: `dpu_hw_sspp_setup_format()` and shared `dpu_hw_setup_format_impl()`.
- Geometry/address path: `dpu_hw_sspp_setup_rects()`, `dpu_hw_sspp_setup_sourceaddress()`, and inline helper from the header.
- Processing path: `dpu_hw_sspp_setup_pe_config()`, `dpu_hw_sspp_setup_scaler3()`, `dpu_hw_sspp_setup_csc()`, and `dpu_hw_sspp_setup_solidfill()`.
- QoS path: `dpu_hw_sspp_setup_qos_lut()`, `dpu_hw_sspp_setup_qos_ctrl()`, `dpu_hw_sspp_setup_cdp()`, and clock force control.

## Control flow
Legacy ops select REC0 or REC1 register offsets based on `pipe->multirect_index`. Format setup programs UBWC fetch config for non-linear fetch modes, builds source format from `msm_format`, applies flips/rotation/solid-fill bits, writes UBWC static control according to UBWC version, enables CSC opmode for YUV, and clears previous UBWC error. Source-address setup either writes all planes in solo mode or interleaves addresses/pitches between RECT0 and RECT1 for multirect. Pixel extension writes per-component overfetch/repeat and total request pixels. The debugfs initializer creates feature, register-range, xin, and clock-control entries.

## State and persistence
Wrapper state includes UBWC config pointer, hardware index, catalog caps, MDSS version, MMIO base, and ops. Programmed source addresses, formats, scalers, QoS LUTs, and multirect registers persist until the next plane update, disable, or hardware reset.

## Dependencies and integration points
Depends on DPU catalog feature bits, MDSS enums, `dpu_hw_util` scaler/CSC/QoS/CDP helpers, MSM format descriptors, UBWC config, and debugfs. `dpu_plane.c` is the primary caller during atomic updates; resource manager owns pipe allocation.

## Risks
Multirect pitch/address sharing is easy to corrupt if RECT0/RECT1 indexes are wrong. UBWC version handling must track new hardware encodings; unsupported versions only warn and write zero control. Pixel extension writes `lr_pe[3]` to the C3 TB register in this version, which is a sensitive programming detail. Callers must not use ops absent from feature-gated pipes.

## Test signals
Use DRM atomic plane tests for scaling, rotation, YUV, UBWC, solid fill, and multirect. Debugfs `sspp/*/src_blk`, scaler, and CSC dumps, UBWC error status clearing, visual output, and bandwidth/QoS tracepoints validate programming.
