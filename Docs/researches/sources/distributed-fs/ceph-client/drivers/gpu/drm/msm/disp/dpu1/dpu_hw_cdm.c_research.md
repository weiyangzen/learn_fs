# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cdm.c

## Purpose
Implements the chroma down module hardware wrapper. CDM converts RGB source data to YUV output, optionally performs horizontal/vertical chroma downsampling, configures HDMI packing, and binds CDM input to a pingpong/CWB source on newer DPU generations.

## Important APIs, Types, and Functions
The public constructor is `dpu_hw_cdm_init`. Exposed ops are `dpu_hw_cdm_enable` and, for DPU core major >= 5, `dpu_hw_cdm_bind_pingpong_blk`. Internal `dpu_hw_cdm_setup_cdwn` programs CDWN2 op mode, coefficients, output size, bit depth, and clamp. Fixed coefficient arrays encode cosite/offsite horizontal and vertical downsampling filters.

## Control Flow and State
The wrapper stores only register base, log mask, index, catalog caps, and ops. `enable` validates non-null inputs and requires a YUV output format. It programs CSC coefficients through `dpu_hw_csc_setup`, programs downsampling, sets HDMI pack mode when output type is HDMI, marks CSC destination as YUV, binds the PP source when supported, and writes opmode registers. `bind_pingpong_blk` updates the `CDM_MUX` low nibble, mapping CWB-like pingpongs to a fixed value, normal PPs to zero-based IDs, and none to disabled `0xf`.

## Dependencies and Integration Points
Depends on `dpu_hw_cdm_cfg` from encoder helpers, MSM format metadata, CSC matrix helpers, catalog CDM configs, and CTL/encoder pending flush. Video and writeback encoders call shared CDM setup before flushing CDM.

## Risks and Test Signals
Risks include rejecting non-YUV formats late, unsupported `CHROMA_H1V2` HDMI output, coefficient mismatch, mux programming errors, and output-size/bit-depth inconsistencies. Tests should cover WB YUV output, HDMI/DP YUV paths if present, all downsample enum values, invalid format rejection, DPU4 lack of bind op, DPU5+ PP binding, and register dumps for opmode/coefficient/output-size fields.
