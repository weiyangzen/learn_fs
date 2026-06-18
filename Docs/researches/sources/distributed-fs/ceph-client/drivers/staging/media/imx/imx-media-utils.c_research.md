# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-utils.c

## Purpose

`imx-media-utils.c` provides shared format, colorimetry, DMA-buffer, naming, pipeline traversal, video-device registration-list, and stream-control helpers for the i.MX media stack.

## Important APIs, Types, and Functions

The central data table is `pixel_formats[]`, containing supported V4L2 FourCCs, media bus codes, bits-per-pixel, color spaces, planar/raw/IPU-internal flags, and parallel-bus cycle counts. Exported format helpers are `imx_media_find_pixel_format()`, `imx_media_find_mbus_format()`, `imx_media_enum_pixel_formats()`, `imx_media_enum_mbus_formats()`, `imx_media_init_mbus_fmt()`, `imx_media_init_state()`, `imx_media_try_colorimetry()`, and `imx_media_mbus_fmt_to_pix_fmt()`.

Other exports include `imx_media_alloc_dma_buf()`, `imx_media_free_dma_buf()`, `imx_media_grp_id_to_sd_name()`, `imx_media_add_video_device()`, `imx_media_pipeline_pad()`, `imx_media_pipeline_subdev()`, and `imx_media_pipeline_set_stream()`.

## Control Flow

Format find/enumeration functions filter `pixel_formats[]` by YUV/RGB/Bayer/IPU selectors and optional media-bus code. `imx_media_init_mbus_fmt()` initializes a default media-bus frame format and colorimetry. `imx_media_mbus_fmt_to_pix_fmt()` maps media-bus format to a V4L2 pixel format, rounds width and stride for IDMAC burst/alignment requirements, and computes `sizeimage`.

Pipeline helpers recursively traverse enabled links upstream or downstream to find pads or subdevices by group id or video buffer type. `imx_media_pipeline_set_stream()` starts a media pipeline under `graph_mutex`, calls the starting subdevice's `s_stream()`, and rolls back the pipeline on failure; stop calls `s_stream(0)` and stops the active media pipeline.

## State and Persistence Behavior

The file has no mutable global state beyond the static format table. DMA helpers allocate/free coherent memory into caller-owned `imx_media_dma_buf` records. `imx_media_add_video_device()` mutates the media device's master video-device list under mutex.

## Dependencies and Integration Points

Utilities are used by capture, CSI, VDIC, MIPI CSI-2, device-common code, and the mem2mem scaler. They depend on V4L2 media bus/pixel format definitions, media graph traversal APIs, DMA coherent allocation, IPUv3 colorspace constants, and group ids from `media/imx.h`.

## Risks and Edge Cases

Duplicate `V4L2_PIX_FMT_XRGB32` entries exist for regular and IPU-internal RGB32, so selectors must include/exclude `PIXFMT_SEL_IPU` correctly. Recursive graph traversal assumes acyclic active media pipelines. The quantization and colorimetry defaults are derived from format color space and may surprise raw formats. `imx_media_mbus_fmt_to_pix_fmt()` rounds visible width up to burst width, so compose rectangles must preserve original source dimensions where needed.

## Test Signals

Test enumeration ordering and selector filters, media-bus-code-filtered FourCC enumeration, default mbus initialization, unsupported code rejection, stride/sizeimage rounding for planar and packed formats, DMA allocation/free reuse, group-id naming, upstream/downstream graph traversal, and stream start rollback on subdevice failure.
