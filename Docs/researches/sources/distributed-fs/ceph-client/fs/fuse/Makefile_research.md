# sources/distributed-fs/ceph-client/fs/fuse/Makefile

## Purpose
The Makefile assembles the FUSE, CUSE, and virtio-fs kernel objects according to Kconfig selections.

## Important Build Rules
- `obj-$(CONFIG_FUSE_FS) += fuse.o`
- `obj-$(CONFIG_CUSE) += cuse.o`
- `obj-$(CONFIG_VIRTIO_FS) += virtiofs.o`
- `fuse-y` includes trace, device, directory, file, inode, control, xattr, ACL, readdir, ioctl, and iomode code.
- Conditional additions include `dax.o`, `passthrough.o backing.o`, `sysctl.o`, and `dev_uring.o`.
- `ccflags-y = -I$(src)` supports local trace event includes.

## Control Flow
No runtime flow exists. Build-time expansion determines which object files are linked into `fuse.o`, `cuse.o`, and `virtiofs.o`.

## State and Persistence
The file contributes only to build artifacts. It does not own runtime state.

## Dependencies and Integration Points
It mirrors `Kconfig` and must stay aligned with conditional declarations and `IS_ENABLED()` use in the source. `trace.o` is intentionally first to surface ftrace errors early.

## Risks
Missing conditional objects can cause unresolved references; extra objects can include dead features. Because `backing.o` is tied to `CONFIG_FUSE_PASSTHROUGH`, ioctls in `dev.c` must preserve `IS_ENABLED()` guards.

## Test Signals
Kernel builds under varied FUSE configs are the primary signal. Compile checks should cover `CONFIG_FUSE_FS=m/y`, `CONFIG_CUSE=m/y`, and combinations of DAX, passthrough, SYSCTL, and io_uring.
