# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_postproc.c

## Purpose
Implements Hantro G1/G2 postprocessor enable/disable, downscale frame-size enumeration, intermediate decode-buffer allocation, and postproc-aware decoded-buffer address selection.

## Important APIs, Types, And Functions
Exports `hantro_needs_postproc`, `hantro_postproc_init`, `hantro_postproc_free`, `hantro_postproc_get_dec_buf_addr`, `hantro_postproc_enable`, `hantro_postproc_disable`, `hanto_postproc_enum_framesizes`, `hantro_g1_postproc_ops`, and `hantro_g2_postproc_ops`. Internal helpers configure G1 pipeline registers, G2 raster/downscale output, buffer sizing, and DMA allocation.

## Control Flow And State
Postproc need is true for decoder contexts when forced by bitstream/controls or destination format metadata. Init allocates intermediate decoder buffers per capture buffer. Address selection reallocates per-index buffers if size requirements grow, otherwise returns the intermediate DMA address. G1 enable programs pipeline mode and YUYV output. G2 enable either writes downscale destinations or raster-scan output addresses, then configures output bit depth/format and enables RS output.

## Dependencies And Integration Points
Uses G1/G2 register descriptors, `hantro_v4l2` format-depth helpers, VB2 capture queues, codec motion-vector size helpers from `hantro_hw.h`, and variant `postproc_ops`.

## Risks And Test Signals
Intermediate buffer sizing must include codec-specific MV and optional HEVC compression data. G1 has a suspicious `input_height_ext` expression using `MB_HEIGHT(ctx->dst_fmt.height >> 8)` rather than shifting the macroblock height result; this deserves review. Tests should cover postprocessed YUYV, G2 downscale indices 0-3, 10-bit output, HEVC compression, buffer growth reallocation, and disable paths.
