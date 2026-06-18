# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_logo.c

## Purpose

This file prepares and displays Linux boot logos on fbdev framebuffers, including palette setup, pseudo-palette construction, mono/VGA16 expansion, rotation, centering, CPU-count repetition, and optional extra logos. The complete 508-line source was read.

## Important APIs, Types, and Functions

Global controls are `fb_center_logo` and `fb_logo_count`. Important functions include `fb_set_logocmap()`, `fb_set_logo_truepalette()`, `fb_set_logo_directpalette()`, `fb_set_logo()`, `fb_rotate_logo_*()`, `fb_rotate_logo()`, `fb_do_show_logo()`, `fb_show_logo_line()`, optional `fb_append_extra_logo()`, `fb_prepare_extra_logos()`, `fb_show_extra_logos()`, and exported core APIs `fb_prepare_logo()` and `fb_show_logo()`.

## Control Flow

`fb_prepare_logo()` skips tileblitting, module-owned fbops, and zero logo count; computes effective depth from visual/depth fields; finds the best built-in logo; determines whether cmap reset or pseudo-palette conversion is needed; accounts for rotation and centering; and returns the vertical space needed. `fb_show_logo()` chooses repeat count from `fb_logo_count` or online CPUs and calls `fb_show_logo_line()`. The show path temporarily programs cmap entries or swaps `info->pseudo_palette`, expands packed 4-bit or 1-bit logos to byte-per-pixel images when needed, optionally rotates into a temporary buffer, then calls the driver `fb_imageblit()` repeatedly.

## State and Persistence Behavior

State includes global logo selection data in `fb_logo`, extra-logo arrays when enabled, and global logo count/centering flags. It temporarily mutates the framebuffer cmap and `info->pseudo_palette` while drawing, then restores the pseudo-palette pointer. The framebuffer contents persist visually after drawing.

## Dependencies and Integration Points

It depends on built-in `linux_logo` assets, fbdev cmap APIs, `fb_find_logo()`, CPU count, framebuffer rotation constants, driver `fb_imageblit()`, and optional extra-logo config. It is invoked by fbcon/fbmem startup paths.

## Risks and Edge Cases

`fb_show_logo_line()` returns zero if the framebuffer is suspended or owned by a module, so logo visibility depends on driver ownership state. Temporary palette allocation failures silently skip drawing. Centering reduces logo count until it fits. Comments note true/direct palette limitations and ignored `msb_right`. Extra logos support only truecolor and matching logo types.

## Test Signals

Test logo preparation for mono, VGA16, CLUT224, truecolor, directcolor, pseudocolor, static pseudocolor, rotations, centered and uncentered layouts, explicit logo count, CPU-count default, allocation failure injection, extra logos, and drivers with/without `fb_imageblit()`.
