# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_jpeg.h

## Purpose
Declares the small JPEG helper contract used by Hantro JPEG encoder backends.

## Important APIs, Types, And Functions
Defines `JPEG_HEADER_SIZE`, `JPEG_QUANT_SIZE`, `struct hantro_jpeg_ctx`, and `hantro_jpeg_header_assemble`. The context carries width, height, quality, output buffer pointer, and hardware-ordered luma/chroma quantization tables.

## Control Flow And State
No persistent state is stored here. A caller fills a stack or transient `hantro_jpeg_ctx`, points `buffer` at the capture buffer, and calls the assembler. The helper writes the software JPEG header and populates quant tables for subsequent register writes.

## Dependencies And Integration Points
Used directly by `hantro_jpeg.c` and `hantro_h1_jpeg_enc.c`. `JPEG_HEADER_SIZE` must match the static header size in the C file and the V4L2 format `header_size` used by the encoder path.

## Risks And Test Signals
The API trusts the caller to provide a buffer at least `JPEG_HEADER_SIZE` bytes. Tests should cover format negotiation exposing the same header size, encoder handling of undersized buffers, and quality/path values that fill both hardware quant table arrays.
