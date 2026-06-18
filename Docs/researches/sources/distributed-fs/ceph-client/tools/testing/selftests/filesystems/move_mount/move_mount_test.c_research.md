# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/move_mount/move_mount_test.c

## Purpose

`move_mount_test.c` verifies `MOVE_MOUNT_BENEATH`, especially root replacement, chroot edge cases, and `MNT_LOCKED` transfer/containment behavior in user namespaces.

## Important APIs, Types, and Functions

Helpers include `get_unique_mnt_id_fd`, `setup_locked_overmount`, and `create_detached_tmpfs`. The fixture isolates a mount namespace and records the original root mount id. Tests use `sys_open_tree`, `sys_move_mount`, `sys_fsopen`, `sys_fsconfig`, `sys_fsmount`, `statmount`, `chroot`, `fchdir`, `umount2`, `setup_userns`, `mount`, and `statx(STATX_MNT_ID_UNIQUE)`.

## Control Flow, State, and Persistence

Rootfs tests clone `/`, move the clone beneath `/`, chroot to the clone, and detach the old root. They verify the visible root id changes and the old root's parent becomes the clone. A chroot into a subdirectory of the same mount must reject mount-beneath with `EINVAL`; a chroot into a separate tmpfs mount must succeed. Locked tests enter a user namespace where existing mounts become locked, move a cloned tree beneath the locked mount, and verify the displaced mount becomes unmountable or unmountable as expected while the replacement inherits locking. Non-rootfs tests build a locked overmount stack at `/mnt_dir`, insert a detached tmpfs beneath it, detach the top mount, and verify the newly visible mount cannot be detached when containment requires it. State is the mount stack and unique ids.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include `MOVE_MOUNT_BENEATH`, open_tree clone support, statmount, userns helpers, and CAP_SYS_ADMIN. It integrates with VFS mount stacking and namespace containment logic. Risks are highly privileged operations, path cleanup in `/mnt_dir`, exact `EINVAL` expectations for locked mounts, and chroot state changes. Passing signals are correct unique mount ids, expected root visibility, statmount parent ids, successful/failed umounts matching lock transfer, and no containment escape.
