# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/iterate_mntns.c

## Purpose

`iterate_mntns.c` tests nsfs ioctls that expose information about mount namespaces and iterate to neighboring mount namespaces.

## Important APIs, Types, and Functions

It defines `struct mnt_ns_info`, `NS_MNT_GET_INFO`, `NS_MNT_GET_NEXT`, and `NS_MNT_GET_PREV`. The fixture stores eleven mount namespace fds and ids. `mntns_in_list` checks whether a returned namespace id belongs to the fixture-created set. Tests use `unshare(CLONE_NEWNS)`, `/proc/self/ns/mnt`, `ioctl`, `fcntl(F_DUPFD_CLOEXEC)`, `setns`, and negative autofs ioctl probes.

## Control Flow, State, and Persistence

Setup repeatedly unshares a mount namespace, opens its nsfs fd, calls `NS_MNT_GET_INFO`, and records the returned ids. Forward and backward whole-list tests duplicate the first or last fd and repeatedly call NEXT or PREV until `ENOENT`, counting fixture ids encountered. Direct iteration tests `setns` into an endpoint and walk exactly ten steps, closing previous fds as they go. `nfs_valid_ioctl` ensures unrelated autofs ioctls on a mount namespace fd fail with `ENOTTY`. Persistent state is a chain of open mount namespace fds held by the fixture.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include nsfs mount namespace iteration ioctls, mount namespace creation, and kselftest harness. It integrates with namespace lifetime and ioctl ABI validation. Risks are global mount namespace ordering assumptions, count checks relying on fixture-created namespaces being visible in traversal, and a test name typo (`nfs_valid_ioctl`). Passing signals are successful INFO ids, NEXT/PREV traversal, `ENOENT` termination, and `ENOTTY` for invalid autofs ioctls.
