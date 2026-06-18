# sources/distributed-fs/ceph-client/samples/binderfs/binderfs_example.c

Purpose: demonstrates creating and removing a binder device inside a binderfs mount.

Important APIs/types/functions: uses `unshare(CLONE_NEWNS)`, `mount` with `MS_REC|MS_PRIVATE`, `mkdir`, `mount(..., "binder", ...)`, `open("/dev/binderfs/binder-control")`, `ioctl(BINDER_CTL_ADD)`, `struct binderfs_device`, and `unlink`.

Control flow: creates a private mount namespace, makes `/` private, ensures `/dev/binderfs` exists, mounts binderfs, requests a new device named `my-binder`, prints major/minor/name, unlinks the device, and exits. Mount cleanup is delegated to namespace teardown.

State and persistence: state is the private mount namespace and transient binder device. The device is unlinked explicitly; the mount disappears when the namespace exits.

Dependencies and integration: requires binderfs kernel support, Android binder UAPI headers, and enough privilege for mount namespace and binderfs mount operations.

Risks: hardcoded `/dev/binderfs` path may conflict with existing systems. `memcpy` copies the name without an explicit terminator but starts from a zeroed struct, so current usage is safe. Runtime failures exit early and rely on namespace cleanup.

Test signals: run as a privileged user on a binderfs-enabled kernel, confirm printed device allocation, and verify no persistent `/dev/binderfs/my-binder` after exit.
