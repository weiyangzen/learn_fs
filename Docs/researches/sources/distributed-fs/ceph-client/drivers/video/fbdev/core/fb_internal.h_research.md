# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_internal.h

## Purpose

This internal header declares shared fbdev core state and cross-file helpers for character-device registration, logos, fbmem registration, procfs, and sysfs/device integration. The complete 84-line source was read.

## Important APIs, Types, and Functions

It declares or stubs `fb_register_chrdev()`, `fb_unregister_chrdev()`, `fb_prepare_logo()`, `fb_show_logo()`, `fb_class`, `registration_lock`, `registered_fb[]`, `num_registered_fb`, `get_fb_info()`, `put_fb_info()`, `fb_init_procfs()`, `fb_cleanup_procfs()`, `fb_device_create()`, and `fb_device_destroy()`.

## Control Flow

There is no executable flow except inline stubs. When `CONFIG_FB_DEVICE=n`, char-device/procfs functions become no-ops and `fb_device_create()`/`destroy()` manually hold and release the parent device reference that sysfs device creation would otherwise manage.

## State and Persistence Behavior

The header exposes global fbdev registration state owned by `fbmem.c`: framebuffer class, registration mutex, registered framebuffer array, and count.

## Dependencies and Integration Points

It coordinates `fb_chrdev.c`, `fb_logo.c`, `fbmem.c`, `fb_procfs.c`, and `fbsysfs.c`. External drivers should not include it; it is for core internals.

## Risks and Edge Cases

Stub behavior under `CONFIG_FB_DEVICE=n` must stay aligned with real device creation behavior, especially parent device references. Exposed globals make lock discipline important; users must hold `registration_lock` or fb references as appropriate.

## Test Signals

Build with `FB_DEVICE=y/n`, `CONFIG_LOGO=y/n`, and verify fb registration/unregistration reference balance, procfs availability, sysfs device creation, and logo stubs.
