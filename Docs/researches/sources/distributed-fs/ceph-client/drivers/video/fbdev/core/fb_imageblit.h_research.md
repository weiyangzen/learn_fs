# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_imageblit.h

## Purpose

This header implements the generic packed-pixel image blit engine for fbdev. It converts 1-bit bitmap images and 8-bit indexed color images into framebuffer pixels, with optimized paths for common pixels-per-word layouts and support for endian and reverse-pixel behavior. The complete 495-line source was read.

## Important APIs, Types, and Functions

Important iterators are `struct fb_bitmap_iter`, `struct fb_color_iter`, and `struct fb_bitmap4x_iter`. Important helpers include `fb_bitmap_image()`, `fb_color_image()`, `fb_bitmap4x_image()`, `fb_bitblit()`, `fb_color_imageblit()`, `fb_bitmap4x_imageblit()`, `fb_bitmap1x_imageblit()`, `fb_bitmap_1ppw()`, `fb_pack()`, `fb_bitmap_2ppw()`, `fb_bitmap_4ppw()`, `fb_bitmap_imageblit()`, and entry `fb_imageblit(struct fb_info *p, const struct fb_image *image)`.

## Control Flow

The entry initializes destination bit address and reversal state, adjusts to image `dx`/`dy`, then selects color or bitmap paths based on `image->depth`. Color images read one byte per pixel and optionally translate through `info->pseudo_palette`. Bitmap images expand foreground/background colors and use optimized one/two/four-pixels-per-word paths where possible; otherwise they fall back to generic bitstream iteration. The low-level bitblitter accumulates pixels into destination words, preserves leading/trailing bits, reverses bytes/bits as required, and writes full or masked words.

## State and Persistence Behavior

No global state is kept. The helper reads source image data and writes framebuffer memory. It uses `info->pseudo_palette` transiently for true/direct color conversion.

## Dependencies and Integration Points

The header depends on `fb_draw.h`, memory-specific framebuffer accessors, `struct fb_image`, fbdev visual/depth metadata, pseudo-palette conventions, and optional `FB_REV_PIXELS_IN_BYTE`. It is included by I/O-memory and system-memory imageblit wrappers.

## Risks and Edge Cases

Risks include palette indices outside the pseudo-palette or hardware cmap range, unusual bpp values, unaligned destinations, byte order for 1/2/4 bpp modes, and source image dimensions that upper layers fail to clip. Optimized paths require careful validation against the generic bitstream path.

## Test Signals

Compare output with a reference renderer for 1-bit and 8-bit images across 1/2/4/8/16/24/32 bpp, all x offsets, truecolor pseudo-palettes, direct/pseudocolor visuals, endian variants, reverse-pixel modes, narrow images, and widths crossing word boundaries.
