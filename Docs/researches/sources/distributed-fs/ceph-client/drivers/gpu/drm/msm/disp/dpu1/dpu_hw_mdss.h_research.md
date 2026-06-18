# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_mdss.h

## Purpose
Provides common DPU/MDSS identifiers, blend bit definitions, format layout structures, CSC structures, color structs, debug masks, tear-check config, and pingpong vsync info shared across DPU hardware wrapper files.

## Important APIs, types, and functions
- Hardware block enums: `dpu_hw_blk_type`, `dpu_sspp`, `dpu_lm`, `dpu_ctl`, `dpu_pingpong`, `dpu_merge_3d`, `dpu_intf`, `dpu_wb`, `dpu_cwb`, and others.
- Composition enums: `dpu_stage`, `dpu_3d_blend_mode`, `dpu_intf_type`, and `dpu_intf_mode`.
- Data structures: `dpu_hw_fmt_layout`, `dpu_csc_cfg`, `dpu_mdss_color`, `dpu_hw_tear_check`, and `dpu_hw_pp_vsync_info`.
- Constants define CSC array sizes, plane/stage limits, blend flags, and debug log masks.

## Control flow
The file is declarative. It shapes how other C files translate DRM state and catalog topology into hardware block IDs and register bitfields.

## State and persistence
No state is stored here. The structures declared here are embedded in plane state, writeback config, pingpong setup, and CSC programming objects elsewhere.

## Dependencies and integration points
It depends on MSM driver and MDP format headers. Nearly every DPU hardware wrapper includes it for common enums and shared programming structures; KMS, plane, pingpong, writeback, LM, top, and VBIF code all rely on the numeric enum ranges matching catalog data and register encodings.

## Risks
Enum numeric values are ABI-like inside the driver: many arrays index by `SSPP_*`, `PINGPONG_*`, or `LM_*` ranges, and register encodings rely on stable values. Adding a block or reordering enums can break array sizing, source routing, debug status decoding, or resource-manager mappings. Several comments contain historical semantics for interface types that newer hardware may ignore but callers still preserve.

## Test signals
Compile coverage catches structural drift, while runtime signals include correct resource allocation, debug status decoding, DSI/DP/WB interface selection, tear-check setup, CSC programming, and absence of out-of-bounds status array use.
