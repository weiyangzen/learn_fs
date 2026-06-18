<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbmem.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbmem.c

## Purpose

`fbmem.c` is the fbdev core registration and setup layer for framebuffer devices. It owns the graphics class, global registered framebuffer table, registration lifetime, mode setting, panning validation, blanking, pixmap scratch-buffer helpers, suspend notifications, and modelist validation. The file was read as a complete 754-line source.

## Important APIs, Types, and Functions

Global state includes `fb_class`, `registered_fb[FB_MAX]`, `num_registered_fb`, and `registration_lock`. Exported APIs include `get_fb_info`, `put_fb_info`, `fb_get_color_depth`, `fb_pad_aligned_buffer`, `fb_pad_unaligned_buffer`, `fb_get_buffer_offset`, `fb_pan_display`, `fb_set_var`, `fb_blank`, `register_framebuffer`, `unregister_framebuffer`, `devm_register_framebuffer`, `fb_set_suspend`, `fb_new_modelist`, and `fb_modesetting_disabled`.

## Control Flow

`fbmem_init()` creates the graphics class, procfs, character device, and fbcon device. `register_framebuffer()` validates endian/math support, picks a free node, initializes modelist/refcount/locks, creates `/sys/class/graphics/fbN`, allocates default pixmap storage if needed, fills blit capability bitmaps, registers PM VT-switch requirements, stores the device in `registered_fb[]`, and notifies fbcon. Unregistration destroys sysfs, unbinds fbcon, frees default pixmap/modelist state, removes the table entry, notifies fbcon, and drops the final reference. `fb_set_var()` validates fields, driver checks, virtual resolution, console blit capabilities, `fb_set_par`, panning, colormap, modelist insertion, and LCD notifications.

## State and Persistence Behavior

All state is in kernel memory. `registered_fb[]` and `num_registered_fb` persist until unregister. `fb_info->node`, locks, refcount, pixmap, modelist, blank state, and device object are initialized on registration. `fb_info->var`, `blank`, `state`, and modelist mutate at runtime.

## Dependencies and Integration Points

It integrates with fbcon callbacks, sysfs device creation/destruction, procfs/chrdev helpers, LCD/backlight LED notification, PM VT-switch requirements, modelist helpers, notifier chains for special configs, and `video_firmware_drivers_only()` for `nomodeset`.

## Risks and Edge Cases

Locking is split between `registration_lock`, `fb_info->lock`, and console lock. Registration must not exceed `FB_MAX` or leak modelist nodes. `fb_set_var()` temporarily mutates `info->var` and must restore on failure. Panning rejects unsupported step alignment. Foreign-endian framebuffers require matching kernel config.

## Test Signals

Register/unregister drivers repeatedly, exercise devm cleanup, sysfs mode changes, pan bounds, FOURCC validation, tiny/overflow resolutions, modelist replacement, suspend/resume under console lock, `nomodeset`, and KASAN/lockdep during concurrent userspace fb access and console activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbmem.c -->
