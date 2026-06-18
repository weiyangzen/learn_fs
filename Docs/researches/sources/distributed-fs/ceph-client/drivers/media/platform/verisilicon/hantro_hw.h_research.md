# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_hw.h

## Purpose
Declares codec-specific hardware contexts, auxiliary DMA buffer type, codec/postproc operation tables, exported backend symbols, dimension constants, and helper functions for buffer-size/layout calculations.

## Important APIs, Types, And Functions
Important structs include `hantro_aux_buf`, `hantro_h264_dec_hw_ctx`, `hantro_hevc_dec_hw_ctx`, `hantro_mpeg2_dec_hw_ctx`, `hantro_vp8_dec_hw_ctx`, `hantro_vp9_dec_hw_ctx`, `hantro_av1_dec_hw_ctx`, `hantro_postproc_ctx`, `hantro_postproc_ops`, and `hantro_codec_ops`. Inline helpers compute macroblock/superblock counts, VP9/H264/HEVC/AV1 motion-vector sizes, and HEVC compressed luma/chroma sizes.

## Control Flow And State
The header defines the persistent per-codec state embedded in `hantro_ctx`: DPB/reference lists, coherent aux buffers, VP9 frame contexts and segmentation state, HEVC tile/reference/compression state, and AV1 reference/probability state. `hantro_codec_ops` establishes the core lifecycle: optional init/exit, per-job run, optional done, and timeout reset.

## Dependencies And Integration Points
Integrates Linux interrupts, V4L2 controls, VP9 helpers, VB2, AV1 probability headers, variant declarations, and all codec backend prototypes. It is the main compile-time contract between platform variants, core driver, postprocessor, and codec files.

## Risks And Test Signals
Size helpers drive buffer allocation; wrong formulas can cause DMA overruns or hardware faults. `hantro_h264_mv_size` uses macroblock width twice, which should be reviewed against expected width-by-height sizing and test coverage. ABI-like struct fields are private but broadly shared, so changes need full codec build and conformance coverage.
