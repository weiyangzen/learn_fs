# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/binderfs/binderfs_test.c

## Purpose
Tests binderfs mount/device lifecycle in privileged and unprivileged user namespaces, plus a stress regression for binderfs device reference lifetime after unmount.

## Important APIs, Types, And Functions
Uses `mount("binder")`, `BINDER_CTL_ADD`, `BINDER_VERSION`, binderfs feature files, user namespace id maps, `socketpair`, `pthread`, and kselftest harness. Helpers include `change_mountns()`, `__do_binderfs_test()`, `wait_for_pid()`, `setid_userns_root()`, `read_nointr()`, `write_nointr()`, `write_id_mapping()`, `change_userns()`, `change_idmaps()`, and `binder_version_thread()`.

## Control Flow
The common test creates a private mount namespace, mounts binderfs, opens `binder-control`, adds `my-binder`, opens it and requests `BINDER_VERSION`, unlinks the device, verifies `binder-control` cannot be unlinked, and opens expected feature files. Privileged test runs directly as root; unprivileged test forks into a user namespace with uid/gid maps. Stress test creates 1000 binder devices in a user/mount namespace, unmounts binderfs, then concurrently calls `BINDER_VERSION` on all retained fds.

## State And Persistence
Creates temporary binderfs mountpoints under `/tmp`, binder devices, user/mount namespaces, threads, and many open fds. Cleanup unmounts and removes mount directories where possible.

## Dependencies And Integration Points
Requires `CONFIG_ANDROID_BINDERFS`, `CONFIG_ANDROID_BINDER_IPC`, user namespace support, mount permissions, and binder UAPI headers.

## Risks
Stress uses many fds and threads and can hit resource limits. Unprivileged user namespace setup depends on `/proc/*/setgroups`, uid_map, and gid_map policy. Feature-file list must track binderfs kernel features.

## Test Signals
Signals include successful binderfs mount, device add/open/version/unlink, `EPERM` on binder-control unlink, feature file presence, and no failure during post-unmount threaded `BINDER_VERSION`.
