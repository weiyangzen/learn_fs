<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/softcursor.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/softcursor.c

## Purpose

`softcursor.c` implements a generic software cursor fallback for framebuffer console when a driver does not provide or accept hardware cursor updates. The file was read as a complete 76-line source.

## Important APIs, Types, and Functions

The single API is `soft_cursor(struct fb_info *info, struct fb_cursor *cursor)`. It uses `info->pixmap` as a scratch destination, `par->cursor_src` and `par->cursor_size` for a cached combined `struct fb_image` plus cursor bitmap, and driver `fb_imageblit` for final drawing.

## Control Flow

If the framebuffer is not running, it returns. It computes source pitch and data size, reallocates the cached buffer if needed with `GFP_ATOMIC`, combines image data and mask using `ROP_XOR` or `ROP_COPY` when enabled, copies the image when disabled, pads into the pixmap scratch buffer, and calls `fb_imageblit()`.

## State and Persistence Behavior

Persistent cursor fallback state is in `info->fbcon_par`: `cursor_src` and `cursor_size` survive across updates and are freed by `fbcon_release()`.

## Dependencies and Integration Points

It depends on `fbcon_par`, `fb_get_buffer_offset`, `fb_pad_aligned_buffer`, and the framebuffer driver's imageblit operation. Rotated and normal fbcon cursor paths call it when hardware cursor setup fails.

## Risks and Edge Cases

Atomic allocation can fail. The code assumes cursor image data and mask cover the computed bitmap size. Drivers without `fb_imageblit` cannot use this fallback safely. The shared pixmap buffer may require synchronization through `fb_get_buffer_offset()`.

## Test Signals

Force hardware cursor failure, test XOR and COPY cursor rops, enable/disable transitions, varying cursor sizes and masks, suspended framebuffer state, and KASAN coverage for image/mask sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/softcursor.c -->
