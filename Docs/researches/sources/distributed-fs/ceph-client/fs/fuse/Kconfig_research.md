# sources/distributed-fs/ceph-client/fs/fuse/Kconfig

## Purpose
This Kconfig file defines build-time feature switches for FUSE, CUSE, virtio-fs, DAX support, passthrough backing-file operations, and FUSE io_uring transport.

## Important Options
- `FUSE_FS` is the base tristate and selects POSIX ACL and iomap support.
- `CUSE` depends on `FUSE_FS` and builds character-device-in-userspace support.
- `VIRTIO_FS` depends on `FUSE_FS` and selects `VIRTIO`.
- `FUSE_DAX` depends on virtio-fs, FS_DAX, and DAX, and selects interval trees.
- `FUSE_PASSTHROUGH` depends on `FUSE_FS` and selects `FS_STACK`.
- `FUSE_IO_URING` depends on `FUSE_FS` and `IO_URING`.

## Control Flow
There is no runtime control flow. The configuration symbols gate object inclusion in the Makefile and compile-time code paths in the FUSE implementation.

## State and Persistence
Selections persist in the kernel build configuration. Runtime feature availability in FUSE connections is then negotiated or enabled by mount/init flags and module parameters.

## Dependencies and Integration Points
The options map directly to `fs/fuse/Makefile` object lists and conditional code in `dax.c`, `backing.c`, `dev_uring.c`, virtio-fs, and sysctl/control paths.

## Risks
Default-y booleans for DAX, passthrough, and io_uring can expose code paths when dependencies are enabled, so build matrices need to include both enabled and disabled variants. Dependency drift can create unresolved symbols or feature negotiation mismatches.

## Test Signals
Build FUSE as built-in and module, with CUSE/virtio-fs/DAX/passthrough/io_uring toggled independently where dependencies permit. Confirm disabled configurations compile out ioctl, DAX, and uring paths cleanly.
