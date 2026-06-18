<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_rotate.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_rotate.h

## Purpose

`fbcon_rotate.h` declares shared rotation helpers and resolution-selection macros used by rotated fbcon bitops. The file was read as a complete 37-line header.

## Important APIs, Types, and Functions

The header declares `fbcon_rotate_font()` and, when rotation is enabled, `fbcon_set_bitops_cw`, `fbcon_set_bitops_ud`, and `fbcon_set_bitops_ccw`; otherwise those setters are empty inline stubs. `GETVYRES()` and `GETVXRES()` choose physical or virtual resolution based on scroll mode and xpan support.

## Control Flow

There is no standalone flow. Rotated bitops call the macros while translating console coordinates. `fbcon.c` calls bitops setters from `fbcon_set_bitops()`.

## State and Persistence Behavior

No state is stored here. The macros inspect `fbcon_display`, `fb_info->var`, and `fb_info->fix`.

## Dependencies and Integration Points

It depends on scroll-mode constants from `fbcon.h` and fbdev resolution fields. It bridges optional rotation support to the common fbcon core.

## Risks and Edge Cases

Wrong physical-versus-virtual resolution selection causes rotated text, cursor, and margins to be offset during pan/wrap. Empty stubs mean actual rotation exists only under the config option.

## Test Signals

Build with and without `CONFIG_FRAMEBUFFER_CONSOLE_ROTATION`, and test rotated panning on hardware with `xpanstep`, `ypanstep`, and redraw-only modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_rotate.h -->
