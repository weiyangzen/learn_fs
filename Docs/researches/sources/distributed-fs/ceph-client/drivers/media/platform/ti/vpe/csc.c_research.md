# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/csc.c

## Purpose
Implements the TI VPE/VIP color-space converter helper library. It selects coefficient matrices for YUV-to-RGB or RGB-to-YUV conversion based on V4L2 pixel format, colorspace encoding, and quantization, fills CSC shadow registers, supports bypass, dumps registers, and maps the hardware resource.

## Important APIs, Types, and Functions
Internal types model coefficient organization: `struct quantization`, `struct colorspace`, `struct encoding_direction`, and `struct csc_coeffs`. Exported functions are `csc_dump_regs()`, `csc_set_coeff_bypass()`, `csc_set_coeff()`, and `csc_create()`.

## Control Flow
`csc_create()` allocates `struct csc_data`, looks up a named memory resource, and maps it with `devm_ioremap_resource()`. `csc_set_coeff()` extracts pixel format, YCbCr encoding, and quantization from single-planar or multiplanar V4L2 formats, obtains format metadata, decides conversion direction, normalizes legacy default encoding/quantization to 601/full, selects one of the static 12-coefficient tables, or sets bypass for non-RGB/YUV conversion. Coefficients are packed in pairs into six 32-bit shadow registers.

## State and Persistence
`struct csc_data` stores mapped base, resource, and platform device pointer. Coefficients are static read-only driver data. Register shadow arrays are provided by the caller and later submitted to hardware by the VPE/VIP pipeline.

## Dependencies and Integration Points
Depends on V4L2 format helpers (`v4l2_format_info()`, `v4l2_is_format_yuv()`, `v4l2_is_format_rgb()`), Linux platform resources, MMIO helpers, and exported symbols consumed by TI VPE/VIP drivers.

## Risks and Edge Cases
If `v4l2_format_info()` returns NULL for an unsupported fourcc, downstream format helper behavior must be safe. Defaults intentionally differ from V4L2 standard defaults for historical compatibility. Unsupported encodings fall back to 601/full or 601 limited paths only through defensive code.

## Test Signals
Test RGB-to-YUV and YUV-to-RGB for 601/709 and full/limited quantization, single and multiplanar formats, same-family bypass cases, register packing, invalid resource names, and debug register dumps.
