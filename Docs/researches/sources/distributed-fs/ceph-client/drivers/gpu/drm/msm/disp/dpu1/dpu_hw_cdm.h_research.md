# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cdm.h

## Purpose
Declares the CDM hardware wrapper contract and configuration payload for chroma downsampling, CSC, output format, output target, bit depth, and PP binding.

## Important APIs, Types, and Functions
`struct dpu_hw_cdm_cfg` carries output dimensions, bit depth, horizontal/vertical downsample types, output `msm_format`, CSC config, output type, and PP ID. Enums define downsample type (`CDM_CDWN_DISABLE`, `PIXEL_DROP`, `AVG`, `COSITE`, `OFFSITE`), output target (`HDMI`, `WB`), output bit depth, and hardware method field values. `struct dpu_hw_cdm_ops` exposes `enable` and `bind_pingpong_blk`. `struct dpu_hw_cdm` stores base hardware block, register map, catalog caps, CDM index, and ops. `dpu_hw_cdm_init` constructs the wrapper and `to_dpu_hw_cdm` casts from the generic block.

## Control Flow and State
No persistent policy exists in the header. It defines the state shape that encoder helpers populate and the hardware wrapper consumes. The presence of `bind_pingpong_blk` is generation-gated in the implementation.

## Dependencies and Integration Points
Includes DPU MDSS and top-level hardware definitions and references `struct msm_format`, `struct dpu_csc_cfg`, catalog `dpu_cdm_cfg`, `enum dpu_cdm`, and `enum dpu_pingpong`. Video and writeback encoder setup paths build `dpu_hw_cdm_cfg`.

## Risks and Test Signals
Enum values must remain synchronized with register field encoding in `dpu_hw_cdm.c`. Tests should verify callers populate all dimensions and format fields, that YUV format requirements are enforced, and that unsupported ops are checked before use. Static analysis should catch null `output_fmt` or `csc_cfg` passed through helper paths.
