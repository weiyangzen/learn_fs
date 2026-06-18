# sources/distributed-fs/ceph-client/include/drm/drm_ioctl.h

Purpose: declares the DRM ioctl dispatch interface, ioctl descriptor format, permission flags, and common helper handlers used by DRM core and drivers.

Important APIs and types: `drm_ioctl_t` is the normal kernel-space handler signature after `drm_ioctl()` has copied ioctl payload data. `drm_ioctl_compat_t` supports 32-bit compatibility handlers. `enum drm_ioctl_flags` defines access policy: `DRM_AUTH`, `DRM_MASTER`, `DRM_ROOT_ONLY`, and `DRM_RENDER_ALLOW`. `struct drm_ioctl_desc` stores command number, flags, handler, and debug name. `DRM_IOCTL_DEF_DRV()` builds driver-private descriptor table entries from UAPI command names. Public functions include `drm_ioctl()`, `drm_ioctl_kernel()`, optional `drm_compat_ioctl()`, `drm_ioctl_flags()`, `drm_noop()`, and `drm_invalid_op()`.

Control flow: file operations route userspace ioctl calls to `drm_ioctl()`, which decodes the command number/type, enforces descriptor flags against the `drm_file` state and node type, copies payload according to ioctl direction, calls the descriptor handler, and copies results back as needed. Kernel callers can bypass userspace copying through `drm_ioctl_kernel()`.

State and persistence behavior: the header defines no persistent state, but its flags gate access to per-file authentication, master ownership, capabilities, and render-node behavior maintained by DRM core.

Dependencies and integration points: uses Linux ioctl encoding, bit operations, `struct file`, `struct drm_device`, and `struct drm_file`. It is included by DRM core ioctl tables and driver files that define private ioctls.

Risks: incorrect flags expose privileged display-control operations to unauthenticated clients or render nodes. Compat handlers should be rare; adding one usually indicates UAPI structure layout issues. Handler data has already been copied and may be copied back, so handler assumptions must match ioctl direction bits.

Test signals: ioctl permission tests across primary/control/render nodes, unauthenticated and non-master file descriptors, root-only SETMASTER/DROPMASTER-like paths, compat builds, invalid op handling, and driver-private `DRM_IOCTL_DEF_DRV()` table indexes.
