# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_sspp_v13.c

## Purpose
Provides MDSS/DPU v13+ SSPP operation implementations for the newer common-plus-record register layout while reusing shared SSPP format, rect, solid-fill, scaler, CSC, QoS, and CDP helpers.

## Important APIs, types, and functions
- `dpu_hw_sspp_init_v13()` installs the v13 ops table.
- `dpu_hw_sspp_calculate_rect_off()` chooses the REC0 or REC1 sub-block base from catalog data.
- V13-specific callbacks include setup for multirect, format, pixel extension, rects, source addresses, solid fill, QoS LUT/control, CDP, and clock force.
- Common register offsets include `SSPP_CMN_*` and record offsets `SSPP_REC_*`.

## Control flow
All per-rectangle programming first computes a record offset from multirect index. Format setup points shared `dpu_hw_setup_format_impl()` at record-local format/opmode/unpack/UBWC registers. Rect and source-address setup write record-local geometry and all plane addresses. V13 pitch packing differs from older code: stride0 combines plane 0 and 2, stride1 combines plane 1 and 3. QoS and clock force use common registers rather than per-record legacy offsets.

## State and persistence
No additional wrapper state is stored beyond `struct dpu_hw_sspp`. Persistent hardware state lives in common SSPP registers and REC0/REC1 record blocks.

## Dependencies and integration points
Depends on `dpu_hw_sspp.h`, UBWC helpers, shared SSPP implementation helpers, and catalog sub-block bases for `sspp_rec0_blk`/`sspp_rec1_blk`. It is selected automatically by `dpu_hw_sspp_init()` when MDSS core major version is 13 or newer.

## Risks
Correct catalog record-base definitions are critical; all offsets are relative to those bases. V13 layout differences in pitch packing, pixel-extension registers, common QoS registers, and clock control can break scanout if legacy assumptions leak in. Unlike older code, clock force is always installed for v13.

## Test signals
Validation should cover v13+ platforms with linear and UBWC formats, multirect REC0/REC1, YUV CSC, scaling, CDP, QoS LUT updates, and SSPP common/record register dumps.
