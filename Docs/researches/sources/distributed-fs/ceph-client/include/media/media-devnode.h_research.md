# sources/distributed-fs/ceph-client/include/media/media-devnode.h

## Purpose
Defines media character-device nodes and file operation wrappers used to expose `/dev/media*`.

## Important APIs, Types, and Functions
`struct media_file_operations` mirrors read/write/poll/ioctl/compat/open/release callbacks with an owner. `struct media_devnode` contains the owning `media_device`, fops, embedded `device`, `cdev`, parent, minor, flags, and release callback. APIs include `media_devnode_register()`, `media_devnode_unregister_prepare()`, `media_devnode_unregister()`, `media_devnode_data()`, and `media_devnode_is_registered()`.

## Control Flow
Registration allocates a dynamic minor and registers the cdev/device. Unregister is two-stage: prepare clears the registered bit to block future opens, then unregister removes the node.

## State and Persistence Behavior
The devnode persists for the registered lifetime of a media device node. `MEDIA_FLAG_REGISTERED` tracks availability and must only be changed by core helpers.

## Dependencies and Integration Points
Depends on Linux file, cdev, device, poll, and debugfs APIs. Integrates media controller core with character-device userspace access.

## Risks
Open/unregister races are avoided only if prepare is called before unregister. Registration failure does not call release, so callers own failure cleanup.

## Test Signals
Open/ioctl through `/dev/media*`, unregister while open attempts race, compat ioctl on 64-bit kernels, release callback execution, minor allocation exhaustion, and disabled graph cleanup.
