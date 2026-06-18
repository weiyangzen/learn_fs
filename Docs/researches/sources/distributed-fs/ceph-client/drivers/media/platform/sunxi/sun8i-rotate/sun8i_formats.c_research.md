# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i_formats.c

Purpose: provides the supported pixel-format table and lookup/enumeration helpers for the sun8i rotate mem2mem driver.

Important APIs and functions: exports `rotate_find_format` and `rotate_enum_fmt`. The static `rotate_formats` table maps V4L2 FourCC values to hardware format codes, plane counts, bytes-per-pixel values, horizontal/vertical subsampling, and policy flags.

Control flow: lookup linearly scans the table by FourCC. Enumeration linearly scans the table while optionally filtering for formats allowed on capture buffers through `ROTATE_FLAG_OUTPUT`.

State and persistence: immutable static format metadata only.

Dependencies and integration points: depends on V4L2 FourCC values and hardware format constants from `sun8i-rotate.h`. The rotate driver uses this metadata for validation, pitch/size calculations, address-plane layout, and capture-format derivation.

Risks: not all hardware formats are present; the file explicitly excludes `ROTATE_FORMAT_BGR565` and `ROTATE_FORMAT_VYUV`. Many YUV input formats lack `ROTATE_FLAG_OUTPUT`, so capture output is normalized to YUV420 for YUV sources. Incorrect bpp/subsampling metadata would corrupt plane offsets and DMA pitches.

Test signals: V4L2 format enumeration for output/capture, round-trip lookup for each listed format, image tests for RGB and YUV planar/semi-planar formats, and pitch/sizeimage verification.
