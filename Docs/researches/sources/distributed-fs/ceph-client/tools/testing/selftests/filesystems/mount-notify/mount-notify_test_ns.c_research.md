# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/mount-notify/mount-notify_test_ns.c

## Purpose

`mount-notify_test_ns.c` is the user-namespace variant of the fanotify mount notification test. It verifies both notification delivery inside the created mount namespace and permission boundaries for watching namespaces and filesystems outside that user namespace.

## Important APIs, Types, and Functions

It uses the same event parsing and mount verification helpers as `mount-notify_test.c`, with added setup of `orig_ns_fd`, `setup_userns`, and `mark_types` covering filesystem, mount, and inode marks. Setup probes `FAN_REPORT_FID` permission against the tmpfs root and original root, then installs `FAN_REPORT_MNT` namespace marks.

## Control Flow, State, and Persistence

Setup opens the original mount namespace, enters a new user namespace, opens the new mount namespace fd, mounts tmpfs as a chroot root, creates test directories, and records the root mount id. It confirms watching tmpfs mounted inside the user namespace is allowed, watching the original root filesystem is rejected, watching the current mount namespace is allowed, and watching the original namespace is rejected. It then runs the same bind, move, propagation, fsmount, reparent, rmdir, and pivot_root notification scenarios as the non-`_ns` file. State consists of namespace fds, fanotify event queues, and the temporary mount tree.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are user namespace support, fanotify permission checks, mount notifications, statmount/listmount, and mount/chroot operations. It integrates fanotify mount notification security rules with namespace ownership semantics. Risks include disabled unprivileged user namespaces, permission errno differences, event ordering, and cleanup after chroot. Passing signals are rejected marks on original objects, accepted marks inside the user namespace, exact mount notification masks, and mounted-set verification after each operation.
