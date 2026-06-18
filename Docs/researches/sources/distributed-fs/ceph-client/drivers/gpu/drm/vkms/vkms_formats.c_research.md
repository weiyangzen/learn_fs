# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_formats.c

## Purpose

`vkms_formats.c` implements framebuffer pixel read and write conversion for VKMS. It converts many DRM formats into the compositor's internal 16-bit ARGB format, writes internal pixels back to supported writeback formats, and provides YUV colorimetry conversion matrices.

## Important APIs and functions

Public APIs are `get_pixel_read_line_function()`, `get_pixel_write_function()`, `get_conversion_matrix_to_argb_u16()`, and KUnit-visible `argb_u16_from_yuv161616()`. Internal helpers compute packed-pixel offsets/addresses, directional byte steps, subsampling offsets, RGB/gray/YUV conversion, generated read-line functions for RGB and grayscale formats, semiplanar/planar YUV readers, and ARGB-to-writeback writers.

## Control flow and state

Read-line callbacks start from a framebuffer coordinate, direction, and count, then walk the appropriate plane memory using pitches, offsets, block sizes, and rotation-derived direction. Packed RGB formats use generated tight loops. Low-bit R formats extract bitfields from blocks. YUV callbacks sample luma and chroma planes with hsub/vsub-aware stepping, then apply the plane's conversion matrix. Writeback row conversion obtains a destination row address and invokes the selected pixel writer for each output pixel.

Matrix selection chooses BT.601/BT.709/BT.2020 and full/limited range constants, copies them into the plane state, and swaps U/V columns for YVU or NV21/NV61/NV42 variants.

## Dependencies and integration

The file depends on DRM format metadata, fixed-point helpers, rect/blend definitions, and VKMS frame/plane/writeback state. Plane atomic setup selects read callbacks and conversion matrices; composer uses read callbacks; writeback uses pixel writers.

## Risks and test signals

Risks include pointer stepping bugs for rotated vertical reads, block-size assumptions, bit-order errors in R1/R2/R4 formats, chroma siting/subsampling mistakes, endian mistakes, unsupported format lists diverging from plane/writeback validation, and `BUG()` paths if validation misses an unsupported format. KUnit covers YUV matrix conversion; IGT should cover CRC/writeback for all advertised formats and rotations.
