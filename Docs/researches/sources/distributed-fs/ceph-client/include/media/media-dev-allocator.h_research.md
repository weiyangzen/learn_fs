# sources/distributed-fs/ceph-client/include/media/media-dev-allocator.h

## Purpose
Declares a global refcounted media-device allocator for USB devices shared by multiple drivers.

## Important APIs, Types, and Functions
When media controller and USB support are enabled, `media_device_usb_allocate()` allocates/initializes a shared `media_device`, and `media_device_delete()` drops its kref. Disabled configurations return `NULL` or no-op.

## Control Flow
USB media drivers request a shared media device during probe and delete it during disconnect/remove. The implementation manages a system-wide media-device list and releases the instance on the last put.

## State and Persistence Behavior
State persists per shared USB media device through krefs and global allocator bookkeeping. The header provides conditional stubs when unavailable.

## Dependencies and Integration Points
Depends on `CONFIG_MEDIA_CONTROLLER` and USB. Integrates composite USB media functions that need one media graph across multiple drivers.

## Risks
Reference imbalance leaks or prematurely frees the media graph. Stub behavior means callers must tolerate `NULL` when media controller or USB support is disabled.

## Test Signals
Multi-driver USB device probe/remove, repeated bind/unbind, kref leak checks, disabled-config builds, and shared graph registration.
