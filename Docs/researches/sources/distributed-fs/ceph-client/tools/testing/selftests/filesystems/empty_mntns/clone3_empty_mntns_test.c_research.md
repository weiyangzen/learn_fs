# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/clone3_empty_mntns_test.c

## Purpose
Tests `clone3()` with `CLONE_EMPTY_MNTNS`, ensuring it creates an empty/nullfs mount namespace, implies `CLONE_NEWNS`, composes correctly with other clone flags, rejects invalid combinations, and supports overmounting and `setns`.

## Important APIs, Types, And Functions
Uses `sys_clone3`, `CLONE_EMPTY_MNTNS`, `CLONE_NEWNS`, `CLONE_NEWUSER`, `CLONE_NEWPID`, `CLONE_PIDFD`, `CLONE_FS`, `setns`, `listmount`, `statmount_alloc`, new mount API wrappers, `chroot`, and helpers from `empty_mntns.h` and `utils.c`. Key helpers are `clone3_empty_mntns()` and `clone3_empty_mntns_supported()`.

## Control Flow
A fixture skips if clone3 empty namespaces are unsupported. Tests fork into user namespaces, clone children with empty mount namespaces, and assert exactly one root mount, root equals cwd, parent mounts unchanged, root fs type is `nullfs`, listmount returns one entry, repeated clones have distinct mount ids, and `setns` works. Other tests verify explicit `CLONE_NEWNS`, `CLONE_NEWUSER`, UTS/IPC, PID namespace pid 1, pidfd output, `CLONE_FS` rejection, EPERM without caps, tmpfs overmount/chroot, unknown flag rejection, and normal `CLONE_NEWNS` full-copy behavior.

## State And Persistence
Creates child processes, user/mount namespaces, temporary tmpfs mounts, bind mounts, pipes, pidfds, and files in child namespaces. No persistent host files are intended.

## Dependencies And Integration Points
Requires clone3, the new empty mount namespace flag, user namespace helpers, statmount/listmount, and new mount API wrappers.

## Risks
Very new UAPI constants and syscalls make this highly kernel-version dependent. Many tests encode child exit status values for failure localization but parent only sees nonzero. Overmount tests rely on `nullfs` semantics and `MOVE_MOUNT_F_EMPTY_PATH`.

## Test Signals
Signals are successful fixture support probe, one-mount listmount counts, `nullfs`/`tmpfs` statmount fs types, expected `EINVAL`/`EPERM`, valid pidfd, pid 1 in new PID namespace, and unchanged parent mount count.
