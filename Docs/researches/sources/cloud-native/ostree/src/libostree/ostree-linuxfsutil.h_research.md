# sources/cloud-native/ostree/src/libostree/ostree-linuxfsutil.h

## Purpose
This private header declares Linux-specific filesystem utility wrappers used elsewhere in libostree.

## Important APIs, State, and Integration
It exports `_ostree_linuxfs_fd_alter_immutable_flag()`, `_ostree_linuxfs_filesystem_freeze()`, and `_ostree_linuxfs_filesystem_thaw()`. The header keeps callers away from direct `linux/fs.h` inclusion, matching the implementation comment about glibc/kernel header conflicts. It depends on `ostree-types.h` for GLib/GIO types.

## Risks and Tests
The API is intentionally low-level and fd-based, so misuse can affect live filesystems. Callers must handle integer errno returns from freeze/thaw and boolean/GError returns from immutable changes consistently. Tests should verify compile isolation, error propagation for unexpected ioctls, and graceful success on unsupported immutable flags.
