# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/statmount_test.c

## Purpose

`statmount_test.c` is the main statmount/listmount ABI validation program. It checks mount ids, parent ids, propagation, superblock fields, string fields, mount options, pagination, and `STATMOUNT_BY_FD` behavior.

## Important APIs, Types, and Functions

Helpers include `write_file`, `get_mnt_id`, `cleanup_namespace`, `setup_namespace`, `setup_mount_tree`, many `test_statmount_*` functions, and `test_listmount_tree`. It uses `statmount`, `listmount`, `statmount_alloc`, `statmount_alloc_by_fd`, `statx`, `statfs`, mount namespace and user namespace setup, bind mounts, chroot, and kselftest result APIs.

## Control Flow, State, and Persistence

`main` probes syscall support, sets up a private user/mount/pid namespace, maps uid/gid, opens mountinfo, creates a temporary bind-mounted root, chroots into it, and records old and unique mount ids for root and parent. It plans 17 tests: list an empty root, zero-mask statmount, mount basic fields, superblock fields, mount root and point strings, filesystem type from a known list, mount options compared with `/proc/self/mountinfo`, string exact-size and `EOVERFLOW` checks, all-mask string checks, listmount tree pagination over propagated bind mounts, statmount by fd on an unmounted mount, and statmount by fd across chroot visibility. Cleanup restores the original root and detaches the temporary mount.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are statmount/listmount syscalls, statx unique mount ids, user namespace mapping, mountinfo format, statfs, bind mounts, and chroot. It integrates directly with the new mount introspection ABI. Risks include exact option-string comparison, known filesystem list aging, global mount changes, chroot cleanup hazards, and statmount masks being optional on older kernels. Passing signals are matching ids/parents, correct masks and sizes, string offsets in bounds, `EOVERFLOW` on short buffers, matching mount options, correct pagination, and expected hidden mountpoint behavior for inaccessible or detached mounts.
