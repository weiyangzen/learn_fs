# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/empty_mntns_test.c

## Purpose
Tests empty mount namespace creation through `unshare(UNSHARE_EMPTY_MNTNS)`. It verifies basic semantics, namespace combinations, permission errors, cwd reset, statmount/listmount properties, repeated unshare, overmounting nullfs with tmpfs, and regressions for ordinary namespace behavior.

## Important APIs, Types, And Functions
Uses `unshare`, `UNSHARE_EMPTY_MNTNS`, `CLONE_NEWUSER`, `CLONE_NEWNS`, `CLONE_NEWUTS`, `CLONE_NEWIPC`, `listmount`, `statmount`, `statmount_alloc`, new mount API wrappers (`fsopen`, `fsconfig`, `fsmount`, `move_mount`), `chroot`, and helpers from `utils.c` and `empty_mntns.h`. Support probe is `unshare_empty_mntns_supported()`.

## Control Flow
The fixture skips if unsupported. Tests fork children, enter user namespaces where needed, call `unshare(UNSHARE_EMPTY_MNTNS)`, and assert one mount, root/cwd identity, permissions, root parent relationship, listmount single entry, and distinct mount IDs on repeated calls. Overmount test confirms `nullfs` root is immutable, mounts tmpfs over `/`, chroots via mount fd, then writes a file. Non-fixture tests verify invalid flags reject, normal `CLONE_NEWNS` copies mount tree, and unrelated UTS namespace behavior still works.

## State And Persistence
Creates child namespaces, tmpfs/bind mounts, temporary directories, and test files within child namespaces. No persistent host state is intended.

## Dependencies And Integration Points
Requires new `UNSHARE_EMPTY_MNTNS` support, user namespace privileges, statmount/listmount, and new mount API wrappers.

## Risks
Tests target new kernel behavior and can skip/fail on older kernels. `open("/test", O_CREAT)` expecting `ENOENT` encodes nullfs lookup behavior. Parent sees only child exit status, so debugging uses source line mapping.

## Test Signals
Signals are exact one-mount counts, root/cwd mount-id equality, `nullfs` then `tmpfs` fs types, `EINVAL` for invalid flags, full-copy count for regular `CLONE_NEWNS`, and successful file creation after tmpfs overmount.
