
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ioc32.c

## Purpose
Provides 32-bit compatibility ioctl handling for Nouveau on 64-bit kernels. Current Nouveau-specific compat translation is effectively disabled, so most driver ioctls are delegated to the normal Nouveau ioctl path.

## Important APIs, Types, and Functions
The single external function is `nouveau_compat_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)`. It uses `DRM_IOCTL_NR()`, `drm_compat_ioctl()`, and `nouveau_drm_ioctl()`.

## Control Flow
If the ioctl number is below `DRM_COMMAND_BASE`, the call is handled by generic DRM compat ioctl support. For driver-private ioctls, the placeholder table lookup is compiled out with `#if 0`; since `fn` remains `NULL`, the handler calls `nouveau_drm_ioctl()` directly. This means compatibility depends on the normal ioctl handlers accepting the same pointer-sized layout or using DRM core-compatible structures.

## State and Persistence
The file owns no persistent state.

## Dependencies and Integration Points
It depends on Linux compat support, DRM ioctl helpers, and the declarations in `nouveau_ioctl.h`. `nouveau_drm.c` installs it as `.compat_ioctl` when `CONFIG_COMPAT` is enabled.

## Risks and Test Signals
The comment still references MGA, indicating copied legacy scaffolding. The practical risk is 32-bit userspace ABI mismatch for private ioctl structures that contain pointers or differently sized fields. Test signals include 32-bit userspace exercising GEM, ABI16, SVM, VM_BIND, and EXEC ioctls on a 64-bit kernel, plus generic DRM ioctls through the compat path.
