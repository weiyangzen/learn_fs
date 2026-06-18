# File Research: sources/block-storage/lvm2/lib/device/dev-ext.c

## Purpose
Implements external device-information handles attached to `struct device`, currently supporting no external source and libudev.

## Core Behavior
A registry maps `DEV_EXT_NONE` and `DEV_EXT_UDEV` to get/release functions. `dev_ext_enable()` switches the source and releases any old incompatible handle. `dev_ext_get()` lazily creates the source handle. `dev_ext_release()` detaches it, and `dev_ext_disable()` returns the device to `DEV_EXT_NONE`.

For udev builds, `_dev_ext_get_udev()` obtains the global udev context, creates a udev device from block `dev_t`, optionally verifies initialization, and stores the handle in `dev->ext.handle`. Release calls `udev_device_unref()`.

Without udev support, udev get returns NULL and release fails.

## Integration
MD and multipath detection use this layer to read udev properties when `external_device_info_source()` selects udev.

## Risk Notes
`_dev_ext_get_udev()` returns NULL if udev reports incomplete information, but it does not unref the created udev device before that return in the initialized-check failure path.
