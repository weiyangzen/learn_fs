# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_formats.h

## Purpose

`vkms_formats.h` declares VKMS format conversion entry points used by plane, composer, writeback, and KUnit code.

## Important APIs

`get_pixel_read_line_function()` maps a DRM fourcc to a scanline reader returning internal 16-bit ARGB pixels. `get_pixel_write_function()` maps a writeback fourcc to an encoder from internal pixels. `get_conversion_matrix_to_argb_u16()` selects the YUV-to-ARGB matrix for a format, encoding, and range. Under KUnit, `argb_u16_from_yuv161616()` is exposed for direct numeric testing.

## Integration, state, and risks

The header has no state, but it defines the callback boundary between VKMS atomic plane/writeback setup and compositor execution. Risks are declaration drift from implementation or format list drift from `vkms_plane.c`/`vkms_writeback.c` validation.

## Test signals

`vkms-format` KUnit validates the exposed YUV conversion helper. Build and IGT format coverage validate the read/write callback mappings.
