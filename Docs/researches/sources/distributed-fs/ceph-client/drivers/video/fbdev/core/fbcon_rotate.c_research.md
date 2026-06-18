<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_rotate.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_rotate.c

## Purpose

`fbcon_rotate.c` owns the common rotated-font cache builder used by clockwise, upside-down, and counter-clockwise fbcon bitops. The file was read as a complete 52-line source.

## Important APIs, Types, and Functions

Its sole function is `fbcon_rotate_font(struct fb_info *info, struct vc_data *vc)`. It checks whether the cached `par->rotated.fontdata` and `buf_rotate` already match, optionally calls driver `fb_sync`, and uses `font_data_rotate()` to create or reuse `par->rotated.buf`.

## Control Flow

Rotated bitops expose this function through their vtable. During console init or switch, `fbcon.c` calls it when present. Matching cache state returns immediately. Successful rotation stores the returned buffer and size; failure frees and clears the old rotated buffer and returns the error.

## State and Persistence Behavior

The function mutates only `par->rotated`. That cache persists for the life of `info->fbcon_par` and is released in `fbcon_release()`.

## Dependencies and Integration Points

It depends on fbdev, console font metadata, `font_data_rotate()`, optional driver `fb_sync`, and private `fbcon_par` fields.

## Risks and Edge Cases

On allocation or rotation failure, the buffer is cleared to avoid stale output. Cache reuse requires exact fontdata and rotation matches, with font lifetime handled by fbcon font references.

## Test Signals

Exercise rotation changes after font changes, switching between rotated consoles, allocation-failure paths, and drivers with asynchronous blits requiring `fb_sync`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_rotate.c -->
