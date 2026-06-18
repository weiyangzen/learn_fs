<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbsysfs.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbsysfs.c

## Purpose

`fbsysfs.c` creates and implements the `/sys/class/graphics/fbN` attribute group for each registered fbdev. It lets userspace inspect and request mode, mode list, bpp, virtual size, stride, blanking, panning, rotation, suspend state, and optional backlight curve changes. The file was read as a complete 481-line source.

## Important APIs, Types, and Functions

Public functions are `fb_device_create()` and `fb_device_destroy()`. Attribute handlers include mode, modes, bits per pixel, rotate, virtual size, blank, pan, name, stride, state, optional backlight curve, and stub console/cursor handlers. `activate()` is the shared forced-mode-changing helper.

## Control Flow

`fb_device_create()` creates `fb%d` under `fb_class` with `fb_device_groups`. Mode-changing stores copy `fb_info->var`, mutate requested fields, and call `activate()`, which takes `console_lock` and `lock_fb_info`, calls `fb_set_var()`, and updates fbcon VCs. `store_modes()` replaces the modelist from a binary array of `struct fb_videomode`, validates through `fb_new_modelist()`, and restores the old list on failure. Blanking and panning call `fb_blank()`/`fb_pan_display()` under console lock.

## State and Persistence Behavior

Sysfs attributes mutate runtime `fb_info` state: `var`, `mode`, `modelist`, `blank`, `state`, and optional `bl_curve`. Attribute files exist only while the device exists. `fb_info->dev` is set on creation and cleared on destroy.

## Dependencies and Integration Points

This layer integrates with fbdev core functions, fbcon update/blank callbacks, class device infrastructure, VT console locking, and optional backlight state.

## Risks and Edge Cases

Parsing uses simple numeric/comma formats for virtual size and pan, and binary struct input for `modes`. Some attributes are stubs. `store_blank()` calls `fbcon_fb_blanked()` after `fb_blank()` and notes possible recursion. `store_modes()` must preserve the old modelist if the new one is unusable.

## Test Signals

Read/write each attribute, test invalid mode strings and binary mode sizes, verify fbcon updates after bpp/mode/modes/rotate/virtual size changes, check pan bounds, blank/unblank notification, suspend state writes, and backlight curve validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbsysfs.c -->
