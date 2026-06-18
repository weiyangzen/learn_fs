# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-dev.c

## Purpose
This file implements the core Video4Linux2 character-device layer. It registers the global V4L2 char-device region and class, allocates and releases `struct video_device`, manages minor/device-node allocation, exposes sysfs/debugfs state, wraps file operations, computes valid ioctl bitmaps, registers media-controller entities/interfaces, unregisters devices, tracks V4L2 priority state, and provides media-pipeline convenience helpers.

## Important APIs, types, and functions
Device allocation/lifetime APIs are `video_device_alloc()`, `video_device_release()`, `video_device_release_empty()`, `__video_register_device()`, and `video_unregister_device()`. `video_devdata()` maps an open file to `video_devices[iminor(file_inode(file))]`. Global state includes `video_devices[VIDEO_NUM_DEVICES]`, `videodev_lock`, and `devnode_nums[]` bitmaps.

File-operation wrappers are `v4l2_open()`, `v4l2_release()`, `v4l2_read()`, `v4l2_write()`, `v4l2_poll()`, `v4l2_ioctl()`, `v4l2_mmap()`, optional `v4l2_get_unmapped_area()`, and the `v4l2_fops` table, with compat ioctl support wired to `v4l2_compat_ioctl32()`. Priority helpers are `v4l2_prio_init()`, `v4l2_prio_change()`, `v4l2_prio_open()`, `v4l2_prio_close()`, `v4l2_prio_max()`, and `v4l2_prio_check()`. `determine_valid_ioctls()` precomputes which standard ioctl numbers are supported by a device.

Media-controller and pipeline helpers include `video_register_media_controller()`, `video_device_pipeline_start()`, `__video_device_pipeline_start()`, `video_device_pipeline_stop()`, `__video_device_pipeline_stop()`, `video_device_pipeline_alloc_start()`, and `video_device_pipeline()`. Module lifecycle is `videodev_init()` and `videodev_exit()`.

## Control flow
`__video_register_device()` validates required callbacks and fields, initializes file-handle tracking, chooses a device-name base from `vfl_devnode_type`, inherits parent, control handler, and priority state from `v4l2_device` when unset, then allocates a free device-node number and minor under `videodev_lock`. It computes valid ioctl bits, allocates and adds a `cdev`, initializes and registers the sysfs device, increments the parent `v4l2_device` refcount, optionally registers media-controller entities/interfaces, and finally sets `V4L2_FL_REGISTERED` to allow opens.

Open is serialized with unregister by `videodev_lock`: it checks the registered bit, gets a device reference, calls the driver's open, and verifies the driver uses `v4l2_fh`. Release optionally serializes with the media request queue mutex before calling the driver release, then drops the device reference. Read/write/poll/ioctl/mmap wrappers reject unregistered devices and otherwise delegate to driver fops with debug logging. Unregister clears `V4L2_FL_REGISTERED`, wakes events, and calls `device_unregister()`. The final device release removes global lookup state, deletes the cdev, clears the node bitmap, unregisters media-controller objects, calls the driver release callback for `video_device`, and drops the `v4l2_device` reference when safe.

`determine_valid_ioctls()` builds a bitmap from device capabilities, direction, type, ioctl ops, streaming support, media-controller mode, EDID support, and control-handler availability. The final bitmap subtracts driver-specified overrides so drivers can mark auto-detected ioctls as invalid.

## State and persistence behavior
Persistent global state is the registered major range, class, debugfs root, global minor table, and node bitmaps. Each registered `video_device` persists its minor, node number, index, flags, cdev, sysfs device, inherited handlers, media-controller objects, and file-handle list. `V4L2_FL_REGISTERED` gates new operations. Reference counting through `get_device()`/`put_device()` keeps devices alive while files are open even after unregister starts. Priority state is persisted in atomics per priority level.

## Dependencies and integration points
It depends on Linux char-device, sysfs, debugfs, module, uaccess, and media headers. It integrates with `v4l2-ioctl.c` through valid ioctl bitmaps and driver `v4l2_ioctl_ops`; with `v4l2-fh` by requiring drivers to use file handles; with the compat layer through `.compat_ioctl`; with `v4l2-event` on unregister and poll; with the media request API through release serialization; and with the media controller framework through entity/interface registration and pipeline helpers.

## Risks
Registration and teardown are race-sensitive. The registered bit, global table, cdev lifetime, sysfs lifetime, and device references must remain ordered so open cannot race use-after-free. Error cleanup after partial registration must undo node allocation and cdev state correctly. `determine_valid_ioctls()` is large and capability-sensitive; missing a bit can hide valid ioctls, while setting an unsupported bit exposes dead operations to userspace. Media-controller registration failure is computed but registration still sets the device registered bit after calling it, so callers rely on return handling inside the function path. Request release serialization depends on `v4l2_device_supports_requests()` and a valid media-device request mutex. Fixed minor ranges and non-fixed minor allocation have different assumptions and need both configuration paths covered.

## Test signals
Useful tests include register/unregister/open races, failed registration cleanup at cdev and device-register stages, fixed and dynamic minor allocation, repeated unregister, sysfs attribute reads/writes, debugfs root creation/removal, fop delegation on registered/unregistered devices, request-aware release locking, compat ioctl availability under `CONFIG_COMPAT`, valid ioctl bitmap generation for video, VBI, radio, SDR, touch, metadata, EDID, streaming, and media-controller devices, priority open/change/close behavior, and media pipeline helpers with one-pad and invalid-pad entities.
