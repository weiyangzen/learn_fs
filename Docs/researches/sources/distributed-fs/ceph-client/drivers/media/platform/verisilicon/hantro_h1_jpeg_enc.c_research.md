# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_h1_jpeg_enc.c

## Purpose
Programs H1 encoder registers for JPEG encode and updates capture-buffer payload after hardware completion.

## Important APIs, Types, And Functions
Exports `hantro_h1_jpeg_enc_run` and `hantro_h1_jpeg_enc_done`. Helpers configure source image format/overfill (`hantro_h1_set_src_img_ctrl`), output/input DMA buffers (`hantro_h1_jpeg_enc_set_buffers`), and luma/chroma quantization table registers (`hantro_h1_jpeg_enc_set_qtable`).

## Control Flow And State
The run path applies request controls, assembles a JPEG header directly into the destination buffer via `hantro_jpeg_header_assemble`, switches the encoder to JPEG mode, writes source format, stream output address after the header, remaining output capacity, source plane addresses, quant tables, AXI swap/burst settings, and finally starts JPEG intra encode. The done callback reads the hardware stream-limit register, converts bits to bytes, and sets capture payload to header size plus encoded bytes.

## Dependencies And Integration Points
Uses H1 register macros, VB2 DMA addresses and CPU mapping for the JPEG destination header, negotiated V4L2 formats from `hantro_v4l2`, and the JPEG helper context from `hantro_jpeg.h`.

## Risks And Test Signals
The destination queue must be CPU-mapped for header writes, unlike decoder queues. Header size is subtracted from output capacity; undersized buffers trigger warnings and zero capacity. Tests should cover one-, two-, and three-plane source formats, crop/overfill dimensions, different JPEG quality values, exact/too-small output buffers, and payload accounting.
